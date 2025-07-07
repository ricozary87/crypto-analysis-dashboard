from flask_socketio import emit, join_room, leave_room
from app import socketio, app
import logging

logger = logging.getLogger(__name__)

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info('Client connected')
    emit('status', {'message': 'Connected to trading signal system'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info('Client disconnected')

@socketio.on('join_room')
def handle_join_room(data):
    """Handle client joining a room."""
    room = data.get('room', 'general')
    join_room(room)
    emit('status', {'message': f'Joined room: {room}'})
    logger.info(f'Client joined room: {room}')

@socketio.on('leave_room')
def handle_leave_room(data):
    """Handle client leaving a room."""
    room = data.get('room', 'general')
    leave_room(room)
    emit('status', {'message': f'Left room: {room}'})
    logger.info(f'Client left room: {room}')

@socketio.on('request_status')
def handle_status_request():
    """Handle status request from client."""
    try:
        from models import TradingSignal, SystemMetrics
        from datetime import datetime, timedelta, timezone
        
        # Get latest system metrics
        latest_metrics = SystemMetrics.query.order_by(SystemMetrics.timestamp.desc()).first()
        
        # Get signal count from last hour
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_signals = TradingSignal.query.filter(
            TradingSignal.created_at >= one_hour_ago
        ).count()
        
        status_data = {
            'system_health': {
                'cpu_usage': latest_metrics.cpu_usage if latest_metrics else 0,
                'memory_usage': latest_metrics.memory_usage if latest_metrics else 0,
                'disk_usage': latest_metrics.disk_usage if latest_metrics else 0,
                'api_response_time': latest_metrics.api_response_time if latest_metrics else 0
            } if latest_metrics else {},
            'recent_signals': recent_signals,
            'status': 'active',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        emit('status_update', status_data)
        
    except Exception as e:
        logger.error(f"Error handling status request: {e}", exc_info=True)
        emit('error', {'message': 'Failed to get status'})

def broadcast_signal(signal_data):
    """Broadcast new signal to all connected clients."""
    socketio.emit('new_signal', signal_data, room='signals')

def broadcast_metrics(metrics_data):
    """Broadcast system metrics to all connected clients."""
    socketio.emit('metrics_update', metrics_data, room='metrics')

def broadcast_alert(alert_data):
    """Broadcast alert to all connected clients."""
    socketio.emit('new_alert', alert_data, room='alerts')

@socketio.on('request_metrics')
def handle_metrics_request():
    """Handle metrics request from dashboard."""
    try:
        # Get latest metrics from database
        from models import SystemMetrics, TradingSignal
        from datetime import datetime, timedelta
        
        latest_metric = SystemMetrics.query.order_by(SystemMetrics.timestamp.desc()).first()
        
        # Get active signals count
        active_signals = TradingSignal.query.filter_by(status='active').count()
        
        # Calculate win rate (last 24h)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_signals = TradingSignal.query.filter(
            TradingSignal.created_at >= yesterday
        ).all()
        
        winning_signals = sum(1 for s in recent_signals if s.status in ['hit_tp1', 'hit_tp2', 'hit_tp3'])
        win_rate = (winning_signals / len(recent_signals) * 100) if recent_signals else 0
        
        # Get cache hit rate
        from core.analyzer import TechnicalAnalyzer
        analyzer = TechnicalAnalyzer()
        cache_hit_rate = analyzer.get_cache_hit_rate() * 100
        
        # API latency
        api_latency = latest_metric.api_response_time * 1000 if latest_metric else 0
        
        emit('metrics_update', {
            'active_signals': active_signals,
            'win_rate': round(win_rate, 1),
            'cache_hit_rate': round(cache_hit_rate, 1),
            'api_latency': round(api_latency, 0)
        })
        
    except Exception as e:
        logger.error(f"Error handling metrics request: {e}")

@socketio.on('request_technical_data')
def handle_technical_request(data):
    """Handle technical analysis request."""
    try:
        symbol = data.get('symbol', 'BTC')
        
        # Get technical data
        from core.analyzer import TechnicalAnalyzer
        from core.okx_fetcher import OKXAPIManager
        
        api = OKXAPIManager()
        analyzer = TechnicalAnalyzer()
        
        symbol_okx = f"{symbol.upper()}-USDT"
        df = api.get_candles(symbol_okx, '1H', limit=100)
        
        if df is not None and not df.empty:
            indicators = analyzer.analyze(df, symbol_okx, '1H')
            summary = analyzer.get_indicator_summary(indicators)
            
            emit('technical_update', {
                'symbol': symbol,
                'indicators': summary,
                'current_price': float(df['close'].iloc[-1])
            })
            
    except Exception as e:
        logger.error(f"Error handling technical request: {e}")
