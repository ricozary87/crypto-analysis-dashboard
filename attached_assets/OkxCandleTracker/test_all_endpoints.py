#!/usr/bin/env python3
"""
Test komprehensif untuk semua endpoint OKX API
"""

from okx_service import OKXService
import json
import time

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
    print("🚀 OKX API Endpoint Testing Suite")
    print("="*60)
    
    okx = OKXService()
    test_symbol = "BTC-USDT"
    futures_symbol = "BTC-USDT-SWAP"
    
    results = {}
    
    # 1. 📊 Candlestick (Kline) - /market/candles
    def test_candlestick():
        data = okx.get_candlestick_data(test_symbol, "1h", 5)
        if data:
            print(f"   📊 Retrieved {len(data)} candlesticks")
            print(f"   💰 Latest price: ${data[-1]['close']:.2f}")
            return True
        return False
    
    results['candlestick'] = test_endpoint("📊 Candlestick (OHLCV)", test_candlestick)
    
    # 2. 🔁 Ticker - /market/ticker
    def test_ticker():
        data = okx.get_ticker_data(test_symbol)
        if data:
            print(f"   💰 Last price: ${data['last_price']:.2f}")
            print(f"   📊 24h volume: {data['volume_24h']:.2f}")
            print(f"   📈 24h change: {data['change_percent_24h']:.2f}%")
            return True
        return False
    
    results['ticker'] = test_endpoint("🔁 Ticker", test_ticker)
    
    # 3. 🧱 Order Book - /market/books
    def test_orderbook():
        data = okx.get_orderbook_data(test_symbol, 5)
        if data:
            print(f"   📊 Bids: {len(data['bids'])}, Asks: {len(data['asks'])}")
            print(f"   💰 Best bid: ${data['bids'][0]['price']:.2f}")
            print(f"   💰 Best ask: ${data['asks'][0]['price']:.2f}")
            return True
        return False
    
    results['orderbook'] = test_endpoint("🧱 Order Book", test_orderbook)
    
    # 4. 📈 Trades - /market/trades
    def test_trades():
        data = okx.get_trades_data(test_symbol, 5)
        if data:
            print(f"   📊 Retrieved {len(data)} recent trades")
            print(f"   💰 Latest trade: ${data[0]['price']:.2f} ({data[0]['side']})")
            return True
        return False
    
    results['trades'] = test_endpoint("📈 Trades", test_trades)
    
    # 5. 💹 Index Price - /market/index-tickers
    def test_index_price():
        data = okx.get_index_tickers(test_symbol)
        if data:
            print(f"   💰 Index price: ${data['index_price']:.2f}")
            print(f"   📈 24h change: {data['change_percent_24h']:.2f}%")
            return True
        return False
    
    results['index_price'] = test_endpoint("💹 Index Price", test_index_price)
    
    # 6. 📦 Open Interest - /public/open-interest
    def test_open_interest():
        data = okx.get_open_interest_data(test_symbol)
        if data:
            print(f"   📊 Open Interest: {data['open_interest']:,.2f}")
            print(f"   💰 OI Currency: {data['open_interest_currency']:,.2f}")
            return True
        return False
    
    results['open_interest'] = test_endpoint("📦 Open Interest", test_open_interest)
    
    # 7. 📊 Mark Price - /public/mark-price
    def test_mark_price():
        data = okx.get_mark_price(futures_symbol)
        if data:
            print(f"   💰 Mark price: ${data['mark_price']:.2f}")
            return True
        return False
    
    results['mark_price'] = test_endpoint("📊 Mark Price", test_mark_price)
    
    # 8. 🔀 Funding Rate - /public/funding-rate
    def test_funding_rate():
        data = okx.get_funding_rate(futures_symbol)
        if data:
            print(f"   💰 Funding rate: {data['funding_rate']:.6f}")
            print(f"   ⏰ Next funding: {data['next_funding_datetime']}")
            return True
        return False
    
    results['funding_rate'] = test_endpoint("🔀 Funding Rate", test_funding_rate)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY HASIL TESTING")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    status_symbols = {
        'candlestick': '📊',
        'ticker': '🔁', 
        'orderbook': '🧱',
        'trades': '📈',
        'index_price': '💹',
        'open_interest': '📦',
        'mark_price': '📊',
        'funding_rate': '🔀'
    }
    
    endpoint_names = {
        'candlestick': 'Candlestick (OHLCV)',
        'ticker': 'Ticker',
        'orderbook': 'Order Book',
        'trades': 'Trades',
        'index_price': 'Index Price',
        'open_interest': 'Open Interest',
        'mark_price': 'Mark Price',
        'funding_rate': 'Funding Rate'
    }
    
    for endpoint, result in results.items():
        status = "✅ BERFUNGSI" if result else "❌ GAGAL"
        symbol = status_symbols.get(endpoint, '📊')
        name = endpoint_names.get(endpoint, endpoint)
        print(f"{symbol} {name:<20} - {status}")
    
    print(f"\n🎯 Total: {passed_tests}/{total_tests} endpoint berhasil")
    
    if passed_tests == total_tests:
        print("🎉 SEMUA ENDPOINT BERFUNGSI DENGAN BAIK!")
    else:
        print(f"⚠️  {total_tests - passed_tests} endpoint perlu diperbaiki")
    
    print("="*60)

if __name__ == "__main__":
    main()