#!/usr/bin/env python3
"""
Quick Weakness Testing - Focused on critical issues
"""

import requests
import json
from datetime import datetime

def test_critical_issues():
    """Test critical issues quickly"""
    base_url = 'http://localhost:5000'
    issues = []
    
    print("🔍 Testing Critical Application Issues...")
    
    # Test 1: Missing Templates
    print("\n1. Testing Missing Templates...")
    pages_to_test = [
        '/advanced-analysis',
        '/analysis-history',
        '/professional-dashboard',
        '/phase2-dashboard'
    ]
    
    for page in pages_to_test:
        try:
            response = requests.get(f"{base_url}{page}", timeout=5)
            if response.status_code == 500:
                issues.append({
                    'severity': 'CRITICAL',
                    'component': 'Templates',
                    'issue': f'Missing template for {page}',
                    'details': 'Template file not found'
                })
                print(f"  ❌ {page}: Missing template (500 error)")
            elif response.status_code == 200:
                print(f"  ✅ {page}: OK")
            else:
                print(f"  ⚠️  {page}: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ {page}: Error - {e}")
    
    # Test 2: API Endpoint Issues  
    print("\n2. Testing API Endpoints...")
    api_endpoints = [
        '/api/candles?symbol=BTC-USDT&interval=1h&limit=100',
        '/api/analyze/BTC-USDT',
        '/api/snapshot/BTC-USDT',
        '/health'
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {endpoint}: OK")
                # Check response structure
                if 'application/json' in response.headers.get('content-type', ''):
                    try:
                        data = response.json()
                        if isinstance(data, dict) and data.get('error'):
                            issues.append({
                                'severity': 'HIGH',
                                'component': 'API',
                                'issue': f'API returns error: {endpoint}',
                                'details': data.get('error')
                            })
                            print(f"    ⚠️  Contains error: {data.get('error')}")
                    except json.JSONDecodeError:
                        issues.append({
                            'severity': 'HIGH',
                            'component': 'API',
                            'issue': f'Invalid JSON response: {endpoint}',
                            'details': 'Response claims JSON but is not parseable'
                        })
            else:
                issues.append({
                    'severity': 'HIGH',
                    'component': 'API',
                    'issue': f'API endpoint failed: {endpoint}',
                    'details': f'Status code: {response.status_code}'
                })
                print(f"  ❌ {endpoint}: Status {response.status_code}")
        except Exception as e:
            issues.append({
                'severity': 'HIGH',
                'component': 'API',
                'issue': f'API endpoint error: {endpoint}',
                'details': str(e)
            })
            print(f"  ❌ {endpoint}: Error - {e}")
    
    # Test 3: Check main dashboard
    print("\n3. Testing Main Dashboard...")
    try:
        response = requests.get(f"{base_url}/react-dashboard", timeout=5)
        if response.status_code == 200:
            print("  ✅ React Dashboard: OK")
            # Check if content is suspiciously small
            if len(response.content) < 5000:
                issues.append({
                    'severity': 'MEDIUM',
                    'component': 'Frontend',
                    'issue': 'React dashboard content too small',
                    'details': f'Content size: {len(response.content)} bytes'
                })
        else:
            issues.append({
                'severity': 'CRITICAL',
                'component': 'Frontend',
                'issue': 'React dashboard not loading',
                'details': f'Status: {response.status_code}'
            })
    except Exception as e:
        issues.append({
            'severity': 'CRITICAL',
            'component': 'Frontend',
            'issue': 'React dashboard error',
            'details': str(e)
        })
    
    # Test 4: Check Chart Data
    print("\n4. Testing Chart Data Quality...")
    try:
        response = requests.get(f"{base_url}/api/candles?symbol=BTC-USDT&interval=1h&limit=50", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('candles'):
                candles = data['candles']
                print(f"  ✅ Chart Data: {len(candles)} candles received")
                
                # Check data integrity
                for i, candle in enumerate(candles[:5]):
                    if candle['high'] < candle['low']:
                        issues.append({
                            'severity': 'CRITICAL',
                            'component': 'Chart Data',
                            'issue': f'Invalid OHLC data at index {i}',
                            'details': f'High ({candle["high"]}) < Low ({candle["low"]})'
                        })
            else:
                issues.append({
                    'severity': 'HIGH',
                    'component': 'Chart Data',
                    'issue': 'No candle data returned',
                    'details': 'API returns no candles'
                })
    except Exception as e:
        issues.append({
            'severity': 'HIGH',
            'component': 'Chart Data',
            'issue': 'Chart data error',
            'details': str(e)
        })
    
    return issues

def check_frontend_errors():
    """Check for frontend-specific issues"""
    print("\n5. Frontend-Specific Issues Analysis...")
    
    frontend_issues = [
        {
            'severity': 'HIGH',
            'component': 'Frontend Production',
            'issue': 'Using CDN Tailwind CSS in production',
            'details': 'Should use PostCSS plugin or Tailwind CLI for production'
        },
        {
            'severity': 'MEDIUM',
            'component': 'Frontend Build',
            'issue': 'Using in-browser Babel transformer',
            'details': 'Should precompile scripts for production'
        },
        {
            'severity': 'MEDIUM',
            'component': 'React Version',
            'issue': 'Using deprecated ReactDOM.render',
            'details': 'Should use createRoot for React 18'
        }
    ]
    
    for issue in frontend_issues:
        print(f"  ⚠️  {issue['component']}: {issue['issue']}")
    
    return frontend_issues

def generate_weakness_report(issues):
    """Generate focused weakness report"""
    print("\n" + "="*80)
    print("🔍 APLIKASI WEAKNESS REPORT")
    print("="*80)
    
    # Group by severity
    critical = [i for i in issues if i['severity'] == 'CRITICAL']
    high = [i for i in issues if i['severity'] == 'HIGH']
    medium = [i for i in issues if i['severity'] == 'MEDIUM']
    
    print(f"\n📊 SUMMARY:")
    print(f"Total Issues Found: {len(issues)}")
    print(f"Critical: {len(critical)}")
    print(f"High: {len(high)}")
    print(f"Medium: {len(medium)}")
    
    if critical:
        print(f"\n🚨 CRITICAL ISSUES (MUST FIX IMMEDIATELY):")
        for i, issue in enumerate(critical, 1):
            print(f"{i}. {issue['component']}: {issue['issue']}")
            if issue['details']:
                print(f"   Details: {issue['details']}")
    
    if high:
        print(f"\n🔴 HIGH PRIORITY ISSUES:")
        for i, issue in enumerate(high, 1):
            print(f"{i}. {issue['component']}: {issue['issue']}")
            if issue['details']:
                print(f"   Details: {issue['details']}")
    
    if medium:
        print(f"\n🟡 MEDIUM PRIORITY ISSUES:")
        for i, issue in enumerate(medium, 1):
            print(f"{i}. {issue['component']}: {issue['issue']}")
            if issue['details']:
                print(f"   Details: {issue['details']}")
    
    # Recommendations
    print(f"\n💡 IMMEDIATE ACTIONS NEEDED:")
    if critical:
        print("  1. Fix missing template files immediately")
        print("  2. Resolve any API endpoint failures")
        print("  3. Fix data integrity issues in charts")
    
    if high:
        print("  4. Review all API error responses")
        print("  5. Test all frontend pages for proper loading")
    
    if medium:
        print("  6. Upgrade to production-ready frontend build")
        print("  7. Update React implementation to use createRoot")
    
    print("\n" + "="*80)
    
    return {
        'total_issues': len(issues),
        'critical': len(critical),
        'high': len(high),
        'medium': len(medium),
        'issues': issues
    }

def main():
    """Main function"""
    print("🚀 Quick Weakness Testing - Crypto Trading Dashboard")
    
    # Test critical issues
    issues = test_critical_issues()
    
    # Add frontend issues
    frontend_issues = check_frontend_errors()
    issues.extend(frontend_issues)
    
    # Generate report
    report = generate_weakness_report(issues)
    
    # Save to file
    with open('weakness_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: weakness_report.json")
    
    return report

if __name__ == "__main__":
    main()