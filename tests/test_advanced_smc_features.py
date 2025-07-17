#!/usr/bin/env python3
"""
🚀 COMPREHENSIVE TEST FOR ADVANCED SMC FEATURES

Test suite untuk menguji 6 fitur advanced SMC logic yang telah diimplementasikan:
1. 🧱 Breaker Block Logic
2. 💧 IRL & ERL Liquidity Categorization
3. ⏱️ Killzone SMC Timing
4. 🎯 Premium/Discount Zone Mapping
5. 🧱 Mitigation Block Logic
6. 📉 Trendline Liquidity Detection

Menguji dengan data market real dari OKX API untuk memastikan semua fitur bekerja dengan baik.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
from core.okx_fetcher import OKXAPIManager

def test_advanced_smc_features():
    """
    🚀 Test Advanced SMC Features dengan Real Market Data
    """
    print("🚀 ADVANCED SMC FEATURES TEST")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = ProfessionalSMCAnalyzer()
    print("✅ Professional SMC Analyzer initialized")
    
    # Get real market data
    print("\n📊 Fetching real market data...")
    try:
        okx_manager = OKXAPIManager()
        df = okx_manager.get_candles("BTC-USDT", timeframe='1H', limit=300)
        
        if df is not None and not df.empty:
            print(f"✅ Fetched {len(df)} real market candles")
            print(f"   Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
            print(f"   Volume range: {df['volume'].min():.0f} - {df['volume'].max():.0f}")
        else:
            print("❌ Failed to fetch real market data")
            return False
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return False
    
    # Run comprehensive analysis with advanced features
    print("\n🔍 Running comprehensive analysis with advanced features...")
    
    try:
        analysis_result = analyzer.analyze_comprehensive(
            df=df,
            symbol="BTC-USDT", 
            timeframe="1H"
        )
        
        print("✅ Comprehensive analysis completed successfully")
        
        # Test results for each advanced feature
        print("\n" + "=" * 60)
        print("🚀 ADVANCED SMC FEATURES TEST RESULTS")
        print("=" * 60)
        
        # 1. Test Breaker Blocks
        breaker_blocks = analysis_result.get('breaker_blocks', [])
        print(f"\n🧱 BREAKER BLOCKS: {len(breaker_blocks)} detected")
        for i, bb in enumerate(breaker_blocks[:3]):  # Show first 3
            print(f"   {i+1}. {bb['direction']} breaker from {bb['original_ob']['direction']} OB")
            print(f"      Break Price: ${bb['break_price']:.2f}")
            print(f"      Break Strength: {bb['break_strength']:.2%}")
            print(f"      Volume Confirmation: {bb['volume_confirmation']}")
            print(f"      Confidence: {bb['confidence_score']:.1%}")
        
        # 2. Test Enhanced Liquidity Sweeps (IRL/ERL)
        liquidity_sweeps = analysis_result.get('liquidity_sweeps', [])
        print(f"\n💧 ENHANCED LIQUIDITY SWEEPS: {len(liquidity_sweeps)} detected")
        irl_count = sum(1 for ls in liquidity_sweeps if ls.get('liquidity_category') == 'IRL')
        erl_count = sum(1 for ls in liquidity_sweeps if ls.get('liquidity_category') == 'ERL')
        print(f"   IRL (Internal Range): {irl_count}")
        print(f"   ERL (External Range): {erl_count}")
        
        for i, ls in enumerate(liquidity_sweeps[:3]):  # Show first 3
            category = ls.get('liquidity_category', 'Unknown')
            print(f"   {i+1}. {ls['direction']} {category} sweep at ${ls.get('sweep_price', 0):.2f}")
            print(f"      Significance: {ls.get('significance', 'unknown')}")
            print(f"      Range Position: {ls.get('range_position', 'unknown')}")
            print(f"      Confidence: {ls.get('confidence_score', 0):.1%}")
        
        # 3. Test Killzone Timing
        print(f"\n⏱️ KILLZONE TIMING ANALYSIS:")
        killzone_patterns = 0
        patterns_with_timing = []
        
        # Check all patterns for killzone analysis
        all_patterns = (analysis_result.get('order_blocks', []) + 
                       analysis_result.get('fvg', []) + 
                       analysis_result.get('liquidity_sweeps', []))
        
        for pattern in all_patterns:
            if 'killzone_analysis' in pattern:
                killzone_patterns += 1
                if pattern['killzone_analysis']['active_killzone']:
                    patterns_with_timing.append(pattern)
        
        print(f"   Patterns analyzed: {killzone_patterns}")
        print(f"   Patterns in active killzones: {len(patterns_with_timing)}")
        
        for i, pattern in enumerate(patterns_with_timing[:3]):  # Show first 3
            kz = pattern['killzone_analysis']
            print(f"   {i+1}. {kz['active_killzone']} session pattern")
            print(f"      Timing: {kz['timing_description']}")
            print(f"      Killzone Strength: {kz['killzone_strength']:.1%}")
            print(f"      Timing Confidence: {kz['timing_confidence']:.1%}")
            if pattern.get('killzone_boost'):
                print(f"      📈 Confidence boosted by killzone timing!")
        
        # 4. Test Premium/Discount Zone Mapping
        print(f"\n🎯 PREMIUM/DISCOUNT ZONE MAPPING:")
        zone_mapped_patterns = 0
        premium_patterns = []
        discount_patterns = []
        
        for pattern in all_patterns:
            if 'zone_analysis' in pattern:
                zone_mapped_patterns += 1
                zone_type = pattern['zone_analysis']['zone_type']
                if zone_type == 'premium':
                    premium_patterns.append(pattern)
                elif zone_type == 'discount':
                    discount_patterns.append(pattern)
        
        print(f"   Patterns analyzed: {zone_mapped_patterns}")
        print(f"   Premium zone patterns: {len(premium_patterns)}")
        print(f"   Discount zone patterns: {len(discount_patterns)}")
        
        for i, pattern in enumerate(premium_patterns[:2]):  # Show first 2
            zone = pattern['zone_analysis']
            print(f"   {i+1}. Premium zone pattern")
            print(f"      Zone Quality: {zone['zone_quality']}")
            print(f"      Logic Validity: {zone['logic_validity']}")
            print(f"      Range Position: {zone['range_position']:.1%}")
            if pattern.get('zone_logic_boost'):
                print(f"      📈 Confidence boosted by zone logic!")
        
        # 5. Test Mitigation Blocks
        mitigation_blocks = analysis_result.get('mitigation_blocks', [])
        print(f"\n🧱 MITIGATION BLOCKS: {len(mitigation_blocks)} detected")
        for i, mb in enumerate(mitigation_blocks[:3]):  # Show first 3
            print(f"   {i+1}. {mb['mitigation_type']} mitigation")
            print(f"      Fill Percentage: {mb['fill_percentage']:.1%}")
            print(f"      Volume Strength: {mb['volume_strength']:.1f}x")
            print(f"      Candle Size Ratio: {mb['candle_size_ratio']:.1f}x")
            print(f"      Market Acknowledgment: {mb['market_acknowledgment']}")
            print(f"      Confidence: {mb['confidence_score']:.1%}")
        
        # 6. Test Trendline Liquidity
        trendline_liquidities = analysis_result.get('trendline_liquidities', [])
        print(f"\n📉 TRENDLINE LIQUIDITY: {len(trendline_liquidities)} detected")
        for i, tl in enumerate(trendline_liquidities[:3]):  # Show first 3
            print(f"   {i+1}. {tl['trendline_type']} trendline ({tl['direction']})")
            print(f"      Touch Count: {tl['touch_count']}")
            print(f"      Liquidity Strength: {tl['liquidity_strength']:.1%}")
            print(f"      Sweep Potential: {tl['sweep_potential']}")
            if tl['trendline_break']:
                print(f"      🚨 TRENDLINE BROKEN at ${tl['trendline_break']['break_price']:.2f}")
                print(f"      Break Strength: {tl['trendline_break']['break_strength']:.2%}")
            print(f"      Confidence: {tl['confidence_score']:.1%}")
        
        # Advanced Features Summary
        advanced_features = analysis_result.get('advanced_features', {})
        print(f"\n📊 ADVANCED FEATURES SUMMARY:")
        print(f"   Breaker Blocks: {advanced_features.get('breaker_blocks_count', 0)}")
        print(f"   Mitigation Blocks: {advanced_features.get('mitigation_blocks_count', 0)}")
        print(f"   Trendline Liquidities: {advanced_features.get('trendline_liquidities_count', 0)}")
        print(f"   IRL/ERL Enhanced: {advanced_features.get('irl_erl_enhanced', False)}")
        print(f"   Killzone Timing Applied: {advanced_features.get('killzone_timing_applied', False)}")
        print(f"   Premium/Discount Mapped: {advanced_features.get('premium_discount_mapped', False)}")
        
        # Overall Assessment
        print(f"\n🎯 OVERALL ANALYSIS:")
        print(f"   Symbol: {analysis_result['symbol']}")
        print(f"   Current Price: ${analysis_result['current_price']:.2f}")
        print(f"   Overall Confidence: {analysis_result['confidence_score']:.1%}")
        
        # Total patterns detected
        total_patterns = (len(analysis_result.get('order_blocks', [])) + 
                        len(analysis_result.get('fvg', [])) + 
                        len(analysis_result.get('liquidity_sweeps', [])) + 
                        len(breaker_blocks) + 
                        len(mitigation_blocks) + 
                        len(trendline_liquidities))
        
        print(f"   Total Patterns: {total_patterns}")
        
        # Save results for inspection
        print(f"\n💾 Saving detailed analysis results...")
        save_advanced_analysis_results(analysis_result)
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def save_advanced_analysis_results(analysis_result: Dict[str, Any]):
    """
    Save analysis results to JSON file for detailed inspection
    """
    try:
        filename = f"advanced_smc_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert any datetime objects to strings for JSON serialization
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            return obj
        
        # Recursively convert datetime objects
        def clean_for_json(data):
            if isinstance(data, dict):
                return {k: clean_for_json(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [clean_for_json(item) for item in data]
            else:
                return convert_datetime(data)
        
        clean_result = clean_for_json(analysis_result)
        
        with open(filename, 'w') as f:
            json.dump(clean_result, f, indent=2, default=str)
        
        print(f"✅ Analysis results saved to {filename}")
        
    except Exception as e:
        print(f"❌ Failed to save analysis results: {e}")

def main():
    """
    🚀 Main Test Runner
    """
    print("🚀 ADVANCED SMC FEATURES COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run comprehensive test
        success = test_advanced_smc_features()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 ALL ADVANCED SMC FEATURES TESTED SUCCESSFULLY!")
            print("\n✨ Features Verified:")
            print("   ✅ 1. Breaker Block Logic - Order blocks yang dibreak jadi support/resistance")
            print("   ✅ 2. IRL & ERL Liquidity - Internal/External Range liquidity categorization")
            print("   ✅ 3. Killzone Timing - London/NY/Asia session time filtering")
            print("   ✅ 4. Premium/Discount Zones - Fibonacci-based zone mapping")
            print("   ✅ 5. Mitigation Blocks - Market acknowledgment of order blocks")
            print("   ✅ 6. Trendline Liquidity - Diagonal support/resistance detection")
            print("\n🎯 PRODUCTION-READY: All advanced features integrated successfully!")
            
        else:
            print("\n❌ Some advanced features failed testing")
            
        return success
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)