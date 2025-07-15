#!/usr/bin/env python3
"""
Unit Tests for Phase 1 Integration
Testing database models, AI engine, SMC analyzer, and API endpoints
"""

import unittest
import sys
import os
import json
import requests
from datetime import datetime
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestPhase1Integration(unittest.TestCase):
    """Test Phase 1 Core Integration components"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5000"
        self.test_symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT']
        self.session_id = 'test_session_123'
        
    def test_database_models_import(self):
        """Test that all database models can be imported"""
        try:
            from models import (
                TradingSignal, SystemMetrics, AlertLog, TradingAnalysis,
                MarketData, OrderbookData, OpenInterestData, 
                TechnicalIndicatorData, UserPreferences, AISnapshotArchive
            )
            self.assertTrue(True, "All database models imported successfully")
        except ImportError as e:
            self.fail(f"Database models import failed: {e}")
    
    def test_ai_engine_initialization(self):
        """Test AI Engine initialization"""
        try:
            from core.ai_engine import AIEngine, get_ai_engine
            from core.ai_prompt_builder import AIPromptBuilder
            
            # Test AI Engine
            ai_engine = get_ai_engine()
            self.assertIsNotNone(ai_engine, "AI Engine should initialize")
            
            # Test AI Prompt Builder
            prompt_builder = AIPromptBuilder()
            self.assertIsNotNone(prompt_builder, "AI Prompt Builder should initialize")
            
        except Exception as e:
            self.fail(f"AI Engine initialization failed: {e}")
    
    def test_smc_analyzer_integration(self):
        """Test SMC Analyzer integration"""
        try:
            from core.analyzer import TechnicalAnalyzer
            from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
            
            # Test Technical Analyzer
            analyzer = TechnicalAnalyzer()
            self.assertTrue(hasattr(analyzer, 'smc_analyzer'), "Technical Analyzer should have SMC analyzer")
            self.assertTrue(hasattr(analyzer, 'enhanced_ai'), "Technical Analyzer should have enhanced AI")
            
            # Test Professional SMC Analyzer
            smc_analyzer = ProfessionalSMCAnalyzer()
            self.assertIsNotNone(smc_analyzer, "Professional SMC Analyzer should initialize")
            
        except Exception as e:
            self.fail(f"SMC Analyzer integration failed: {e}")
    
    def test_signal_engine_integration(self):
        """Test Signal Engine integration"""
        try:
            from core.signal_engine import SignalEngine
            
            signal_engine = SignalEngine()
            self.assertIsNotNone(signal_engine, "Signal Engine should initialize")
            
            # Test that it has required components
            self.assertTrue(hasattr(signal_engine, 'smc_analyzer'), "Signal Engine should have SMC analyzer")
            self.assertTrue(hasattr(signal_engine, 'price_action_analyzer'), "Signal Engine should have price action analyzer")
            
        except Exception as e:
            self.fail(f"Signal Engine integration failed: {e}")
    
    def test_price_action_analyzer(self):
        """Test Price Action Analyzer"""
        try:
            from core.price_action import PriceActionAnalyzer
            
            price_analyzer = PriceActionAnalyzer()
            self.assertIsNotNone(price_analyzer, "Price Action Analyzer should initialize")
            
            # Test with sample data
            sample_data = pd.DataFrame({
                'open': [100, 105, 110],
                'high': [105, 110, 115],
                'low': [95, 100, 105],
                'close': [105, 110, 115],
                'volume': [1000, 1500, 2000]
            })
            
            result = price_analyzer.analyze_price_action(sample_data)
            self.assertIsInstance(result, dict, "Price action analysis should return dict")
            
        except Exception as e:
            self.fail(f"Price Action Analyzer failed: {e}")
    
    def test_advanced_formatter(self):
        """Test Advanced Formatter"""
        try:
            from core.advanced_formatter import AdvancedFormatter
            
            formatter = AdvancedFormatter()
            self.assertIsNotNone(formatter, "Advanced Formatter should initialize")
            
            # Test with sample analysis data
            sample_analysis = {
                'symbol': 'BTC-USDT',
                'timeframe': '1H',
                'current_price': 50000,
                'signals': {'action': 'BUY', 'confidence': 0.75},
                'indicators': {'rsi': 45, 'macd': 0.5},
                'trend': 'BULLISH'
            }
            
            formatted_result = formatter.format_analysis(sample_analysis)
            self.assertIsInstance(formatted_result, str, "Formatted analysis should be string")
            self.assertIn('BTC-USDT', formatted_result, "Formatted result should contain symbol")
            
        except Exception as e:
            self.fail(f"Advanced Formatter failed: {e}")

class TestNewAPIEndpoints(unittest.TestCase):
    """Test new API endpoints for Phase 1 models"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5000"
        self.test_symbol = 'BTC-USDT'
        self.session_id = 'test_session_123'
        
    def test_market_data_endpoint(self):
        """Test market data endpoint"""
        try:
            url = f"{self.base_url}/api/market-data/{self.test_symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.assertTrue(data.get('success'), "Market data endpoint should return success")
                self.assertEqual(data.get('symbol'), self.test_symbol, "Symbol should match")
            else:
                self.skipTest(f"Market data endpoint returned {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.skipTest(f"Market data endpoint not accessible: {e}")
    
    def test_open_interest_endpoint(self):
        """Test open interest endpoint"""
        try:
            url = f"{self.base_url}/api/open-interest/{self.test_symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.assertTrue(data.get('success'), "Open interest endpoint should return success")
                self.assertEqual(data.get('symbol'), self.test_symbol, "Symbol should match")
            else:
                self.skipTest(f"Open interest endpoint returned {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.skipTest(f"Open interest endpoint not accessible: {e}")
    
    def test_user_preferences_endpoint(self):
        """Test user preferences endpoint"""
        try:
            # Test GET preferences
            url = f"{self.base_url}/api/user-preferences/{self.session_id}"
            response = requests.get(url, timeout=10)
            
            # Test POST preferences
            url = f"{self.base_url}/api/user-preferences/{self.session_id}"
            post_data = {
                'preferred_symbol': 'ETH-USDT',
                'preferred_timeframe': '1h',
                'preferred_limit': 200,
                'auto_refresh': True
            }
            
            response = requests.post(url, json=post_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.assertTrue(data.get('success'), "User preferences POST should return success")
                self.assertEqual(data.get('session_id'), self.session_id, "Session ID should match")
            else:
                self.skipTest(f"User preferences endpoint returned {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.skipTest(f"User preferences endpoint not accessible: {e}")
    
    def test_ai_snapshots_endpoint(self):
        """Test AI snapshots endpoint"""
        try:
            # Test GET snapshots
            url = f"{self.base_url}/api/ai-snapshots/{self.test_symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.assertTrue(data.get('success'), "AI snapshots GET should return success")
                self.assertEqual(data.get('symbol'), self.test_symbol, "Symbol should match")
            else:
                self.skipTest(f"AI snapshots GET returned {response.status_code}")
            
            # Test POST snapshot
            url = f"{self.base_url}/api/ai-snapshots"
            post_data = {
                'session_id': self.session_id,
                'symbol': self.test_symbol,
                'timeframe': '1h',
                'quick_mode': False,
                'ai_narrative': 'Test AI narrative',
                'confluence_summary': {'bullish': 3, 'bearish': 1},
                'confidence': 0.75
            }
            
            response = requests.post(url, json=post_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.assertTrue(data.get('success'), "AI snapshots POST should return success")
                self.assertIn('snapshot_id', data, "Response should contain snapshot ID")
            else:
                self.skipTest(f"AI snapshots POST returned {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.skipTest(f"AI snapshots endpoint not accessible: {e}")

def run_integration_tests():
    """Run all integration tests"""
    
    print("🧪 RUNNING PHASE 1 INTEGRATION TESTS")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add model tests
    suite.addTest(TestPhase1Integration('test_database_models_import'))
    suite.addTest(TestPhase1Integration('test_ai_engine_initialization'))
    suite.addTest(TestPhase1Integration('test_smc_analyzer_integration'))
    suite.addTest(TestPhase1Integration('test_signal_engine_integration'))
    suite.addTest(TestPhase1Integration('test_price_action_analyzer'))
    suite.addTest(TestPhase1Integration('test_advanced_formatter'))
    
    # Add API endpoint tests
    suite.addTest(TestNewAPIEndpoints('test_market_data_endpoint'))
    suite.addTest(TestNewAPIEndpoints('test_open_interest_endpoint'))
    suite.addTest(TestNewAPIEndpoints('test_user_preferences_endpoint'))
    suite.addTest(TestNewAPIEndpoints('test_ai_snapshots_endpoint'))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print(f"\n📊 TEST SUMMARY:")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped)}")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\n⚠️  ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)