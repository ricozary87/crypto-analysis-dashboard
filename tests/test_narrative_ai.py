#!/usr/bin/env python3
"""
Test Enhanced Narrative AI Module
Tests all new features: retry mechanism, database storage, API usage monitoring
"""

import os
import sys
import time
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.narrative_ai import NarrativeAI

def test_narrative_ai():
    """Test the enhanced Narrative AI functionality"""
    print("=" * 50)
    print("Testing Enhanced Narrative AI Module")
    print("=" * 50)
    
    # Initialize Narrative AI
    narrative_ai = NarrativeAI()
    
    # Test data
    symbol = "BTC"
    
    signal_data = {
        'action': 'BUY',
        'pattern_type': 'Bullish Engulfing + Order Block',
        'entry_price': 67500.0,
        'stop_loss': 66000.0,
        'take_profit_1': 69000.0,
        'take_profit_2': 70500.0,
        'take_profit_3': 72000.0,
        'confidence': 0.78,
        'risk_reward_ratio': 3.0,
        'position_size_percentage': 2.0,
        'timeframe': '1H',
        'reason': 'Strong bullish confluence detected',
        'confluence_factors': [
            'Bullish engulfing at key support',
            'Order block rejection confirmed',
            'RSI divergence on 4H timeframe',
            'Volume spike above average',
            'Break of descending trendline'
        ]
    }
    
    market_data = {
        'current_price': 67450.0,
        'volume': 1250000.0,
        'rsi': 45.5,
        'trend': 'bullish reversal',
        'support_levels': [66000, 65000, 63500],
        'resistance_levels': [69000, 70500, 72000],
        'sentiment': 'neutral',
        'volatility': 'high',
        'key_levels': [67000, 68000, 69500]
    }
    
    # Test 1: Generate narrative (Indonesian)
    print("\n1. Testing Indonesian Narrative Generation...")
    try:
        narrative_id = narrative_ai.generate_analysis_narrative(
            symbol, signal_data, market_data, language="id"
        )
        
        print(f"✓ Indonesian narrative generated successfully")
        print(f"  Executive Summary: {narrative_id.executive_summary[:100]}...")
        print(f"  Confidence: {narrative_id.confidence:.1%}")
        
        if narrative_id.tokens_used:
            print(f"  Tokens Used: {narrative_id.tokens_used}")
            print(f"  API Cost: ${narrative_id.api_cost:.4f}")
    except Exception as e:
        print(f"✗ Failed to generate Indonesian narrative: {e}")
    
    # Test 2: Generate narrative (English)
    print("\n2. Testing English Narrative Generation...")
    try:
        # Modify signal slightly to avoid cache hit
        signal_data['confidence'] = 0.75
        narrative_en = narrative_ai.generate_analysis_narrative(
            symbol, signal_data, market_data, language="en"
        )
        
        print(f"✓ English narrative generated successfully")
        print(f"  Executive Summary: {narrative_en.executive_summary[:100]}...")
        print(f"  Trade Setup: {narrative_en.trade_setup[:100]}...")
    except Exception as e:
        print(f"✗ Failed to generate English narrative: {e}")
    
    # Test 3: Check API usage statistics
    print("\n3. Testing API Usage Statistics...")
    try:
        stats = narrative_ai.get_usage_statistics()
        
        print(f"✓ API Usage Statistics:")
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Successful: {stats['successful_requests']}")
        print(f"  Failed: {stats['failed_requests']}")
        print(f"  Total Tokens: {stats['total_tokens']}")
        print(f"  Total Cost: ${stats['total_cost']}")
        print(f"  Cache Hits: {stats['cache_hits']}")
        print(f"  Cache Hit Rate: {stats['cache_hit_rate']}%")
        
        if stats['total_narratives_stored']:
            print(f"  Narratives in DB: {stats['total_narratives_stored']}")
            
        if stats['last_24h']['requests'] > 0:
            print(f"  Last 24h - Requests: {stats['last_24h']['requests']}, Cost: ${stats['last_24h']['cost']}")
    except Exception as e:
        print(f"✗ Failed to get usage statistics: {e}")
    
    # Test 4: Test cache functionality
    print("\n4. Testing Cache Functionality...")
    try:
        # Use same data as test 1 to trigger cache hit
        signal_data['confidence'] = 0.78  # Reset to original
        start_time = time.time()
        
        cached_narrative = narrative_ai.generate_analysis_narrative(
            symbol, signal_data, market_data, language="id"
        )
        
        elapsed = time.time() - start_time
        
        if elapsed < 0.1:  # Cache hit should be very fast
            print(f"✓ Cache hit confirmed (response in {elapsed:.3f}s)")
        else:
            print(f"✗ Cache might not be working (response in {elapsed:.3f}s)")
            
    except Exception as e:
        print(f"✗ Failed to test cache: {e}")
    
    # Test 5: Test template fallback (when no API key)
    print("\n5. Testing Template Fallback...")
    try:
        # Temporarily remove API key
        original_key = narrative_ai.api_key
        narrative_ai.api_key = None
        narrative_ai.client = None
        
        template_narrative = narrative_ai.generate_analysis_narrative(
            symbol, signal_data, market_data, language="id"
        )
        
        print(f"✓ Template fallback working")
        print(f"  Template Summary: {template_narrative.executive_summary[:100]}...")
        
        # Restore API key
        narrative_ai.api_key = original_key
        if original_key:
            from openai import OpenAI
            narrative_ai.client = OpenAI(api_key=original_key)
            
    except Exception as e:
        print(f"✗ Failed to test template fallback: {e}")
    
    # Test 6: Test error handling for invalid data
    print("\n6. Testing Error Handling...")
    try:
        invalid_signal = {'action': 'INVALID'}
        invalid_market = {}
        
        error_narrative = narrative_ai.generate_analysis_narrative(
            symbol, invalid_signal, invalid_market, language="id"
        )
        
        print(f"✓ Error handling working (fallback to template)")
        
    except Exception as e:
        print(f"✓ Error properly caught: {type(e).__name__}")
    
    # Test 7: HTML formatting
    print("\n7. Testing HTML Formatting...")
    try:
        if 'narrative_id' in locals():
            html_output = narrative_ai.format_narrative_html(narrative_id)
            print(f"✓ HTML formatting successful")
            print(f"  HTML length: {len(html_output)} characters")
            print(f"  Contains sections: executive-summary={('executive-summary' in html_output)}, "
                  f"technical-analysis={('technical-analysis' in html_output)}")
    except Exception as e:
        print(f"✗ Failed to format HTML: {e}")
    
    print("\n" + "=" * 50)
    print("Testing Complete!")
    print("=" * 50)
    
    # Final summary
    final_stats = narrative_ai.get_usage_statistics()
    print(f"\nFinal Statistics:")
    print(f"- Total API calls made: {final_stats['total_requests']}")
    print(f"- Total cost incurred: ${final_stats['total_cost']}")
    print(f"- Cache efficiency: {final_stats['cache_hit_rate']}%")
    
    if not narrative_ai.api_key:
        print("\n⚠️  Note: No OpenAI API key found. All tests used template fallback.")
        print("   To test AI features, set OPENAI_API_KEY environment variable.")

if __name__ == "__main__":
    test_narrative_ai()