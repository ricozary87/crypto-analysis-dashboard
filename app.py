import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("trading_app.log"),
        logging.StreamHandler()
    ]
)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the PostgreSQL database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
}

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Initialize scheduler for background tasks
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

with app.app_context():
    # Import models to create tables
    import models
    db.create_all()

# Import routes and websocket handlers after app context
from routes import *
from websocket_handler import *

# Initialize trading orchestrator
from core.orchestrator import MainOrchestrator
trading_orchestrator = MainOrchestrator()

def run_trading_cycle():
    """Background task to run trading analysis"""
    try:
        trading_orchestrator.run()
    except Exception as e:
        app.logger.error(f"Trading cycle error: {e}", exc_info=True)

# Disabled automatic scheduling - analysis runs on-demand only
# scheduler.add_job(
#     func=run_trading_cycle,
#     trigger=IntervalTrigger(minutes=5),
#     id='trading_cycle',
#     name='Run trading analysis cycle',
#     replace_existing=True
# )

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
