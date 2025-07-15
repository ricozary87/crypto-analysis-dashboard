#!/usr/bin/env python3
"""
Comprehensive Pipeline Testing Script
Tests the entire flow: OKX Data → 7-Layer Analysis → AI Snapshot → API → UI
"""

import json
import logging
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensivePipelineTest:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        
        # Test configurations
        self.test_pairs = ['SOL-USDT', 'BTC-USDT', 'ETH-USDT']
        self.test_timeframes = ['5m', '15m', '1h', '4h', '1d']
        self.critical_endpoints = [
            '/api/candlestick',
            '/api/orderbook',
            '/api/open-interest',
            '/api/technical-indicators',
            '/api/comprehensive-analysis',
            '/api/snapshot-ai',
            '/api/snapshot'
        ]
        
    def log_test_result(self, test_name: str, status: str, details: str, data: Any = None):
        """Log test result with timestamp"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'test_name': test_name,
            'status': status,
            'details': details,
            'data': data
        }
        self.test_results.append(result)
        
        if status == 'PASS':
            logger.info(f"✅ {test_name}: {details}")
        elif status == 'FAIL':
            logger.error(f"❌ {test_name}: {details}")
        else:
            logger.warning(f"⚠️ {test_name}: {details}")
    
    def test_okx_data_fetch(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Test OKX data fetching for all endpoints"""
        test_name = f"OKX Data Fetch - {symbol} {timeframe}"
        
        try:
            # Test candlestick data
            candlestick_url = f"{self.base_url}/api/candlestick/{symbol}/{timeframe}"
            resp = requests.get(candlestick_url, timeout=30)
            
            if resp.status_code != 200:
                self.log_test_result(test_name, 'FAIL', f"Candlestick API failed: {resp.status_code}")
                return {'success': False, 'error': f"HTTP {resp.status_code}"}
            
            candlestick_data = resp.json()
            
            # Test orderbook data
            orderbook_url = f"{self.base_url}/api/orderbook/{symbol}"
            resp = requests.get(orderbook_url, timeout=30)
            orderbook_data = resp.json() if resp.status_code == 200 else {}
            
            # Test open interest data
            oi_url = f"{self.base_url}/api/open-interest/{symbol}"
            resp = requests.get(oi_url, timeout=30)
            oi_data = resp.json() if resp.status_code == 200 else {}
            
            # Test technical indicators
            ti_url = f"{self.base_url}/api/technical-indicators/{symbol}/{timeframe}"
            resp = requests.get(ti_url, timeout=30)
            ti_data = resp.json() if resp.status_code == 200 else {}
            
            # Validate data structure
            if not isinstance(candlestick_data, list) or len(candlestick_data) == 0:
                self.log_test_result(test_name, 'FAIL', "Empty or invalid candlestick data")
                return {'success': False, 'error': 'Invalid candlestick data'}
            
            # Check required fields in candlestick data
            required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            for field in required_fields:
                if field not in candlestick_data[0]:
                    self.log_test_result(test_name, 'FAIL', f"Missing field: {field}")
                    return {'success': False, 'error': f'Missing field: {field}'}
            
            self.log_test_result(test_name, 'PASS', f"All data fetched successfully. Candlestick: {len(candlestick_data)} points")
            
            return {
                'success': True,
                'candlestick': candlestick_data,
                'orderbook': orderbook_data,
                'open_interest': oi_data,
                'technical_indicators': ti_data
            }
            
        except requests.exceptions.RequestException as e:
            self.log_test_result(test_name, 'FAIL', f"Request failed: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            self.log_test_result(test_name, 'FAIL', f"Unexpected error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def test_comprehensive_analysis(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Test comprehensive analysis endpoint"""
        test_name = f"Comprehensive Analysis - {symbol} {timeframe}"
        
        try:
            url = f"{self.base_url}/api/comprehensive-analysis/{symbol}/{timeframe}"
            resp = requests.get(url, timeout=60)
            
            if resp.status_code != 200:
                self.log_test_result(test_name, 'FAIL', f"API failed: {resp.status_code}")
                return {'success': False, 'error': f"HTTP {resp.status_code}"}
            
            data = resp.json()
            
            # Check for error in response
            if 'error' in data:
                self.log_test_result(test_name, 'FAIL', f"Analysis error: {data['error']}")
                return {'success': False, 'error': data['error']}
            
            # Validate expected analysis components
            expected_components = ['smc_analysis', 'volume_analysis', 'price_action']
            missing_components = [comp for comp in expected_components if comp not in data]
            
            if missing_components:
                self.log_test_result(test_name, 'WARN', f"Missing components: {missing_components}")
            else:
                self.log_test_result(test_name, 'PASS', "All analysis components present")
            
            return {'success': True, 'data': data}
            
        except requests.exceptions.RequestException as e:
            self.log_test_result(test_name, 'FAIL', f"Request failed: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            self.log_test_result(test_name, 'FAIL', f"Unexpected error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def test_ai_snapshot(self, symbol: str, timeframe: str, quick_mode: bool = False) -> Dict[str, Any]:
        """Test AI snapshot generation"""
        mode_text = "Quick" if quick_mode else "Comprehensive"
        test_name = f"AI Snapshot {mode_text} - {symbol} {timeframe}"
        
        try:
            url = f"{self.base_url}/api/snapshot-ai/{symbol}/{timeframe}"
            if quick_mode:
                url += "?quick=true"
            
            resp = requests.get(url, timeout=120)  # Longer timeout for AI processing
            
            if resp.status_code != 200:
                self.log_test_result(test_name, 'FAIL', f"API failed: {resp.status_code}")
                return {'success': False, 'error': f"HTTP {resp.status_code}"}
            
            data = resp.json()
            
            # Check response structure
            if not data.get('success', False):
                self.log_test_result(test_name, 'FAIL', f"API returned error: {data.get('error', 'Unknown error')}")
                return {'success': False, 'error': data.get('error', 'Unknown error')}
            
            # Validate AI narrative
            ai_narrative = data.get('ai_narrative', '')
            if not ai_narrative or len(ai_narrative) < 100:
                self.log_test_result(test_name, 'FAIL', "AI narrative too short or empty")
                return {'success': False, 'error': 'Invalid AI narrative'}
            
            # Check for required fields
            required_fields = ['symbol', 'timeframe', 'quick_mode', 'ai_narrative', 'generated_at']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test_result(test_name, 'WARN', f"Missing fields: {missing_fields}")
            
            # Validate confluence summary and layer analysis
            confluence_summary = data.get('confluence_summary', {})
            layer_analysis = data.get('layer_analysis', {})
            
            narrative_length = len(ai_narrative)
            self.log_test_result(test_name, 'PASS', f"AI narrative generated successfully ({narrative_length} characters)")
            
            return {
                'success': True,
                'data': data,
                'narrative_length': narrative_length,
                'has_confluence': bool(confluence_summary),
                'has_layer_analysis': bool(layer_analysis)
            }
            
        except requests.exceptions.RequestException as e:
            self.log_test_result(test_name, 'FAIL', f"Request failed: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            self.log_test_result(test_name, 'FAIL', f"Unexpected error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def test_regular_snapshot(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Test regular snapshot generation"""
        test_name = f"Regular Snapshot - {symbol} {timeframe}"
        
        try:
            url = f"{self.base_url}/api/snapshot/{symbol}/{timeframe}"
            resp = requests.get(url, timeout=90)
            
            if resp.status_code != 200:
                self.log_test_result(test_name, 'FAIL', f"API failed: {resp.status_code}")
                return {'success': False, 'error': f"HTTP {resp.status_code}"}
            
            data = resp.json()
            
            # Check for error in response
            if 'error' in data:
                self.log_test_result(test_name, 'FAIL', f"Snapshot error: {data['error']}")
                return {'success': False, 'error': data['error']}
            
            # Validate snapshot structure
            expected_sections = ['confluence_summary', 'layer_analysis', 'narrative_analysis']
            present_sections = [section for section in expected_sections if section in data]
            
            self.log_test_result(test_name, 'PASS', f"Snapshot generated with {len(present_sections)} sections")
            
            return {'success': True, 'data': data, 'sections': present_sections}
            
        except requests.exceptions.RequestException as e:
            self.log_test_result(test_name, 'FAIL', f"Request failed: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            self.log_test_result(test_name, 'FAIL', f"Unexpected error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        logger.info("🚀 Starting Comprehensive Pipeline Testing")
        logger.info("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        # Test a subset of combinations to avoid overwhelming the system
        test_combinations = [
            ('SOL-USDT', '5m'),
            ('SOL-USDT', '1h'),
            ('BTC-USDT', '15m'),
            ('BTC-USDT', '1h'),
            ('ETH-USDT', '1h'),
            ('ETH-USDT', '4h')
        ]
        
        for symbol, timeframe in test_combinations:
            logger.info(f"Testing {symbol} {timeframe}...")
            
            # Test 1: OKX Data Fetch
            okx_result = self.test_okx_data_fetch(symbol, timeframe)
            total_tests += 1
            if okx_result['success']:
                passed_tests += 1
            else:
                failed_tests += 1
                continue  # Skip other tests if data fetch fails
            
            # Test 2: Comprehensive Analysis
            comp_result = self.test_comprehensive_analysis(symbol, timeframe)
            total_tests += 1
            if comp_result['success']:
                passed_tests += 1
            else:
                failed_tests += 1
            
            # Test 3: Regular Snapshot
            snapshot_result = self.test_regular_snapshot(symbol, timeframe)
            total_tests += 1
            if snapshot_result['success']:
                passed_tests += 1
            else:
                failed_tests += 1
            
            # Test 4: AI Snapshot (Quick Mode)
            ai_quick_result = self.test_ai_snapshot(symbol, timeframe, quick_mode=True)
            total_tests += 1
            if ai_quick_result['success']:
                passed_tests += 1
            else:
                failed_tests += 1
            
            # Test 5: AI Snapshot (Comprehensive Mode) - Only for select pairs
            if symbol in ['SOL-USDT', 'BTC-USDT'] and timeframe in ['1h']:
                ai_comp_result = self.test_ai_snapshot(symbol, timeframe, quick_mode=False)
                total_tests += 1
                if ai_comp_result['success']:
                    passed_tests += 1
                else:
                    failed_tests += 1
            
            # Small delay between tests to avoid overwhelming the system
            time.sleep(2)
        
        # Generate summary report
        logger.info("=" * 60)
        logger.info("🏁 Test Summary")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Save detailed results
        self.save_test_results()
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests/total_tests)*100
        }
    
    def save_test_results(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': len(self.test_results),
                    'passed': len([r for r in self.test_results if r['status'] == 'PASS']),
                    'failed': len([r for r in self.test_results if r['status'] == 'FAIL']),
                    'warnings': len([r for r in self.test_results if r['status'] == 'WARN'])
                },
                'results': self.test_results
            }, f, indent=2)
        
        logger.info(f"📊 Test results saved to {filename}")

def main():
    """Main function to run the comprehensive test"""
    tester = ComprehensivePipelineTest()
    
    try:
        results = tester.run_comprehensive_test()
        
        if results['success_rate'] >= 80:
            logger.info("🎉 System is performing well!")
        elif results['success_rate'] >= 60:
            logger.warning("⚠️ System has some issues but is functional")
        else:
            logger.error("🚨 System has significant issues that need attention")
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")

if __name__ == "__main__":
    main()