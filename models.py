from app import db
from datetime import datetime, timezone
from sqlalchemy import Index

class TradingSignal(db.Model):
    __tablename__ = 'trading_signals'
    
    id = db.Column(db.Integer, primary_key=True)
    signal_id = db.Column(db.String(128), unique=True, nullable=False)
    symbol = db.Column(db.String(32), nullable=False)
    action = db.Column(db.String(16), nullable=False)  # BUY or SELL
    pattern_type = db.Column(db.String(32), nullable=False)  # BOS, CHoCH, FVG, ORDER_BLOCK
    entry_price = db.Column(db.Float, nullable=False)
    stop_loss = db.Column(db.Float, nullable=False)
    take_profit_1 = db.Column(db.Float, nullable=False)
    take_profit_2 = db.Column(db.Float, nullable=False)
    take_profit_3 = db.Column(db.Float, nullable=False)
    risk_reward_ratio = db.Column(db.Float, default=2.0)
    position_size_percentage = db.Column(db.Float, default=2.0)
    confidence = db.Column(db.Float, default=0.0)
    timeframe = db.Column(db.String(8), default="1H")
    reason = db.Column(db.Text)
    invalidation_level = db.Column(db.Float)
    status = db.Column(db.String(16), default="active")  # active, hit_tp1, hit_tp2, hit_tp3, stopped, cancelled
    timestamp = db.Column(db.BigInteger, nullable=False)  # Unix timestamp in milliseconds
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_symbol_timeframe', 'symbol', 'timeframe'),
        Index('idx_timestamp', 'timestamp'),
        Index('idx_action', 'action'),
        Index('idx_status', 'status'),
    )

class SystemMetrics(db.Model):
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Float)
    disk_usage = db.Column(db.Float)
    api_response_time = db.Column(db.Float)
    active_connections = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    cycle_count = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class AlertLog(db.Model):
    __tablename__ = 'alert_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(32), nullable=False)  # signal, system, error
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(16), default="info")  # info, warning, error, critical
    channel = db.Column(db.String(32))  # telegram, email, sms
    status = db.Column(db.String(16), default="pending")  # pending, sent, failed
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class TradingAnalysis(db.Model):
    __tablename__ = 'trading_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(32), nullable=False)
    timeframe = db.Column(db.String(8), default="1H")
    analysis_type = db.Column(db.String(32), default="advanced")  # advanced, basic
    
    # Price data at time of analysis
    current_price = db.Column(db.Float, nullable=False)
    price_change_24h = db.Column(db.Float)
    
    # Analysis results
    has_signal = db.Column(db.Boolean, default=False)
    signal_action = db.Column(db.String(16))  # BUY, SELL
    signal_confidence = db.Column(db.Float)
    entry_price = db.Column(db.Float)
    stop_loss = db.Column(db.Float)
    take_profit_1 = db.Column(db.Float)
    take_profit_2 = db.Column(db.Float)
    take_profit_3 = db.Column(db.Float)
    
    # SMC Analysis summary
    smc_patterns_detected = db.Column(db.JSON)  # {"BOS": 2, "FVG": 1, etc}
    
    # Technical indicators
    rsi_value = db.Column(db.Float)
    ema_trend = db.Column(db.String(16))  # bullish, bearish, neutral
    volume_trend = db.Column(db.String(16))  # increasing, decreasing, stable
    
    # Full formatted analysis text
    formatted_analysis = db.Column(db.Text)  # Full Indonesian formatted text
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_ip = db.Column(db.String(64))
    
    # Indexes for quick search
    __table_args__ = (
        Index('idx_symbol_created', 'symbol', 'created_at'),
        Index('idx_has_signal', 'has_signal'),
        Index('idx_created_at', 'created_at'),
    )
