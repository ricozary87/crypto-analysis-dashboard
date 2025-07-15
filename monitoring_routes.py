"""
Monitoring Routes for Trading AI Application
Professional monitoring endpoints for Sentry, Prometheus, and Grafana integration
"""

import os
import time
import logging
from datetime import datetime, timedelta
from flask import jsonify, request, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app import app, db
from core.monitoring import monitor, monitor_api_performance
from models import TradingSignal, TradingAnalysis, SystemMetrics

logger = logging.getLogger(__name__)


@app.route('/health')
@monitor_api_performance('health_check')
def health_check():
    """Health check endpoint for load balancers"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        # Get basic system metrics
        metrics = monitor.get_system_metrics()
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'version': '1.0.0',
            'uptime': time.time(),
            'metrics': metrics
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/metrics-custom')
def custom_metrics():
    """Custom metrics endpoint (avoiding conflict with prometheus-flask-exporter)"""
    try:
        # Update real-time metrics before serving
        monitor.update_active_signals_count()
        monitor.update_win_rate_metrics()
        monitor.update_database_connections()
        
        # Generate Prometheus metrics
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
        
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/system')
@monitor_api_performance('system_metrics')
def get_system_metrics():
    """Get comprehensive system metrics"""
    try:
        metrics = monitor.get_system_metrics()
        return jsonify({
            'success': True,
            'data': metrics,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        monitor.send_alert(f"System metrics endpoint failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/trading')
@monitor_api_performance('trading_metrics')
def get_trading_metrics():
    """Get trading-specific metrics"""
    try:
        symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'TIA-USDT', 'RENDER-USDT']
        trading_metrics = {}
        
        for symbol in symbols:
            # Get active signals
            active_signals = db.session.query(TradingSignal).filter(
                TradingSignal.symbol == symbol,
                TradingSignal.status == 'active'
            ).count()
            
            # Get recent analysis
            recent_analysis = db.session.query(TradingAnalysis).filter(
                TradingAnalysis.symbol == symbol,
                TradingAnalysis.created_at >= datetime.now() - timedelta(hours=24)
            ).count()
            
            # Calculate win rate (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            total_signals = db.session.query(TradingSignal).filter(
                TradingSignal.symbol == symbol,
                TradingSignal.created_at >= cutoff_date,
                TradingSignal.status.in_(['hit_tp1', 'hit_tp2', 'hit_tp3', 'stopped'])
            ).count()
            
            winning_signals = db.session.query(TradingSignal).filter(
                TradingSignal.symbol == symbol,
                TradingSignal.created_at >= cutoff_date,
                TradingSignal.status.in_(['hit_tp1', 'hit_tp2', 'hit_tp3'])
            ).count()
            
            win_rate = (winning_signals / total_signals * 100) if total_signals > 0 else 0
            
            trading_metrics[symbol] = {
                'active_signals': active_signals,
                'recent_analysis': recent_analysis,
                'win_rate': round(win_rate, 2),
                'total_signals_30d': total_signals,
                'winning_signals_30d': winning_signals
            }
        
        return jsonify({
            'success': True,
            'data': trading_metrics,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get trading metrics: {e}")
        monitor.send_alert(f"Trading metrics endpoint failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/performance')
@monitor_api_performance('performance_metrics')
def get_performance_metrics():
    """Get API performance metrics"""
    try:
        # Get recent system metrics
        recent_metrics = db.session.query(SystemMetrics).filter(
            SystemMetrics.timestamp >= datetime.now() - timedelta(hours=1)
        ).order_by(SystemMetrics.timestamp.desc()).limit(60).all()
        
        performance_data = []
        for metric in recent_metrics:
            performance_data.append({
                'timestamp': metric.timestamp.isoformat(),
                'cpu_usage': metric.cpu_usage,
                'memory_usage': metric.memory_usage,
                'api_response_time': metric.api_response_time,
                'active_connections': metric.active_connections,
                'error_count': metric.error_count
            })
        
        return jsonify({
            'success': True,
            'data': performance_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        monitor.send_alert(f"Performance metrics endpoint failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/alerts')
@monitor_api_performance('alerts_metrics')
def get_monitoring_alerts():
    """Get recent alerts and system status"""
    try:
        # Get recent alerts from database
        recent_alerts = db.session.query(AlertLog).filter(
            AlertLog.timestamp >= datetime.now() - timedelta(hours=24)
        ).order_by(AlertLog.timestamp.desc()).limit(50).all()
        
        alerts_data = []
        for alert in recent_alerts:
            alerts_data.append({
                'id': alert.id,
                'type': alert.alert_type,
                'message': alert.message,
                'severity': alert.severity,
                'status': alert.status,
                'timestamp': alert.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': alerts_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        monitor.send_alert(f"Alerts endpoint failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/test-sentry')
@monitor_api_performance('test_sentry')
def test_sentry():
    """Test Sentry integration"""
    try:
        # Test different types of Sentry events
        test_type = request.args.get('type', 'info')
        
        if test_type == 'error':
            # Test error tracking
            try:
                raise Exception("Test error for Sentry monitoring")
            except Exception as e:
                monitor.send_alert("Test error generated for Sentry", level="error")
                raise
                
        elif test_type == 'warning':
            # Test warning
            monitor.send_alert("Test warning for Sentry monitoring", level="warning")
            
        else:
            # Test info message
            monitor.send_alert("Test info message for Sentry monitoring", level="info")
        
        return jsonify({
            'success': True,
            'message': f'Sentry test {test_type} sent successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Sentry test failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/dashboard')
@monitor_api_performance('monitoring_dashboard')
def monitoring_dashboard():
    """Get comprehensive monitoring dashboard data"""
    try:
        # Get system metrics
        system_metrics = monitor.get_system_metrics()
        
        # Get trading metrics
        trading_response = get_trading_metrics()
        trading_data = trading_response.get_json()
        
        # Get performance metrics
        performance_response = get_performance_metrics()
        performance_data = performance_response.get_json()
        
        # Combine all data
        dashboard_data = {
            'system': system_metrics,
            'trading': trading_data.get('data', {}),
            'performance': performance_data.get('data', []),
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy'
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        monitor.send_alert(f"Dashboard endpoint failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/force-update')
@monitor_api_performance('force_metrics_update')
def force_metrics_update():
    """Force update all monitoring metrics"""
    try:
        # Update all metrics
        monitor.update_active_signals_count()
        monitor.update_win_rate_metrics()
        monitor.update_database_connections()
        
        # Send confirmation
        return jsonify({
            'success': True,
            'message': 'All monitoring metrics updated successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to force update metrics: {e}")
        monitor.send_alert(f"Force metrics update failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Import AlertLog model
from models import AlertLog

# Initialize monitoring routes
logger.info("Monitoring routes initialized successfully")