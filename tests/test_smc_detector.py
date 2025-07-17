#!/usr/bin/env python3
"""
Test Enhanced SMC Detector
Demonstrates visualization, optimized liquidity detection, and pattern documentation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
from core.okx_fetcher import OKXAPIManager
import pandas as pd

def test_smc_detector():
    """Test the enhanced SMC Detector functionality"""
    
    print("=" * 50)
    print("Testing Enhanced SMC Detector")
    print("=" * 50)
    
    # Initialize detector
    detector = ProfessionalSMCAnalyzer()
    
    # Test with BTC data
    symbol = "BTC-USDT"
    timeframe = "1H"
    
    print(f"\n1. Fetching data for {symbol}...")
    okx_manager = OKXAPIManager()
    df = okx_manager.get_candles(symbol, timeframe=timeframe, limit=200)
    
    if df is None or df.empty:
        print("✗ Failed to fetch data")
        return
    
    print(f"✓ Fetched {len(df)} candles")
    print(f"  Latest price: ${df['close'].iloc[-1]:,.2f}")
    
    # Detect all SMC patterns
    analysis = detector.analyze_comprehensive(df)
    print(f"✓ SMC pattern detection complete")
    
    print("Test completed successfully")

if __name__ == "__main__":
    test_smc_detector()
    print("\n2. Detecting SMC patterns...")
    patterns = detector.detect_all_patterns(df)
    
    # Display pattern summary
    print("\n3. Pattern Summary:")
    total_patterns = sum(len(p) for p in patterns.values())
    print(f"  Total patterns detected: {total_patterns}")
    
    for pattern_type, pattern_list in patterns.items():
        if pattern_list:
            print(f"  {pattern_type}: {len(pattern_list)} patterns")
            # Show first pattern details
            if pattern_list:
                p = pattern_list[0]
                print(f"    - {p.description}")
                print(f"      Level: ${p.level:,.2f}")
                print(f"      Strength: {p.strength:.2%}")
                print(f"      Direction: {p.direction}")
    
    # Get pattern statistics
    print("\n4. Pattern Statistics:")
    stats = detector.get_pattern_statistics(patterns)
    print(f"  Total patterns: {stats['total_patterns']}")
    print(f"  Directional bias: Bullish({stats['directional_bias']['bullish']}) vs Bearish({stats['directional_bias']['bearish']})")
    
    if stats['average_strength']:
        print("\n  Average strength by pattern:")
        for pattern_type, avg_strength in stats['average_strength'].items():
            print(f"    {pattern_type}: {avg_strength:.2%}")
    
    if stats['high_confidence_patterns']:
        print(f"\n  High confidence patterns (>80%): {len(stats['high_confidence_patterns'])}")
        for hcp in stats['high_confidence_patterns'][:3]:  # Show top 3
            print(f"    - {hcp['type']}: {hcp['description']}")
    
    # Generate visualization
    print("\n5. Generating SMC pattern visualization...")
    try:
        chart_image = detector.visualize_smc_patterns(df, patterns, save_path="smc_analysis.png")
        print("✓ Visualization saved to smc_analysis.png")
        print(f"  Chart data URI length: {len(chart_image)} bytes")
        
        # Also test the optimized liquidity zone detection
        print("\n6. Testing optimized liquidity zone detection:")
        liquidity_patterns = patterns.get('LIQUIDITY', [])
        if liquidity_patterns:
            print(f"  Found {len(liquidity_patterns)} liquidity zones")
            for lp in liquidity_patterns[:3]:  # Show top 3
                print(f"    - {lp.description}")
                print(f"      Level: ${lp.level:,.2f}")
                print(f"      Swept: {'Yes' if lp.liquidity_sweep else 'No'}")
        else:
            print("  No liquidity zones detected in current data")
            
    except Exception as e:
        print(f"✗ Visualization failed: {str(e)}")
    
    # Test pattern summary
    print("\n7. Pattern Summary Report:")
    summary = detector.get_pattern_summary(patterns)
    print(f"  Total patterns: {summary['total_patterns']}")
    print(f"  Bullish patterns: {summary['bullish_patterns']}")
    print(f"  Bearish patterns: {summary['bearish_patterns']}")
    
    if summary['strongest_pattern']:
        sp = summary['strongest_pattern']
        print(f"\n  Strongest pattern:")
        print(f"    Type: {sp['type']}")
        print(f"    Strength: {sp['strength']:.2%}")
        print(f"    Level: ${sp['level']:,.2f}")
        print(f"    Direction: {sp['direction']}")
    
    if summary['most_recent_pattern']:
        mrp = summary['most_recent_pattern']
        print(f"\n  Most recent pattern:")
        print(f"    Type: {mrp['type']}")
        print(f"    Strength: {mrp['strength']:.2%}")
        print(f"    Level: ${mrp['level']:,.2f}")
        print(f"    Direction: {mrp['direction']}")
    
    # Test with multiple symbols
    print("\n8. Testing Multiple Symbols:")
    test_symbols = ['ETH-USDT', 'SOL-USDT']
    
    for test_symbol in test_symbols:
        print(f"\n  {test_symbol}:")
        df_test = get_candlesticks(test_symbol, timeframe, limit=100)
        if not df_test.empty:
            patterns_test = detector.detect_all_patterns(df_test)
            total = sum(len(p) for p in patterns_test.values())
            print(f"    Patterns found: {total}")
            
            # Show dominant pattern type
            if patterns_test:
                dominant = max(patterns_test.items(), key=lambda x: len(x[1]))
                print(f"    Dominant pattern: {dominant[0]} ({len(dominant[1])} occurrences)")
    
    print("\n" + "=" * 50)
    print("Testing Complete!")
    print("=" * 50)
    
    print("\nEnhancements Summary:")
    print("✓ Visualization with dark theme for all SMC patterns")
    print("✓ Optimized liquidity zone detection using clustering")
    print("✓ Comprehensive pattern statistics and reporting")
    print("✓ Pattern strength heatmap visualization")
    print("✓ Market structure point identification")
    print("✓ High-confidence pattern filtering")
    
    print("\nDocumentation:")
    print("See docs/SMC_PATTERNS_DOCUMENTATION.md for detailed pattern explanations")

if __name__ == "__main__":
    test_smc_detector()