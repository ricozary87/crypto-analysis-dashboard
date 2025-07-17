"""
Monitoring Dashboard untuk Response Time dan Error Logging
Simple monitoring system untuk track API performance
"""

import time
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
from collections import defaultdict, deque
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleMonitor:
    """Simple monitoring system untuk API performance"""
    
    def __init__(self):
        self.response_times = defaultdict(deque)  # Keep last 100 requests per endpoint
        self.error_counts = defaultdict(int)
        self.request_counts = defaultdict(int)
        self.lock = threading.Lock()
        
        # Keep only last 100 entries per endpoint
        self.max_entries = 100
        
    def track_request(self, endpoint, response_time, success=True):
        """Track API request performance"""
        with self.lock:
            # Track response time
            if len(self.response_times[endpoint]) >= self.max_entries:
                self.response_times[endpoint].popleft()
            self.response_times[endpoint].append(response_time)
            
            # Track request count
            self.request_counts[endpoint] += 1
            
            # Track errors
            if not success:
                self.error_counts[endpoint] += 1
                
        # Log slow requests
        if response_time > 2.0:  # Log if slower than 2 seconds
            logger.warning(f"Slow request detected: {endpoint} took {response_time:.2f}s")
    
    def get_stats(self):
        """Get current monitoring statistics"""
        with self.lock:
            stats = {}
            
            for endpoint in self.response_times:
                response_times = list(self.response_times[endpoint])
                if response_times:
                    stats[endpoint] = {
                        'avg_response_time': sum(response_times) / len(response_times),
                        'min_response_time': min(response_times),
                        'max_response_time': max(response_times),
                        'request_count': self.request_counts[endpoint],
                        'error_count': self.error_counts[endpoint],
                        'error_rate': self.error_counts[endpoint] / self.request_counts[endpoint] * 100,
                        'recent_requests': len(response_times)
                    }
            
            return stats
    
    def get_health_score(self):
        """Calculate overall system health score"""
        stats = self.get_stats()
        
        if not stats:
            return 100  # No data = healthy
        
        total_score = 0
        endpoint_count = 0
        
        for endpoint, data in stats.items():
            score = 100
            
            # Penalize slow response times
            if data['avg_response_time'] > 2.0:
                score -= 30
            elif data['avg_response_time'] > 1.0:
                score -= 15
            
            # Penalize high error rates
            if data['error_rate'] > 10:
                score -= 40
            elif data['error_rate'] > 5:
                score -= 20
            
            total_score += max(score, 0)
            endpoint_count += 1
        
        return total_score / endpoint_count if endpoint_count > 0 else 100

# Global monitor instance
simple_monitor = SimpleMonitor()

def monitor_performance(endpoint_name):
    """Decorator untuk monitor API performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                logger.error(f"Error in {endpoint_name}: {str(e)}")
                raise
            finally:
                end_time = time.time()
                response_time = end_time - start_time
                simple_monitor.track_request(endpoint_name, response_time, success)
                
        return wrapper
    return decorator

def create_monitoring_routes(app):
    """Create monitoring routes for Flask app"""
    
    @app.route('/api/monitoring/simple-stats')
    def get_simple_stats():
        """Get simple monitoring statistics"""
        try:
            stats = simple_monitor.get_stats()
            health_score = simple_monitor.get_health_score()
            
            return jsonify({
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'health_score': health_score,
                'endpoint_stats': stats,
                'summary': {
                    'total_endpoints': len(stats),
                    'total_requests': sum(s['request_count'] for s in stats.values()),
                    'total_errors': sum(s['error_count'] for s in stats.values()),
                    'avg_response_time': sum(s['avg_response_time'] for s in stats.values()) / len(stats) if stats else 0
                }
            })
        except Exception as e:
            logger.error(f"Error getting monitoring stats: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/monitoring/health-simple')
    def get_simple_health():
        """Simple health check dengan performance data"""
        try:
            health_score = simple_monitor.get_health_score()
            stats = simple_monitor.get_stats()
            
            status = 'healthy' if health_score > 70 else 'degraded' if health_score > 40 else 'unhealthy'
            
            return jsonify({
                'status': status,
                'health_score': health_score,
                'timestamp': datetime.now().isoformat(),
                'active_endpoints': len(stats),
                'recent_activity': sum(s['recent_requests'] for s in stats.values()),
                'message': f"System is {status} with {health_score:.1f}% health score"
            })
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.route('/api/monitoring/reset-stats')
    def reset_stats():
        """Reset monitoring statistics"""
        try:
            with simple_monitor.lock:
                simple_monitor.response_times.clear()
                simple_monitor.error_counts.clear()
                simple_monitor.request_counts.clear()
            
            return jsonify({
                'status': 'success',
                'message': 'Monitoring statistics reset successfully',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error resetting stats: {e}")
            return jsonify({'error': str(e)}), 500

# Export monitor instance and decorator
__all__ = ['simple_monitor', 'monitor_performance', 'create_monitoring_routes']