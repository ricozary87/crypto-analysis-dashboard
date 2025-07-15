#!/usr/bin/env python3
"""
Simple OKX API test to isolate the timestamp issue
"""

import sys
import logging
from okx_service import OKXService
from database_service import DatabaseService
from smc_analyzer import SMCAnalyzer
from app import app

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_okx_direct():
    """Test OKX service directly"""
    print("🔍 Testing OKX Service directly...")
    
    try:
        okx = OKXService()
        data = okx.get_candlestick_data('SOL-USDT', '1h', 10)
        
        if data:
            print(f"✅ OKX direct test SUCCESS: Got {len(data)} candles")
            print(f"First candle: {data[0]}")
            print(f"Timestamp type: {type(data[0]['timestamp'])}")
            return data
        else:
            print("❌ OKX direct test FAILED: No data returned")
            return None
            
    except Exception as e:
        print(f"❌ OKX direct test FAILED: {str(e)}")
        return None

def test_smc_analyzer(data):
    """Test SMC Analyzer with the data"""
    print("\n🔍 Testing SMC Analyzer...")
    
    try:
        smc = SMCAnalyzer()
        
        # Test swing point identification
        swing_points = smc.identify_swing_points(data)
        print(f"✅ SMC swing points SUCCESS: {len(swing_points['swing_highs'])} highs, {len(swing_points['swing_lows'])} lows")
        
        # Test CHoCH/BOS detection
        choch_bos = smc.detect_choch_bos(data, swing_points)
        print(f"✅ SMC CHoCH/BOS SUCCESS: {len(choch_bos)} signals")
        
        return True
        
    except Exception as e:
        print(f"❌ SMC Analyzer test FAILED: {str(e)}")
        return False

def test_database_service(data):
    """Test database service with the data"""
    print("\n🔍 Testing Database Service...")
    
    try:
        with app.app_context():
            db = DatabaseService()
            
            # Test saving data
            success = db.save_market_data('SOL-USDT', '1h', data)
            if success:
                print("✅ Database save SUCCESS")
            else:
                print("❌ Database save FAILED")
                return False
            
            # Test retrieving data
            retrieved_data = db.get_market_data('SOL-USDT', '1h', 10)
            if retrieved_data:
                print(f"✅ Database retrieve SUCCESS: Got {len(retrieved_data)} candles")
                print(f"Retrieved timestamp type: {type(retrieved_data[0]['timestamp'])}")
                
                # Test mixing data types
                mixed_data = data + retrieved_data
                print(f"Mixed data length: {len(mixed_data)}")
                
                # Test if sorting mixed data works
                try:
                    mixed_data.sort(key=lambda x: x['timestamp'])
                    print("✅ Mixed data sorting SUCCESS")
                except Exception as e:
                    print(f"❌ Mixed data sorting FAILED: {str(e)}")
                    return False
                    
            else:
                print("❌ Database retrieve FAILED")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Database service test FAILED: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Simple OKX Test")
    print("=" * 50)
    
    # Test 1: OKX Direct
    data = test_okx_direct()
    if not data:
        print("❌ Cannot proceed without OKX data")
        return
    
    # Test 2: SMC Analyzer
    smc_success = test_smc_analyzer(data)
    
    # Test 3: Database Service
    db_success = test_database_service(data)
    
    print("\n" + "=" * 50)
    print("🏁 Test Results:")
    print(f"OKX Direct: {'✅ PASS' if data else '❌ FAIL'}")
    print(f"SMC Analyzer: {'✅ PASS' if smc_success else '❌ FAIL'}")
    print(f"Database Service: {'✅ PASS' if db_success else '❌ FAIL'}")
    
    if data and smc_success and db_success:
        print("\n🎉 All tests PASSED!")
    else:
        print("\n🚨 Some tests FAILED!")

if __name__ == "__main__":
    main()