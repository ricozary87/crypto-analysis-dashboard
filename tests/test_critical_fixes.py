#!/usr/bin/env python3
"""
Test Script untuk Critical Fixes
Testing 3 critical issues yang sudah diperbaiki
"""

import requests
import json
from datetime import datetime

def test_critical_fixes():
    """Test all 3 critical fixes"""
    base_url = "http://localhost:5000"
    results = []
    
    print("=" * 70)
    print("🔧 TESTING CRITICAL FIXES")
    print("=" * 70)
    
    # TEST 1: Price Action Analysis (Data Type Fix)
    print("\n1. Testing Price Action Analysis Fix...")
    try:
        response = requests.get(f"{base_url}/api/analyze/BTC", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("   ✅ Price Action Analysis: WORKING")
                print(f"   Current Price: ${data.get('currentPrice', 0):,.2f}")
                results.append(("Price Action Analysis", "PASS"))
            else:
                print("   ❌ Price Action Analysis: Failed (success=false)")
                results.append(("Price Action Analysis", "FAIL"))
        else:
            print(f"   ❌ Price Action Analysis: HTTP {response.status_code}")
            results.append(("Price Action Analysis", "FAIL"))
    except Exception as e:
        print(f"   ❌ Price Action Analysis: Error - {str(e)}")
        results.append(("Price Action Analysis", "ERROR"))
    
    # TEST 2: CCI Indicator (Added to Calculator)
    print("\n2. Testing CCI Indicator Fix...")
    try:
        response = requests.get(f"{base_url}/api/technical-indicators/BTC?indicators=cci", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "cci" in data.get("indicators", {}):
                cci_data = data["indicators"]["cci"]
                print("   ✅ CCI Indicator: WORKING")
                print(f"   CCI Signal: {cci_data.get('signal', 'N/A')}")
                print(f"   CCI Interpretation: {cci_data.get('interpretation', 'N/A')}")
                results.append(("CCI Indicator", "PASS"))
            else:
                print("   ❌ CCI Indicator: Not found in response")
                results.append(("CCI Indicator", "FAIL"))
        else:
            print(f"   ❌ CCI Indicator: HTTP {response.status_code}")
            results.append(("CCI Indicator", "FAIL"))
    except Exception as e:
        print(f"   ❌ CCI Indicator: Error - {str(e)}")
        results.append(("CCI Indicator", "ERROR"))
    
    # TEST 3: JSON Serialization (All indicators)
    print("\n3. Testing JSON Serialization Fix...")
    try:
        response = requests.get(f"{base_url}/api/technical-indicators/BTC", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                # Check if we can properly parse all indicators without errors
                indicators = data.get("indicators", {})
                indicator_count = len(indicators)
                print("   ✅ JSON Serialization: WORKING")
                print(f"   Successfully serialized {indicator_count} indicators")
                print(f"   Indicators: {', '.join(list(indicators.keys())[:5])}...")
                results.append(("JSON Serialization", "PASS"))
            else:
                print("   ❌ JSON Serialization: Failed (success=false)")
                results.append(("JSON Serialization", "FAIL"))
        else:
            print(f"   ❌ JSON Serialization: HTTP {response.status_code}")
            results.append(("JSON Serialization", "FAIL"))
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON Serialization: JSON Parse Error - {str(e)}")
        results.append(("JSON Serialization", "JSON_ERROR"))
    except Exception as e:
        print(f"   ❌ JSON Serialization: Error - {str(e)}")
        results.append(("JSON Serialization", "ERROR"))
    
    # SUMMARY
    print("\n" + "=" * 70)
    print("📊 CRITICAL FIXES SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, status in results if status == "PASS")
    total = len(results)
    
    for fix_name, status in results:
        status_emoji = "✅" if status == "PASS" else "❌"
        print(f"{status_emoji} {fix_name}: {status}")
    
    print(f"\nTotal Score: {passed}/{total} ({(passed/total*100):.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL CRITICAL FIXES ARE WORKING PERFECTLY!")
    else:
        print("\n⚠️  Some fixes still need attention")
    
    return passed, total

if __name__ == "__main__":
    test_critical_fixes()