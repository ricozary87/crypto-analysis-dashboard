"""
Smart Money Concept (SMC) Analyzer
Detects CHoCH, BOS, Order Block, FVG, Liquidity Pool/Sweep, EQH/EQL
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

class SMCAnalyzer:
    def __init__(self):
        self.swing_period = 5  # Period for swing high/low detection
        self.min_swing_strength = 3  # Minimum bars for swing confirmation
        
    def identify_swing_points(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        """Identify swing highs and lows"""
        if len(data) < self.swing_period * 2 + 1:
            return {'swing_highs': [], 'swing_lows': []}
        
        swing_highs = []
        swing_lows = []
        
        for i in range(self.swing_period, len(data) - self.swing_period):
            current_high = data[i]['high']
            current_low = data[i]['low']
            
            # Check for swing high
            is_swing_high = True
            for j in range(i - self.swing_period, i + self.swing_period + 1):
                if j != i and data[j]['high'] >= current_high:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                swing_highs.append({
                    'timestamp': int(data[i]['timestamp']) if isinstance(data[i]['timestamp'], str) else data[i]['timestamp'],
                    'index': i,
                    'price': current_high,
                    'type': 'swing_high'
                })
            
            # Check for swing low
            is_swing_low = True
            for j in range(i - self.swing_period, i + self.swing_period + 1):
                if j != i and data[j]['low'] <= current_low:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                swing_lows.append({
                    'timestamp': int(data[i]['timestamp']) if isinstance(data[i]['timestamp'], str) else data[i]['timestamp'],
                    'index': i,
                    'price': current_low,
                    'type': 'swing_low'
                })
        
        return {'swing_highs': swing_highs, 'swing_lows': swing_lows}
    
    def detect_choch_bos(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect Change of Character (CHoCH) and Break of Structure (BOS)"""
        if not swing_points or len(swing_points['swing_highs']) < 2 or len(swing_points['swing_lows']) < 2:
            return []
        
        choch_bos_signals = []
        swing_highs = swing_points['swing_highs']
        swing_lows = swing_points['swing_lows']
        
        # Combine and sort swing points by timestamp
        all_swings = swing_highs + swing_lows
        # Ensure all timestamps are integers for comparison
        for swing in all_swings:
            swing['timestamp'] = int(swing['timestamp']) if isinstance(swing['timestamp'], str) else swing['timestamp']
        all_swings.sort(key=lambda x: x['timestamp'])
        
        if len(all_swings) < 3:
            return []
        
        # Track market structure
        for i in range(2, len(all_swings)):
            current_swing = all_swings[i]
            prev_swing = all_swings[i-1]
            prev_prev_swing = all_swings[i-2]
            
            # Detect CHoCH (Change of Character)
            if (prev_prev_swing['type'] == 'swing_high' and 
                prev_swing['type'] == 'swing_low' and 
                current_swing['type'] == 'swing_high'):
                
                # Bullish CHoCH: Higher High after Lower Low
                if (current_swing['price'] > prev_prev_swing['price'] and 
                    prev_swing['price'] < self._get_previous_swing_low(all_swings, i-1)['price']):
                    
                    choch_bos_signals.append({
                        'timestamp': current_swing['timestamp'],
                        'type': 'CHoCH',
                        'direction': 'bullish',
                        'price': current_swing['price'],
                        'strength': self._calculate_signal_strength(data, current_swing, prev_swing)
                    })
            
            elif (prev_prev_swing['type'] == 'swing_low' and 
                  prev_swing['type'] == 'swing_high' and 
                  current_swing['type'] == 'swing_low'):
                
                # Bearish CHoCH: Lower Low after Higher High
                if (current_swing['price'] < prev_prev_swing['price'] and 
                    prev_swing['price'] > self._get_previous_swing_high(all_swings, i-1)['price']):
                    
                    choch_bos_signals.append({
                        'timestamp': current_swing['timestamp'],
                        'type': 'CHoCH',
                        'direction': 'bearish',
                        'price': current_swing['price'],
                        'strength': self._calculate_signal_strength(data, current_swing, prev_swing)
                    })
            
            # Detect BOS (Break of Structure)
            # BOS occurs when price breaks a significant swing level
            if current_swing['type'] == 'swing_high':
                # Look for breaks above previous swing highs
                for j in range(i-1, -1, -1):
                    if all_swings[j]['type'] == 'swing_high':
                        if current_swing['price'] > all_swings[j]['price'] * 1.002:  # 0.2% buffer
                            choch_bos_signals.append({
                                'timestamp': current_swing['timestamp'],
                                'type': 'BOS',
                                'direction': 'bullish',
                                'price': current_swing['price'],
                                'broken_level': all_swings[j]['price'],
                                'strength': self._calculate_signal_strength(data, current_swing, all_swings[j])
                            })
                        break
            
            elif current_swing['type'] == 'swing_low':
                # Look for breaks below previous swing lows
                for j in range(i-1, -1, -1):
                    if all_swings[j]['type'] == 'swing_low':
                        if current_swing['price'] < all_swings[j]['price'] * 0.998:  # 0.2% buffer
                            choch_bos_signals.append({
                                'timestamp': current_swing['timestamp'],
                                'type': 'BOS',
                                'direction': 'bearish',
                                'price': current_swing['price'],
                                'broken_level': all_swings[j]['price'],
                                'strength': self._calculate_signal_strength(data, current_swing, all_swings[j])
                            })
                        break
        
        return choch_bos_signals
    
    def detect_order_blocks(self, data: List[Dict], choch_bos_signals: List[Dict]) -> List[Dict]:
        """Detect Order Blocks (OB) - areas where institutions place large orders"""
        if not choch_bos_signals:
            return []
        
        order_blocks = []
        
        for signal in choch_bos_signals:
            if signal['type'] == 'CHoCH' or signal['type'] == 'BOS':
                # Find the candle that created the signal
                signal_timestamp = signal['timestamp']
                signal_index = None
                
                for i, candle in enumerate(data):
                    if candle['timestamp'] == signal_timestamp:
                        signal_index = i
                        break
                
                if signal_index is None or signal_index < 10:
                    continue
                
                # Look for order block in previous candles
                if signal['direction'] == 'bullish':
                    # Bullish OB: Last bearish candle before bullish move
                    for i in range(signal_index - 1, max(0, signal_index - 10), -1):
                        if data[i]['close'] < data[i]['open']:  # Bearish candle
                            order_blocks.append({
                                'timestamp': data[i]['timestamp'],
                                'type': 'bullish_ob',
                                'high': data[i]['high'],
                                'low': data[i]['low'],
                                'open': data[i]['open'],
                                'close': data[i]['close'],
                                'volume': data[i]['volume'],
                                'signal_type': signal['type'],
                                'strength': signal.get('strength', 0)
                            })
                            break
                
                elif signal['direction'] == 'bearish':
                    # Bearish OB: Last bullish candle before bearish move
                    for i in range(signal_index - 1, max(0, signal_index - 10), -1):
                        if data[i]['close'] > data[i]['open']:  # Bullish candle
                            order_blocks.append({
                                'timestamp': data[i]['timestamp'],
                                'type': 'bearish_ob',
                                'high': data[i]['high'],
                                'low': data[i]['low'],
                                'open': data[i]['open'],
                                'close': data[i]['close'],
                                'volume': data[i]['volume'],
                                'signal_type': signal['type'],
                                'strength': signal.get('strength', 0)
                            })
                            break
        
        return order_blocks
    
    def detect_fvg(self, data: List[Dict]) -> List[Dict]:
        """Detect Fair Value Gaps (FVG) - price gaps in the market"""
        if len(data) < 3:
            return []
        
        fvg_signals = []
        
        for i in range(1, len(data) - 1):
            prev_candle = data[i-1]
            current_candle = data[i]
            next_candle = data[i+1]
            
            # Bullish FVG: Gap between prev low and next high
            if (prev_candle['low'] > next_candle['high'] and 
                current_candle['close'] > current_candle['open']):  # Bullish impulse candle
                
                gap_size = prev_candle['low'] - next_candle['high']
                if gap_size > 0:
                    fvg_signals.append({
                        'timestamp': current_candle['timestamp'],
                        'type': 'bullish_fvg',
                        'upper_level': prev_candle['low'],
                        'lower_level': next_candle['high'],
                        'gap_size': gap_size,
                        'impulse_candle': {
                            'open': current_candle['open'],
                            'close': current_candle['close'],
                            'high': current_candle['high'],
                            'low': current_candle['low']
                        }
                    })
            
            # Bearish FVG: Gap between prev high and next low
            elif (prev_candle['high'] < next_candle['low'] and 
                  current_candle['close'] < current_candle['open']):  # Bearish impulse candle
                
                gap_size = next_candle['low'] - prev_candle['high']
                if gap_size > 0:
                    fvg_signals.append({
                        'timestamp': current_candle['timestamp'],
                        'type': 'bearish_fvg',
                        'upper_level': next_candle['low'],
                        'lower_level': prev_candle['high'],
                        'gap_size': gap_size,
                        'impulse_candle': {
                            'open': current_candle['open'],
                            'close': current_candle['close'],
                            'high': current_candle['high'],
                            'low': current_candle['low']
                        }
                    })
        
        return fvg_signals
    
    def detect_liquidity_levels(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect liquidity levels and potential sweeps"""
        if not swing_points:
            return []
        
        liquidity_levels = []
        swing_highs = swing_points['swing_highs']
        swing_lows = swing_points['swing_lows']
        
        # Equal Highs (EQH)
        for i in range(len(swing_highs) - 1):
            for j in range(i + 1, len(swing_highs)):
                high1 = swing_highs[i]
                high2 = swing_highs[j]
                
                # Check if highs are approximately equal (within 0.5%)
                if abs(high1['price'] - high2['price']) / high1['price'] < 0.005:
                    liquidity_levels.append({
                        'timestamp': high2['timestamp'],
                        'type': 'EQH',
                        'price': (high1['price'] + high2['price']) / 2,
                        'first_touch': high1['timestamp'],
                        'second_touch': high2['timestamp'],
                        'strength': self._calculate_liquidity_strength(data, high1, high2)
                    })
        
        # Equal Lows (EQL)
        for i in range(len(swing_lows) - 1):
            for j in range(i + 1, len(swing_lows)):
                low1 = swing_lows[i]
                low2 = swing_lows[j]
                
                # Check if lows are approximately equal (within 0.5%)
                if abs(low1['price'] - low2['price']) / low1['price'] < 0.005:
                    liquidity_levels.append({
                        'timestamp': low2['timestamp'],
                        'type': 'EQL',
                        'price': (low1['price'] + low2['price']) / 2,
                        'first_touch': low1['timestamp'],
                        'second_touch': low2['timestamp'],
                        'strength': self._calculate_liquidity_strength(data, low1, low2)
                    })
        
        return liquidity_levels
    
    def detect_liquidity_sweeps(self, data: List[Dict], liquidity_levels: List[Dict]) -> List[Dict]:
        """Detect liquidity sweeps (false breakouts)"""
        if not liquidity_levels:
            return []
        
        sweep_signals = []
        
        for level in liquidity_levels:
            level_price = level['price']
            level_timestamp = level['timestamp']
            
            # Find the level index in data
            level_index = None
            for i, candle in enumerate(data):
                if candle['timestamp'] == level_timestamp:
                    level_index = i
                    break
            
            if level_index is None or level_index >= len(data) - 5:
                continue
            
            # Look for sweeps after the level formation
            for i in range(level_index + 1, min(len(data), level_index + 20)):
                candle = data[i]
                
                if level['type'] == 'EQH':
                    # Look for sweep above EQH followed by rejection
                    if candle['high'] > level_price * 1.002:  # 0.2% above level
                        # Check for rejection in next few candles
                        rejected = False
                        for j in range(i + 1, min(len(data), i + 5)):
                            if data[j]['close'] < level_price * 0.998:  # Close below level
                                rejected = True
                                break
                        
                        if rejected:
                            sweep_signals.append({
                                'timestamp': candle['timestamp'],
                                'type': 'liquidity_sweep',
                                'direction': 'bearish',
                                'level_type': 'EQH',
                                'level_price': level_price,
                                'sweep_price': candle['high'],
                                'rejection_confirmed': True
                            })
                            break
                
                elif level['type'] == 'EQL':
                    # Look for sweep below EQL followed by rejection
                    if candle['low'] < level_price * 0.998:  # 0.2% below level
                        # Check for rejection in next few candles
                        rejected = False
                        for j in range(i + 1, min(len(data), i + 5)):
                            if data[j]['close'] > level_price * 1.002:  # Close above level
                                rejected = True
                                break
                        
                        if rejected:
                            sweep_signals.append({
                                'timestamp': candle['timestamp'],
                                'type': 'liquidity_sweep',
                                'direction': 'bullish',
                                'level_type': 'EQL',
                                'level_price': level_price,
                                'sweep_price': candle['low'],
                                'rejection_confirmed': True
                            })
                            break
        
        return sweep_signals
    
    def analyze_market_structure(self, data: List[Dict]) -> Dict[str, Any]:
        """Complete SMC analysis"""
        if not data or len(data) < 20:
            return {}
        
        try:
            # Step 1: Identify swing points
            swing_points = self.identify_swing_points(data)
            
            # Step 2: Detect CHoCH and BOS
            choch_bos_signals = self.detect_choch_bos(data, swing_points)
            
            # Step 3: Detect Order Blocks
            order_blocks = self.detect_order_blocks(data, choch_bos_signals)
            
            # Step 4: Detect FVG
            fvg_signals = self.detect_fvg(data)
            
            # Step 5: Detect Liquidity Levels
            liquidity_levels = self.detect_liquidity_levels(data, swing_points)
            
            # Step 6: Detect Liquidity Sweeps
            liquidity_sweeps = self.detect_liquidity_sweeps(data, liquidity_levels)
            
            # Step 7: Determine overall market structure
            market_structure = self._determine_market_structure(choch_bos_signals, order_blocks)
            
            return {
                'swing_points': swing_points,
                'choch_bos_signals': choch_bos_signals,
                'order_blocks': order_blocks,
                'fvg_signals': fvg_signals,
                'liquidity_levels': liquidity_levels,
                'liquidity_sweeps': liquidity_sweeps,
                'market_structure': market_structure,
                'summary': self._generate_smc_summary(choch_bos_signals, order_blocks, fvg_signals, liquidity_sweeps)
            }
            
        except Exception as e:
            logging.error(f"Error in SMC analysis: {str(e)}")
            return {}
    
    def _get_previous_swing_low(self, all_swings: List[Dict], current_index: int) -> Dict:
        """Get previous swing low"""
        for i in range(current_index - 1, -1, -1):
            if all_swings[i]['type'] == 'swing_low':
                return all_swings[i]
        return all_swings[0] if all_swings else {}
    
    def _get_previous_swing_high(self, all_swings: List[Dict], current_index: int) -> Dict:
        """Get previous swing high"""
        for i in range(current_index - 1, -1, -1):
            if all_swings[i]['type'] == 'swing_high':
                return all_swings[i]
        return all_swings[0] if all_swings else {}
    
    def _calculate_signal_strength(self, data: List[Dict], swing1: Dict, swing2: Dict) -> float:
        """Calculate signal strength based on price movement and volume"""
        try:
            price_diff = abs(swing1['price'] - swing2['price'])
            price_strength = price_diff / swing1['price'] * 100
            
            # Add volume consideration if available
            volume_strength = 1.0
            if 'volume' in swing1 and 'volume' in swing2:
                avg_volume = (swing1['volume'] + swing2['volume']) / 2
                volume_strength = min(avg_volume / 1000, 2.0)  # Cap at 2.0
            
            return min(price_strength * volume_strength, 100)
        except:
            return 50.0  # Default strength
    
    def _calculate_liquidity_strength(self, data: List[Dict], point1: Dict, point2: Dict) -> float:
        """Calculate liquidity level strength"""
        try:
            # Consider time between touches
            time_diff = abs(point2['index'] - point1['index'])
            time_strength = min(time_diff / 20, 2.0)  # More time = stronger level
            
            # Consider price precision
            price_diff = abs(point1['price'] - point2['price'])
            precision_strength = 1.0 / (1.0 + price_diff / point1['price'] * 100)
            
            return min(time_strength * precision_strength * 50, 100)
        except:
            return 50.0
    
    def _determine_market_structure(self, choch_bos_signals: List[Dict], order_blocks: List[Dict]) -> Dict[str, Any]:
        """Determine overall market structure"""
        if not choch_bos_signals:
            return {'trend': 'neutral', 'strength': 0}
        
        # Analyze recent signals (last 5)
        recent_signals = choch_bos_signals[-5:] if len(choch_bos_signals) >= 5 else choch_bos_signals
        
        bullish_count = sum(1 for signal in recent_signals if signal['direction'] == 'bullish')
        bearish_count = sum(1 for signal in recent_signals if signal['direction'] == 'bearish')
        
        if bullish_count > bearish_count:
            trend = 'bullish'
            strength = (bullish_count / len(recent_signals)) * 100
        elif bearish_count > bullish_count:
            trend = 'bearish'
            strength = (bearish_count / len(recent_signals)) * 100
        else:
            trend = 'neutral'
            strength = 0
        
        return {
            'trend': trend,
            'strength': strength,
            'recent_signals': len(recent_signals),
            'order_blocks_count': len(order_blocks)
        }
    
    def _generate_smc_summary(self, choch_bos_signals: List[Dict], order_blocks: List[Dict], 
                             fvg_signals: List[Dict], liquidity_sweeps: List[Dict]) -> Dict[str, Any]:
        """Generate SMC analysis summary"""
        return {
            'total_choch_bos': len(choch_bos_signals),
            'total_order_blocks': len(order_blocks),
            'total_fvg': len(fvg_signals),
            'total_liquidity_sweeps': len(liquidity_sweeps),
            'bullish_signals': len([s for s in choch_bos_signals if s['direction'] == 'bullish']),
            'bearish_signals': len([s for s in choch_bos_signals if s['direction'] == 'bearish']),
            'recent_activity': len([s for s in choch_bos_signals[-10:] if s]) if choch_bos_signals else 0
        }