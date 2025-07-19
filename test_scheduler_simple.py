#!/usr/bin/env python3
"""
Simple test untuk memverifikasi APScheduler fix tanpa import module lain yang bermasalah
"""
import os
import sys
import time

def test_scheduler_fix():
    """Test scheduler fix dengan import minimal"""
    print("🧪 Testing APScheduler Fix...")
    
    # Set environment untuk SQLite fallback
    os.environ["DATABASE_URL"] = "sqlite:///test_scheduler.db"
    
    try:
        # Import hanya yang diperlukan
        sys.path.insert(0, '.')
        
        # Check apakah scheduler variable ada
        from app import scheduler
        print(f"📊 Initial scheduler state: {scheduler}")
        
        # Test init scheduler function
        from app import init_scheduler
        
        # Initialize scheduler
        test_scheduler = init_scheduler()
        print(f"📊 After init scheduler: {test_scheduler}")
        
        if test_scheduler and test_scheduler.running:
            print("✅ Scheduler initialized and running")
            
            # Test init ulang
            test_scheduler2 = init_scheduler()
            if test_scheduler is test_scheduler2:
                print("✅ Scheduler reuse working - tidak ada duplikasi")
                return True
            else:
                print("❌ Multiple schedulers detected")
                return False
        else:
            print("❌ Scheduler tidak running")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        try:
            if 'test_scheduler' in locals() and test_scheduler:
                test_scheduler.shutdown()
                print("🧹 Test scheduler cleaned up")
        except:
            pass

def test_main_py():
    """Test entry point main.py"""
    print("\n🧪 Testing main.py entry point...")
    
    try:
        # Read main.py content
        with open("main.py", "r") as f:
            content = f.read()
        
        if "init_scheduler()" in content:
            print("✅ main.py calls init_scheduler()")
        else:
            print("❌ main.py tidak call init_scheduler()")
            return False
            
        if "__name__ == '__main__'" in content:
            print("✅ main.py has proper entry point")
            return True
        else:
            print("❌ main.py tidak ada proper entry point")
            return False
    except Exception as e:
        print(f"❌ main.py test failed: {e}")
        return False

def test_wsgi_py():
    """Test WSGI entry point"""
    print("\n🧪 Testing wsgi.py entry point...")
    
    try:
        # Read wsgi.py content
        with open("wsgi.py", "r") as f:
            content = f.read()
        
        if "init_scheduler()" in content:
            print("✅ wsgi.py calls init_scheduler()")
            return True
        else:
            print("❌ wsgi.py tidak call init_scheduler()")
            return False
    except Exception as e:
        print(f"❌ wsgi.py test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 APScheduler Simple Fix Test")
    print("=" * 40)
    
    tests = [
        ("Scheduler Fix", test_scheduler_fix),
        ("main.py Entry", test_main_py),
        ("wsgi.py Entry", test_wsgi_py)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 APScheduler fix berhasil!")
    else:
        print("❌ Ada masalah yang perlu diperbaiki")
        
    sys.exit(0 if passed == len(tests) else 1)