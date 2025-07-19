#!/usr/bin/env python3
"""
Comprehensive System Evaluation - AI Trading System
Testing all 3 phases of development
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

class SystemEvaluator:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.results = {
            'phase1': {},
            'phase2': {},
            'phase3': {},
            'overall': {}
        }
        self.errors = []
        
    def test_endpoint(self, endpoint, method='GET', data=None, description=""):
        """Test a single endpoint and return result"""
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{self.base_url}{endpoint}", json=data, timeout=10)
            
            response_time = (time.time() - start_time) * 1000  # in ms
            
            result = {
                'status_code': response.status_code,
                'response_time': response_time,
                'success': response.status_code == 200,
                'data': None,
                'error': None
            }
            
            if response.status_code == 200:
                try:
                    result['data'] = response.json()
                except:
                    result['data'] = response.text
            else:
                result['error'] = f"HTTP {response.status_code}: {response.text[:200]}"
                self.errors.append(f"{endpoint}: {result['error']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Exception in {endpoint}: {str(e)}"
            self.errors.append(error_msg)
            return {
                'status_code': 0,
                'response_time': 0,
                'success': False,
                'data': None,
                'error': error_msg
            }
    
    def evaluate_phase1(self):
        """PHASE 1: Core Integration Testing"""
        print("\n" + "="*60)
        print("🔍 PHASE 1: Core Integration Evaluation")
        print("="*60)
        
        phase1_results = {}
        
        # Test 1: Check if SMC analyzer is integrated
        print("\n1. Testing SMC Analyzer Integration...")
        analyze_result = self.test_endpoint("/api/analyze/BTC")
        
        if analyze_result['success'] and analyze_result['data']:
            data = analyze_result['data']
            # Check for SMC patterns
            has_smc = any([
                'patterns' in data,
                'smc_analysis' in data,
                'bos' in str(data).lower(),
                'choch' in str(data).lower(),
                'fvg' in str(data).lower()
            ])
            phase1_results['smc_analyzer'] = "✅ Working" if has_smc else "⚠️ SMC patterns not found"
            print(f"   SMC Analyzer: {phase1_results['smc_analyzer']}")
        else:
            phase1_results['smc_analyzer'] = "❌ Failed"
            print(f"   SMC Analyzer: ❌ Failed - {analyze_result['error']}")
        
        # Test 2: Check AI Engine integration
        print("\n2. Testing AI Engine Integration...")
        ai_result = self.test_endpoint("/api/enhanced-ai/narrative/BTC")
        
        if ai_result['success'] and ai_result['data']:
            data = ai_result['data']
            has_narrative = 'narrative' in data and len(str(data.get('narrative', ''))) > 100
            phase1_results['ai_engine'] = "✅ Working" if has_narrative else "⚠️ Narrative too short"
            print(f"   AI Engine: {phase1_results['ai_engine']}")
            
            # Check if GPT-4o accessible
            if 'ai_provider' in data:
                print(f"   AI Provider: {data.get('ai_provider', 'Unknown')}")
        else:
            phase1_results['ai_engine'] = "❌ Failed"
            print(f"   AI Engine: ❌ Failed - {ai_result['error']}")
        
        # Test 3: Check database models
        print("\n3. Testing Database Models...")
        db_endpoints = [
            ("/api/market-data", "MarketData"),
            ("/api/orderbook-data", "OrderbookData"),
            ("/api/technical-indicators-data", "TechnicalIndicatorData"),
            ("/api/ai-snapshots", "AISnapshotArchive")
        ]
        
        db_working = 0
        for endpoint, model_name in db_endpoints:
            result = self.test_endpoint(endpoint)
            if result['success']:
                db_working += 1
                print(f"   {model_name}: ✅")
            else:
                print(f"   {model_name}: ❌")
        
        phase1_results['database_models'] = f"✅ {db_working}/4 models working" if db_working >= 3 else f"⚠️ Only {db_working}/4 models working"
        
        # Test 4: File integration
        print("\n4. Testing Core File Integration...")
        core_files_exist = all([
            os.path.exists('core/professional_smc_analyzer.py'),
            os.path.exists('core/enhanced_ai_engine.py'),
            os.path.exists('routes.py'),
            os.path.exists('models.py')
        ])
        
        phase1_results['file_integration'] = "✅ All core files present" if core_files_exist else "❌ Missing core files"
        print(f"   File Integration: {phase1_results['file_integration']}")
        
        self.results['phase1'] = phase1_results
        
        # Calculate phase 1 score
        phase1_score = sum(1 for v in phase1_results.values() if '✅' in str(v))
        phase1_total = len(phase1_results)
        print(f"\n📊 Phase 1 Score: {phase1_score}/{phase1_total} components working")
        
        return phase1_score, phase1_total
    
    def evaluate_phase2(self):
        """PHASE 2: Advanced Trading Dashboard Testing"""
        print("\n" + "="*60)
        print("🎨 PHASE 2: Advanced Trading Dashboard Evaluation")
        print("="*60)
        
        phase2_results = {}
        
        # Test 1: Dashboard accessibility
        print("\n1. Testing Dashboard Accessibility...")
        dashboard_result = self.test_endpoint("/phase2-dashboard")
        phase2_results['dashboard_access'] = "✅ Accessible" if dashboard_result['success'] else "❌ Not accessible"
        print(f"   Dashboard Access: {phase2_results['dashboard_access']}")
        
        # Test 2: Snapshot system
        print("\n2. Testing Snapshot System...")
        snapshot_modes = ['quick', 'comprehensive', 'deep']
        snapshot_working = 0
        
        for mode in snapshot_modes:
            result = self.test_endpoint(f"/api/snapshot/BTC?mode={mode}")
            if result['success']:
                snapshot_working += 1
                print(f"   Snapshot ({mode}): ✅")
            else:
                print(f"   Snapshot ({mode}): ❌")
        
        phase2_results['snapshot_system'] = f"✅ {snapshot_working}/3 modes working" if snapshot_working == 3 else f"⚠️ Only {snapshot_working}/3 modes working"
        
        # Test 3: Technical indicators
        print("\n3. Testing Technical Indicators...")
        indicators_result = self.test_endpoint("/api/technical-indicators/BTC")
        
        if indicators_result['success'] and indicators_result['data']:
            data = indicators_result['data']
            # Count indicator categories
            categories = ['trend', 'momentum', 'volatility', 'volume']
            available_categories = sum(1 for cat in categories if cat in data)
            
            # Count total indicators
            total_indicators = 0
            for category in categories:
                if category in data and isinstance(data[category], dict):
                    total_indicators += len(data[category])
            
            phase2_results['technical_indicators'] = f"✅ {total_indicators} indicators in {available_categories} categories" if total_indicators >= 30 else f"⚠️ Only {total_indicators} indicators"
            print(f"   Technical Indicators: {phase2_results['technical_indicators']}")
        else:
            phase2_results['technical_indicators'] = "❌ Failed"
            print(f"   Technical Indicators: ❌ Failed")
        
        # Test 4: Chart data API
        print("\n4. Testing Chart Data API...")
        chart_result = self.test_endpoint("/api/enhanced-charts/data/BTC")
        
        if chart_result['success'] and chart_result['data']:
            has_candlestick = 'candlestick' in chart_result['data']
            has_volume = 'volume' in chart_result['data']
            phase2_results['chart_system'] = "✅ Plotly charts working" if has_candlestick and has_volume else "⚠️ Incomplete chart data"
        else:
            phase2_results['chart_system'] = "❌ Chart API failed"
        print(f"   Chart System: {phase2_results['chart_system']}")
        
        self.results['phase2'] = phase2_results
        
        # Calculate phase 2 score
        phase2_score = sum(1 for v in phase2_results.values() if '✅' in str(v))
        phase2_total = len(phase2_results)
        print(f"\n📊 Phase 2 Score: {phase2_score}/{phase2_total} components working")
        
        return phase2_score, phase2_total
    
    def evaluate_phase3(self):
        """PHASE 3: API Endpoint Enhancement Testing"""
        print("\n" + "="*60)
        print("🚀 PHASE 3: API Endpoint Enhancement Evaluation")
        print("="*60)
        
        phase3_results = {}
        
        # Test all 6 enhanced endpoints
        endpoints_to_test = [
            ("/api/analyze/BTC", "Enhanced Analyze"),
            ("/api/snapshot/BTC", "Snapshot Generator"),
            ("/api/orderbook/BTC", "Orderbook Data"),
            ("/api/depth-chart/BTC", "Depth Chart"),
            ("/api/technical-indicators/BTC", "Technical Indicators"),
            ("/api/enhanced-ai/narrative/BTC", "AI Narrative")
        ]
        
        print("\n1. Testing All Enhanced Endpoints...")
        endpoint_success = 0
        total_response_time = 0
        
        for endpoint, name in endpoints_to_test:
            result = self.test_endpoint(endpoint)
            if result['success']:
                endpoint_success += 1
                total_response_time += result['response_time']
                status = f"✅ Working ({result['response_time']:.0f}ms)"
            else:
                status = f"❌ Failed"
            
            phase3_results[name] = status
            print(f"   {name}: {status}")
        
        # Test OKX Authentication
        print("\n2. Testing OKX Authentication...")
        
        # Check if OKX credentials exist
        okx_api_key = os.environ.get('OKX_API_KEY')
        okx_secret_key = os.environ.get('OKX_SECRET_KEY')
        okx_passphrase = os.environ.get('OKX_PASSPHRASE')
        
        if all([okx_api_key, okx_secret_key, okx_passphrase]):
            # Test authenticated endpoint
            from core.okx_fetcher import OKXAPIManager
            try:
                okx = OKXAPIManager()
                auth_success = okx.test_authentication()
                
                if auth_success:
                    phase3_results['okx_authentication'] = "✅ Authenticated endpoints working"
                    print("   OKX Authentication: ✅ Working")
                    
                    # Test specific authenticated endpoints
                    balance = okx.get_account_balance()
                    config = okx.get_account_config()
                    
                    if balance:
                        print("   - Account Balance: ✅ Accessible")
                    if config:
                        print("   - Account Config: ✅ Accessible")
                else:
                    phase3_results['okx_authentication'] = "❌ Authentication failed"
                    print("   OKX Authentication: ❌ Failed")
            except Exception as e:
                phase3_results['okx_authentication'] = f"❌ Error: {str(e)}"
                print(f"   OKX Authentication: ❌ Error - {str(e)}")
        else:
            phase3_results['okx_authentication'] = "⚠️ Credentials missing"
            print("   OKX Authentication: ⚠️ Missing credentials")
        
        # Check response times
        if endpoint_success > 0:
            avg_response_time = total_response_time / endpoint_success
            phase3_results['avg_response_time'] = f"{'✅' if avg_response_time < 500 else '⚠️'} {avg_response_time:.0f}ms average"
            print(f"\n3. Average Response Time: {phase3_results['avg_response_time']}")
        
        self.results['phase3'] = phase3_results
        
        # Calculate phase 3 score
        phase3_score = sum(1 for v in phase3_results.values() if '✅' in str(v))
        phase3_total = len(phase3_results)
        print(f"\n📊 Phase 3 Score: {phase3_score}/{phase3_total} components working")
        
        return phase3_score, phase3_total
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE SYSTEM EVALUATION REPORT")
        print("="*80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Run all evaluations
        phase1_score, phase1_total = self.evaluate_phase1()
        phase2_score, phase2_total = self.evaluate_phase2()
        phase3_score, phase3_total = self.evaluate_phase3()
        
        # Calculate overall score
        total_score = phase1_score + phase2_score + phase3_score
        total_components = phase1_total + phase2_total + phase3_total
        overall_percentage = (total_score / total_components) * 100
        
        # Summary
        print("\n" + "="*60)
        print("📈 OVERALL SYSTEM STATUS")
        print("="*60)
        
        print(f"\n✅ PHASE 1 - Core Integration: {phase1_score}/{phase1_total} components working")
        for component, status in self.results['phase1'].items():
            print(f"   - {component}: {status}")
        
        print(f"\n✅ PHASE 2 - Advanced Dashboard: {phase2_score}/{phase2_total} components working")
        for component, status in self.results['phase2'].items():
            print(f"   - {component}: {status}")
        
        print(f"\n✅ PHASE 3 - API Enhancement: {phase3_score}/{phase3_total} components working")
        for component, status in self.results['phase3'].items():
            print(f"   - {component}: {status}")
        
        # Error log
        if self.errors:
            print("\n" + "="*60)
            print("❌ ERROR LOG")
            print("="*60)
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
        
        # Production readiness assessment
        print("\n" + "="*60)
        print("🎯 PRODUCTION READINESS ASSESSMENT")
        print("="*60)
        
        print(f"\nOverall Score: {total_score}/{total_components} ({overall_percentage:.1f}%)")
        
        if overall_percentage >= 90:
            readiness = "✅ PRODUCTION READY"
            recommendation = "System is fully functional and ready for production deployment."
        elif overall_percentage >= 70:
            readiness = "⚠️ NEARLY READY"
            recommendation = "System is mostly functional but needs minor fixes before production."
        else:
            readiness = "❌ NOT READY"
            recommendation = "System requires significant fixes before production deployment."
        
        print(f"Status: {readiness}")
        print(f"Recommendation: {recommendation}")
        
        # Specific recommendations
        if overall_percentage < 100:
            print("\n📝 RECOMMENDED FIXES:")
            
            fix_count = 1
            for phase, results in [('Phase 1', self.results['phase1']), 
                                  ('Phase 2', self.results['phase2']), 
                                  ('Phase 3', self.results['phase3'])]:
                for component, status in results.items():
                    if '❌' in str(status) or '⚠️' in str(status):
                        print(f"{fix_count}. Fix {phase} - {component}: Current status {status}")
                        fix_count += 1
        
        print("\n" + "="*80)
        print("EVALUATION COMPLETE")
        print("="*80)

# Run evaluation
if __name__ == "__main__":
    print("🚀 Starting Comprehensive System Evaluation...")
    evaluator = SystemEvaluator()
    evaluator.generate_final_report()