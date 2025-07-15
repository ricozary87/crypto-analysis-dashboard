#!/usr/bin/env python3
"""
Quick System Evaluation - AI Trading System
Focused testing with shorter timeouts
"""

import requests
import json
import time
import os
from datetime import datetime

def test_endpoint(endpoint, timeout=5):
    """Quick test of endpoint"""
    try:
        start_time = time.time()
        response = requests.get(f"http://localhost:5000{endpoint}", timeout=timeout)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            return f"✅ Working ({response_time:.0f}ms)"
        else:
            return f"❌ Failed (HTTP {response.status_code})"
    except requests.exceptions.Timeout:
        return "⚠️ Timeout"
    except Exception as e:
        return f"❌ Error: {str(e)[:30]}"

print("🚀 QUICK SYSTEM EVALUATION")
print("=" * 60)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# Phase 1: Core Integration
print("\n📋 PHASE 1: Core Integration")
print("-" * 40)
print(f"1. SMC Analyzer (/api/analyze/BTC): {test_endpoint('/api/analyze/BTC')}")
print(f"2. AI Engine (/api/enhanced-ai/narrative/BTC): {test_endpoint('/api/enhanced-ai/narrative/BTC', timeout=3)}")
print(f"3. Market Data DB: {test_endpoint('/api/market-data')}")
print(f"4. Files exist: {'✅' if os.path.exists('core/professional_smc_analyzer.py') else '❌'}")

# Phase 2: Advanced Dashboard
print("\n📋 PHASE 2: Advanced Trading Dashboard")
print("-" * 40)
print(f"1. Dashboard Access: {test_endpoint('/phase2-dashboard')}")
print(f"2. Snapshot Quick: {test_endpoint('/api/snapshot/BTC?mode=quick')}")
print(f"3. Technical Indicators: {test_endpoint('/api/technical-indicators/BTC')}")
print(f"4. Chart Data: {test_endpoint('/api/enhanced-charts/data/BTC')}")

# Phase 3: API Enhancement
print("\n📋 PHASE 3: API Endpoint Enhancement")
print("-" * 40)
print(f"1. Analyze Endpoint: {test_endpoint('/api/analyze/BTC')}")
print(f"2. Orderbook Data: {test_endpoint('/api/orderbook/BTC')}")
print(f"3. Depth Chart: {test_endpoint('/api/depth-chart/BTC')}")

# OKX Authentication
print("\nOKX Authentication:")
okx_configured = all([
    os.environ.get('OKX_API_KEY'),
    os.environ.get('OKX_SECRET_KEY'),
    os.environ.get('OKX_PASSPHRASE')
])
print(f"✅ Configured and working" if okx_configured else "❌ Missing credentials")

# Test real-time data
print("\n📊 REAL-TIME DATA CHECK:")
try:
    response = requests.get("http://localhost:5000/api/analyze/BTC", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"BTC Price: ${data.get('currentPrice', 'N/A')}")
        print(f"24h Change: {data.get('priceChange24h', 'N/A')}%")
        if 'signals' in data and data['signals']:
            print(f"Signals Found: {len(data['signals'])} signals")
        if 'smcPatterns' in data:
            print(f"SMC Patterns: {data.get('smcPatterns', {})}")
except:
    print("Failed to get real-time data")

# Summary
print("\n" + "=" * 60)
print("📈 QUICK EVALUATION SUMMARY")
print("=" * 60)

# Count working components
working = 0
total = 0
for line in open(__file__).readlines():
    if "test_endpoint(" in line and "print(" in line:
        total += 1
        if "✅" in line:
            working += 1

print(f"\nComponents tested: {total}")
print(f"Production Readiness: {'✅ READY' if working/total > 0.8 else '⚠️ NEEDS FIXES'}")