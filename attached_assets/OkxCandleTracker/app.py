import os
import logging
import io
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from okx_service import OKXService
from technical_indicators import TechnicalIndicators
from signal_engine import SignalEngine
from database_service import DatabaseService
from snapshot_generator import SnapshotGenerator
from models import db, MarketData, OrderbookData, OpenInterestData, TechnicalIndicatorData, UserPreferences, AISnapshotArchive
from snapshot_archiver import simpan_snapshot_ai, get_snapshot_archive, get_snapshot_by_id, delete_snapshot, get_snapshot_statistics

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)

# Initialize services
okx_service = OKXService()
tech_indicators = TechnicalIndicators()
signal_engine = SignalEngine()
db_service = DatabaseService()
snapshot_generator = SnapshotGenerator()

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Main dashboard page"""
    # Load user preferences if available
    if 'user_id' not in session:
        import uuid
        session['user_id'] = str(uuid.uuid4())
    
    user_prefs = db_service.get_user_preferences(session['user_id'])
    
    return render_template('index.html', user_prefs=user_prefs)

@app.route('/plotly')
def plotly_index():
    """Plotly.js candlestick chart page"""
    return render_template('plotly_index.html')

@app.route('/api/candlestick/<symbol>/<timeframe>')
def get_candlestick(symbol, timeframe):
    """Get candlestick data for a symbol and timeframe"""
    try:
        limit = request.args.get('limit', '100', type=int)
        use_cache = request.args.get('cache', 'true').lower() == 'true'
        
        # Try to get from database first if cache is enabled
        if use_cache:
            cached_data = db_service.get_market_data(symbol, timeframe, limit)
            if cached_data:
                return jsonify({
                    'success': True,
                    'data': cached_data,
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'source': 'cache'
                })
        
        # Get fresh data from API
        data = okx_service.get_candlestick_data(symbol, timeframe, limit)
        
        if not data:
            return jsonify({'error': 'No data available for the specified parameters'}), 404
        
        # Ensure all timestamps are integers before saving
        for item in data:
            if isinstance(item.get('timestamp'), str):
                item['timestamp'] = int(item['timestamp'])
        
        # Save to database for caching
        db_service.save_market_data(symbol, timeframe, data)
            
        return jsonify({
            'success': True,
            'data': data,
            'symbol': symbol,
            'timeframe': timeframe,
            'source': 'api'
        })
    except Exception as e:
        logging.error(f"Error fetching candlestick data: {str(e)}")
        return jsonify({'error': f'Failed to fetch candlestick data: {str(e)}'}), 500

@app.route('/api/orderbook/<symbol>')
def get_orderbook(symbol):
    """Get orderbook data for a symbol"""
    try:
        depth = request.args.get('depth', '50', type=int)
        use_cache = request.args.get('cache', 'false').lower() == 'true'
        
        # Try to get from database first if cache is enabled
        if use_cache:
            cached_data = db_service.get_latest_orderbook_data(symbol)
            if cached_data:
                return jsonify({
                    'success': True,
                    'data': cached_data,
                    'symbol': symbol,
                    'source': 'cache'
                })
        
        # Get fresh data from API
        data = okx_service.get_orderbook_data(symbol, depth)
        
        if not data:
            return jsonify({'error': 'No orderbook data available'}), 404
        
        # Ensure timestamp is integer
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = int(data['timestamp'])
        
        # Save to database for caching
        db_service.save_orderbook_data(symbol, data)
            
        return jsonify({
            'success': True,
            'data': data,
            'symbol': symbol,
            'source': 'api'
        })
    except Exception as e:
        logging.error(f"Error fetching orderbook data: {str(e)}")
        return jsonify({'error': f'Failed to fetch orderbook data: {str(e)}'}), 500

@app.route('/api/open-interest/<symbol>')
def get_open_interest(symbol):
    """Get open interest data for a symbol"""
    try:
        data = okx_service.get_open_interest_data(symbol)
        
        if not data:
            return jsonify({'error': 'No open interest data available'}), 404
            
        return jsonify({
            'success': True,
            'data': data,
            'symbol': symbol
        })
    except Exception as e:
        logging.error(f"Error fetching open interest data: {str(e)}")
        return jsonify({'error': f'Failed to fetch open interest data: {str(e)}'}), 500

@app.route('/api/technical-indicators/<symbol>/<timeframe>')
def get_technical_indicators(symbol, timeframe):
    """Get technical indicators for a symbol and timeframe"""
    try:
        limit = request.args.get('limit', '100', type=int)
        
        # Get candlestick data first
        candlestick_data = okx_service.get_candlestick_data(symbol, timeframe, limit)
        
        if not candlestick_data:
            return jsonify({'error': 'No candlestick data available for indicator calculation'}), 404
        
        # Ensure all timestamps are integers
        for item in candlestick_data:
            if isinstance(item.get('timestamp'), str):
                item['timestamp'] = int(item['timestamp'])
        
        # Calculate technical indicators
        indicators = tech_indicators.calculate_all_indicators(candlestick_data)
        
        return jsonify({
            'success': True,
            'data': indicators,
            'symbol': symbol,
            'timeframe': timeframe
        })
    except Exception as e:
        logging.error(f"Error calculating technical indicators: {str(e)}")
        return jsonify({'error': f'Failed to calculate technical indicators: {str(e)}'}), 500

@app.route('/api/market-data/<symbol>')
def get_market_data(symbol):
    """Get comprehensive market data for a symbol"""
    try:
        timeframe = request.args.get('timeframe', '1h')
        limit = request.args.get('limit', '100', type=int)
        
        # Get all data
        candlestick_data = okx_service.get_candlestick_data(symbol, timeframe, limit)
        orderbook_data = okx_service.get_orderbook_data(symbol, 50)
        open_interest_data = okx_service.get_open_interest_data(symbol)
        
        if not candlestick_data:
            return jsonify({'error': 'No market data available'}), 404
        
        # Calculate technical indicators
        indicators = tech_indicators.calculate_all_indicators(candlestick_data)
        
        return jsonify({
            'success': True,
            'data': {
                'candlestick': candlestick_data,
                'orderbook': orderbook_data,
                'open_interest': open_interest_data,
                'technical_indicators': indicators
            },
            'symbol': symbol,
            'timeframe': timeframe
        })
    except Exception as e:
        logging.error(f"Error fetching market data: {str(e)}")
        return jsonify({'error': f'Failed to fetch market data: {str(e)}'}), 500

@app.route('/api/symbols')
def get_symbols():
    """Get available trading symbols"""
    try:
        symbols = okx_service.get_available_symbols()
        return jsonify({
            'success': True,
            'data': symbols
        })
    except Exception as e:
        logging.error(f"Error fetching symbols: {str(e)}")
        return jsonify({'error': f'Failed to fetch symbols: {str(e)}'}), 500

@app.route('/api/preferences', methods=['GET', 'POST'])
def user_preferences():
    """Get or save user preferences"""
    if 'user_id' not in session:
        import uuid
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    
    if request.method == 'GET':
        try:
            prefs = db_service.get_user_preferences(user_id)
            if prefs:
                return jsonify({
                    'success': True,
                    'data': prefs.to_dict()
                })
            else:
                return jsonify({
                    'success': True,
                    'data': {
                        'preferred_symbol': 'BTC-USDT',
                        'preferred_timeframe': '1h',
                        'preferred_limit': 100,
                        'auto_refresh': True
                    }
                })
        except Exception as e:
            logging.error(f"Error getting user preferences: {str(e)}")
            return jsonify({'error': f'Failed to get preferences: {str(e)}'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            success = db_service.save_user_preferences(user_id, data)
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Preferences saved successfully'
                })
            else:
                return jsonify({'error': 'Failed to save preferences'}), 500
        except Exception as e:
            logging.error(f"Error saving user preferences: {str(e)}")
            return jsonify({'error': f'Failed to save preferences: {str(e)}'}), 500

@app.route('/api/database/cleanup', methods=['POST'])
def cleanup_database():
    """Clean up old database records"""
    try:
        days_to_keep = request.json.get('days_to_keep', 30) if request.json else 30
        success = db_service.cleanup_old_data(days_to_keep)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Database cleaned up, kept last {days_to_keep} days'
            })
        else:
            return jsonify({'error': 'Failed to cleanup database'}), 500
    except Exception as e:
        logging.error(f"Error cleaning up database: {str(e)}")
        return jsonify({'error': f'Failed to cleanup database: {str(e)}'}), 500

@app.route("/api/candlestick_data")
def candlestick_data():
    """Get candlestick data formatted for Plotly.js"""
    try:
        # Get parameters from query string
        symbol = request.args.get('symbol', 'SOL-USDT')
        timeframe = request.args.get('timeframe', '1H')
        limit = int(request.args.get('limit', 50))
        
        # Import get_candlesticks function
        from okx_service import get_candlesticks
        
        # Get candlestick data
        candles = get_candlesticks(symbol, bar=timeframe, limit=limit)
        
        if not candles:
            return jsonify({'error': 'No data available'}), 404
        
        # Format data for Plotly.js
        ohlc = {
            "time": [datetime.fromtimestamp(int(c['timestamp'])/1000).strftime('%Y-%m-%d %H:%M') for c in candles],
            "open": [float(c['open']) for c in candles],
            "high": [float(c['high']) for c in candles],
            "low": [float(c['low']) for c in candles],
            "close": [float(c['close']) for c in candles],
            "volume": [float(c['volume']) for c in candles]
        }
        
        return jsonify(ohlc)
        
    except Exception as e:
        logging.error(f"Error getting candlestick data: {str(e)}")
        return jsonify({'error': f'Failed to get candlestick data: {str(e)}'}), 500

@app.route('/api/comprehensive-analysis/<symbol>/<timeframe>')
def get_comprehensive_analysis(symbol, timeframe):
    """Get comprehensive analysis combining all modules"""
    try:
        # Get market data
        data = okx_service.get_candlestick_data(symbol, timeframe, limit=200)
        if not data:
            return jsonify({'error': 'No market data available'}), 404
        
        # Ensure all timestamps are integers
        for item in data:
            if isinstance(item.get('timestamp'), str):
                item['timestamp'] = int(item['timestamp'])
        
        # Get orderbook data
        orderbook = okx_service.get_orderbook_data(symbol, depth=50)
        
        # Get open interest data
        open_interest = okx_service.get_open_interest_data(symbol)
        
        # Generate comprehensive signals
        analysis_result = signal_engine.generate_comprehensive_signals(
            data, orderbook, open_interest
        )
        
        # Save to database if successful
        if 'error' not in analysis_result:
            # Save analysis results (optional)
            pass
        
        return jsonify(analysis_result)
        
    except Exception as e:
        logging.error(f"Error in comprehensive analysis: {str(e)}")
        return jsonify({'error': f'Comprehensive analysis failed: {str(e)}'}), 500

@app.route('/api/snapshot-ai/<symbol>/<timeframe>')
def get_ai_snapshot_analysis(symbol, timeframe):
    """Get AI-powered snapshot analysis narrative"""
    try:
        # Get quick_mode parameter
        quick_mode = request.args.get('quick', 'false').lower() == 'true'
        
        # Get comprehensive market data
        market_data = {}
        
        # Get candlestick data
        candlestick_data = okx_service.get_candlestick_data(symbol, timeframe, limit=200)
        if not candlestick_data:
            return jsonify({
                'success': False, 
                'error': 'No candlestick data available',
                'symbol': symbol,
                'timeframe': timeframe
            }), 404
        
        # Ensure all timestamps are integers
        for item in candlestick_data:
            if isinstance(item.get('timestamp'), str):
                item['timestamp'] = int(item['timestamp'])
        
        market_data['candlestick'] = candlestick_data
        
        # Get orderbook data (optional, don't fail if not available)
        try:
            orderbook_data = okx_service.get_orderbook_data(symbol, depth=50)
            if orderbook_data:
                market_data['orderbook'] = orderbook_data
        except Exception as e:
            logging.warning(f"Orderbook data unavailable for {symbol}: {str(e)}")
        
        # Get open interest data (optional, don't fail if not available)
        try:
            open_interest_data = okx_service.get_open_interest_data(symbol)
            if open_interest_data:
                market_data['open_interest'] = open_interest_data
        except Exception as e:
            logging.warning(f"Open interest data unavailable for {symbol}: {str(e)}")
        
        # Get funding rate data (optional, don't fail if not available)
        try:
            funding_rate_data = okx_service.get_funding_rate(symbol)
            if funding_rate_data:
                market_data['funding_rate'] = funding_rate_data
        except Exception as e:
            logging.warning(f"Funding rate data unavailable for {symbol}: {str(e)}")
        
        # Generate AI snapshot using snapshot generator
        snapshot_result = snapshot_generator.generate_snapshot(symbol, timeframe, market_data, quick_mode)
        
        if 'error' in snapshot_result:
            return jsonify({
                'success': False, 
                'error': snapshot_result['error'],
                'symbol': symbol,
                'timeframe': timeframe,
                'quick_mode': quick_mode
            }), 500
        
        # Extract AI narrative from the result
        ai_narrative = snapshot_result.get('ai_narrative', 'No AI narrative available')
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'quick_mode': quick_mode,
            'ai_narrative': ai_narrative,
            'confluence_summary': snapshot_result.get('confluence_summary', {}),
            'layer_analysis': snapshot_result.get('layer_analysis', {}),
            'generated_at': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error in AI snapshot analysis: {str(e)}")
        # Always return JSON even on error
        return jsonify({
            'success': False, 
            'error': f'AI snapshot analysis failed: {str(e)}',
            'symbol': symbol,
            'timeframe': timeframe,
            'quick_mode': request.args.get('quick', 'false').lower() == 'true'
        }), 500

@app.route('/api/snapshot/<symbol>/<timeframe>')
def get_snapshot_analysis(symbol, timeframe):
    """Get comprehensive 7-layer confluence snapshot analysis"""
    try:
        # Get comprehensive market data
        market_data = {}
        
        # Get candlestick data
        candlestick_data = okx_service.get_candlestick_data(symbol, timeframe, limit=200)
        if not candlestick_data:
            return jsonify({'error': 'No candlestick data available'}), 404
        
        market_data['candlestick'] = candlestick_data
        
        # Get orderbook data
        orderbook_data = okx_service.get_orderbook_data(symbol, depth=50)
        market_data['orderbook'] = orderbook_data
        
        # Get open interest data
        open_interest_data = okx_service.get_open_interest_data(symbol)
        market_data['open_interest'] = open_interest_data
        
        # Get technical indicators
        technical_indicators = tech_indicators.calculate_all_indicators(candlestick_data)
        market_data['technical_indicators'] = technical_indicators
        
        # Get comprehensive signals for additional analysis
        comprehensive_signals = signal_engine.generate_comprehensive_signals(
            candlestick_data, orderbook_data, open_interest_data
        )
        
        # Extract component analyses
        market_data['smc_analysis'] = comprehensive_signals.get('smc_analysis', {})
        market_data['price_action'] = comprehensive_signals.get('price_action', {})
        market_data['volume_analysis'] = comprehensive_signals.get('volume_analysis', {})
        
        # Generate snapshot analysis with quick mode support
        quick_mode = request.args.get('quick', 'false').lower() == 'true'
        snapshot = snapshot_generator.generate_snapshot(symbol, timeframe, market_data, quick_mode)
        
        return jsonify({
            'success': True,
            'data': snapshot,
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'quick_mode': quick_mode
        })
        
    except Exception as e:
        logging.error(f"Error in snapshot analysis: {str(e)}")
        return jsonify({'error': f'Snapshot analysis failed: {str(e)}'}), 500

@app.route('/export_snapshot_pdf', methods=['POST'])
def export_snapshot_pdf():
    """Export snapshot analysis as PDF"""
    try:
        symbol = request.form.get('symbol', 'BTC-USDT')
        timeframe = request.form.get('timeframe', '1h')
        
        # Get market data and generate snapshot
        market_data = {}
        
        # Get candlestick data
        candlestick_data = okx_service.get_candlestick_data(symbol, timeframe, 100)
        market_data['candlestick'] = candlestick_data
        
        # Get orderbook data
        orderbook_data = okx_service.get_orderbook_data(symbol, depth=50)
        market_data['orderbook'] = orderbook_data
        
        # Get open interest data
        open_interest_data = okx_service.get_open_interest_data(symbol)
        market_data['open_interest'] = open_interest_data
        
        # Get technical indicators
        technical_indicators = tech_indicators.calculate_all_indicators(candlestick_data)
        market_data['technical_indicators'] = technical_indicators
        
        # Get comprehensive signals for additional analysis
        comprehensive_signals = signal_engine.generate_comprehensive_signals(
            candlestick_data, orderbook_data, open_interest_data
        )
        
        # Extract component analyses
        market_data['smc_analysis'] = comprehensive_signals.get('smc_analysis', {})
        market_data['price_action'] = comprehensive_signals.get('price_action', {})
        market_data['volume_analysis'] = comprehensive_signals.get('volume_analysis', {})
        
        # Generate snapshot analysis
        snapshot = snapshot_generator.generate_snapshot(symbol, timeframe, market_data)
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        story = []
        
        # Title
        story.append(Paragraph(f"📊 Trading Analysis Snapshot", title_style))
        story.append(Paragraph(f"{symbol} - {timeframe}", styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Narrative Analysis
        story.append(Paragraph("📝 Narrative Analysis", heading_style))
        narrative = snapshot.get('narrative_analysis', 'No narrative analysis available')
        story.append(Paragraph(narrative, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Confidence Score
        story.append(Paragraph("📈 Confidence Score", heading_style))
        confidence = snapshot.get('confidence_score', 'N/A')
        story.append(Paragraph(f"Confidence: {confidence}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Primary Trading Plan
        story.append(Paragraph("🎯 Primary Trading Plan", heading_style))
        primary_plan = snapshot.get('primary_plan', {})
        if primary_plan:
            plan_data = [
                ['Direction', primary_plan.get('direction', 'N/A')],
                ['Entry Zone', primary_plan.get('entry_zone', 'N/A')],
                ['Stop Loss', primary_plan.get('stop_loss', 'N/A')],
                ['Take Profit 1', primary_plan.get('tp1', 'N/A')],
                ['Take Profit 2', primary_plan.get('tp2', 'N/A')],
                ['Risk/Reward', primary_plan.get('risk_reward', 'N/A')],
                ['Position Size', primary_plan.get('position_size', 'N/A')]
            ]
            
            if primary_plan.get('entry_strategy'):
                plan_data.append(['Entry Strategy', primary_plan['entry_strategy']])
            
            table = Table(plan_data, colWidths=[2*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        story.append(Spacer(1, 12))
        
        # 7-Layer Analysis
        story.append(Paragraph("🔍 7-Layer Confluence Analysis", heading_style))
        
        # Create layer data
        layer_data = []
        layers = [
            ('SMC Analysis', snapshot.get('smc_analysis', {})),
            ('Volume Analysis', snapshot.get('volume_analysis', {})),
            ('Orderbook Analysis', snapshot.get('orderbook_analysis', {})),
            ('RSI & EMA', snapshot.get('rsi_ema_analysis', {})),
            ('Fibonacci', snapshot.get('fibonacci_analysis', {})),
            ('OI & Funding', snapshot.get('oi_funding_analysis', {})),
            ('Trend Structure', snapshot.get('trend_structure', {}))
        ]
        
        for layer_name, layer_data_dict in layers:
            signal = layer_data_dict.get('signal', 'neutral')
            strength = layer_data_dict.get('strength', 0)
            description = layer_data_dict.get('description', 'No data available')
            
            layer_data.append([
                layer_name,
                signal.upper(),
                f"{strength:.1f}%",
                description[:80] + "..." if len(description) > 80 else description
            ])
        
        layer_table = Table(layer_data, colWidths=[1.5*inch, 0.8*inch, 0.7*inch, 2.5*inch])
        layer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        story.append(layer_table)
        story.append(Spacer(1, 12))
        
        # Risk Factors
        story.append(Paragraph("⚠️ Risk Factors", heading_style))
        risk_factors = snapshot.get('risk_factors', [])
        if risk_factors:
            risk_text = ""
            for factor in risk_factors:
                risk_text += f"• {factor.get('factor', 'Unknown')}: {factor.get('description', 'No description')}\n"
            story.append(Paragraph(risk_text, styles['Normal']))
        else:
            story.append(Paragraph("No specific risk factors identified", styles['Normal']))
        
        story.append(Spacer(1, 12))
        
        # Footer
        story.append(Paragraph("Generated by OKX Market Analysis Dashboard", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Create filename
        filename = f"snapshot_{symbol}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logging.error(f"Error exporting PDF: {str(e)}")
        return jsonify({'error': f'PDF export failed: {str(e)}'}), 500

@app.route('/api/snapshot-archive', methods=['POST'])
def save_snapshot_archive():
    """Save AI snapshot to archive"""
    try:
        if 'user_id' not in session:
            import uuid
            session['user_id'] = str(uuid.uuid4())
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Use the new simpan_snapshot_ai function
        result = simpan_snapshot_ai(
            symbol=data.get('symbol', 'UNKNOWN'),
            timeframe=data.get('timeframe', 'UNKNOWN'),
            content=data.get('ai_narrative', ''),
            confidence=data.get('confidence', 0.5),  # Default confidence if not provided
            session_id=session['user_id'],
            quick_mode=data.get('quick_mode', False),
            confluence_summary=data.get('confluence_summary', {}),
            layer_analysis=data.get('layer_analysis', {}),
            snapshot_data=data  # Store full snapshot data
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'archive_id': result['id']
            })
        else:
            return jsonify({'error': result['message']}), 400
        
    except Exception as e:
        logging.error(f"Error saving snapshot archive: {str(e)}")
        return jsonify({'error': f'Failed to save snapshot: {str(e)}'}), 500

@app.route('/api/snapshot-archive', methods=['GET'])
def get_snapshot_archive():
    """Get AI snapshot archive for current user"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': True, 'data': []})
        
        user_id = session['user_id']
        limit = request.args.get('limit', 50, type=int)
        symbol = request.args.get('symbol', None)
        timeframe = request.args.get('timeframe', None)
        
        # Use the new get_snapshot_archive function
        snapshots = get_snapshot_archive(
            session_id=user_id,
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': snapshots
        })
        
    except Exception as e:
        logging.error(f"Error fetching snapshot archive: {str(e)}")
        return jsonify({'error': f'Failed to fetch archive: {str(e)}'}), 500

# Additional API endpoints for snapshot archive management
@app.route('/api/snapshot-archive/<int:snapshot_id>', methods=['GET'])
def get_snapshot_by_id_api(snapshot_id):
    """Get specific AI snapshot by ID"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'User session not found'}), 401
        
        snapshot = get_snapshot_by_id(snapshot_id)
        
        if not snapshot:
            return jsonify({'error': 'Snapshot not found'}), 404
        
        # Security check: ensure user owns this snapshot
        if snapshot['session_id'] != session['user_id']:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'success': True,
            'data': snapshot
        })
        
    except Exception as e:
        logging.error(f"Error getting snapshot by ID: {str(e)}")
        return jsonify({'error': f'Failed to get snapshot: {str(e)}'}), 500

@app.route('/api/snapshot-archive/<int:snapshot_id>', methods=['DELETE'])
def delete_snapshot_api(snapshot_id):
    """Delete AI snapshot by ID"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'User session not found'}), 401
        
        result = delete_snapshot(snapshot_id, session['user_id'])
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logging.error(f"Error deleting snapshot: {str(e)}")
        return jsonify({'error': f'Failed to delete snapshot: {str(e)}'}), 500

@app.route('/api/snapshot-archive/statistics', methods=['GET'])
def get_snapshot_statistics_api():
    """Get AI snapshot statistics for current user"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'User session not found'}), 401
        
        stats = get_snapshot_statistics(session['user_id'])
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logging.error(f"Error getting snapshot statistics: {str(e)}")
        return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500

# Test endpoint for simpan_snapshot_ai function
@app.route('/api/test-simpan-snapshot', methods=['POST'])
def test_simpan_snapshot():
    """Test endpoint for simpan_snapshot_ai function"""
    try:
        if 'user_id' not in session:
            import uuid
            session['user_id'] = str(uuid.uuid4())
        
        # Test with sample data
        result = simpan_snapshot_ai(
            symbol="BTC-USDT",
            timeframe="1h",
            content="Test AI narrative content from GPT-4o",
            confidence=0.75,
            session_id=session['user_id'],
            quick_mode=False,
            confluence_summary={"overall_signal": "bullish", "signal_strength": 75},
            layer_analysis={"smc": {"bias": "bullish"}, "volume": {"trend": "increasing"}},
            snapshot_data={"test": "data"}
        )
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error testing simpan_snapshot_ai: {str(e)}")
        return jsonify({'error': f'Test failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
