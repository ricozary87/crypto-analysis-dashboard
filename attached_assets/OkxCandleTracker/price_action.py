"""
Price Action Analyzer
Detects candlestick patterns, support/resistance, breakouts, and market structure
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

class PriceActionAnalyzer:
    def __init__(self):
        self.min_body_ratio = 0.1  # Minimum body size relative to range
        self.doji_threshold = 0.05  # Threshold for doji detection
        self.hammer_ratio = 2.0  # Wick to body ratio for hammer
        
    def detect_candlestick_patterns(self, data: List[Dict]) -> List[Dict]:
        """Detect major candlestick patterns"""
        if len(data) < 3:
            return []
        
        patterns = []
        
        for i in range(1, len(data) - 1):
            prev_candle = data[i-1]
            current_candle = data[i]
            next_candle = data[i+1]
            
            # Basic candle measurements
            body_size = abs(current_candle['close'] - current_candle['open'])
            range_size = current_candle['high'] - current_candle['low']
            upper_wick = current_candle['high'] - max(current_candle['open'], current_candle['close'])
            lower_wick = min(current_candle['open'], current_candle['close']) - current_candle['low']
            
            if range_size == 0:
                continue
                
            body_ratio = body_size / range_size
            
            # Doji patterns
            if body_ratio < self.doji_threshold:
                patterns.append({
                    'timestamp': current_candle['timestamp'],
                    'pattern': 'doji',
                    'type': 'reversal',
                    'strength': self._calculate_pattern_strength(current_candle, prev_candle, next_candle),
                    'candle_data': current_candle
                })
            
            # Hammer/Hanging Man
            elif (lower_wick > body_size * self.hammer_ratio and 
                  upper_wick < body_size * 0.5):
                
                if prev_candle['close'] > prev_candle['open']:  # Previous bullish
                    pattern_name = 'hanging_man'
                    pattern_type = 'bearish_reversal'
                else:  # Previous bearish
                    pattern_name = 'hammer'
                    pattern_type = 'bullish_reversal'
                
                patterns.append({
                    'timestamp': current_candle['timestamp'],
                    'pattern': pattern_name,
                    'type': pattern_type,
                    'strength': self._calculate_pattern_strength(current_candle, prev_candle, next_candle),
                    'candle_data': current_candle
                })
            
            # Inverted Hammer/Shooting Star
            elif (upper_wick > body_size * self.hammer_ratio and 
                  lower_wick < body_size * 0.5):
                
                if prev_candle['close'] < prev_candle['open']:  # Previous bearish
                    pattern_name = 'inverted_hammer'
                    pattern_type = 'bullish_reversal'
                else:  # Previous bullish
                    pattern_name = 'shooting_star'
                    pattern_type = 'bearish_reversal'
                
                patterns.append({
                    'timestamp': current_candle['timestamp'],
                    'pattern': pattern_name,
                    'type': pattern_type,
                    'strength': self._calculate_pattern_strength(current_candle, prev_candle, next_candle),
                    'candle_data': current_candle
                })
            
            # Pin Bar
            elif (max(upper_wick, lower_wick) > body_size * 2 and 
                  min(upper_wick, lower_wick) < body_size * 0.5):
                
                pin_direction = 'bullish' if lower_wick > upper_wick else 'bearish'
                
                patterns.append({
                    'timestamp': current_candle['timestamp'],
                    'pattern': 'pin_bar',
                    'type': f'{pin_direction}_reversal',
                    'strength': self._calculate_pattern_strength(current_candle, prev_candle, next_candle),
                    'candle_data': current_candle
                })
        
        # Multi-candle patterns
        patterns.extend(self._detect_engulfing_patterns(data))
        patterns.extend(self._detect_inside_outside_bars(data))
        
        return patterns
    
    def _detect_engulfing_patterns(self, data: List[Dict]) -> List[Dict]:
        """Detect bullish and bearish engulfing patterns"""
        if len(data) < 2:
            return []
        
        patterns = []
        
        for i in range(1, len(data)):
            prev_candle = data[i-1]
            current_candle = data[i]
            
            prev_body_size = abs(prev_candle['close'] - prev_candle['open'])
            current_body_size = abs(current_candle['close'] - current_candle['open'])
            
            # Skip if bodies are too small
            if prev_body_size < (prev_candle['high'] - prev_candle['low']) * 0.3:
                continue
            if current_body_size < (current_candle['high'] - current_candle['low']) * 0.3:
                continue
            
            # Bullish Engulfing
            if (prev_candle['close'] < prev_candle['open'] and  # Previous bearish
                current_candle['close'] > current_candle['open'] and  # Current bullish
                current_candle['open'] < prev_candle['close'] and  # Opens below prev close
                current_candle['close'] > prev_candle['open']):  # Closes above prev open
                
                patterns.append({
                    'timestamp': current_candle['timestamp'],
                    'pattern': 'bullish_engulfing',
                    'type': 'bullish_reversal',
                    'strength': self._calculate_engulfing_strength(current_candle, prev_candle),
                    'candle_data': current_candle,
                    'prev_candle_data': prev_candle
                })
            
            # Bearish Engulfing
            elif (prev_candle['close'] > prev_candle['open'] and  # Previous bullish
                  current_candle['close'] < current_candle['open'] and  # Current bearish
                  current_candle['open'] > prev_candle['close'] and  # Opens above prev close
                  current_candle['close'] < prev_candle['open']):  # Closes below prev open
                
                patterns.append({
                    'timestamp': current_candle['timestamp'],
                    'pattern': 'bearish_engulfing',
                    'type': 'bearish_reversal',
                    'strength': self._calculate_engulfing_strength(current_candle, prev_candle),
                    'candle_data': current_candle,
                    'prev_candle_data': prev_candle
                })
        
        return patterns
    
    def _detect_inside_outside_bars(self, data: List[Dict]) -> List[Dict]:
        """Detect inside and outside bar patterns"""
        if len(data) < 2:
            return []
        
        patterns = []
        
        for i in range(1, len(data)):
            prev_candle = data[i-1]
            current_candle = data[i]
            
            # Inside Bar
            if (current_candle['high'] < prev_candle['high'] and 
                current_candle['low'] > prev_candle['low']):
                
                patterns.append({
                    'timestamp': current_candle['timestamp'],
                    'pattern': 'inside_bar',
                    'type': 'consolidation',
                    'strength': self._calculate_inside_bar_strength(current_candle, prev_candle),
                    'candle_data': current_candle,
                    'mother_bar': prev_candle
                })
            
            # Outside Bar
            elif (current_candle['high'] > prev_candle['high'] and 
                  current_candle['low'] < prev_candle['low']):
                
                patterns.append({
                    'timestamp': current_candle['timestamp'],
                    'pattern': 'outside_bar',
                    'type': 'expansion',
                    'strength': self._calculate_outside_bar_strength(current_candle, prev_candle),
                    'candle_data': current_candle,
                    'engulfed_bar': prev_candle
                })
        
        return patterns
    
    def detect_support_resistance(self, data: List[Dict], lookback_period: int = 20) -> List[Dict]:
        """Detect support and resistance levels using pivot points"""
        if len(data) < lookback_period * 2:
            return []
        
        support_resistance_levels = []
        
        # Find pivot highs and lows
        for i in range(lookback_period, len(data) - lookback_period):
            current_high = data[i]['high']
            current_low = data[i]['low']
            
            # Check for pivot high
            is_pivot_high = True
            for j in range(i - lookback_period, i + lookback_period + 1):
                if j != i and data[j]['high'] >= current_high:
                    is_pivot_high = False
                    break
            
            if is_pivot_high:
                # Check how many times this level has been tested
                test_count = self._count_level_tests(data, current_high, i, 'resistance')
                
                support_resistance_levels.append({
                    'timestamp': data[i]['timestamp'],
                    'level': current_high,
                    'type': 'resistance',
                    'strength': min(test_count * 20, 100),
                    'test_count': test_count,
                    'last_test': data[i]['timestamp']
                })
            
            # Check for pivot low
            is_pivot_low = True
            for j in range(i - lookback_period, i + lookback_period + 1):
                if j != i and data[j]['low'] <= current_low:
                    is_pivot_low = False
                    break
            
            if is_pivot_low:
                # Check how many times this level has been tested
                test_count = self._count_level_tests(data, current_low, i, 'support')
                
                support_resistance_levels.append({
                    'timestamp': data[i]['timestamp'],
                    'level': current_low,
                    'type': 'support',
                    'strength': min(test_count * 20, 100),
                    'test_count': test_count,
                    'last_test': data[i]['timestamp']
                })
        
        return support_resistance_levels
    
    def detect_breakouts(self, data: List[Dict], support_resistance_levels: List[Dict]) -> List[Dict]:
        """Detect breakouts from support/resistance levels"""
        if not support_resistance_levels:
            return []
        
        breakout_signals = []
        
        for level in support_resistance_levels:
            level_price = level['level']
            level_type = level['type']
            
            # Find level index
            level_index = None
            for i, candle in enumerate(data):
                if candle['timestamp'] == level['timestamp']:
                    level_index = i
                    break
            
            if level_index is None or level_index >= len(data) - 10:
                continue
            
            # Look for breakouts after level formation
            for i in range(level_index + 1, len(data)):
                candle = data[i]
                
                if level_type == 'resistance':
                    # Resistance breakout (bullish)
                    if (candle['close'] > level_price * 1.005 and  # Close above level
                        candle['volume'] > self._get_avg_volume(data, i, 10) * 1.5):  # Volume confirmation
                        
                        # Check for retest
                        retest_confirmed = self._check_for_retest(data, i, level_price, 'resistance')
                        
                        breakout_signals.append({
                            'timestamp': candle['timestamp'],
                            'type': 'resistance_breakout',
                            'direction': 'bullish',
                            'level_price': level_price,
                            'breakout_price': candle['close'],
                            'volume': candle['volume'],
                            'retest_confirmed': retest_confirmed,
                            'strength': self._calculate_breakout_strength(candle, level, data, i)
                        })
                        break
                
                elif level_type == 'support':
                    # Support breakdown (bearish)
                    if (candle['close'] < level_price * 0.995 and  # Close below level
                        candle['volume'] > self._get_avg_volume(data, i, 10) * 1.5):  # Volume confirmation
                        
                        # Check for retest
                        retest_confirmed = self._check_for_retest(data, i, level_price, 'support')
                        
                        breakout_signals.append({
                            'timestamp': candle['timestamp'],
                            'type': 'support_breakdown',
                            'direction': 'bearish',
                            'level_price': level_price,
                            'breakout_price': candle['close'],
                            'volume': candle['volume'],
                            'retest_confirmed': retest_confirmed,
                            'strength': self._calculate_breakout_strength(candle, level, data, i)
                        })
                        break
        
        return breakout_signals
    
    def detect_false_breakouts(self, data: List[Dict], breakout_signals: List[Dict]) -> List[Dict]:
        """Detect false breakouts (liquidity sweeps)"""
        if not breakout_signals:
            return []
        
        false_breakout_signals = []
        
        for breakout in breakout_signals:
            breakout_price = breakout['breakout_price']
            level_price = breakout['level_price']
            direction = breakout['direction']
            
            # Find breakout index
            breakout_index = None
            for i, candle in enumerate(data):
                if candle['timestamp'] == breakout['timestamp']:
                    breakout_index = i
                    break
            
            if breakout_index is None or breakout_index >= len(data) - 5:
                continue
            
            # Check for false breakout (quick reversal)
            for i in range(breakout_index + 1, min(len(data), breakout_index + 10)):
                candle = data[i]
                
                if direction == 'bullish':
                    # False bullish breakout: quick return below level
                    if candle['close'] < level_price * 0.998:
                        false_breakout_signals.append({
                            'timestamp': candle['timestamp'],
                            'type': 'false_breakout',
                            'original_direction': 'bullish',
                            'new_direction': 'bearish',
                            'level_price': level_price,
                            'breakout_price': breakout_price,
                            'reversal_price': candle['close'],
                            'bars_to_reversal': i - breakout_index
                        })
                        break
                
                elif direction == 'bearish':
                    # False bearish breakout: quick return above level
                    if candle['close'] > level_price * 1.002:
                        false_breakout_signals.append({
                            'timestamp': candle['timestamp'],
                            'type': 'false_breakout',
                            'original_direction': 'bearish',
                            'new_direction': 'bullish',
                            'level_price': level_price,
                            'breakout_price': breakout_price,
                            'reversal_price': candle['close'],
                            'bars_to_reversal': i - breakout_index
                        })
                        break
        
        return false_breakout_signals
    
    def analyze_price_action(self, data: List[Dict]) -> Dict[str, Any]:
        """Complete price action analysis"""
        if not data or len(data) < 20:
            return {}
        
        try:
            # Detect candlestick patterns
            candlestick_patterns = self.detect_candlestick_patterns(data)
            
            # Detect support/resistance
            support_resistance = self.detect_support_resistance(data)
            
            # Detect breakouts
            breakout_signals = self.detect_breakouts(data, support_resistance)
            
            # Detect false breakouts
            false_breakouts = self.detect_false_breakouts(data, breakout_signals)
            
            # Analyze current market structure
            current_structure = self._analyze_current_structure(data, support_resistance)
            
            return {
                'candlestick_patterns': candlestick_patterns,
                'support_resistance': support_resistance,
                'breakout_signals': breakout_signals,
                'false_breakouts': false_breakouts,
                'current_structure': current_structure,
                'summary': self._generate_price_action_summary(
                    candlestick_patterns, support_resistance, breakout_signals, false_breakouts
                )
            }
            
        except Exception as e:
            logging.error(f"Error in price action analysis: {str(e)}")
            return {}
    
    def _calculate_pattern_strength(self, current: Dict, prev: Dict, next: Dict) -> float:
        """Calculate candlestick pattern strength"""
        try:
            # Volume consideration
            volume_factor = 1.0
            if current['volume'] > prev['volume'] * 1.5:
                volume_factor = 1.5
            
            # Size consideration
            body_size = abs(current['close'] - current['open'])
            range_size = current['high'] - current['low']
            size_factor = body_size / range_size if range_size > 0 else 0.5
            
            # Context consideration (trend)
            trend_factor = 1.0
            if prev['close'] > prev['open'] and next['close'] < next['open']:
                trend_factor = 1.3  # Reversal confirmation
            
            return min(volume_factor * size_factor * trend_factor * 50, 100)
            
        except:
            return 50.0
    
    def _calculate_engulfing_strength(self, current: Dict, prev: Dict) -> float:
        """Calculate engulfing pattern strength"""
        try:
            current_body = abs(current['close'] - current['open'])
            prev_body = abs(prev['close'] - prev['open'])
            
            size_ratio = current_body / prev_body if prev_body > 0 else 1
            volume_factor = current['volume'] / prev['volume'] if prev['volume'] > 0 else 1
            
            return min(size_ratio * volume_factor * 30, 100)
            
        except:
            return 50.0
    
    def _calculate_inside_bar_strength(self, current: Dict, prev: Dict) -> float:
        """Calculate inside bar strength"""
        try:
            prev_range = prev['high'] - prev['low']
            current_range = current['high'] - current['low']
            
            compression_ratio = 1 - (current_range / prev_range) if prev_range > 0 else 0
            return min(compression_ratio * 100, 100)
            
        except:
            return 50.0
    
    def _calculate_outside_bar_strength(self, current: Dict, prev: Dict) -> float:
        """Calculate outside bar strength"""
        try:
            prev_range = prev['high'] - prev['low']
            current_range = current['high'] - current['low']
            
            expansion_ratio = (current_range / prev_range) - 1 if prev_range > 0 else 0
            volume_factor = current['volume'] / prev['volume'] if prev['volume'] > 0 else 1
            
            return min(expansion_ratio * volume_factor * 50, 100)
            
        except:
            return 50.0
    
    def _count_level_tests(self, data: List[Dict], level: float, start_index: int, level_type: str) -> int:
        """Count how many times a level has been tested"""
        test_count = 1  # Include the initial touch
        tolerance = level * 0.002  # 0.2% tolerance
        
        for i in range(start_index + 1, len(data)):
            candle = data[i]
            
            if level_type == 'resistance':
                if abs(candle['high'] - level) <= tolerance:
                    test_count += 1
            else:  # support
                if abs(candle['low'] - level) <= tolerance:
                    test_count += 1
        
        return test_count
    
    def _get_avg_volume(self, data: List[Dict], index: int, period: int) -> float:
        """Get average volume for a period"""
        start_index = max(0, index - period)
        volumes = [data[i]['volume'] for i in range(start_index, index)]
        return np.mean(volumes) if volumes else 0
    
    def _check_for_retest(self, data: List[Dict], breakout_index: int, level_price: float, level_type: str) -> bool:
        """Check if breakout has been retested"""
        for i in range(breakout_index + 1, min(len(data), breakout_index + 10)):
            candle = data[i]
            
            if level_type == 'resistance':
                # Check if price retests the broken resistance as support
                if abs(candle['low'] - level_price) <= level_price * 0.01:
                    return True
            else:  # support
                # Check if price retests the broken support as resistance
                if abs(candle['high'] - level_price) <= level_price * 0.01:
                    return True
        
        return False
    
    def _calculate_breakout_strength(self, candle: Dict, level: Dict, data: List[Dict], index: int) -> float:
        """Calculate breakout strength"""
        try:
            # Volume strength
            avg_volume = self._get_avg_volume(data, index, 10)
            volume_strength = candle['volume'] / avg_volume if avg_volume > 0 else 1
            
            # Price strength
            level_price = level['level']
            price_strength = abs(candle['close'] - level_price) / level_price
            
            # Level strength
            level_strength = level.get('strength', 50) / 100
            
            return min(volume_strength * price_strength * level_strength * 100, 100)
            
        except:
            return 50.0
    
    def _analyze_current_structure(self, data: List[Dict], support_resistance: List[Dict]) -> Dict[str, Any]:
        """Analyze current market structure"""
        if len(data) < 10:
            return {}
        
        recent_data = data[-10:]
        current_price = data[-1]['close']
        
        # Find nearest support/resistance levels
        nearest_support = None
        nearest_resistance = None
        
        for level in support_resistance:
            if level['type'] == 'support' and level['level'] < current_price:
                if nearest_support is None or level['level'] > nearest_support['level']:
                    nearest_support = level
            elif level['type'] == 'resistance' and level['level'] > current_price:
                if nearest_resistance is None or level['level'] < nearest_resistance['level']:
                    nearest_resistance = level
        
        # Analyze recent price action
        recent_highs = [candle['high'] for candle in recent_data]
        recent_lows = [candle['low'] for candle in recent_data]
        
        higher_highs = sum(1 for i in range(1, len(recent_highs)) if recent_highs[i] > recent_highs[i-1])
        lower_lows = sum(1 for i in range(1, len(recent_lows)) if recent_lows[i] < recent_lows[i-1])
        
        if higher_highs > lower_lows:
            trend = 'bullish'
        elif lower_lows > higher_highs:
            trend = 'bearish'
        else:
            trend = 'ranging'
        
        return {
            'current_price': current_price,
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'trend': trend,
            'higher_highs': higher_highs,
            'lower_lows': lower_lows,
            'range_bound': abs(higher_highs - lower_lows) <= 1
        }
    
    def _generate_price_action_summary(self, patterns: List[Dict], support_resistance: List[Dict], 
                                     breakouts: List[Dict], false_breakouts: List[Dict]) -> Dict[str, Any]:
        """Generate price action summary"""
        recent_patterns = [p for p in patterns[-10:] if p] if patterns else []
        recent_breakouts = [b for b in breakouts[-5:] if b] if breakouts else []
        
        bullish_signals = len([p for p in recent_patterns if 'bullish' in p.get('type', '')])
        bearish_signals = len([p for p in recent_patterns if 'bearish' in p.get('type', '')])
        
        return {
            'total_patterns': len(patterns),
            'total_support_resistance': len(support_resistance),
            'total_breakouts': len(breakouts),
            'total_false_breakouts': len(false_breakouts),
            'recent_bullish_signals': bullish_signals,
            'recent_bearish_signals': bearish_signals,
            'recent_breakouts': len(recent_breakouts),
            'false_breakout_rate': len(false_breakouts) / len(breakouts) * 100 if breakouts else 0
        }