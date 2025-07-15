from app import db
from datetime import datetime, timezone
from sqlalchemy import Index, Column, Integer, String, Float, DateTime, Boolean, Text, JSON, BigInteger

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

# ============================================================================
# NEW MODELS FROM OkxCandleTracker - Phase 1 Integration
# ============================================================================

class MarketData(db.Model):
    """Model untuk menyimpan data pasar candlestick dari OKX"""
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(5), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    volume_currency = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'timestamp': int(self.timestamp.timestamp() * 1000),
            'datetime': self.timestamp.isoformat(),
            'open': self.open_price,
            'high': self.high_price,
            'low': self.low_price,
            'close': self.close_price,
            'volume': self.volume,
            'volume_currency': self.volume_currency
        }

class OrderbookData(db.Model):
    """Model untuk menyimpan data orderbook dari OKX"""
    __tablename__ = 'orderbook_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    bids = Column(JSON, nullable=False)  # JSON array of bid orders
    asks = Column(JSON, nullable=False)  # JSON array of ask orders
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'timestamp': int(self.timestamp.timestamp() * 1000),
            'datetime': self.timestamp.isoformat(),
            'bids': self.bids,
            'asks': self.asks
        }

class OpenInterestData(db.Model):
    """Model untuk menyimpan data open interest dari OKX"""
    __tablename__ = 'open_interest_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open_interest = Column(Float, nullable=False)
    open_interest_currency = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'timestamp': int(self.timestamp.timestamp() * 1000),
            'datetime': self.timestamp.isoformat(),
            'open_interest': self.open_interest,
            'open_interest_currency': self.open_interest_currency
        }

class TechnicalIndicatorData(db.Model):
    """Model untuk menyimpan data indikator teknis"""
    __tablename__ = 'technical_indicator_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(5), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    indicator_type = Column(String(20), nullable=False)  # 'MACD', 'RSI', 'OBV', etc.
    values = Column(JSON, nullable=False)  # JSON object with indicator values
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'timestamp': int(self.timestamp.timestamp() * 1000),
            'datetime': self.timestamp.isoformat(),
            'indicator_type': self.indicator_type,
            'values': self.values
        }

class UserPreferences(db.Model):
    """Model untuk menyimpan preferensi pengguna"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, nullable=False)
    preferred_symbol = Column(String(20), default='BTC-USDT')
    preferred_timeframe = Column(String(5), default='1h')
    preferred_limit = Column(Integer, default=100)
    auto_refresh = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'preferred_symbol': self.preferred_symbol,
            'preferred_timeframe': self.preferred_timeframe,
            'preferred_limit': self.preferred_limit,
            'auto_refresh': self.auto_refresh,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AISnapshotArchive(db.Model):
    """Model untuk menyimpan arsip AI snapshot"""
    __tablename__ = 'ai_snapshot_archive'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(5), nullable=False)
    quick_mode = Column(Boolean, default=False)
    ai_narrative = Column(Text, nullable=False)
    confluence_summary = Column(JSON, nullable=True)
    layer_analysis = Column(JSON, nullable=True)
    snapshot_data = Column(JSON, nullable=True)  # Full snapshot data
    confidence = Column(Float, nullable=True)  # Confidence score (0-1)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'quick_mode': self.quick_mode,
            'ai_narrative': self.ai_narrative,
            'confluence_summary': self.confluence_summary,
            'layer_analysis': self.layer_analysis,
            'snapshot_data': self.snapshot_data,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
