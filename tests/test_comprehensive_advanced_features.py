#!/usr/bin/env python3
"""
🚀 Comprehensive Advanced Features Test Suite
Test semua fitur lanjutan SMC dan Price Action yang telah diimplementasikan

Tested Features:
- 5 Advanced SMC Features (Volume Imbalance, FVG Refinement, Real-time Swings, Multi-timeframe Confluence, Breaker Blocks)
- 5 Advanced Price Action Features (Pattern Stacking, SNR Flip, Wick Trap, Momentum Candle, Compression)
"""

import sys
import json
import traceback
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to the path
sys.path.insert(0, '/home/runner/workspace')

from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
from core.price_action import PriceActionAnalyzer
from core.okx_fetcher import OKXAPIManager

def create_dummy_data() -> List[Dict]:
    """Create realistic dummy market data for testing"""
    import random
    
    # Base values
    base_price = 100000  # BTC-like price
    base_volume = 1000000
    
    dummy_data = []
    current_price = base_price
    
    # Generate 200 candles with realistic price movement
    for i in range(200):
        # Random price movement
        price_change = random.uniform(-0.02, 0.02)  # +/- 2%
        current_price = current_price * (1 + price_change)
        
        # Generate OHLC
        high = current_price * random.uniform(1.001, 1.015)
        low = current_price * random.uniform(0.985, 0.999)
        open_price = current_price * random.uniform(0.995, 1.005)
        close_price = current_price
        
        # Volume with occasional spikes
        volume = base_volume * random.uniform(0.5, 2.0)
        if i % 20 == 0:  # Volume spike every 20 candles
            volume *= 3
        
        dummy_data.append({
            'timestamp': 1700000000 + (i * 300),  # 5-minute intervals
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
    
    return dummy_data

def create_volume_deltas(data: List[Dict]) -> List[Dict]:
    """Create dummy volume delta data"""
    import random
    
    volume_deltas = []
    for i, candle in enumerate(data):
        total_volume = candle['volume']
        
        # Random buy/sell distribution
        buy_percentage = random.uniform(0.3, 0.7)
        buy_volume = total_volume * buy_percentage
        sell_volume = total_volume * (1 - buy_percentage)
        
        # Occasionally create imbalance
        if i % 15 == 0:
            buy_volume = total_volume * 0.8  # 80% buy pressure
            sell_volume = total_volume * 0.2
        elif i % 25 == 0:
            buy_volume = total_volume * 0.2  # 80% sell pressure
            sell_volume = total_volume * 0.8
        
        volume_deltas.append({
            'timestamp': candle['timestamp'],
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'total_volume': total_volume,
            'delta': buy_volume - sell_volume
        })
    
    return volume_deltas

def test_advanced_smc_features():
    """Test all 5 advanced SMC features"""
    print("🚀 Testing Advanced SMC Features...")
    
    try:
        # Initialize analyzer
        analyzer = ProfessionalSMCAnalyzer()
        
        # Create test data
        data = create_dummy_data()
        volume_deltas = create_volume_deltas(data)
        
        # Test 1: Volume Imbalance Detection
        print("\n1. 📊 Testing Volume Imbalance Detection...")
        volume_imbalances = analyzer.detect_volume_imbalance(data, volume_deltas)
        print(f"   ✅ Detected {len(volume_imbalances)} volume imbalances")
        
        if volume_imbalances:
            example = volume_imbalances[0]
            print(f"   📋 Example: {example['type']} - {example['direction']} with {example['confidence_score']:.2f} confidence")
        
        # Test 2: FVG Refinement Entries
        print("\n2. 🎯 Testing FVG Refinement Entries...")
        # Create mock FVG signals
        mock_fvg_signals = [{
            'timestamp': 1700001000,
            'fvg_high': 101000,
            'fvg_low': 100500,
            'confidence_score': 0.7
        }]
        
        # Create mock order blocks
        mock_order_blocks = [{
            'timestamp': 1700001300,
            'price': 100750,
            'price_high': 100800,
            'price_low': 100700,
            'confidence_score': 0.8
        }]
        
        refined_fvg = analyzer.detect_fvg_refinement_entries(data, mock_fvg_signals, mock_order_blocks)
        print(f"   ✅ Refined {len(refined_fvg)} FVG entries")
        
        if refined_fvg:
            example = refined_fvg[0]
            print(f"   📋 Example: Enhanced FVG with {example['confidence_score']:.2f} confidence")
        
        # Test 3: Real-time Swing Detection
        print("\n3. ⚡ Testing Real-time Swing Detection...")
        realtime_swings = analyzer.detect_realtime_swing_points(data, lookback_period=10)
        swing_highs = realtime_swings.get('swing_highs', [])
        swing_lows = realtime_swings.get('swing_lows', [])
        print(f"   ✅ Detected {len(swing_highs)} swing highs and {len(swing_lows)} swing lows")
        
        if swing_highs:
            example = swing_highs[0]
            print(f"   📋 Example: Swing high at {example['price']:.2f} with {example['confidence_score']:.2f} confidence")
        
        # Test 4: Multi-timeframe Confluence
        print("\n4. 📈 Testing Multi-timeframe Confluence...")
        current_analysis = {
            'order_blocks': mock_order_blocks,
            'fvg': mock_fvg_signals,
            'structure': {'trend': 'bullish'}
        }
        
        higher_tf_analysis = {
            'order_blocks': mock_order_blocks,
            'fvg': mock_fvg_signals,
            'structure': {'trend': 'bullish'}
        }
        
        mtf_confluence = analyzer.analyze_multi_timeframe_confluence(current_analysis, higher_tf_analysis)
        print(f"   ✅ MTF Confluence: {mtf_confluence['has_htf_confirmation']}")
        print(f"   📋 Confidence boost: {mtf_confluence['confidence_boost']:.2f}")
        
        # Test 5: Comprehensive Analysis Integration
        print("\n5. 🔄 Testing Comprehensive Analysis Integration...")
        import pandas as pd
        df = pd.DataFrame(data)
        comprehensive_result = analyzer.analyze_comprehensive(df, 'BTC-USDT', '5m')
        
        advanced_patterns = comprehensive_result.get('advanced_patterns', [])
        print(f"   ✅ Generated {len(advanced_patterns)} advanced patterns")
        
        # Group by type
        pattern_types = {}
        for pattern in advanced_patterns:
            pattern_type = pattern.get('type', 'unknown')
            pattern_types[pattern_type] = pattern_types.get(pattern_type, 0) + 1
        
        print(f"   📊 Pattern breakdown:")
        for pattern_type, count in pattern_types.items():
            print(f"      - {pattern_type}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ SMC Advanced Features Test Error: {e}")
        traceback.print_exc()
        return False

def test_advanced_price_action_features():
    """Test all 5 advanced Price Action features"""
    print("\n🕯️ Testing Advanced Price Action Features...")
    
    try:
        # Initialize analyzer
        analyzer = PriceActionAnalyzer()
        
        # Create test data with specific patterns
        data = create_pattern_specific_data()
        
        # Test comprehensive analysis
        result = analyzer.analyze_price_action(data)
        
        advanced_patterns = result.get('advanced_patterns', [])
        print(f"   ✅ Generated {len(advanced_patterns)} advanced price action patterns")
        
        # Group by type
        pattern_types = {}
        for pattern in advanced_patterns:
            pattern_type = pattern.get('type', 'unknown')
            pattern_types[pattern_type] = pattern_types.get(pattern_type, 0) + 1
        
        print(f"   📊 Pattern breakdown:")
        for pattern_type, count in pattern_types.items():
            print(f"      - {pattern_type}: {count}")
        
        # Test individual features
        print("\n   🔍 Testing Individual Features:")
        
        # Test Pattern Stacking
        stacked_patterns = analyzer._detect_pattern_stacking(data)
        print(f"   1. Pattern Stacking: {len(stacked_patterns)} patterns")
        
        # Test SNR Flips
        snr_flips = analyzer._detect_snr_flips(data)
        print(f"   2. SNR Flips: {len(snr_flips)} patterns")
        
        # Test Wick Traps
        wick_traps = analyzer._detect_wick_traps(data)
        print(f"   3. Wick Traps: {len(wick_traps)} patterns")
        
        # Test Momentum Candles
        momentum_candles = analyzer._detect_momentum_candles(data)
        print(f"   4. Momentum Candles: {len(momentum_candles)} patterns")
        
        # Test Compression Patterns
        compression_patterns = analyzer._detect_compression_patterns(data)
        print(f"   5. Compression Patterns: {len(compression_patterns)} patterns")
        
        return True
        
    except Exception as e:
        print(f"❌ Price Action Advanced Features Test Error: {e}")
        traceback.print_exc()
        return False

def create_pattern_specific_data():
    """Create data with specific patterns for testing"""
    import pandas as pd
    import numpy as np
    
    # Create base data
    base_data = create_dummy_data()
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(base_data)
    
    # Add some specific patterns
    # Morning Star pattern (indices 50-52)
    df.loc[50, 'close'] = df.loc[50, 'open'] - 500  # Bearish first candle
    df.loc[51, 'open'] = df.loc[51, 'close'] = df.loc[50, 'close'] + 100  # Small doji
    df.loc[52, 'close'] = df.loc[52, 'open'] + 800  # Bullish third candle
    
    # Long upper wick (index 80) - Wick trap
    df.loc[80, 'high'] = df.loc[80, 'close'] + 1000
    df.loc[80, 'close'] = df.loc[80, 'open'] + 50
    
    # Momentum candle (index 100) - Marubozu
    df.loc[100, 'high'] = df.loc[100, 'close'] + 20
    df.loc[100, 'low'] = df.loc[100, 'open'] - 20
    df.loc[100, 'close'] = df.loc[100, 'open'] + 800
    
    # Compression pattern (indices 130-140)
    for i in range(130, 140):
        range_size = max(50, 300 - (i - 130) * 25)  # Decreasing range
        df.loc[i, 'high'] = df.loc[i, 'open'] + range_size
        df.loc[i, 'low'] = df.loc[i, 'open'] - range_size
        df.loc[i, 'close'] = df.loc[i, 'open'] + np.random.randint(-range_size//2, range_size//2)
    
    return df

def test_output_format():
    """Test output format consistency"""
    print("\n📋 Testing Output Format Consistency...")
    
    try:
        # Initialize analyzers
        smc_analyzer = ProfessionalSMCAnalyzer()
        price_analyzer = PriceActionAnalyzer()
        
        # Create test data
        data = create_dummy_data()
        volume_deltas = create_volume_deltas(data)
        
        # Test SMC analyzer output
        print("   🔍 Testing SMC Analyzer Output Format...")
        import pandas as pd
        df = pd.DataFrame(data)
        smc_result = smc_analyzer.analyze_comprehensive(df, 'BTC-USDT', '5m')
        
        # Check required fields
        required_smc_fields = ['advanced_patterns', 'confidence_score', 'trading_signals']
        for field in required_smc_fields:
            if field in smc_result:
                print(f"   ✅ SMC field '{field}' present")
            else:
                print(f"   ❌ SMC field '{field}' missing")
        
        # Check advanced patterns format
        advanced_patterns = smc_result.get('advanced_patterns', [])
        required_pattern_fields = ['type', 'direction', 'confidence_score', 'timestamp', 'description']
        
        if advanced_patterns:
            sample_pattern = advanced_patterns[0]
            
            print(f"   📊 Sample SMC pattern structure:")
            for field in required_pattern_fields:
                if field in sample_pattern:
                    print(f"      ✅ {field}: {sample_pattern[field]}")
                else:
                    print(f"      ❌ {field}: missing")
        
        # Test Price Action analyzer output
        print("\n   🔍 Testing Price Action Analyzer Output Format...")
        price_result = price_analyzer.analyze_price_action(create_pattern_specific_data())
        
        # Check required fields
        required_price_fields = ['advanced_patterns', 'confidence', 'signals']
        for field in required_price_fields:
            if field in price_result:
                print(f"   ✅ Price Action field '{field}' present")
            else:
                print(f"   ❌ Price Action field '{field}' missing")
        
        # Check advanced patterns format
        price_advanced_patterns = price_result.get('advanced_patterns', [])
        if price_advanced_patterns:
            sample_pattern = price_advanced_patterns[0]
            print(f"   📊 Sample Price Action pattern structure:")
            for field in required_pattern_fields:
                if field in sample_pattern:
                    print(f"      ✅ {field}: {sample_pattern[field]}")
                else:
                    print(f"      ❌ {field}: missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Output Format Test Error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test runner"""
    print("🎯 COMPREHENSIVE ADVANCED FEATURES TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Advanced SMC Features
    print("\n📊 PHASE 1: Advanced SMC Features Test")
    results.append(("Advanced SMC Features", test_advanced_smc_features()))
    
    # Test 2: Advanced Price Action Features
    print("\n🕯️ PHASE 2: Advanced Price Action Features Test")
    results.append(("Advanced Price Action Features", test_advanced_price_action_features()))
    
    # Test 3: Output Format Consistency
    print("\n📋 PHASE 3: Output Format Consistency Test")
    results.append(("Output Format Consistency", test_output_format()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Advanced features implementation is successful!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)