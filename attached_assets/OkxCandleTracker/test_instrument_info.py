#!/usr/bin/env python3
"""
Test untuk endpoint Instrument Info OKX API
"""

from okx_service import OKXService
import json

def test_endpoint(endpoint_name, test_func):
    """Helper function to test an endpoint"""
    print(f"\n🔍 Testing {endpoint_name}...")
    try:
        result = test_func()
        if result:
            print(f"✅ {endpoint_name} - BERFUNGSI")
            return True
        else:
            print(f"❌ {endpoint_name} - GAGAL (No data)")
            return False
    except Exception as e:
        print(f"❌ {endpoint_name} - ERROR: {str(e)}")
        return False

def main():
    print("🔹 OKX Instrument Info API Testing")
    print("="*50)
    
    okx = OKXService()
    
    results = {}
    
    # 1. 📄 List Semua Pair - /api/v5/public/instruments
    def test_all_instruments():
        # Test SPOT instruments
        spot_data = okx.get_all_instruments('SPOT')
        if spot_data:
            print(f"   📊 SPOT instruments: {len(spot_data)}")
            if spot_data:
                sample = spot_data[0]
                print(f"   💰 Sample: {sample['symbol']} ({sample['base_currency']}/{sample['quote_currency']})")
        
        # Test FUTURES instruments
        futures_data = okx.get_all_instruments('FUTURES')
        if futures_data:
            print(f"   📊 FUTURES instruments: {len(futures_data)}")
            
        # Test SWAP instruments
        swap_data = okx.get_all_instruments('SWAP')
        if swap_data:
            print(f"   📊 SWAP instruments: {len(swap_data)}")
            
        return len(spot_data) > 0 or len(futures_data) > 0 or len(swap_data) > 0
    
    results['instruments'] = test_endpoint("📄 List Semua Pair", test_all_instruments)
    
    # 2. 📅 Delivery Info - /api/v5/public/delivery-exercise-history
    def test_delivery_history():
        # Test dengan underlying yang memiliki delivery history
        underlyings = ['BTC-USD', 'ETH-USD', 'BTC-USDT']
        
        for underlying in underlyings:
            try:
                data = okx.get_delivery_exercise_history(underlying)
                if data:
                    print(f"   📅 Delivery history for {underlying}: {len(data)} records")
                    if data:
                        sample = data[0]
                        print(f"   💰 Sample: {sample['symbol']} - Price ${sample['delivery_price']:.2f}")
                        print(f"   📅 Delivery: {sample['delivery_datetime']}")
                    return True
            except Exception as e:
                continue
        
        print("   ℹ️  No delivery history found for test underlyings")
        return False
    
    results['delivery_history'] = test_endpoint("📅 Delivery Info", test_delivery_history)
    
    # 3. ⏱ Estimated Funding - /api/v5/public/funding-rate
    def test_estimated_funding():
        # Test dengan SWAP symbol (perpetual futures)
        swap_symbols = ['BTC-USDT-SWAP', 'ETH-USDT-SWAP', 'SOL-USDT-SWAP']
        
        for symbol in swap_symbols:
            try:
                data = okx.get_estimated_funding_rate(symbol)
                if data:
                    print(f"   ⏱ Funding rate for {symbol}: {data['funding_rate']:.6f}")
                    print(f"   ⏰ Next funding: {data['next_funding_datetime']}")
                    print(f"   📊 Interval: {data['funding_interval']}")
                    return True
            except Exception as e:
                continue
        
        return False
    
    results['estimated_funding'] = test_endpoint("⏱ Estimated Funding", test_estimated_funding)
    
    # Summary
    print("\n" + "="*50)
    print("📊 SUMMARY HASIL TESTING INSTRUMENT INFO")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    endpoint_names = {
        'instruments': 'List Semua Pair (/instruments)',
        'delivery_history': 'Delivery Info (/delivery-exercise-history)',
        'estimated_funding': 'Estimated Funding (/funding-rate)'
    }
    
    status_symbols = {
        'instruments': '📄',
        'delivery_history': '📅',
        'estimated_funding': '⏱'
    }
    
    for endpoint, result in results.items():
        status = "✅ BERFUNGSI" if result else "❌ GAGAL"
        symbol = status_symbols.get(endpoint, '📊')
        name = endpoint_names.get(endpoint, endpoint)
        print(f"{symbol} {name:<35} - {status}")
    
    print(f"\n🎯 Total: {passed_tests}/{total_tests} endpoint berhasil")
    
    if passed_tests == total_tests:
        print("🎉 SEMUA ENDPOINT INSTRUMENT INFO BERFUNGSI!")
    else:
        print(f"⚠️  {total_tests - passed_tests} endpoint perlu diperbaiki")
    
    print("="*50)
    
    # Tampilkan detail endpoint info
    print("\n📋 DETAIL ENDPOINT INFO:")
    print("="*50)
    print("📄 List Semua Pair - /api/v5/public/instruments")
    print("   • Daftar lengkap instrumen (spot, futures, options)")
    print("   • Mendukung filter berdasarkan instType")
    print("   • Informasi detail kontrak dan spesifikasi")
    print()
    print("📅 Delivery Info - /api/v5/public/delivery-exercise-history")
    print("   • Riwayat delivery/exercise untuk futures")
    print("   • Harga settlement dan waktu delivery")
    print("   • Data historis kontrak yang sudah expired")
    print()
    print("⏱ Estimated Funding - /api/v5/public/funding-rate")
    print("   • Estimasi funding rate periode berikutnya")
    print("   • Waktu funding berikutnya")
    print("   • Interval funding (biasanya 8 jam)")
    print("="*50)

if __name__ == "__main__":
    main()