#!/usr/bin/env python3
"""
Simple VPS Deployment Test Script
Quick functional test to verify application readiness
"""

import os
import sys
import time
import subprocess
import signal
import requests
from datetime import datetime

# Force SQLite for testing
os.environ.pop("DATABASE_URL", None)

def test_basic_functionality():
    """Test basic app functionality"""
    print("🔍 1. Testing Basic Functionality...")
    
    try:
        sys.path.append('.')
        from app import app, db, init_scheduler
        with app.app_context():
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1')).fetchone()
            
        scheduler = init_scheduler()
        time.sleep(1)
        
        print("✅ Basic functionality working")
        return True
    except Exception as e:
        print(f"❌ Basic functionality failed: {e}")
        return False

def test_server_startup():
    """Test server startup with both methods"""
    print("\n🚀 2. Testing Server Startup Methods...")
    
    # Test 1: Python main.py
    print("   Testing: python main.py")
    try:
        env = os.environ.copy()
        env.pop("DATABASE_URL", None)
        
        proc = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            preexec_fn=os.setsid
        )
        
        time.sleep(5)
        
        if proc.poll() is None:
            print("   ✅ main.py startup successful")
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=5)
            main_success = True
        else:
            stdout, stderr = proc.communicate()
            print(f"   ❌ main.py failed: {stderr.decode()[:200]}")
            main_success = False
            
    except Exception as e:
        print(f"   ❌ main.py test error: {e}")
        main_success = False
    
    # Test 2: Gunicorn
    print("   Testing: gunicorn wsgi:application")
    try:
        env = os.environ.copy()
        env.pop("DATABASE_URL", None)
        
        proc = subprocess.Popen(
            ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8001", "--timeout", "10"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            preexec_fn=os.setsid
        )
        
        time.sleep(5)
        
        if proc.poll() is None:
            print("   ✅ gunicorn startup successful")
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=5)
            gunicorn_success = True
        else:
            stdout, stderr = proc.communicate()
            print(f"   ❌ gunicorn failed: {stderr.decode()[:200]}")
            gunicorn_success = False
            
    except Exception as e:
        print(f"   ❌ gunicorn test error: {e}")
        gunicorn_success = False
    
    if main_success and gunicorn_success:
        print("✅ Both startup methods working")
        return True
    elif main_success or gunicorn_success:
        print("⚠️  One startup method working")
        return True
    else:
        print("❌ Both startup methods failed")
        return False

def test_requirements():
    """Test requirements.txt completeness"""
    print("\n📦 3. Testing Requirements...")
    
    missing_deps = []
    required_modules = [
        'flask', 'flask_sqlalchemy', 'flask_socketio', 'flask_cors',
        'apscheduler', 'gunicorn', 'pandas', 'numpy', 'requests',
        'psycopg2', 'sqlalchemy', 'werkzeug', 'openai', 'prometheus_client'
    ]
    
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
        except ImportError:
            missing_deps.append(module)
    
    if not missing_deps:
        print("✅ All required dependencies available")
        return True
    else:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        return False

def test_files_exist():
    """Test critical files exist"""
    print("\n📁 4. Testing Critical Files...")
    
    required_files = [
        'app.py', 'main.py', 'wsgi.py', 'requirements.txt',
        'myapp.service', 'install-myapp-service.sh'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if not missing_files:
        print("✅ All critical files present")
        return True
    else:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False

def generate_vps_commands():
    """Generate VPS deployment commands"""
    print("\n📋 VPS Deployment Commands:")
    print("=" * 50)
    
    commands = """
# 1. Copy aplikasi ke VPS
scp -r * user@your-vps:/home/user/myapp/

# 2. SSH ke VPS
ssh user@your-vps

# 3. Setup virtual environment
cd /home/user/myapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
nano .env  # Edit dengan API keys

# 5. Install sebagai systemd service
sudo ./install-myapp-service.sh

# 6. Start service
sudo systemctl start myapp

# 7. Check status dan logs
sudo systemctl status myapp
sudo journalctl -fu myapp
"""
    
    print(commands)

def main():
    """Run all tests"""
    print("🚀 VPS DEPLOYMENT READINESS TEST")
    print("=" * 50)
    
    tests = [
        test_basic_functionality,
        test_server_startup,  
        test_requirements,
        test_files_exist
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test error: {e}")
            results.append(False)
        time.sleep(1)
    
    # Generate report
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results)
    
    print(f"📈 Tests Passed: {passed_tests}/{total_tests}")
    print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("✅ APPLICATION READY FOR VPS DEPLOYMENT!")
    elif passed_tests >= 3:
        print("⚠️  APPLICATION MOSTLY READY - Minor issues to fix")
    else:
        print("❌ APPLICATION NOT READY - Critical issues found")
    
    generate_vps_commands()
    
    return passed_tests >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)