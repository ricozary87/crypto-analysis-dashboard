"""
Price Action Analyzer - Candlestick Pattern Detection
Enhanced with improved scoring system and pattern visualization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class PriceActionAnalyzer:
    """
    Enhanced Price Action Analyzer with multiple candlestick pattern detection
    Provides confidence scoring and pattern visualization capabilities
    """
    
    def __init__(self):
        self.patterns = {
            'hammer': {'strength': 0.7, 'type': 'bullish'},
            'hanging_man': {'strength': 0.7, 'type': 'bearish'},
            'shooting_star': {'strength': 0.8, 'type': 'bearish'},
            'inverted_hammer': {'strength': 0.6, 'type': 'bullish'},
            'bullish_engulfing': {'strength': 0.9, 'type': 'bullish'},
            'bearish_engulfing': {'strength': 0.9, 'type': 'bearish'},
            'morning_star': {'strength': 0.9, 'type': 'bullish'},
            'evening_star': {'strength': 0.9, 'type': 'bearish'},
            'doji': {'strength': 0.5, 'type': 'neutral'},
            'spinning_top': {'strength': 0.4, 'type': 'neutral'}
        }
        
    def analyze_price_action(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze price action patterns in the given DataFrame
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary containing detected patterns and signals
        """
        
        # Validate and convert input data
        if df is None:
            return self._empty_analysis()
            
        # Convert list to DataFrame if needed
        if isinstance(df, list):
            try:
                # Assume list of dicts with OHLCV data
                df = pd.DataFrame(df)
            except Exception as e:
                logger.error(f"Failed to convert list to DataFrame: {e}")
                return self._empty_analysis()
        
        # Ensure it's a DataFrame
        if not isinstance(df, pd.DataFrame):
            logger.error(f"Expected DataFrame, got {type(df)}")
            return self._empty_analysis()
        
        if len(df) < 3:
            return self._empty_analysis()
        
        try:
            # Ensure we have the required columns
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                return self._empty_analysis()
            
            # Convert to float to ensure numeric operations
            for col in required_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove any NaN values
            df = df.dropna()
            
            if len(df) < 3:
                return self._empty_analysis()
            
            # Detect patterns
            patterns_detected = self._detect_patterns(df)
            
            # Generate signals
            signals = self._generate_signals(patterns_detected)
            
            # Calculate confidence
            confidence = self._calculate_confidence(patterns_detected)
            
            # Analyze trend strength
            trend_strength = self._analyze_trend_strength(df)
            
            # Identify support/resistance levels
            support_resistance = self._identify_support_resistance(df)
            
            return {
                'patterns_detected': patterns_detected,
                'signals': signals,
                'confidence': confidence,
                'trend_strength': trend_strength,
                'support_resistance': support_resistance,
                'total_patterns': len(patterns_detected),
                'bullish_patterns': len([p for p in patterns_detected if p['type'] == 'bullish']),
                'bearish_patterns': len([p for p in patterns_detected if p['type'] == 'bearish'])
            }
            
        except Exception as e:
            logger.error(f"Error in price action analysis: {e}")
            return self._empty_analysis()
    
    def _detect_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect various candlestick patterns"""
        patterns = []
        
        for i in range(2, len(df)):
            current = df.iloc[i]
            prev = df.iloc[i-1]
            prev2 = df.iloc[i-2]
            
            # Hammer pattern
            if self._is_hammer(current):
                patterns.append({
                    'name': 'hammer',
                    'type': 'bullish',
                    'strength': 0.7,
                    'index': i,
                    'description': 'Hammer pattern detected - potential bullish reversal'
                })
            
            # Shooting star pattern
            if self._is_shooting_star(current):
                patterns.append({
                    'name': 'shooting_star',
                    'type': 'bearish',
                    'strength': 0.8,
                    'index': i,
                    'description': 'Shooting star pattern detected - potential bearish reversal'
                })
            
            # Bullish engulfing pattern
            if self._is_bullish_engulfing(prev, current):
                patterns.append({
                    'name': 'bullish_engulfing',
                    'type': 'bullish',
                    'strength': 0.9,
                    'index': i,
                    'description': 'Bullish engulfing pattern detected - strong bullish signal'
                })
            
            # Bearish engulfing pattern
            if self._is_bearish_engulfing(prev, current):
                patterns.append({
                    'name': 'bearish_engulfing',
                    'type': 'bearish',
                    'strength': 0.9,
                    'index': i,
                    'description': 'Bearish engulfing pattern detected - strong bearish signal'
                })
            
            # Doji pattern
            if self._is_doji(current):
                patterns.append({
                    'name': 'doji',
                    'type': 'neutral',
                    'strength': 0.5,
                    'index': i,
                    'description': 'Doji pattern detected - market indecision'
                })
        
        return patterns
    
    def _is_hammer(self, candle) -> bool:
        """Check if candle is a hammer pattern"""
        body = abs(candle['close'] - candle['open'])
        lower_shadow = candle['open'] - candle['low'] if candle['close'] > candle['open'] else candle['close'] - candle['low']
        upper_shadow = candle['high'] - candle['close'] if candle['close'] > candle['open'] else candle['high'] - candle['open']
        
        return (
            lower_shadow > 2 * body and
            upper_shadow < 0.5 * body and
            body > 0
        )
    
    def _is_shooting_star(self, candle) -> bool:
        """Check if candle is a shooting star pattern"""
        body = abs(candle['close'] - candle['open'])
        lower_shadow = candle['open'] - candle['low'] if candle['close'] > candle['open'] else candle['close'] - candle['low']
        upper_shadow = candle['high'] - candle['close'] if candle['close'] > candle['open'] else candle['high'] - candle['open']
        
        return (
            upper_shadow > 2 * body and
            lower_shadow < 0.5 * body and
            body > 0
        )
    
    def _is_bullish_engulfing(self, prev_candle, current_candle) -> bool:
        """Check if current candle engulfs previous bearish candle"""
        return (
            prev_candle['close'] < prev_candle['open'] and  # Previous candle is bearish
            current_candle['close'] > current_candle['open'] and  # Current candle is bullish
            current_candle['open'] < prev_candle['close'] and  # Current opens below previous close
            current_candle['close'] > prev_candle['open']  # Current closes above previous open
        )
    
    def _is_bearish_engulfing(self, prev_candle, current_candle) -> bool:
        """Check if current candle engulfs previous bullish candle"""
        return (
            prev_candle['close'] > prev_candle['open'] and  # Previous candle is bullish
            current_candle['close'] < current_candle['open'] and  # Current candle is bearish
            current_candle['open'] > prev_candle['close'] and  # Current opens above previous close
            current_candle['close'] < prev_candle['open']  # Current closes below previous open
        )
    
    def _is_doji(self, candle) -> bool:
        """Check if candle is a doji pattern"""
        body = abs(candle['close'] - candle['open'])
        total_range = candle['high'] - candle['low']
        
        return body < 0.1 * total_range if total_range > 0 else False
    
    def _generate_signals(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate trading signals from detected patterns"""
        signals = []
        
        # Group patterns by type
        bullish_patterns = [p for p in patterns if p['type'] == 'bullish']
        bearish_patterns = [p for p in patterns if p['type'] == 'bearish']
        
        # Generate bullish signal if bullish patterns are stronger
        if bullish_patterns:
            bullish_strength = sum(p['strength'] for p in bullish_patterns)
            signals.append({
                'signal': 'BUY',
                'confidence': min(bullish_strength, 1.0),
                'patterns': [p['name'] for p in bullish_patterns],
                'reason': f"Strong bullish patterns detected: {', '.join(p['name'] for p in bullish_patterns)}"
            })
        
        # Generate bearish signal if bearish patterns are stronger
        if bearish_patterns:
            bearish_strength = sum(p['strength'] for p in bearish_patterns)
            signals.append({
                'signal': 'SELL',
                'confidence': min(bearish_strength, 1.0),
                'patterns': [p['name'] for p in bearish_patterns],
                'reason': f"Strong bearish patterns detected: {', '.join(p['name'] for p in bearish_patterns)}"
            })
        
        return signals
    
    def _calculate_confidence(self, patterns: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence based on detected patterns"""
        if not patterns:
            return 0.0
        
        total_strength = sum(p['strength'] for p in patterns)
        return min(total_strength / len(patterns), 1.0)
    
    def _analyze_trend_strength(self, df: pd.DataFrame) -> str:
        """Analyze trend strength from price action"""
        if len(df) < 10:
            return 'weak'
        
        # Calculate recent price movement
        recent_close = df['close'].iloc[-1]
        past_close = df['close'].iloc[-10]
        
        price_change = (recent_close - past_close) / past_close * 100
        
        if abs(price_change) > 5:
            return 'strong'
        elif abs(price_change) > 2:
            return 'moderate'
        else:
            return 'weak'
    
    def _identify_support_resistance(self, df: pd.DataFrame) -> Dict[str, float]:
        """Identify key support and resistance levels"""
        if len(df) < 20:
            return {}
        
        # Simple support/resistance based on recent highs and lows
        recent_data = df.tail(20)
        
        support = float(recent_data['low'].min())
        resistance = float(recent_data['high'].max())
        current_price = float(df['close'].iloc[-1])
        
        return {
            'support': support,
            'resistance': resistance,
            'current_price': current_price,
            'distance_to_support': ((current_price - support) / current_price) * 100,
            'distance_to_resistance': ((resistance - current_price) / current_price) * 100
        }
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'patterns_detected': [],
            'signals': [],
            'confidence': 0.0,
            'trend_strength': 'weak',
            'support_resistance': {},
            'total_patterns': 0,
            'bullish_patterns': 0,
            'bearish_patterns': 0
        }