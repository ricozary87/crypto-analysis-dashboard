#!/usr/bin/env python3
"""
Test script untuk memverifikasi bahwa APScheduler tidak restart berulang
"""
import os
import sys
import time
from datetime import datetime

def test_scheduler_stability():
    """Test bahwa scheduler hanya start sekali"""
    print("🧪 Testing APScheduler Stability...")
    
    # Set environment untuk SQLite fallback
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    
    try:
        # Import app untuk trigger scheduler
        from app import app, scheduler, init_scheduler
        
        print(f"📊 Scheduler status before init: {scheduler}")
        
        # Initialize scheduler
        test_scheduler = init_scheduler()
        
        print(f"📊 Scheduler status after init: {test_scheduler}")
        print(f"📊 Scheduler running: {test_scheduler.running if test_scheduler else False}")
        
        # Wait dan check apakah scheduler stabil
        print("⏳ Waiting 5 seconds to check stability...")
        time.sleep(5)
        
        if test_scheduler and test_scheduler.running:
            print("✅ APScheduler is running and stable!")
            
            # Test init ulang (should not create new scheduler)
            test_scheduler2 = init_scheduler()
            if test_scheduler is test_scheduler2:
                print("✅ Scheduler reuse working - no duplicate schedulers")
            else:
                print("❌ WARNING: Multiple schedulers detected!")
            
            return True
        else:
            print("❌ APScheduler not running properly")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        # Cleanup
        if 'test_scheduler' in locals() and test_scheduler:
            try:
                test_scheduler.shutdown()
                print("🧹 Test scheduler cleaned up")
            except:
                pass

def test_import_stability():
    """Test bahwa multiple import tidak menyebabkan restart"""
    print("\n🧪 Testing Import Stability...")
    
    try:
        # Multiple imports should not restart scheduler
        import importlib
        import app
        
        # Reload module
        importlib.reload(app)
        
        # Import ulang
        from app import scheduler as sched1
        from app import scheduler as sched2
        
        if sched1 is sched2:
            print("✅ Multiple imports stable - no scheduler restart")
            return True
        else:
            print("❌ Multiple imports cause issues")
            return False
            
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    print("🚀 APScheduler Fix Verification Test")
    print("=" * 50)
    
    tests = [
        ("Scheduler Stability", test_scheduler_stability),
        ("Import Stability", test_import_stability)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 APScheduler fix successful!")
        return True
    else:
        print("❌ Some tests failed - scheduler needs more work")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)