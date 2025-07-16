from flask import render_template, jsonify, request, send_from_directory
from app import app, db
from models import TradingSignal, SystemMetrics, AlertLog, TradingAnalysis, MarketData, OrderbookData, OpenInterestData, TechnicalIndicatorData, UserPreferences, AISnapshotArchive
from datetime import datetime, timedelta, timezone
from config import Config
import logging
import numpy as np
import pandas as pd

# Common core imports moved to top to avoid repetition
from core.analyzer import TechnicalAnalyzer
from core.okx_fetcher import OKXAPIManager
from core.snapshot_generator import SnapshotGenerator, SnapshotType

# Monitoring imports
from core.monitoring import monitor_api_performance, track_trading_signal, track_ai_narrative, monitor

logger = logging.getLogger(__name__)

# JSON Safe Converter Helper
def json_safe(obj):
    """Convert object to JSON-safe format"""
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.fillna(0).tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.fillna(0).to_dict(orient='records')
    elif pd.isna(obj) or (isinstance(obj, float) and np.isnan(obj)):
        return 0
    elif isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [json_safe(item) for item in obj]
    return obj

# Initialize services locally to avoid circular imports
def get_narrative_ai():
    from core.narrative_ai import NarrativeAI
    return NarrativeAI()

def get_realtime_streamer():
    from core.realtime_streamer import RealtimeDataStreamer, streamer
    return streamer

# Helper functions for enhanced charts endpoint
def prepare_candlestick_data(df):
    """Prepare candlestick data with proper timestamp handling"""
    candlestick_data = []
    for i in range(len(df)):
        # Get timestamp from DataFrame - it's a column, not index
        if 'timestamp' in df.columns:
            timestamp_val = df['timestamp'].iloc[i]
            if hasattr(timestamp_val, 'isoformat'):
                timestamp_iso = timestamp_val.isoformat()
                timestamp_ms = int(timestamp_val.timestamp() * 1000)
            else:
                # Convert to proper datetime if needed
                try:
                    if isinstance(timestamp_val, (int, float)):
                        # Assume Unix timestamp
                        if timestamp_val > 10000000000:  # Milliseconds
                            timestamp_dt = datetime.fromtimestamp(timestamp_val / 1000)
                        else:  # Seconds
                            timestamp_dt = datetime.fromtimestamp(timestamp_val)
                    else:
                        # Invalid timestamp, use current time minus interval
                        timestamp_dt = datetime.now() - timedelta(hours=(len(df) - i))
                    
                    timestamp_iso = timestamp_dt.isoformat()
                    timestamp_ms = int(timestamp_dt.timestamp() * 1000)
                except (ValueError, TypeError):
                    # Final fallback - use current time minus interval
                    timestamp_dt = datetime.now() - timedelta(hours=(len(df) - i))
                    timestamp_iso = timestamp_dt.isoformat()
                    timestamp_ms = int(timestamp_dt.timestamp() * 1000)
        else:
            # Fallback if no timestamp column
            timestamp_dt = datetime.now() - timedelta(hours=(len(df) - i))
            timestamp_iso = timestamp_dt.isoformat()
            timestamp_ms = int(timestamp_dt.timestamp() * 1000)
        
        candlestick_data.append({
            'timestamp': timestamp_iso,
            'time': timestamp_ms,
            'open': float(df['open'].iloc[i]),
            'high': float(df['high'].iloc[i]),
            'low': float(df['low'].iloc[i]),
            'close': float(df['close'].iloc[i]),
            'volume': float(df['volume'].iloc[i])
        })
    
    return candlestick_data

def prepare_support_resistance_levels(df):
    """Calculate and prepare support/resistance levels"""
    support_levels = []
    resistance_levels = []
    
    # Calculate basic support/resistance (simplified)
    recent_lows = df['low'].rolling(window=20).min()
    recent_highs = df['high'].rolling(window=20).max()
    
    if not recent_lows.empty and not recent_highs.empty:
        support_levels = [float(recent_lows.iloc[-1])]
        resistance_levels = [float(recent_highs.iloc[-1])]
    
    return support_levels, resistance_levels

def prepare_smc_levels(smc_analysis, df):
    """Prepare SMC levels (Order Blocks, FVG Gaps, Swing Points)"""
    smc_levels = {
        'orderBlocks': [],
        'fvgGaps': [],
        'swingPoints': smc_analysis.get('swing_points', {})
    }
    
    # Extract order blocks from SMC analysis
    order_blocks = smc_analysis.get('order_blocks', [])
    for block in order_blocks:
        # Handle timestamp conversion safely
        start_time = block.get('start_time', df.index[0])
        end_time = block.get('end_time', df.index[-1])
        
        if hasattr(start_time, 'isoformat'):
            start_time_iso = start_time.isoformat()
        else:
            start_time_iso = str(start_time)
            
        if hasattr(end_time, 'isoformat'):
            end_time_iso = end_time.isoformat()
        else:
            end_time_iso = str(end_time)
        
        smc_levels['orderBlocks'].append({
            'start_time': start_time_iso,
            'end_time': end_time_iso,
            'high': block.get('high', 0),
            'low': block.get('low', 0),
            'type': block.get('type', 'bullish')
        })
    
    # Extract FVG gaps
    fvg_signals = smc_analysis.get('fvg_signals', [])
    for gap in fvg_signals:
        # Handle timestamp conversion safely
        start_time = gap.get('start_time', df.index[0])
        end_time = gap.get('end_time', df.index[-1])
        
        if hasattr(start_time, 'isoformat'):
            start_time_iso = start_time.isoformat()
        else:
            start_time_iso = str(start_time)
            
        if hasattr(end_time, 'isoformat'):
            end_time_iso = end_time.isoformat()
        else:
            end_time_iso = str(end_time)
        
        smc_levels['fvgGaps'].append({
            'start_time': start_time_iso,
            'end_time': end_time_iso,
            'high': gap.get('high', 0),
            'low': gap.get('low', 0),
            'type': gap.get('type', 'bullish')
        })
    
    return smc_levels

@app.route('/dashboard')
def dashboard():
    """Main trading dashboard"""
    return render_template('dashboard.html')

@app.route('/react/static/<path:filename>')
def serve_react_static(filename):
    """Serve React static files"""
    return send_from_directory('static', filename)

@app.route('/react/src/<path:filename>')
def serve_react_src(filename):
    """Serve React source files"""
    return send_from_directory('src', filename)

@app.route('/react/public/<path:filename>')
def serve_react_public(filename):
    """Serve React public files"""
    return send_from_directory('public', filename)

@app.route('/advanced-analysis')
def advanced_analysis_page():
    """Advanced analysis test page"""
    return render_template('advanced_analysis.html')

@app.route('/api/signals')
def get_signals():
    """Get recent trading signals"""
    try:
        hours = request.args.get('hours', 24, type=int)
        symbol = request.args.get('symbol', '')
        signal_type = request.args.get('type', '')
        
        query = TradingSignal.query
        
        # Filter by time
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        query = query.filter(TradingSignal.created_at >= since)
        
        # Filter by symbol if provided
        if symbol:
            query = query.filter(TradingSignal.symbol == symbol)
            
        # Filter by signal type if provided
        if signal_type:
            query = query.filter(TradingSignal.pattern_type == signal_type)
        
        signals = query.order_by(TradingSignal.created_at.desc()).limit(100).all()
        
        return jsonify([{
            'id': signal.id,
            'signal_id': signal.signal_id,
            'symbol': signal.symbol,
            'action': signal.action,
            'pattern_type': signal.pattern_type,
            'entry_price': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'take_profit_1': signal.take_profit_1,
            'take_profit_2': signal.take_profit_2,
            'take_profit_3': signal.take_profit_3,
            'risk_reward_ratio': signal.risk_reward_ratio,
            'position_size_percentage': signal.position_size_percentage,
            'confidence': signal.confidence,
            'timeframe': signal.timeframe,
            'reason': signal.reason,
            'status': signal.status,
            'timestamp': signal.timestamp,
            'created_at': signal.created_at.isoformat()
        } for signal in signals])
        
    except Exception as e:
        logger.error(f"Error fetching signals: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch signals'}), 500

@app.route('/api/metrics')
def get_metrics():
    """Get system performance metrics"""
    try:
        hours = request.args.get('hours', 24, type=int)
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        metrics = SystemMetrics.query.filter(
            SystemMetrics.timestamp >= since
        ).order_by(SystemMetrics.timestamp.desc()).limit(100).all()
        
        return jsonify([{
            'id': metric.id,
            'cpu_usage': metric.cpu_usage,
            'memory_usage': metric.memory_usage,
            'disk_usage': metric.disk_usage,
            'api_response_time': metric.api_response_time,
            'active_connections': metric.active_connections,
            'error_count': metric.error_count,
            'cycle_count': metric.cycle_count,
            'timestamp': metric.timestamp.isoformat()
        } for metric in metrics])
        
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch metrics'}), 500

@app.route('/api/stats')
def get_stats():
    """Get trading statistics summary"""
    try:
        # Get stats for last 24 hours
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        
        total_signals = TradingSignal.query.filter(
            TradingSignal.created_at >= since
        ).count()
        
        # Pattern type breakdown
        pattern_types = db.session.query(
            TradingSignal.pattern_type,
            db.func.count(TradingSignal.id)
        ).filter(
            TradingSignal.created_at >= since
        ).group_by(TradingSignal.pattern_type).all()
        
        # Symbol breakdown
        symbols = db.session.query(
            TradingSignal.symbol,
            db.func.count(TradingSignal.id)
        ).filter(
            TradingSignal.created_at >= since
        ).group_by(TradingSignal.symbol).all()
        
        # High confidence signals
        high_conf_signals = TradingSignal.query.filter(
            TradingSignal.created_at >= since,
            TradingSignal.confidence >= 0.75
        ).count()
        
        # Recent alerts
        recent_alerts = AlertLog.query.filter(
            AlertLog.timestamp >= since
        ).count()
        
        # Latest system metrics
        latest_metrics = SystemMetrics.query.order_by(
            SystemMetrics.timestamp.desc()
        ).first()
        
        return jsonify({
            'total_signals': total_signals,
            'high_confidence_signals': high_conf_signals,
            'recent_alerts': recent_alerts,
            'pattern_types': dict(pattern_types),
            'symbols': dict(symbols),
            'system_health': {
                'cpu_usage': latest_metrics.cpu_usage if latest_metrics else 0,
                'memory_usage': latest_metrics.memory_usage if latest_metrics else 0,
                'disk_usage': latest_metrics.disk_usage if latest_metrics else 0,
                'api_response_time': latest_metrics.api_response_time if latest_metrics else 0
            } if latest_metrics else {}
        })
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@app.route('/api/alerts')
def get_alerts():
    """Get recent alerts"""
    try:
        hours = request.args.get('hours', 24, type=int)
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        alerts = AlertLog.query.filter(
            AlertLog.timestamp >= since
        ).order_by(AlertLog.timestamp.desc()).limit(50).all()
        
        return jsonify([{
            'id': alert.id,
            'alert_type': alert.alert_type,
            'message': alert.message,
            'severity': alert.severity,
            'channel': alert.channel,
            'status': alert.status,
            'timestamp': alert.timestamp.isoformat()
        } for alert in alerts])
        
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch alerts'}), 500

@app.route('/api/chart-data/<symbol>')
def chart_data(symbol):
    """Get chart data for TradingView Lightweight Charts"""
    try:
        # Import necessary modules
        from core.okx_fetcher import OKXDataFetcher
        from datetime import datetime, timedelta
        
        # Get query parameters
        timeframe = request.args.get('timeframe', '1H')
        limit = int(request.args.get('limit', 300))
        
        # Initialize fetcher
        fetcher = OKXDataFetcher()
        
        # Fetch candle data
        df = fetcher.fetch_data(symbol, timeframe, limit)
        
        if df is None or df.empty:
            return jsonify({
                "status": "error",
                "message": f"No data available for {symbol}"
            }), 404
            
        # Convert to TradingView format
        candles = []
        for _, row in df.iterrows():
            candles.append({
                "time": int(row['timestamp'] / 1000),  # Convert to seconds
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": float(row['volume'])
            })
            
        # Calculate indicators
        indicators = {
            "ema9": df['close'].ewm(span=9).mean().tolist() if len(df) > 9 else [],
            "ema21": df['close'].ewm(span=21).mean().tolist() if len(df) > 21 else [],
            "ema50": df['close'].ewm(span=50).mean().tolist() if len(df) > 50 else []
        }
        
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "candles": candles,
            "indicators": indicators
        })
        
    except Exception as e:
        logger.error(f"Error getting chart data for {symbol}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/analyze/<symbol>')
@monitor_api_performance('analyze_symbol')
def analyze_coin(symbol):
    """Enhanced real-time analysis with OkxCandleTracker SMC integration"""
    try:
        # Import necessary modules
        from core.okx_fetcher import OKXAPIManager
        from core.analyzer import TechnicalAnalyzer
        from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
        from core.signal_engine import SignalEngine
        import pandas as pd
        
        # Validate symbol
        valid_symbols = ['BTC', 'ETH', 'SOL', 'TIA', 'RENDER']
        if symbol.upper() not in valid_symbols:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Get parameters
        timeframe = request.args.get('timeframe', '1H')
        include_ai = request.args.get('ai', 'true').lower() == 'true'  # Enable AI by default
        include_smc = request.args.get('smc', 'true').lower() == 'true'
            
        # Initialize components
        okx_api = OKXAPIManager()
        analyzer = TechnicalAnalyzer()
        
        # Fetch real-time data
        symbol_okx = f"{symbol.upper()}-USDT"
        df = okx_api.get_candles(symbol_okx, timeframe=timeframe, limit=200)
        
        if df is None or df.empty:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch market data',
                'symbol': symbol
            }), 500
            
        # Run enhanced technical analysis
        analysis = analyzer.analyze(df, symbol_okx, timeframe)
        
        # Ensure analysis is a dictionary
        if not isinstance(analysis, dict):
            analysis = {'error': 'Analysis failed', 'indicators': {}, 'signals': [], 'confidence': 0}
        
        # Extract key data from analysis
        current_price = float(df['close'].iloc[-1])
        price_change_24h = analysis.get('price_change_24h', 0)
        
        # Professional SMC analysis (if enabled)
        smc_analysis = {}
        if include_smc:
            try:
                smc_analyzer = ProfessionalSMCAnalyzer()
                smc_analysis = smc_analyzer.analyze_comprehensive(df, symbol_okx, timeframe)
            except Exception as e:
                logger.warning(f"SMC analysis failed: {e}")
        
        # Signal engine analysis
        signal_data = {}
        try:
            signal_engine = SignalEngine()
            signal_data = signal_engine.generate_comprehensive_signals(df, symbol_okx, timeframe)
        except Exception as e:
            logger.warning(f"Signal engine analysis failed: {e}")
        
        # Calculate technical indicators with better error handling
        indicators = analysis.get('indicators', {})
        
        # RSI handling
        rsi_value = indicators.get('rsi', 50)
        if isinstance(rsi_value, (list, tuple)) and len(rsi_value) > 0:
            rsi_value = rsi_value[-1]
        elif isinstance(rsi_value, dict):
            rsi_value = 50  # Default if dict format
        
        # MACD calculation with safe handling
        macd_data = indicators.get('macd', {})
        if isinstance(macd_data, dict):
            macd_value = macd_data.get('macd', 0)
            macd_signal = macd_data.get('signal', 0)
            
            # Handle both numeric and list/array types
            if isinstance(macd_value, (list, tuple)) and len(macd_value) > 0:
                macd_value = macd_value[-1]
            if isinstance(macd_signal, (list, tuple)) and len(macd_signal) > 0:
                macd_signal = macd_signal[-1]
                
            macd_diff = macd_value - macd_signal if isinstance(macd_value, (int, float)) and isinstance(macd_signal, (int, float)) else 0
        else:
            macd_diff = 0
        
        # Enhanced signal processing
        signals = []
        
        # Traditional signals
        traditional_signals = analysis.get('signals', []) if isinstance(analysis, dict) else []
        for sig in traditional_signals:
            if isinstance(sig, dict):
                signals.append({
                    'type': 'TRADITIONAL',
                    'action': sig.get('action', 'NEUTRAL'),
                    'confidence': sig.get('confidence', 0),
                    'reason': sig.get('reason', 'Technical indicator signal'),
                    'entry_price': sig.get('entry_price'),
                    'stop_loss': sig.get('stop_loss'),
                    'take_profit_1': sig.get('take_profit_1')
                })
        
        # SMC signals
        if smc_analysis.get('signals'):
            for smc_signal in smc_analysis['signals']:
                signals.append({
                    'type': 'SMC',
                    'action': smc_signal.get('action', 'NEUTRAL'),
                    'confidence': smc_signal.get('confidence', 0),
                    'pattern': smc_signal.get('pattern', 'UNKNOWN'),
                    'reason': smc_signal.get('reason', 'SMC Pattern Detection'),
                    'entry_price': smc_signal.get('entry_price'),
                    'stop_loss': smc_signal.get('stop_loss'),
                    'take_profit_1': smc_signal.get('take_profit_1')
                })
        
        # Signal engine signals
        if signal_data.get('signals'):
            for eng_signal in signal_data['signals']:
                signals.append({
                    'type': 'SIGNAL_ENGINE',
                    'action': eng_signal.get('action', 'NEUTRAL'),
                    'confidence': eng_signal.get('confidence', 0),
                    'reason': eng_signal.get('reason', 'Multi-factor signal'),
                    'entry_price': eng_signal.get('entry_price'),
                    'stop_loss': eng_signal.get('stop_loss'),
                    'take_profit_1': eng_signal.get('take_profit_1')
                })
        
        has_signal = len(signals) > 0
        
        # Generate basic analysis text with safe formatting
        trend = str(analysis.get('trend', 'neutral'))
        volume_trend = str(analysis.get('volume_trend', 'stable'))
        
        # Ensure all variables are safe for formatting
        safe_symbol = str(symbol.upper())
        safe_current_price = float(current_price) if isinstance(current_price, (int, float)) else 0.0
        safe_price_change = float(price_change_24h) if isinstance(price_change_24h, (int, float)) else 0.0
        safe_rsi = float(rsi_value) if isinstance(rsi_value, (int, float)) else 50.0
        safe_macd = float(macd_diff) if isinstance(macd_diff, (int, float)) else 0.0
        
        # Get detailed SMC and signal data
        smc_data = smc_analysis if smc_analysis else {}
        signal_engine_data = signal_data if signal_data else {}
        
        # Extract SMC patterns
        smc_patterns = smc_data.get('smc_summary', {})
        total_choch_bos = smc_patterns.get('total_choch_bos', 0)
        total_order_blocks = smc_patterns.get('total_order_blocks', 0)
        total_fvg = smc_patterns.get('total_fvg', 0)
        total_liquidity = smc_patterns.get('total_liquidity_sweeps', 0)
        bullish_signals = smc_patterns.get('bullish_signals', 0)
        bearish_signals = smc_patterns.get('bearish_signals', 0)
        
        # Extract swing points
        swing_points = smc_data.get('swing_points', {})
        swing_highs = len(swing_points.get('highs', []))
        swing_lows = len(swing_points.get('lows', []))
        
        # Extract signal engine data
        final_signal = signal_engine_data.get('final_signal', {})
        signal_action = final_signal.get('action', 'NEUTRAL')
        signal_confidence = final_signal.get('confidence', 0)
        
        # Extract risk assessment
        risk_data = signal_engine_data.get('risk_assessment', {})
        risk_level = risk_data.get('risk_level', 'MEDIUM')
        
        # Safe string conversion
        market_structure = str(smc_data.get('market_structure', 'NEUTRAL')).upper()
        ema_trend = str(indicators.get('ema', {}).get('trend', 'NEUTRAL')).upper()
        
        formatted_analysis = f"""📊 **ANALISIS TEKNIKAL KOMPREHENSIF - {safe_symbol}-USDT**
==================================================

💰 **Harga Saat Ini:** ${safe_current_price:,.2f}
📈 **Perubahan 24h:** {safe_price_change:+.2f}%
🎯 **Tren:** {trend.upper()}

**📈 SMART MONEY CONCEPTS (SMC):**
• Market Structure: {market_structure}
• Swing Points: {swing_highs} highs, {swing_lows} lows
• CHoCH/BOS Signals: {total_choch_bos}
• Order Blocks: {total_order_blocks}
• Fair Value Gaps: {total_fvg}
• Liquidity Sweeps: {total_liquidity}
• Bullish Patterns: {bullish_signals}
• Bearish Patterns: {bearish_signals}

**📊 INDIKATOR TEKNIKAL:**
• RSI: {safe_rsi:.1f} ({'Oversold' if safe_rsi < 30 else 'Overbought' if safe_rsi > 70 else 'Normal'})
• MACD: {safe_macd:+.4f} ({'Bullish' if safe_macd > 0 else 'Bearish'})
• EMA Trend: {ema_trend}
• Volume: {volume_trend.upper()}

**🎯 SIGNAL ENGINE:**
• Action: {signal_action}
• Confidence: {signal_confidence:.1f}%
• Risk Level: {risk_level}
• Components: {len(signal_engine_data.get('component_signals', []))} signals

**📈 PRICE ACTION:**
• Current Structure: {trend.upper()}
• Volume Trend: {volume_trend.upper()}
• Market Momentum: {'Bullish' if bullish_signals > bearish_signals else 'Bearish' if bearish_signals > bullish_signals else 'Neutral'}

**🎯 TRADING OUTLOOK:**
• Signal Status: {'ACTIVE' if has_signal else 'STANDBY'}
• Entry Zones: {'Available' if has_signal else 'Waiting for setup'}
• Risk Management: {risk_level} risk level

**⚠️ DISCLAIMER:** Analisis ini hanya untuk tujuan edukasi. 
Selalu lakukan riset sendiri sebelum trading."""
        
        # Prepare chart data for frontend
        chart_data = []
        for i in range(len(df)):
            try:
                chart_data.append({
                    'timestamp': df.index[i].isoformat() if hasattr(df.index[i], 'isoformat') else str(df.index[i]),
                    'open': float(df['open'].iloc[i]),
                    'high': float(df['high'].iloc[i]),
                    'low': float(df['low'].iloc[i]),
                    'close': float(df['close'].iloc[i]),
                    'volume': float(df['volume'].iloc[i])
                })
            except (IndexError, ValueError, KeyError):
                continue
        
        return jsonify({
            'success': True,
            'status': 'success',
            'symbol': symbol.upper(),
            'currentPrice': current_price,
            'priceChange24h': price_change_24h,
            'hasSignal': has_signal,
            'rsiValue': float(rsi_value),
            'macdValue': float(macd_diff),
            'formattedAnalysis': formatted_analysis,
            'analysis': {
                **analysis,
                'chart': chart_data,  # Add chart data for frontend
                'indicators': indicators,
                'signals': signals,
                'smc_analysis': smc_analysis,
                'signal_data': signal_data
            },
            'chart': chart_data,  # Also add at root level for backward compatibility
            'rawData': {
                'confidence': analysis.get('confidence', 0),
                'patterns': len(analysis.get('smc_analysis', {}).get('patterns', [])),
                'trend': trend
            }
        })
        
    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'chart': [],  # Empty chart data for error case
            'analysis': {
                'chart': [],
                'indicators': {},
                'signals': []
            }
        }), 500

@app.route('/api/snapshot/<symbol>')
def get_comprehensive_snapshot(symbol):
    """Get comprehensive market snapshot with enhanced analysis"""
    try:
        from core.snapshot_generator import SnapshotGenerator, SnapshotType
        
        # Validate symbol
        valid_symbols = ['BTC', 'ETH', 'SOL', 'TIA', 'RENDER']
        if symbol.upper() not in valid_symbols:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Get parameters
        timeframe = request.args.get('timeframe', '1H')
        snapshot_type = request.args.get('type', 'comprehensive')
        session_id = request.args.get('session_id', 'api_request')
        
        # Map snapshot type
        type_mapping = {
            'quick': SnapshotType.QUICK,
            'comprehensive': SnapshotType.COMPREHENSIVE,
            'deep': SnapshotType.DEEP_ANALYSIS
        }
        
        snapshot_type_enum = type_mapping.get(snapshot_type, SnapshotType.COMPREHENSIVE)
        
        # Generate snapshot
        generator = SnapshotGenerator()
        snapshot = generator.generate_snapshot(
            symbol=f"{symbol.upper()}-USDT",
            timeframe=timeframe,
            snapshot_type=snapshot_type_enum,
            session_id=session_id
        )
        
        return jsonify({
            'success': True,
            'snapshot': {
                'symbol': snapshot.symbol,
                'timeframe': snapshot.timeframe,
                'timestamp': snapshot.timestamp,
                'current_price': snapshot.current_price,
                'price_change_24h': snapshot.price_change_24h,
                'confidence_score': snapshot.confidence_score,
                'data_quality': snapshot.data_quality,
                'generation_time': snapshot.generation_time,
                'snapshot_type': snapshot.snapshot_type.value,
                'analysis': snapshot.ai_narrative,
                'technical_indicators': snapshot.technical_summary if hasattr(snapshot, 'technical_summary') else {},
                'smc_analysis': snapshot.smc_analysis if hasattr(snapshot, 'smc_analysis') else {},
                'ai_narrative': snapshot.ai_narrative
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating snapshot for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orderbook/<symbol>')
def get_orderbook_data(symbol):
    """Get real-time orderbook data"""
    try:
        from core.okx_fetcher import OKXAPIManager
        
        # Validate symbol
        valid_symbols = ['BTC', 'ETH', 'SOL', 'TIA', 'RENDER']
        if symbol.upper() not in valid_symbols:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Get parameters
        depth = request.args.get('depth', 20, type=int)
        
        # Initialize API manager
        api = OKXAPIManager()
        symbol_okx = f"{symbol.upper()}-USDT"
        
        # Get orderbook data
        orderbook = api.get_orderbook(symbol_okx, depth)
        
        if not orderbook:
            return jsonify({'error': 'Failed to fetch orderbook data'}), 500
        
        # Process orderbook data
        bids = []
        asks = []
        
        for bid in orderbook.get('bids', []):
            bids.append({
                'price': float(bid[0]),
                'size': float(bid[1]),
                'total': float(bid[0]) * float(bid[1])
            })
        
        for ask in orderbook.get('asks', []):
            asks.append({
                'price': float(ask[0]),
                'size': float(ask[1]),
                'total': float(ask[0]) * float(ask[1])
            })
        
        # Calculate spread
        best_bid = float(orderbook['bids'][0][0]) if orderbook.get('bids') else 0
        best_ask = float(orderbook['asks'][0][0]) if orderbook.get('asks') else 0
        spread = best_ask - best_bid
        spread_percentage = (spread / best_ask * 100) if best_ask > 0 else 0
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'timestamp': datetime.fromtimestamp(float(orderbook.get('ts', 0)) / 1000).replace(microsecond=0).isoformat() if orderbook.get('ts') else datetime.now().replace(microsecond=0).isoformat(),
            'bids': bids,
            'asks': asks,
            'spread': {
                'absolute': spread,
                'percentage': spread_percentage,
                'best_bid': best_bid,
                'best_ask': best_ask
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting orderbook for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/depth-chart/<symbol>')
def get_depth_chart_data(symbol):
    """Get market depth visualization data"""
    try:
        from core.okx_fetcher import OKXAPIManager
        
        # Validate symbol
        valid_symbols = ['BTC', 'ETH', 'SOL', 'TIA', 'RENDER']
        if symbol.upper() not in valid_symbols:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Get parameters
        depth = request.args.get('depth', 50, type=int)
        
        # Initialize API manager
        api = OKXAPIManager()
        symbol_okx = f"{symbol.upper()}-USDT"
        
        # Get orderbook data
        orderbook = api.get_orderbook(symbol_okx, depth)
        
        if not orderbook:
            return jsonify({'error': 'Failed to fetch orderbook data'}), 500
        
        # Process depth chart data
        bid_depths = []
        ask_depths = []
        
        cumulative_bid_size = 0
        for bid in orderbook.get('bids', []):
            price = float(bid[0])
            size = float(bid[1])
            cumulative_bid_size += size
            bid_depths.append({
                'price': price,
                'size': size,
                'cumulative_size': cumulative_bid_size,
                'total_value': price * cumulative_bid_size
            })
        
        cumulative_ask_size = 0
        for ask in orderbook.get('asks', []):
            price = float(ask[0])
            size = float(ask[1])
            cumulative_ask_size += size
            ask_depths.append({
                'price': price,
                'size': size,
                'cumulative_size': cumulative_ask_size,
                'total_value': price * cumulative_ask_size
            })
        
        # Calculate market depth metrics
        total_bid_value = sum(float(bid[0]) * float(bid[1]) for bid in orderbook.get('bids', []))
        total_ask_value = sum(float(ask[0]) * float(ask[1]) for ask in orderbook.get('asks', []))
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'timestamp': datetime.fromtimestamp(float(orderbook.get('ts', 0)) / 1000).replace(microsecond=0).isoformat() if orderbook.get('ts') else datetime.now().replace(microsecond=0).isoformat(),
            'depth_data': {
                'bids': bid_depths,
                'asks': ask_depths,
                'total_bid_value': total_bid_value,
                'total_ask_value': total_ask_value,
                'imbalance': (total_bid_value - total_ask_value) / (total_bid_value + total_ask_value) if (total_bid_value + total_ask_value) > 0 else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting depth chart for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/technical-indicators/<symbol>')
def get_enhanced_technical_indicators(symbol):
    """Get complete technical indicators with enhanced analysis"""
    try:
        from core.indicator_calculator import AdvancedIndicatorCalculator
        from core.okx_fetcher import OKXAPIManager
        
        # Validate symbol
        valid_symbols = ['BTC', 'ETH', 'SOL', 'TIA', 'RENDER']
        if symbol.upper() not in valid_symbols:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Get parameters
        timeframe = request.args.get('timeframe', '1H')
        indicators = request.args.get('indicators', '').split(',') if request.args.get('indicators') else []
        
        # Initialize components
        api = OKXAPIManager()
        calculator = AdvancedIndicatorCalculator()
        
        # Fetch data
        symbol_okx = f"{symbol.upper()}-USDT"
        df = api.get_candles(symbol_okx, timeframe, limit=200)
        
        if df is None or df.empty:
            return jsonify({'error': 'Failed to fetch market data'}), 500
        
        # Calculate indicators
        if not indicators:
            # Default indicators
            indicators = ['rsi', 'macd', 'bb', 'sma', 'ema', 'atr', 'obv', 'stoch', 'williams_r', 'cci']
        
        results = {}
        for indicator in indicators:
            try:
                result = calculator.calculate_indicator(df, indicator)
                
                # Handle JSON serialization using json_safe
                values = json_safe(result.values)
                
                # Ensure values is a list
                if not isinstance(values, list):
                    if isinstance(values, dict):
                        values = [values]
                    else:
                        values = [values] if values is not None else []
                
                # Take only last 10 values for API efficiency
                if len(values) > 10:
                    values = values[-10:]
                
                results[indicator] = {
                    'signal': json_safe(result.signal) if result.signal is not None else 'NEUTRAL',
                    'strength': json_safe(result.strength) if result.strength is not None else 0.0,
                    'values': values,
                    'interpretation': json_safe(result.interpretation) if hasattr(result, 'interpretation') and result.interpretation is not None else 'No interpretation available'
                }
            except Exception as e:
                logger.warning(f"Error calculating {indicator}: {e}")
                results[indicator] = {
                    'signal': 'ERROR',
                    'strength': 0.0,
                    'values': None,
                    'interpretation': f"Error: {str(e)}"
                }
        
        # Get trading signals with error handling
        try:
            signals = calculator.get_indicator_signals(df)
            # Convert signals to JSON-serializable format using json_safe
            signals = json_safe(signals)
        except Exception as e:
            logger.warning(f"Error getting indicator signals: {e}")
            signals = []
        
        # Cache information with error handling
        try:
            cache_info = calculator.get_cache_info()
        except Exception as e:
            logger.warning(f"Error getting cache info: {e}")
            cache_info = {}
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'timeframe': timeframe,
            'indicators': results,
            'signals': signals,
            'cache_info': cache_info,
            'timestamp': datetime.now().replace(microsecond=0).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting technical indicators for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/roi-analysis/<symbol>')
def get_roi_analysis(symbol):
    """Get ROI analysis for a specific symbol"""
    try:
        # Get signals for the symbol
        recent_signals = TradingSignal.query.filter_by(symbol=symbol.upper()).order_by(
            TradingSignal.timestamp.desc()
        ).limit(100).all()
        
        if not recent_signals:
            return jsonify({
                'success': False,
                'message': 'No signal data available'
            }), 404
        
        # Calculate basic ROI metrics
        total_trades = len(recent_signals)
        win_count = sum(1 for s in recent_signals if s.status in ['hit_tp1', 'hit_tp2', 'hit_tp3'])
        loss_count = sum(1 for s in recent_signals if s.status == 'stopped')
        
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'roi_metrics': {
                'total_trades': total_trades,
                'win_count': win_count,
                'loss_count': loss_count,
                'win_rate': round(win_rate, 2),
                'active_trades': total_trades - win_count - loss_count
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting ROI analysis for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500



@app.route('/api/performance-chart/<symbol>')
def get_performance_chart(symbol):
    """Get performance chart data for visualization"""
    try:
        from core.historical_analysis import HistoricalAnalysis
        from models import TradingSignal
        
        # Get historical signals
        signals = TradingSignal.query.filter(
            TradingSignal.symbol == symbol,
            TradingSignal.status.in_(['hit_tp1', 'hit_tp2', 'hit_tp3', 'stopped'])
        ).order_by(TradingSignal.created_at).all()
        
        if not signals:
            return jsonify({
                'status': 'success',
                'data': {
                    'dates': [],
                    'cumulative_pnl': [],
                    'trades': []
                }
            })
        
        # Calculate cumulative P&L
        cumulative_pnl = []
        dates = []
        trades = []
        running_pnl = 0
        
        for signal in signals:
            # Calculate P&L for this trade
            if signal.status == 'stopped':
                pnl = -abs(signal.stop_loss - signal.entry_price) / signal.entry_price * 100
            else:
                if signal.status == 'hit_tp1':
                    tp_price = signal.take_profit_1
                elif signal.status == 'hit_tp2':
                    tp_price = signal.take_profit_2
                else:
                    tp_price = signal.take_profit_3
                    
                pnl = (tp_price - signal.entry_price) / signal.entry_price * 100
                if signal.action == 'SELL':
                    pnl = -pnl
            
            running_pnl += pnl
            
            dates.append(signal.created_at.isoformat())
            cumulative_pnl.append(round(running_pnl, 2))
            trades.append({
                'date': signal.created_at.isoformat(),
                'pnl': round(pnl, 2),
                'action': signal.action,
                'pattern': signal.pattern_type,
                'status': signal.status
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'dates': dates,
                'cumulative_pnl': cumulative_pnl,
                'trades': trades
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting performance chart for {symbol}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/narrative/<symbol>')
def get_ai_narrative(symbol):
    """Get AI-generated narrative for a trading signal"""
    try:
        # Get the latest signal for the symbol
        signal = TradingSignal.query.filter_by(
            symbol=symbol,
            status='active'
        ).order_by(TradingSignal.created_at.desc()).first()
        
        if not signal:
            return jsonify({
                'status': 'error',
                'message': f'No active signal found for {symbol}'
            }), 404
            
        # Prepare signal data
        signal_data = {
            'action': signal.action,
            'pattern_type': signal.pattern_type,
            'entry_price': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'take_profit_1': signal.take_profit_1,
            'take_profit_2': signal.take_profit_2,
            'take_profit_3': signal.take_profit_3,
            'confidence': signal.confidence,
            'risk_reward_ratio': signal.risk_reward_ratio,
            'position_size_percentage': signal.position_size_percentage,
            'timeframe': signal.timeframe,
            'reason': signal.reason
        }
        
        # Get market data
        from core.okx_fetcher import get_ohlcv_data
        df = get_ohlcv_data(f"{symbol}-USDT", "1H", 100)
        
        market_data = {
            'current_price': float(df['close'].iloc[-1]) if df is not None and not df.empty else signal.entry_price,
            'volume': float(df['volume'].iloc[-1]) if df is not None and not df.empty else 0,
            'rsi': 50.0,  # Would need to calculate this
            'trend': 'bullish' if signal.action == 'BUY' else 'bearish',
            'support_levels': [],
            'resistance_levels': []
        }
        
        # Generate narrative using local import to avoid circular import
        language = request.args.get('lang', 'id')  # Default to Indonesian
        narrative_ai = get_narrative_ai()
        narrative = narrative_ai.generate_analysis_narrative(
            symbol, 
            signal_data, 
            market_data,
            language
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'symbol': narrative.symbol,
                'action': narrative.action,
                'confidence': narrative.confidence,
                'executive_summary': narrative.executive_summary,
                'technical_analysis': narrative.technical_analysis,
                'risk_assessment': narrative.risk_assessment,
                'trade_setup': narrative.trade_setup,
                'market_context': narrative.market_context,
                'disclaimer': narrative.disclaimer,
                'created_at': narrative.created_at.isoformat() if narrative.created_at else None,
                'tokens_used': narrative.tokens_used,
                'api_cost': narrative.api_cost
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating narrative for {symbol}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/narrative/usage')
def get_narrative_usage():
    """Get OpenAI API usage statistics"""
    try:
        narrative_ai = get_narrative_ai()
        stats = narrative_ai.get_usage_statistics()
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting usage statistics: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/confluence/performance')
@app.route('/api/confluence/performance/<symbol>')
def get_confluence_performance(symbol=None):
    """Get historical performance statistics from confluence checker"""
    try:
        from core.confluence_checker import ConfluenceChecker
        
        # Get timeframe from query params
        timeframe = request.args.get('timeframe', None)
        
        # Initialize confluence checker
        confluence = ConfluenceChecker()
        
        # Get historical performance
        performance = confluence.get_historical_performance(symbol, timeframe)
        
        return jsonify({
            'success': True,
            'performance': performance,
            'symbol': symbol or 'All',
            'timeframe': timeframe or 'All'
        })
        
    except Exception as e:
        logger.error(f"Error getting confluence performance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/confluence/active')
def get_active_confluence_signals():
    """Get currently active confluence signals"""
    try:
        from core.confluence_checker import ConfluenceChecker
        
        # Initialize confluence checker
        confluence = ConfluenceChecker()
        
        # Get active signals
        active_signals = confluence.get_active_signals()
        
        # Convert to JSON-serializable format
        signals_data = []
        for signal in active_signals:
            signals_data.append({
                'signal_id': signal.signal_id,
                'symbol': signal.symbol,
                'action': signal.action,
                'confidence': f"{signal.confidence * 100:.0f}%",
                'entry_price': signal.entry_price,
                'current_status': {
                    'hit_tp1': signal.hit_tp1,
                    'hit_tp2': signal.hit_tp2,
                    'hit_tp3': signal.hit_tp3,
                    'hit_sl': signal.hit_sl
                },
                'max_profit': f"{signal.max_profit_percent:.2f}%",
                'max_drawdown': f"{signal.max_drawdown_percent:.2f}%",
                'time_to_tp1': signal.time_to_tp1
            })
        
        return jsonify({
            'success': True,
            'active_signals': signals_data,
            'count': len(signals_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting active signals: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/confluence/weights', methods=['GET', 'POST'])
def manage_confluence_weights():
    """Get or update confluence checker component weights"""
    try:
        from core.confluence_checker import ConfluenceChecker
        
        if request.method == 'GET':
            # Get current weights
            confluence = ConfluenceChecker()
            return jsonify({
                'success': True,
                'weights': confluence.component_weights,
                'min_confluence_score': confluence.min_confluence_score,
                'required_confirmations': confluence.required_confirmations,
                'risk_reward_min': confluence.risk_reward_min
            })
        
        elif request.method == 'POST':
            # Update weights
            data = request.get_json()
            
            # Validate weights sum to 1.0
            if 'weights' in data:
                total = sum(data['weights'].values())
                if abs(total - 1.0) > 0.01:
                    return jsonify({'error': f'Weights must sum to 1.0, got {total}'}), 400
            
            # Create new confluence checker with updated params
            confluence = ConfluenceChecker(
                min_confluence_score=data.get('min_confluence_score', 0.65),
                required_confirmations=data.get('required_confirmations', 3),
                risk_reward_min=data.get('risk_reward_min', 2.0),
                component_weights=data.get('weights')
            )
            
            return jsonify({
                'success': True,
                'message': 'Confluence weights updated',
                'weights': confluence.component_weights
            })
            
    except Exception as e:
        logger.error(f"Error managing confluence weights: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/advanced-dashboard')
def advanced_dashboard():
    """Advanced trading dashboard with all modules integrated"""
    return render_template('advanced_dashboard.html', config=Config)

@app.route('/api/dashboard/metrics')
def get_dashboard_metrics():
    """Get comprehensive dashboard metrics"""
    try:
        # Get system metrics
        latest_metric = SystemMetrics.query.order_by(SystemMetrics.timestamp.desc()).first()
        
        # Get active signals count
        active_signals = TradingSignal.query.filter_by(status='active').count()
        
        # Calculate win rate (last 24h)
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_signals = TradingSignal.query.filter(
            TradingSignal.created_at >= yesterday
        ).all()
        
        winning_signals = sum(1 for s in recent_signals if s.status in ['hit_tp1', 'hit_tp2', 'hit_tp3'])
        win_rate = (winning_signals / len(recent_signals) * 100) if recent_signals else 0
        
        # Get cache hit rate from technical analyzer
        from core.analyzer import TechnicalAnalyzer
        analyzer = TechnicalAnalyzer()
        cache_hit_rate = analyzer.get_cache_hit_rate() * 100
        
        # Calculate total P&L
        total_pnl = 0
        for signal in recent_signals:
            if signal.status.startswith('hit_tp'):
                if signal.action == 'BUY':
                    if signal.status == 'hit_tp1':
                        pnl = (signal.take_profit_1 - signal.entry_price) / signal.entry_price
                    elif signal.status == 'hit_tp2':
                        pnl = (signal.take_profit_2 - signal.entry_price) / signal.entry_price
                    else:
                        pnl = (signal.take_profit_3 - signal.entry_price) / signal.entry_price
                else:  # SELL
                    if signal.status == 'hit_tp1':
                        pnl = (signal.entry_price - signal.take_profit_1) / signal.entry_price
                    elif signal.status == 'hit_tp2':
                        pnl = (signal.entry_price - signal.take_profit_2) / signal.entry_price
                    else:
                        pnl = (signal.entry_price - signal.take_profit_3) / signal.entry_price
                total_pnl += pnl * signal.position_size_percentage
            elif signal.status == 'stopped':
                pnl = -0.02  # 2% loss per stopped trade
                total_pnl += pnl * signal.position_size_percentage
        
        # Calculate risk score (0-10)
        open_positions = TradingSignal.query.filter_by(status='active').count()
        risk_score = min(open_positions * 1.5, 10)
        
        # API latency
        api_latency = latest_metric.api_response_time * 1000 if latest_metric else 0
        
        return jsonify({
            'success': True,
            'metrics': {
                'active_signals': active_signals,
                'win_rate': round(win_rate, 1),
                'total_pnl': round(total_pnl * 10000, 2),  # Assuming $10k account
                'risk_score': round(risk_score, 1),
                'cache_hit_rate': round(cache_hit_rate, 1),
                'api_latency': round(api_latency, 0),
                'cpu_usage': latest_metric.cpu_usage if latest_metric else 0,
                'memory_usage': latest_metric.memory_usage if latest_metric else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/technical/<symbol>')
def get_technical_analysis(symbol):
    """Get technical analysis for dashboard"""
    try:
        from core.analyzer import TechnicalAnalyzer
        from core.okx_fetcher import OKXAPIManager
        
        # Validate symbol
        valid_symbols = ['BTC', 'ETH', 'SOL', 'TIA', 'RENDER']
        if symbol.upper() not in valid_symbols:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Get data
        api = OKXAPIManager()
        analyzer = TechnicalAnalyzer()
        
        symbol_okx = f"{symbol.upper()}-USDT"
        df = api.get_candles(symbol_okx, '1H', limit=200)
        
        if df is None or df.empty:
            return jsonify({'error': 'Failed to fetch data'}), 500
        
        # Get technical indicators
        indicators = analyzer.analyze(df, symbol_okx, '1H')
        summary = analyzer.get_indicator_summary(indicators)
        
        # Prepare candlestick data for chart
        candle_data = []
        volume_data = []
        for i in range(len(df)):
            candle_data.append({
                'time': int(df.index[i].timestamp()),
                'open': float(df['open'].iloc[i]),
                'high': float(df['high'].iloc[i]),
                'low': float(df['low'].iloc[i]),
                'close': float(df['close'].iloc[i])
            })
            volume_data.append({
                'time': int(df.index[i].timestamp()),
                'value': float(df['volume'].iloc[i]),
                'color': '#00d68f' if df['close'].iloc[i] > df['open'].iloc[i] else '#ff3d71'
            })
        
        # Prepare volume profile data
        vp = indicators.volume_profile
        volume_profile_data = {
            'price_levels': [float(p) for p in vp['price_levels']],
            'volumes': [float(v) for v in vp['volumes']],
            'poc': float(indicators.poc),
            'value_area_high': float(indicators.value_area_high),
            'value_area_low': float(indicators.value_area_low)
        }
        
        # OBV data (last 50 points)
        obv_data = []
        for i in range(max(0, len(df) - 50), len(df)):
            obv_data.append({
                'x': i,
                'y': float(indicators.obv.iloc[i])
            })
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'current_price': float(df['close'].iloc[-1]),
            'technical_summary': summary,
            'candle_data': candle_data[-100:],  # Last 100 candles
            'volume_data': volume_data[-100:],
            'volume_profile': volume_profile_data,
            'obv_data': obv_data,
            'support_resistance': {
                'support': [float(s) for s in indicators.support_levels],
                'resistance': [float(r) for r in indicators.resistance_levels]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting technical analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/risk-metrics')
def get_risk_metrics():
    """Get risk management metrics"""
    try:
        from core.risk_manager import RiskManager
        
        risk_manager = RiskManager()
        
        # Get active positions
        active_signals = TradingSignal.query.filter_by(status='active').all()
        
        total_risk = 0
        open_positions = len(active_signals)
        
        # Calculate total risk exposure
        for signal in active_signals:
            # Risk per trade (difference between entry and stop loss)
            if signal.action == 'BUY':
                risk_per_unit = signal.entry_price - signal.stop_loss
            else:
                risk_per_unit = signal.stop_loss - signal.entry_price
            
            risk_percentage = (risk_per_unit / signal.entry_price) * 100
            total_risk += risk_percentage * signal.position_size_percentage / 100
        
        # Calculate max drawdown from recent trades
        recent_signals = TradingSignal.query.order_by(
            TradingSignal.created_at.desc()
        ).limit(100).all()
        
        cumulative_pnl = 0
        max_cumulative = 0
        max_drawdown = 0
        
        for signal in reversed(recent_signals):
            if signal.status == 'stopped':
                pnl = -2  # 2% loss
            elif signal.status.startswith('hit_tp'):
                # Calculate profit based on which TP was hit
                if signal.action == 'BUY':
                    if signal.status == 'hit_tp1':
                        pnl = ((signal.take_profit_1 - signal.entry_price) / signal.entry_price) * 100
                    elif signal.status == 'hit_tp2':
                        pnl = ((signal.take_profit_2 - signal.entry_price) / signal.entry_price) * 100
                    else:
                        pnl = ((signal.take_profit_3 - signal.entry_price) / signal.entry_price) * 100
                else:  # SELL
                    if signal.status == 'hit_tp1':
                        pnl = ((signal.entry_price - signal.take_profit_1) / signal.entry_price) * 100
                    elif signal.status == 'hit_tp2':
                        pnl = ((signal.entry_price - signal.take_profit_2) / signal.entry_price) * 100
                    else:
                        pnl = ((signal.entry_price - signal.take_profit_3) / signal.entry_price) * 100
            else:
                continue
            
            cumulative_pnl += pnl
            max_cumulative = max(max_cumulative, cumulative_pnl)
            drawdown = max_cumulative - cumulative_pnl
            max_drawdown = max(max_drawdown, drawdown)
        
        return jsonify({
            'success': True,
            'risk_metrics': {
                'total_risk_exposure': round(total_risk, 2),
                'risk_per_trade': 2.0,  # Default 2%
                'max_drawdown': round(max_drawdown, 2),
                'risk_reward_ratio': '1:2',
                'open_positions': open_positions,
                'max_positions': risk_manager.max_positions,
                'current_leverage': 1.0  # No leverage by default
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting risk metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/module-performance')
def get_module_performance():
    """Get performance metrics for each module"""
    try:
        # Get confluence checker performance
        from core.confluence_checker import ConfluenceChecker
        confluence = ConfluenceChecker()
        confluence_perf = confluence.get_historical_performance()
        
        # Count SMC patterns detected
        smc_patterns = 0
        price_action_patterns = 0
        
        # Get recent signals and count pattern types
        recent_signals = TradingSignal.query.order_by(
            TradingSignal.created_at.desc()
        ).limit(100).all()
        
        for signal in recent_signals:
            if signal.pattern_type in ['BOS', 'CHoCH', 'FVG', 'ORDER_BLOCK']:
                smc_patterns += 1
            elif signal.pattern_type in ['PIN_BAR', 'ENGULFING', 'HAMMER', 'DOJI']:
                price_action_patterns += 1
        
        # Calculate accuracy (simplified - based on win rate)
        winning_smc = sum(1 for s in recent_signals 
                         if s.pattern_type in ['BOS', 'CHoCH', 'FVG', 'ORDER_BLOCK'] 
                         and s.status in ['hit_tp1', 'hit_tp2', 'hit_tp3'])
        smc_accuracy = (winning_smc / smc_patterns * 100) if smc_patterns > 0 else 0
        
        winning_pa = sum(1 for s in recent_signals 
                        if s.pattern_type in ['PIN_BAR', 'ENGULFING', 'HAMMER', 'DOJI'] 
                        and s.status in ['hit_tp1', 'hit_tp2', 'hit_tp3'])
        pa_success = (winning_pa / price_action_patterns * 100) if price_action_patterns > 0 else 0
        
        return jsonify({
            'success': True,
            'module_performance': {
                'confluence': {
                    'signals_generated': confluence_perf['total_signals'],
                    'win_rate': confluence_perf['win_rate']
                },
                'smc': {
                    'patterns_detected': smc_patterns,
                    'accuracy': round(smc_accuracy, 1)
                },
                'price_action': {
                    'patterns_found': price_action_patterns,
                    'success_rate': round(pa_success, 1)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting module performance: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/signal-distribution')
def get_signal_distribution():
    """Get signal distribution data"""
    try:
        # Count signals by type
        buy_count = TradingSignal.query.filter_by(action='BUY', status='active').count()
        sell_count = TradingSignal.query.filter_by(action='SELL', status='active').count()
        
        # Count by symbol
        symbol_distribution = {}
        symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'TIA-USDT', 'RENDER-USDT']
        
        for symbol in symbols:
            count = TradingSignal.query.filter_by(symbol=symbol, status='active').count()
            if count > 0:
                symbol_distribution[symbol] = count
        
        return jsonify({
            'success': True,
            'distribution': {
                'by_action': {
                    'buy': buy_count,
                    'sell': sell_count,
                    'neutral': 0
                },
                'by_symbol': symbol_distribution
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting signal distribution: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/advanced/<symbol>')
def get_advanced_analysis(symbol):
    """Get advanced formatted analysis with detailed Indonesian format"""
    try:
        # Import necessary modules
        from core.okx_fetcher import OKXAPIManager
        from core.smc_detector import SMCDetector
        from core.confluence_checker import ConfluenceChecker
        from core.advanced_formatter import AdvancedFormatter
        from core.realtime_streamer import RealtimeDataStreamer, streamer
        import pandas as pd
        import pandas_ta as ta
        
        # Validate symbol
        valid_symbols = ['BTC', 'ETH', 'SOL', 'TIA', 'RENDER']
        if symbol.upper() not in valid_symbols:
            return jsonify({'error': 'Invalid symbol'}), 400
            
        # Initialize components
        okx_api = OKXAPIManager()
        smc_detector = SMCDetector()
        confluence_checker = ConfluenceChecker()
        formatter = AdvancedFormatter()
        
        # Fetch real-time data
        symbol_okx = f"{symbol.upper()}-USDT"
        df = okx_api.get_candles(symbol_okx, timeframe="1H", limit=100)
        
        if df.empty:
            return jsonify({
                'symbol': symbol,
                'status': 'error',
                'message': 'No data available'
            }), 404
            
        # Calculate indicators
        df['rsi'] = ta.rsi(df['close'], length=14)
        df['ema_9'] = ta.ema(df['close'], length=9)
        df['ema_20'] = ta.ema(df['close'], length=20)
        df['ema_50'] = ta.ema(df['close'], length=50)
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        
        # Detect SMC patterns
        smc_patterns = smc_detector.detect_all_patterns(df)
        
        # Check for confluence
        confluence_signal = confluence_checker.analyze_confluence(df, symbol_okx, '1H')
        
        # Prepare data for formatter
        current_price = float(df['close'].iloc[-1])
        price_change_24h = ((current_price - float(df['close'].iloc[-24])) / float(df['close'].iloc[-24])) * 100 if len(df) > 24 else 0
        
        formatter_data = {
            'symbol': symbol_okx,
            'current_price': current_price,
            'timeframe': '1H',
            'trend': 'bullish' if confluence_signal and confluence_signal.action == 'BUY' else 'bearish' if confluence_signal and confluence_signal.action == 'SELL' else 'sideways',
            'signal': {
                'action': confluence_signal.action if confluence_signal else None,
                'entry_price': confluence_signal.entry_price if confluence_signal else 0,
                'stop_loss': confluence_signal.stop_loss if confluence_signal else 0,
                'take_profit_1': confluence_signal.take_profit_1 if confluence_signal else 0,
                'take_profit_2': confluence_signal.take_profit_2 if confluence_signal else 0,
                'take_profit_3': confluence_signal.take_profit_3 if confluence_signal else 0,
                'confidence': confluence_signal.confidence if confluence_signal else 0
            } if confluence_signal else {},
            'smc_analysis': {
                'patterns': [
                    {'type': pattern_type, 'count': len(patterns)} 
                    for pattern_type, patterns in smc_patterns.items() if patterns
                ]
            },
            'indicators': {
                'rsi': float(df['rsi'].iloc[-1]) if not pd.isna(df['rsi'].iloc[-1]) else 50,
                'rsi_4h': float(df['rsi'].iloc[-1]) if not pd.isna(df['rsi'].iloc[-1]) else 50,
                'volume_trend': 'high' if float(df['volume'].iloc[-1]) > df['volume'].mean() * 1.5 else 'normal',
                'macd_bullish': confluence_signal.action == 'BUY' if confluence_signal else False,
                'ema': {
                    'above_50': float(df['close'].iloc[-1]) > float(df['ema_50'].iloc[-1]) if not pd.isna(df['ema_50'].iloc[-1]) else True,
                    'spread': abs(float(df['ema_9'].iloc[-1]) - float(df['ema_20'].iloc[-1])) if not pd.isna(df['ema_9'].iloc[-1]) else 0
                }
            },
            'orderbook': {
                'bid_dominance': 52.5,  # Placeholder
                'ask_walls': [
                    {'price': current_price * 1.02, 'size': 3500000},
                    {'price': current_price * 1.03, 'size': 5200000}
                ],
                'bid_walls': [
                    {'price': current_price * 0.98, 'size': 4200000},
                    {'price': current_price * 0.97, 'size': 6100000}
                ]
            },
            'liquidation_heatmap': {
                'clusters': [
                    {'price': current_price * 1.015, 'is_target': True},
                    {'price': current_price * 0.985, 'is_target': False}
                ]
            },
            'long_short_ratio': {
                'long_percentage': 52.0,
                'short_percentage': 48.0
            },
            'volume_confirmation': float(df['volume'].iloc[-1]) > df['volume'].mean() * 1.2,
            'key_levels': [
                confluence_signal.take_profit_1 if confluence_signal else current_price * 1.02,
                confluence_signal.take_profit_2 if confluence_signal else current_price * 1.04
            ],
            'confidence': confluence_signal.confidence if confluence_signal else 0
        }
        
        # Generate formatted analysis
        formatted_analysis = formatter.format_complete_analysis(formatter_data)
        
        # Save analysis to database
        try:
            # Calculate SMC patterns count
            smc_patterns_count = {}
            for pattern_type, patterns in smc_patterns.items():
                if patterns:
                    smc_patterns_count[pattern_type] = len(patterns)
            
            # Determine trend
            ema_20 = float(df['ema_20'].iloc[-1]) if 'ema_20' in df.columns and not pd.isna(df['ema_20'].iloc[-1]) else current_price
            ema_50 = float(df['ema_50'].iloc[-1]) if 'ema_50' in df.columns and not pd.isna(df['ema_50'].iloc[-1]) else current_price
            ema_trend = "bullish" if ema_20 > ema_50 else "bearish" if ema_20 < ema_50 else "neutral"
            
            # Determine volume trend
            recent_volume = df['volume'].tail(5).mean()
            older_volume = df['volume'].tail(20).head(15).mean()
            volume_trend = "increasing" if recent_volume > older_volume * 1.2 else "decreasing" if recent_volume < older_volume * 0.8 else "stable"
            
            # Create new analysis record
            analysis = TradingAnalysis(
                symbol=symbol.upper(),
                timeframe='1H',
                analysis_type='advanced',
                current_price=current_price,
                price_change_24h=price_change_24h,
                has_signal=bool(confluence_signal),
                signal_action=confluence_signal.action if confluence_signal else None,
                signal_confidence=confluence_signal.confidence if confluence_signal else None,
                entry_price=confluence_signal.entry_price if confluence_signal else None,
                stop_loss=confluence_signal.stop_loss if confluence_signal else None,
                take_profit_1=confluence_signal.take_profit_1 if confluence_signal else None,
                take_profit_2=confluence_signal.take_profit_2 if confluence_signal else None,
                take_profit_3=confluence_signal.take_profit_3 if confluence_signal else None,
                smc_patterns_detected=smc_patterns_count,
                rsi_value=float(df['rsi'].iloc[-1]) if not pd.isna(df['rsi'].iloc[-1]) else None,
                ema_trend=ema_trend,
                volume_trend=volume_trend,
                formatted_analysis=formatted_analysis,
                user_ip=request.remote_addr
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            logger.info(f"Saved analysis for {symbol} to database with ID {analysis.id}")
            
        except Exception as e:
            logger.error(f"Error saving analysis to database: {e}")
            db.session.rollback()
        
        # Calculate technical indicators for dashboard
        rsi_value = float(df['rsi'].iloc[-1]) if not pd.isna(df['rsi'].iloc[-1]) else 50
        
        # Calculate MACD
        macd = ta.macd(df['close'])
        macd_value = float(macd['MACD_12_26_9'].iloc[-1]) if not pd.isna(macd['MACD_12_26_9'].iloc[-1]) else 0
        macd_signal = float(macd['MACDs_12_26_9'].iloc[-1]) if not pd.isna(macd['MACDs_12_26_9'].iloc[-1]) else 0
        macd_diff = macd_value - macd_signal
        
        # Calculate Stochastic
        stoch = ta.stoch(df['high'], df['low'], df['close'])
        stoch_k = float(stoch['STOCHk_14_3_3'].iloc[-1]) if not pd.isna(stoch['STOCHk_14_3_3'].iloc[-1]) else 50
        stoch_d = float(stoch['STOCHd_14_3_3'].iloc[-1]) if not pd.isna(stoch['STOCHd_14_3_3'].iloc[-1]) else 50
        
        # Calculate ATR
        atr_value = float(df['atr'].iloc[-1]) if not pd.isna(df['atr'].iloc[-1]) else 1.5
        
        # Calculate orderbook (simulated)
        bid_percent = 45 + (hash(symbol) % 20)
        
        return jsonify({
            'symbol': symbol,
            'status': 'success',
            'currentPrice': current_price,
            'priceChange24h': round(price_change_24h, 2),
            'hasSignal': confluence_signal is not None,
            'formattedAnalysis': formatted_analysis,
            'bidPercent': bid_percent,
            'rsiValue': rsi_value,
            'macdValue': macd_diff,
            'stochK': stoch_k,
            'stochD': stoch_d,
            'atrValue': atr_value,
            'rawData': {
                'patterns': len(smc_patterns),
                'confidence': confluence_signal.confidence if confluence_signal else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error in advanced analysis for {symbol}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/analysis/history/<symbol>')
def get_analysis_history(symbol):
    """Get historical analysis for a symbol"""
    try:
        # Get limit from query params, default 20
        limit = request.args.get('limit', 20, type=int)
        
        # Query historical analysis
        analyses = TradingAnalysis.query.filter_by(
            symbol=symbol.upper()
        ).order_by(
            TradingAnalysis.created_at.desc()
        ).limit(limit).all()
        
        # Format response
        history = []
        for analysis in analyses:
            history.append({
                'id': analysis.id,
                'created_at': analysis.created_at.isoformat(),
                'current_price': analysis.current_price,
                'price_change_24h': analysis.price_change_24h,
                'has_signal': analysis.has_signal,
                'signal_action': analysis.signal_action,
                'signal_confidence': analysis.signal_confidence,
                'entry_price': analysis.entry_price,
                'stop_loss': analysis.stop_loss,
                'take_profit_1': analysis.take_profit_1,
                'smc_patterns': analysis.smc_patterns_detected,
                'rsi_value': analysis.rsi_value,
                'ema_trend': analysis.ema_trend,
                'volume_trend': analysis.volume_trend
            })
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'count': len(history),
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Error getting analysis history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced-ai/narrative/<symbol>')
def get_enhanced_ai_narrative(symbol):
    """Get enhanced AI narrative for a symbol using advanced AI engine"""
    try:
        from core.analyzer import TechnicalAnalyzer
        from core.okx_fetcher import OKXAPIManager
        
        # Validate symbol
        valid_symbols = ['BTC', 'ETH', 'SOL', 'TIA', 'RENDER']
        if symbol.upper() not in valid_symbols:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Get parameters
        language = request.args.get('language', 'indonesian')
        quick_mode = request.args.get('quick', 'false').lower() == 'true'
        
        # Get data and analyze
        api = OKXAPIManager()
        analyzer = TechnicalAnalyzer()
        
        symbol_okx = f"{symbol.upper()}-USDT"
        df = api.get_candles(symbol_okx, '1H', limit=200)
        
        if df is None or df.empty:
            return jsonify({'error': 'Failed to fetch market data'}), 500
        
        # Get comprehensive analysis
        analysis_data = analyzer.analyze(df, symbol_okx, '1H')
        
        # Generate enhanced AI narrative
        narrative = analyzer.generate_enhanced_ai_narrative(
            analysis_data=analysis_data,
            language=language,
            quick_mode=quick_mode
        )
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'language': language,
            'quick_mode': quick_mode,
            'narrative': narrative,
            'generated_at': datetime.now().replace(microsecond=0).isoformat(),
            'current_price': analysis_data.get('current_price', 0)
        })
        
    except Exception as e:
        logger.error(f"Error generating enhanced AI narrative for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced-ai/stats')
def get_enhanced_ai_stats():
    """Get enhanced AI engine statistics"""
    try:
        from core.analyzer import TechnicalAnalyzer
        
        analyzer = TechnicalAnalyzer()
        stats = analyzer.get_enhanced_ai_stats()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'retrieved_at': datetime.now().replace(microsecond=0).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting enhanced AI stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced-ai/test-connection')
def test_enhanced_ai_connection():
    """Test enhanced AI connection"""
    try:
        from core.analyzer import TechnicalAnalyzer
        
        analyzer = TechnicalAnalyzer()
        connection_status = analyzer.test_enhanced_ai_connection()
        
        return jsonify({
            'success': True,
            'connection_test': connection_status,
            'tested_at': datetime.now().replace(microsecond=0).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error testing enhanced AI connection: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced-charts/data/<symbol>')
def get_enhanced_chart_data(symbol):
    """Get comprehensive chart data for enhanced Plotly.js charts"""
    try:
        # Validate symbol
        valid_symbols = ['BTC', 'ETH', 'SOL', 'TIA', 'RENDER']
        if symbol.upper() not in valid_symbols:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Get parameters
        timeframe = request.args.get('timeframe', '1H')
        limit = request.args.get('limit', 200, type=int)
        
        # Get data using common imports
        api = OKXAPIManager()
        analyzer = TechnicalAnalyzer()
        
        symbol_okx = f"{symbol.upper()}-USDT"
        df = api.get_candles(symbol_okx, timeframe, limit=limit)
        
        if df is None or df.empty:
            return jsonify({'error': 'Failed to fetch market data'}), 500
        
        # Get comprehensive analysis
        analysis = analyzer.analyze(df, symbol_okx, timeframe)
        
        # Use helper functions for data preparation
        candlestick_data = prepare_candlestick_data(df)
        indicators = analysis.get('indicators', {})
        smc_analysis = analysis.get('smc_analysis', {})
        support_levels, resistance_levels = prepare_support_resistance_levels(df)
        smc_levels = prepare_smc_levels(smc_analysis, df)
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'timeframe': timeframe,
            'data': candlestick_data,
            'indicators': {
                'rsi': indicators.get('rsi', {}),
                'macd': indicators.get('macd', {}),
                'ema': indicators.get('ema', {}),
                'bollinger': indicators.get('bollinger', {}),
                'volume': indicators.get('volume', {})
            },
            'smc_analysis': smc_analysis,
            'support_levels': support_levels,
            'resistance_levels': resistance_levels,
            'smc_levels': smc_levels,
            'current_price': float(df['close'].iloc[-1]),
            'price_change_24h': analysis.get('price_change_24h', 0),
            'generated_at': datetime.now().replace(microsecond=0).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting enhanced chart data for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced-charts/volume-profile/<symbol>')
def get_volume_profile_data(symbol):
    """Get volume profile data for enhanced charts"""
    try:
        from core.analyzer import TechnicalAnalyzer
        from core.okx_fetcher import OKXAPIManager
        
        # Validate symbol
        valid_symbols = ['BTC', 'ETH', 'SOL', 'TIA', 'RENDER']
        if symbol.upper() not in valid_symbols:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Get data
        api = OKXAPIManager()
        analyzer = TechnicalAnalyzer()
        
        symbol_okx = f"{symbol.upper()}-USDT"
        df = api.get_candles(symbol_okx, '1H', limit=200)
        
        if df is None or df.empty:
            return jsonify({'error': 'Failed to fetch market data'}), 500
        
        # Calculate volume profile
        price_range = df['high'].max() - df['low'].min()
        price_levels = []
        volumes = []
        
        # Create price bins
        num_bins = 50
        bin_size = price_range / num_bins
        
        for i in range(num_bins):
            price_level = df['low'].min() + (i * bin_size)
            price_levels.append(price_level)
            
            # Calculate volume at this price level
            volume_at_level = 0
            for j in range(len(df)):
                if df['low'].iloc[j] <= price_level <= df['high'].iloc[j]:
                    volume_at_level += df['volume'].iloc[j]
            
            volumes.append(volume_at_level)
        
        # Find Point of Control (POC) - price level with highest volume
        max_volume_index = volumes.index(max(volumes))
        poc = price_levels[max_volume_index]
        
        # Calculate Value Area (70% of volume)
        total_volume = sum(volumes)
        value_area_volume = total_volume * 0.7
        
        # Find value area high and low
        sorted_volumes = sorted(enumerate(volumes), key=lambda x: x[1], reverse=True)
        cumulative_volume = 0
        value_area_indices = []
        
        for idx, vol in sorted_volumes:
            cumulative_volume += vol
            value_area_indices.append(idx)
            if cumulative_volume >= value_area_volume:
                break
        
        value_area_high = max([price_levels[i] for i in value_area_indices])
        value_area_low = min([price_levels[i] for i in value_area_indices])
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'volume_profile': {
                'price_levels': price_levels,
                'volumes': volumes,
                'poc': poc,
                'value_area_high': value_area_high,
                'value_area_low': value_area_low,
                'total_volume': total_volume
            },
            'generated_at': datetime.now().replace(microsecond=0).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting volume profile data for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/realtime/market-overview')
def get_market_overview():
    """Get real-time market overview"""
    try:
        streamer = get_realtime_streamer()
        overview = streamer.get_market_overview()
        return jsonify(overview)
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/realtime/streaming-stats')
def get_streaming_stats():
    """Get real-time streaming statistics"""
    try:
        streamer = get_realtime_streamer()
        stats = streamer.get_streaming_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        logger.error(f"Error getting streaming stats: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/realtime/start-streaming')
def start_streaming():
    """Start real-time streaming"""
    try:
        streamer = get_realtime_streamer()
        streamer.start_streaming()
        return jsonify({'success': True, 'message': 'Real-time streaming started'})
    except Exception as e:
        logger.error(f"Error starting streaming: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/realtime/stop-streaming')
def stop_streaming():
    """Stop real-time streaming"""
    try:
        streamer = get_realtime_streamer()
        streamer.stop_streaming()
        return jsonify({'success': True, 'message': 'Real-time streaming stopped'})
    except Exception as e:
        logger.error(f"Error stopping streaming: {e}")
        return jsonify({'success': False, 'error': str(e)})

# =======================================================================
# NEW ENDPOINTS FOR PHASE 1 INTEGRATED MODELS
# =======================================================================

@app.route('/api/market-data/<symbol>')
def get_market_data(symbol):
    """Get market data (candlestick) for a symbol"""
    try:
        # Get query parameters
        timeframe = request.args.get('timeframe', '1h')
        limit = request.args.get('limit', 100, type=int)
        
        # Validate symbol
        if not symbol or len(symbol) < 3:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Query market data
        query = MarketData.query.filter_by(symbol=symbol.upper(), timeframe=timeframe)
        query = query.order_by(MarketData.timestamp.desc()).limit(limit)
        
        market_data = query.all()
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'timeframe': timeframe,
            'count': len(market_data),
            'data': [data.to_dict() for data in market_data]
        })
        
    except Exception as e:
        logger.error(f"Error getting market data for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/open-interest/<symbol>')
def get_open_interest(symbol):
    """Get open interest data for a symbol"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        
        # Validate symbol
        if not symbol or len(symbol) < 3:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Query open interest data
        query = OpenInterestData.query.filter_by(symbol=symbol.upper())
        query = query.order_by(OpenInterestData.timestamp.desc()).limit(limit)
        
        oi_data = query.all()
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'count': len(oi_data),
            'data': [data.to_dict() for data in oi_data]
        })
        
    except Exception as e:
        logger.error(f"Error getting open interest data for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

# Removed duplicate endpoint - enhanced version already exists above

# Removed duplicate endpoint - enhanced version already exists above

@app.route('/api/user-preferences/<session_id>')
def get_user_preferences(session_id):
    """Get user preferences for a session"""
    try:
        # Query user preferences
        preferences = UserPreferences.query.filter_by(session_id=session_id).first()
        
        if not preferences:
            return jsonify({'error': 'No preferences found for this session'}), 404
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'preferences': preferences.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting user preferences for {session_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-preferences/<session_id>', methods=['POST'])
def save_user_preferences(session_id):
    """Save or update user preferences"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Find existing preferences or create new
        preferences = UserPreferences.query.filter_by(session_id=session_id).first()
        
        if preferences:
            # Update existing preferences
            preferences.preferred_symbol = data.get('preferred_symbol', preferences.preferred_symbol)
            preferences.preferred_timeframe = data.get('preferred_timeframe', preferences.preferred_timeframe)
            preferences.preferred_limit = data.get('preferred_limit', preferences.preferred_limit)
            preferences.auto_refresh = data.get('auto_refresh', preferences.auto_refresh)
            preferences.updated_at = datetime.utcnow()
        else:
            # Create new preferences
            preferences = UserPreferences(
                session_id=session_id,
                preferred_symbol=data.get('preferred_symbol', 'BTC-USDT'),
                preferred_timeframe=data.get('preferred_timeframe', '1h'),
                preferred_limit=data.get('preferred_limit', 100),
                auto_refresh=data.get('auto_refresh', True)
            )
            db.session.add(preferences)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'preferences': preferences.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error saving user preferences for {session_id}: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-snapshots/<symbol>')
def get_ai_snapshots(symbol):
    """Get AI snapshots for a symbol"""
    try:
        # Get query parameters
        timeframe = request.args.get('timeframe', '1h')
        limit = request.args.get('limit', 50, type=int)
        session_id = request.args.get('session_id', None)
        
        # Validate symbol
        if not symbol or len(symbol) < 3:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Standardize symbol format to BTC-USDT
        symbol_formatted = f"{symbol.upper()}-USDT" if not symbol.upper().endswith('-USDT') else symbol.upper()
        
        # Build query
        query = AISnapshotArchive.query.filter_by(symbol=symbol_formatted, timeframe=timeframe)
        
        if session_id:
            query = query.filter_by(session_id=session_id)
        
        query = query.order_by(AISnapshotArchive.created_at.desc()).limit(limit)
        
        snapshots = query.all()
        
        return jsonify({
            'success': True,
            'symbol': symbol_formatted,
            'timeframe': timeframe,
            'session_id': session_id,
            'count': len(snapshots),
            'data': [snapshot.to_dict() for snapshot in snapshots]
        })
        
    except Exception as e:
        logger.error(f"Error getting AI snapshots for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-snapshots', methods=['POST'])
def create_ai_snapshot():
    """Create a new AI snapshot"""
    try:
        data = request.get_json()
        
        if not data or 'symbol' not in data:
            return jsonify({'error': 'Symbol is required'}), 400
        
        # Standardize symbol format to BTC-USDT
        symbol = data['symbol'].upper()
        symbol_formatted = f"{symbol}-USDT" if not symbol.endswith('-USDT') else symbol
        
        # Create new AI snapshot
        snapshot = AISnapshotArchive(
            session_id=data.get('session_id', 'anonymous'),
            symbol=symbol_formatted,
            timeframe=data.get('timeframe', '1h'),
            quick_mode=data.get('quick_mode', False),
            ai_narrative=data.get('ai_narrative', ''),
            confluence_summary=data.get('confluence_summary', {}),
            layer_analysis=data.get('layer_analysis', {}),
            snapshot_data=data.get('snapshot_data', {}),
            confidence=data.get('confidence', 0.0)
        )
        
        db.session.add(snapshot)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'AI snapshot created successfully',
            'snapshot_id': snapshot.id,
            'snapshot': snapshot.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error creating AI snapshot: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =======================================================================
# PHASE 2: ADVANCED SNAPSHOT AND INDICATOR ENDPOINTS
# =======================================================================

@app.route('/api/snapshots/generate/<symbol>')
def generate_market_snapshot(symbol):
    """Generate comprehensive market snapshot"""
    try:
        from core.snapshot_generator import snapshot_generator, SnapshotType
        
        # Get parameters
        timeframe = request.args.get('timeframe', '1H')
        snapshot_type = request.args.get('type', 'comprehensive')
        session_id = request.args.get('session_id', 'api_user')
        
        # Validate symbol
        if not symbol or len(symbol) < 3:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Convert snapshot type
        if snapshot_type == 'quick':
            snap_type = SnapshotType.QUICK
        elif snapshot_type == 'deep':
            snap_type = SnapshotType.DEEP_ANALYSIS
        else:
            snap_type = SnapshotType.COMPREHENSIVE
        
        # Generate snapshot
        snapshot = snapshot_generator.generate_snapshot(
            symbol=f"{symbol.upper()}-USDT",
            timeframe=timeframe,
            snapshot_type=snap_type,
            session_id=session_id
        )
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'timeframe': timeframe,
            'snapshot_type': snapshot_type,
            'snapshot': snapshot.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error generating snapshot for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/snapshots/statistics')
def get_snapshot_statistics():
    """Get snapshot statistics"""
    try:
        from core.snapshot_archiver import snapshot_archiver
        
        symbol = request.args.get('symbol', None)
        timeframe = request.args.get('timeframe', None)
        
        # Standardize symbol format if provided
        if symbol:
            symbol = f"{symbol.upper()}-USDT" if not symbol.upper().endswith('-USDT') else symbol.upper()
        
        stats = snapshot_archiver.get_snapshot_statistics(symbol, timeframe)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting snapshot statistics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/snapshots/comparative/<symbol>')
def get_comparative_analysis(symbol):
    """Get comparative analysis over time"""
    try:
        from core.snapshot_archiver import snapshot_archiver
        
        days = request.args.get('days', 7, type=int)
        
        # Validate symbol
        if not symbol or len(symbol) < 3:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Standardize symbol format to BTC-USDT
        symbol_formatted = f"{symbol.upper()}-USDT" if not symbol.upper().endswith('-USDT') else symbol.upper()
        
        analysis = snapshot_archiver.get_comparative_analysis(symbol_formatted, days)
        
        return jsonify({
            'success': True,
            'symbol': symbol_formatted,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error getting comparative analysis for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/snapshots/export')
def export_snapshots():
    """Export snapshots to JSON"""
    try:
        from core.snapshot_archiver import snapshot_archiver
        
        symbol = request.args.get('symbol', None)
        timeframe = request.args.get('timeframe', None)
        
        # Standardize symbol format if provided
        if symbol:
            symbol = f"{symbol.upper()}-USDT" if not symbol.upper().endswith('-USDT') else symbol.upper()
        
        filepath = snapshot_archiver.export_snapshots_to_json(symbol, timeframe)
        
        if filepath:
            return jsonify({
                'success': True,
                'message': 'Snapshots exported successfully',
                'filepath': filepath
            })
        else:
            return jsonify({'error': 'Export failed'}), 500
        
    except Exception as e:
        logger.error(f"Error exporting snapshots: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/snapshots/pdf-report/<symbol>')
def generate_pdf_report(symbol):
    """Generate PDF report for symbol"""
    try:
        from core.snapshot_archiver import snapshot_archiver
        
        timeframe = request.args.get('timeframe', '1H')
        snapshot_id = request.args.get('snapshot_id', None, type=int)
        
        # Validate symbol
        if not symbol or len(symbol) < 3:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Standardize symbol format to BTC-USDT
        symbol_formatted = f"{symbol.upper()}-USDT" if not symbol.upper().endswith('-USDT') else symbol.upper()
        
        pdf_path = snapshot_archiver.generate_pdf_report(
            symbol_formatted, timeframe, snapshot_id
        )
        
        if pdf_path:
            return jsonify({
                'success': True,
                'message': 'PDF report generated successfully',
                'pdf_path': pdf_path
            })
        else:
            return jsonify({'error': 'PDF generation failed'}), 500
        
    except Exception as e:
        logger.error(f"Error generating PDF report for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/snapshots/cleanup')
def cleanup_old_snapshots():
    """Cleanup old snapshots"""
    try:
        from core.snapshot_archiver import snapshot_archiver
        
        days = request.args.get('days', 30, type=int)
        
        deleted_count = snapshot_archiver.cleanup_old_snapshots(days)
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {deleted_count} old snapshots',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up snapshots: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/indicators/calculate/<symbol>')
def calculate_technical_indicators(symbol):
    """Calculate technical indicators for symbol"""
    try:
        from core.indicator_calculator import indicator_calculator
        from core.okx_fetcher import OKXAPIManager
        
        # Get parameters
        timeframe = request.args.get('timeframe', '1H')
        indicators = request.args.get('indicators', '').split(',')
        
        # Validate symbol
        if not symbol or len(symbol) < 3:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Get market data
        api_manager = OKXAPIManager()
        df = api_manager.get_candles(f"{symbol.upper()}-USDT", timeframe, limit=200)
        
        if df is None or df.empty:
            return jsonify({'error': 'No market data available'}), 500
        
        # Calculate indicators
        if indicators and indicators[0]:  # If specific indicators requested
            results = {}
            for indicator in indicators:
                if indicator.strip():
                    try:
                        result = indicator_calculator.calculate_indicator(df, indicator.strip())
                        results[indicator.strip()] = {
                            'name': result.name,
                            'type': result.type.value,
                            'signal': result.signal,
                            'strength': result.strength,
                            'description': result.description,
                            'parameters': result.parameters
                        }
                    except Exception as e:
                        logger.error(f"Error calculating indicator {indicator}: {e}")
                        results[indicator.strip()] = {'error': str(e)}
        else:
            # Calculate all indicators
            results = indicator_calculator.calculate_all_indicators(df)
            results = {name: {
                'name': result.name,
                'type': result.type.value,
                'signal': result.signal,
                'strength': result.strength,
                'description': result.description,
                'parameters': result.parameters
            } for name, result in results.items()}
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'timeframe': timeframe,
            'indicators': results
        })
        
    except Exception as e:
        logger.error(f"Error calculating indicators for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/indicators/signals/<symbol>')
def get_indicator_signals(symbol):
    """Get trading signals from indicators"""
    try:
        from core.indicator_calculator import indicator_calculator
        from core.okx_fetcher import OKXAPIManager
        
        # Get parameters
        timeframe = request.args.get('timeframe', '1H')
        confidence_threshold = request.args.get('confidence', 0.6, type=float)
        
        # Validate symbol
        if not symbol or len(symbol) < 3:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Get market data
        api_manager = OKXAPIManager()
        df = api_manager.get_candles(f"{symbol.upper()}-USDT", timeframe, limit=200)
        
        if df is None or df.empty:
            return jsonify({'error': 'No market data available'}), 500
        
        # Get signals
        signals = indicator_calculator.get_indicator_signals(df, confidence_threshold)
        
        # Calculate overall signal
        buy_signals = [s for s in signals.values() if s.get('signal') == 'BUY']
        sell_signals = [s for s in signals.values() if s.get('signal') == 'SELL']
        
        if len(buy_signals) > len(sell_signals):
            overall_signal = 'BUY'
            overall_strength = sum(s.get('strength', 0) for s in buy_signals) / len(buy_signals)
        elif len(sell_signals) > len(buy_signals):
            overall_signal = 'SELL'
            overall_strength = sum(s.get('strength', 0) for s in sell_signals) / len(sell_signals)
        else:
            overall_signal = 'NEUTRAL'
            overall_strength = 0.5
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'timeframe': timeframe,
            'overall_signal': overall_signal,
            'overall_strength': overall_strength,
            'confidence_threshold': confidence_threshold,
            'signals': signals
        })
        
    except Exception as e:
        logger.error(f"Error getting indicator signals for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/indicators/cache')
def get_indicator_cache_info():
    """Get indicator cache information"""
    try:
        from core.indicator_calculator import indicator_calculator
        
        cache_info = indicator_calculator.get_cache_info()
        
        return jsonify({
            'success': True,
            'cache_info': cache_info
        })
        
    except Exception as e:
        logger.error(f"Error getting cache info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/indicators/cache/clear', methods=['POST'])
def clear_indicator_cache():
    """Clear indicator cache"""
    try:
        from core.indicator_calculator import indicator_calculator
        
        indicator_calculator.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Indicator cache cleared successfully'
        })
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/detail/<int:analysis_id>')
def get_analysis_detail(analysis_id):
    """Get full analysis detail by ID"""
    try:
        analysis = TradingAnalysis.query.get_or_404(analysis_id)
        
        return jsonify({
            'success': True,
            'analysis': {
                'id': analysis.id,
                'symbol': analysis.symbol,
                'created_at': analysis.created_at.isoformat(),
                'current_price': analysis.current_price,
                'price_change_24h': analysis.price_change_24h,
                'has_signal': analysis.has_signal,
                'signal_action': analysis.signal_action,
                'signal_confidence': analysis.signal_confidence,
                'entry_price': analysis.entry_price,
                'stop_loss': analysis.stop_loss,
                'take_profit_1': analysis.take_profit_1,
                'take_profit_2': analysis.take_profit_2,
                'take_profit_3': analysis.take_profit_3,
                'smc_patterns': analysis.smc_patterns_detected,
                'rsi_value': analysis.rsi_value,
                'ema_trend': analysis.ema_trend,
                'volume_trend': analysis.volume_trend,
                'formatted_analysis': analysis.formatted_analysis
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting analysis detail: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/analysis-history')
def analysis_history_page():
    """Page to view historical analyses"""
    return render_template('analysis_history.html')

@app.route('/professional-dashboard')
def professional_dashboard():
    """Professional trading dashboard with modern UI"""
    return render_template('professional_dashboard.html')

@app.route('/react-dashboard')
def react_dashboard():
    """New React-based trading dashboard"""
    return render_template('react_dashboard.html')

@app.route('/')
def index():
    """Default route showing React dashboard"""
    return render_template('react_dashboard.html')

@app.route('/phase2-dashboard')
def phase2_dashboard():
    """Phase 2 Advanced Trading Dashboard with enhanced features"""
    return render_template('phase2_advanced_dashboard.html')

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get today's analysis count
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = TradingAnalysis.query.filter(
            TradingAnalysis.created_at >= today_start
        ).count()
        
        # Get most active pair
        most_active = db.session.query(
            TradingAnalysis.symbol,
            db.func.count(TradingAnalysis.id).label('count')
        ).group_by(TradingAnalysis.symbol).order_by(db.func.count(TradingAnalysis.id).desc()).first()
        
        # Get signal count
        active_signals = TradingSignal.query.filter_by(status='active').count()
        
        # Calculate accuracy (mock for now)
        total_signals = TradingSignal.query.count()
        successful_signals = TradingSignal.query.filter(
            TradingSignal.status.in_(['hit_tp1', 'hit_tp2', 'hit_tp3'])
        ).count()
        
        accuracy = (successful_signals / total_signals * 100) if total_signals > 0 else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'totalAnalysisToday': today_count,
                'activePair': most_active.symbol if most_active else 'N/A',
                'activeSignals': active_signals,
                'signalAccuracy': f"{accuracy:.1f}%"
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500
