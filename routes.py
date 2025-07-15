from flask import render_template, jsonify, request
from app import app, db
from models import TradingSignal, SystemMetrics, AlertLog, TradingAnalysis
from datetime import datetime, timedelta, timezone
from config import Config
import logging
from core.narrative_ai import NarrativeAI

logger = logging.getLogger(__name__)

# Initialize Narrative AI
narrative_ai = NarrativeAI()

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Main trading dashboard"""
    return render_template('dashboard.html')

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
def analyze_coin(symbol):
    """Perform real-time analysis for a specific coin"""
    try:
        # Import necessary modules
        from core.okx_fetcher import OKXAPIManager
        from core.analyzer import TechnicalAnalyzer
        from core.confluence_checker import ConfluenceChecker
        from core.narrative_ai import NarrativeAI
        from core.advanced_formatter import AdvancedFormatter
        import pandas as pd
        
        # Validate symbol
        valid_symbols = ['BTC', 'ETH', 'SOL', 'TIA', 'RENDER']
        if symbol.upper() not in valid_symbols:
            return jsonify({'error': 'Invalid symbol'}), 400
            
        # Initialize components
        okx_api = OKXAPIManager()
        analyzer = TechnicalAnalyzer()
        confluence_checker = ConfluenceChecker()
        narrative_ai = NarrativeAI()
        formatter = AdvancedFormatter()
        
        # Fetch real-time data
        symbol_okx = f"{symbol.upper()}-USDT"
        df = okx_api.get_candles(symbol_okx, timeframe="1H", limit=100)
        
        if df is None or df.empty:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch market data',
                'symbol': symbol
            }), 500
            
        # Run technical analysis
        analysis = analyzer.analyze(df, symbol_okx, '1H')
        
        # Check confluence
        confluence_data = confluence_checker.check_confluence(analysis)
        
        # Generate formatted analysis
        formatted_analysis = formatter.format_analysis(analysis)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'analysis': analysis,
            'confluence': confluence_data,
            'formatted_analysis': formatted_analysis
        })
        
    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
        
        # Generate narrative
        language = request.args.get('lang', 'id')  # Default to Indonesian
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
