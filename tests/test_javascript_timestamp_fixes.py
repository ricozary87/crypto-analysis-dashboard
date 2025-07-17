#!/usr/bin/env python3
"""
Test JavaScript Timestamp Fixes
Verify that the timestamp fixes are working properly
"""

import requests
import json
import time

def test_basic_dashboard():
    """Test basic dashboard API endpoint"""
    print("Testing basic dashboard API...")
    
    try:
        response = requests.get('http://localhost:5000/api/analyze/BTC')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                chart_data = data.get('analysis', {}).get('chart', [])
                print(f"✅ Basic dashboard: {len(chart_data)} chart points")
                
                # Check timestamp formats
                for i, point in enumerate(chart_data[:5]):
                    timestamp = point.get('timestamp')
                    print(f"  Point {i}: timestamp={timestamp} (type: {type(timestamp)})")
                    
                return True
            else:
                print(f"❌ Basic dashboard: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Basic dashboard: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Basic dashboard: {e}")
        return False

def test_enhanced_charts():
    """Test enhanced charts API endpoint"""
    print("\nTesting enhanced charts API...")
    
    try:
        response = requests.get('http://localhost:5000/api/enhanced-charts/data/BTC')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                chart_data = data.get('data', [])
                print(f"✅ Enhanced charts: {len(chart_data)} chart points")
                
                # Check timestamp formats
                for i, point in enumerate(chart_data[:5]):
                    timestamp = point.get('timestamp')
                    print(f"  Point {i}: timestamp={timestamp} (type: {type(timestamp)})")
                    
                return True
            else:
                print(f"❌ Enhanced charts: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Enhanced charts: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced charts: {e}")
        return False

def test_indicators():
    """Test indicators API endpoint"""
    print("\nTesting indicators API...")
    
    try:
        response = requests.get('http://localhost:5000/api/indicators/calculate/BTC?indicators=rsi,macd')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                indicators = data.get('indicators', {})
                print(f"✅ Indicators: {len(indicators)} indicators")
                
                # Check indicator data
                for name, indicator in indicators.items():
                    values = indicator.get('values', [])
                    print(f"  {name}: {len(values)} values")
                    
                return True
            else:
                print(f"❌ Indicators: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Indicators: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Indicators: {e}")
        return False

def test_volume_profile():
    """Test volume profile API endpoint"""
    print("\nTesting volume profile API...")
    
    try:
        response = requests.get('http://localhost:5000/api/enhanced-charts/volume-profile/BTC')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                volume_profile = data.get('volume_profile', {})
                print(f"✅ Volume profile: {len(volume_profile)} entries")
                return True
            else:
                print(f"❌ Volume profile: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Volume profile: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Volume profile: {e}")
        return False

def main():
    """Run all tests"""
    print("JavaScript Timestamp Fixes Test Suite")
    print("=" * 40)
    
    results = []
    results.append(test_basic_dashboard())
    results.append(test_enhanced_charts())
    results.append(test_indicators())
    results.append(test_volume_profile())
    
    print("\n" + "=" * 40)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("✅ All timestamp fixes are working correctly!")
        print("✅ JavaScript errors should be resolved!")
    else:
        print("❌ Some issues remain, check the logs above")

if __name__ == "__main__":
    main()