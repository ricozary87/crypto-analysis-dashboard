"""
Test Enhanced Technical Analyzer
Demonstrates OBV, Volume Profile, and caching optimization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import TechnicalAnalyzer
from core.okx_fetcher import OKXAPIManager
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_technical_analyzer():
    """Test the enhanced Technical Analyzer"""
    print("=" * 80)
    print("Testing Enhanced Technical Analyzer with OBV and Volume Profile")
    print("=" * 80)
    
    # Initialize components
    analyzer = TechnicalAnalyzer(cache_ttl_minutes=5)  # 5 minute cache
    api = OKXAPIManager()
    
    # Test different timeframes to demonstrate caching benefit
    timeframes = ['15m', '1H', '4H']
    symbol = 'BTC-USDT'
    
    for timeframe in timeframes:
        print(f"\n{'='*60}")
        print(f"Analyzing {symbol} on {timeframe} timeframe")
        print(f"{'='*60}")
        
        # Fetch data
        df = api.get_candles(symbol, timeframe, limit=200)
        if df is None or df.empty:
            print(f"Failed to fetch data for {timeframe}")
            continue
        
        # First analysis (cache miss)
        start_time = time.time()
        indicators1 = analyzer.analyze(df, symbol, timeframe)
        time1 = time.time() - start_time
        
        # Second analysis (cache hit)
        start_time = time.time()
        indicators2 = analyzer.analyze(df, symbol, timeframe)
        time2 = time.time() - start_time
        
        print(f"\n⏱️  Performance Comparison:")
        print(f"   First run (cache miss): {time1:.3f} seconds")
        print(f"   Second run (cache hit): {time2:.3f} seconds")
        print(f"   Speed improvement: {time1/time2:.1f}x faster")
        print(f"   Cache hit rate: {analyzer.get_cache_hit_rate():.1%}")
        
        # Display indicator summary
        summary = analyzer.get_indicator_summary(indicators1)
        
        print(f"\n📊 Technical Indicators Summary:")
        print(f"\n1. Trend Analysis:")
        print(f"   EMA Alignment: {summary['trend']['ema_alignment']}")
        print(f"   ADX: {summary['trend']['adx']} ({summary['trend']['trend_strength']} trend)")
        
        print(f"\n2. Momentum Indicators:")
        print(f"   RSI: {summary['momentum']['rsi']}")
        print(f"   MACD Signal: {summary['momentum']['macd_signal']}")
        print(f"   Stochastic: {summary['momentum']['stochastic']}")
        
        print(f"\n3. Volatility:")
        print(f"   ATR: ${summary['volatility']['atr']}")
        print(f"   BB Width: ${summary['volatility']['bb_width']}")
        print(f"   BB Position: {summary['volatility']['bb_position']}")
        
        print(f"\n4. Volume Analysis:")
        print(f"   OBV Trend: {summary['volume']['obv_trend']}")
        print(f"   Volume Ratio: {summary['volume']['volume_ratio']}")
        print(f"   VWAP Position: {summary['volume']['vwap_position']}")
        
        print(f"\n5. Volume Profile:")
        print(f"   POC (Point of Control): ${summary['volume_profile']['poc']:,.2f}")
        print(f"   Value Area High: ${summary['volume_profile']['value_area_high']:,.2f}")
        print(f"   Value Area Low: ${summary['volume_profile']['value_area_low']:,.2f}")
        
        print(f"\n6. Key Levels:")
        print(f"   Support: {[f'${s:,.2f}' for s in summary['levels']['support']]}")
        print(f"   Resistance: {[f'${r:,.2f}' for r in summary['levels']['resistance']]}")
        
        # Visualize OBV and Volume Profile
        if timeframe == '1H':  # Only visualize for 1H to save time
            visualize_obv_and_volume_profile(df, indicators1, symbol, timeframe)
    
    # Test cache performance with repeated calls
    print(f"\n{'='*60}")
    print("Cache Performance Test")
    print(f"{'='*60}")
    
    # Clear cache and test
    analyzer.clear_cache()
    print("\nCache cleared. Testing performance with 10 repeated analyses...")
    
    df = api.get_candles('BTC-USDT', '1H', limit=100)
    times = []
    
    for i in range(10):
        start = time.time()
        _ = analyzer.analyze(df, 'BTC-USDT', '1H')
        times.append(time.time() - start)
    
    print(f"\nExecution times:")
    for i, t in enumerate(times):
        cache_status = "MISS" if i == 0 else "HIT"
        print(f"   Run {i+1}: {t:.3f}s (Cache {cache_status})")
    
    print(f"\nAverage time (cache hits): {sum(times[1:])/len(times[1:]):.3f}s")
    print(f"Speed improvement: {times[0]/sum(times[1:])*len(times[1:]):.1f}x")
    print(f"Final cache hit rate: {analyzer.get_cache_hit_rate():.1%}")

def visualize_obv_and_volume_profile(df, indicators, symbol, timeframe):
    """Create visualization for OBV and Volume Profile"""
    print(f"\n📈 Creating visualization for OBV and Volume Profile...")
    
    # Set dark theme
    plt.style.use('dark_background')
    
    # Create subplots
    fig = plt.figure(figsize=(15, 10))
    
    # Price and OBV subplot
    ax1 = plt.subplot(3, 1, 1)
    ax2 = ax1.twinx()
    
    # Plot price
    ax1.plot(df.index[-100:], df['close'].iloc[-100:], 'cyan', linewidth=2, label='Price')
    ax1.fill_between(df.index[-100:], df['low'].iloc[-100:], df['high'].iloc[-100:], 
                     alpha=0.1, color='cyan')
    ax1.set_ylabel('Price ($)', color='cyan')
    ax1.tick_params(axis='y', labelcolor='cyan')
    ax1.set_title(f'{symbol} {timeframe} - Price and OBV Analysis', fontsize=14, pad=20)
    ax1.grid(True, alpha=0.3)
    
    # Plot OBV
    ax2.plot(df.index[-100:], indicators.obv.iloc[-100:], 'yellow', linewidth=2, label='OBV')
    ax2.set_ylabel('OBV', color='yellow')
    ax2.tick_params(axis='y', labelcolor='yellow')
    
    # Format x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Volume subplot
    ax3 = plt.subplot(3, 1, 2)
    colors = ['green' if df['close'].iloc[i] > df['close'].iloc[i-1] else 'red' 
              for i in range(len(df)-100, len(df))]
    ax3.bar(df.index[-100:], df['volume'].iloc[-100:], color=colors, alpha=0.5)
    ax3.plot(df.index[-100:], indicators.volume_ma.iloc[-100:], 'yellow', 
             linewidth=2, label='Volume MA(20)')
    ax3.set_ylabel('Volume')
    ax3.set_title('Volume Analysis', fontsize=12)
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    # Format x-axis
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax3.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    
    # Volume Profile subplot
    ax4 = plt.subplot(3, 1, 3)
    
    # Get volume profile data
    vp = indicators.volume_profile
    price_levels = vp['price_levels']
    volumes = vp['volumes']
    
    # Create horizontal bar chart for volume profile
    ax4.barh(price_levels, volumes, height=(max(price_levels)-min(price_levels))/len(price_levels)*0.8,
             color='skyblue', alpha=0.6, label='Volume Profile')
    
    # Mark POC, Value Area
    ax4.axhline(indicators.poc, color='red', linestyle='--', linewidth=2, label=f'POC: ${indicators.poc:,.2f}')
    ax4.axhline(indicators.value_area_high, color='green', linestyle='--', linewidth=1, 
                label=f'VA High: ${indicators.value_area_high:,.2f}')
    ax4.axhline(indicators.value_area_low, color='green', linestyle='--', linewidth=1, 
                label=f'VA Low: ${indicators.value_area_low:,.2f}')
    
    # Add current price
    current_price = df['close'].iloc[-1]
    ax4.axhline(current_price, color='yellow', linestyle='-', linewidth=2, 
                label=f'Current: ${current_price:,.2f}')
    
    ax4.set_xlabel('Volume')
    ax4.set_ylabel('Price Level ($)')
    ax4.set_title('Volume Profile Analysis', fontsize=12)
    ax4.legend(loc='upper right')
    ax4.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    # Save chart
    filename = f'analyzer_obv_volume_profile_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(filename, dpi=100, bbox_inches='tight', facecolor='black')
    print(f"✅ Chart saved as: {filename}")
    
    plt.close()

if __name__ == "__main__":
    test_technical_analyzer()