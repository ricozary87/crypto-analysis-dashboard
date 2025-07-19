#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE TEST - Crypto Trading Dashboard
Validating all critical fixes and improvements
"""

import requests
import json
import time
from datetime import datetime

class FinalComprehensiveTest:
    def __init__(self):
        self.base_url = 'http://localhost:5000'
        self.results = []
        self.start_time = time.time()
        
    def log_test(self, test_name, status, details="", response_time=None):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'response_time': response_time,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if response_time:
            print(f"   Response Time: {response_time:.2f}s")
        print()
    
    def test_endpoint(self, endpoint, method='GET', expected_status=200, timeout=30):
        """Test a single endpoint"""
        try:
            start_time = time.time()
            response = requests.request(method, f"{self.base_url}{endpoint}", timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code == expected_status:
                try:
                    data = response.json()
                    return True, data, response_time
                except json.JSONDecodeError:
                    return True, response.text, response_time
            else:
                return False, f"Status {response.status_code}: {response.text}", response_time
        except requests.exceptions.Timeout:
            return False, f"Timeout after {timeout}s", timeout
        except Exception as e:
            return False, str(e), 0
    
    def test_critical_fixes(self):
        """Test all critical fixes that were implemented"""
        print("🔧 TESTING CRITICAL FIXES")
        print("=" * 50)
        
        # 1. Missing Template Fix
        success, data, response_time = self.test_endpoint('/advanced-analysis')
        if success and 'Advanced Analysis' in str(data):
            self.log_test(
                "Missing Template Fix", 
                "PASS", 
                "advanced-analysis page loads correctly", 
                response_time
            )
        else:
            self.log_test(
                "Missing Template Fix", 
                "FAIL", 
                f"Page failed to load: {data}", 
                response_time
            )
        
        # 2. Symbol Validation Fix - BTC-USDT Format
        success, data, response_time = self.test_endpoint('/api/snapshot/BTC-USDT')
        if success and isinstance(data, dict) and data.get('success'):
            self.log_test(
                "Symbol Validation (BTC-USDT)", 
                "PASS", 
                f"Current price: ${data.get('snapshot', {}).get('current_price', 'N/A')}", 
                response_time
            )
        else:
            self.log_test(
                "Symbol Validation (BTC-USDT)", 
                "FAIL", 
                f"API error: {data}", 
                response_time
            )
        
        # 3. Symbol Validation Fix - BTC Format
        success, data, response_time = self.test_endpoint('/api/snapshot/BTC')
        if success and isinstance(data, dict) and data.get('success'):
            self.log_test(
                "Symbol Validation (BTC)", 
                "PASS", 
                f"Both formats working", 
                response_time
            )
        else:
            self.log_test(
                "Symbol Validation (BTC)", 
                "FAIL", 
                f"API error: {data}", 
                response_time
            )
    
    def test_performance_improvements(self):
        """Test performance improvements"""
        print("🚀 TESTING PERFORMANCE IMPROVEMENTS")
        print("=" * 50)
        
        # Test optimized analyze endpoint
        success, data, response_time = self.test_endpoint('/api/analyze/BTC-USDT', timeout=10)
        if success and isinstance(data, dict) and data.get('success'):
            self.log_test(
                "Optimized Analyze Endpoint", 
                "PASS", 
                f"Analysis successful with caching", 
                response_time
            )
        else:
            self.log_test(
                "Optimized Analyze Endpoint", 
                "FAIL" if not success else "WARN", 
                f"Response: {data}", 
                response_time
            )
        
        # Test cache effectiveness (second request should be faster)
        success2, data2, response_time2 = self.test_endpoint('/api/analyze/BTC-USDT', timeout=10)
        if success2 and response_time2 < response_time:
            self.log_test(
                "Cache Effectiveness", 
                "PASS", 
                f"Cache hit: {response_time2:.2f}s vs {response_time:.2f}s", 
                response_time2
            )
        else:
            self.log_test(
                "Cache Effectiveness", 
                "WARN", 
                f"Cache may not be working optimally", 
                response_time2
            )
    
    def test_frontend_improvements(self):
        """Test frontend improvements"""
        print("🎨 TESTING FRONTEND IMPROVEMENTS")
        print("=" * 50)
        
        # Test React dashboard
        success, data, response_time = self.test_endpoint('/dashboard')
        if success and 'React' in str(data):
            self.log_test(
                "React Dashboard", 
                "PASS", 
                "React dashboard loads successfully", 
                response_time
            )
        else:
            self.log_test(
                "React Dashboard", 
                "FAIL", 
                f"Dashboard failed to load: {data}", 
                response_time
            )
        
        # Test chart data API
        success, data, response_time = self.test_endpoint('/api/candles?symbol=BTC-USDT&interval=1h')
        if success and isinstance(data, dict) and data.get('success'):
            candle_count = data.get('count', 0)
            self.log_test(
                "Chart Data API", 
                "PASS", 
                f"Retrieved {candle_count} candles", 
                response_time
            )
        else:
            self.log_test(
                "Chart Data API", 
                "FAIL", 
                f"Chart data failed: {data}", 
                response_time
            )
    
    def test_api_stability(self):
        """Test API stability and error handling"""
        print("🛡️ TESTING API STABILITY")
        print("=" * 50)
        
        # Test invalid symbol handling
        success, data, response_time = self.test_endpoint('/api/analyze/INVALID', expected_status=400)
        if success and isinstance(data, dict) and 'error' in data:
            self.log_test(
                "Invalid Symbol Handling", 
                "PASS", 
                f"Properly rejected invalid symbol", 
                response_time
            )
        else:
            self.log_test(
                "Invalid Symbol Handling", 
                "FAIL", 
                f"Error handling failed: {data}", 
                response_time
            )
        
        # Test health check
        success, data, response_time = self.test_endpoint('/health')
        if success:
            self.log_test(
                "Health Check", 
                "PASS", 
                "System health check working", 
                response_time
            )
        else:
            self.log_test(
                "Health Check", 
                "FAIL", 
                f"Health check failed: {data}", 
                response_time
            )
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAIL'])
        warning_tests = len([r for r in self.results if r['status'] == 'WARN'])
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "="*80)
        print("🎯 FINAL COMPREHENSIVE TEST REPORT")
        print("="*80)
        print(f"Test Duration: {time.time() - self.start_time:.2f} seconds")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        for result in self.results:
            status_icon = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result['details']:
                print(f"   {result['details']}")
            if result['response_time']:
                print(f"   Response Time: {result['response_time']:.2f}s")
            print()
        
        # Overall assessment
        print("🎯 OVERALL ASSESSMENT:")
        if success_rate >= 80:
            print("✅ EXCELLENT - System is working well with most fixes successful")
        elif success_rate >= 60:
            print("⚠️ GOOD - Most critical issues fixed, some minor issues remain")
        elif success_rate >= 40:
            print("❌ NEEDS IMPROVEMENT - Several critical issues still need fixing")
        else:
            print("❌ CRITICAL - Major issues need immediate attention")
        
        print("\n🚀 NEXT STEPS:")
        if failed_tests > 0:
            print("1. Address failed tests to improve system reliability")
        if warning_tests > 0:
            print("2. Investigate warnings to prevent future issues")
        print("3. Monitor system performance in production")
        print("4. Continue optimizing based on user feedback")
        
        return {
            'success_rate': success_rate,
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'warnings': warning_tests
        }
    
    def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🚀 STARTING FINAL COMPREHENSIVE TEST")
        print("="*80)
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all test suites
        self.test_critical_fixes()
        self.test_performance_improvements()
        self.test_frontend_improvements()
        self.test_api_stability()
        
        # Generate final report
        return self.generate_final_report()

def main():
    """Main test function"""
    tester = FinalComprehensiveTest()
    results = tester.run_comprehensive_test()
    
    # Return success/failure based on results
    return results['success_rate'] >= 70

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)