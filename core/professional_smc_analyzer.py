"""
Professional Smart Money Concept (SMC) Analyzer
Upgraded from OkxCandleTracker with advanced pattern detection:
- CHoCH (Change of Character) detection
- BOS (Break of Structure) detection  
- Order Block identification
- FVG (Fair Value Gap) detection
- Liquidity Pool/Sweep detection
- EQH/EQL (Equal Highs/Lows) detection
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from .inducement_detector import InducementDetector

logger = logging.getLogger(__name__)

class ProfessionalSMCAnalyzer:
    """Professional SMC Analyzer with advanced pattern detection"""
    
    def __init__(self):
        self.swing_period = 5  # Period for swing high/low detection
        self.min_swing_strength = 3  # Minimum bars for swing confirmation
        self.inducement_detector = InducementDetector()  # Initialize inducement detector
        self.logger = logging.getLogger(__name__)
        
    def analyze_comprehensive(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Comprehensive SMC analysis combining all detection methods"""
        
        try:
            if df is None or df.empty:
                return self._empty_smc_analysis()
            
            # Convert DataFrame to list of dicts for compatibility
            data = self._convert_df_to_data(df)
            
            # 1. Identify swing points
            swing_points = self.identify_swing_points(data)
            
            # 2. Detect CHoCH and BOS patterns
            choch_bos_signals = self.detect_choch_bos(data, swing_points)
            
            # 3. Detect Order Blocks
            order_blocks = self.detect_order_blocks(data, swing_points)
            
            # 4. Detect Fair Value Gaps (FVG)
            fvg_signals = self.detect_fvg(data)
            
            # 5. Detect Liquidity Sweeps
            liquidity_sweeps = self.detect_liquidity_sweeps(data, swing_points)
            
            # 6. Detect Equal Highs/Lows (EQH/EQL)
            eqh_eql_signals = self.detect_eqh_eql(data, swing_points)
            
            # 7. Detect Inducement Patterns
            inducement_patterns = self.inducement_detector.detect_inducements(data, swing_points)
            
            # 8. Determine market structure
            market_structure = self._determine_market_structure(choch_bos_signals, order_blocks)
            
            # 9. Generate comprehensive summary
            smc_summary = self._generate_smc_summary(
                choch_bos_signals, order_blocks, fvg_signals, 
                liquidity_sweeps, eqh_eql_signals, inducement_patterns
            )
            
            # 10. Generate trading signals
            trading_signals = self._generate_trading_signals(
                choch_bos_signals, order_blocks, fvg_signals, 
                liquidity_sweeps, market_structure, inducement_patterns
            )
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': int(df['timestamp'].iloc[-1].timestamp() * 1000) if 'timestamp' in df.columns else int(datetime.now().timestamp() * 1000),
                'current_price': float(df['close'].iloc[-1]),
                'swing_points': swing_points,
                'choch_bos_signals': choch_bos_signals,
                'order_blocks': order_blocks,
                'fvg_signals': fvg_signals,
                'liquidity_sweeps': liquidity_sweeps,
                'eqh_eql_signals': eqh_eql_signals,
                'inducement_patterns': inducement_patterns,
                'market_structure': market_structure,
                'smc_summary': smc_summary,
                'trading_signals': trading_signals,
                'confidence_score': self._calculate_confidence_score(
                    choch_bos_signals, order_blocks, fvg_signals, liquidity_sweeps, inducement_patterns
                )
            }
            
        except Exception as e:
            self.logger.error(f"Professional SMC analysis error for {symbol}: {e}")
            return self._empty_smc_analysis()
    
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
                    'timestamp': int(data[i]['timestamp'].timestamp() * 1000) if hasattr(data[i]['timestamp'], 'timestamp') else int(data[i]['timestamp']),
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
                    'timestamp': int(data[i]['timestamp'].timestamp() * 1000) if hasattr(data[i]['timestamp'], 'timestamp') else int(data[i]['timestamp']),
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
            # BOS occurs when price breaks significant support/resistance
            if current_swing['type'] == 'swing_high':
                recent_highs = [s for s in swing_highs if s['timestamp'] < current_swing['timestamp']][-3:]
                if recent_highs:
                    max_recent_high = max(recent_highs, key=lambda x: x['price'])
                    if current_swing['price'] > max_recent_high['price'] * 1.01:  # 1% break
                        choch_bos_signals.append({
                            'timestamp': current_swing['timestamp'],
                            'type': 'BOS',
                            'direction': 'bullish',
                            'price': current_swing['price'],
                            'strength': self._calculate_signal_strength(data, current_swing, max_recent_high)
                        })
            
            elif current_swing['type'] == 'swing_low':
                recent_lows = [s for s in swing_lows if s['timestamp'] < current_swing['timestamp']][-3:]
                if recent_lows:
                    min_recent_low = min(recent_lows, key=lambda x: x['price'])
                    if current_swing['price'] < min_recent_low['price'] * 0.99:  # 1% break
                        choch_bos_signals.append({
                            'timestamp': current_swing['timestamp'],
                            'type': 'BOS',
                            'direction': 'bearish',
                            'price': current_swing['price'],
                            'strength': self._calculate_signal_strength(data, current_swing, min_recent_low)
                        })
        
        return choch_bos_signals
    
    def detect_order_blocks(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect Order Blocks (institutional interest zones)"""
        order_blocks = []
        
        if not swing_points or len(data) < 10:
            return order_blocks
        
        # Order blocks form around swing points with high volume
        for swing_high in swing_points['swing_highs']:
            idx = swing_high['index']
            if idx >= 3 and idx < len(data) - 3:
                # Look for order block formation around swing high
                block_start = max(0, idx - 3)
                block_end = min(len(data), idx + 3)
                
                # Calculate volume average
                avg_volume = sum(data[i]['volume'] for i in range(block_start, block_end)) / (block_end - block_start)
                
                # Check if volume is above average
                if avg_volume > self._get_average_volume(data) * 1.5:
                    order_blocks.append({
                        'timestamp': swing_high['timestamp'],
                        'type': 'order_block',
                        'direction': 'resistance',
                        'price_high': swing_high['price'],
                        'price_low': min(data[i]['low'] for i in range(block_start, block_end)),
                        'volume': avg_volume,
                        'strength': self._calculate_order_block_strength(data, block_start, block_end)
                    })
        
        for swing_low in swing_points['swing_lows']:
            idx = swing_low['index']
            if idx >= 3 and idx < len(data) - 3:
                # Look for order block formation around swing low
                block_start = max(0, idx - 3)
                block_end = min(len(data), idx + 3)
                
                # Calculate volume average
                avg_volume = sum(data[i]['volume'] for i in range(block_start, block_end)) / (block_end - block_start)
                
                # Check if volume is above average
                if avg_volume > self._get_average_volume(data) * 1.5:
                    order_blocks.append({
                        'timestamp': swing_low['timestamp'],
                        'type': 'order_block',
                        'direction': 'support',
                        'price_high': max(data[i]['high'] for i in range(block_start, block_end)),
                        'price_low': swing_low['price'],
                        'volume': avg_volume,
                        'strength': self._calculate_order_block_strength(data, block_start, block_end)
                    })
        
        return order_blocks
    
    def detect_fvg(self, data: List[Dict]) -> List[Dict]:
        """Detect Fair Value Gaps (FVG)"""
        fvg_signals = []
        
        if len(data) < 3:
            return fvg_signals
        
        for i in range(1, len(data) - 1):
            prev_candle = data[i-1]
            current_candle = data[i]
            next_candle = data[i+1]
            
            # Bullish FVG: Gap between prev high and next low
            if (prev_candle['high'] < next_candle['low'] and
                current_candle['close'] > current_candle['open']):  # Bullish candle
                
                gap_size = next_candle['low'] - prev_candle['high']
                if gap_size > 0:
                    fvg_signals.append({
                        'timestamp': int(current_candle['timestamp']) if isinstance(current_candle['timestamp'], (int, float)) else int(current_candle['timestamp'].timestamp() * 1000),
                        'type': 'FVG',
                        'direction': 'bullish',
                        'gap_high': next_candle['low'],
                        'gap_low': prev_candle['high'],
                        'gap_size': gap_size,
                        'strength': self._calculate_fvg_strength(gap_size, current_candle)
                    })
            
            # Bearish FVG: Gap between prev low and next high
            elif (prev_candle['low'] > next_candle['high'] and
                  current_candle['close'] < current_candle['open']):  # Bearish candle
                
                gap_size = prev_candle['low'] - next_candle['high']
                if gap_size > 0:
                    fvg_signals.append({
                        'timestamp': int(current_candle['timestamp']) if isinstance(current_candle['timestamp'], (int, float)) else int(current_candle['timestamp'].timestamp() * 1000),
                        'type': 'FVG',
                        'direction': 'bearish',
                        'gap_high': prev_candle['low'],
                        'gap_low': next_candle['high'],
                        'gap_size': gap_size,
                        'strength': self._calculate_fvg_strength(gap_size, current_candle)
                    })
        
        return fvg_signals
    
    def detect_liquidity_sweeps(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect Liquidity Pool Sweeps"""
        liquidity_sweeps = []
        
        if not swing_points or len(data) < 10:
            return liquidity_sweeps
        
        # Check for liquidity sweeps at swing highs
        for swing_high in swing_points['swing_highs']:
            idx = swing_high['index']
            if idx < len(data) - 5:
                # Look for price breaking above swing high and then reversing
                for i in range(idx + 1, min(idx + 6, len(data))):
                    if data[i]['high'] > swing_high['price'] * 1.005:  # Break above with 0.5% buffer
                        # Check for reversal within next few candles
                        reversal_found = False
                        for j in range(i + 1, min(i + 4, len(data))):
                            if data[j]['low'] < swing_high['price'] * 0.995:  # Reversal below swing high
                                reversal_found = True
                                break
                        
                        if reversal_found:
                            liquidity_sweeps.append({
                                'timestamp': int(data[i]['timestamp']) if isinstance(data[i]['timestamp'], (int, float)) else int(data[i]['timestamp'].timestamp() * 1000),
                                'type': 'liquidity_sweep',
                                'direction': 'bearish',
                                'sweep_price': data[i]['high'],
                                'original_level': swing_high['price'],
                                'strength': self._calculate_liquidity_strength(data, i, swing_high)
                            })
                            break
        
        # Check for liquidity sweeps at swing lows
        for swing_low in swing_points['swing_lows']:
            idx = swing_low['index']
            if idx < len(data) - 5:
                # Look for price breaking below swing low and then reversing
                for i in range(idx + 1, min(idx + 6, len(data))):
                    if data[i]['low'] < swing_low['price'] * 0.995:  # Break below with 0.5% buffer
                        # Check for reversal within next few candles
                        reversal_found = False
                        for j in range(i + 1, min(i + 4, len(data))):
                            if data[j]['high'] > swing_low['price'] * 1.005:  # Reversal above swing low
                                reversal_found = True
                                break
                        
                        if reversal_found:
                            liquidity_sweeps.append({
                                'timestamp': int(data[i]['timestamp']) if isinstance(data[i]['timestamp'], (int, float)) else int(data[i]['timestamp'].timestamp() * 1000),
                                'type': 'liquidity_sweep',
                                'direction': 'bullish',
                                'sweep_price': data[i]['low'],
                                'original_level': swing_low['price'],
                                'strength': self._calculate_liquidity_strength(data, i, swing_low)
                            })
                            break
        
        return liquidity_sweeps
    
    def detect_eqh_eql(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect Equal Highs (EQH) and Equal Lows (EQL)"""
        eqh_eql_signals = []
        tolerance = 0.002  # 0.2% tolerance for "equal" levels
        
        if not swing_points:
            return eqh_eql_signals
        
        # Detect Equal Highs (EQH)
        swing_highs = swing_points['swing_highs']
        for i in range(len(swing_highs) - 1):
            for j in range(i + 1, len(swing_highs)):
                high1 = swing_highs[i]
                high2 = swing_highs[j]
                
                price_diff = abs(high1['price'] - high2['price'])
                if price_diff / high1['price'] <= tolerance:
                    eqh_eql_signals.append({
                        'timestamp': high2['timestamp'],
                        'type': 'EQH',
                        'direction': 'resistance',
                        'price': (high1['price'] + high2['price']) / 2,
                        'price_diff': price_diff,
                        'strength': self._calculate_eqh_eql_strength(high1, high2)
                    })
        
        # Detect Equal Lows (EQL)
        swing_lows = swing_points['swing_lows']
        for i in range(len(swing_lows) - 1):
            for j in range(i + 1, len(swing_lows)):
                low1 = swing_lows[i]
                low2 = swing_lows[j]
                
                price_diff = abs(low1['price'] - low2['price'])
                if price_diff / low1['price'] <= tolerance:
                    eqh_eql_signals.append({
                        'timestamp': low2['timestamp'],
                        'type': 'EQL',
                        'direction': 'support',
                        'price': (low1['price'] + low2['price']) / 2,
                        'price_diff': price_diff,
                        'strength': self._calculate_eqh_eql_strength(low1, low2)
                    })
        
        return eqh_eql_signals
    
    def _generate_trading_signals(self, choch_bos_signals: List[Dict], order_blocks: List[Dict], 
                                 fvg_signals: List[Dict], liquidity_sweeps: List[Dict], 
                                 market_structure: Dict[str, Any]) -> List[Dict]:
        """Generate trading signals based on SMC analysis"""
        trading_signals = []
        
        # Recent signals only (last 10)
        recent_choch_bos = choch_bos_signals[-10:] if choch_bos_signals else []
        recent_order_blocks = order_blocks[-5:] if order_blocks else []
        recent_fvg = fvg_signals[-5:] if fvg_signals else []
        recent_liquidity = liquidity_sweeps[-5:] if liquidity_sweeps else []
        
        # Generate signals based on pattern confluences
        for signal in recent_choch_bos:
            if signal['type'] == 'CHoCH' and signal['strength'] > 60:
                # Look for confluence with order blocks
                confluence_count = 0
                supporting_patterns = []
                
                # Check for order block confluence
                for ob in recent_order_blocks:
                    if (signal['direction'] == 'bullish' and ob['direction'] == 'support' and
                        abs(signal['price'] - ob['price_low']) / signal['price'] < 0.02):
                        confluence_count += 1
                        supporting_patterns.append('order_block')
                
                # Check for FVG confluence  
                for fvg in recent_fvg:
                    if (signal['direction'] == fvg['direction'] and
                        abs(signal['timestamp'] - fvg['timestamp']) < 3600000):  # Within 1 hour
                        confluence_count += 1
                        supporting_patterns.append('fvg')
                
                # Generate signal if confluence is strong
                if confluence_count >= 1:
                    trading_signals.append({
                        'timestamp': signal['timestamp'],
                        'action': 'BUY' if signal['direction'] == 'bullish' else 'SELL',
                        'pattern_type': 'CHoCH_CONFLUENCE',
                        'entry_price': signal['price'],
                        'confidence': min(signal['strength'] + confluence_count * 10, 100),
                        'supporting_patterns': supporting_patterns,
                        'timeframe_strength': market_structure.get('strength', 0)
                    })
        
        return trading_signals
    
    # Helper methods
    def _convert_df_to_data(self, df: pd.DataFrame) -> List[Dict]:
        """Convert DataFrame to list of dictionaries"""
        data = []
        for _, row in df.iterrows():
            # Handle timestamp conversion properly
            if 'timestamp' in row:
                timestamp = row['timestamp']
                try:
                    if hasattr(timestamp, 'timestamp'):  # pandas Timestamp
                        timestamp = int(timestamp.timestamp() * 1000)
                    elif isinstance(timestamp, str):
                        # Handle string timestamps
                        timestamp = int(float(timestamp))
                    elif isinstance(timestamp, (int, float)):
                        timestamp = int(timestamp)
                    else:
                        timestamp = int(datetime.now().timestamp() * 1000)
                except (ValueError, TypeError):
                    timestamp = int(datetime.now().timestamp() * 1000)
            else:
                timestamp = int(datetime.now().timestamp() * 1000)
            
            data.append({
                'timestamp': timestamp,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume']) if 'volume' in row else 0.0
            })
        return data
    
    def _get_previous_swing_low(self, all_swings: List[Dict], current_index: int) -> Dict:
        """Get previous swing low before current index"""
        for i in range(current_index - 1, -1, -1):
            if all_swings[i]['type'] == 'swing_low':
                return all_swings[i]
        return {'price': 0}
    
    def _get_previous_swing_high(self, all_swings: List[Dict], current_index: int) -> Dict:
        """Get previous swing high before current index"""
        for i in range(current_index - 1, -1, -1):
            if all_swings[i]['type'] == 'swing_high':
                return all_swings[i]
        return {'price': float('inf')}
    
    def _calculate_signal_strength(self, data: List[Dict], signal_point: Dict, reference_point: Dict) -> float:
        """Calculate signal strength based on various factors"""
        try:
            # Volume factor
            idx = signal_point.get('index', 0)
            if idx < len(data):
                volume_factor = data[idx]['volume'] / self._get_average_volume(data)
            else:
                volume_factor = 1.0
            
            # Price movement factor
            price_diff = abs(signal_point['price'] - reference_point['price'])
            price_factor = price_diff / reference_point['price'] * 100
            
            # Time factor (more recent = stronger)
            time_diff = abs(signal_point['timestamp'] - reference_point['timestamp']) / 3600000  # hours
            time_factor = max(1, 24 / (time_diff + 1))  # Decay over 24 hours
            
            strength = min(volume_factor * price_factor * time_factor * 20, 100)
            return max(strength, 30)  # Minimum strength
        except:
            return 50.0
    
    def _calculate_order_block_strength(self, data: List[Dict], start_idx: int, end_idx: int) -> float:
        """Calculate order block strength"""
        try:
            avg_volume = sum(data[i]['volume'] for i in range(start_idx, end_idx)) / (end_idx - start_idx)
            total_avg_volume = self._get_average_volume(data)
            volume_strength = min(avg_volume / total_avg_volume * 50, 100)
            return max(volume_strength, 40)
        except:
            return 50.0
    
    def _calculate_fvg_strength(self, gap_size: float, current_candle: Dict) -> float:
        """Calculate FVG strength"""
        try:
            gap_percentage = gap_size / current_candle['close'] * 100
            return min(gap_percentage * 10, 100)
        except:
            return 50.0
    
    def _calculate_liquidity_strength(self, data: List[Dict], sweep_idx: int, original_level: Dict) -> float:
        """Calculate liquidity sweep strength"""
        try:
            volume_factor = data[sweep_idx]['volume'] / self._get_average_volume(data)
            price_factor = abs(data[sweep_idx]['high'] - original_level['price']) / original_level['price'] * 100
            return min(volume_factor * price_factor * 20, 100)
        except:
            return 50.0
    
    def _calculate_eqh_eql_strength(self, point1: Dict, point2: Dict) -> float:
        """Calculate EQH/EQL strength"""
        try:
            time_diff = abs(point1['timestamp'] - point2['timestamp']) / 3600000
            time_strength = min(time_diff / 20, 2.0)
            price_diff = abs(point1['price'] - point2['price'])
            precision_strength = 1.0 / (1.0 + price_diff / point1['price'] * 100)
            return min(time_strength * precision_strength * 50, 100)
        except:
            return 50.0
    
    def _get_average_volume(self, data: List[Dict]) -> float:
        """Calculate average volume"""
        if not data:
            return 1.0
        return sum(d['volume'] for d in data) / len(data)
    
    def _determine_market_structure(self, choch_bos_signals: List[Dict], order_blocks: List[Dict]) -> Dict[str, Any]:
        """Determine overall market structure"""
        if not choch_bos_signals:
            return {'trend': 'neutral', 'strength': 0}
        
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
                             fvg_signals: List[Dict], liquidity_sweeps: List[Dict], 
                             eqh_eql_signals: List[Dict]) -> Dict[str, Any]:
        """Generate SMC analysis summary"""
        return {
            'total_choch_bos': len(choch_bos_signals),
            'total_order_blocks': len(order_blocks),
            'total_fvg': len(fvg_signals),
            'total_liquidity_sweeps': len(liquidity_sweeps),
            'total_eqh_eql': len(eqh_eql_signals),
            'bullish_signals': len([s for s in choch_bos_signals if s['direction'] == 'bullish']),
            'bearish_signals': len([s for s in choch_bos_signals if s['direction'] == 'bearish']),
            'recent_activity': len([s for s in choch_bos_signals[-10:] if s]) if choch_bos_signals else 0,
            'pattern_diversity': len([t for t in ['CHoCH', 'BOS', 'FVG', 'liquidity_sweep', 'EQH', 'EQL'] 
                                    if any(s.get('type') == t for s in (choch_bos_signals + fvg_signals + liquidity_sweeps + eqh_eql_signals))])
        }
    
    def _calculate_confidence_score(self, choch_bos_signals: List[Dict], order_blocks: List[Dict], 
                                   fvg_signals: List[Dict], liquidity_sweeps: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not any([choch_bos_signals, order_blocks, fvg_signals, liquidity_sweeps]):
            return 0.0
        
        # Base score from signal count
        signal_count = len(choch_bos_signals) + len(order_blocks) + len(fvg_signals) + len(liquidity_sweeps)
        base_score = min(signal_count * 10, 60)
        
        # Confluence bonus
        confluence_bonus = 0
        if len(choch_bos_signals) > 0 and len(order_blocks) > 0:
            confluence_bonus += 15
        if len(fvg_signals) > 0 and len(liquidity_sweeps) > 0:
            confluence_bonus += 10
        
        # Recent activity bonus
        recent_signals = [s for s in choch_bos_signals if s['timestamp'] > (datetime.now().timestamp() - 3600) * 1000]
        recent_bonus = len(recent_signals) * 5
        
        total_score = base_score + confluence_bonus + recent_bonus
        return min(total_score, 100)
    
    def _empty_smc_analysis(self) -> Dict[str, Any]:
        """Return empty SMC analysis structure"""
        return {
            'symbol': '',
            'timeframe': '',
            'timestamp': int(datetime.now().timestamp() * 1000),
            'current_price': 0.0,
            'swing_points': {'swing_highs': [], 'swing_lows': []},
            'choch_bos_signals': [],
            'order_blocks': [],
            'fvg_signals': [],
            'liquidity_sweeps': [],
            'eqh_eql_signals': [],
            'market_structure': {'trend': 'neutral', 'strength': 0},
            'smc_summary': {
                'total_choch_bos': 0,
                'total_order_blocks': 0,
                'total_fvg': 0,
                'total_liquidity_sweeps': 0,
                'total_eqh_eql': 0,
                'bullish_signals': 0,
                'bearish_signals': 0,
                'recent_activity': 0,
                'pattern_diversity': 0
            },
            'trading_signals': [],
            'confidence_score': 0.0
        }