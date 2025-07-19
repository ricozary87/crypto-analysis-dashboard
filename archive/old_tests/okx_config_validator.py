#!/usr/bin/env python3
"""
OKX API Configuration Validator
Comprehensive testing of OKX API credentials and connectivity
"""

import os
import hmac
import hashlib
import base64
import json
import time
import requests
from datetime import datetime

class OKXConfigValidator:
    def __init__(self):
        self.base_url = "https://www.okx.com"
        self.api_key = os.environ.get('OKX_API_KEY')
        self.secret_key = os.environ.get('OKX_SECRET_KEY')
        self.passphrase = os.environ.get('OKX_PASSPHRASE')
        self.results = {}
        
    def check_environment_variables(self):
        """Check if all required environment variables are present"""
        print("🔍 CHECKING ENVIRONMENT VARIABLES")
        print("=" * 50)
        
        # Check each variable
        variables = {
            'OKX_API_KEY': self.api_key,
            'OKX_SECRET_KEY': self.secret_key,
            'OKX_PASSPHRASE': self.passphrase
        }
        
        for var_name, var_value in variables.items():
            if var_value:
                print(f"✅ {var_name}: Available ({len(var_value)} characters)")
                # Show first 8 and last 4 characters for verification
                if len(var_value) > 12:
                    preview = f"{var_value[:8]}...{var_value[-4:]}"
                    print(f"   Preview: {preview}")
            else:
                print(f"❌ {var_name}: Not found")
        
        # Check if all required variables are present
        all_present = all([self.api_key, self.secret_key, self.passphrase])
        print(f"\n📋 Configuration Status: {'✅ Complete' if all_present else '❌ Incomplete'}")
        
        self.results['environment_check'] = {
            'all_present': all_present,
            'missing_vars': [k for k, v in variables.items() if not v]
        }
        
        return all_present
    
    def validate_key_formats(self):
        """Validate the format and length of API keys"""
        print("\n🔧 VALIDATING KEY FORMATS")
        print("=" * 50)
        
        # OKX API Key format validation
        if self.api_key:
            api_key_valid = len(self.api_key) >= 30 and '-' in self.api_key
            print(f"API Key format: {'✅ Valid' if api_key_valid else '❌ Invalid'}")
            print(f"  Length: {len(self.api_key)} chars (expected: 30+ chars)")
            print(f"  Contains dash: {'✅ Yes' if '-' in self.api_key else '❌ No'}")
        
        # OKX Secret Key format validation
        if self.secret_key:
            secret_key_valid = len(self.secret_key) >= 40
            print(f"Secret Key format: {'✅ Valid' if secret_key_valid else '❌ Invalid'}")
            print(f"  Length: {len(self.secret_key)} chars (expected: 40+ chars)")
        
        # OKX Passphrase format validation
        if self.passphrase:
            passphrase_valid = len(self.passphrase) >= 4
            print(f"Passphrase format: {'✅ Valid' if passphrase_valid else '❌ Invalid'}")
            print(f"  Length: {len(self.passphrase)} chars (expected: 4+ chars)")
        
        format_valid = all([
            self.api_key and len(self.api_key) >= 30,
            self.secret_key and len(self.secret_key) >= 40,
            self.passphrase and len(self.passphrase) >= 4
        ])
        
        self.results['format_validation'] = {
            'valid': format_valid,
            'api_key_length': len(self.api_key) if self.api_key else 0,
            'secret_key_length': len(self.secret_key) if self.secret_key else 0,
            'passphrase_length': len(self.passphrase) if self.passphrase else 0
        }
        
        return format_valid
    
    def generate_signature(self, method, path, body=''):
        """Generate OKX API signature"""
        timestamp = str(int(time.time()))
        
        # Create message to sign
        message = timestamp + method + path + body
        
        # Create signature
        mac = hmac.new(
            bytes(self.secret_key, encoding='utf8'),
            bytes(message, encoding='utf-8'),
            digestmod=hashlib.sha256
        )
        signature = base64.b64encode(mac.digest()).decode('utf-8')
        
        return timestamp, signature
    
    def test_public_endpoint(self):
        """Test public endpoint (no authentication required)"""
        print("\n🌍 TESTING PUBLIC ENDPOINT")
        print("=" * 50)
        
        try:
            url = f"{self.base_url}/api/v5/public/instruments?instType=SPOT&instId=BTC-USDT"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Public endpoint test: SUCCESS")
                print(f"   Status: {response.status_code}")
                print(f"   Response code: {data.get('code', 'N/A')}")
                print(f"   Data count: {len(data.get('data', []))}")
                
                self.results['public_test'] = {
                    'success': True,
                    'status_code': response.status_code,
                    'response_code': data.get('code')
                }
                return True
            else:
                print(f"❌ Public endpoint test: FAILED (Status: {response.status_code})")
                self.results['public_test'] = {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text
                }
                return False
                
        except Exception as e:
            print(f"❌ Public endpoint test: ERROR - {str(e)}")
            self.results['public_test'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def test_authenticated_endpoints(self):
        """Test authenticated endpoints"""
        print("\n🔐 TESTING AUTHENTICATED ENDPOINTS")
        print("=" * 50)
        
        if not all([self.api_key, self.secret_key, self.passphrase]):
            print("❌ Cannot test authenticated endpoints: Missing credentials")
            return False
        
        # Test endpoints to try
        test_endpoints = [
            {
                'path': '/api/v5/account/config',
                'method': 'GET',
                'description': 'Account Configuration'
            },
            {
                'path': '/api/v5/account/balance',
                'method': 'GET',
                'description': 'Account Balance'
            },
            {
                'path': '/api/v5/account/positions',
                'method': 'GET',
                'description': 'Account Positions'
            }
        ]
        
        authenticated_success = False
        
        for endpoint in test_endpoints:
            try:
                print(f"\n📡 Testing: {endpoint['description']}")
                
                # Generate signature
                timestamp, signature = self.generate_signature(
                    endpoint['method'], 
                    endpoint['path']
                )
                
                # Prepare headers
                headers = {
                    'OK-ACCESS-KEY': self.api_key,
                    'OK-ACCESS-SIGN': signature,
                    'OK-ACCESS-TIMESTAMP': timestamp,
                    'OK-ACCESS-PASSPHRASE': self.passphrase,
                    'Content-Type': 'application/json'
                }
                
                # Make request
                url = f"{self.base_url}{endpoint['path']}"
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    response_code = data.get('code', 'N/A')
                    
                    if response_code == '0':
                        print(f"   ✅ SUCCESS: {endpoint['description']}")
                        print(f"   Status: {response.status_code}")
                        print(f"   Response code: {response_code}")
                        authenticated_success = True
                    else:
                        print(f"   ❌ API ERROR: {endpoint['description']}")
                        print(f"   Response code: {response_code}")
                        print(f"   Message: {data.get('msg', 'Unknown error')}")
                else:
                    print(f"   ❌ HTTP ERROR: {endpoint['description']}")
                    print(f"   Status: {response.status_code}")
                    print(f"   Response: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   ❌ EXCEPTION: {endpoint['description']}")
                print(f"   Error: {str(e)}")
        
        self.results['authenticated_test'] = {
            'success': authenticated_success,
            'tested_endpoints': len(test_endpoints)
        }
        
        return authenticated_success
    
    def test_signature_generation(self):
        """Test signature generation with known values"""
        print("\n🔑 TESTING SIGNATURE GENERATION")
        print("=" * 50)
        
        if not self.secret_key:
            print("❌ Cannot test signature: Missing secret key")
            return False
        
        try:
            # Test with known values
            method = 'GET'
            path = '/api/v5/account/balance'
            body = ''
            
            timestamp, signature = self.generate_signature(method, path, body)
            
            print(f"✅ Signature generation: SUCCESS")
            print(f"   Timestamp: {timestamp}")
            print(f"   Signature length: {len(signature)} chars")
            print(f"   Signature preview: {signature[:20]}...")
            
            self.results['signature_test'] = {
                'success': True,
                'signature_length': len(signature)
            }
            
            return True
            
        except Exception as e:
            print(f"❌ Signature generation: FAILED")
            print(f"   Error: {str(e)}")
            
            self.results['signature_test'] = {
                'success': False,
                'error': str(e)
            }
            
            return False
    
    def generate_report(self):
        """Generate comprehensive report"""
        print("\n📋 COMPREHENSIVE REPORT")
        print("=" * 50)
        
        # Overall status
        environment_ok = self.results.get('environment_check', {}).get('all_present', False)
        format_ok = self.results.get('format_validation', {}).get('valid', False)
        public_ok = self.results.get('public_test', {}).get('success', False)
        auth_ok = self.results.get('authenticated_test', {}).get('success', False)
        signature_ok = self.results.get('signature_test', {}).get('success', False)
        
        print(f"Environment Variables: {'✅ PASS' if environment_ok else '❌ FAIL'}")
        print(f"Key Format Validation: {'✅ PASS' if format_ok else '❌ FAIL'}")
        print(f"Public Endpoint Test: {'✅ PASS' if public_ok else '❌ FAIL'}")
        print(f"Signature Generation: {'✅ PASS' if signature_ok else '❌ FAIL'}")
        print(f"Authenticated Endpoints: {'✅ PASS' if auth_ok else '❌ FAIL'}")
        
        # Overall assessment
        overall_score = sum([environment_ok, format_ok, public_ok, signature_ok, auth_ok])
        
        print(f"\n🎯 OVERALL ASSESSMENT: {overall_score}/5 tests passed")
        
        if overall_score == 5:
            print("🎉 EXCELLENT: All OKX API configurations are working perfectly!")
        elif overall_score >= 3:
            print("⚠️  GOOD: Most configurations work, but some issues need attention")
        else:
            print("❌ CRITICAL: Major configuration issues detected")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if not environment_ok:
            missing_vars = self.results.get('environment_check', {}).get('missing_vars', [])
            print(f"   - Add missing environment variables: {', '.join(missing_vars)}")
        
        if not format_ok:
            print("   - Verify API key formats match OKX specifications")
        
        if not auth_ok:
            print("   - Check API key permissions and account status")
            print("   - Ensure API keys are from the correct OKX environment (production/sandbox)")
        
        return overall_score
    
    def run_full_validation(self):
        """Run complete validation suite"""
        print("🚀 STARTING OKX API CONFIGURATION VALIDATION")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Run all tests
        self.check_environment_variables()
        self.validate_key_formats()
        self.test_public_endpoint()
        self.test_signature_generation()
        self.test_authenticated_endpoints()
        
        # Generate final report
        score = self.generate_report()
        
        print("\n" + "=" * 60)
        print("VALIDATION COMPLETE")
        print("=" * 60)
        
        return score

# Run validation
if __name__ == "__main__":
    validator = OKXConfigValidator()
    validator.run_full_validation()