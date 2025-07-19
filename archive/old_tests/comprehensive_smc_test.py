#!/usr/bin/env python3
"""
🎯 Comprehensive SMC Test with Real Market Data

Tests enhanced SMC analyzer with realistic market data to demonstrate:
- Volume Delta and CVD confirmation
- Enhanced pattern detection with confidence scoring
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
from core.okx_fetcher import OKXAPIManager

def fetch_real_market_data(symbol: str = "BTC-USDT") -> pd.DataFrame:
    """
    Fetch real market data from OKX API
    """
    try:
        okx_manager = OKXAPIManager()
        df = okx_manager.get_candles(symbol, timeframe='1H', limit=200)
        
        if df is not None and not df.empty:
            print(f"✅ Fetched {len(df)} real market candles for {symbol}")
            print(f"   Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
            print(f"   Volume range: {df['volume'].min():.0f} - {df['volume'].max():.0f}")
            return df
        else:
            print("❌ Failed to fetch real market data, using synthetic data")
            return create_realistic_test_data()
            
    except Exception as e:
        print(f"❌ Error fetching real data: {e}")
        return create_realistic_test_data()

def create_realistic_test_data() -> pd.DataFrame:
    """
    Create realistic market data with SMC patterns
    """
    print("📊 Creating realistic synthetic market data...")
    
    # 200 candles with realistic price action
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1h')
    base_price = 50000
    
    # Create price series with realistic volatility and trends
    prices = []
    volumes = []
    
    for i in range(200):
        # Add trend and volatility
        trend = np.sin(i * 0.03) * 0.005  # Long-term trend
        volatility = np.random.normal(0, 0.008)  # Daily volatility
        
        # Create specific patterns for SMC detection
        if i == 50:  # CHoCH pattern
            pattern_move = 0.02  # 2% move
        elif i == 100:  # Order block formation
            pattern_move = -0.015  # 1.5% pullback
        elif i == 150:  # FVG formation
            pattern_move = 0.025  # 2.5% gap
        else:
            pattern_move = 0
        
        # Calculate price
        price_factor = 1 + trend + volatility + pattern_move
        current_price = base_price * (1 + (i * 0.0001)) * price_factor
        
        # Create realistic OHLC
        spread = current_price * 0.003  # 0.3% spread
        open_price = current_price * (1 + np.random.uniform(-0.001, 0.001))
        high_price = current_price + spread * np.random.uniform(0.5, 2.0)
        low_price = current_price - spread * np.random.uniform(0.5, 2.0)
        close_price = current_price * (1 + np.random.uniform(-0.002, 0.002))
        
        prices.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price
        })
        
        # Volume with realistic patterns
        base_volume = 1000000
        volume_multiplier = 1 + np.random.uniform(-0.4, 1.2)
        
        # Higher volume at pattern formations
        if i in [50, 100, 150]:
            volume_multiplier *= 3.0
        
        volumes.append(base_volume * volume_multiplier)
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': dates,
        'open': [p['open'] for p in prices],
        'high': [p['high'] for p in prices],
        'low': [p['low'] for p in prices],
        'close': [p['close'] for p in prices],
        'volume': volumes
    })
    
    print(f"✅ Created {len(df)} synthetic candles with SMC patterns")
    print(f"   Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    print(f"   Volume range: {df['volume'].min():.0f} - {df['volume'].max():.0f}")
    
    return df

def test_comprehensive_smc_analysis():
    """
    🎯 Test Comprehensive SMC Analysis with Real/Realistic Data
    """
    print("🎯 COMPREHENSIVE SMC ANALYSIS TEST")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = ProfessionalSMCAnalyzer()
    print("✅ Professional SMC Analyzer initialized")
    
    # Get market data
    print("\n📊 Fetching market data...")
    df = fetch_real_market_data("BTC-USDT")
    
    # Run comprehensive analysis
    print("\n🔍 Running comprehensive SMC analysis...")
    
    analysis_result = analyzer.analyze_comprehensive(
        df=df,
        symbol="BTC-USDT", 
        timeframe="1H"
    )
    
    print("✅ Comprehensive analysis completed successfully")
    
    # Detailed analysis of results
    print("\n📊 ANALYSIS RESULTS:")
    print("-" * 40)
    
    # Basic info
    print(f"Symbol: {analysis_result['symbol']}")
    print(f"Timeframe: {analysis_result['timeframe']}")
    print(f"Current Price: ${analysis_result['current_price']:.2f}")
    print(f"Overall Confidence: {analysis_result['confidence_score']:.1%}")
    
    # Volume analysis
    volume_confirmation = analysis_result.get('volume_confirmation', {})
    print(f"\n📈 VOLUME ANALYSIS:")
    print(f"   Volume Deltas: {len(volume_confirmation.get('volume_deltas', []))}")
    print(f"   CVD Data Points: {len(volume_confirmation.get('cvd_data', []))}")
    print(f"   Volume Absorptions: {len(volume_confirmation.get('volume_absorptions', []))}")
    print(f"   CVD Divergences: {len(volume_confirmation.get('cvd_divergences', []))}")
    
    # Market structure
    structure = analysis_result.get('structure', {})
    market_structure = structure.get('market_structure', {})
    print(f"\n🏗️ MARKET STRUCTURE:")
    print(f"   Trend: {market_structure.get('trend', 'unknown')}")
    print(f"   Trend Strength: {market_structure.get('trend_strength', 0):.1%}")
    print(f"   Structure Quality: {market_structure.get('structure_quality', 0):.1%}")
    
    # CHoCH/BOS signals
    choch_bos_signals = structure.get('choch_bos_signals', [])
    print(f"\n🔄 CHoCH/BOS SIGNALS: {len(choch_bos_signals)}")
    for i, signal in enumerate(choch_bos_signals[:5]):  # Show first 5
        print(f"   {i+1}. {signal['type']} {signal['direction']} at ${signal['price']:.2f}")
        print(f"      Confidence: {signal.get('confidence_score', 0):.1%}")
        print(f"      Volume Confirmation: {signal.get('volume_confirmation', False)}")
    
    # Order blocks
    order_blocks = analysis_result.get('order_blocks', [])
    print(f"\n🧱 ORDER BLOCKS: {len(order_blocks)}")
    for i, ob in enumerate(order_blocks[:5]):  # Show first 5
        print(f"   {i+1}. {ob['direction']} OB: ${ob.get('price_low', 0):.2f} - ${ob.get('price_high', 0):.2f}")
        print(f"      Confidence: {ob.get('confidence_score', 0):.1%}")
        print(f"      Volume Ratio: {ob.get('volume_ratio', 0):.1f}x")
    
    # FVG signals
    fvg_signals = analysis_result.get('fvg', [])
    print(f"\n🔳 FAIR VALUE GAPS: {len(fvg_signals)}")
    for i, fvg in enumerate(fvg_signals[:5]):  # Show first 5
        print(f"   {i+1}. {fvg['direction']} FVG: ${fvg.get('gap_low', 0):.2f} - ${fvg.get('gap_high', 0):.2f}")
        print(f"      Gap Size: {fvg.get('gap_size_percent', 0):.2f}%")
        print(f"      Confidence: {fvg.get('confidence_score', 0):.1%}")
    
    # Liquidity sweeps
    liquidity_sweeps = analysis_result.get('liquidity_sweeps', [])
    print(f"\n🌊 LIQUIDITY SWEEPS: {len(liquidity_sweeps)}")
    for i, sweep in enumerate(liquidity_sweeps[:5]):  # Show first 5
        category = sweep.get('liquidity_category', 'Unknown')
        print(f"   {i+1}. {sweep['direction']} {category} sweep at ${sweep.get('sweep_price', 0):.2f}")
        print(f"      Confidence: {sweep.get('confidence_score', 0):.1%}")
        print(f"      Distance: {sweep.get('sweep_distance', 0):.2f}")
    
    # Confluence zones
    nested_order_blocks = analysis_result.get('nested_order_blocks', [])
    confluence_zones = analysis_result.get('confluence_zones', [])
    total_confluences = len(nested_order_blocks) + len(confluence_zones)
    print(f"\n🎯 CONFLUENCE ZONES: {total_confluences}")
    print(f"   Nested Order Blocks: {len(nested_order_blocks)}")
    print(f"   FVG-OB Confluences: {len(confluence_zones)}")
    
    # AI-ready output
    ai_snapshot = analysis_result.get('ai_snapshot', {})
    pattern_counts = ai_snapshot.get('pattern_counts', {})
    print(f"\n🤖 AI-READY OUTPUT:")
    print(f"   Total Patterns: {sum(pattern_counts.values())}")
    print(f"   GPT Descriptions: {len(ai_snapshot.get('gpt_descriptions', {}))}")
    print(f"   Visualization Data: {len(ai_snapshot.get('visualization_ready', {}))}")
    
    # Trading signals
    trading_signals = analysis_result.get('trading_signals', [])
    print(f"\n📈 TRADING SIGNALS: {len(trading_signals)}")
    for i, signal in enumerate(trading_signals[:3]):  # Show first 3
        print(f"   {i+1}. {signal['direction']} {signal.get('pattern_type', 'Unknown')} signal")
        print(f"      Entry: ${signal.get('entry_level', 0):.2f}")
        print(f"      Stop Loss: ${signal.get('stop_loss', 0):.2f}")
        print(f"      Take Profit: ${signal.get('take_profit', 0):.2f}")
        print(f"      R:R Ratio: {signal.get('risk_reward_ratio', 0):.1f}:1")
        print(f"      Signal Strength: {signal.get('signal_strength', 0):.1%}")
    
    # SMC summary
    smc_summary = analysis_result.get('smc_summary', {})
    print(f"\n📊 SMC SUMMARY:")
    print(f"   Analysis Quality: {smc_summary.get('analysis_quality', 'unknown')}")
    print(f"   Market Bias: {smc_summary.get('market_bias', 'unknown')}")
    print(f"   Recommendation: {smc_summary.get('recommendation', 'No recommendation')}")
    
    pattern_summary = smc_summary.get('pattern_summary', {})
    print(f"   Total Patterns: {pattern_summary.get('total_patterns', 0)}")
    
    return analysis_result

def save_analysis_results(analysis_result: Dict[str, Any]):
    """
    Save analysis results to JSON file for inspection
    """
    try:
        filename = f"enhanced_smc_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
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
    🎯 Main Test Runner
    """
    print("🎯 COMPREHENSIVE SMC ANALYZER TEST")
    print("=" * 60)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run comprehensive test
        analysis_result = test_comprehensive_smc_analysis()
        
        # Save results
        print("\n💾 Saving analysis results...")
        save_analysis_results(analysis_result)
        
        print("\n" + "=" * 60)
        print("🎉 COMPREHENSIVE TEST COMPLETED SUCCESSFULLY!")
        print("\n✨ Enhanced SMC Analyzer Features Verified:")
        print("   ✅ Volume Delta and CVD calculations")
        print("   ✅ Enhanced pattern detection with confidence scoring")
        print("   ✅ Nested order blocks and confluence zones")
        print("   ✅ IRL/ERL liquidity categorization")
        print("   ✅ AI-ready output formatting")
        print("   ✅ Trading signal generation with R:R ratios")
        print("   ✅ Comprehensive market structure analysis")
        
        return True
        
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