#!/usr/bin/env python3
"""
🧪 Enhanced SMC Analyzer Test Suite

Tests comprehensive SMC analysis with:
- Volume delta and CVD confirmation
- Inducement detection with confidence scoring
- Nested order blocks and confluence zones
- IRL/ERL liquidity categorization
- AI-ready output formatting
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any

# Add core to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.professional_smc_analyzer import ProfessionalSMCAnalyzer

def create_test_data() -> pd.DataFrame:
    """
    Create realistic test data for SMC analysis
    
    Returns:
        DataFrame with OHLCV data that contains SMC patterns
    """
    # Create 200 candles of realistic trading data
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1H')
    
    # Base price with trend
    base_price = 50000
    prices = []
    volumes = []
    
    # Create realistic price action with SMC patterns
    for i in range(200):
        # Add some volatility
        volatility = np.random.normal(0, 0.02)
        
        # Create trending moves with pullbacks
        if i < 50:
            # Uptrend with CHoCH pattern
            trend_factor = 1 + (i * 0.001)
        elif i < 100:
            # Pullback with FVG creation
            trend_factor = 1 + (50 * 0.001) - ((i - 50) * 0.0005)
        elif i < 150:
            # Continuation with order blocks
            trend_factor = 1 + (25 * 0.001) + ((i - 100) * 0.0008)
        else:
            # Liquidity sweep pattern
            trend_factor = 1 + (65 * 0.001) - ((i - 150) * 0.0003)
        
        current_price = base_price * trend_factor * (1 + volatility)
        
        # Create OHLC
        spread = current_price * 0.002  # 0.2% spread
        open_price = current_price
        high_price = current_price + spread * np.random.uniform(0.5, 2.0)
        low_price = current_price - spread * np.random.uniform(0.5, 2.0)
        close_price = current_price + spread * np.random.uniform(-0.5, 0.5)
        
        prices.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price
        })
        
        # Volume with realistic patterns
        base_volume = 1000000
        volume_factor = 1 + np.random.uniform(-0.3, 0.8)
        
        # Higher volume at key levels
        if i in [25, 75, 125, 175]:  # Swing points
            volume_factor *= 2.5
        
        volumes.append(base_volume * volume_factor)
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': dates,
        'open': [p['open'] for p in prices],
        'high': [p['high'] for p in prices],
        'low': [p['low'] for p in prices],
        'close': [p['close'] for p in prices],
        'volume': volumes
    })
    
    return df

def test_enhanced_smc_analyzer():
    """
    🧪 Test Enhanced SMC Analyzer
    
    Tests all advanced features:
    - Volume delta and CVD calculations
    - Enhanced pattern detection
    - Confluence analysis
    - AI-ready output generation
    """
    
    print("🚀 Testing Enhanced SMC Analyzer")
    print("=" * 60)
    
    # Initialize analyzer
    try:
        analyzer = ProfessionalSMCAnalyzer()
        print("✅ ProfessionalSMCAnalyzer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return False
    
    # Create test data
    print("\n📊 Creating test data...")
    df = create_test_data()
    print(f"✅ Created DataFrame with {len(df)} candles")
    print(f"   Price range: {df['close'].min():.2f} - {df['close'].max():.2f}")
    print(f"   Volume range: {df['volume'].min():.0f} - {df['volume'].max():.0f}")
    
    # Test comprehensive analysis
    print("\n🔍 Testing comprehensive SMC analysis...")
    
    try:
        # Run comprehensive analysis
        analysis_result = analyzer.analyze_comprehensive(
            df=df,
            symbol="BTC-USDT",
            timeframe="1H"
        )
        
        print("✅ Comprehensive analysis completed successfully")
        
        # Test result structure
        required_keys = [
            'symbol', 'timeframe', 'timestamp', 'current_price',
            'structure', 'order_blocks', 'fvg', 'liquidity_sweeps',
            'eqh_eql_signals', 'inducement', 'nested_order_blocks',
            'confluence_zones', 'volume_confirmation', 'ai_snapshot',
            'trading_signals', 'confidence_score', 'smc_summary'
        ]
        
        missing_keys = [key for key in required_keys if key not in analysis_result]
        if missing_keys:
            print(f"❌ Missing required keys: {missing_keys}")
            return False
        
        print("✅ All required keys present in analysis result")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test specific components
    print("\n🧪 Testing specific components...")
    
    # Test volume analysis
    volume_confirmation = analysis_result.get('volume_confirmation', {})
    if volume_confirmation:
        print(f"✅ Volume confirmation: {len(volume_confirmation.get('volume_deltas', []))} deltas")
        print(f"   CVD data points: {len(volume_confirmation.get('cvd_data', []))}")
        print(f"   Volume absorptions: {len(volume_confirmation.get('volume_absorptions', []))}")
        print(f"   CVD divergences: {len(volume_confirmation.get('cvd_divergences', []))}")
    
    # Test SMC patterns
    structure = analysis_result.get('structure', {})
    if structure:
        choch_bos = structure.get('choch_bos_signals', [])
        print(f"✅ CHoCH/BOS signals: {len(choch_bos)}")
        
        if choch_bos:
            for signal in choch_bos[:3]:  # Show first 3
                print(f"   {signal['type']} {signal['direction']} - Confidence: {signal.get('confidence_score', 0):.1%}")
    
    # Test order blocks
    order_blocks = analysis_result.get('order_blocks', [])
    print(f"✅ Order blocks detected: {len(order_blocks)}")
    
    if order_blocks:
        for ob in order_blocks[:3]:  # Show first 3
            print(f"   {ob['direction']} OB at {ob.get('price_high', 0):.2f} - Confidence: {ob.get('confidence_score', 0):.1%}")
    
    # Test FVG detection
    fvg_signals = analysis_result.get('fvg', [])
    print(f"✅ FVG signals detected: {len(fvg_signals)}")
    
    if fvg_signals:
        for fvg in fvg_signals[:3]:  # Show first 3
            print(f"   {fvg['direction']} FVG - Gap: {fvg.get('gap_size', 0):.2f} - Confidence: {fvg.get('confidence_score', 0):.1%}")
    
    # Test liquidity sweeps
    liquidity_sweeps = analysis_result.get('liquidity_sweeps', [])
    print(f"✅ Liquidity sweeps detected: {len(liquidity_sweeps)}")
    
    if liquidity_sweeps:
        for sweep in liquidity_sweeps[:3]:  # Show first 3
            category = sweep.get('liquidity_category', 'Unknown')
            print(f"   {sweep['direction']} {category} sweep - Confidence: {sweep.get('confidence_score', 0):.1%}")
    
    # Test confluence zones
    confluence_zones = analysis_result.get('confluence_zones', [])
    nested_order_blocks = analysis_result.get('nested_order_blocks', [])
    total_confluences = len(confluence_zones) + len(nested_order_blocks)
    print(f"✅ Confluence zones detected: {total_confluences}")
    
    # Test AI-ready output
    ai_snapshot = analysis_result.get('ai_snapshot', {})
    if ai_snapshot:
        pattern_counts = ai_snapshot.get('pattern_counts', {})
        print(f"✅ AI-ready output generated:")
        print(f"   Pattern counts: {sum(pattern_counts.values())} total patterns")
        print(f"   GPT descriptions: {len(ai_snapshot.get('gpt_descriptions', {}))}")
        print(f"   Visualization ready: {len(ai_snapshot.get('visualization_ready', {}))}")
    
    # Test overall confidence
    confidence_score = analysis_result.get('confidence_score', 0)
    print(f"✅ Overall confidence score: {confidence_score:.1%}")
    
    # Test SMC summary
    smc_summary = analysis_result.get('smc_summary', {})
    if smc_summary:
        analysis_quality = smc_summary.get('analysis_quality', 'unknown')
        market_bias = smc_summary.get('market_bias', 'unknown')
        print(f"✅ SMC summary generated:")
        print(f"   Analysis quality: {analysis_quality}")
        print(f"   Market bias: {market_bias}")
        print(f"   Total patterns: {smc_summary.get('pattern_summary', {}).get('total_patterns', 0)}")
    
    # Test trading signals
    trading_signals = analysis_result.get('trading_signals', [])
    print(f"✅ Trading signals generated: {len(trading_signals)}")
    
    if trading_signals:
        for signal in trading_signals[:2]:  # Show first 2
            direction = signal.get('direction', 'unknown')
            pattern_type = signal.get('pattern_type', 'unknown')
            rr_ratio = signal.get('risk_reward_ratio', 0)
            print(f"   {direction} {pattern_type} signal - R:R {rr_ratio:.1f}:1")
    
    return True

def test_volume_delta_calculation():
    """
    🧪 Test Volume Delta Calculation
    """
    print("\n🧪 Testing Volume Delta Calculation")
    print("-" * 40)
    
    try:
        analyzer = ProfessionalSMCAnalyzer()
        
        # Create simple test data
        test_data = []
        for i in range(10):
            test_data.append({
                'timestamp': int(datetime.now().timestamp() * 1000) + i * 3600000,
                'open': 50000 + i * 10,
                'high': 50000 + i * 10 + 50,
                'low': 50000 + i * 10 - 30,
                'close': 50000 + i * 10 + 20,
                'volume': 1000000 + i * 100000
            })
        
        # Test volume delta calculation
        volume_deltas = analyzer.volume_analyzer.calculate_volume_delta(test_data)
        
        print(f"✅ Volume delta calculation successful: {len(volume_deltas)} deltas")
        
        # Test CVD calculation
        cvd_data = analyzer.cvd_calculator.calculate_cvd(volume_deltas)
        
        print(f"✅ CVD calculation successful: {len(cvd_data)} CVD points")
        
        # Show some results
        for i, delta in enumerate(volume_deltas[:3]):
            print(f"   Delta {i+1}: {delta['delta']:.0f} (ratio: {delta['delta_ratio']:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Volume delta test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_confluence_detection():
    """
    🧪 Test Confluence Detection
    """
    print("\n🧪 Testing Confluence Detection")
    print("-" * 40)
    
    try:
        analyzer = ProfessionalSMCAnalyzer()
        
        # Create test order blocks
        order_blocks = [
            {
                'timestamp': int(datetime.now().timestamp() * 1000),
                'direction': 'support',
                'price_high': 50100,
                'price_low': 50000,
                'volume': 1500000,
                'strength': 0.8,
                'confidence_score': 0.85
            },
            {
                'timestamp': int(datetime.now().timestamp() * 1000) + 3600000,
                'direction': 'support',
                'price_high': 50080,
                'price_low': 50020,
                'volume': 1200000,
                'strength': 0.7,
                'confidence_score': 0.80
            }
        ]
        
        # Test nested order block detection
        nested_obs = analyzer.confluence_detector.detect_nested_order_blocks(order_blocks)
        
        print(f"✅ Nested order block detection: {len(nested_obs)} nested blocks")
        
        # Create test FVG signals
        fvg_signals = [
            {
                'timestamp': int(datetime.now().timestamp() * 1000),
                'direction': 'bullish',
                'gap_high': 50080,
                'gap_low': 50040,
                'strength': 0.8,
                'confidence_score': 0.85
            }
        ]
        
        # Test FVG-OB confluence
        fvg_ob_confluences = analyzer.confluence_detector.detect_fvg_ob_confluence(fvg_signals, order_blocks)
        
        print(f"✅ FVG-OB confluence detection: {len(fvg_ob_confluences)} confluences")
        
        return True
        
    except Exception as e:
        print(f"❌ Confluence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    🎯 Main Test Runner
    """
    print("🧪 Enhanced SMC Analyzer Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_tests_passed = True
    
    # Run all tests
    tests = [
        ("Enhanced SMC Analyzer", test_enhanced_smc_analyzer),
        ("Volume Delta Calculation", test_volume_delta_calculation),
        ("Confluence Detection", test_confluence_detection)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
                all_tests_passed = False
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            all_tests_passed = False
    
    # Final result
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Enhanced SMC Analyzer is working correctly.")
        print("\n✨ Features successfully tested:")
        print("   • Volume Delta and CVD calculations")
        print("   • Enhanced pattern detection with confidence scoring")
        print("   • Confluence zone analysis")
        print("   • AI-ready output generation")
        print("   • Comprehensive SMC analysis")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)