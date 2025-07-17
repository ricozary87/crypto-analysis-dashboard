#!/usr/bin/env python3
"""
Test OKX authenticated endpoints with updated fetcher
"""

import sys
import os
sys.path.append('.')

from core.okx_fetcher import OKXAPIManager
import json

def test_okx_authenticated_endpoints():
    """Test all authenticated endpoints"""
    print("🔐 TESTING OKX AUTHENTICATED ENDPOINTS")
    print("=" * 50)
    
    # Initialize OKX API manager
    okx = OKXAPIManager()
    
    # Check if credentials are available
    if not okx.has_credentials:
        print("❌ No credentials available for testing")
        return False
    
    print("✅ Credentials loaded successfully")
    
    # Test 1: Authentication test
    print("\n1. Testing Authentication...")
    auth_success = okx.test_authentication()
    print(f"   Authentication: {'✅ SUCCESS' if auth_success else '❌ FAILED'}")
    
    if not auth_success:
        print("   Cannot proceed with other tests")
        return False
    
    # Test 2: Account Balance
    print("\n2. Testing Account Balance...")
    try:
        balance = okx.get_account_balance()
        if balance:
            print("   ✅ Account balance retrieved successfully")
            print(f"   Available balance details: {len(balance.get('details', []))} currencies")
            if balance.get('details'):
                # Show first currency balance
                first_currency = balance['details'][0]
                print(f"   Sample: {first_currency.get('ccy', 'N/A')} - Available: {first_currency.get('availBal', 'N/A')}")
        else:
            print("   ❌ Failed to retrieve account balance")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 3: Account Config
    print("\n3. Testing Account Configuration...")
    try:
        config = okx.get_account_config()
        if config:
            print("   ✅ Account configuration retrieved successfully")
            print(f"   Account level: {config.get('acctLv', 'N/A')}")
            print(f"   Position mode: {config.get('posMode', 'N/A')}")
            print(f"   Account role: {config.get('roleType', 'N/A')}")
        else:
            print("   ❌ Failed to retrieve account configuration")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 4: Positions
    print("\n4. Testing Account Positions...")
    try:
        positions = okx.get_positions()
        if positions is not None:
            print(f"   ✅ Positions retrieved successfully: {len(positions)} positions")
            if positions:
                # Show first position
                first_pos = positions[0]
                print(f"   Sample position: {first_pos.get('instId', 'N/A')} - Size: {first_pos.get('pos', 'N/A')}")
            else:
                print("   No active positions found")
        else:
            print("   ❌ Failed to retrieve positions")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 5: Public endpoints (should still work)
    print("\n5. Testing Public Endpoints (for comparison)...")
    try:
        ticker = okx.get_ticker('BTC-USDT')
        if ticker:
            print("   ✅ Public ticker retrieved successfully")
            print(f"   BTC-USDT Last Price: {ticker.get('last', 'N/A')}")
        else:
            print("   ❌ Failed to retrieve ticker")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 OKX AUTHENTICATED ENDPOINTS TEST COMPLETE")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_okx_authenticated_endpoints()