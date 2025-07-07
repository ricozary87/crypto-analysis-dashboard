"""
Test Enhanced Confluence Checker
Demonstrates configurable weights, detailed logging, and historical analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.confluence_checker import ConfluenceChecker
from core.okx_fetcher import OKXAPIManager
import logging
import json

# Configure logging to show detailed decision logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('confluence_checker.log')
    ]
)

def test_confluence_checker():
    """Test the enhanced Confluence Checker functionality"""
    print("=" * 80)
    print("Testing Enhanced Confluence Checker with Configurable Weights")
    print("=" * 80)
    
    # Initialize with custom weights
    custom_weights = {
        'smc': 0.35,           # Give more weight to SMC
        'price_action': 0.20,  # Less weight to price action
        'indicators': 0.20,    # Equal weight to indicators
        'volume': 0.15,        # Volume confirmation
        'structure': 0.10      # Market structure
    }
    
    confluence = ConfluenceChecker(
        min_confluence_score=0.60,  # 60% minimum confidence
        required_confirmations=3,
        risk_reward_min=2.0,
        component_weights=custom_weights
    )
    
    # Get test data
    api = OKXAPIManager()
    df = api.get_candles('BTC-USDT', '1H', limit=300)
    
    if df is None or df.empty:
        print("Failed to fetch data")
        return
    
    # Test 1: Analyze for confluence signals
    print("\n1. Analyzing BTC-USDT for high-confluence trading opportunities...")
    signal = confluence.analyze_confluence(df, 'BTC-USDT', '1H')
    
    if signal:
        print("\n✅ HIGH-CONFLUENCE SIGNAL DETECTED!")
        summary = confluence.get_confluence_summary(signal)
        
        print(f"\n📊 Signal Summary:")
        print(f"   Signal ID: {summary['signal_id']}")
        print(f"   Action: {summary['action']}")
        print(f"   Confidence: {summary['confidence']}")
        print(f"   Entry: ${summary['entry']:,.2f}")
        print(f"   Stop Loss: ${summary['stop_loss']:,.2f}")
        print(f"   Targets: ${summary['targets'][0]:,.2f}, ${summary['targets'][1]:,.2f}, ${summary['targets'][2]:,.2f}")
        print(f"   Risk/Reward: {summary['risk_reward']}")
        
        print(f"\n📈 Component Scores:")
        for component, score in summary['scores'].items():
            print(f"   {component}: {score}")
        
        print(f"\n✓ Confluence Factors ({summary['confirmations']} confirmations):")
        for factor in summary['factors']:
            print(f"   - {factor}")
        
        # Show detailed decision logs
        print("\n📝 Detailed Decision Logs:")
        print("-" * 60)
        for log in summary['decision_logs']:
            print(log)
        
        # Test 2: Simulate price movement and update performance
        print("\n" + "=" * 80)
        print("2. Simulating Price Movement and Tracking Performance...")
        
        # Simulate price reaching TP1
        if signal.action == 'BUY':
            simulated_price = signal.take_profit_1 + 10
        else:
            simulated_price = signal.take_profit_1 - 10
        
        confluence.update_signal_performance(signal.signal_id, simulated_price)
        
        # Get updated performance
        active_signals = confluence.get_active_signals()
        print(f"\nActive signals: {len(active_signals)}")
        
        for active in active_signals:
            print(f"\nSignal {active.signal_id}:")
            print(f"  Status: TP1 hit: {active.hit_tp1}, TP2 hit: {active.hit_tp2}, SL hit: {active.hit_sl}")
            print(f"  Max profit: {active.max_profit_percent:.2f}%")
            if active.time_to_tp1:
                print(f"  Time to TP1: {active.time_to_tp1} minutes")
    else:
        print("\n❌ No high-confluence signal found at this time")
        print("   This is normal - high-confluence opportunities are rare!")
    
    # Test 3: Show historical performance (with simulated data for demonstration)
    print("\n" + "=" * 80)
    print("3. Historical Performance Analysis")
    
    # Add some simulated historical signals for demonstration
    if signal:
        # Simulate a few more signals
        for i in range(3):
            confluence.signal_history.append(signal)  # Just for demo
    
    performance = confluence.get_historical_performance()
    
    print(f"\n📊 Overall Performance Statistics:")
    print(f"   Total signals: {performance['total_signals']}")
    print(f"   Win rate: {performance['win_rate']}")
    print(f"   Average confidence: {performance['avg_confidence']}")
    print(f"   Average time to TP1: {performance['avg_time_to_tp1']}")
    
    if performance['component_performance']:
        print(f"\n📈 Component Performance:")
        for component, stats in performance['component_performance'].items():
            print(f"   {component}: {stats['signals']} signals, {stats['win_rate']:.1f}% win rate")
    
    # Test 4: Test different weight configurations
    print("\n" + "=" * 80)
    print("4. Testing Different Weight Configurations")
    
    # Conservative weights (favor indicators)
    conservative_weights = {
        'smc': 0.20,
        'price_action': 0.15,
        'indicators': 0.35,  # More weight on traditional indicators
        'volume': 0.20,
        'structure': 0.10
    }
    
    confluence_conservative = ConfluenceChecker(
        min_confluence_score=0.70,  # Higher threshold
        required_confirmations=4,   # More confirmations needed
        component_weights=conservative_weights
    )
    
    print("\n🛡️ Conservative Configuration:")
    print("   Weights:", json.dumps(conservative_weights, indent=2))
    
    signal_conservative = confluence_conservative.analyze_confluence(df, 'BTC-USDT', '1H')
    if signal_conservative:
        print("   ✓ Signal found with conservative settings")
    else:
        print("   ✗ No signal with conservative settings (more selective)")
    
    # Aggressive weights (favor SMC and price action)
    aggressive_weights = {
        'smc': 0.40,         # Heavy on SMC
        'price_action': 0.30, # Heavy on price action
        'indicators': 0.15,
        'volume': 0.10,
        'structure': 0.05
    }
    
    confluence_aggressive = ConfluenceChecker(
        min_confluence_score=0.55,  # Lower threshold
        required_confirmations=2,   # Fewer confirmations
        component_weights=aggressive_weights
    )
    
    print("\n⚡ Aggressive Configuration:")
    print("   Weights:", json.dumps(aggressive_weights, indent=2))
    
    signal_aggressive = confluence_aggressive.analyze_confluence(df, 'BTC-USDT', '1H')
    if signal_aggressive:
        print("   ✓ Signal found with aggressive settings")
    else:
        print("   ✗ No signal with aggressive settings")
    
    print("\n" + "=" * 80)
    print("✅ Enhanced Confluence Checker test completed!")
    print("Check 'confluence_checker.log' for detailed decision logs")

if __name__ == "__main__":
    test_confluence_checker()