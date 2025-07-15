"""
Advanced Technical Indicator Calculator
Calculates RSI, MACD, EMA/SMA, Bollinger Bands, Stochastic, OBV, VWAP, ATR
"""

import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

class IndicatorCalculator:
    def __init__(self):
        pass
    
    def calculate_sma(self, data: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        if len(data) < period:
            return []
        
        sma = []
        for i in range(period - 1, len(data)):
            sma.append(np.mean(data[i - period + 1:i + 1]))
        
        return sma
    
    def calculate_ema(self, data: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(data) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = [np.mean(data[:period])]  # Start with SMA
        
        for i in range(period, len(data)):
            ema.append((data[i] * multiplier) + (ema[-1] * (1 - multiplier)))
        
        return ema
    
    def calculate_rsi(self, data: List[Dict], period: int = 14) -> List[Dict]:
        """Calculate Relative Strength Index"""
        if len(data) < period + 1:
            return []
        
        closes = [candle['close'] for candle in data]
        changes = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        
        gains = [change if change > 0 else 0 for change in changes]
        losses = [-change if change < 0 else 0 for change in changes]
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        rsi_values = []
        
        for i in range(period, len(changes)):
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append({
                'timestamp': data[i + 1]['timestamp'],
                'rsi': rsi,
                'overbought': rsi > 70,
                'oversold': rsi < 30
            })
            
            # Update averages
            gain = gains[i] if i < len(gains) else 0
            loss = losses[i] if i < len(losses) else 0
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period
        
        return rsi_values
    
    def calculate_macd(self, data: List[Dict], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> List[Dict]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(data) < slow_period + signal_period:
            return []
        
        closes = [candle['close'] for candle in data]
        
        # Calculate EMAs
        fast_ema = self.calculate_ema(closes, fast_period)
        slow_ema = self.calculate_ema(closes, slow_period)
        
        # Align EMAs (slow EMA starts later)
        ema_start_idx = slow_period - fast_period
        fast_ema_aligned = fast_ema[ema_start_idx:]
        
        # Calculate MACD line
        macd_line = [fast_ema_aligned[i] - slow_ema[i] for i in range(len(slow_ema))]
        
        # Calculate Signal line (EMA of MACD)
        signal_line = self.calculate_ema(macd_line, signal_period)
        
        # Calculate Histogram
        histogram = [macd_line[i + len(macd_line) - len(signal_line)] - signal_line[i] for i in range(len(signal_line))]
        
        # Format results
        macd_results = []
        start_idx = slow_period + signal_period - 1
        
        for i in range(len(histogram)):
            data_idx = start_idx + i
            if data_idx < len(data):
                macd_results.append({
                    'timestamp': data[data_idx]['timestamp'],
                    'macd': macd_line[i + len(macd_line) - len(signal_line)],
                    'signal': signal_line[i],
                    'histogram': histogram[i],
                    'bullish_crossover': i > 0 and histogram[i] > 0 and histogram[i-1] <= 0,
                    'bearish_crossover': i > 0 and histogram[i] < 0 and histogram[i-1] >= 0
                })
        
        return macd_results
    
    def calculate_bollinger_bands(self, data: List[Dict], period: int = 20, std_multiplier: float = 2.0) -> List[Dict]:
        """Calculate Bollinger Bands"""
        if len(data) < period:
            return []
        
        closes = [candle['close'] for candle in data]
        sma = self.calculate_sma(closes, period)
        
        bb_results = []
        
        for i in range(len(sma)):
            data_idx = i + period - 1
            window_data = closes[i:i + period]
            std_dev = np.std(window_data)
            
            middle = sma[i]
            upper = middle + (std_dev * std_multiplier)
            lower = middle - (std_dev * std_multiplier)
            
            current_price = data[data_idx]['close']
            
            bb_results.append({
                'timestamp': data[data_idx]['timestamp'],
                'upper': upper,
                'middle': middle,
                'lower': lower,
                'price': current_price,
                'squeeze': (upper - lower) / middle < 0.1,  # Bollinger squeeze
                'breakout_up': current_price > upper,
                'breakout_down': current_price < lower
            })
        
        return bb_results
    
    def calculate_stochastic(self, data: List[Dict], k_period: int = 14, d_period: int = 3) -> List[Dict]:
        """Calculate Stochastic Oscillator"""
        if len(data) < k_period + d_period:
            return []
        
        stoch_results = []
        
        for i in range(k_period - 1, len(data)):
            window_data = data[i - k_period + 1:i + 1]
            
            highest_high = max(candle['high'] for candle in window_data)
            lowest_low = min(candle['low'] for candle in window_data)
            current_close = data[i]['close']
            
            if highest_high == lowest_low:
                k_percent = 50
            else:
                k_percent = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
            
            stoch_results.append({
                'timestamp': data[i]['timestamp'],
                'k_percent': k_percent
            })
        
        # Calculate %D (SMA of %K)
        k_values = [result['k_percent'] for result in stoch_results]
        d_values = self.calculate_sma(k_values, d_period)
        
        # Combine results
        final_results = []
        for i in range(len(d_values)):
            result_idx = i + d_period - 1
            if result_idx < len(stoch_results):
                k_val = stoch_results[result_idx]['k_percent']
                d_val = d_values[i]
                
                final_results.append({
                    'timestamp': stoch_results[result_idx]['timestamp'],
                    'k_percent': k_val,
                    'd_percent': d_val,
                    'overbought': k_val > 80 and d_val > 80,
                    'oversold': k_val < 20 and d_val < 20,
                    'bullish_crossover': i > 0 and k_val > d_val and stoch_results[result_idx-1]['k_percent'] <= d_values[i-1],
                    'bearish_crossover': i > 0 and k_val < d_val and stoch_results[result_idx-1]['k_percent'] >= d_values[i-1]
                })
        
        return final_results
    
    def calculate_atr(self, data: List[Dict], period: int = 14) -> List[Dict]:
        """Calculate Average True Range"""
        if len(data) < period + 1:
            return []
        
        true_ranges = []
        
        for i in range(1, len(data)):
            high_low = data[i]['high'] - data[i]['low']
            high_close_prev = abs(data[i]['high'] - data[i-1]['close'])
            low_close_prev = abs(data[i]['low'] - data[i-1]['close'])
            
            tr = max(high_low, high_close_prev, low_close_prev)
            true_ranges.append(tr)
        
        # Calculate ATR using EMA
        atr_values = self.calculate_ema(true_ranges, period)
        
        atr_results = []
        for i in range(len(atr_values)):
            data_idx = i + period
            if data_idx < len(data):
                atr_results.append({
                    'timestamp': data[data_idx]['timestamp'],
                    'atr': atr_values[i],
                    'volatility': 'high' if atr_values[i] > np.mean(atr_values[-20:]) * 1.5 else 'normal'
                })
        
        return atr_results
    
    def calculate_vwap(self, data: List[Dict]) -> List[Dict]:
        """Calculate Volume Weighted Average Price"""
        if len(data) < 1:
            return []
        
        vwap_results = []
        cumulative_volume = 0
        cumulative_pv = 0
        
        for i, candle in enumerate(data):
            typical_price = (candle['high'] + candle['low'] + candle['close']) / 3
            volume = candle['volume']
            
            cumulative_volume += volume
            cumulative_pv += typical_price * volume
            
            vwap = cumulative_pv / cumulative_volume if cumulative_volume > 0 else typical_price
            
            vwap_results.append({
                'timestamp': candle['timestamp'],
                'vwap': vwap,
                'price': candle['close'],
                'above_vwap': candle['close'] > vwap,
                'volume': volume
            })
        
        return vwap_results
    
    def calculate_volume_spike(self, data: List[Dict], period: int = 20, multiplier: float = 2.0) -> List[Dict]:
        """Detect volume spikes"""
        if len(data) < period:
            return []
        
        volumes = [candle['volume'] for candle in data]
        volume_sma = self.calculate_sma(volumes, period)
        
        spike_results = []
        
        for i in range(len(volume_sma)):
            data_idx = i + period - 1
            current_volume = data[data_idx]['volume']
            avg_volume = volume_sma[i]
            
            spike_results.append({
                'timestamp': data[data_idx]['timestamp'],
                'volume': current_volume,
                'avg_volume': avg_volume,
                'volume_spike': current_volume > avg_volume * multiplier,
                'spike_ratio': current_volume / avg_volume if avg_volume > 0 else 1
            })
        
        return spike_results
    
    def calculate_all_indicators(self, data: List[Dict]) -> Dict[str, Any]:
        """Calculate all technical indicators"""
        if not data or len(data) < 50:
            return {}
        
        try:
            # Ensure all timestamps are integers to avoid comparison issues
            normalized_data = []
            for item in data:
                normalized_item = item.copy()
                if isinstance(normalized_item.get('timestamp'), str):
                    normalized_item['timestamp'] = int(normalized_item['timestamp'])
                normalized_data.append(normalized_item)
            
            indicators = {
                'rsi': self.calculate_rsi(normalized_data),
                'macd': self.calculate_macd(normalized_data),
                'bollinger_bands': self.calculate_bollinger_bands(normalized_data),
                'stochastic': self.calculate_stochastic(normalized_data),
                'atr': self.calculate_atr(normalized_data),
                'vwap': self.calculate_vwap(normalized_data),
                'volume_spike': self.calculate_volume_spike(normalized_data),
                'ema_21': self.calculate_ema([d['close'] for d in normalized_data], 21),
                'ema_50': self.calculate_ema([d['close'] for d in normalized_data], 50),
                'sma_200': self.calculate_sma([d['close'] for d in normalized_data], 200)
            }
            
            # Add trend analysis
            indicators['trend_analysis'] = self.analyze_trend(normalized_data, indicators)
            
            return indicators
            
        except Exception as e:
            logging.error(f"Error calculating indicators: {str(e)}")
            return {}
    
    def analyze_trend(self, data: List[Dict], indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall trend based on multiple indicators"""
        if not data or len(data) < 20:
            return {}
        
        try:
            current_price = data[-1]['close']
            trend_signals = []
            
            # EMA trend
            if 'ema_21' in indicators and 'ema_50' in indicators:
                if len(indicators['ema_21']) > 0 and len(indicators['ema_50']) > 0:
                    if indicators['ema_21'][-1] > indicators['ema_50'][-1]:
                        trend_signals.append('bullish')
                    else:
                        trend_signals.append('bearish')
            
            # RSI trend
            if 'rsi' in indicators and len(indicators['rsi']) > 0:
                rsi_current = indicators['rsi'][-1]['rsi']
                if rsi_current > 50:
                    trend_signals.append('bullish')
                else:
                    trend_signals.append('bearish')
            
            # MACD trend
            if 'macd' in indicators and len(indicators['macd']) > 0:
                macd_current = indicators['macd'][-1]
                if macd_current['histogram'] > 0:
                    trend_signals.append('bullish')
                else:
                    trend_signals.append('bearish')
            
            # Calculate overall trend
            bullish_count = trend_signals.count('bullish')
            bearish_count = trend_signals.count('bearish')
            
            if bullish_count > bearish_count:
                overall_trend = 'bullish'
            elif bearish_count > bullish_count:
                overall_trend = 'bearish'
            else:
                overall_trend = 'neutral'
            
            return {
                'overall_trend': overall_trend,
                'trend_strength': abs(bullish_count - bearish_count) / len(trend_signals) if trend_signals else 0,
                'signals': trend_signals,
                'confidence': (max(bullish_count, bearish_count) / len(trend_signals)) * 100 if trend_signals else 0
            }
            
        except Exception as e:
            logging.error(f"Error analyzing trend: {str(e)}")
            return {}