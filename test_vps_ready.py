#!/usr/bin/env python3
"""
VPS Readiness Test Script
Tests if the trading AI application is ready for VPS deployment
"""

import os
import sys
import time
import requests
import signal
import subprocess
import threading
from datetime import datetime

# Ensure SQLite fallback for testing
os.environ.pop("DATABASE_URL", None)

class VPSReadinessTest:
    def __init__(self):
        self.test_results = []
        self.server_process = None
        self.test_port = 5000
        
    def log_test(self, test_name, success, message=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        print(f"{status} | {test_name}: {message}")
        
    def test_dependencies(self):
        """Test 1: Check all dependencies can be imported"""
        print("\n🔍 Testing Dependencies...")
        try:
            # Core imports
            from app import app, socketio, init_scheduler, db
            import main
            import wsgi
            
            # Check critical imports
            import flask
            import flask_sqlalchemy
            import flask_socketio 
            import apscheduler
            import pandas
            import numpy
            import requests
            import gunicorn
            
            self.log_test("Dependencies Import", True, "All critical dependencies available")
            return True
        except ImportError as e:
            self.log_test("Dependencies Import", False, f"Missing dependency: {e}")
            return False
        except Exception as e:
            self.log_test("Dependencies Import", False, f"Import error: {e}")
            return False
    
    def test_database_connection(self):
        """Test 2: Check database connection and table creation"""
        print("\n🗄️ Testing Database Connection...")
        try:
            from app import app, db
            
            with app.app_context():
                # Test database connection
                db.engine.execute("SELECT 1").fetchone()
                
                # Check if tables exist
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                
                self.log_test("Database Connection", True, f"Connected to database, {len(tables)} tables created")
                return True
        except Exception as e:
            self.log_test("Database Connection", False, f"Database error: {e}")
            return False
    
    def test_scheduler_stability(self):
        """Test 3: Test APScheduler initialization and stability"""
        print("\n⏰ Testing APScheduler Stability...")
        try:
            from app import init_scheduler
            
            scheduler = init_scheduler()
            
            if scheduler and scheduler.running:
                time.sleep(2)  # Wait to ensure no restart loop
                
                if scheduler.running:
                    self.log_test("Scheduler Stability", True, "APScheduler running stable")
                    return True
                else:
                    self.log_test("Scheduler Stability", False, "Scheduler stopped unexpectedly")
                    return False
            else:
                self.log_test("Scheduler Stability", False, "Scheduler failed to start")
                return False
        except Exception as e:
            self.log_test("Scheduler Stability", False, f"Scheduler error: {e}")
            return False
    
    def start_test_server(self):
        """Start server for endpoint testing"""
        try:
            # Use main.py for testing
            env = os.environ.copy()
            env.pop("DATABASE_URL", None)  # Force SQLite
            
            self.server_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            # Wait for server to start
            time.sleep(5)
            return True
        except Exception as e:
            print(f"Failed to start test server: {e}")
            return False
    
    def stop_test_server(self):
        """Stop test server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait(timeout=10)
    
    def test_server_startup(self):
        """Test 4: Test server startup without errors"""
        print("\n🚀 Testing Server Startup...")
        
        if not self.start_test_server():
            self.log_test("Server Startup", False, "Failed to start server process")
            return False
        
        # Check if process is running
        if self.server_process.poll() is None:
            self.log_test("Server Startup", True, "Server started successfully")
            return True
        else:
            stdout, stderr = self.server_process.communicate()
            error_msg = stderr.decode() if stderr else "Unknown error"
            self.log_test("Server Startup", False, f"Server crashed: {error_msg[:200]}")
            return False
    
    def test_endpoint_health(self):
        """Test 5: Test basic endpoint response"""
        print("\n🌐 Testing Endpoint Health...")
        
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"http://localhost:{self.test_port}/", timeout=10)
                
                if response.status_code == 200:
                    self.log_test("Endpoint Health", True, f"GET / returned 200 OK")
                    return True
                else:
                    self.log_test("Endpoint Health", False, f"GET / returned {response.status_code}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                if i == max_retries - 1:
                    self.log_test("Endpoint Health", False, f"Endpoint unreachable: {e}")
                    return False
                else:
                    time.sleep(2)  # Wait and retry
        
        return False
    
    def test_gunicorn_compatibility(self):
        """Test 6: Test Gunicorn WSGI compatibility"""
        print("\n🦄 Testing Gunicorn Compatibility...")
        try:
            # Test import of wsgi module
            import wsgi
            
            # Check if application object exists
            if hasattr(wsgi, 'application'):
                self.log_test("Gunicorn Compatibility", True, "WSGI application object available")
                return True
            else:
                self.log_test("Gunicorn Compatibility", False, "WSGI application object not found")
                return False
        except Exception as e:
            self.log_test("Gunicorn Compatibility", False, f"WSGI import error: {e}")
            return False
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*60)
        print("🏁 VPS READINESS TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Test Details:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test']}: {result['message']}")
        
        print("\n🚀 VPS Deployment Recommendations:")
        if passed_tests == total_tests:
            print("✅ Application is READY for VPS deployment!")
            print("✅ All systems working correctly")
            print("✅ Can be deployed with confidence")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️ Application is MOSTLY READY for VPS deployment")
            print("⚠️ Some issues need attention but non-critical")
            print("⚠️ Recommend fixing failed tests before deployment")
        else:
            print("❌ Application is NOT READY for VPS deployment")
            print("❌ Critical issues need to be fixed first")
            print("❌ Fix all failed tests before deploying")
        
        print(f"\n📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all VPS readiness tests"""
        print("🚀 STARTING VPS READINESS TEST")
        print("="*60)
        
        tests = [
            self.test_dependencies,
            self.test_database_connection,
            self.test_scheduler_stability,
            self.test_server_startup,
            self.test_endpoint_health,
            self.test_gunicorn_compatibility
        ]
        
        try:
            for test in tests:
                if not test():
                    # Continue with other tests even if one fails
                    pass
                time.sleep(1)  # Brief pause between tests
        finally:
            self.stop_test_server()
        
        return self.generate_report()

if __name__ == "__main__":
    tester = VPSReadinessTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)