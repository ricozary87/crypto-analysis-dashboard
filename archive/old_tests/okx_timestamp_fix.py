#!/usr/bin/env python3
"""
OKX API Timestamp Fix and Authentication Test
"""

import os
import hmac
import hashlib
import base64
import json
import time
import requests
from datetime import datetime, timezone

def get_okx_timestamp():
    """Get proper OKX timestamp in ISO format"""
    # OKX expects timestamp in ISO format with milliseconds
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def generate_okx_signature(method, path, body=''):
    """Generate OKX signature with proper timestamp format"""
    
    # Get credentials
    secret_key = os.environ.get('OKX_SECRET_KEY')
    if not secret_key:
        raise ValueError("OKX_SECRET_KEY not found")
    
    # Generate timestamp in correct format
    timestamp = get_okx_timestamp()
    
    # Create message to sign
    message = timestamp + method + path + body
    print(f"Message to sign: {message}")
    
    # Create signature
    mac = hmac.new(
        bytes(secret_key, encoding='utf8'),
        bytes(message, encoding='utf-8'),
        digestmod=hashlib.sha256
    )
    signature = base64.b64encode(mac.digest()).decode('utf-8')
    
    return timestamp, signature

def test_authenticated_request():
    """Test authenticated request with proper timestamp"""
    
    # Get credentials
    api_key = os.environ.get('OKX_API_KEY')
    secret_key = os.environ.get('OKX_SECRET_KEY')
    passphrase = os.environ.get('OKX_PASSPHRASE')
    
    if not all([api_key, secret_key, passphrase]):
        print("❌ Missing credentials")
        return False
    
    print("🔐 TESTING AUTHENTICATED REQUEST WITH FIXED TIMESTAMP")
    print("=" * 60)
    
    try:
        # Test endpoint
        method = 'GET'
        path = '/api/v5/account/config'
        
        # Generate signature with proper timestamp
        timestamp, signature = generate_okx_signature(method, path)
        
        print(f"Timestamp: {timestamp}")
        print(f"Signature: {signature[:20]}...")
        
        # Prepare headers
        headers = {
            'OK-ACCESS-KEY': api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': passphrase,
            'Content-Type': 'application/json'
        }
        
        # Make request
        url = f"https://www.okx.com{path}"
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Code: {data.get('code', 'N/A')}")
            print(f"Response Message: {data.get('msg', 'N/A')}")
            
            if data.get('code') == '0':
                print("✅ SUCCESS: Authentication working!")
                return True
            else:
                print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_unix_timestamp():
    """Test with Unix timestamp format"""
    
    print("\n🔄 TESTING WITH UNIX TIMESTAMP")
    print("=" * 60)
    
    # Get credentials
    api_key = os.environ.get('OKX_API_KEY')
    secret_key = os.environ.get('OKX_SECRET_KEY')
    passphrase = os.environ.get('OKX_PASSPHRASE')
    
    try:
        method = 'GET'
        path = '/api/v5/account/config'
        
        # Use Unix timestamp with milliseconds
        timestamp = str(int(time.time() * 1000))
        
        # Create message to sign
        message = timestamp + method + path
        
        # Create signature
        mac = hmac.new(
            bytes(secret_key, encoding='utf8'),
            bytes(message, encoding='utf-8'),
            digestmod=hashlib.sha256
        )
        signature = base64.b64encode(mac.digest()).decode('utf-8')
        
        print(f"Unix Timestamp: {timestamp}")
        print(f"Signature: {signature[:20]}...")
        
        # Prepare headers
        headers = {
            'OK-ACCESS-KEY': api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': passphrase,
            'Content-Type': 'application/json'
        }
        
        # Make request
        url = f"https://www.okx.com{path}"
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Code: {data.get('code', 'N/A')}")
            
            if data.get('code') == '0':
                print("✅ SUCCESS: Unix timestamp working!")
                return True
            else:
                print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def check_secret_key_validity():
    """Check if secret key is valid by attempting to decode it"""
    
    print("\n🔍 CHECKING SECRET KEY VALIDITY")
    print("=" * 60)
    
    secret_key = os.environ.get('OKX_SECRET_KEY')
    
    if not secret_key:
        print("❌ Secret key not found")
        return False
    
    print(f"Secret key length: {len(secret_key)} characters")
    print(f"Secret key preview: {secret_key[:8]}...{secret_key[-4:]}")
    
    # Check if it's base64 encoded
    try:
        decoded = base64.b64decode(secret_key)
        print(f"✅ Can decode as base64: {len(decoded)} bytes")
        return True
    except Exception as e:
        print(f"❌ Cannot decode as base64: {str(e)}")
        # This is actually normal - OKX secret keys are usually not base64 encoded
        print("ℹ️  This is normal - OKX secret keys are typically plain text")
        return True

if __name__ == "__main__":
    print("🚀 OKX TIMESTAMP FIX AND AUTHENTICATION TEST")
    print("=" * 60)
    
    # Check secret key validity
    check_secret_key_validity()
    
    # Test with ISO timestamp
    success_iso = test_authenticated_request()
    
    # Test with Unix timestamp
    success_unix = test_unix_timestamp()
    
    print(f"\n📋 SUMMARY:")
    print(f"ISO Timestamp: {'✅ SUCCESS' if success_iso else '❌ FAILED'}")
    print(f"Unix Timestamp: {'✅ SUCCESS' if success_unix else '❌ FAILED'}")
    
    if success_iso or success_unix:
        print("🎉 Authentication is working with at least one timestamp format!")
    else:
        print("❌ Authentication failed with both timestamp formats")
        print("💡 Recommendation: Check if OKX_SECRET_KEY is complete and correct")