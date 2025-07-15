from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from models import db, MarketData, OrderbookData, OpenInterestData, TechnicalIndicatorData, UserPreferences
from sqlalchemy import and_, desc
import logging

class DatabaseService:
    """Service untuk mengelola operasi database"""
    
    def __init__(self):
        pass
    
    def save_market_data(self, symbol: str, timeframe: str, data: List[Dict]) -> bool:
        """Simpan data candlestick ke database"""
        try:
            for item in data:
                # Ensure timestamp is an integer
                timestamp_ms = int(item['timestamp']) if isinstance(item['timestamp'], str) else item['timestamp']
                timestamp = datetime.fromtimestamp(timestamp_ms / 1000, timezone.utc)
                
                # Cek apakah data sudah ada
                existing = MarketData.query.filter_by(
                    symbol=symbol, 
                    timeframe=timeframe, 
                    timestamp=timestamp
                ).first()
                
                if not existing:
                    market_data = MarketData(
                        symbol=symbol,
                        timeframe=timeframe,
                        timestamp=timestamp,
                        open_price=float(item['open']),
                        high_price=float(item['high']),
                        low_price=float(item['low']),
                        close_price=float(item['close']),
                        volume=float(item['volume']),
                        volume_currency=float(item.get('volume_currency', 0))
                    )
                    db.session.add(market_data)
            
            db.session.commit()
            return True
            
        except Exception as e:
            logging.error(f"Error saving market data: {str(e)}")
            db.session.rollback()
            return False
    
    def get_market_data(self, symbol: str, timeframe: str, limit: int = 100) -> List[Dict]:
        """Ambil data candlestick dari database"""
        try:
            data = MarketData.query.filter_by(
                symbol=symbol, 
                timeframe=timeframe
            ).order_by(desc(MarketData.timestamp)).limit(limit).all()
            
            return [item.to_dict() for item in reversed(data)]
            
        except Exception as e:
            logging.error(f"Error getting market data: {str(e)}")
            return []
    
    def save_orderbook_data(self, symbol: str, data: Dict) -> bool:
        """Simpan data orderbook ke database"""
        try:
            # Ensure timestamp is an integer
            timestamp_ms = int(data['timestamp']) if isinstance(data['timestamp'], str) else data['timestamp']
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000, timezone.utc)
            
            orderbook_data = OrderbookData(
                symbol=symbol,
                timestamp=timestamp,
                bids=data['bids'],
                asks=data['asks']
            )
            
            db.session.add(orderbook_data)
            db.session.commit()
            return True
            
        except Exception as e:
            logging.error(f"Error saving orderbook data: {str(e)}")
            db.session.rollback()
            return False
    
    def get_latest_orderbook_data(self, symbol: str) -> Optional[Dict]:
        """Ambil data orderbook terbaru dari database"""
        try:
            data = OrderbookData.query.filter_by(symbol=symbol).order_by(
                desc(OrderbookData.timestamp)
            ).first()
            
            return data.to_dict() if data else None
            
        except Exception as e:
            logging.error(f"Error getting orderbook data: {str(e)}")
            return None
    
    def save_open_interest_data(self, symbol: str, data: Dict) -> bool:
        """Simpan data open interest ke database"""
        try:
            # Ensure timestamp is an integer
            timestamp_ms = int(data['timestamp']) if isinstance(data['timestamp'], str) else data['timestamp']
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000, timezone.utc)
            
            # Cek apakah data sudah ada
            existing = OpenInterestData.query.filter_by(
                symbol=symbol, 
                timestamp=timestamp
            ).first()
            
            if not existing:
                oi_data = OpenInterestData(
                    symbol=symbol,
                    timestamp=timestamp,
                    open_interest=float(data['open_interest']),
                    open_interest_currency=float(data.get('open_interest_currency', 0))
                )
                
                db.session.add(oi_data)
                db.session.commit()
            
            return True
            
        except Exception as e:
            logging.error(f"Error saving open interest data: {str(e)}")
            db.session.rollback()
            return False
    
    def get_latest_open_interest_data(self, symbol: str) -> Optional[Dict]:
        """Ambil data open interest terbaru dari database"""
        try:
            data = OpenInterestData.query.filter_by(symbol=symbol).order_by(
                desc(OpenInterestData.timestamp)
            ).first()
            
            return data.to_dict() if data else None
            
        except Exception as e:
            logging.error(f"Error getting open interest data: {str(e)}")
            return None
    
    def save_technical_indicators(self, symbol: str, timeframe: str, indicators: Dict) -> bool:
        """Simpan data indikator teknis ke database"""
        try:
            for indicator_type, values in indicators.items():
                if not values:
                    continue
                
                # Simpan setiap nilai indikator
                for value in values:
                    if isinstance(value, dict) and 'timestamp' in value:
                        timestamp = datetime.fromtimestamp(value['timestamp'] / 1000, timezone.utc)
                        
                        # Cek apakah data sudah ada
                        existing = TechnicalIndicatorData.query.filter_by(
                            symbol=symbol,
                            timeframe=timeframe,
                            timestamp=timestamp,
                            indicator_type=indicator_type
                        ).first()
                        
                        if not existing:
                            indicator_data = TechnicalIndicatorData(
                                symbol=symbol,
                                timeframe=timeframe,
                                timestamp=timestamp,
                                indicator_type=indicator_type,
                                values=value
                            )
                            db.session.add(indicator_data)
            
            db.session.commit()
            return True
            
        except Exception as e:
            logging.error(f"Error saving technical indicators: {str(e)}")
            db.session.rollback()
            return False
    
    def get_technical_indicators(self, symbol: str, timeframe: str, limit: int = 100) -> Dict:
        """Ambil data indikator teknis dari database"""
        try:
            indicators = {}
            
            # Ambil semua jenis indikator
            indicator_types = ['MACD', 'RSI', 'OBV', 'SMA']
            
            for indicator_type in indicator_types:
                data = TechnicalIndicatorData.query.filter_by(
                    symbol=symbol,
                    timeframe=timeframe,
                    indicator_type=indicator_type
                ).order_by(desc(TechnicalIndicatorData.timestamp)).limit(limit).all()
                
                if data:
                    indicators[indicator_type.lower()] = [item.values for item in reversed(data)]
            
            return indicators
            
        except Exception as e:
            logging.error(f"Error getting technical indicators: {str(e)}")
            return {}
    
    def get_user_preferences(self, session_id: str) -> Optional[UserPreferences]:
        """Ambil preferensi pengguna"""
        try:
            return UserPreferences.query.filter_by(session_id=session_id).first()
            
        except Exception as e:
            logging.error(f"Error getting user preferences: {str(e)}")
            return None
    
    def save_user_preferences(self, session_id: str, preferences: Dict) -> bool:
        """Simpan preferensi pengguna"""
        try:
            existing = UserPreferences.query.filter_by(session_id=session_id).first()
            
            if existing:
                existing.preferred_symbol = preferences.get('symbol', existing.preferred_symbol)
                existing.preferred_timeframe = preferences.get('timeframe', existing.preferred_timeframe)
                existing.preferred_limit = preferences.get('limit', existing.preferred_limit)
                existing.auto_refresh = preferences.get('auto_refresh', existing.auto_refresh)
                existing.updated_at = datetime.utcnow()
            else:
                user_prefs = UserPreferences(
                    session_id=session_id,
                    preferred_symbol=preferences.get('symbol', 'BTC-USDT'),
                    preferred_timeframe=preferences.get('timeframe', '1h'),
                    preferred_limit=preferences.get('limit', 100),
                    auto_refresh=preferences.get('auto_refresh', True)
                )
                db.session.add(user_prefs)
            
            db.session.commit()
            return True
            
        except Exception as e:
            logging.error(f"Error saving user preferences: {str(e)}")
            db.session.rollback()
            return False
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """Bersihkan data lama dari database"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Hapus data lama
            MarketData.query.filter(MarketData.created_at < cutoff_date).delete()
            OrderbookData.query.filter(OrderbookData.created_at < cutoff_date).delete()
            OpenInterestData.query.filter(OpenInterestData.created_at < cutoff_date).delete()
            TechnicalIndicatorData.query.filter(TechnicalIndicatorData.created_at < cutoff_date).delete()
            
            db.session.commit()
            return True
            
        except Exception as e:
            logging.error(f"Error cleaning up old data: {str(e)}")
            db.session.rollback()
            return False