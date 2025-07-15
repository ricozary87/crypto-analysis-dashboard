import numpy as np
import pandas as pd
from typing import Dict, List, Any
import logging

class TechnicalIndicators:
    def __init__(self):
        pass
    
    def calculate_obv(self, data: List[Dict]) -> List[Dict]:
        """Calculate On-Balance Volume (OBV)"""
        if len(data) < 2:
            return []
        
        obv_values = []
        obv = 0
        
        for i, candle in enumerate(data):
            if i == 0:
                obv = candle['volume']
            else:
                prev_close = data[i-1]['close']
                current_close = candle['close']
                
                if current_close > prev_close:
                    obv += candle['volume']
                elif current_close < prev_close:
                    obv -= candle['volume']
                # If close == prev_close, OBV stays the same
            
            obv_values.append({
                'timestamp': int(candle['timestamp']) if isinstance(candle['timestamp'], str) else candle['timestamp'],
                'datetime': candle['datetime'],
                'obv': obv
            })
        
        return obv_values
    
    def calculate_ema(self, values: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(values) < period:
            return [None] * len(values)
        
        ema_values = [None] * (period - 1)
        
        # First EMA value is SMA
        sma = sum(values[:period]) / period
        ema_values.append(sma)
        
        # Calculate multiplier
        multiplier = 2 / (period + 1)
        
        # Calculate remaining EMA values
        for i in range(period, len(values)):
            ema = (values[i] * multiplier) + (ema_values[i-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    def calculate_macd(self, data: List[Dict], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> List[Dict]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(data) < slow_period:
            return []
        
        closes = [candle['close'] for candle in data]
        
        # Calculate EMAs
        ema_fast = self.calculate_ema(closes, fast_period)
        ema_slow = self.calculate_ema(closes, slow_period)
        
        # Calculate MACD line
        macd_line = []
        for i in range(len(closes)):
            if ema_fast[i] is not None and ema_slow[i] is not None:
                macd_line.append(ema_fast[i] - ema_slow[i])
            else:
                macd_line.append(None)
        
        # Calculate signal line (EMA of MACD)
        valid_macd = [x for x in macd_line if x is not None]
        if len(valid_macd) < signal_period:
            signal_line = [None] * len(macd_line)
        else:
            signal_ema = self.calculate_ema(valid_macd, signal_period)
            signal_line = [None] * (len(macd_line) - len(signal_ema)) + signal_ema
        
        # Calculate histogram
        histogram = []
        for i in range(len(macd_line)):
            if macd_line[i] is not None and signal_line[i] is not None:
                histogram.append(macd_line[i] - signal_line[i])
            else:
                histogram.append(None)
        
        # Format results
        macd_results = []
        for i, candle in enumerate(data):
            macd_results.append({
                'timestamp': int(candle['timestamp']) if isinstance(candle['timestamp'], str) else candle['timestamp'],
                'datetime': candle['datetime'],
                'macd': macd_line[i],
                'signal': signal_line[i],
                'histogram': histogram[i]
            })
        
        return macd_results
    
    def calculate_volume_analysis(self, data: List[Dict]) -> Dict[str, Any]:
        """Calculate volume analysis metrics"""
        if not data:
            return {}
        
        volumes = [candle['volume'] for candle in data]
        
        # Calculate volume statistics
        total_volume = sum(volumes)
        avg_volume = total_volume / len(volumes)
        max_volume = max(volumes)
        min_volume = min(volumes)
        
        # Calculate volume trend (last 20 periods vs previous 20)
        volume_trend = 0
        if len(volumes) >= 40:
            recent_avg = sum(volumes[-20:]) / 20
            previous_avg = sum(volumes[-40:-20]) / 20
            volume_trend = ((recent_avg - previous_avg) / previous_avg) * 100
        
        # Calculate volume price relationship
        volume_price_correlation = 0
        if len(data) >= 2:
            price_changes = []
            volume_changes = []
            
            for i in range(1, len(data)):
                price_change = (data[i]['close'] - data[i-1]['close']) / data[i-1]['close']
                volume_change = (data[i]['volume'] - data[i-1]['volume']) / data[i-1]['volume'] if data[i-1]['volume'] > 0 else 0
                
                price_changes.append(price_change)
                volume_changes.append(volume_change)
            
            # Simple correlation calculation
            if len(price_changes) > 1:
                try:
                    price_df = pd.Series(price_changes)
                    volume_df = pd.Series(volume_changes)
                    volume_price_correlation = price_df.corr(volume_df)
                    if pd.isna(volume_price_correlation):
                        volume_price_correlation = 0
                except:
                    volume_price_correlation = 0
        
        return {
            'total_volume': total_volume,
            'average_volume': avg_volume,
            'max_volume': max_volume,
            'min_volume': min_volume,
            'volume_trend_percent': volume_trend,
            'volume_price_correlation': volume_price_correlation,
            'periods_analyzed': len(data)
        }
    
    def calculate_all_indicators(self, data: List[Dict]) -> Dict[str, Any]:
        """Calculate all technical indicators"""
        try:
            # Ensure all timestamps are integers to avoid comparison issues
            normalized_data = []
            for item in data:
                normalized_item = item.copy()
                if isinstance(normalized_item.get('timestamp'), str):
                    normalized_item['timestamp'] = int(normalized_item['timestamp'])
                normalized_data.append(normalized_item)
            
            indicators = {}
            
            # Calculate OBV
            indicators['obv'] = self.calculate_obv(normalized_data)
            
            # Calculate MACD
            indicators['macd'] = self.calculate_macd(normalized_data)
            
            # Calculate volume analysis
            indicators['volume_analysis'] = self.calculate_volume_analysis(normalized_data)
            
            # Calculate simple moving averages
            closes = [candle['close'] for candle in normalized_data]
            
            # SMA 20
            sma_20 = []
            for i in range(len(closes)):
                if i < 19:
                    sma_20.append(None)
                else:
                    sma_20.append(sum(closes[i-19:i+1]) / 20)
            
            # SMA 50
            sma_50 = []
            for i in range(len(closes)):
                if i < 49:
                    sma_50.append(None)
                else:
                    sma_50.append(sum(closes[i-49:i+1]) / 50)
            
            # Format SMAs
            sma_data = []
            for i, candle in enumerate(normalized_data):
                sma_data.append({
                    'timestamp': candle['timestamp'],
                    'datetime': candle['datetime'],
                    'sma_20': sma_20[i],
                    'sma_50': sma_50[i]
                })
            
            indicators['sma'] = sma_data
            
            # Calculate RSI
            indicators['rsi'] = self.calculate_rsi(normalized_data)
            
            return indicators
            
        except Exception as e:
            logging.error(f"Error calculating technical indicators: {str(e)}")
            return {}
    
    def calculate_rsi(self, data: List[Dict], period: int = 14) -> List[Dict]:
        """Calculate Relative Strength Index (RSI)"""
        if len(data) < period + 1:
            return []
        
        closes = [candle['close'] for candle in data]
        
        # Calculate price changes
        price_changes = []
        for i in range(1, len(closes)):
            price_changes.append(closes[i] - closes[i-1])
        
        # Calculate gains and losses
        gains = [max(change, 0) for change in price_changes]
        losses = [abs(min(change, 0)) for change in price_changes]
        
        # Calculate RSI
        rsi_values = [None] * (period)  # First 'period' values will be None
        
        # Calculate first RS and RSI
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        if avg_loss == 0:
            rsi_values.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsi_values.append(rsi)
        
        # Calculate subsequent RSI values
        for i in range(period + 1, len(price_changes)):
            avg_gain = (avg_gain * (period - 1) + gains[i-1]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i-1]) / period
            
            if avg_loss == 0:
                rsi_values.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                rsi_values.append(rsi)
        
        # Format results
        rsi_results = []
        for i, candle in enumerate(data):
            if i < len(rsi_values):
                rsi_results.append({
                    'timestamp': int(candle['timestamp']) if isinstance(candle['timestamp'], str) else candle['timestamp'],
                    'datetime': candle['datetime'],
                    'rsi': rsi_values[i]
                })
        
        return rsi_results
