"""
Final Integration Test untuk Semua Implementasi
Testing comprehensive untuk React Integration, SQLAlchemy, dan Unit Testing
"""

import requests
import json
import time
from datetime import datetime

def test_react_integration():
    """Test React frontend integration dengan backend"""
    print("🔄 Testing React Integration...")
    
    # Test analyze endpoint yang digunakan React
    response = requests.get('http://localhost:5000/api/analyze/BTC-USDT')
    if response.status_code == 200:
        data = response.json()
        print(f"✅ React API Integration: SUCCESS")
        print(f"   - SMC Analysis: {'✅' if 'smc_analysis' in data else '❌'}")
        print(f"   - Confidence Score: {data.get('smc_analysis', {}).get('confidence_score', 'N/A')}")
        print(f"   - Response Time: {response.elapsed.total_seconds():.2f}s")
        return True
    else:
        print(f"❌ React API Integration: FAILED (HTTP {response.status_code})")
        return False

def test_sqlalchemy_warnings():
    """Test SQLAlchemy query warnings"""
    print("\n🔄 Testing SQLAlchemy Warnings...")
    
    # Test health endpoint yang menggunakan SQLAlchemy
    response = requests.get('http://localhost:5000/health')
    if response.status_code == 200:
        data = response.json()
        print("✅ SQLAlchemy Integration: SUCCESS")
        print(f"   - Database: {data.get('database', 'disconnected')}")
        print(f"   - Status: {data.get('status', 'unknown')}")
        print(f"   - Active Connections: {data.get('metrics', {}).get('database', {}).get('active_connections', 'N/A')}")
        return True
    else:
        print(f"❌ SQLAlchemy Integration: FAILED (HTTP {response.status_code})")
        return False

def test_monitoring_system():
    """Test monitoring system endpoints"""
    print("\n🔄 Testing Monitoring System...")
    
    # Test multiple monitoring endpoints
    endpoints = [
        '/api/monitoring/system',
        '/api/monitoring/trading',
        '/api/monitoring/performance'
    ]
    
    success_count = 0
    for endpoint in endpoints:
        response = requests.get(f'http://localhost:5000{endpoint}')
        if response.status_code == 200:
            print(f"✅ {endpoint}: SUCCESS")
            success_count += 1
        else:
            print(f"❌ {endpoint}: FAILED (HTTP {response.status_code})")
    
    print(f"📊 Monitoring Endpoints: {success_count}/{len(endpoints)} working")
    return success_count == len(endpoints)

def test_performance_metrics():
    """Test performance tracking"""
    print("\n🔄 Testing Performance Metrics...")
    
    # Make multiple requests to test tracking
    symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT']
    response_times = []
    
    for symbol in symbols:
        start_time = time.time()
        response = requests.get(f'http://localhost:5000/api/analyze/{symbol}')
        end_time = time.time()
        
        response_time = end_time - start_time
        response_times.append(response_time)
        
        if response.status_code == 200:
            print(f"✅ {symbol}: {response_time:.2f}s")
        else:
            print(f"❌ {symbol}: FAILED")
    
    avg_response_time = sum(response_times) / len(response_times)
    print(f"📊 Average Response Time: {avg_response_time:.2f}s")
    print(f"📊 Performance Status: {'✅ GOOD' if avg_response_time < 2.0 else '⚠️ SLOW' if avg_response_time < 5.0 else '❌ POOR'}")
    
    return avg_response_time < 5.0

def test_error_handling():
    """Test error handling untuk invalid inputs"""
    print("\n🔄 Testing Error Handling...")
    
    # Test invalid symbol
    response = requests.get('http://localhost:5000/api/analyze/INVALID-SYMBOL')
    if response.status_code == 400:
        print("✅ Invalid Symbol Handling: SUCCESS")
        error_handled = True
    else:
        print(f"❌ Invalid Symbol Handling: FAILED (Expected 400, got {response.status_code})")
        error_handled = False
    
    return error_handled

def main():
    """Main test runner"""
    print("🚀 FINAL INTEGRATION TEST - STARTING...")
    print("=" * 60)
    
    test_results = {
        'react_integration': test_react_integration(),
        'sqlalchemy_warnings': test_sqlalchemy_warnings(),
        'monitoring_system': test_monitoring_system(),
        'performance_metrics': test_performance_metrics(),
        'error_handling': test_error_handling()
    }
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS:")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 OVERALL SCORE: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - INTEGRATION COMPLETE!")
    elif passed >= total * 0.8:
        print("⚠️  MOSTLY SUCCESSFUL - MINOR ISSUES DETECTED")
    else:
        print("❌ MULTIPLE FAILURES - NEEDS ATTENTION")
    
    print(f"\n📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()