from core.okx_fetcher import get_candlesticks
from core.analyzer import SMAnalyzer
from core.signal_generator import SignalGenerator
import logging

logging.basicConfig(level=logging.INFO)

print("Testing signal generation with real OKX data...")

# Get data
df = get_candlesticks('BTC-USDT', '1H', 100)
print(f"Data fetched: {len(df)} candles")

# Analyze structure
analyzer = SMAnalyzer()
structure = analyzer.detect_structure(df)
print(f"Structure analysis complete")

# Generate signals
generator = SignalGenerator()
signals = generator.generate_signals_from_structure(structure, df, 'BTC-USDT', '1H')

print(f"\nTotal signals generated: {len(signals)}")

for i, signal in enumerate(signals):
    print(f"\n{'='*50}")
    print(f"SIGNAL #{i+1}: {signal.signal_type} {signal.symbol}")
    print(f"{'='*50}")
    print(f"Pattern Type: {signal.pattern_type}")
    print(f"Entry Price: ${signal.entry_price:,.2f}")
    print(f"Stop Loss: ${signal.stop_loss:,.2f}")
    print(f"Take Profit 1: ${signal.take_profit_1:,.2f}")
    print(f"Take Profit 2: ${signal.take_profit_2:,.2f}")
    print(f"Take Profit 3: ${signal.take_profit_3:,.2f}")
    print(f"Risk/Reward Ratio: 1:{signal.risk_reward_ratio}")
    print(f"Position Size: {signal.position_size_percentage}% of capital")
    print(f"Confidence: {signal.confidence:.0%}")
    print(f"Timeframe: {signal.timeframe}")
    print(f"Reason: {signal.reason}")
    print(f"Invalidation Level: ${signal.invalidation_level:,.2f}")

if not signals:
    print("\nNo trading signals generated. Market conditions may not meet criteria.")