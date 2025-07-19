import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_socketio import SocketIO
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

# Sentry Integration for Error Monitoring
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Prometheus Integration for Metrics
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Configure Sentry for Error Monitoring
sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)

# Initialize Sentry SDK
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[
        FlaskIntegration(transaction_style='endpoint'),
        SqlalchemyIntegration(),
        sentry_logging,
    ],
    # Set traces_sample_rate to 1.0 to capture 100% of transactions
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions
    profiles_sample_rate=1.0,
    # Release information
    release=os.environ.get("SENTRY_RELEASE", "trading-ai-v1.0.0"),
    environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
    # Enable performance monitoring
    enable_tracing=True,
    # Additional configuration
    before_send_transaction=lambda event, hint: event if event.get('transaction') != '/health' else None,
    debug=os.environ.get("SENTRY_DEBUG", "false").lower() == "true"
)

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

# Enable CORS for React frontend
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"], 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Configure the database with fallback
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to SQLite for local development
    DATABASE_URL = "sqlite:///trading_local.db"
    print("🔧 Using SQLite database for local development")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

# Engine options (only for PostgreSQL)
if DATABASE_URL.startswith("postgresql"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }
else:
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Initialize Prometheus Metrics
metrics = PrometheusMetrics(app)
metrics.info('trading_ai_app_info', 'Application info', version='1.0.0')

# Custom Prometheus Metrics for Trading AI
trading_signals_total = Counter('trading_signals_total', 'Total trading signals generated', ['symbol', 'action'])
api_response_time = Histogram('api_response_time_seconds', 'API response time in seconds', ['endpoint'])
active_signals = Gauge('active_signals_count', 'Number of active trading signals', ['symbol'])
win_rate = Gauge('trading_win_rate', 'Trading win rate percentage', ['symbol'])
analysis_confidence = Histogram('analysis_confidence_score', 'Analysis confidence score distribution', ['symbol'])
okx_api_calls = Counter('okx_api_calls_total', 'Total OKX API calls', ['endpoint', 'status'])
ai_narrative_requests = Counter('ai_narrative_requests_total', 'Total AI narrative requests', ['model', 'status'])
system_health = Gauge('system_health_score', 'System health score (0-100)')
database_connections = Gauge('database_connections_active', 'Active database connections')

# Initialize scheduler for background tasks
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

with app.app_context():
    # Import models to create tables
    import models
    db.create_all()

# Import routes and websocket handlers after app context
def setup_routes():
    """Setup routes after app initialization to avoid circular imports"""
    import routes
    import websocket_handler
    return routes, websocket_handler

# Setup routes
setup_routes()

# Setup monitoring routes
import monitoring_routes

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

# Entry point moved to main.py for cleaner architecture
# Use: python main.py to run the application
