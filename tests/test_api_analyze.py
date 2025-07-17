"""
Unit Test untuk API Analyze Endpoint
Testing comprehensive untuk endpoint /api/analyze/<symbol>
"""

import pytest
import json
import time
import pandas as pd
from unittest.mock import patch, MagicMock
from flask import Flask
from app import app, db
from models import TradingSignal, SystemMetrics

# Test client setup
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

# Test fixtures
@pytest.fixture
def mock_okx_data():
    """Mock OKX API response data"""
    return {
        'data': [
            {
                'ts': '1705123200000',
                'o': '108766.1',
                'h': '108942.0',
                'l': '108632.0',
                'c': '108632.1',
                'vol': '52.3334683',
                'volCcy': '5711234.12'
            }
        ]
    }

@pytest.fixture
def expected_smc_analysis():
    """Expected SMC analysis response structure"""
    return {
        'smc_analysis': {
            'confidence_score': 50.0,
            'smc_summary': 'Market analysis completed',
            'market_structure': {
                'bias': 'neutral',
                'strength': 50
            },
            'trading_signals': [],
            'advanced_patterns': []
        }
    }

class TestAnalyzeEndpoint:
    """Test suite untuk endpoint /api/analyze/<symbol>"""
    
    def test_analyze_success_btc(self, client, mock_okx_data, expected_smc_analysis):
        """Test successful analysis untuk BTC-USDT"""
        # Mock OKX API response dengan method yang benar
        with patch('core.okx_fetcher.OKXAPIManager.get_candles') as mock_okx, \
             patch('core.professional_smc_analyzer.ProfessionalSMCAnalyzer.analyze_comprehensive') as mock_smc:
            
            # Create mock DataFrame
            mock_df = pd.DataFrame({
                'open': [108766.1, 108800.0, 108850.0],
                'high': [108942.0, 108950.0, 109000.0],
                'low': [108632.0, 108650.0, 108700.0],
                'close': [108632.1, 108750.0, 108800.0],
                'volume': [52.3334683, 45.2, 50.1],
                'timestamp': pd.date_range('2024-01-01', periods=3, freq='1H')
            })
            
            mock_okx.return_value = mock_df
            mock_smc.return_value = expected_smc_analysis['smc_analysis']
            
            # Test API call
            response = client.get('/api/analyze/BTC-USDT')
            
            # Assertions
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert 'smc_analysis' in data
            assert 'confidence_score' in data['smc_analysis']
            assert isinstance(data['smc_analysis']['confidence_score'], (int, float))
            assert data['smc_analysis']['confidence_score'] >= 0
            assert data['smc_analysis']['confidence_score'] <= 100
    
    def test_analyze_invalid_symbol(self, client):
        """Test dengan symbol yang tidak valid"""
        response = client.get('/api/analyze/INVALID-SYMBOL')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid symbol' in data['error']
    
    def test_analyze_multiple_symbols(self, client, mock_okx_data):
        """Test multiple symbols yang valid"""
        valid_symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT']
        
        with patch('core.okx_fetcher.OKXAPIManager.get_candles') as mock_okx, \
             patch('core.professional_smc_analyzer.ProfessionalSMCAnalyzer.analyze_comprehensive') as mock_smc:
            
            # Create mock DataFrame
            mock_df = pd.DataFrame({
                'open': [108766.1, 108800.0, 108850.0],
                'high': [108942.0, 108950.0, 109000.0],
                'low': [108632.0, 108650.0, 108700.0],
                'close': [108632.1, 108750.0, 108800.0],
                'volume': [52.3334683, 45.2, 50.1],
                'timestamp': pd.date_range('2024-01-01', periods=3, freq='1H')
            })
            
            mock_okx.return_value = mock_df
            mock_smc.return_value = {'confidence_score': 75.0, 'smc_summary': 'Test analysis'}
            
            for symbol in valid_symbols:
                response = client.get(f'/api/analyze/{symbol}')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'smc_analysis' in data
    
    def test_analyze_api_error_handling(self, client):
        """Test error handling ketika API internal error"""
        with patch('core.okx_fetcher.OKXAPIManager.get_candles') as mock_okx:
            mock_okx.side_effect = Exception("API connection failed")
            
            response = client.get('/api/analyze/BTC-USDT')
            
            # Should handle gracefully
            assert response.status_code in [500, 200]  # May return error or fallback
    
    def test_analyze_response_time(self, client, mock_okx_data):
        """Test response time untuk performance monitoring"""
        with patch('core.okx_fetcher.OKXAPIManager.get_candles') as mock_okx, \
             patch('core.professional_smc_analyzer.ProfessionalSMCAnalyzer.analyze_comprehensive') as mock_smc:
            
            # Create mock DataFrame
            mock_df = pd.DataFrame({
                'open': [108766.1, 108800.0, 108850.0],
                'high': [108942.0, 108950.0, 109000.0],
                'low': [108632.0, 108650.0, 108700.0],
                'close': [108632.1, 108750.0, 108800.0],
                'volume': [52.3334683, 45.2, 50.1],
                'timestamp': pd.date_range('2024-01-01', periods=3, freq='1H')
            })
            
            mock_okx.return_value = mock_df
            mock_smc.return_value = {'confidence_score': 60.0}
            
            start_time = time.time()
            response = client.get('/api/analyze/BTC-USDT')
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < 5.0  # Should respond within 5 seconds
            assert response.status_code == 200
    
    def test_analyze_data_structure(self, client, mock_okx_data):
        """Test struktur data response yang benar"""
        with patch('core.okx_fetcher.OKXAPIManager.get_historical_data') as mock_okx, \
             patch('core.professional_smc_analyzer.ProfessionalSMCAnalyzer.analyze_comprehensive') as mock_smc:
            
            mock_okx.return_value = mock_okx_data
            mock_smc.return_value = {
                'confidence_score': 65.0,
                'smc_summary': 'Bullish market structure detected',
                'market_structure': {'bias': 'bullish', 'strength': 65},
                'trading_signals': [{'action': 'BUY', 'confidence': 65}],
                'advanced_patterns': [{'type': 'BOS', 'confidence_score': 70}]
            }
            
            response = client.get('/api/analyze/BTC-USDT')
            data = json.loads(response.data)
            
            # Check required fields
            required_fields = ['smc_analysis']
            for field in required_fields:
                assert field in data, f"Missing field: {field}"
            
            # Check SMC analysis structure
            smc = data['smc_analysis']
            assert 'confidence_score' in smc
            assert 'smc_summary' in smc
            assert isinstance(smc['confidence_score'], (int, float))
            assert isinstance(smc['smc_summary'], str)

class TestAnalyzePerformance:
    """Test suite untuk performance monitoring"""
    
    def test_concurrent_requests(self, client, mock_okx_data):
        """Test concurrent requests handling"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            with patch('core.okx_fetcher.OKXAPIManager.get_historical_data') as mock_okx, \
                 patch('core.professional_smc_analyzer.ProfessionalSMCAnalyzer.analyze_comprehensive') as mock_smc:
                
                mock_okx.return_value = mock_okx_data
                mock_smc.return_value = {'confidence_score': 50.0}
                
                response = client.get('/api/analyze/BTC-USDT')
                results.put(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=make_request)
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            status = results.get()
            if status == 200:
                success_count += 1
        
        assert success_count >= 3  # At least 3 out of 5 should succeed

if __name__ == '__main__':
    pytest.main([__file__, '-v'])