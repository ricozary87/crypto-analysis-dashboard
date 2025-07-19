#!/usr/bin/env python3
"""
WSGI Entry Point for Production Deployment
Standard entry point compatible with gunicorn, uwsgi, and other WSGI servers
"""

from app import app, socketio, init_scheduler

# Initialize scheduler for production deployment
init_scheduler()

# For WSGI servers (gunicorn, uwsgi)
application = socketio

if __name__ == "__main__":
    # For development only
    import os
    # Use SQLite for local development if DATABASE_URL not set
    if not os.environ.get("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "sqlite:///trading_local.db"
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)