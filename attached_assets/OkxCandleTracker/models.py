from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
import json

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class MarketData(db.Model):
    """Model untuk menyimpan data pasar candlestick"""
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
    """Model untuk menyimpan data orderbook"""
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
    """Model untuk menyimpan data open interest"""
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