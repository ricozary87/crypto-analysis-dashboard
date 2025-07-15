#!/usr/bin/env python3
"""
Test script untuk fungsi simpan_snapshot_ai
"""
import requests
import json
import time

def test_simpan_snapshot_ai():
    """Test the simpan_snapshot_ai function via API"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing simpan_snapshot_ai function...")
    
    # Test 1: Basic functionality
    print("\n1. Testing basic save functionality...")
    test_data = {
        "symbol": "SOL-USDT",
        "timeframe": "5m",
        "ai_narrative": "Test AI narrative dari GPT-4o untuk SOL-USDT 5m timeframe",
        "confidence": 0.67,
        "quick_mode": False,
        "confluence_summary": {
            "overall_signal": "bullish",
            "signal_strength": 67,
            "bearish_layers": 1,
            "bullish_layers": 4,
            "neutral_layers": 2
        },
        "layer_analysis": {
            "smc": {"bias": "bullish", "confidence": 0.7},
            "volume": {"trend": "increasing", "confidence": 0.6},
            "orderbook": {"bias": "neutral", "confidence": 0.5}
        }
    }
    
    response = requests.post(f"{base_url}/api/snapshot-archive", json=test_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Save successful: {result}")
        archive_id = result.get('archive_id')
    else:
        print(f"❌ Save failed: {response.status_code} - {response.text}")
        return
    
    # Test 2: Retrieve saved snapshots
    print("\n2. Testing retrieval functionality...")
    response = requests.get(f"{base_url}/api/snapshot-archive")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Retrieval successful: Found {len(result.get('data', []))} snapshots")
        for snapshot in result.get('data', [])[:2]:  # Show first 2
            print(f"   - {snapshot['symbol']} {snapshot['timeframe']} (Confidence: {snapshot.get('confidence', 'N/A')})")
    else:
        print(f"❌ Retrieval failed: {response.status_code} - {response.text}")
    
    # Test 3: Get specific snapshot by ID
    if archive_id:
        print(f"\n3. Testing get by ID (ID: {archive_id})...")
        response = requests.get(f"{base_url}/api/snapshot-archive/{archive_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Get by ID successful: {result['data']['symbol']} {result['data']['timeframe']}")
        else:
            print(f"❌ Get by ID failed: {response.status_code} - {response.text}")
    
    # Test 4: Get statistics
    print("\n4. Testing statistics functionality...")
    response = requests.get(f"{base_url}/api/snapshot-archive/statistics")
    if response.status_code == 200:
        result = response.json()
        stats = result.get('data', {})
        print(f"✅ Statistics successful:")
        print(f"   - Total snapshots: {stats.get('total_snapshots', 0)}")
        print(f"   - Average confidence: {stats.get('avg_confidence', 0):.2f}")
        print(f"   - Quick mode count: {stats.get('quick_mode_count', 0)}")
        print(f"   - Comprehensive mode count: {stats.get('comprehensive_mode_count', 0)}")
    else:
        print(f"❌ Statistics failed: {response.status_code} - {response.text}")
    
    # Test 5: Multiple saves with different parameters
    print("\n5. Testing multiple saves...")
    symbols = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
    timeframes = ["1h", "5m", "15m"]
    
    for i, (symbol, timeframe) in enumerate(zip(symbols, timeframes)):
        test_data = {
            "symbol": symbol,
            "timeframe": timeframe,
            "ai_narrative": f"Test AI narrative #{i+1} untuk {symbol} {timeframe}",
            "confidence": 0.5 + (i * 0.15),  # Varying confidence
            "quick_mode": i % 2 == 0,  # Alternate quick mode
            "confluence_summary": {"overall_signal": "neutral", "signal_strength": 50 + (i * 10)}
        }
        
        response = requests.post(f"{base_url}/api/snapshot-archive", json=test_data)
        if response.status_code == 200:
            print(f"✅ Saved {symbol} {timeframe}")
        else:
            print(f"❌ Failed to save {symbol} {timeframe}")
    
    # Test 6: Filter by symbol
    print("\n6. Testing filter by symbol...")
    response = requests.get(f"{base_url}/api/snapshot-archive?symbol=BTC-USDT")
    if response.status_code == 200:
        result = response.json()
        btc_snapshots = result.get('data', [])
        print(f"✅ BTC-USDT filter successful: Found {len(btc_snapshots)} snapshots")
    else:
        print(f"❌ BTC-USDT filter failed: {response.status_code} - {response.text}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_simpan_snapshot_ai()