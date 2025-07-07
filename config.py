import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    # Use PostgreSQL database from environment variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Trading configuration
    TRADING_SYMBOLS = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'TIA-USDT', 'RENDER-USDT']
    TRADING_TIMEFRAMES = ['1m', '5m', '15m', '1H', '4H']
    CONFIDENCE_THRESHOLD = 0.65
    MAX_RETRIES = 3
    
    # API configuration
    OKX_API_KEY = os.environ.get('OKX_API_KEY', 'demo_key')
    OKX_SECRET_KEY = os.environ.get('OKX_SECRET_KEY', 'demo_secret')
    OKX_PASSPHRASE = os.environ.get('OKX_PASSPHRASE', 'demo_passphrase')
    
    # Telegram configuration
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
