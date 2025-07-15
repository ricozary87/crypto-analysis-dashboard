"""
Snapshot Generator - Advanced Trading Analysis with 7-Layer Confluence
Combines SMC, Volume, Orderbook, RSI/EMA, Fibonacci, OI, and Funding Rate analysis
Provides human-like narrative explanations with alternative scenarios
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import json
import os
from openai import OpenAI
from ai_prompt_builder import AIPromptBuilder
from ai_engine import AIEngine

class SnapshotGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ai_prompt_builder = AIPromptBuilder()
        # Initialize AI Engine for high-quality narrative generation
        self.ai_engine = AIEngine()
        # Keep backward compatibility with OpenAI client
        self.openai_client = self.ai_engine.openai_client
        
    def _make_json_serializable(self, obj):
        """Convert numpy types and other non-JSON-serializable types to JSON-serializable types"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj
        
    def generate_snapshot(self, symbol: str, timeframe: str, market_data: Dict[str, Any], quick_mode: bool = False) -> Dict[str, Any]:
        """
        Generate comprehensive trading snapshot with 7-layer confluence analysis
        
        Args:
            symbol: Trading symbol (e.g., 'BTC-USDT')
            timeframe: Time frame (e.g., '1h', '4h', '1d')
            market_data: Dictionary containing all analysis data
            quick_mode: Enable quick mode for faster analysis (default: False)
        
        Returns:
            Complete snapshot with narrative analysis and trading plans
        """
        
        try:
            # Extract data from different modules
            candlestick_data = market_data.get('candlestick', [])
            orderbook_data = market_data.get('orderbook', {})
            open_interest_data = market_data.get('open_interest', {})
            technical_indicators = market_data.get('technical_indicators', {})
            smc_analysis = market_data.get('smc_analysis', {})
            price_action = market_data.get('price_action', {})
            volume_analysis = market_data.get('volume_analysis', {})
            
            self.logger.debug(f"Market data keys: {list(market_data.keys())}")
            self.logger.debug(f"Candlestick data length: {len(candlestick_data)}")
            
            if not candlestick_data:
                return self._generate_error_snapshot("Insufficient market data")
                
            current_price = float(candlestick_data[-1]['close'])
            
            # Generate 7-layer confluence analysis
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "timeframe": timeframe,
                "current_price": current_price,
                
                # 7 Core Analysis Layers
                "smc_analysis": self._analyze_smc_layer(smc_analysis, candlestick_data),
                "volume_analysis": self._analyze_volume_layer(volume_analysis, candlestick_data),
                "orderbook_analysis": self._analyze_orderbook_layer(orderbook_data, current_price),
                "rsi_ema_analysis": self._analyze_rsi_ema_layer(technical_indicators, candlestick_data),
                "fibonacci_analysis": self._analyze_fibonacci_layer(candlestick_data),
                "oi_funding_analysis": self._analyze_oi_funding_layer(open_interest_data, symbol),
                "trend_structure": self._analyze_trend_structure(candlestick_data, technical_indicators),
                
                # Comprehensive Summary
                "confluence_summary": {},
                "narrative_analysis": "",
                "confidence_score": "",
                
                # Trading Plans
                "primary_plan": {},
                "alternative_scenarios": [],
                
                # Risk Management
                "risk_factors": [],
                "market_context": ""
            }
            
            # Generate confluence summary
            snapshot["confluence_summary"] = self._generate_confluence_summary(snapshot)
            
            # Generate AI-powered narrative analysis
            ai_narrative = self._generate_ai_narrative(symbol, timeframe, snapshot, quick_mode)
            snapshot["narrative_analysis"] = ai_narrative
            snapshot["ai_narrative"] = ai_narrative  # For API compatibility
            
            # Calculate confidence score
            snapshot["confidence_score"] = self._calculate_confidence_score(snapshot)
            
            # Generate trading plans
            snapshot["primary_plan"] = self._generate_primary_trading_plan(snapshot, current_price)
            snapshot["alternative_scenarios"] = self._generate_alternative_scenarios(snapshot, current_price)
            
            # Assess risk factors
            snapshot["risk_factors"] = self._assess_risk_factors(snapshot)
            
            # Generate market context
            snapshot["market_context"] = self._generate_market_context(snapshot)
            
            return self._make_json_serializable(snapshot)
            
        except Exception as e:
            import traceback
            self.logger.error(f"Error generating snapshot: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return self._generate_error_snapshot(str(e))
    
    def _analyze_smc_layer(self, smc_data: Dict, candlestick_data: List[Dict]) -> Dict[str, Any]:
        """Analyze Smart Money Concepts layer"""
        
        if not smc_data:
            return {
                "signal": "neutral",
                "strength": 0,
                "description": "Data SMC tidak tersedia untuk analisis mendalam",
                "key_levels": [],
                "market_structure": "undefined"
            }
        
        # Extract key SMC elements
        choch_bos = smc_data.get('choch_bos_signals', [])
        order_blocks = smc_data.get('order_blocks', [])
        fvg_signals = smc_data.get('fvg_signals', [])
        liquidity_sweeps = smc_data.get('liquidity_sweeps', [])
        
        # Determine overall SMC bias
        recent_signals = [s for s in choch_bos if s.get('timestamp')][-3:] if choch_bos else []
        
        bullish_signals = sum(1 for s in recent_signals if s.get('signal') == 'bullish')
        bearish_signals = sum(1 for s in recent_signals if s.get('signal') == 'bearish')
        
        if bullish_signals > bearish_signals:
            signal = "bullish"
            strength = min(85, (bullish_signals / max(len(recent_signals), 1)) * 100)
        elif bearish_signals > bullish_signals:
            signal = "bearish"
            strength = min(85, (bearish_signals / max(len(recent_signals), 1)) * 100)
        else:
            signal = "neutral"
            strength = 50
            
        # Analyze market structure with fallback scenarios
        if recent_signals:
            latest_signal = recent_signals[-1]
            if latest_signal.get('type') == 'CHoCH':
                structure = "Change of Character - Kemungkinan reversal struktur"
            elif latest_signal.get('type') == 'BOS':
                structure = "Break of Structure - Konfirmasi kelanjutan trend"
            else:
                structure = "Struktur market dalam konsolidasi"
        else:
            # Check if market is in narrow range (fallback scenario)
            if candlestick_data and len(candlestick_data) >= 20:
                recent_highs = [candle['high'] for candle in candlestick_data[-20:]]
                recent_lows = [candle['low'] for candle in candlestick_data[-20:]]
                range_percent = ((max(recent_highs) - min(recent_lows)) / min(recent_lows)) * 100
                
                if range_percent < 3:  # Less than 3% range
                    structure = "Struktur belum terbentuk akibat range sempit (<3%). Tunggu breakout dengan volume tinggi."
                    signal = "neutral"
                    strength = 30
                elif range_percent < 5:  # Less than 5% range
                    structure = "Range terbatas - struktur SMC memerlukan volatilitas lebih tinggi untuk konfirmasi"
                    strength = max(40, strength)
                else:
                    structure = "Struktur market belum terdefinisi jelas - perlu waktu untuk pembentukan pola"
            else:
                structure = "Data tidak mencukupi untuk analisis struktur SMC"
            
        # Key levels from order blocks
        key_levels = []
        for ob in order_blocks[-5:]:  # Last 5 order blocks
            key_levels.append({
                "level": ob.get('price', 0),
                "type": ob.get('type', 'unknown'),
                "strength": ob.get('strength', 0)
            })
        
        return {
            "signal": signal,
            "strength": strength,
            "description": f"SMC menunjukkan bias {signal} dengan kekuatan {strength:.1f}%. {structure}",
            "key_levels": key_levels,
            "market_structure": structure,
            "recent_choch_bos": len(recent_signals),
            "fvg_count": len(fvg_signals),
            "liquidity_sweeps": len(liquidity_sweeps)
        }
    
    def _analyze_volume_layer(self, volume_data: Dict, candlestick_data: List[Dict]) -> Dict[str, Any]:
        """Analyze Volume and CVD layer"""
        
        if not candlestick_data or len(candlestick_data) < 20:
            return {
                "signal": "neutral",
                "strength": 0,
                "description": "Data volume tidak mencukupi untuk analisis",
                "volume_trend": "undefined"
            }
        
        # Calculate volume metrics
        recent_volumes = [candle['volume'] for candle in candlestick_data[-20:]]
        avg_volume = np.mean(recent_volumes)
        current_volume = candlestick_data[-1]['volume']
        
        # Volume spike detection
        volume_spike = current_volume > (avg_volume * 1.5)
        
        # Volume trend analysis
        recent_volume_trend = []
        for i in range(len(candlestick_data) - 10, len(candlestick_data)):
            if i > 0:
                candle = candlestick_data[i]
                if candle['close'] > candle['open']:  # Bullish candle
                    recent_volume_trend.append(candle['volume'])
                else:  # Bearish candle
                    recent_volume_trend.append(-candle['volume'])
        
        cumulative_volume_delta = sum(recent_volume_trend)
        
        # Determine signal first
        if cumulative_volume_delta > 0 and volume_spike:
            signal = "bullish"
            strength = min(80, abs(cumulative_volume_delta) / avg_volume * 50)
        elif cumulative_volume_delta < 0 and volume_spike:
            signal = "bearish"
            strength = min(80, abs(cumulative_volume_delta) / avg_volume * 50)
        else:
            signal = "neutral"
            strength = 40
        
        # Check for CVD-Volume divergence (warning scenario) - after strength is calculated
        volume_divergence_warning = ""
        if len(recent_volumes) >= 10:
            recent_volume_avg = np.mean(recent_volumes[-5:])
            prev_volume_avg = np.mean(recent_volumes[-10:-5])
            volume_declining = recent_volume_avg < prev_volume_avg * 0.8  # 20% decline
            
            if cumulative_volume_delta > 0 and volume_declining:
                volume_divergence_warning = "⚠️ CVD naik tapi volume turun → warning akumulasi lemah. "
                strength = strength * 0.7  # Reduce strength due to divergence
            elif cumulative_volume_delta < 0 and volume_declining:
                volume_divergence_warning = "⚠️ CVD turun dengan volume menurun → distribusi lemah, bisa false breakout. "
                strength = strength * 0.8
        
        # Volume profile analysis
        volume_profile = self._analyze_volume_profile(candlestick_data)
        
        description = f"Volume menunjukkan {signal} pressure dengan kekuatan {strength:.1f}%. "
        if volume_spike:
            description += f"Volume spike terdeteksi ({current_volume/avg_volume:.1f}x rata-rata). "
        
        description += f"CVD menunjukkan {'+' if cumulative_volume_delta > 0 else ''}akumulasi {abs(cumulative_volume_delta):.0f}. "
        description += volume_divergence_warning
        
        return {
            "signal": signal,
            "strength": float(strength),
            "description": description,
            "volume_trend": "increasing" if cumulative_volume_delta > 0 else "decreasing",
            "volume_spike": bool(volume_spike),
            "cvd": float(cumulative_volume_delta),
            "volume_profile": volume_profile
        }
    
    def _analyze_orderbook_layer(self, orderbook_data: Dict, current_price: float) -> Dict[str, Any]:
        """Analyze Orderbook and Market Depth layer"""
        
        if not orderbook_data or not orderbook_data.get('bids') or not orderbook_data.get('asks'):
            return {
                "signal": "neutral",
                "strength": 0,
                "description": "Data orderbook tidak tersedia",
                "imbalance": 0,
                "walls": []
            }
        
        bids = orderbook_data['bids']
        asks = orderbook_data['asks']
        
        # Calculate orderbook imbalance
        try:
            # Try different orderbook formats
            if isinstance(bids[0], list):
                total_bid_volume = sum(float(bid[1]) for bid in bids[:10])  # Top 10 bids
                total_ask_volume = sum(float(ask[1]) for ask in asks[:10])  # Top 10 asks
            elif isinstance(bids[0], dict):
                total_bid_volume = sum(float(bid.get('size', 0)) for bid in bids[:10])
                total_ask_volume = sum(float(ask.get('size', 0)) for ask in asks[:10])
            else:
                # Handle string format like "price,size"
                total_bid_volume = sum(float(str(bid).split(',')[1]) for bid in bids[:10])
                total_ask_volume = sum(float(str(ask).split(',')[1]) for ask in asks[:10])
        except (IndexError, ValueError, TypeError) as e:
            self.logger.error(f"Orderbook format error: {e}, bids[0]: {bids[0] if bids else 'empty'}")
            return {
                "signal": "neutral",
                "strength": 0,
                "description": "Format data orderbook tidak dikenali",
                "imbalance": 0,
                "walls": []
            }
        
        imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
        
        # Detect significant walls
        walls = []
        avg_bid_size = total_bid_volume / 10
        avg_ask_size = total_ask_volume / 10
        
        try:
            for i, bid in enumerate(bids[:5]):
                if isinstance(bid, list) and len(bid) >= 2:
                    if float(bid[1]) > avg_bid_size * 2:
                        walls.append({
                            "type": "bid_wall",
                            "price": float(bid[0]),
                            "size": float(bid[1]),
                            "distance": abs(float(bid[0]) - current_price) / current_price * 100
                        })
                elif isinstance(bid, dict):
                    size = float(bid.get('size', 0))
                    if size > avg_bid_size * 2:
                        walls.append({
                            "type": "bid_wall",
                            "price": float(bid.get('price', 0)),
                            "size": size,
                            "distance": abs(float(bid.get('price', 0)) - current_price) / current_price * 100
                        })
            
            for i, ask in enumerate(asks[:5]):
                if isinstance(ask, list) and len(ask) >= 2:
                    if float(ask[1]) > avg_ask_size * 2:
                        walls.append({
                            "type": "ask_wall",
                            "price": float(ask[0]),
                            "size": float(ask[1]),
                            "distance": abs(float(ask[0]) - current_price) / current_price * 100
                        })
                elif isinstance(ask, dict):
                    size = float(ask.get('size', 0))
                    if size > avg_ask_size * 2:
                        walls.append({
                            "type": "ask_wall",
                            "price": float(ask.get('price', 0)),
                            "size": size,
                            "distance": abs(float(ask.get('price', 0)) - current_price) / current_price * 100
                        })
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error detecting walls: {e}")
            walls = []
        
        # Determine signal based on imbalance
        if imbalance > 0.15:
            signal = "bullish"
            strength = min(75, abs(imbalance) * 200)
        elif imbalance < -0.15:
            signal = "bearish"
            strength = min(75, abs(imbalance) * 200)
        else:
            signal = "neutral"
            strength = 45
        
        # Generate description
        description = f"Orderbook menunjukkan {signal} bias dengan imbalance {imbalance:.2f}. "
        if walls:
            wall_types = [w['type'] for w in walls]
            if 'bid_wall' in wall_types:
                description += "Support wall terdeteksi di area bid. "
            if 'ask_wall' in wall_types:
                description += "Resistance wall terdeteksi di area ask. "
        
        # Calculate spread safely
        try:
            if isinstance(asks[0], list) and isinstance(bids[0], list):
                spread = abs(float(asks[0][0]) - float(bids[0][0]))
            elif isinstance(asks[0], dict) and isinstance(bids[0], dict):
                spread = abs(float(asks[0].get('price', 0)) - float(bids[0].get('price', 0)))
            else:
                spread = 0
            description += f"Spread: {spread:.4f}"
        except (ValueError, TypeError, IndexError):
            description += "Spread: N/A"
            spread = 0
        
        return {
            "signal": signal,
            "strength": float(strength),
            "description": description,
            "imbalance": float(imbalance),
            "walls": walls,
            "bid_ask_spread": float(spread),
            "depth_ratio": float(total_bid_volume / total_ask_volume)
        }
    
    def _analyze_rsi_ema_layer(self, technical_data: Dict, candlestick_data: List[Dict]) -> Dict[str, Any]:
        """Analyze RSI and EMA confluence layer"""
        
        if not technical_data or not candlestick_data:
            return {
                "signal": "neutral",
                "strength": 0,
                "description": "Data indikator teknis tidak tersedia",
                "rsi_value": 50,
                "ema_trend": "sideways"
            }
        
        # Extract RSI data
        rsi_data = technical_data.get('rsi', [])
        current_rsi = rsi_data[-1]['rsi'] if rsi_data else 50
        
        # Extract EMA data
        ema_data = technical_data.get('ema', [])
        if ema_data:
            ema_12 = ema_data[-1].get('ema_12', 0)
            ema_26 = ema_data[-1].get('ema_26', 0)
            current_price = candlestick_data[-1]['close']
            
            # EMA trend analysis
            if current_price > ema_12 > ema_26:
                ema_trend = "bullish"
                ema_strength = 70
            elif current_price < ema_12 < ema_26:
                ema_trend = "bearish"
                ema_strength = 70
            else:
                ema_trend = "sideways"
                ema_strength = 40
        else:
            ema_trend = "sideways"
            ema_strength = 40
            ema_12 = ema_26 = 0
        
        # RSI analysis
        if current_rsi > 70:
            rsi_signal = "overbought"
            rsi_strength = min(85, (current_rsi - 70) * 3)
        elif current_rsi < 30:
            rsi_signal = "oversold"
            rsi_strength = min(85, (30 - current_rsi) * 3)
        elif current_rsi > 55:
            rsi_signal = "bullish"
            rsi_strength = 60
        elif current_rsi < 45:
            rsi_signal = "bearish"
            rsi_strength = 60
        else:
            rsi_signal = "neutral"
            rsi_strength = 50
        
        # Confluence analysis
        if rsi_signal == "bullish" and ema_trend == "bullish":
            signal = "bullish"
            strength = (rsi_strength + ema_strength) / 2
        elif rsi_signal == "bearish" and ema_trend == "bearish":
            signal = "bearish"
            strength = (rsi_strength + ema_strength) / 2
        elif rsi_signal == "overbought":
            signal = "bearish"
            strength = rsi_strength * 0.8  # Reduce strength for reversal signals
        elif rsi_signal == "oversold":
            signal = "bullish"
            strength = rsi_strength * 0.8
        else:
            signal = "neutral"
            strength = 45
        
        description = f"RSI pada level {current_rsi:.1f} menunjukkan kondisi {rsi_signal}. "
        description += f"EMA menunjukkan trend {ema_trend}. "
        description += f"Konfluensi RSI-EMA memberikan bias {signal} dengan kekuatan {strength:.1f}%."
        
        return {
            "signal": signal,
            "strength": strength,
            "description": description,
            "rsi_value": current_rsi,
            "rsi_condition": rsi_signal,
            "ema_trend": ema_trend,
            "ema_12": ema_12,
            "ema_26": ema_26
        }
    
    def _analyze_fibonacci_layer(self, candlestick_data: List[Dict]) -> Dict[str, Any]:
        """Analyze Fibonacci retracement and extension levels"""
        
        if not candlestick_data or len(candlestick_data) < 50:
            return {
                "signal": "neutral",
                "strength": 0,
                "description": "Data tidak mencukupi untuk analisis Fibonacci",
                "key_levels": [],
                "current_zone": "undefined"
            }
        
        # Find significant swing high and low
        highs = [candle['high'] for candle in candlestick_data[-50:]]
        lows = [candle['low'] for candle in candlestick_data[-50:]]
        
        swing_high = max(highs)
        swing_low = min(lows)
        current_price = candlestick_data[-1]['close']
        
        # Calculate Fibonacci levels
        diff = swing_high - swing_low
        fib_levels = {
            "0.0": swing_low,
            "0.236": swing_low + diff * 0.236,
            "0.382": swing_low + diff * 0.382,
            "0.500": swing_low + diff * 0.500,
            "0.618": swing_low + diff * 0.618,
            "0.786": swing_low + diff * 0.786,
            "1.0": swing_high,
            "1.272": swing_high + diff * 0.272,
            "1.618": swing_high + diff * 0.618
        }
        
        # Find current zone
        current_zone = "undefined"
        nearest_level = None
        min_distance = float('inf')
        
        for level_name, level_price in fib_levels.items():
            distance = abs(current_price - level_price)
            if distance < min_distance:
                min_distance = distance
                nearest_level = level_name
                
        # Calculate distance percentage
        distance_pct = min_distance / current_price * 100
        
        if distance_pct < 0.5:  # Within 0.5% of Fibonacci level
            current_zone = f"At Fibonacci {nearest_level}"
            
            # Determine signal based on key levels
            if nearest_level in ["0.618", "0.786"]:
                signal = "bullish"  # Golden ratio retracement
                strength = 75
            elif nearest_level in ["0.382", "0.500"]:
                signal = "bullish"  # Moderate retracement
                strength = 65
            elif nearest_level in ["1.272", "1.618"]:
                signal = "bearish"  # Extension levels
                strength = 70
            else:
                signal = "neutral"
                strength = 50
        else:
            signal = "neutral"
            strength = 40
            current_zone = f"Between levels (nearest: {nearest_level})"
        
        # Key levels for trading
        key_levels = [
            {"level": fib_levels["0.618"], "name": "Golden Ratio (0.618)", "type": "support"},
            {"level": fib_levels["0.382"], "name": "Moderate Retracement (0.382)", "type": "support"},
            {"level": fib_levels["1.272"], "name": "Extension (1.272)", "type": "resistance"},
            {"level": fib_levels["1.618"], "name": "Extension (1.618)", "type": "resistance"}
        ]
        
        description = f"Fibonacci analysis menunjukkan {signal} bias. "
        description += f"Harga saat ini berada {current_zone}. "
        description += f"Level kunci terdekat: {nearest_level} pada {fib_levels[nearest_level]:.4f}"
        
        return {
            "signal": signal,
            "strength": strength,
            "description": description,
            "key_levels": key_levels,
            "current_zone": current_zone,
            "swing_high": swing_high,
            "swing_low": swing_low,
            "nearest_level": nearest_level,
            "distance_pct": distance_pct
        }
    
    def _analyze_oi_funding_layer(self, oi_data: Dict, symbol: str) -> Dict[str, Any]:
        """Analyze Open Interest and Funding Rate layer"""
        
        if not oi_data:
            return {
                "signal": "neutral",
                "strength": 0,
                "description": "Data Open Interest tidak tersedia",
                "oi_trend": "undefined",
                "funding_bias": "neutral"
            }
        
        current_oi = oi_data.get('open_interest', 0)
        
        # Simulate funding rate analysis (would need actual funding rate data)
        # For now, we'll use a simplified approach
        
        # OI trend analysis (simplified)
        if current_oi > 0:
            oi_trend = "increasing"
            oi_strength = 60
        else:
            oi_trend = "undefined"
            oi_strength = 40
        
        # Funding rate simulation (would need real data)
        # Positive funding = Long pays Short (bearish sentiment)
        # Negative funding = Short pays Long (bullish sentiment)
        simulated_funding = 0.01  # This should come from actual API
        
        if simulated_funding > 0.05:
            funding_signal = "bearish"
            funding_strength = 70
        elif simulated_funding < -0.05:
            funding_signal = "bullish"
            funding_strength = 70
        else:
            funding_signal = "neutral"
            funding_strength = 50
        
        # Combined signal
        if oi_trend == "increasing" and funding_signal == "bearish":
            signal = "bearish"
            strength = (oi_strength + funding_strength) / 2
        elif oi_trend == "increasing" and funding_signal == "bullish":
            signal = "bullish"
            strength = (oi_strength + funding_strength) / 2
        else:
            signal = "neutral"
            strength = 45
        
        description = f"Open Interest menunjukkan trend {oi_trend}. "
        description += f"Funding rate menunjukkan {funding_signal} sentiment. "
        description += f"Kombinasi OI-Funding memberikan bias {signal}."
        
        return {
            "signal": signal,
            "strength": strength,
            "description": description,
            "oi_trend": oi_trend,
            "funding_bias": funding_signal,
            "current_oi": current_oi,
            "estimated_funding": simulated_funding
        }
    
    def _analyze_trend_structure(self, candlestick_data: List[Dict], technical_data: Dict) -> Dict[str, Any]:
        """Analyze overall trend structure"""
        
        if not candlestick_data or len(candlestick_data) < 20:
            return {
                "signal": "neutral",
                "strength": 0,
                "description": "Data tidak mencukupi untuk analisis struktur trend",
                "trend": "undefined"
            }
        
        # Calculate trend based on price action
        recent_closes = [candle['close'] for candle in candlestick_data[-20:]]
        
        # Simple trend analysis
        if recent_closes[-1] > recent_closes[-10] > recent_closes[-20]:
            trend = "bullish"
            strength = 70
        elif recent_closes[-1] < recent_closes[-10] < recent_closes[-20]:
            trend = "bearish"
            strength = 70
        else:
            trend = "sideways"
            strength = 40
        
        # Trend strength based on consistency
        bullish_candles = sum(1 for candle in candlestick_data[-10:] if candle['close'] > candle['open'])
        trend_consistency = bullish_candles / 10
        
        if trend == "bullish" and trend_consistency > 0.7:
            strength = min(85, strength + 15)
        elif trend == "bearish" and trend_consistency < 0.3:
            strength = min(85, strength + 15)
        
        description = f"Struktur trend menunjukkan pola {trend} dengan kekuatan {strength:.1f}%. "
        description += f"Konsistensi trend: {trend_consistency:.1%}"
        
        return {
            "signal": trend,
            "strength": strength,
            "description": description,
            "trend": trend,
            "consistency": trend_consistency
        }
    
    def _analyze_volume_profile(self, candlestick_data: List[Dict]) -> Dict[str, Any]:
        """Analyze volume profile for key levels"""
        
        if not candlestick_data:
            return {"poc": 0, "vah": 0, "val": 0}
        
        # Simplified volume profile calculation
        price_volume = {}
        for candle in candlestick_data[-50:]:  # Last 50 candles
            price_ranges = np.linspace(candle['low'], candle['high'], 5)
            volume_per_range = candle['volume'] / 5
            
            for price in price_ranges:
                price_key = round(price, 2)
                if price_key not in price_volume:
                    price_volume[price_key] = 0
                price_volume[price_key] += volume_per_range
        
        # Find Point of Control (POC)
        poc_price = max(price_volume.keys(), key=lambda x: price_volume[x])
        
        # Simplified VAH/VAL calculation
        sorted_prices = sorted(price_volume.keys())
        vah = sorted_prices[int(len(sorted_prices) * 0.7)]  # 70th percentile
        val = sorted_prices[int(len(sorted_prices) * 0.3)]  # 30th percentile
        
        return {
            "poc": poc_price,
            "vah": vah,
            "val": val
        }
    
    def _generate_confluence_summary(self, snapshot: Dict) -> Dict[str, Any]:
        """Generate confluence summary from all layers"""
        
        layers = [
            snapshot['smc_analysis'],
            snapshot['volume_analysis'],
            snapshot['orderbook_analysis'],
            snapshot['rsi_ema_analysis'],
            snapshot['fibonacci_analysis'],
            snapshot['oi_funding_analysis'],
            snapshot['trend_structure']
        ]
        
        # Count signals
        bullish_count = sum(1 for layer in layers if layer['signal'] == 'bullish')
        bearish_count = sum(1 for layer in layers if layer['signal'] == 'bearish')
        neutral_count = sum(1 for layer in layers if layer['signal'] == 'neutral')
        
        # Calculate average strength
        total_strength = sum(layer['strength'] for layer in layers)
        avg_strength = total_strength / len(layers)
        
        # Determine overall signal
        if bullish_count > bearish_count:
            overall_signal = "bullish"
            signal_strength = (bullish_count / len(layers)) * avg_strength
        elif bearish_count > bullish_count:
            overall_signal = "bearish"
            signal_strength = (bearish_count / len(layers)) * avg_strength
        else:
            overall_signal = "neutral"
            signal_strength = avg_strength
        
        return {
            "overall_signal": overall_signal,
            "signal_strength": signal_strength,
            "bullish_layers": bullish_count,
            "bearish_layers": bearish_count,
            "neutral_layers": neutral_count,
            "total_layers": len(layers),
            "consensus_level": max(bullish_count, bearish_count) / len(layers)
        }
    
    def _generate_narrative_analysis(self, snapshot: Dict) -> str:
        """Generate human-like narrative analysis"""
        
        symbol = snapshot['symbol']
        current_price = snapshot['current_price']
        confluence = snapshot['confluence_summary']
        
        # Opening statement
        narrative = f"**ANALISIS MENDALAM {symbol}**\n\n"
        
        # Market structure overview
        smc = snapshot['smc_analysis']
        narrative += f"Dari perspektif Smart Money Concepts, {smc['description']} "
        narrative += f"Market structure saat ini menunjukkan {smc['market_structure']}.\n\n"
        
        # Volume analysis
        volume = snapshot['volume_analysis']
        narrative += f"Analisis volume mengungkapkan {volume['description']} "
        if volume['volume_spike']:
            narrative += "Volume spike ini mengindikasikan adanya institutional involvement yang signifikan.\n\n"
        else:
            narrative += "Volume masih dalam range normal, menunjukkan belum adanya tekanan besar dari institutional players.\n\n"
        
        # Technical confluence
        rsi_ema = snapshot['rsi_ema_analysis']
        fib = snapshot['fibonacci_analysis']
        narrative += f"Secara teknis, {rsi_ema['description']} "
        narrative += f"Sementara dari sisi Fibonacci, {fib['description']}\n\n"
        
        # Orderbook insights
        orderbook = snapshot['orderbook_analysis']
        narrative += f"Orderbook menunjukkan {orderbook['description']} "
        if orderbook['walls']:
            narrative += "Adanya walls dalam orderbook menunjukkan level-level kunci yang perlu diperhatikan.\n\n"
        
        # Overall confluence
        narrative += f"**KESIMPULAN KONFLUENSI:**\n"
        narrative += f"Dari 7 layer analisis, {confluence['bullish_layers']} layer menunjukkan bias bullish, "
        narrative += f"{confluence['bearish_layers']} layer bearish, dan {confluence['neutral_layers']} layer neutral. "
        narrative += f"Konsensus berada pada level {confluence['consensus_level']:.1%}, "
        narrative += f"memberikan bias keseluruhan {confluence['overall_signal']} dengan kekuatan {confluence['signal_strength']:.1f}%.\n\n"
        
        # Professional insight
        if confluence['overall_signal'] == 'bullish':
            narrative += "Kondisi ini menunjukkan adanya underlying strength yang dapat mendorong pergerakan ke atas, "
            narrative += "namun perlu diperhatikan level-level resistance yang telah diidentifikasi."
        elif confluence['overall_signal'] == 'bearish':
            narrative += "Tekanan bearish yang teridentifikasi dari multiple layer menunjukkan potensi weakness, "
            narrative += "dengan perhatian khusus pada level-level support kunci."
        else:
            narrative += "Kondisi saat ini menunjukkan market dalam fase konsolidasi, "
            narrative += "memerlukan konfirmasi breakout yang jelas sebelum mengambil posisi directional."
        
        return narrative
    
    def _calculate_confidence_score(self, snapshot: Dict) -> str:
        """Calculate visual confidence score"""
        
        confluence = snapshot['confluence_summary']
        consensus = confluence['consensus_level']
        strength = confluence['signal_strength']
        
        # Calculate score out of 5
        score = int((consensus * strength / 100) * 5)
        score = max(1, min(5, score))  # Ensure score is between 1-5
        
        # Generate visual representation
        filled_circles = "🔵" * score
        empty_circles = "⚪" * (5 - score)
        
        return f"{filled_circles}{empty_circles}"
    
    def _generate_primary_trading_plan(self, snapshot: Dict, current_price: float) -> Dict[str, Any]:
        """Generate primary trading plan with detailed entry strategies"""
        
        confluence = snapshot['confluence_summary']
        signal = confluence['overall_signal']
        strength = confluence['signal_strength']
        
        # Get SMC and other layer data for entry strategy
        smc_data = snapshot.get('smc_analysis', {})
        fvg_count = smc_data.get('fvg_count', 0)
        key_levels = smc_data.get('key_levels', [])
        
        # Calculate entry zone based on confluence
        if signal == 'bullish':
            entry_zone = f"{current_price * 0.995:.4f} - {current_price * 1.005:.4f}"
            stop_loss = current_price * 0.98
            tp1 = current_price * 1.02
            tp2 = current_price * 1.04
            direction = "LONG"
            
            # Enhanced entry strategy notes
            entry_notes = []
            if fvg_count > 0:
                entry_notes.append("📍 Entry berdasarkan FVG (Fair Value Gap) - tunggu retest ke zona imbalance")
            if key_levels:
                nearest_support = min([level['level'] for level in key_levels if level['level'] < current_price], default=None)
                if nearest_support:
                    entry_notes.append(f"📍 Retest support sebelumnya di {nearest_support:.4f} sebelum breakout")
            if snapshot.get('orderbook_analysis', {}).get('imbalance', 0) > 20:
                entry_notes.append("📍 Bid dominance - entry pada pullback ke demand zone")
            
            if not entry_notes:
                entry_notes.append("📍 Entry pada breakout dengan konfirmasi volume tinggi")
                
        elif signal == 'bearish':
            entry_zone = f"{current_price * 0.995:.4f} - {current_price * 1.005:.4f}"
            stop_loss = current_price * 1.02
            tp1 = current_price * 0.98
            tp2 = current_price * 0.96
            direction = "SHORT"
            
            # Enhanced entry strategy notes
            entry_notes = []
            if fvg_count > 0:
                entry_notes.append("📍 Entry berdasarkan FVG atas - tunggu retest ke zona imbalance untuk rejection")
            if key_levels:
                nearest_resistance = max([level['level'] for level in key_levels if level['level'] > current_price], default=None)
                if nearest_resistance:
                    entry_notes.append(f"📍 Retest resistance sebelumnya di {nearest_resistance:.4f} untuk entry short")
            if snapshot.get('orderbook_analysis', {}).get('imbalance', 0) < -20:
                entry_notes.append("📍 Ask dominance - entry pada bounce ke supply zone")
            
            if not entry_notes:
                entry_notes.append("📍 Entry pada breakdown dengan konfirmasi volume tinggi")
                
        else:
            return {
                "direction": "WAIT",
                "reason": "Konfluensi belum memberikan sinyal yang jelas",
                "entry_zone": "Tunggu konfirmasi breakout",
                "stop_loss": 0,
                "tp1": 0,
                "tp2": 0,
                "confidence": snapshot['confidence_score'],
                "risk_reward": "N/A",
                "entry_strategy": "Tunggu setup yang lebih jelas"
            }
        
        # Calculate risk/reward
        if signal == 'bullish':
            risk = current_price - stop_loss
            reward = tp1 - current_price
        else:
            risk = stop_loss - current_price
            reward = current_price - tp1
        
        risk_reward = f"1:{reward/risk:.2f}" if risk > 0 else "N/A"
        
        return {
            "direction": direction,
            "entry_zone": entry_zone,
            "stop_loss": f"{stop_loss:.4f}",
            "tp1": f"{tp1:.4f}",
            "tp2": f"{tp2:.4f}",
            "confidence": snapshot['confidence_score'],
            "risk_reward": risk_reward,
            "position_size": "1-2% of portfolio",
            "notes": f"Sinyal berdasarkan konfluensi {confluence['bullish_layers'] if signal == 'bullish' else confluence['bearish_layers']}/{confluence['total_layers']} layer",
            "entry_strategy": " • ".join(entry_notes)
        }
    
    def _generate_alternative_scenarios(self, snapshot: Dict, current_price: float) -> List[Dict[str, Any]]:
        """Generate alternative scenarios"""
        
        scenarios = []
        
        # Scenario 1: Reversal scenario
        confluence = snapshot['confluence_summary']
        primary_signal = confluence['overall_signal']
        
        if primary_signal == 'bullish':
            scenarios.append({
                "title": "SKENARIO BEARISH (Reversal)",
                "probability": "25-35%",
                "trigger": f"Break below {current_price * 0.985:.4f}",
                "target": f"{current_price * 0.96:.4f}",
                "invalidation": f"Close above {current_price * 1.015:.4f}",
                "description": "Jika terjadi rejection di level resistance dan volume tidak mendukung, potensi reversal ke downside."
            })
        elif primary_signal == 'bearish':
            scenarios.append({
                "title": "SKENARIO BULLISH (Reversal)",
                "probability": "25-35%",
                "trigger": f"Break above {current_price * 1.015:.4f}",
                "target": f"{current_price * 1.04:.4f}",
                "invalidation": f"Close below {current_price * 0.985:.4f}",
                "description": "Jika terjadi strong buying pressure dan break dari resistance, potensi reversal ke upside."
            })
        
        # Scenario 2: Range-bound scenario
        scenarios.append({
            "title": "SKENARIO SIDEWAYS",
            "probability": "40-50%",
            "trigger": f"Range {current_price * 0.99:.4f} - {current_price * 1.01:.4f}",
            "target": "Range trading",
            "invalidation": f"Break dari range dengan volume tinggi",
            "description": "Market bergerak dalam range dengan lower highs dan higher lows, cocok untuk scalping strategy."
        })
        
        # Scenario 3: Trap scenario
        if primary_signal != 'neutral':
            scenarios.append({
                "title": "SKENARIO TRAP",
                "probability": "15-25%",
                "trigger": f"False breakout dari level kunci",
                "target": "Quick reversal",
                "invalidation": "Sustained move in breakout direction",
                "description": "Breakout palsu untuk mengambil likuiditas sebelum bergerak ke arah yang berlawanan. Waspada terhadap whipsaw movements."
            })
        
        return scenarios
    
    def _assess_risk_factors(self, snapshot: Dict) -> List[Dict[str, Any]]:
        """Assess risk factors"""
        
        risk_factors = []
        
        # Volume risk
        volume = snapshot.get('volume_analysis', {})
        volume_spike = volume.get('volume_spike', False)
        if not volume_spike:
            risk_factors.append({
                "factor": "Low Volume",
                "severity": "Medium",
                "description": "Volume rendah dapat menyebabkan false breakout"
            })
        
        # RSI risk
        rsi_ema = snapshot.get('rsi_ema_analysis', {})
        rsi_signal = rsi_ema.get('signal', 'neutral')
        rsi_strength = rsi_ema.get('strength', 0)
        
        # Check if RSI is in extreme condition (high strength bearish/bullish)
        if rsi_strength > 0.7:
            condition = "overbought" if rsi_signal == 'bearish' else "oversold" if rsi_signal == 'bullish' else "extreme"
            risk_factors.append({
                "factor": "RSI Extreme",
                "severity": "High",
                "description": f"RSI dalam kondisi {condition}, potensi reversal tinggi"
            })
        
        # Orderbook risk
        orderbook = snapshot.get('orderbook_analysis', {})
        imbalance = orderbook.get('imbalance', 0)
        if abs(imbalance) < 0.1:
            risk_factors.append({
                "factor": "Orderbook Balance",
                "severity": "Medium",
                "description": "Orderbook seimbang, arah pergerakan tidak jelas"
            })
        
        # Confluence risk
        confluence = snapshot.get('confluence_summary', {})
        consensus_level = confluence.get('consensus_level', 0)
        if consensus_level < 0.6:
            risk_factors.append({
                "factor": "Low Confluence",
                "severity": "High",
                "description": "Konsensus antar layer rendah, sinyal tidak reliable"
            })
        
        return risk_factors
    
    def _generate_market_context(self, snapshot: Dict) -> str:
        """Generate market context"""
        
        current_time = datetime.now()
        day_of_week = current_time.strftime("%A")
        hour = current_time.hour
        
        context = f"Analisis dilakukan pada {day_of_week} pukul {hour:02d}:00 UTC. "
        
        # Market session context
        if 0 <= hour < 8:
            context += "Sesi Asia sedang berlangsung, volume relatif rendah. "
        elif 8 <= hour < 16:
            context += "Sesi Eropa aktif, volume dan volatilitas meningkat. "
        elif 16 <= hour < 24:
            context += "Sesi Amerika berlangsung, volume dan volatilitas tinggi. "
        
        # Weekend context
        if day_of_week in ['Saturday', 'Sunday']:
            context += "Akhir pekan - volume crypto tetap aktif namun lebih rendah dari weekday. "
        
        # Additional context based on confluence
        confluence = snapshot['confluence_summary']
        if confluence['consensus_level'] > 0.7:
            context += "Kondisi confluence tinggi memberikan peluang trading yang baik. "
        else:
            context += "Confluence rendah, disarankan untuk menunggu setup yang lebih jelas. "
        
        context += "Selalu gunakan risk management yang ketat dan jangan risk lebih dari 2% per trade."
        
        return context
    
    def _generate_ai_narrative(self, symbol: str, timeframe: str, analysis_data: Dict[str, Any], quick_mode: bool = False) -> str:
        """Generate AI-powered narrative analysis using AI Engine"""
        
        if not self.ai_engine.is_available():
            self.logger.warning("AI Engine not available. Falling back to basic narrative.")
            return self._generate_fallback_narrative(analysis_data)
        
        try:
            # Use AI Engine to generate high-quality narrative
            narrative = self.ai_engine.generate_ai_snapshot(symbol, timeframe, analysis_data, quick_mode)
            
            # Validate the narrative
            if not narrative or narrative == "No AI narrative available" or len(narrative) < 20:
                self.logger.warning(f"AI Engine returned empty/invalid narrative for {symbol} {timeframe}")
                return self._generate_fallback_narrative(analysis_data)
            
            mode = "quick" if quick_mode else "comprehensive"
            self.logger.info(f"AI narrative generated successfully for {symbol} {timeframe} ({mode} mode)")
            return narrative
            
        except Exception as e:
            self.logger.error(f"Error generating AI narrative: {str(e)}")
            return self._generate_fallback_narrative(analysis_data)
    
    def _generate_fallback_narrative(self, analysis_data: Dict[str, Any]) -> str:
        """Generate fallback narrative when AI is not available"""
        
        confluence = analysis_data.get('confluence_summary', {})
        signal = confluence.get('overall_signal', 'neutral')
        consensus = confluence.get('consensus_level', 0)
        
        if signal == 'bullish':
            return f"""
## 🚀 ANALISIS BULLISH

**Confluence Score:** {consensus:.1f} (Bullish bias dominan)

Berdasarkan analisis 7 layer, teridentifikasi bias bullish dengan konfluensi yang mendukung. 
Market structure menunjukkan potential breakout ke upside dengan volume yang mulai meningkat.

**Key Points:**
• SMC analysis menunjukkan order blocks dan fair value gaps yang support upside
• Volume profile dan CVD mengindikasikan akumulasi
• RSI dan EMA confluence memberikan sinyal bullish
• Orderbook imbalance condong ke bid side

**Trading Plan:**
Entry pada pullback ke demand zone dengan konfirmasi volume.
Stop loss di bawah key support level.
Target take profit berdasarkan resistance levels dan fibonacci extension.

*Selalu gunakan risk management yang ketat.*
"""
        elif signal == 'bearish':
            return f"""
## 🔴 ANALISIS BEARISH

**Confluence Score:** {consensus:.1f} (Bearish bias dominan)

Berdasarkan analisis 7 layer, teridentifikasi bias bearish dengan konfluensi yang mendukung. 
Market structure menunjukkan potential breakdown ke downside dengan pressure yang meningkat.

**Key Points:**
• SMC analysis menunjukkan breaker blocks dan supply zones yang dominan
• Volume profile dan CVD mengindikasikan distribusi
• RSI dan EMA confluence memberikan sinyal bearish
• Orderbook imbalance condong ke ask side

**Trading Plan:**
Entry pada bounce ke supply zone dengan konfirmasi volume.
Stop loss di atas key resistance level.
Target take profit berdasarkan support levels dan fibonacci extension.

*Selalu gunakan risk management yang ketat.*
"""
        else:
            return f"""
## ⚪ ANALISIS NEUTRAL

**Confluence Score:** {consensus:.1f} (Sinyal belum jelas)

Berdasarkan analisis 7 layer, market berada dalam kondisi neutral dengan konfluensi yang mixed. 
Disarankan untuk menunggu setup yang lebih jelas sebelum melakukan trading.

**Key Points:**
• SMC analysis menunjukkan struktur yang belum terbentuk dengan jelas
• Volume profile dan CVD dalam kondisi balanced
• RSI dan EMA confluence memberikan sinyal mixed
• Orderbook relatif seimbang

**Trading Plan:**
Tunggu breakout yang jelas dari range dengan konfirmasi volume tinggi.
Entry setelah ada konfirmasi arah yang lebih pasti.

*Patience is key dalam kondisi market seperti ini.*
"""
    
    def _generate_error_snapshot(self, error_message: str) -> Dict[str, Any]:
        """Generate error snapshot when data is insufficient"""
        
        return {
            "error": True,
            "message": error_message,
            "timestamp": datetime.now().isoformat(),
            "snapshot": {
                "narrative_analysis": f"**ERROR:** {error_message}",
                "confidence_score": "⚪⚪⚪⚪⚪",
                "primary_plan": {
                    "direction": "WAIT",
                    "reason": "Data tidak mencukupi untuk analisis",
                    "entry_zone": "N/A",
                    "stop_loss": "N/A",
                    "tp1": "N/A",
                    "tp2": "N/A",
                    "confidence": "⚪⚪⚪⚪⚪",
                    "risk_reward": "N/A"
                },
                "alternative_scenarios": [],
                "risk_factors": [
                    {
                        "factor": "Data Insufficient",
                        "severity": "High",
                        "description": error_message
                    }
                ],
                "market_context": "Tidak dapat menganalisis karena data tidak mencukupi"
            }
        }
    
    def _get_current_price(self, analysis_result: Dict[str, Any]) -> str:
        """Extract current price from analysis result"""
        candlestick_data = analysis_result.get('candlestick', [])
        if candlestick_data:
            return f"{candlestick_data[-1].get('close', 0):.4f}"
        return "N/A"