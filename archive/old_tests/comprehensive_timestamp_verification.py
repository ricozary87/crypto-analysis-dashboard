#!/usr/bin/env python3
"""
COMPREHENSIVE TIMESTAMP VERIFICATION
Verifikasi lengkap sistem timestamp di dashboard analisa kripto
"""

import requests
import json
from datetime import datetime
import re

class TimestampVerifier:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.test_symbols = ['BTC', 'ETH', 'SOL', 'TIA', 'RENDER']
        self.results = []
        
    def is_valid_iso_timestamp(self, timestamp_str):
        """Check if timestamp is in valid ISO format"""
        try:
            # Check basic ISO format: YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM:SS.sss
            iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$'
            if not re.match(iso_pattern, str(timestamp_str)):
                return False, f"Invalid ISO format: {timestamp_str}"
            
            # Try to parse as datetime
            if timestamp_str.endswith('Z'):
                dt = datetime.fromisoformat(timestamp_str[:-1])
            else:
                dt = datetime.fromisoformat(timestamp_str)
            
            # Check if year is reasonable (not 1970)
            if dt.year < 2020:
                return False, f"Year too old: {dt.year}"
                
            return True, f"Valid ISO: {timestamp_str}"
            
        except Exception as e:
            return False, f"Parse error: {e}"
    
    def test_endpoint(self, endpoint, symbol="BTC", description=""):
        """Test a single endpoint for timestamp format"""
        print(f"\n🔍 Testing {endpoint} - {description}")
        
        try:
            url = f"{self.base_url}{endpoint.replace('<symbol>', symbol)}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                result = f"❌ HTTP {response.status_code}"
                print(f"  {result}")
                self.results.append({
                    'endpoint': endpoint,
                    'status': 'FAILED',
                    'error': result
                })
                return False
            
            data = response.json()
            
            # Check different possible timestamp locations
            timestamp_fields = []
            
            # Check chart data timestamps
            if 'chart' in data and isinstance(data['chart'], list):
                for i, item in enumerate(data['chart'][:5]):  # Check first 5 items
                    if 'timestamp' in item:
                        timestamp_fields.append(f"chart[{i}].timestamp")
            
            # Check enhanced chart data
            if 'data' in data and isinstance(data['data'], list):
                for i, item in enumerate(data['data'][:5]):  # Check first 5 items
                    if 'timestamp' in item:
                        timestamp_fields.append(f"data[{i}].timestamp")
            
            # Check candlestick data
            if 'candlestick_data' in data and isinstance(data['candlestick_data'], list):
                for i, item in enumerate(data['candlestick_data'][:5]):  # Check first 5 items
                    if 'timestamp' in item:
                        timestamp_fields.append(f"candlestick_data[{i}].timestamp")
            
            # Check analysis chart
            if 'analysis' in data and 'chart' in data['analysis']:
                for i, item in enumerate(data['analysis']['chart'][:5]):  # Check first 5 items
                    if 'timestamp' in item:
                        timestamp_fields.append(f"analysis.chart[{i}].timestamp")
            
            # Check analysis timestamp field
            if 'analysis' in data and isinstance(data['analysis'], dict):
                if 'timestamp' in data['analysis']:
                    timestamp_fields.append("analysis.timestamp")
            
            # Check generated_at timestamp
            if 'generated_at' in data and data['generated_at']:
                timestamp_fields.append("generated_at")
            
            # Check created_at timestamp
            if 'created_at' in data and data['created_at']:
                timestamp_fields.append("created_at")
            
            # Check orderbook data timestamps
            if 'data' in data and isinstance(data['data'], dict):
                if 'ts' in data['data']:
                    timestamp_fields.append("data.ts")
            
            # Check snapshot data timestamps
            if 'snapshot' in data and isinstance(data['snapshot'], dict):
                if 'timestamp' in data['snapshot']:
                    timestamp_fields.append("snapshot.timestamp")
            
            # Check any other timestamp fields in root
            for key in ['timestamp', 'ts', 'time', 'updated_at']:
                if key in data and data[key]:
                    timestamp_fields.append(key)
            
            if not timestamp_fields:
                result = f"⚠️  No timestamp fields found"
                print(f"  {result}")
                self.results.append({
                    'endpoint': endpoint,
                    'status': 'WARNING',
                    'error': result
                })
                return True  # Not necessarily an error
            
            # Verify each timestamp field
            all_valid = True
            for field in timestamp_fields:
                # Extract the actual timestamp value
                try:
                    parts = field.split('.')
                    value = data
                    for part in parts:
                        if '[' in part:
                            # Handle array access like chart[0]
                            key = part.split('[')[0]
                            index = int(part.split('[')[1].split(']')[0])
                            value = value[key][index]
                        else:
                            value = value[part]
                    
                    is_valid, msg = self.is_valid_iso_timestamp(value)
                    if is_valid:
                        print(f"  ✅ {field}: {msg}")
                    else:
                        print(f"  ❌ {field}: {msg}")
                        all_valid = False
                        
                except Exception as e:
                    print(f"  ❌ {field}: Error accessing - {e}")
                    all_valid = False
            
            if all_valid:
                self.results.append({
                    'endpoint': endpoint,
                    'status': 'SUCCESS',
                    'timestamp_fields': len(timestamp_fields)
                })
                print(f"  ✅ All {len(timestamp_fields)} timestamp fields valid")
                return True
            else:
                self.results.append({
                    'endpoint': endpoint,
                    'status': 'FAILED',
                    'error': 'Invalid timestamp format'
                })
                return False
                
        except Exception as e:
            result = f"❌ Exception: {e}"
            print(f"  {result}")
            self.results.append({
                'endpoint': endpoint,
                'status': 'FAILED',
                'error': result
            })
            return False
    
    def verify_backend_endpoints(self):
        """Verify all backend endpoints that send timestamp data"""
        print("=" * 60)
        print("🔍 BACKEND API TIMESTAMP VERIFICATION")
        print("=" * 60)
        
        endpoints = [
            ('/api/analyze/<symbol>', 'Basic analysis with chart data'),
            ('/api/enhanced-charts/data/<symbol>', 'Enhanced candlestick chart data'),
            ('/api/enhanced-charts/volume-profile/<symbol>', 'Volume profile data'),
            ('/api/indicators/calculate/<symbol>', 'Technical indicators'),
            ('/api/snapshot/<symbol>', 'Market snapshot data'),
            ('/api/orderbook/<symbol>', 'Orderbook data'),
            ('/api/depth-chart/<symbol>', 'Depth chart data'),
        ]
        
        backend_results = []
        for endpoint, description in endpoints:
            success = self.test_endpoint(endpoint, 'BTC', description)
            backend_results.append(success)
        
        return backend_results
    
    def verify_frontend_handling(self):
        """Check frontend JavaScript timestamp handling"""
        print("\n" + "=" * 60)
        print("🔍 FRONTEND JAVASCRIPT TIMESTAMP HANDLING")
        print("=" * 60)
        
        # Check dashboard.html
        try:
            with open('templates/dashboard.html', 'r') as f:
                dashboard_content = f.read()
            
            # Check for formatTimestamp function
            if 'function formatTimestamp' in dashboard_content:
                print("  ✅ formatTimestamp function found in dashboard.html")
            else:
                print("  ❌ formatTimestamp function NOT found in dashboard.html")
                return False
            
            # Check for timestamp usage in charts
            if 'formatTimestamp(c.timestamp)' in dashboard_content:
                print("  ✅ formatTimestamp is used in chart rendering")
            else:
                print("  ❌ formatTimestamp is NOT used in chart rendering")
                return False
                
        except Exception as e:
            print(f"  ❌ Error reading dashboard.html: {e}")
            return False
        
        # Check phase2_advanced_dashboard.html
        try:
            with open('templates/phase2_advanced_dashboard.html', 'r') as f:
                phase2_content = f.read()
            
            # Check for any problematic timestamp handling
            if 'new Date(' in phase2_content:
                print("  ⚠️  new Date() usage found in phase2_advanced_dashboard.html")
                # This is ok for some cases, but let's note it
            
            print("  ✅ Phase2 dashboard checked")
                
        except Exception as e:
            print(f"  ❌ Error reading phase2_advanced_dashboard.html: {e}")
            return False
        
        return True
    
    def test_actual_chart_rendering(self):
        """Test actual chart data that would be sent to frontend"""
        print("\n" + "=" * 60)
        print("🔍 ACTUAL CHART DATA VERIFICATION")
        print("=" * 60)
        
        # Test enhanced charts endpoint specifically
        try:
            response = requests.get(f"{self.base_url}/api/enhanced-charts/data/BTC")
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    chart_data = data['data']
                    
                    print(f"  📊 Chart data points: {len(chart_data)}")
                    
                    # Check first 10 timestamps
                    for i in range(min(10, len(chart_data))):
                        item = chart_data[i]
                        timestamp = item.get('timestamp')
                        is_valid, msg = self.is_valid_iso_timestamp(timestamp)
                        
                        if is_valid:
                            print(f"  ✅ Point {i}: {timestamp}")
                        else:
                            print(f"  ❌ Point {i}: {msg}")
                            return False
                    
                    return True
                else:
                    print(f"  ❌ No chart data in response")
                    print(f"  Response keys: {list(data.keys())}")
                    return False
            else:
                print(f"  ❌ HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error testing chart data: {e}")
            return False
    
    def generate_report(self):
        """Generate comprehensive verification report"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TIMESTAMP VERIFICATION REPORT")
        print("=" * 60)
        
        # Count results
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r['status'] == 'SUCCESS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAILED'])
        warning_tests = len([r for r in self.results if r['status'] == 'WARNING'])
        
        print(f"📊 STATISTICS:")
        print(f"  Total Tests: {total_tests}")
        print(f"  ✅ Successful: {successful_tests}")
        print(f"  ❌ Failed: {failed_tests}")
        print(f"  ⚠️  Warnings: {warning_tests}")
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"  📈 Success Rate: {success_rate:.1f}%")
        
        # Detailed results
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAILED':
                    print(f"  - {result['endpoint']}: {result['error']}")
        
        if warning_tests > 0:
            print(f"\n⚠️  WARNINGS:")
            for result in self.results:
                if result['status'] == 'WARNING':
                    print(f"  - {result['endpoint']}: {result['error']}")
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if success_rate >= 90:
            print("  ✅ EXCELLENT - Timestamp system working properly")
        elif success_rate >= 70:
            print("  ⚠️  GOOD - Minor issues need attention")
        else:
            print("  ❌ NEEDS WORK - Significant timestamp issues remain")
        
        return success_rate >= 90
    
    def run_complete_verification(self):
        """Run complete timestamp verification"""
        print("🚀 STARTING COMPREHENSIVE TIMESTAMP VERIFICATION")
        print("=" * 60)
        
        # 1. Backend API verification
        backend_success = self.verify_backend_endpoints()
        
        # 2. Frontend handling verification
        frontend_success = self.verify_frontend_handling()
        
        # 3. Actual chart data verification
        chart_success = self.test_actual_chart_rendering()
        
        # 4. Generate comprehensive report
        overall_success = self.generate_report()
        
        print(f"\n🏁 VERIFICATION COMPLETE!")
        print(f"Backend Success: {sum(backend_success)}/{len(backend_success)}")
        print(f"Frontend Success: {frontend_success}")
        print(f"Chart Data Success: {chart_success}")
        print(f"Overall Success: {overall_success}")
        
        return overall_success

def main():
    """Main verification function"""
    verifier = TimestampVerifier()
    success = verifier.run_complete_verification()
    
    if success:
        print("\n🎉 TIMESTAMP VERIFICATION SUCCESS!")
        print("✅ All systems are working properly")
    else:
        print("\n⚠️  TIMESTAMP VERIFICATION ISSUES FOUND")
        print("❌ Some systems need attention")
    
    return success

if __name__ == "__main__":
    main()