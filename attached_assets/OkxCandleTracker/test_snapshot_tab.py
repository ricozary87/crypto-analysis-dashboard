#!/usr/bin/env python3
"""
Test script untuk debugging snapshot tab error
"""
import requests
import json

def test_snapshot_endpoints():
    """Test both snapshot endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing snapshot endpoints...")
    
    # Test 1: Regular snapshot endpoint
    print("\n1. Testing regular snapshot endpoint...")
    try:
        response = requests.get(f"{base_url}/api/snapshot/BTC-USDT/1h", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success', 'N/A')}")
            print(f"   Has smc_analysis: {'smc_analysis' in result}")
            print(f"   Has volume_analysis: {'volume_analysis' in result}")
            print(f"   Has layer_analysis: {'layer_analysis' in result}")
        else:
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    
    # Test 2: AI snapshot endpoint  
    print("\n2. Testing AI snapshot endpoint...")
    try:
        response = requests.get(f"{base_url}/api/snapshot-ai/BTC-USDT/1h", timeout=15)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success', 'N/A')}")
            print(f"   Has ai_narrative: {'ai_narrative' in result}")
            print(f"   Has layer_analysis: {'layer_analysis' in result}")
            print(f"   Has confluence_summary: {'confluence_summary' in result}")
            if 'ai_narrative' in result:
                print(f"   AI narrative length: {len(result['ai_narrative'])} chars")
        else:
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    
    # Test 3: Quick mode AI snapshot
    print("\n3. Testing AI snapshot quick mode...")
    try:
        response = requests.get(f"{base_url}/api/snapshot-ai/BTC-USDT/1h?quick=true", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success', 'N/A')}")
            print(f"   Has ai_narrative: {'ai_narrative' in result}")
            if 'ai_narrative' in result:
                print(f"   AI narrative length: {len(result['ai_narrative'])} chars")
        else:
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_snapshot_endpoints()