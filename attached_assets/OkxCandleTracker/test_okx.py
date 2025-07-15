from okx_service import get_candlesticks

if __name__ == "__main__":
    result = get_candlesticks(instId="BTC-USDT", bar="1h", limit=10)
    print(result)