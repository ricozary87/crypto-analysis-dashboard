#!/usr/bin/env python3
"""Trigger immediate trading analysis for testing"""

import time
from core.orchestrator import MainOrchestrator

def main():
    print("Starting immediate trading analysis...")
    
    # Initialize orchestrator
    orchestrator = MainOrchestrator()
    
    # Run one cycle immediately
    print(f"Running analysis cycle with confidence threshold: {orchestrator.confidence_threshold}")
    
    try:
        processed = orchestrator.process_symbols_with_retry()
        print(f"Analysis complete! Processed {processed} symbol-timeframe combinations.")
        
        # Log performance
        orchestrator.log_performance_metrics()
        
        print("Check the dashboard for new signals!")
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    main()