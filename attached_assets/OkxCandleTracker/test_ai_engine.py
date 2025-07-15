#!/usr/bin/env python3
"""
Test script untuk AI Engine
Menguji fungsi generate_ai_snapshot dengan data sample
"""

import json
from ai_engine import AIEngine

def test_ai_engine():
    """Test AI Engine dengan sample data"""
    
    # Sample analysis data
    sample_analysis = {
        "candlestick": [
            {"timestamp": "2025-07-14T08:00:00Z", "open": 166.5, "high": 167.8, "low": 165.2, "close": 167.4, "volume": 1250000},
            {"timestamp": "2025-07-14T08:05:00Z", "open": 167.4, "high": 167.9, "low": 166.8, "close": 167.1, "volume": 1180000}
        ],
        "confluence_summary": {
            "overall_signal": "bullish",
            "consensus_level": 0.72,
            "bullish_factors": 5,
            "bearish_factors": 2,
            "neutral_factors": 1
        },
        "smc_analysis": {
            "signal": "bullish",
            "strength": 0.65,
            "bias": "bullish",
            "market_structure": "higher_highs"
        },
        "volume_analysis": {
            "signal": "neutral",
            "strength": 0.45,
            "volume_trend": "increasing",
            "cvd": 12500
        },
        "orderbook_analysis": {
            "signal": "bullish",
            "strength": 0.68,
            "bid_ask_imbalance": 0.034,
            "spread": 0.01
        }
    }
    
    # Initialize AI Engine
    ai_engine = AIEngine()
    
    if not ai_engine.is_available():
        print("⚠️  AI Engine tidak tersedia (OpenAI API key tidak ditemukan)")
        return
    
    print("🚀 Testing AI Engine...")
    
    try:
        # Test Quick Mode
        print("\n🔥 Testing Quick Mode...")
        quick_narrative = ai_engine.generate_ai_snapshot("SOL-USDT", "5m", sample_analysis, quick_mode=True)
        print(f"✅ Quick Mode berhasil! Length: {len(quick_narrative)} characters")
        
        # Test Comprehensive Mode
        print("\n📊 Testing Comprehensive Mode...")
        full_narrative = ai_engine.generate_ai_snapshot("SOL-USDT", "5m", sample_analysis, quick_mode=False)
        print(f"✅ Comprehensive Mode berhasil! Length: {len(full_narrative)} characters")
        
        # Show sample output
        print("\n📝 Sample Quick Mode Output:")
        print("-" * 50)
        print(quick_narrative[:500] + "..." if len(quick_narrative) > 500 else quick_narrative)
        
        print("\n🎯 AI Engine Test PASSED! 🎯")
        
    except Exception as e:
        print(f"❌ AI Engine Test FAILED: {str(e)}")

if __name__ == "__main__":
    test_ai_engine()