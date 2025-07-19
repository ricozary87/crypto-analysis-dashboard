"""
Gunicorn Configuration File for Production Deployment
Standard configuration for VPS deployment
"""

import os
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'crypto_trading_ai'

# Server mechanics
daemon = False
pidfile = 'tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment for HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment variables
raw_env = [
    'DATABASE_URL=postgresql://user:password@localhost/trading_db',
    'SESSION_SECRET=your-secret-key-here',
    'FLASK_ENV=production',
    'OPENAI_API_KEY=your-openai-key',
    'OKX_API_KEY=your-okx-api-key',
    'OKX_SECRET_KEY=your-okx-secret',
    'OKX_PASSPHRASE=your-okx-passphrase'
]