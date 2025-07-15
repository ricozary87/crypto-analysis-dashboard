"""
Signal Engine - Comprehensive Trading Signal Generator
Combines technical indicators, SMC analysis, price action, and market data
"""

import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from indicator_calculator import IndicatorCalculator
from smc_analyzer import SMCAnalyzer
from price_action import PriceActionAnalyzer

class SignalEngine:
    def __init__(self):
        self.indicator_calc = IndicatorCalculator()
        self.smc_analyzer = SMCAnalyzer()
        self.price_action_analyzer = PriceActionAnalyzer()
        
        # Signal weights for different analysis types
        self.weights = {
            'technical_indicators': 0.3,
            'smc_analysis': 0.3,
            'price_action': 0.25,
            'volume_analysis': 0.15
        }
    
    def generate_comprehensive_signals(self, data: List[Dict], orderbook: Dict = None, 
                                     open_interest: Dict = None) -> Dict[str, Any]:
        """Generate comprehensive trading signals from all analysis modules"""
        
        if not data or len(data) < 50:
            return {
                'error': 'Insufficient data for signal generation',
                'min_required': 50,
                'received': len(data) if data else 0
            }
        
        try:
            # 1. Technical Indicators Analysis
            technical_signals = self._analyze_technical_indicators(data)
            
            # 2. SMC Analysis
            smc_signals = self._analyze_smc(data)
            
            # 3. Price Action Analysis
            price_action_signals = self._analyze_price_action(data)
            
            # 4. Volume Analysis
            volume_signals = self._analyze_volume(data)
            
            # 5. Orderbook Analysis (if available)
            orderbook_signals = self._analyze_orderbook(orderbook) if orderbook else {}
            
            # 6. Open Interest Analysis (if available)
            oi_signals = self._analyze_open_interest(open_interest) if open_interest else {}
            
            # 7. Generate Final Signal
            final_signal = self._generate_final_signal(
                technical_signals, smc_signals, price_action_signals, 
                volume_signals, orderbook_signals, oi_signals
            )
            
            # 8. Risk Management
            risk_assessment = self._assess_risk(data, final_signal)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'Current Symbol',
                'final_signal': final_signal,
                'risk_assessment': risk_assessment,
                'component_signals': {
                    'technical_indicators': technical_signals,
                    'smc_analysis': smc_signals,
                    'price_action': price_action_signals,
                    'volume_analysis': volume_signals,
                    'orderbook_analysis': orderbook_signals,
                    'open_interest_analysis': oi_signals
                },
                'confidence_score': final_signal.get('confidence', 0),
                'trade_setup': self._generate_trade_setup(final_signal, risk_assessment, data)
            }
            
        except Exception as e:
            logging.error(f"Error generating signals: {str(e)}")
            return {
                'error': f'Signal generation failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_technical_indicators(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze technical indicators for signal generation"""
        # Ensure all timestamps are integers before calculations
        normalized_data = []
        for item in data:
            normalized_item = item.copy()
            if isinstance(normalized_item.get('timestamp'), str):
                normalized_item['timestamp'] = int(normalized_item['timestamp'])
            normalized_data.append(normalized_item)
        
        indicators = self.indicator_calc.calculate_all_indicators(normalized_data)
        
        if not indicators:
            return {'signal': 'neutral', 'strength': 0, 'components': []}
        
        signals = []
        current_price = data[-1]['close']
        
        # RSI Signal
        if 'rsi' in indicators and indicators['rsi']:
            rsi_current = indicators['rsi'][-1]
            if rsi_current['oversold']:
                signals.append({'type': 'rsi', 'signal': 'buy', 'strength': 70})
            elif rsi_current['overbought']:
                signals.append({'type': 'rsi', 'signal': 'sell', 'strength': 70})
        
        # MACD Signal
        if 'macd' in indicators and indicators['macd']:
            macd_current = indicators['macd'][-1]
            if macd_current['bullish_crossover']:
                signals.append({'type': 'macd', 'signal': 'buy', 'strength': 80})
            elif macd_current['bearish_crossover']:
                signals.append({'type': 'macd', 'signal': 'sell', 'strength': 80})
        
        # EMA Trend Signal
        if 'ema_21' in indicators and 'ema_50' in indicators:
            if (len(indicators['ema_21']) > 0 and len(indicators['ema_50']) > 0):
                ema21 = indicators['ema_21'][-1]
                ema50 = indicators['ema_50'][-1]
                
                if ema21 > ema50 and current_price > ema21:
                    signals.append({'type': 'ema_trend', 'signal': 'buy', 'strength': 60})
                elif ema21 < ema50 and current_price < ema21:
                    signals.append({'type': 'ema_trend', 'signal': 'sell', 'strength': 60})
        
        # Bollinger Bands Signal
        if 'bollinger_bands' in indicators and indicators['bollinger_bands']:
            bb_current = indicators['bollinger_bands'][-1]
            if bb_current['breakout_up']:
                signals.append({'type': 'bollinger', 'signal': 'buy', 'strength': 50})
            elif bb_current['breakout_down']:
                signals.append({'type': 'bollinger', 'signal': 'sell', 'strength': 50})
        
        # Calculate overall technical signal
        buy_signals = [s for s in signals if s['signal'] == 'buy']
        sell_signals = [s for s in signals if s['signal'] == 'sell']
        
        if buy_signals and len(buy_signals) > len(sell_signals):
            avg_strength = np.mean([s['strength'] for s in buy_signals])
            overall_signal = 'buy'
        elif sell_signals and len(sell_signals) > len(buy_signals):
            avg_strength = np.mean([s['strength'] for s in sell_signals])
            overall_signal = 'sell'
        else:
            avg_strength = 0
            overall_signal = 'neutral'
        
        return {
            'signal': overall_signal,
            'strength': avg_strength,
            'components': signals,
            'trend_analysis': indicators.get('trend_analysis', {})
        }
    
    def _analyze_smc(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze Smart Money Concepts for signal generation"""
        # Ensure all timestamps are integers before calculations
        normalized_data = []
        for item in data:
            normalized_item = item.copy()
            if isinstance(normalized_item.get('timestamp'), str):
                normalized_item['timestamp'] = int(normalized_item['timestamp'])
            normalized_data.append(normalized_item)
        
        smc_analysis = self.smc_analyzer.analyze_market_structure(normalized_data)
        
        if not smc_analysis:
            return {'signal': 'neutral', 'strength': 0, 'components': []}
        
        signals = []
        
        # CHoCH and BOS Signals
        if 'choch_bos_signals' in smc_analysis:
            recent_signals = smc_analysis['choch_bos_signals'][-3:] if smc_analysis['choch_bos_signals'] else []
            
            for signal in recent_signals:
                if signal['direction'] == 'bullish':
                    signals.append({
                        'type': signal['type'],
                        'signal': 'buy',
                        'strength': min(signal.get('strength', 50), 90)
                    })
                elif signal['direction'] == 'bearish':
                    signals.append({
                        'type': signal['type'],
                        'signal': 'sell',
                        'strength': min(signal.get('strength', 50), 90)
                    })
        
        # Order Block Signals
        if 'order_blocks' in smc_analysis:
            recent_obs = smc_analysis['order_blocks'][-2:] if smc_analysis['order_blocks'] else []
            
            for ob in recent_obs:
                if ob['type'] == 'bullish_ob':
                    signals.append({
                        'type': 'order_block',
                        'signal': 'buy',
                        'strength': min(ob.get('strength', 60), 80)
                    })
                elif ob['type'] == 'bearish_ob':
                    signals.append({
                        'type': 'order_block',
                        'signal': 'sell',
                        'strength': min(ob.get('strength', 60), 80)
                    })
        
        # FVG Signals
        if 'fvg_signals' in smc_analysis:
            recent_fvg = smc_analysis['fvg_signals'][-2:] if smc_analysis['fvg_signals'] else []
            
            for fvg in recent_fvg:
                if fvg['type'] == 'bullish_fvg':
                    signals.append({
                        'type': 'fvg',
                        'signal': 'buy',
                        'strength': 70
                    })
                elif fvg['type'] == 'bearish_fvg':
                    signals.append({
                        'type': 'fvg',
                        'signal': 'sell',
                        'strength': 70
                    })
        
        # Liquidity Sweep Signals
        if 'liquidity_sweeps' in smc_analysis:
            recent_sweeps = smc_analysis['liquidity_sweeps'][-2:] if smc_analysis['liquidity_sweeps'] else []
            
            for sweep in recent_sweeps:
                if sweep['direction'] == 'bullish':
                    signals.append({
                        'type': 'liquidity_sweep',
                        'signal': 'buy',
                        'strength': 85
                    })
                elif sweep['direction'] == 'bearish':
                    signals.append({
                        'type': 'liquidity_sweep',
                        'signal': 'sell',
                        'strength': 85
                    })
        
        # Calculate overall SMC signal
        buy_signals = [s for s in signals if s['signal'] == 'buy']
        sell_signals = [s for s in signals if s['signal'] == 'sell']
        
        if buy_signals and len(buy_signals) > len(sell_signals):
            avg_strength = np.mean([s['strength'] for s in buy_signals])
            overall_signal = 'buy'
        elif sell_signals and len(sell_signals) > len(buy_signals):
            avg_strength = np.mean([s['strength'] for s in sell_signals])
            overall_signal = 'sell'
        else:
            avg_strength = 0
            overall_signal = 'neutral'
        
        return {
            'signal': overall_signal,
            'strength': avg_strength,
            'components': signals,
            'market_structure': smc_analysis.get('market_structure', {})
        }
    
    def _analyze_price_action(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze price action for signal generation"""
        price_action_analysis = self.price_action_analyzer.analyze_price_action(data)
        
        if not price_action_analysis:
            return {'signal': 'neutral', 'strength': 0, 'components': []}
        
        signals = []
        
        # Candlestick Pattern Signals
        if 'candlestick_patterns' in price_action_analysis:
            recent_patterns = price_action_analysis['candlestick_patterns'][-3:] if price_action_analysis['candlestick_patterns'] else []
            
            for pattern in recent_patterns:
                if 'bullish' in pattern['type']:
                    signals.append({
                        'type': f"pattern_{pattern['pattern']}",
                        'signal': 'buy',
                        'strength': min(pattern.get('strength', 50), 75)
                    })
                elif 'bearish' in pattern['type']:
                    signals.append({
                        'type': f"pattern_{pattern['pattern']}",
                        'signal': 'sell',
                        'strength': min(pattern.get('strength', 50), 75)
                    })
        
        # Breakout Signals
        if 'breakout_signals' in price_action_analysis:
            recent_breakouts = price_action_analysis['breakout_signals'][-2:] if price_action_analysis['breakout_signals'] else []
            
            for breakout in recent_breakouts:
                if breakout['direction'] == 'bullish':
                    signals.append({
                        'type': 'breakout',
                        'signal': 'buy',
                        'strength': min(breakout.get('strength', 60), 85)
                    })
                elif breakout['direction'] == 'bearish':
                    signals.append({
                        'type': 'breakout',
                        'signal': 'sell',
                        'strength': min(breakout.get('strength', 60), 85)
                    })
        
        # Calculate overall price action signal
        buy_signals = [s for s in signals if s['signal'] == 'buy']
        sell_signals = [s for s in signals if s['signal'] == 'sell']
        
        if buy_signals and len(buy_signals) > len(sell_signals):
            avg_strength = np.mean([s['strength'] for s in buy_signals])
            overall_signal = 'buy'
        elif sell_signals and len(sell_signals) > len(buy_signals):
            avg_strength = np.mean([s['strength'] for s in sell_signals])
            overall_signal = 'sell'
        else:
            avg_strength = 0
            overall_signal = 'neutral'
        
        return {
            'signal': overall_signal,
            'strength': avg_strength,
            'components': signals,
            'current_structure': price_action_analysis.get('current_structure', {})
        }
    
    def _analyze_volume(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze volume for signal confirmation"""
        if len(data) < 20:
            return {'signal': 'neutral', 'strength': 0, 'components': []}
        
        signals = []
        
        # Volume spike analysis
        recent_volumes = [candle['volume'] for candle in data[-20:]]
        avg_volume = np.mean(recent_volumes[:-1])
        current_volume = data[-1]['volume']
        
        if current_volume > avg_volume * 2:
            # High volume suggests strong move
            price_direction = 'buy' if data[-1]['close'] > data[-2]['close'] else 'sell'
            signals.append({
                'type': 'volume_spike',
                'signal': price_direction,
                'strength': min((current_volume / avg_volume) * 20, 80)
            })
        
        # Volume trend analysis
        recent_volume_trend = np.mean(recent_volumes[-5:]) / np.mean(recent_volumes[-10:-5])
        
        if recent_volume_trend > 1.3:
            signals.append({
                'type': 'volume_trend',
                'signal': 'buy' if data[-1]['close'] > data[-5]['close'] else 'sell',
                'strength': min(recent_volume_trend * 30, 70)
            })
        
        # Calculate overall volume signal
        buy_signals = [s for s in signals if s['signal'] == 'buy']
        sell_signals = [s for s in signals if s['signal'] == 'sell']
        
        if buy_signals and len(buy_signals) > len(sell_signals):
            avg_strength = np.mean([s['strength'] for s in buy_signals])
            overall_signal = 'buy'
        elif sell_signals and len(sell_signals) > len(buy_signals):
            avg_strength = np.mean([s['strength'] for s in sell_signals])
            overall_signal = 'sell'
        else:
            avg_strength = 0
            overall_signal = 'neutral'
        
        return {
            'signal': overall_signal,
            'strength': avg_strength,
            'components': signals,
            'volume_analysis': {
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 1
            }
        }
    
    def _analyze_orderbook(self, orderbook: Dict) -> Dict[str, Any]:
        """Analyze orderbook for signal generation"""
        if not orderbook or 'bids' not in orderbook or 'asks' not in orderbook:
            return {'signal': 'neutral', 'strength': 0, 'components': []}
        
        signals = []
        
        # Bid/Ask imbalance
        total_bid_volume = sum(bid['size'] for bid in orderbook['bids'][:10])
        total_ask_volume = sum(ask['size'] for ask in orderbook['asks'][:10])
        
        if total_bid_volume > 0 and total_ask_volume > 0:
            imbalance_ratio = total_bid_volume / total_ask_volume
            
            if imbalance_ratio > 2:
                signals.append({
                    'type': 'orderbook_imbalance',
                    'signal': 'buy',
                    'strength': min((imbalance_ratio - 1) * 30, 70)
                })
            elif imbalance_ratio < 0.5:
                signals.append({
                    'type': 'orderbook_imbalance',
                    'signal': 'sell',
                    'strength': min((1 - imbalance_ratio) * 60, 70)
                })
        
        # Large order detection
        if orderbook['bids']:
            large_bids = [bid for bid in orderbook['bids'][:5] if bid['size'] > total_bid_volume * 0.3]
            if large_bids:
                signals.append({
                    'type': 'large_bid',
                    'signal': 'buy',
                    'strength': 60
                })
        
        if orderbook['asks']:
            large_asks = [ask for ask in orderbook['asks'][:5] if ask['size'] > total_ask_volume * 0.3]
            if large_asks:
                signals.append({
                    'type': 'large_ask',
                    'signal': 'sell',
                    'strength': 60
                })
        
        # Calculate overall orderbook signal
        buy_signals = [s for s in signals if s['signal'] == 'buy']
        sell_signals = [s for s in signals if s['signal'] == 'sell']
        
        if buy_signals and len(buy_signals) > len(sell_signals):
            avg_strength = np.mean([s['strength'] for s in buy_signals])
            overall_signal = 'buy'
        elif sell_signals and len(sell_signals) > len(buy_signals):
            avg_strength = np.mean([s['strength'] for s in sell_signals])
            overall_signal = 'sell'
        else:
            avg_strength = 0
            overall_signal = 'neutral'
        
        return {
            'signal': overall_signal,
            'strength': avg_strength,
            'components': signals,
            'orderbook_metrics': {
                'bid_ask_imbalance': imbalance_ratio if 'imbalance_ratio' in locals() else 1,
                'total_bid_volume': total_bid_volume,
                'total_ask_volume': total_ask_volume
            }
        }
    
    def _analyze_open_interest(self, open_interest: Dict) -> Dict[str, Any]:
        """Analyze open interest for signal generation"""
        if not open_interest:
            return {'signal': 'neutral', 'strength': 0, 'components': []}
        
        signals = []
        
        # Open interest trend (would need historical data for proper analysis)
        # For now, we'll use basic analysis
        oi_value = open_interest.get('open_interest', 0)
        
        if oi_value > 0:
            # High OI suggests strong conviction
            signals.append({
                'type': 'open_interest',
                'signal': 'neutral',  # Need more context for direction
                'strength': min(oi_value / 1000000, 50)  # Scale based on OI size
            })
        
        return {
            'signal': 'neutral',
            'strength': 0,
            'components': signals,
            'open_interest_value': oi_value
        }
    
    def _generate_final_signal(self, technical: Dict, smc: Dict, price_action: Dict, 
                             volume: Dict, orderbook: Dict, oi: Dict) -> Dict[str, Any]:
        """Generate final trading signal by combining all analysis"""
        
        # Collect all signals with their weights
        weighted_signals = []
        
        if technical['signal'] != 'neutral':
            weighted_signals.append({
                'signal': technical['signal'],
                'strength': technical['strength'],
                'weight': self.weights['technical_indicators']
            })
        
        if smc['signal'] != 'neutral':
            weighted_signals.append({
                'signal': smc['signal'],
                'strength': smc['strength'],
                'weight': self.weights['smc_analysis']
            })
        
        if price_action['signal'] != 'neutral':
            weighted_signals.append({
                'signal': price_action['signal'],
                'strength': price_action['strength'],
                'weight': self.weights['price_action']
            })
        
        if volume['signal'] != 'neutral':
            weighted_signals.append({
                'signal': volume['signal'],
                'strength': volume['strength'],
                'weight': self.weights['volume_analysis']
            })
        
        if orderbook.get('signal') != 'neutral':
            weighted_signals.append({
                'signal': orderbook['signal'],
                'strength': orderbook['strength'],
                'weight': 0.1  # Lower weight for orderbook
            })
        
        if not weighted_signals:
            return {
                'signal': 'neutral',
                'direction': 'hold',
                'strength': 0,
                'confidence': 0
            }
        
        # Calculate weighted scores
        buy_score = sum(s['strength'] * s['weight'] for s in weighted_signals if s['signal'] == 'buy')
        sell_score = sum(s['strength'] * s['weight'] for s in weighted_signals if s['signal'] == 'sell')
        
        # Determine final signal
        if buy_score > sell_score and buy_score > 30:
            final_signal = 'buy'
            final_strength = buy_score
        elif sell_score > buy_score and sell_score > 30:
            final_signal = 'sell'
            final_strength = sell_score
        else:
            final_signal = 'neutral'
            final_strength = 0
        
        # Calculate confidence based on signal alignment
        buy_signals = len([s for s in weighted_signals if s['signal'] == 'buy'])
        sell_signals = len([s for s in weighted_signals if s['signal'] == 'sell'])
        total_signals = len(weighted_signals)
        
        if total_signals > 0:
            confidence = max(buy_signals, sell_signals) / total_signals * 100
        else:
            confidence = 0
        
        return {
            'signal': final_signal,
            'direction': final_signal,
            'strength': final_strength,
            'confidence': confidence,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'signal_count': {
                'buy': buy_signals,
                'sell': sell_signals,
                'total': total_signals
            }
        }
    
    def _assess_risk(self, data: List[Dict], signal: Dict) -> Dict[str, Any]:
        """Assess risk for the trading signal"""
        if len(data) < 20:
            return {'risk_level': 'high', 'risk_score': 80}
        
        # Calculate volatility
        recent_prices = [candle['close'] for candle in data[-20:]]
        price_changes = [abs(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] 
                        for i in range(1, len(recent_prices))]
        avg_volatility = np.mean(price_changes) * 100
        
        # Risk factors
        risk_factors = []
        
        # Volatility risk
        if avg_volatility > 5:
            risk_factors.append({'type': 'high_volatility', 'impact': 20})
        
        # Confidence risk
        if signal['confidence'] < 60:
            risk_factors.append({'type': 'low_confidence', 'impact': 15})
        
        # Signal strength risk
        if signal['strength'] < 40:
            risk_factors.append({'type': 'weak_signal', 'impact': 10})
        
        # Calculate total risk score
        total_risk = sum(factor['impact'] for factor in risk_factors)
        
        # Determine risk level
        if total_risk > 40:
            risk_level = 'high'
        elif total_risk > 20:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_score': total_risk,
            'volatility': avg_volatility,
            'risk_factors': risk_factors
        }
    
    def _generate_trade_setup(self, signal: Dict, risk: Dict, data: List[Dict]) -> Dict[str, Any]:
        """Generate trade setup recommendations"""
        if signal['signal'] == 'neutral':
            return {'recommendation': 'No trade setup - wait for clearer signals'}
        
        current_price = data[-1]['close']
        
        # Calculate stop loss and take profit based on volatility
        recent_high = max(candle['high'] for candle in data[-10:])
        recent_low = min(candle['low'] for candle in data[-10:])
        
        if signal['direction'] == 'buy':
            stop_loss = recent_low * 0.98  # 2% below recent low
            take_profit = current_price + (current_price - stop_loss) * 2  # 2:1 RR
        else:  # sell
            stop_loss = recent_high * 1.02  # 2% above recent high
            take_profit = current_price - (stop_loss - current_price) * 2  # 2:1 RR
        
        # Position sizing based on risk
        if risk['risk_level'] == 'high':
            position_size = '1-2%'
        elif risk['risk_level'] == 'medium':
            position_size = '2-3%'
        else:
            position_size = '3-5%'
        
        return {
            'direction': signal['direction'],
            'entry_price': current_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward_ratio': abs(take_profit - current_price) / abs(current_price - stop_loss),
            'position_size': position_size,
            'confidence': signal['confidence'],
            'notes': f"Risk level: {risk['risk_level']}, Signal strength: {signal['strength']:.1f}"
        }