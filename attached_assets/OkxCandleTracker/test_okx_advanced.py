from okx_service import get_candlesticks, OKXService
from technical_indicators import TechnicalIndicators
import json

def test_basic_candlesticks():
    """Test basic candlestick data fetching"""
    print("=== Testing Basic Candlestick Data ===")
    result = get_candlesticks(instId="BTC-USDT", bar="1h", limit=10)
    print(f"Retrieved {len(result)} candlesticks")
    
    if result:
        latest = result[-1]
        print(f"Latest candle: {latest['datetime']}")
        print(f"Price: Open={latest['open']}, High={latest['high']}, Low={latest['low']}, Close={latest['close']}")
        print(f"Volume: {latest['volume']}")
    print()

def test_multiple_symbols():
    """Test multiple cryptocurrency symbols"""
    print("=== Testing Multiple Symbols ===")
    symbols = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
    
    for symbol in symbols:
        result = get_candlesticks(instId=symbol, bar="1h", limit=5)
        if result:
            latest = result[-1]
            print(f"{symbol}: ${latest['close']:.2f} (Vol: {latest['volume']:.2f})")
    print()

def test_different_timeframes():
    """Test different timeframes"""
    print("=== Testing Different Timeframes ===")
    timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]
    
    for timeframe in timeframes:
        result = get_candlesticks(instId="BTC-USDT", bar=timeframe, limit=3)
        if result:
            print(f"{timeframe}: {len(result)} candles, latest close: ${result[-1]['close']:.2f}")
    print()

def test_technical_indicators():
    """Test technical indicators calculation"""
    print("=== Testing Technical Indicators ===")
    
    # Get data for indicators
    data = get_candlesticks(instId="BTC-USDT", bar="1h", limit=50)
    
    if data:
        tech_indicators = TechnicalIndicators()
        indicators = tech_indicators.calculate_all_indicators(data)
        
        print("Available indicators:")
        for indicator_name, indicator_data in indicators.items():
            if indicator_data:
                if indicator_name == 'volume_analysis':
                    print(f"- {indicator_name}: {indicator_data}")
                else:
                    print(f"- {indicator_name}: {len(indicator_data)} data points")
    print()

def test_full_service():
    """Test full OKX service capabilities"""
    print("=== Testing Full OKX Service ===")
    
    okx_service = OKXService()
    
    # Test candlestick data
    candlestick_data = okx_service.get_candlestick_data("BTC-USDT", "1h", 5)
    print(f"Candlestick data: {len(candlestick_data)} candles")
    
    # Test orderbook data
    orderbook_data = okx_service.get_orderbook_data("BTC-USDT", 5)
    if orderbook_data:
        print(f"Orderbook: {len(orderbook_data['bids'])} bids, {len(orderbook_data['asks'])} asks")
        print(f"Best bid: ${orderbook_data['bids'][0]['price']:.2f}")
        print(f"Best ask: ${orderbook_data['asks'][0]['price']:.2f}")
    
    # Test open interest data
    oi_data = okx_service.get_open_interest_data("BTC-USDT")
    if oi_data:
        print(f"Open Interest: {oi_data['open_interest']:,.2f}")
    
    # Test available symbols
    symbols = okx_service.get_available_symbols()
    print(f"Available symbols: {len(symbols)}")
    print()

if __name__ == "__main__":
    print("🚀 OKX API Testing Suite")
    print("=" * 50)
    
    test_basic_candlesticks()
    test_multiple_symbols()
    test_different_timeframes()
    test_technical_indicators()
    test_full_service()
    
    print("✅ All tests completed successfully!")