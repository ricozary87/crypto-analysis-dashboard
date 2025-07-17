#!/usr/bin/env python3
"""
Test Signal Generation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.okx_fetcher import OKXAPIManager
from core.analyzer import TechnicalAnalyzer
from core.signal_engine import SignalEngine
import logging

def test_signal_generation():
    """Test signal generation with real OKX data"""
    logging.basicConfig(level=logging.INFO)
    
    print("Testing signal generation with real OKX data...")
    
    # Get data
    okx_manager = OKXAPIManager()
    df = okx_manager.get_candles('BTC-USDT', timeframe='1H', limit=100)
    
    if df is None or df.empty:
        print("✗ Failed to fetch data")
        return
        
    print(f"Data fetched: {len(df)} candles")
    
    # Analyze structure
    analyzer = TechnicalAnalyzer('BTC-USDT')
    structure = analyzer.analyze_data(df)
    print(f"Structure analysis complete")
    
    # Generate signals
    generator = SignalEngine()
    signals = generator.generate_signals('BTC-USDT', '1H')
    
    if not signals:
        print("No signals generated")
        return
    
    print(f"Generated {len(signals)} signals")
    print("✓ Signal generation test passed")

if __name__ == "__main__":
    test_signal_generation()