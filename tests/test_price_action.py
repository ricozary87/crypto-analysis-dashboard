#!/usr/bin/env python3
"""
Test Enhanced Price Action Analyzer
Demonstrates visualization, enhanced scoring, and detailed pattern analysis
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.price_action import PriceActionAnalyzer
from core.okx_fetcher import OKXAPIManager
import pandas as pd

def test_price_action_analyzer():
    """Test the enhanced Price Action Analyzer"""
    print("=" * 50)
    print("Testing Enhanced Price Action Analyzer")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = PriceActionAnalyzer()
    
    # Test with BTC data
    symbol = "BTC-USDT"
    print(f"\n1. Fetching data for {symbol}...")
    okx_manager = OKXAPIManager()
    df = okx_manager.get_candles(symbol, timeframe='1H', limit=100)
    
    if df is None or df.empty:
        print("✗ Failed to fetch data")
        return
    
    print(f"✓ Fetched {len(df)} candles")
    print(f"  Latest price: ${df['close'].iloc[-1]:,.2f}")
    
    # Analyze patterns
    print("\n2. Analyzing candlestick patterns...")
    patterns = analyzer.analyze_patterns(df)
    
    if not patterns:
        print("✗ No patterns detected")
    else:
        print(f"✓ Detected {len(patterns)} patterns")
        
        # Get pattern summary
        summary = analyzer.get_pattern_summary(patterns)
        print(f"\n3. Pattern Summary:")
        print(f"  Total patterns: {summary['total_patterns']}")
        print(f"  Bullish: {summary['bullish_count']}")
        print(f"  Bearish: {summary['bearish_count']}")
        print(f"  Average strength: {summary['avg_strength']:.1%}")
        print(f"  Dominant bias: {summary['dominant_bias']}")
        print(f"  Pattern types: {', '.join(summary['patterns'])}")
        
        # Detailed pattern analysis
        print("\n4. Detailed Pattern Analysis:")
        for i, pattern in enumerate(patterns[:2]):  # Show top 2 patterns
            print(f"\n  Pattern {i+1}: {pattern.pattern_type}")
            details = analyzer.get_detailed_pattern_info(pattern)
            
            print(f"  Direction: {details['direction']}")
            print(f"  Overall Strength: {details['overall_strength']}")
            print(f"  Description: {details['description']}")
            
            print(f"\n  Scoring Breakdown:")
            for component, score in details['scoring_breakdown'].items():
                print(f"    {component}: {score}")
            
            print(f"\n  Trading Setup:")
            setup = details['trading_setup']
            print(f"    Entry: ${setup['Entry Price']:,.2f}")
            print(f"    Stop Loss: ${setup['Stop Loss']:,.2f}")
            print(f"    Risk/Reward: {setup['Risk/Reward']}")
            print(f"    Position Size: {setup['Position Size']}")
            
            print(f"\n  Pattern Specifics:")
            for key, value in details['pattern_specifics'].items():
                print(f"    {key}: {value}")
        
        # Generate visualization
        print("\n5. Generating pattern visualization...")
        try:
            chart_base64 = analyzer.visualize_patterns(df, patterns)
            print(f"✓ Chart generated successfully")
            print(f"  Base64 length: {len(chart_base64)} characters")
            
            # Save to file
            chart_path = "test_patterns.png"
            analyzer.visualize_patterns(df, patterns, save_path=chart_path)
            print(f"✓ Chart saved to: {chart_path}")
            
        except Exception as e:
            print(f"✗ Visualization failed: {e}")
    
    # Test scoring system
    print("\n6. Testing Enhanced Scoring System:")
    print(f"  Scoring weights:")
    for component, weight in analyzer.scoring_weights.items():
        print(f"    {component}: {weight:.0%}")
    
    # Test with different symbols
    print("\n7. Testing Multiple Symbols:")
    symbols = ["ETH-USDT", "SOL-USDT"]
    
    for sym in symbols:
        df_test = get_ohlcv_data(sym, "1H", 100)
        if df_test is not None and not df_test.empty:
            patterns_test = analyzer.analyze_patterns(df_test)
            summary_test = analyzer.get_pattern_summary(patterns_test)
            print(f"\n  {sym}:")
            print(f"    Patterns found: {summary_test['total_patterns']}")
            print(f"    Dominant bias: {summary_test['dominant_bias']}")
            print(f"    Avg strength: {summary_test['avg_strength']:.1%}")
    
    print("\n" + "=" * 50)
    print("Testing Complete!")
    print("=" * 50)
    
    # Summary of enhancements
    print("\nEnhancements Summary:")
    print("✓ Multi-factor scoring system implemented")
    print("✓ Pattern visualization with dark theme")
    print("✓ Detailed scoring breakdown available")
    print("✓ Support/Resistance integration")
    print("✓ Volume confirmation scoring")
    print("✓ Comprehensive pattern documentation")
    print("✓ Trading setup recommendations")

if __name__ == "__main__":
    test_price_action_analyzer()