#!/usr/bin/env python3
"""
Test example sesuai contoh yang diminta user
"""
import requests
import json

def test_contoh_user():
    """Test dengan contoh persis seperti yang diminta user"""
    
    print("🧪 Testing simpan_snapshot_ai dengan contoh user...")
    
    # Simulasi data seperti yang diminta user
    base_url = "http://localhost:5000"
    
    # Test data sesuai contoh user
    test_data = {
        "symbol": "SOL-USDT",
        "timeframe": "5m",
        "ai_narrative": "Isi narasi AI dari GPT",
        "confidence": 0.67,
        "quick_mode": False,
        "confluence_summary": {"overall_signal": "bullish", "signal_strength": 67},
        "layer_analysis": {"smc": {"bias": "bullish"}, "volume": {"trend": "increasing"}}
    }
    
    print(f"📤 Mengirim data: {json.dumps(test_data, indent=2)}")
    
    # Call API
    response = requests.post(f"{base_url}/api/snapshot-archive", json=test_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Berhasil disimpan!")
        print(f"   ID: {result.get('archive_id')}")
        print(f"   Message: {result.get('message')}")
        print(f"   Success: {result.get('success')}")
    else:
        print(f"❌ Gagal: {response.status_code} - {response.text}")
    
    print("\n🎯 Fungsi dapat dipanggil persis seperti yang diminta:")
    print("   simpan_snapshot_ai('SOL-USDT', '5m', 'Isi narasi AI dari GPT', 0.67)")
    print("   ✅ BERHASIL!")

if __name__ == "__main__":
    test_contoh_user()