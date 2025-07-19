#!/usr/bin/env python3
"""
Comprehensive Application Testing - Crypto Trading Dashboard
Testing all components and identifying weaknesses
"""

import requests
import json
import time
import sys
from datetime import datetime
from urllib.parse import urljoin

class ComprehensiveAppTester:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.issues_found = []
        self.test_results = {}
        
    def log_issue(self, severity, component, issue, details=""):
        """Log an issue found during testing"""
        self.issues_found.append({
            'severity': severity,  # CRITICAL, HIGH, MEDIUM, LOW
            'component': component,
            'issue': issue,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
    def test_endpoint(self, endpoint, method='GET', data=None, timeout=10):
        """Test a single endpoint with comprehensive error handling"""
        try:
            url = urljoin(self.base_url, endpoint)
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=timeout)
            
            response_time = time.time() - start_time
            
            result = {
                'endpoint': endpoint,
                'status_code': response.status_code,
                'response_time': response_time,
                'success': response.status_code == 200,
                'content_type': response.headers.get('content-type', ''),
                'content_length': len(response.content)
            }
            
            # Performance issues
            if response_time > 5:
                self.log_issue('HIGH', 'Performance', f'Slow response: {endpoint}', 
                             f'Response time: {response_time:.2f}s')
            elif response_time > 2:
                self.log_issue('MEDIUM', 'Performance', f'Moderate response time: {endpoint}', 
                             f'Response time: {response_time:.2f}s')
            
            # HTTP errors
            if response.status_code >= 500:
                self.log_issue('CRITICAL', 'Backend', f'Server error: {endpoint}', 
                             f'Status: {response.status_code}')
            elif response.status_code >= 400:
                self.log_issue('HIGH', 'Backend', f'Client error: {endpoint}', 
                             f'Status: {response.status_code}')
            
            # Try to parse JSON if content-type suggests it
            if 'application/json' in result['content_type']:
                try:
                    result['json_data'] = response.json()
                except json.JSONDecodeError:
                    self.log_issue('HIGH', 'API', f'Invalid JSON response: {endpoint}',
                                 'Response claims to be JSON but is not parseable')
            
            return result
            
        except requests.exceptions.Timeout:
            self.log_issue('HIGH', 'Performance', f'Timeout: {endpoint}', 
                         f'Request timed out after {timeout}s')
            return {'endpoint': endpoint, 'success': False, 'error': 'timeout'}
        except requests.exceptions.ConnectionError:
            self.log_issue('CRITICAL', 'Infrastructure', f'Connection error: {endpoint}',
                         'Cannot connect to server')
            return {'endpoint': endpoint, 'success': False, 'error': 'connection_error'}
        except Exception as e:
            self.log_issue('HIGH', 'Testing', f'Unexpected error: {endpoint}', str(e))
            return {'endpoint': endpoint, 'success': False, 'error': str(e)}
    
    def test_frontend_pages(self):
        """Test all frontend pages"""
        print("🔍 Testing Frontend Pages...")
        
        pages = [
            '/',
            '/react-dashboard',
            '/professional-dashboard',
            '/phase2-dashboard',
            '/advanced-analysis',
            '/analysis-history'
        ]
        
        results = []
        for page in pages:
            result = self.test_endpoint(page)
            results.append(result)
            
            # Check if page loads properly
            if result.get('success'):
                if result['content_length'] < 1000:
                    self.log_issue('HIGH', 'Frontend', f'Suspiciously small page: {page}',
                                 f'Content length: {result["content_length"]} bytes')
            
        self.test_results['frontend_pages'] = results
        return results
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        print("🔍 Testing API Endpoints...")
        
        # Core API endpoints
        api_endpoints = [
            '/api/analyze/BTC-USDT',
            '/api/analyze/ETH-USDT',
            '/api/snapshot/BTC-USDT',
            '/api/orderbook/BTC-USDT',
            '/api/depth-chart/BTC-USDT',
            '/api/technical-indicators/BTC-USDT',
            '/api/enhanced-ai/narrative/BTC-USDT',
            '/api/candles?symbol=BTC-USDT&interval=1h&limit=100',
            '/api/realtime/market-overview',
            '/api/realtime/streaming-stats',
            '/api/monitoring/system',
            '/api/monitoring/trading',
            '/api/monitoring/performance',
            '/health'
        ]
        
        results = []
        for endpoint in api_endpoints:
            result = self.test_endpoint(endpoint)
            results.append(result)
            
            # Check API-specific issues
            if result.get('success') and result.get('json_data'):
                data = result['json_data']
                
                # Check for error responses disguised as 200 OK
                if isinstance(data, dict):
                    if data.get('error') or data.get('success') == False:
                        self.log_issue('HIGH', 'API', f'API error in {endpoint}',
                                     f'Error: {data.get("error", "Unknown error")}')
                    
                    # Check for missing required fields
                    if endpoint.startswith('/api/analyze/') and 'analysis' not in data:
                        self.log_issue('HIGH', 'API', f'Missing analysis data: {endpoint}',
                                     'Analysis endpoint should return analysis data')
                    
                    # Check for timestamp issues
                    if 'timestamp' in data:
                        try:
                            # Try to parse timestamp
                            datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                        except (ValueError, AttributeError):
                            self.log_issue('MEDIUM', 'API', f'Invalid timestamp format: {endpoint}',
                                         f'Timestamp: {data.get("timestamp")}')
        
        self.test_results['api_endpoints'] = results
        return results
    
    def test_chart_integration(self):
        """Test chart-related functionality"""
        print("🔍 Testing Chart Integration...")
        
        # Test candles endpoint with different parameters
        test_params = [
            {'symbol': 'BTC-USDT', 'interval': '1h', 'limit': 100},
            {'symbol': 'ETH-USDT', 'interval': '15m', 'limit': 50},
            {'symbol': 'SOL-USDT', 'interval': '1d', 'limit': 30},
            {'symbol': 'INVALID-PAIR', 'interval': '1h', 'limit': 100},  # Test error handling
            {'symbol': 'BTC-USDT', 'interval': 'invalid', 'limit': 100}   # Test error handling
        ]
        
        results = []
        for params in test_params:
            query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
            endpoint = f'/api/candles?{query_string}'
            result = self.test_endpoint(endpoint)
            results.append(result)
            
            # Check candle data structure
            if result.get('success') and result.get('json_data'):
                data = result['json_data']
                if data.get('success') and data.get('candles'):
                    candles = data['candles']
                    if len(candles) > 0:
                        # Check candle structure
                        first_candle = candles[0]
                        required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                        for field in required_fields:
                            if field not in first_candle:
                                self.log_issue('HIGH', 'Chart Data', f'Missing field in candle: {field}',
                                             f'Endpoint: {endpoint}')
                        
                        # Check data consistency
                        for candle in candles[:10]:  # Check first 10 candles
                            if candle['high'] < candle['low']:
                                self.log_issue('CRITICAL', 'Chart Data', 'Invalid OHLC data',
                                             f'High < Low: {candle}')
                            if candle['high'] < candle['open'] or candle['high'] < candle['close']:
                                self.log_issue('CRITICAL', 'Chart Data', 'Invalid OHLC data',
                                             f'High < Open/Close: {candle}')
                            if candle['low'] > candle['open'] or candle['low'] > candle['close']:
                                self.log_issue('CRITICAL', 'Chart Data', 'Invalid OHLC data',
                                             f'Low > Open/Close: {candle}')
        
        self.test_results['chart_integration'] = results
        return results
    
    def test_smc_analysis(self):
        """Test Smart Money Concept analysis"""
        print("🔍 Testing SMC Analysis...")
        
        symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT']
        results = []
        
        for symbol in symbols:
            endpoint = f'/api/analyze/{symbol}'
            result = self.test_endpoint(endpoint)
            results.append(result)
            
            if result.get('success') and result.get('json_data'):
                data = result['json_data']
                
                # Check for SMC-specific fields
                smc_fields = ['smc_patterns', 'confluence_score', 'market_structure']
                for field in smc_fields:
                    if field not in data:
                        self.log_issue('MEDIUM', 'SMC Analysis', f'Missing SMC field: {field}',
                                     f'Symbol: {symbol}')
                
                # Check confidence score validity
                if 'confidence' in data:
                    confidence = data['confidence']
                    if not (0 <= confidence <= 1):
                        self.log_issue('HIGH', 'SMC Analysis', 'Invalid confidence score',
                                     f'Confidence: {confidence}, should be 0-1')
        
        self.test_results['smc_analysis'] = results
        return results
    
    def test_ai_components(self):
        """Test AI-powered components"""
        print("🔍 Testing AI Components...")
        
        # Test AI narrative endpoint
        symbols = ['BTC-USDT', 'ETH-USDT']
        results = []
        
        for symbol in symbols:
            endpoint = f'/api/enhanced-ai/narrative/{symbol}'
            result = self.test_endpoint(endpoint, timeout=30)  # AI calls take longer
            results.append(result)
            
            if result.get('success') and result.get('json_data'):
                data = result['json_data']
                
                # Check AI response structure
                if 'narrative' not in data:
                    self.log_issue('HIGH', 'AI Components', f'Missing AI narrative: {symbol}',
                                 'AI endpoint should return narrative')
                
                # Check for empty or too short narratives
                if data.get('narrative') and len(data['narrative']) < 50:
                    self.log_issue('MEDIUM', 'AI Components', f'Suspiciously short narrative: {symbol}',
                                 f'Narrative length: {len(data["narrative"])} chars')
        
        # Test AI connection
        ai_test_result = self.test_endpoint('/api/enhanced-ai/test-connection')
        results.append(ai_test_result)
        
        self.test_results['ai_components'] = results
        return results
    
    def test_error_handling(self):
        """Test error handling capabilities"""
        print("🔍 Testing Error Handling...")
        
        # Test invalid endpoints
        invalid_endpoints = [
            '/api/analyze/INVALID-SYMBOL',
            '/api/nonexistent-endpoint',
            '/api/candles?symbol=INVALID&interval=invalid',
            '/api/analyze/',  # Missing symbol
        ]
        
        results = []
        for endpoint in invalid_endpoints:
            result = self.test_endpoint(endpoint)
            results.append(result)
            
            # Error endpoints should return proper HTTP codes
            if result.get('status_code') == 200:
                self.log_issue('MEDIUM', 'Error Handling', f'Invalid endpoint returns 200: {endpoint}',
                             'Should return 400 or 404 for invalid requests')
        
        self.test_results['error_handling'] = results
        return results
    
    def test_performance_monitoring(self):
        """Test monitoring and performance endpoints"""
        print("🔍 Testing Performance Monitoring...")
        
        monitoring_endpoints = [
            '/health',
            '/api/monitoring/system',
            '/api/monitoring/trading',
            '/api/monitoring/performance',
            '/api/monitoring/dashboard'
        ]
        
        results = []
        for endpoint in monitoring_endpoints:
            result = self.test_endpoint(endpoint)
            results.append(result)
            
            if result.get('success') and result.get('json_data'):
                data = result['json_data']
                
                # Check health endpoint
                if endpoint == '/health':
                    if 'status' not in data:
                        self.log_issue('HIGH', 'Monitoring', 'Health endpoint missing status',
                                     'Health check should return status')
                
                # Check monitoring data structure
                if endpoint.startswith('/api/monitoring/'):
                    if not isinstance(data, dict):
                        self.log_issue('HIGH', 'Monitoring', f'Invalid monitoring data: {endpoint}',
                                     'Monitoring endpoints should return dict')
        
        self.test_results['performance_monitoring'] = results
        return results
    
    def test_database_connectivity(self):
        """Test database-related functionality"""
        print("🔍 Testing Database Connectivity...")
        
        # Test endpoints that require database
        db_endpoints = [
            '/api/analyze/BTC-USDT',  # Should store analysis
            '/analysis-history',       # Should retrieve history
            '/api/monitoring/trading'  # Should access trading data
        ]
        
        results = []
        for endpoint in db_endpoints:
            result = self.test_endpoint(endpoint)
            results.append(result)
            
            if not result.get('success'):
                self.log_issue('HIGH', 'Database', f'Database-dependent endpoint failed: {endpoint}',
                             'May indicate database connectivity issues')
        
        self.test_results['database_connectivity'] = results
        return results
    
    def generate_comprehensive_report(self):
        """Generate comprehensive testing report"""
        print("\n" + "="*80)
        print("🔍 COMPREHENSIVE APPLICATION TESTING REPORT")
        print("="*80)
        
        # Summary statistics
        total_tests = sum(len(results) for results in self.test_results.values())
        total_issues = len(self.issues_found)
        
        print(f"\n📊 TESTING SUMMARY:")
        print(f"Total Tests Executed: {total_tests}")
        print(f"Total Issues Found: {total_issues}")
        
        # Issue breakdown by severity
        severity_counts = {}
        for issue in self.issues_found:
            severity = issue['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        print(f"\n⚠️  ISSUES BY SEVERITY:")
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                print(f"  {severity}: {count} issues")
        
        # Detailed issues
        print(f"\n🔍 DETAILED ISSUES:")
        for i, issue in enumerate(self.issues_found, 1):
            print(f"\n{i}. [{issue['severity']}] {issue['component']}: {issue['issue']}")
            if issue['details']:
                print(f"   Details: {issue['details']}")
        
        # Test results summary
        print(f"\n📋 TEST RESULTS SUMMARY:")
        for test_category, results in self.test_results.items():
            successful = sum(1 for r in results if r.get('success'))
            total = len(results)
            print(f"  {test_category}: {successful}/{total} passed")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        critical_issues = [i for i in self.issues_found if i['severity'] == 'CRITICAL']
        if critical_issues:
            print("  🚨 CRITICAL ISSUES MUST BE FIXED IMMEDIATELY:")
            for issue in critical_issues:
                print(f"    - {issue['component']}: {issue['issue']}")
        
        high_issues = [i for i in self.issues_found if i['severity'] == 'HIGH']
        if high_issues:
            print("  🔴 HIGH PRIORITY FIXES:")
            for issue in high_issues[:5]:  # Show top 5
                print(f"    - {issue['component']}: {issue['issue']}")
        
        # Performance recommendations
        slow_endpoints = [i for i in self.issues_found if 'Performance' in i['component']]
        if slow_endpoints:
            print("  ⚡ PERFORMANCE OPTIMIZATIONS NEEDED:")
            for issue in slow_endpoints:
                print(f"    - {issue['issue']}")
        
        print("\n" + "="*80)
        print("🔍 TESTING COMPLETE")
        print("="*80)
        
        return {
            'total_tests': total_tests,
            'total_issues': total_issues,
            'severity_breakdown': severity_counts,
            'issues': self.issues_found,
            'test_results': self.test_results
        }
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Application Testing...")
        print("="*80)
        
        # Run all test categories
        self.test_frontend_pages()
        self.test_api_endpoints()
        self.test_chart_integration()
        self.test_smc_analysis()
        self.test_ai_components()
        self.test_error_handling()
        self.test_performance_monitoring()
        self.test_database_connectivity()
        
        # Generate comprehensive report
        return self.generate_comprehensive_report()

def main():
    """Main testing function"""
    print("🔍 Comprehensive Application Testing - Crypto Trading Dashboard")
    print("Testing all components to identify weaknesses and issues...")
    
    tester = ComprehensiveAppTester()
    
    try:
        report = tester.run_comprehensive_tests()
        
        # Save report to file
        with open('comprehensive_testing_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: comprehensive_testing_report.json")
        
        return report
        
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()