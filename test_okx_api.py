#!/usr/bin/env python3
"""Test OKX API connection with real credentials"""

import os
import requests
import hmac
import hashlib
import base64
from datetime import datetime, timezone

def test_okx_connection():
    api_key = os.getenv('OKX_API_KEY')
    secret_key = os.getenv('OKX_SECRET_KEY')
    passphrase = os.getenv('OKX_PASSPHRASE')
    
    if not all([api_key, secret_key, passphrase]):
        print("Missing OKX credentials")
        return False
    
    # Test public endpoint first (no auth required)
    public_url = "https://www.okx.com/api/v5/market/candles"
    params = {
        'instId': 'BTC-USDT',
        'bar': '1H',
        'limit': '10'
    }
    
    try:
        print(f"Testing public endpoint: {public_url}")
        response = requests.get(public_url, params=params, timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0' and data.get('data'):
                print("✓ Public API working correctly")
                print(f"Got {len(data['data'])} candles")
                return True
            else:
                print(f"API returned error: {data}")
                return False
        else:
            print(f"HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error testing public API: {e}")
        return False

if __name__ == "__main__":
    test_okx_connection()