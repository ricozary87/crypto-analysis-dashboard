"""
Unit Test untuk Monitoring System
Testing untuk endpoint monitoring dan performance tracking
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
from app import app, db
from core.monitoring import monitor

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

class TestMonitoringEndpoints:
    """Test suite untuk monitoring endpoints"""
    
    def test_health_check_success(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'database' in data
        assert 'version' in data
        assert 'metrics' in data
    
    def test_system_metrics_endpoint(self, client):
        """Test system metrics endpoint"""
        response = client.get('/api/monitoring/system')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check required metrics
        assert 'cpu_usage' in data
        assert 'memory_usage' in data
        assert 'disk_usage' in data
        assert isinstance(data['cpu_usage'], (int, float))
        assert isinstance(data['memory_usage'], (int, float))
    
    def test_trading_metrics_endpoint(self, client):
        """Test trading metrics endpoint"""
        response = client.get('/api/monitoring/trading')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check trading-specific metrics
        assert 'active_signals' in data
        assert 'win_rate' in data
        assert 'total_analyses' in data
        assert isinstance(data['active_signals'], int)
        assert isinstance(data['win_rate'], (int, float))
    
    def test_performance_metrics_endpoint(self, client):
        """Test performance metrics endpoint"""
        response = client.get('/api/monitoring/performance')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check performance metrics
        assert 'api_response_times' in data
        assert 'database_connections' in data
        assert 'error_rates' in data
    
    def test_prometheus_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint"""
        response = client.get('/metrics-custom')
        
        assert response.status_code == 200
        assert response.content_type == 'text/plain; version=0.0.4; charset=utf-8'
        
        # Check if metrics are properly formatted
        metrics_text = response.data.decode('utf-8')
        assert 'trading_signals_total' in metrics_text
        assert 'api_response_time_seconds' in metrics_text

class TestMonitoringSystem:
    """Test suite untuk monitoring system functionality"""
    
    def test_system_metrics_collection(self):
        """Test system metrics collection"""
        metrics = monitor.get_system_metrics()
        
        assert 'cpu_usage' in metrics
        assert 'memory_usage' in metrics
        assert 'disk_usage' in metrics
        assert 'health_score' in metrics
        
        # Check values are reasonable
        assert 0 <= metrics['cpu_usage'] <= 100
        assert 0 <= metrics['memory_usage'] <= 100
        assert 0 <= metrics['disk_usage'] <= 100
        assert 0 <= metrics['health_score'] <= 100
    
    def test_api_performance_tracking(self, client):
        """Test API performance tracking"""
        # Make a request to trigger performance tracking
        start_time = time.time()
        response = client.get('/api/analyze/BTC-USDT')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Check if performance was tracked
        performance_metrics = monitor.get_api_performance_metrics()
        assert 'analyze_symbol' in performance_metrics
        
        # Check response time is reasonable
        assert response_time < 10.0  # Should be under 10 seconds

class TestErrorHandling:
    """Test suite untuk error handling dalam monitoring"""
    
    def test_health_check_database_error(self, client):
        """Test health check dengan database error"""
        with patch('app.db.session.execute') as mock_execute:
            mock_execute.side_effect = Exception("Database connection failed")
            
            response = client.get('/health')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'unhealthy'
            assert 'error' in data
    
    def test_metrics_collection_error(self):
        """Test metrics collection dengan error"""
        with patch('psutil.cpu_percent') as mock_cpu:
            mock_cpu.side_effect = Exception("CPU monitoring failed")
            
            metrics = monitor.get_system_metrics()
            
            # Should handle gracefully
            assert 'cpu_usage' in metrics
            assert metrics['cpu_usage'] == 0  # Default fallback value

if __name__ == '__main__':
    pytest.main([__file__, '-v'])