"""
Technical analysis engine for cryptocurrency trading
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
import ta

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Technical analysis engine with various indicators"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Perform comprehensive technical analysis"""
        
        try:
            if df is None or df.empty:
                return self._empty_analysis()
            
            # Calculate indicators
            indicators = self._calculate_indicators(df)
            
            # Generate signals
            signals = self._generate_signals(df, indicators)
            
            # Create analysis summary
            analysis = {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': df['timestamp'].iloc[-1] if 'timestamp' in df.columns else None,
                'current_price': float(df['close'].iloc[-1]),
                'price_change_24h': self._calculate_price_change(df),
                'indicators': indicators,
                'signals': signals,
                'trend': self._determine_trend(df, indicators),
                'volume_status': self._analyze_volume(df),
                'summary': self._create_summary(indicators, signals)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Analysis error for {symbol}: {e}")
            return self._empty_analysis()
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators"""
        
        indicators = {}
        
        try:
            # RSI
            rsi = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
            indicators['rsi'] = {
                'value': float(rsi.iloc[-1]) if not rsi.empty else 50.0,
                'overbought': bool(rsi.iloc[-1] > 70) if not rsi.empty else False,
                'oversold': bool(rsi.iloc[-1] < 30) if not rsi.empty else False
            }
            
            # Moving Averages
            ema_20 = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()
            ema_50 = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
            
            indicators['ema'] = {
                'ema_20': float(ema_20.iloc[-1]) if not ema_20.empty else float(df['close'].iloc[-1]),
                'ema_50': float(ema_50.iloc[-1]) if not ema_50.empty else float(df['close'].iloc[-1]),
                'trend': 'bullish' if ema_20.iloc[-1] > ema_50.iloc[-1] else 'bearish'
            }
            
            # MACD
            macd_indicator = ta.trend.MACD(df['close'])
            macd_line = macd_indicator.macd()
            macd_signal = macd_indicator.macd_signal()
            macd_histogram = macd_indicator.macd_diff()
            
            if not macd_line.empty and not macd_signal.empty:
                indicators['macd'] = {
                    'macd': float(macd_line.iloc[-1]),
                    'signal': float(macd_signal.iloc[-1]),
                    'histogram': float(macd_histogram.iloc[-1]),
                    'bullish': bool(macd_line.iloc[-1] > macd_signal.iloc[-1])
                }
            
            # Bollinger Bands
            bb_indicator = ta.volatility.BollingerBands(df['close'])
            bb_upper = bb_indicator.bollinger_hband()
            bb_middle = bb_indicator.bollinger_mavg()
            bb_lower = bb_indicator.bollinger_lband()
            
            if not bb_upper.empty and not bb_middle.empty and not bb_lower.empty:
                indicators['bollinger'] = {
                    'upper': float(bb_upper.iloc[-1]),
                    'middle': float(bb_middle.iloc[-1]),
                    'lower': float(bb_lower.iloc[-1]),
                    'squeeze': bool(abs(bb_upper.iloc[-1] - bb_lower.iloc[-1]) < (bb_middle.iloc[-1] * 0.1))
                }
            
            # Volume indicators
            volume_sma = ta.trend.SMAIndicator(df['volume'], window=20).sma_indicator()
            indicators['volume'] = {
                'current': float(df['volume'].iloc[-1]),
                'average': float(volume_sma.iloc[-1]) if not volume_sma.empty else float(df['volume'].iloc[-1]),
                'above_average': bool(df['volume'].iloc[-1] > volume_sma.iloc[-1]) if not volume_sma.empty else False
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            indicators = self._default_indicators()
        
        return indicators
    
    def _generate_signals(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signals based on indicators"""
        
        signals = {
            'action': 'HOLD',
            'confidence': 0.0,
            'reason': [],
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None
        }
        
        try:
            current_price = df['close'].iloc[-1]
            confidence_score = 0
            reasons = []
            
            # RSI signals
            if indicators.get('rsi', {}).get('oversold', False):
                confidence_score += 0.3
                reasons.append("RSI oversold")
            elif indicators.get('rsi', {}).get('overbought', False):
                confidence_score -= 0.3
                reasons.append("RSI overbought")
            
            # EMA trend
            if indicators.get('ema', {}).get('trend') == 'bullish':
                confidence_score += 0.2
                reasons.append("EMA bullish trend")
            elif indicators.get('ema', {}).get('trend') == 'bearish':
                confidence_score -= 0.2
                reasons.append("EMA bearish trend")
            
            # MACD signals
            if indicators.get('macd', {}).get('bullish', False):
                confidence_score += 0.25
                reasons.append("MACD bullish crossover")
            else:
                confidence_score -= 0.25
                reasons.append("MACD bearish")
            
            # Volume confirmation
            if indicators.get('volume', {}).get('above_average', False):
                confidence_score += 0.15
                reasons.append("Volume above average")
            
            # Determine action
            if confidence_score > 0.5:
                signals['action'] = 'BUY'
                signals['entry_price'] = current_price
                signals['stop_loss'] = current_price * 0.95  # 5% stop loss
                signals['take_profit'] = current_price * 1.10  # 10% take profit
            elif confidence_score < -0.5:
                signals['action'] = 'SELL'
                signals['entry_price'] = current_price
                signals['stop_loss'] = current_price * 1.05  # 5% stop loss
                signals['take_profit'] = current_price * 0.90  # 10% take profit
            
            signals['confidence'] = min(abs(confidence_score), 1.0)
            signals['reason'] = reasons
            
        except Exception as e:
            self.logger.error(f"Error generating signals: {e}")
        
        return signals
    
    def _determine_trend(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> str:
        """Determine overall trend"""
        
        try:
            ema_trend = indicators.get('ema', {}).get('trend', 'neutral')
            macd_bullish = indicators.get('macd', {}).get('bullish', False)
            
            if ema_trend == 'bullish' and macd_bullish:
                return 'BULLISH'
            elif ema_trend == 'bearish' and not macd_bullish:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
                
        except Exception:
            return 'NEUTRAL'
    
    def _analyze_volume(self, df: pd.DataFrame) -> str:
        """Analyze volume patterns"""
        
        try:
            recent_volume = df['volume'].tail(5).mean()
            older_volume = df['volume'].tail(20).mean()
            
            if recent_volume > older_volume * 1.2:
                return 'INCREASING'
            elif recent_volume < older_volume * 0.8:
                return 'DECREASING'
            else:
                return 'STABLE'
                
        except Exception:
            return 'STABLE'
    
    def _calculate_price_change(self, df: pd.DataFrame) -> float:
        """Calculate 24h price change percentage"""
        
        try:
            if len(df) >= 24:
                old_price = df['close'].iloc[-24]
                current_price = df['close'].iloc[-1]
                return ((current_price - old_price) / old_price) * 100
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def _create_summary(self, indicators: Dict[str, Any], signals: Dict[str, Any]) -> str:
        """Create analysis summary"""
        
        try:
            action = signals.get('action', 'HOLD')
            confidence = signals.get('confidence', 0) * 100
            trend = indicators.get('ema', {}).get('trend', 'neutral')
            rsi = indicators.get('rsi', {}).get('value', 50)
            
            return f"Signal: {action} (Confidence: {confidence:.0f}%) | Trend: {trend} | RSI: {rsi:.1f}"
            
        except Exception:
            return "Analysis unavailable"
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        
        return {
            'symbol': '',
            'timeframe': '',
            'timestamp': None,
            'current_price': 0.0,
            'price_change_24h': 0.0,
            'indicators': self._default_indicators(),
            'signals': {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': [],
                'entry_price': None,
                'stop_loss': None,
                'take_profit': None
            },
            'trend': 'NEUTRAL',
            'volume_status': 'STABLE',
            'summary': 'No data available'
        }
    
    def _default_indicators(self) -> Dict[str, Any]:
        """Return default indicators"""
        
        return {
            'rsi': {'value': 50, 'overbought': False, 'oversold': False},
            'ema': {'ema_20': 0, 'ema_50': 0, 'trend': 'neutral'},
            'macd': {'macd': 0, 'signal': 0, 'histogram': 0, 'bullish': False},
            'bollinger': {'upper': 0, 'middle': 0, 'lower': 0, 'squeeze': False},
            'volume': {'current': 0, 'average': 0, 'above_average': False}
        }
    
    def get_indicator_summary(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Get simplified indicator summary for UI"""
        
        return {
            'rsi': indicators.get('rsi', {}).get('value', 50),
            'trend': indicators.get('ema', {}).get('trend', 'neutral'),
            'macd_bullish': indicators.get('macd', {}).get('bullish', False),
            'volume_above_avg': indicators.get('volume', {}).get('above_average', False)
        }