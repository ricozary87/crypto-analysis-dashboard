#!/usr/bin/env python3
"""
Test script untuk timeout handling AI Engine
"""
import requests
import time

def test_ai_timeout():
    """Test AI timeout handling"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing AI timeout handling...")
    
    # Test 1: Quick mode (should be faster)
    print("\n1. Testing quick mode...")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/api/snapshot-ai/BTC-USDT/1h?quick=true", timeout=30)
        elapsed = time.time() - start_time
        print(f"   Status: {response.status_code}")
        print(f"   Time taken: {elapsed:.2f} seconds")
        if response.status_code == 200:
            result = response.json()
            if 'ai_narrative' in result:
                print(f"   AI narrative length: {len(result['ai_narrative'])} chars")
                print(f"   Success: {result.get('success', False)}")
                if "timeout" in result['ai_narrative'].lower():
                    print("   ⚠️ Fallback narrative due to timeout")
                else:
                    print("   ✅ AI narrative generated successfully")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 2: Comprehensive mode
    print("\n2. Testing comprehensive mode...")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/api/snapshot-ai/BTC-USDT/1h", timeout=45)
        elapsed = time.time() - start_time
        print(f"   Status: {response.status_code}")
        print(f"   Time taken: {elapsed:.2f} seconds")
        if response.status_code == 200:
            result = response.json()
            if 'ai_narrative' in result:
                print(f"   AI narrative length: {len(result['ai_narrative'])} chars")
                print(f"   Success: {result.get('success', False)}")
                if "timeout" in result['ai_narrative'].lower():
                    print("   ⚠️ Fallback narrative due to timeout")
                else:
                    print("   ✅ AI narrative generated successfully")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_ai_timeout()