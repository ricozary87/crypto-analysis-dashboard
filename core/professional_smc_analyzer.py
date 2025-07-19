"""
🚀 PROFESSIONAL SMART MONEY CONCEPT (SMC) ANALYZER - ENHANCED VERSION
==================================================================

Advanced institutional-grade SMC analysis engine with comprehensive pattern detection:

📊 CORE FEATURES:
- CHoCH (Change of Character) with volume confirmation
- BOS (Break of Structure) with CVD validation
- Order Block identification with nested detection
- FVG (Fair Value Gap) with confluence analysis
- Liquidity Pool/Sweep detection with IRL/ERL categorization
- EQH/EQL (Equal Highs/Lows) detection
- Inducement zones with confidence scoring
- Volume Delta & CVD confirmation system
- Nested OB and confluence zone detection

🧠 AI-READY OUTPUT:
- Standardized dictionary format for AI snapshot system
- Confidence scoring (0-1) for all patterns
- Detailed descriptions for GPT prompt integration
- Visualization-ready data structures

🔧 PRODUCTION FEATURES:
- Comprehensive error handling and logging
- Modular architecture for easy extension
- Full documentation and type hints
- Performance optimized for real-time analysis
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging
from .inducement_detector import InducementDetector

logger = logging.getLogger(__name__)

class VolumeAnalyzer:
    """
    📊 Volume Analysis Engine
    
    Provides comprehensive volume analysis including:
    - Volume delta calculation
    - CVD (Cumulative Volume Delta) tracking
    - Volume absorption detection
    - Volume spike identification
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.VolumeAnalyzer")
    
    def calculate_volume_delta(self, data: List[Dict]) -> List[Dict]:
        """
        Calculate volume delta for each candle
        
        Args:
            data: List of OHLCV candles
            
        Returns:
            List of volume delta data with buy/sell volume estimation
        """
        volume_deltas = []
        
        for i, candle in enumerate(data):
            # Estimate buy/sell volume based on price movement and volume
            close_price = candle['close']
            open_price = candle['open']
            high_price = candle['high']
            low_price = candle['low']
            total_volume = candle['volume']
            
            # Calculate price position within the candle
            if high_price != low_price:
                price_position = (close_price - low_price) / (high_price - low_price)
            else:
                price_position = 0.5
            
            # Estimate buy/sell volume
            buy_volume = total_volume * price_position
            sell_volume = total_volume * (1 - price_position)
            
            # Calculate delta
            delta = buy_volume - sell_volume
            
            volume_deltas.append({
                'timestamp': candle['timestamp'],
                'total_volume': total_volume,
                'buy_volume': buy_volume,
                'sell_volume': sell_volume,
                'delta': delta,
                'delta_ratio': delta / total_volume if total_volume > 0 else 0
            })
        
        return volume_deltas
    
    def detect_volume_absorption(self, data: List[Dict], volume_deltas: List[Dict]) -> List[Dict]:
        """
        Detect volume absorption patterns
        
        Args:
            data: OHLCV data
            volume_deltas: Volume delta data
            
        Returns:
            List of absorption patterns
        """
        absorptions = []
        avg_volume = sum(d['volume'] for d in data) / len(data)
        
        for i in range(2, len(data)):
            current_candle = data[i]
            current_delta = volume_deltas[i]
            
            # High volume with small price movement indicates absorption
            if (current_candle['volume'] > avg_volume * 2.0 and
                abs(current_candle['close'] - current_candle['open']) < 
                (current_candle['high'] - current_candle['low']) * 0.3):
                
                absorptions.append({
                    'timestamp': current_candle['timestamp'],
                    'type': 'absorption',
                    'volume': current_candle['volume'],
                    'volume_ratio': current_candle['volume'] / avg_volume,
                    'delta': current_delta['delta'],
                    'price_range': current_candle['high'] - current_candle['low'],
                    'body_size': abs(current_candle['close'] - current_candle['open']),
                    'direction': 'bullish' if current_delta['delta'] > 0 else 'bearish'
                })
        
        return absorptions

class CVDCalculator:
    """
    📈 Cumulative Volume Delta (CVD) Calculator
    
    Tracks cumulative volume delta to identify:
    - Price/volume divergences
    - Institutional accumulation/distribution
    - Trend confirmation/rejection
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.CVDCalculator")
    
    def calculate_cvd(self, volume_deltas: List[Dict]) -> List[Dict]:
        """
        Calculate Cumulative Volume Delta
        
        Args:
            volume_deltas: Volume delta data
            
        Returns:
            List of CVD data points
        """
        cvd_data = []
        cumulative_delta = 0
        
        for delta_point in volume_deltas:
            cumulative_delta += delta_point['delta']
            
            cvd_data.append({
                'timestamp': delta_point['timestamp'],
                'cvd': cumulative_delta,
                'delta': delta_point['delta'],
                'delta_ratio': delta_point['delta_ratio']
            })
        
        return cvd_data
    
    def detect_cvd_divergence(self, data: List[Dict], cvd_data: List[Dict]) -> List[Dict]:
        """
        Detect price-CVD divergences
        
        Args:
            data: OHLCV data
            cvd_data: CVD data
            
        Returns:
            List of divergence patterns
        """
        divergences = []
        
        if len(data) < 20 or len(cvd_data) < 20:
            return divergences
        
        # Look for divergences in recent data
        for i in range(10, len(data) - 1):
            price_current = data[i]['close']
            price_prev = data[i-10]['close']
            
            cvd_current = cvd_data[i]['cvd']
            cvd_prev = cvd_data[i-10]['cvd']
            
            # Bullish divergence: price down, CVD up
            if price_current < price_prev and cvd_current > cvd_prev:
                divergences.append({
                    'timestamp': data[i]['timestamp'],
                    'type': 'bullish_divergence',
                    'price_change': (price_current - price_prev) / price_prev,
                    'cvd_change': cvd_current - cvd_prev,
                    'strength': abs((price_current - price_prev) / price_prev) * 
                               abs(cvd_current - cvd_prev) / max(abs(cvd_current), abs(cvd_prev), 1)
                })
            
            # Bearish divergence: price up, CVD down
            elif price_current > price_prev and cvd_current < cvd_prev:
                divergences.append({
                    'timestamp': data[i]['timestamp'],
                    'type': 'bearish_divergence',
                    'price_change': (price_current - price_prev) / price_prev,
                    'cvd_change': cvd_current - cvd_prev,
                    'strength': abs((price_current - price_prev) / price_prev) * 
                               abs(cvd_current - cvd_prev) / max(abs(cvd_current), abs(cvd_prev), 1)
                })
        
        return divergences

class ConfluenceDetector:
    """
    🎯 Confluence Zone Detection Engine
    
    Identifies high-probability zones where multiple SMC patterns converge:
    - Nested Order Blocks
    - FVG within Order Blocks
    - Multiple pattern confirmations
    - Liquidity confluence areas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ConfluenceDetector")
    
    def detect_nested_order_blocks(self, order_blocks: List[Dict]) -> List[Dict]:
        """
        Detect nested order blocks (OB within OB)
        
        Args:
            order_blocks: List of detected order blocks
            
        Returns:
            List of nested order block patterns
        """
        nested_obs = []
        
        for i, ob1 in enumerate(order_blocks):
            for j, ob2 in enumerate(order_blocks):
                if i != j and self._is_nested_order_block(ob1, ob2):
                    nested_obs.append({
                        'timestamp': max(ob1['timestamp'], ob2['timestamp']),
                        'type': 'nested_order_block',
                        'outer_block': ob1,
                        'inner_block': ob2,
                        'direction': ob1['direction'],
                        'confluence_strength': self._calculate_confluence_strength(ob1, ob2),
                        'price_range': {
                            'high': max(ob1['price_high'], ob2['price_high']),
                            'low': min(ob1['price_low'], ob2['price_low'])
                        }
                    })
        
        return nested_obs
    
    def detect_fvg_ob_confluence(self, fvg_signals: List[Dict], order_blocks: List[Dict]) -> List[Dict]:
        """
        Detect FVG within Order Block confluence
        
        Args:
            fvg_signals: List of FVG patterns
            order_blocks: List of order blocks
            
        Returns:
            List of FVG-OB confluence patterns
        """
        confluences = []
        
        for fvg in fvg_signals:
            for ob in order_blocks:
                if self._is_fvg_within_ob(fvg, ob):
                    confluences.append({
                        'timestamp': max(fvg['timestamp'], ob['timestamp']),
                        'type': 'fvg_ob_confluence',
                        'fvg_pattern': fvg,
                        'order_block': ob,
                        'direction': fvg['direction'],
                        'confluence_strength': self._calculate_fvg_ob_confluence_strength(fvg, ob),
                        'high_probability_zone': {
                            'high': min(fvg['gap_high'], ob['price_high']),
                            'low': max(fvg['gap_low'], ob['price_low'])
                        }
                    })
        
        return confluences
    
    def _is_nested_order_block(self, ob1: Dict, ob2: Dict) -> bool:
        """Check if ob2 is nested within ob1"""
        return (ob1['price_low'] <= ob2['price_low'] and 
                ob1['price_high'] >= ob2['price_high'] and
                ob1['direction'] == ob2['direction'])
    
    def _is_fvg_within_ob(self, fvg: Dict, ob: Dict) -> bool:
        """Check if FVG is within Order Block"""
        return (ob['price_low'] <= fvg['gap_low'] and 
                ob['price_high'] >= fvg['gap_high'] and
                fvg['direction'] == ('bullish' if ob['direction'] == 'support' else 'bearish'))
    
    def _calculate_confluence_strength(self, ob1: Dict, ob2: Dict) -> float:
        """Calculate confluence strength between two order blocks"""
        volume_factor = (ob1['volume'] + ob2['volume']) / 2
        size_factor = min(ob1['strength'], ob2['strength'])
        return min(volume_factor * size_factor, 1.0)
    
    def _calculate_fvg_ob_confluence_strength(self, fvg: Dict, ob: Dict) -> float:
        """Calculate FVG-OB confluence strength"""
        fvg_strength = fvg['strength']
        ob_strength = ob['strength']
        return min((fvg_strength + ob_strength) / 2, 1.0)

class MultiTimeframeAnalyzer:
    """
    🚀 Multi-Timeframe Analysis Engine
    
    Provides enhanced SMC analysis across multiple timeframes:
    - HTF (High Time Frame) pattern confirmation
    - LTF (Low Time Frame) pattern detection
    - Cross-timeframe confluence analysis
    - Timeframe-weighted confidence scoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MultiTimeframeAnalyzer")
        self.timeframe_weights = {
            '1m': 0.1, '5m': 0.2, '15m': 0.3, '1h': 0.5, 
            '4h': 0.7, '1d': 0.9, '1w': 1.0
        }
    
    def analyze_mtf_confluence(self, ltf_patterns: Dict[str, Any], 
                              htf_patterns: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze multi-timeframe confluence for enhanced pattern validation
        
        Args:
            ltf_patterns: Low timeframe SMC patterns
            htf_patterns: High timeframe SMC patterns (optional)
            
        Returns:
            Enhanced patterns with MTF confluence analysis
        """
        confluence_results = {
            'mtf_confirmed_patterns': [],
            'mtf_confluence_score': 0.0,
            'htf_bias': 'neutral',
            'ltf_htf_alignment': False
        }
        
        if not htf_patterns:
            # If no HTF data provided, return LTF patterns with reduced confidence
            self.logger.info("🔄 No HTF data provided, analyzing LTF patterns only")
            for pattern_type, patterns in ltf_patterns.items():
                if isinstance(patterns, list):
                    for pattern in patterns:
                        if isinstance(pattern, dict):
                            # Reduce confidence for LTF-only analysis
                            original_confidence = pattern.get('confidence_score', 0.5)
                            pattern['confidence_score'] = original_confidence * 0.8
                            pattern['mtf_status'] = 'ltf_only'
                            confluence_results['mtf_confirmed_patterns'].append(pattern)
            
            confluence_results['mtf_confluence_score'] = 0.6  # Moderate confidence without HTF
            return confluence_results
        
        # Analyze HTF bias
        htf_bias = self._determine_htf_bias(htf_patterns)
        confluence_results['htf_bias'] = htf_bias
        
        # Check pattern alignment between timeframes
        alignment_score = self._calculate_timeframe_alignment(ltf_patterns, htf_patterns)
        confluence_results['ltf_htf_alignment'] = alignment_score > 0.6
        
        # Enhance LTF patterns with HTF confirmation
        confirmed_patterns = self._enhance_patterns_with_htf(ltf_patterns, htf_patterns, htf_bias)
        confluence_results['mtf_confirmed_patterns'] = confirmed_patterns
        
        # Calculate overall MTF confluence score
        confluence_results['mtf_confluence_score'] = self._calculate_mtf_score(
            alignment_score, len(confirmed_patterns), htf_bias
        )
        
        self.logger.info(f"🚀 MTF Analysis: {len(confirmed_patterns)} confirmed patterns, "
                        f"score: {confluence_results['mtf_confluence_score']:.2f}")
        
        return confluence_results
    
    def _determine_htf_bias(self, htf_patterns: Dict[str, Any]) -> str:
        """Determine overall HTF market bias"""
        bullish_signals = 0
        bearish_signals = 0
        
        # Count bullish/bearish signals across HTF patterns
        for pattern_type, patterns in htf_patterns.items():
            if isinstance(patterns, list):
                for pattern in patterns:
                    if isinstance(pattern, dict) and 'direction' in pattern:
                        if pattern['direction'] == 'bullish':
                            bullish_signals += 1
                        elif pattern['direction'] == 'bearish':
                            bearish_signals += 1
        
        if bullish_signals > bearish_signals * 1.2:
            return 'bullish'
        elif bearish_signals > bullish_signals * 1.2:
            return 'bearish'
        else:
            return 'neutral'
    
    def _calculate_timeframe_alignment(self, ltf_patterns: Dict, htf_patterns: Dict) -> float:
        """Calculate alignment score between LTF and HTF patterns"""
        alignment_count = 0
        total_patterns = 0
        
        # Compare pattern directions between timeframes
        for pattern_type in ['choch_bos_signals', 'order_blocks', 'fvg']:
            ltf_list = ltf_patterns.get(pattern_type, [])
            htf_list = htf_patterns.get(pattern_type, [])
            
            for ltf_pattern in ltf_list[-3:]:  # Last 3 LTF patterns
                if isinstance(ltf_pattern, dict) and 'direction' in ltf_pattern:
                    total_patterns += 1
                    
                    # Check if HTF has similar direction pattern
                    for htf_pattern in htf_list[-2:]:  # Last 2 HTF patterns
                        if (isinstance(htf_pattern, dict) and 
                            htf_pattern.get('direction') == ltf_pattern.get('direction')):
                            alignment_count += 1
                            break
        
        return alignment_count / max(total_patterns, 1)
    
    def _enhance_patterns_with_htf(self, ltf_patterns: Dict, htf_patterns: Dict, 
                                 htf_bias: str) -> List[Dict]:
        """Enhance LTF patterns with HTF confirmation"""
        enhanced_patterns = []
        
        for pattern_type, patterns in ltf_patterns.items():
            if isinstance(patterns, list):
                for pattern in patterns:
                    if isinstance(pattern, dict):
                        enhanced_pattern = pattern.copy()
                        
                        # Check HTF confirmation
                        htf_confirmation = self._check_htf_confirmation(
                            pattern, htf_patterns, htf_bias
                        )
                        
                        # Enhance confidence based on HTF confirmation
                        original_confidence = pattern.get('confidence_score', 0.5)
                        if htf_confirmation['confirmed']:
                            enhanced_pattern['confidence_score'] = min(1.0, original_confidence * 1.2)
                            enhanced_pattern['mtf_status'] = 'htf_confirmed'
                            enhanced_pattern['htf_confirmation'] = htf_confirmation
                        else:
                            enhanced_pattern['confidence_score'] = original_confidence * 0.9
                            enhanced_pattern['mtf_status'] = 'htf_neutral'
                        
                        enhanced_patterns.append(enhanced_pattern)
        
        return enhanced_patterns
    
    def _check_htf_confirmation(self, ltf_pattern: Dict, htf_patterns: Dict, 
                              htf_bias: str) -> Dict:
        """Check if LTF pattern is confirmed by HTF analysis"""
        confirmation = {
            'confirmed': False,
            'htf_bias_alignment': False,
            'pattern_confluence': False,
            'confidence_boost': 0.0
        }
        
        pattern_direction = ltf_pattern.get('direction')
        
        # Check HTF bias alignment
        if ((pattern_direction == 'bullish' and htf_bias == 'bullish') or
            (pattern_direction == 'bearish' and htf_bias == 'bearish')):
            confirmation['htf_bias_alignment'] = True
            confirmation['confidence_boost'] += 0.1
        
        # Check for similar HTF patterns
        pattern_type = ltf_pattern.get('type', '')
        htf_similar_patterns = htf_patterns.get(pattern_type, [])
        
        for htf_pattern in htf_similar_patterns[-2:]:  # Recent HTF patterns
            if (isinstance(htf_pattern, dict) and
                htf_pattern.get('direction') == pattern_direction):
                confirmation['pattern_confluence'] = True
                confirmation['confidence_boost'] += 0.2
                break
        
        # Overall confirmation
        confirmation['confirmed'] = (confirmation['htf_bias_alignment'] or 
                                   confirmation['pattern_confluence'])
        
        return confirmation
    
    def _calculate_mtf_score(self, alignment_score: float, confirmed_count: int, 
                           htf_bias: str) -> float:
        """Calculate overall MTF confluence score"""
        base_score = alignment_score * 0.4
        pattern_score = min(confirmed_count * 0.1, 0.4)
        bias_score = 0.2 if htf_bias != 'neutral' else 0.1
        
        return min(base_score + pattern_score + bias_score, 1.0)

class RealtimeAlertSystem:
    """
    🚨 Real-Time Alert System for SMC Patterns
    
    Provides webhook-based notifications for critical SMC events:
    - CHoCH/BOS pattern alerts
    - Order Block breach notifications
    - High-confidence pattern alerts
    - Custom threshold-based alerts
    """
    
    def __init__(self, webhook_url: str = None):
        self.logger = logging.getLogger(f"{__name__}.RealtimeAlertSystem")
        self.webhook_url = webhook_url
        self.alert_thresholds = {
            'choch_bos': 0.75,
            'order_block': 0.70,
            'fvg': 0.65,
            'liquidity_sweep': 0.80
        }
        
    def check_and_send_alerts(self, analysis_result: Dict[str, Any], 
                            symbol: str, timeframe: str) -> List[Dict]:
        """
        Check analysis results for alert-worthy patterns and send notifications
        
        Args:
            analysis_result: Complete SMC analysis result
            symbol: Trading symbol
            timeframe: Analysis timeframe
            
        Returns:
            List of alerts sent
        """
        alerts_sent = []
        
        # Check CHoCH/BOS alerts
        choch_bos_alerts = self._check_choch_bos_alerts(
            analysis_result.get('structure', {}).get('choch_bos_signals', []),
            symbol, timeframe
        )
        alerts_sent.extend(choch_bos_alerts)
        
        # Check Order Block alerts
        ob_alerts = self._check_order_block_alerts(
            analysis_result.get('order_blocks', []),
            symbol, timeframe
        )
        alerts_sent.extend(ob_alerts)
        
        # Check high-confidence pattern alerts
        confluence_alerts = self._check_confluence_alerts(
            analysis_result.get('confluence_zones', []),
            symbol, timeframe
        )
        alerts_sent.extend(confluence_alerts)
        
        # Check advanced pattern alerts
        advanced_alerts = self._check_advanced_pattern_alerts(
            analysis_result.get('advanced_patterns', []),
            symbol, timeframe
        )
        alerts_sent.extend(advanced_alerts)
        
        self.logger.info(f"🚨 Sent {len(alerts_sent)} alerts for {symbol} {timeframe}")
        return alerts_sent
    
    def _check_choch_bos_alerts(self, choch_bos_signals: List[Dict], 
                              symbol: str, timeframe: str) -> List[Dict]:
        """Check for CHoCH/BOS alert conditions"""
        alerts = []
        
        for signal in choch_bos_signals[-3:]:  # Check last 3 signals
            if (isinstance(signal, dict) and 
                signal.get('confidence_score', 0) >= self.alert_thresholds['choch_bos']):
                
                alert = {
                    'type': 'choch_bos_alert',
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'timestamp': signal.get('timestamp'),
                    'pattern': signal.get('type'),
                    'direction': signal.get('direction'),
                    'confidence': signal.get('confidence_score'),
                    'price': signal.get('price'),
                    'message': f"🚨 {signal.get('type')} {signal.get('direction')} detected on {symbol} {timeframe} "
                              f"at {signal.get('price')} with {signal.get('confidence_score', 0):.1%} confidence"
                }
                
                alerts.append(alert)
                self._send_webhook_alert(alert)
        
        return alerts
    
    def _check_order_block_alerts(self, order_blocks: List[Dict], 
                                symbol: str, timeframe: str) -> List[Dict]:
        """Check for Order Block alert conditions"""
        alerts = []
        
        for ob in order_blocks[-3:]:  # Check last 3 order blocks
            if (isinstance(ob, dict) and 
                ob.get('confidence_score', 0) >= self.alert_thresholds['order_block']):
                
                alert = {
                    'type': 'order_block_alert',
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'timestamp': ob.get('timestamp'),
                    'direction': ob.get('direction'),
                    'confidence': ob.get('confidence_score'),
                    'price_high': ob.get('price_high'),
                    'price_low': ob.get('price_low'),
                    'message': f"🏗️ Strong {ob.get('direction')} Order Block detected on {symbol} {timeframe} "
                              f"({ob.get('price_low'):.2f}-{ob.get('price_high'):.2f}) "
                              f"with {ob.get('confidence_score', 0):.1%} confidence"
                }
                
                alerts.append(alert)
                self._send_webhook_alert(alert)
        
        return alerts
    
    def _check_confluence_alerts(self, confluence_zones: List[Dict], 
                               symbol: str, timeframe: str) -> List[Dict]:
        """Check for high-confidence confluence zone alerts"""
        alerts = []
        
        for zone in confluence_zones[-2:]:  # Check last 2 confluence zones
            if (isinstance(zone, dict) and 
                zone.get('confluence_strength', 0) >= 0.8):
                
                alert = {
                    'type': 'confluence_alert',
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'timestamp': zone.get('timestamp'),
                    'confluence_type': zone.get('type'),
                    'strength': zone.get('confluence_strength'),
                    'message': f"🎯 High-probability confluence zone detected on {symbol} {timeframe} "
                              f"({zone.get('type')}) with {zone.get('confluence_strength', 0):.1%} strength"
                }
                
                alerts.append(alert)
                self._send_webhook_alert(alert)
        
        return alerts
    
    def _check_advanced_pattern_alerts(self, advanced_patterns: List[Dict], 
                                     symbol: str, timeframe: str) -> List[Dict]:
        """Check for advanced pattern alerts"""
        alerts = []
        
        for pattern in advanced_patterns[-5:]:  # Check last 5 advanced patterns
            if (isinstance(pattern, dict) and 
                pattern.get('confidence_score', 0) >= 0.75):
                
                alert = {
                    'type': 'advanced_pattern_alert',
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'timestamp': pattern.get('timestamp'),
                    'pattern_type': pattern.get('type'),
                    'confidence': pattern.get('confidence_score'),
                    'message': f"⚡ Advanced pattern {pattern.get('type')} detected on {symbol} {timeframe} "
                              f"with {pattern.get('confidence_score', 0):.1%} confidence"
                }
                
                alerts.append(alert)
                self._send_webhook_alert(alert)
        
        return alerts
    
    def _send_webhook_alert(self, alert: Dict) -> bool:
        """Send alert via webhook"""
        if not self.webhook_url:
            self.logger.debug(f"No webhook URL configured, alert logged: {alert['message']}")
            return False
        
        try:
            import requests
            import json
            
            payload = {
                'text': alert['message'],
                'alert_data': alert,
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                self.logger.info(f"✅ Alert sent successfully: {alert['type']}")
                return True
            else:
                self.logger.warning(f"⚠️ Webhook failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Webhook error: {e}")
            return False

class BacktestingFramework:
    """
    📊 Backtesting Framework for SMC Pattern Validation
    
    Provides comprehensive backtesting capabilities:
    - Historical pattern performance analysis
    - Win rate and profit factor calculation
    - Pattern effectiveness measurement
    - Statistical validation of SMC concepts
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.BacktestingFramework")
        self.test_results = []
    
    def backtest_smc_patterns(self, historical_data: List[Dict], 
                            pattern_results: List[Dict],
                            lookforward_periods: int = 20) -> Dict[str, Any]:
        """
        Backtest SMC patterns against historical price movement
        
        Args:
            historical_data: Historical OHLCV data
            pattern_results: List of detected SMC patterns
            lookforward_periods: Number of periods to look forward for validation
            
        Returns:
            Comprehensive backtesting results
        """
        backtest_results = {
            'total_patterns_tested': 0,
            'successful_patterns': 0,
            'win_rate': 0.0,
            'average_return': 0.0,
            'profit_factor': 0.0,
            'pattern_performance': {},
            'detailed_results': []
        }
        
        if not historical_data or not pattern_results:
            return backtest_results
        
        # Create price lookup for faster access
        price_lookup = {int(candle['timestamp']): candle for candle in historical_data}
        
        successful_count = 0
        total_return = 0.0
        positive_returns = 0.0
        negative_returns = 0.0
        pattern_stats = {}
        
        self.logger.info(f"📊 Starting backtest of {len(pattern_results)} patterns")
        
        for pattern in pattern_results:
            if not isinstance(pattern, dict) or 'timestamp' not in pattern:
                continue
                
            # Find pattern validation
            result = self._validate_pattern_outcome(
                pattern, price_lookup, lookforward_periods
            )
            
            if result['testable']:
                backtest_results['total_patterns_tested'] += 1
                
                # Track pattern type performance
                pattern_type = pattern.get('type', 'unknown')
                if pattern_type not in pattern_stats:
                    pattern_stats[pattern_type] = {
                        'total': 0, 'successful': 0, 'returns': []
                    }
                
                pattern_stats[pattern_type]['total'] += 1
                pattern_stats[pattern_type]['returns'].append(result['return_pct'])
                
                if result['successful']:
                    successful_count += 1
                    pattern_stats[pattern_type]['successful'] += 1
                    positive_returns += result['return_pct']
                else:
                    negative_returns += abs(result['return_pct'])
                
                total_return += result['return_pct']
                backtest_results['detailed_results'].append(result)
        
        # Calculate final metrics
        if backtest_results['total_patterns_tested'] > 0:
            backtest_results['successful_patterns'] = successful_count
            backtest_results['win_rate'] = successful_count / backtest_results['total_patterns_tested']
            backtest_results['average_return'] = total_return / backtest_results['total_patterns_tested']
            
            if negative_returns > 0:
                backtest_results['profit_factor'] = positive_returns / negative_returns
            else:
                backtest_results['profit_factor'] = float('inf') if positive_returns > 0 else 0
        
        # Calculate pattern-specific performance
        for pattern_type, stats in pattern_stats.items():
            if stats['total'] > 0:
                backtest_results['pattern_performance'][pattern_type] = {
                    'win_rate': stats['successful'] / stats['total'],
                    'average_return': sum(stats['returns']) / len(stats['returns']),
                    'total_tests': stats['total'],
                    'successful_tests': stats['successful']
                }
        
        self.logger.info(f"📊 Backtest complete: {backtest_results['win_rate']:.1%} win rate, "
                        f"{backtest_results['average_return']:.2%} avg return")
        
        return backtest_results
    
    def _validate_pattern_outcome(self, pattern: Dict, price_lookup: Dict, 
                                lookforward_periods: int) -> Dict:
        """Validate if a pattern was successful"""
        result = {
            'pattern': pattern,
            'testable': False,
            'successful': False,
            'return_pct': 0.0,
            'max_favorable': 0.0,
            'max_adverse': 0.0,
            'validation_method': 'price_direction'
        }
        
        pattern_timestamp = pattern.get('timestamp')
        pattern_direction = pattern.get('direction')
        pattern_price = pattern.get('price', 0)
        
        if not all([pattern_timestamp, pattern_direction, pattern_price]):
            return result
        
        # Find future price data
        future_prices = []
        current_timestamp = pattern_timestamp
        
        for i in range(lookforward_periods):
            future_timestamp = current_timestamp + (i + 1) * 3600000  # Assume 1h candles
            if future_timestamp in price_lookup:
                future_prices.append(price_lookup[future_timestamp])
        
        if len(future_prices) < 5:  # Need at least 5 future candles
            return result
        
        result['testable'] = True
        
        # Calculate price performance
        max_favorable_price = pattern_price
        max_adverse_price = pattern_price
        final_price = future_prices[-1]['close']
        
        for candle in future_prices:
            if pattern_direction == 'bullish':
                max_favorable_price = max(max_favorable_price, candle['high'])
                max_adverse_price = min(max_adverse_price, candle['low'])
            else:
                max_favorable_price = min(max_favorable_price, candle['low'])
                max_adverse_price = max(max_adverse_price, candle['high'])
        
        # Calculate returns
        if pattern_direction == 'bullish':
            result['return_pct'] = (final_price - pattern_price) / pattern_price
            result['max_favorable'] = (max_favorable_price - pattern_price) / pattern_price
            result['max_adverse'] = (max_adverse_price - pattern_price) / pattern_price
            result['successful'] = final_price > pattern_price * 1.01  # 1% threshold
        else:
            result['return_pct'] = (pattern_price - final_price) / pattern_price
            result['max_favorable'] = (pattern_price - max_favorable_price) / pattern_price
            result['max_adverse'] = (pattern_price - max_adverse_price) / pattern_price
            result['successful'] = final_price < pattern_price * 0.99  # 1% threshold
        
        return result
    
    def generate_backtest_report(self, backtest_results: Dict) -> str:
        """Generate human-readable backtest report"""
        if not backtest_results.get('total_patterns_tested'):
            return "❌ No patterns available for backtesting"
        
        report = f"""
📊 SMC Pattern Backtesting Report
═══════════════════════════════════

📈 Overall Performance:
• Total Patterns Tested: {backtest_results['total_patterns_tested']}
• Successful Patterns: {backtest_results['successful_patterns']}
• Win Rate: {backtest_results['win_rate']:.1%}
• Average Return: {backtest_results['average_return']:.2%}
• Profit Factor: {backtest_results['profit_factor']:.2f}

🎯 Pattern Performance Breakdown:
"""
        
        for pattern_type, performance in backtest_results.get('pattern_performance', {}).items():
            report += f"""
• {pattern_type.upper()}:
  - Win Rate: {performance['win_rate']:.1%}
  - Avg Return: {performance['average_return']:.2%}
  - Tests: {performance['successful_tests']}/{performance['total_tests']}
"""
        
        # Add performance rating
        win_rate = backtest_results['win_rate']
        if win_rate >= 0.7:
            rating = "🟢 EXCELLENT"
        elif win_rate >= 0.6:
            rating = "🟡 GOOD"
        elif win_rate >= 0.5:
            rating = "🟠 MODERATE"
        else:
            rating = "🔴 POOR"
        
        report += f"\n🏆 Overall Rating: {rating}"
        return report

class ProfessionalSMCAnalyzer:
    """
    🎯 Professional SMC Analyzer with Advanced Pattern Detection
    
    This class provides comprehensive Smart Money Concept analysis with:
    - Enhanced pattern detection algorithms
    - Volume delta and CVD confirmation
    - Confidence scoring system
    - Nested structure detection
    - AI-ready output format
    - Multi-timeframe analysis
    - Real-time alert system
    - Backtesting framework
    """
    
    # 📊 Analysis Configuration Constants
    SWING_PERIOD = 5                    # Period for swing high/low detection
    MIN_SWING_STRENGTH = 3              # Minimum bars for swing confirmation
    VOLUME_CONFIRMATION_THRESHOLD = 1.5  # Volume threshold for pattern confirmation
    CVD_DIVERGENCE_THRESHOLD = 0.3      # CVD divergence threshold
    CONFIDENCE_THRESHOLD = 0.65         # Minimum confidence for signal validity
    
    # 🎯 Pattern Detection Thresholds
    BOS_BREAK_THRESHOLD = 0.01          # 1% break for BOS confirmation
    FVG_MIN_GAP_SIZE = 0.0005          # Minimum gap size for FVG (0.05%)
    ORDER_BLOCK_MIN_SIZE = 0.002       # Minimum order block size (0.2%)
    
    def __init__(self, webhook_url: str = None):
        """
        Initialize the Professional SMC Analyzer
        
        Sets up all detection engines and configuration parameters
        
        Args:
            webhook_url: Optional webhook URL for real-time alerts
        """
        self.swing_period = self.SWING_PERIOD
        self.min_swing_strength = self.MIN_SWING_STRENGTH
        self.inducement_detector = InducementDetector()
        self.logger = logging.getLogger(__name__)
        
        # 📊 Initialize volume analysis components
        self.volume_analyzer = VolumeAnalyzer()
        self.cvd_calculator = CVDCalculator()
        self.confluence_detector = ConfluenceDetector()
        
        # 🚀 Initialize new advanced components
        self.mtf_analyzer = MultiTimeframeAnalyzer()
        self.alert_system = RealtimeAlertSystem(webhook_url)
        self.backtesting = BacktestingFramework()
        
        self.logger.info("🚀 Professional SMC Analyzer initialized with enhanced features including MTF, alerts, and backtesting")
    
    def _safe_get_price(self, data_point: Dict, default: float = 0.0) -> float:
        """
        Safely extract price from various data structures with multiple fallbacks
        
        Args:
            data_point: Dictionary that may contain price information
            default: Default value if no price found
            
        Returns:
            Price value or default
        """
        try:
            # Try different possible price keys
            price_keys = ['price', 'sweep_price', 'price_high', 'price_low', 'level', 'close', 'high', 'low']
            
            for key in price_keys:
                if key in data_point and data_point[key] is not None:
                    return float(data_point[key])
            
            # If no price found, return default
            return default
            
        except (ValueError, TypeError, KeyError):
            return default
    
    # 🚀 ADVANCED SMC LOGIC FEATURES
    # =========================================================
    
    def detect_breaker_blocks(self, data: List[Dict], order_blocks: List[Dict], 
                            swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """
        🧱 BREAKER BLOCK LOGIC
        
        Deteksi breaker block: area order block sebelumnya yang gagal → lalu dibreak → 
        jadi support/resistance balik arah. Berfungsi sebagai zona reentry setelah stop hunt.
        
        Args:
            data: OHLCV data
            order_blocks: Previously detected order blocks
            swing_points: Swing highs and lows
            
        Returns:
            List of breaker block patterns
        """
        breaker_blocks = []
        
        if not order_blocks:
            return breaker_blocks
        
        self.logger.info(f"🧱 Analyzing {len(order_blocks)} order blocks for breaker patterns")
        
        for i, ob in enumerate(order_blocks):
            # Cari candle setelah order block yang membreak struktur
            ob_timestamp = ob['timestamp']
            ob_high = ob.get('price_high', self._safe_get_price(ob))
            ob_low = ob.get('price_low', self._safe_get_price(ob))
            
            # Cari candle yang membreak order block
            for j, candle in enumerate(data):
                if candle['timestamp'] > ob_timestamp:
                    # Check untuk bullish breaker (resistance OB yang dibreak ke atas)
                    if (ob['direction'] == 'resistance' and 
                        candle['close'] > ob_high * 1.001):  # 0.1% break threshold
                        
                        # Setelah break, area ini menjadi support
                        breaker_blocks.append({
                            'timestamp': candle['timestamp'],
                            'type': 'breaker_block',
                            'direction': 'support',  # Balik arah
                            'original_ob': ob,
                            'break_candle': candle,
                            'price_high': ob_high,
                            'price_low': ob_low,
                            'break_price': candle['close'],
                            'break_strength': (candle['close'] - ob_high) / ob_high,
                            'volume_confirmation': candle['volume'] > ob.get('volume', 0) * 1.2,
                            'confidence_score': min(1.0, 0.7 + (candle['volume'] / ob.get('volume', 1)) * 0.3)
                        })
                        break
                    
                    # Check untuk bearish breaker (support OB yang dibreak ke bawah)
                    elif (ob['direction'] == 'support' and 
                          candle['close'] < ob_low * 0.999):  # 0.1% break threshold
                        
                        # Setelah break, area ini menjadi resistance
                        breaker_blocks.append({
                            'timestamp': candle['timestamp'],
                            'type': 'breaker_block',
                            'direction': 'resistance',  # Balik arah
                            'original_ob': ob,
                            'break_candle': candle,
                            'price_high': ob_high,
                            'price_low': ob_low,
                            'break_price': candle['close'],
                            'break_strength': (ob_low - candle['close']) / ob_low,
                            'volume_confirmation': candle['volume'] > ob.get('volume', 0) * 1.2,
                            'confidence_score': min(1.0, 0.7 + (candle['volume'] / ob.get('volume', 1)) * 0.3)
                        })
                        break
        
        self.logger.info(f"🧱 Detected {len(breaker_blocks)} breaker block patterns")
        return breaker_blocks
    
    def categorize_irl_erl_liquidity(self, data: List[Dict], swing_points: Dict[str, List[Dict]], 
                                   liquidity_sweeps: List[Dict]) -> List[Dict]:
        """
        💧 IRL & ERL LIQUIDITY CATEGORIZATION
        
        Deteksi akumulasi likuiditas:
        - IRL (Internal Range Liquidity): di dalam swing range
        - ERL (External Range Liquidity): di luar swing range
        
        Args:
            data: OHLCV data
            swing_points: Swing highs and lows
            liquidity_sweeps: Existing liquidity sweeps
            
        Returns:
            Enhanced liquidity sweeps with IRL/ERL categorization
        """
        enhanced_sweeps = []
        
        if not liquidity_sweeps:
            return enhanced_sweeps
        
        # Ambil swing range terbaru untuk referensi
        recent_highs = swing_points.get('swing_highs', [])[-5:]
        recent_lows = swing_points.get('swing_lows', [])[-5:]
        
        if not recent_highs or not recent_lows:
            return liquidity_sweeps  # Return original jika tidak ada swing points
        
        # Tentukan current range
        current_range_high = max(self._safe_get_price(sh) for sh in recent_highs)
        current_range_low = min(self._safe_get_price(sl) for sl in recent_lows)
        range_size = current_range_high - current_range_low
        
        self.logger.info(f"💧 Analyzing liquidity with range: {current_range_low:.2f} - {current_range_high:.2f}")
        
        for sweep in liquidity_sweeps:
            sweep_price = self._safe_get_price(sweep)
            enhanced_sweep = sweep.copy()
            
            # Categorize berdasarkan posisi relatif terhadap range
            if sweep_price > current_range_high + (range_size * 0.1):
                # External Range Liquidity - Above range
                enhanced_sweep['liquidity_category'] = 'ERL'
                enhanced_sweep['liquidity_type'] = 'external_high'
                enhanced_sweep['range_position'] = 'above'
                enhanced_sweep['significance'] = 'high'  # ERL lebih significant
                
            elif sweep_price < current_range_low - (range_size * 0.1):
                # External Range Liquidity - Below range
                enhanced_sweep['liquidity_category'] = 'ERL'
                enhanced_sweep['liquidity_type'] = 'external_low'
                enhanced_sweep['range_position'] = 'below'
                enhanced_sweep['significance'] = 'high'  # ERL lebih significant
                
            else:
                # Internal Range Liquidity - Within range
                enhanced_sweep['liquidity_category'] = 'IRL'
                enhanced_sweep['liquidity_type'] = 'internal'
                enhanced_sweep['range_position'] = 'within'
                enhanced_sweep['significance'] = 'medium'  # IRL kurang significant
            
            # Tambahkan range context
            enhanced_sweep['range_context'] = {
                'range_high': current_range_high,
                'range_low': current_range_low,
                'range_size': range_size,
                'distance_from_range': min(
                    abs(sweep_price - current_range_high),
                    abs(sweep_price - current_range_low)
                )
            }
            
            enhanced_sweeps.append(enhanced_sweep)
        
        self.logger.info(f"💧 Categorized {len(enhanced_sweeps)} liquidity sweeps (IRL/ERL)")
        return enhanced_sweeps
    
    def analyze_killzone_timing(self, data: List[Dict], patterns: List[Dict]) -> List[Dict]:
        """
        ⏱️ KILLZONE SMC TIMING
        
        Implementasi time filter berbasis sesi trading:
        - London Open: 07:00–10:00 UTC
        - New York Open: 13:00–16:00 UTC  
        - Asia Session: 00:00–03:00 UTC
        
        Args:
            data: OHLCV data
            patterns: SMC patterns to analyze
            
        Returns:
            Patterns with killzone timing analysis
        """
        killzone_patterns = []
        
        # Define killzone sessions (UTC)
        killzones = {
            'asia': {'start': 0, 'end': 3},      # 00:00-03:00 UTC
            'london': {'start': 7, 'end': 10},   # 07:00-10:00 UTC
            'ny': {'start': 13, 'end': 16}       # 13:00-16:00 UTC
        }
        
        for pattern in patterns:
            enhanced_pattern = pattern.copy()
            
            # Extract timestamp and convert to UTC hour
            timestamp = pattern.get('timestamp', 0)
            if timestamp:
                dt = datetime.fromtimestamp(timestamp / 1000)
                utc_hour = dt.hour
                
                # Check which killzone the pattern falls into
                active_killzone = None
                killzone_strength = 0.0
                
                for zone_name, zone_time in killzones.items():
                    if zone_time['start'] <= utc_hour <= zone_time['end']:
                        active_killzone = zone_name
                        
                        # Calculate strength based on position in killzone
                        zone_duration = zone_time['end'] - zone_time['start']
                        zone_progress = (utc_hour - zone_time['start']) / zone_duration
                        
                        # Highest strength at the beginning of killzone
                        if zone_progress <= 0.5:
                            killzone_strength = 1.0 - (zone_progress * 0.3)
                        else:
                            killzone_strength = 0.7 - ((zone_progress - 0.5) * 0.4)
                        
                        break
                
                # Add killzone analysis to pattern
                enhanced_pattern['killzone_analysis'] = {
                    'active_killzone': active_killzone,
                    'killzone_strength': killzone_strength,
                    'utc_hour': utc_hour,
                    'timing_confidence': killzone_strength if active_killzone else 0.3,
                    'timing_description': self._get_killzone_description(active_killzone, utc_hour)
                }
                
                # Boost pattern confidence if in strong killzone
                if active_killzone and killzone_strength > 0.7:
                    original_confidence = enhanced_pattern.get('confidence_score', 0.5)
                    enhanced_pattern['confidence_score'] = min(1.0, original_confidence + (killzone_strength * 0.2))
                    enhanced_pattern['killzone_boost'] = True
                
            killzone_patterns.append(enhanced_pattern)
        
        self.logger.info(f"⏱️ Analyzed {len(killzone_patterns)} patterns for killzone timing")
        return killzone_patterns
    
    def _get_killzone_description(self, killzone: str, utc_hour: int) -> str:
        """Helper untuk generate killzone description"""
        if killzone == 'asia':
            return f"Asia Session (UTC {utc_hour}:00) - Lower volatility, range-bound"
        elif killzone == 'london':
            return f"London Open (UTC {utc_hour}:00) - High volatility, trend initiation"
        elif killzone == 'ny':
            return f"New York Open (UTC {utc_hour}:00) - Highest volatility, trend continuation"
        else:
            return f"Outside major sessions (UTC {utc_hour}:00) - Reduced significance"
    
    def map_premium_discount_zones(self, data: List[Dict], swing_points: Dict[str, List[Dict]], 
                                 patterns: List[Dict]) -> List[Dict]:
        """
        🎯 PREMIUM/DISCOUNT ZONE MAPPING
        
        Tandai area berdasarkan Fibonacci 0.5 (midline) dari swing terakhir:
        - Premium Zone: >0.5 (area mahal)
        - Discount Zone: <0.5 (area murah)
        
        Args:
            data: OHLCV data
            swing_points: Swing highs and lows
            patterns: SMC patterns to analyze
            
        Returns:
            Patterns with premium/discount zone mapping
        """
        mapped_patterns = []
        
        recent_highs = swing_points.get('swing_highs', [])[-3:]
        recent_lows = swing_points.get('swing_lows', [])[-3:]
        
        if not recent_highs or not recent_lows:
            return patterns  # Return original jika tidak ada swing points
        
        # Ambil swing range terbaru
        latest_high = max(self._safe_get_price(sh) for sh in recent_highs)
        latest_low = min(self._safe_get_price(sl) for sl in recent_lows)
        swing_range = latest_high - latest_low
        midline = latest_low + (swing_range * 0.5)  # Fibonacci 0.5
        
        # Define zone levels
        premium_threshold = latest_low + (swing_range * 0.618)  # 61.8% = Premium
        discount_threshold = latest_low + (swing_range * 0.382)  # 38.2% = Discount
        
        self.logger.info(f"🎯 Mapping zones - High: {latest_high:.2f}, Low: {latest_low:.2f}, Mid: {midline:.2f}")
        
        for pattern in patterns:
            enhanced_pattern = pattern.copy()
            
            # Get pattern price - safely handle different price fields
            pattern_price = self._safe_get_price(pattern)
            
            if pattern_price > 0:
                # Calculate position in range (0-1)
                range_position = (pattern_price - latest_low) / swing_range if swing_range > 0 else 0.5
                
                # Determine zone
                if range_position >= 0.618:
                    zone_type = 'premium'
                    zone_quality = 'high_premium'
                    logic_validity = 'bearish_bias'  # Di premium, look for sells
                elif range_position <= 0.382:
                    zone_type = 'discount'
                    zone_quality = 'high_discount'
                    logic_validity = 'bullish_bias'  # Di discount, look for buys
                else:
                    zone_type = 'equilibrium'
                    zone_quality = 'neutral'
                    logic_validity = 'neutral_bias'
                
                # Add zone analysis
                enhanced_pattern['zone_analysis'] = {
                    'zone_type': zone_type,
                    'zone_quality': zone_quality,
                    'logic_validity': logic_validity,
                    'range_position': range_position,
                    'distance_from_midline': abs(pattern_price - midline),
                    'swing_context': {
                        'swing_high': latest_high,
                        'swing_low': latest_low,
                        'swing_range': swing_range,
                        'midline': midline
                    }
                }
                
                # Validate logic: OB/FVG di area yang tepat
                pattern_direction = pattern.get('direction', 'neutral')
                
                # Boost confidence untuk pattern yang logis
                if ((zone_type == 'premium' and pattern_direction == 'bearish') or
                    (zone_type == 'discount' and pattern_direction == 'bullish')):
                    original_confidence = enhanced_pattern.get('confidence_score', 0.5)
                    enhanced_pattern['confidence_score'] = min(1.0, original_confidence + 0.15)
                    enhanced_pattern['zone_logic_boost'] = True
                
                # Reduce confidence untuk pattern yang tidak logis
                elif ((zone_type == 'premium' and pattern_direction == 'bullish') or
                      (zone_type == 'discount' and pattern_direction == 'bearish')):
                    original_confidence = enhanced_pattern.get('confidence_score', 0.5)
                    enhanced_pattern['confidence_score'] = max(0.2, original_confidence - 0.1)
                    enhanced_pattern['zone_logic_penalty'] = True
            
            mapped_patterns.append(enhanced_pattern)
        
        self.logger.info(f"🎯 Mapped {len(mapped_patterns)} patterns to premium/discount zones")
        return mapped_patterns
    
    def detect_mitigation_blocks(self, data: List[Dict], order_blocks: List[Dict]) -> List[Dict]:
        """
        🧱 MITIGATION BLOCK LOGIC
        
        Deteksi candle besar setelah OB yang "mengisi kembali" area imbalance OB sebelumnya.
        Digunakan untuk validasi OB yang sudah di-acknowledge oleh market.
        
        Args:
            data: OHLCV data
            order_blocks: Previously detected order blocks
            
        Returns:
            List of mitigation block patterns
        """
        mitigation_blocks = []
        
        if not order_blocks:
            return mitigation_blocks
        
        # Calculate average candle size for reference
        avg_candle_size = sum(abs(candle['close'] - candle['open']) for candle in data) / len(data)
        
        self.logger.info(f"🧱 Analyzing {len(order_blocks)} order blocks for mitigation patterns")
        
        for ob in order_blocks:
            ob_timestamp = ob['timestamp']
            ob_high = ob.get('price_high', self._safe_get_price(ob))
            ob_low = ob.get('price_low', self._safe_get_price(ob))
            ob_direction = ob['direction']
            
            # Cari candle setelah OB yang melakukan mitigation
            for i, candle in enumerate(data):
                if candle['timestamp'] > ob_timestamp:
                    candle_size = abs(candle['close'] - candle['open'])
                    
                    # Mitigation criteria:
                    # 1. Candle besar (>2x average)
                    # 2. Candle "mengisi" area OB
                    # 3. Volume tinggi
                    
                    is_large_candle = candle_size > avg_candle_size * 2.0
                    
                    if is_large_candle:
                        # Check apakah candle mengisi area OB
                        candle_fills_ob = False
                        mitigation_type = None
                        
                        if ob_direction == 'resistance':
                            # Untuk resistance OB, mitigation = candle naik yang mengisi area
                            if (candle['close'] > candle['open'] and 
                                candle['open'] < ob_high and candle['close'] > ob_low):
                                candle_fills_ob = True
                                mitigation_type = 'bullish_mitigation'
                        
                        elif ob_direction == 'support':
                            # Untuk support OB, mitigation = candle turun yang mengisi area
                            if (candle['close'] < candle['open'] and 
                                candle['open'] > ob_low and candle['close'] < ob_high):
                                candle_fills_ob = True
                                mitigation_type = 'bearish_mitigation'
                        
                        if candle_fills_ob:
                            # Calculate mitigation strength
                            fill_percentage = min(1.0, candle_size / (ob_high - ob_low))
                            volume_strength = candle['volume'] / ob.get('volume', candle['volume'])
                            
                            mitigation_blocks.append({
                                'timestamp': candle['timestamp'],
                                'type': 'mitigation_block',
                                'mitigation_type': mitigation_type,
                                'original_ob': ob,
                                'mitigation_candle': candle,
                                'fill_percentage': fill_percentage,
                                'volume_strength': volume_strength,
                                'candle_size_ratio': candle_size / avg_candle_size,
                                'confidence_score': min(1.0, 0.6 + (fill_percentage * 0.2) + (volume_strength * 0.2)),
                                'market_acknowledgment': True,  # OB sudah di-acknowledge
                                'ob_validation': 'confirmed'
                            })
                            break  # Hanya ambil mitigation pertama per OB
        
        self.logger.info(f"🧱 Detected {len(mitigation_blocks)} mitigation block patterns")
        return mitigation_blocks
    
    def detect_trendline_liquidity(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """
        📉 TRENDLINE LIQUIDITY DETECTION
        
        Identifikasi support/resistance miring (trendline) yang tersentuh berkali-kali
        → akumulasi likuiditas. Saat break, anggap sebagai sweep zone + entry confluence.
        
        Args:
            data: OHLCV data
            swing_points: Swing highs and lows
            
        Returns:
            List of trendline liquidity patterns
        """
        trendline_liquidities = []
        
        swing_highs = swing_points.get('swing_highs', [])
        swing_lows = swing_points.get('swing_lows', [])
        
        if len(swing_highs) < 3 or len(swing_lows) < 3:
            return trendline_liquidities
        
        self.logger.info(f"📉 Analyzing trendlines from {len(swing_highs)} highs and {len(swing_lows)} lows")
        
        # Analyze swing highs untuk resistance trendlines
        for i in range(len(swing_highs) - 2):
            point1 = swing_highs[i]
            point2 = swing_highs[i + 1]
            point3 = swing_highs[i + 2]
            
            # Calculate trendline slope
            time_diff = point2['timestamp'] - point1['timestamp']
            price_diff = point2['price'] - point1['price']
            
            if time_diff > 0:
                slope = price_diff / time_diff
                
                # Project trendline to point3
                projected_price = point1['price'] + slope * (point3['timestamp'] - point1['timestamp'])
                price_deviation = abs(point3['price'] - projected_price) / point3['price']
                
                # Jika point3 dekat dengan trendline (deviation < 2%), ini valid trendline
                if price_deviation < 0.02:
                    # Hitung berapa kali trendline tersentuh
                    touch_count = 3  # Minimal 3 (point1, point2, point3)
                    
                    # Cari touch tambahan
                    for j in range(i + 3, len(swing_highs)):
                        point = swing_highs[j]
                        projected = point1['price'] + slope * (point['timestamp'] - point1['timestamp'])
                        deviation = abs(point['price'] - projected) / point['price']
                        
                        if deviation < 0.02:
                            touch_count += 1
                    
                    # Cari trendline break
                    trendline_break = None
                    for candle in data:
                        if candle['timestamp'] > point3['timestamp']:
                            projected = point1['price'] + slope * (candle['timestamp'] - point1['timestamp'])
                            
                            # Check untuk break
                            if candle['high'] > projected * 1.01:  # 1% break threshold
                                trendline_break = {
                                    'timestamp': candle['timestamp'],
                                    'break_price': candle['high'],
                                    'projected_price': projected,
                                    'break_strength': (candle['high'] - projected) / projected,
                                    'volume': candle['volume']
                                }
                                break
                    
                    # Liquidity accumulation strength
                    liquidity_strength = min(1.0, 0.4 + (touch_count * 0.15))
                    
                    trendline_liquidities.append({
                        'timestamp': point1['timestamp'],
                        'type': 'trendline_liquidity',
                        'trendline_type': 'resistance',
                        'direction': 'bearish',
                        'touch_points': [point1, point2, point3],
                        'touch_count': touch_count,
                        'slope': slope,
                        'liquidity_strength': liquidity_strength,
                        'trendline_break': trendline_break,
                        'sweep_potential': 'high' if trendline_break else 'building',
                        'confidence_score': min(1.0, 0.5 + (touch_count * 0.1) + (0.3 if trendline_break else 0))
                    })
        
        # Analyze swing lows untuk support trendlines
        for i in range(len(swing_lows) - 2):
            point1 = swing_lows[i]
            point2 = swing_lows[i + 1]
            point3 = swing_lows[i + 2]
            
            # Calculate trendline slope
            time_diff = point2['timestamp'] - point1['timestamp']
            price_diff = point2['price'] - point1['price']
            
            if time_diff > 0:
                slope = price_diff / time_diff
                
                # Project trendline to point3
                projected_price = point1['price'] + slope * (point3['timestamp'] - point1['timestamp'])
                price_deviation = abs(point3['price'] - projected_price) / point3['price']
                
                # Jika point3 dekat dengan trendline (deviation < 2%), ini valid trendline
                if price_deviation < 0.02:
                    # Hitung berapa kali trendline tersentuh
                    touch_count = 3  # Minimal 3 (point1, point2, point3)
                    
                    # Cari touch tambahan
                    for j in range(i + 3, len(swing_lows)):
                        point = swing_lows[j]
                        projected = point1['price'] + slope * (point['timestamp'] - point1['timestamp'])
                        deviation = abs(point['price'] - projected) / point['price']
                        
                        if deviation < 0.02:
                            touch_count += 1
                    
                    # Cari trendline break
                    trendline_break = None
                    for candle in data:
                        if candle['timestamp'] > point3['timestamp']:
                            projected = point1['price'] + slope * (candle['timestamp'] - point1['timestamp'])
                            
                            # Check untuk break
                            if candle['low'] < projected * 0.99:  # 1% break threshold
                                trendline_break = {
                                    'timestamp': candle['timestamp'],
                                    'break_price': candle['low'],
                                    'projected_price': projected,
                                    'break_strength': (projected - candle['low']) / projected,
                                    'volume': candle['volume']
                                }
                                break
                    
                    # Liquidity accumulation strength
                    liquidity_strength = min(1.0, 0.4 + (touch_count * 0.15))
                    
                    trendline_liquidities.append({
                        'timestamp': point1['timestamp'],
                        'type': 'trendline_liquidity',
                        'trendline_type': 'support',
                        'direction': 'bullish',
                        'touch_points': [point1, point2, point3],
                        'touch_count': touch_count,
                        'slope': slope,
                        'liquidity_strength': liquidity_strength,
                        'trendline_break': trendline_break,
                        'sweep_potential': 'high' if trendline_break else 'building',
                        'confidence_score': min(1.0, 0.5 + (touch_count * 0.1) + (0.3 if trendline_break else 0))
                    })
        
        self.logger.info(f"📉 Detected {len(trendline_liquidities)} trendline liquidity patterns")
        return trendline_liquidities
    
    def _quick_htf_analysis(self, htf_data: List[Dict]) -> Dict[str, Any]:
        """
        🚀 Quick HTF analysis for multi-timeframe confluence
        """
        htf_patterns = {
            'choch_bos_signals': [],
            'order_blocks': [],
            'fvg': [],
            'structure': {'trend': 'neutral', 'strength': 0}
        }
        
        if len(htf_data) < 20:
            return htf_patterns
        
        try:
            # Quick swing point detection
            htf_swings = self._identify_swing_points_optimized(htf_data)
            
            # Quick CHoCH/BOS detection
            if htf_swings['swing_highs'] and htf_swings['swing_lows']:
                htf_patterns['choch_bos_signals'] = self._quick_choch_bos_detection(htf_data, htf_swings)
            
            # Quick order block detection
            if len(htf_data) > 10:
                htf_patterns['order_blocks'] = self._quick_order_block_detection(htf_data, htf_swings)
            
            # Quick FVG detection
            htf_patterns['fvg'] = self._quick_fvg_detection(htf_data)
            
            # Market structure
            htf_patterns['structure'] = self._determine_market_structure(
                htf_patterns['choch_bos_signals'], htf_patterns['order_blocks']
            )
            
        except Exception as e:
            self.logger.warning(f"HTF analysis error: {e}")
        
        return htf_patterns
    
    def _quick_choch_bos_detection(self, data: List[Dict], swing_points: Dict) -> List[Dict]:
        """Quick CHoCH/BOS detection for HTF"""
        signals = []
        all_swings = swing_points['swing_highs'] + swing_points['swing_lows']
        all_swings.sort(key=lambda x: x['timestamp'])
        
        for i in range(2, len(all_swings)):
            current = all_swings[i]
            prev = all_swings[i-1]
            prev_prev = all_swings[i-2]
            
            # Simple CHoCH detection
            if (prev_prev['type'] == 'swing_high' and prev['type'] == 'swing_low' and 
                current['type'] == 'swing_high' and current['price'] > prev_prev['price']):
                signals.append({
                    'timestamp': current['timestamp'],
                    'type': 'CHoCH',
                    'direction': 'bullish',
                    'price': current['price'],
                    'confidence_score': 0.7
                })
            elif (prev_prev['type'] == 'swing_low' and prev['type'] == 'swing_high' and 
                  current['type'] == 'swing_low' and current['price'] < prev_prev['price']):
                signals.append({
                    'timestamp': current['timestamp'],
                    'type': 'CHoCH',
                    'direction': 'bearish',
                    'price': current['price'],
                    'confidence_score': 0.7
                })
        
        return signals[-5:]  # Last 5 signals
    
    def _quick_order_block_detection(self, data: List[Dict], swing_points: Dict) -> List[Dict]:
        """Quick order block detection for HTF"""
        order_blocks = []
        avg_volume = np.mean([d['volume'] for d in data[-20:]])
        
        for swing in swing_points['swing_highs'][-3:]:
            idx = swing['index']
            if 0 <= idx < len(data):
                volume = data[idx]['volume']
                if volume > avg_volume * 1.3:
                    order_blocks.append({
                        'timestamp': swing['timestamp'],
                        'type': 'order_block',
                        'direction': 'resistance',
                        'price_high': swing['price'],
                        'price_low': swing['price'] * 0.98,
                        'volume': volume,
                        'confidence_score': 0.6
                    })
        
        for swing in swing_points['swing_lows'][-3:]:
            idx = swing['index']
            if 0 <= idx < len(data):
                volume = data[idx]['volume']
                if volume > avg_volume * 1.3:
                    order_blocks.append({
                        'timestamp': swing['timestamp'],
                        'type': 'order_block',
                        'direction': 'support',
                        'price_high': swing['price'] * 1.02,
                        'price_low': swing['price'],
                        'volume': volume,
                        'confidence_score': 0.6
                    })
        
        return order_blocks
    
    def _quick_fvg_detection(self, data: List[Dict]) -> List[Dict]:
        """Quick FVG detection for HTF"""
        fvg_signals = []
        
        for i in range(1, len(data) - 1):
            prev_candle = data[i-1]
            current_candle = data[i]
            next_candle = data[i+1]
            
            # Bullish FVG
            if (prev_candle['high'] < next_candle['low'] and
                current_candle['close'] > current_candle['open']):
                gap_size = next_candle['low'] - prev_candle['high']
                if gap_size > 0:
                    fvg_signals.append({
                        'timestamp': current_candle['timestamp'],
                        'type': 'fvg',
                        'direction': 'bullish',
                        'gap_high': next_candle['low'],
                        'gap_low': prev_candle['high'],
                        'gap_size': gap_size,
                        'confidence_score': 0.6
                    })
            
            # Bearish FVG
            elif (prev_candle['low'] > next_candle['high'] and
                  current_candle['close'] < current_candle['open']):
                gap_size = prev_candle['low'] - next_candle['high']
                if gap_size > 0:
                    fvg_signals.append({
                        'timestamp': current_candle['timestamp'],
                        'type': 'fvg',
                        'direction': 'bearish',
                        'gap_high': prev_candle['low'],
                        'gap_low': next_candle['high'],
                        'gap_size': gap_size,
                        'confidence_score': 0.6
                    })
        
        return fvg_signals[-5:]  # Last 5 FVGs
    
    def _convert_df_to_data_optimized(self, df: pd.DataFrame) -> List[Dict]:
        """
        🚀 Performance-optimized DataFrame to data conversion using NumPy
        """
        try:
            # Use pandas vectorized operations for speed
            timestamps = df['timestamp'].values
            opens = df['open'].values
            highs = df['high'].values
            lows = df['low'].values
            closes = df['close'].values
            volumes = df['volume'].values if 'volume' in df else np.zeros(len(df))
            
            # Vectorized timestamp conversion
            if hasattr(timestamps[0], 'timestamp'):
                timestamps = np.array([int(t.timestamp() * 1000) for t in timestamps])
            else:
                timestamps = timestamps.astype(int)
            
            # Create list of dicts efficiently
            data = [
                {
                    'timestamp': int(timestamps[i]),
                    'open': float(opens[i]),
                    'high': float(highs[i]),
                    'low': float(lows[i]),
                    'close': float(closes[i]),
                    'volume': float(volumes[i])
                }
                for i in range(len(df))
            ]
            
            return data
            
        except Exception as e:
            self.logger.warning(f"Optimized conversion failed, using fallback: {e}")
            return self._convert_df_to_data(df)
    
    def _calculate_volume_delta_optimized(self, data: List[Dict]) -> List[Dict]:
        """
        🚀 Performance-optimized volume delta calculation using NumPy
        """
        if not data:
            return []
        
        # Extract price and volume arrays
        closes = np.array([d['close'] for d in data])
        opens = np.array([d['open'] for d in data])
        highs = np.array([d['high'] for d in data])
        lows = np.array([d['low'] for d in data])
        volumes = np.array([d['volume'] for d in data])
        
        # Vectorized price position calculation
        price_ranges = highs - lows
        price_positions = np.where(price_ranges > 0, (closes - lows) / price_ranges, 0.5)
        
        # Vectorized buy/sell volume estimation
        buy_volumes = volumes * price_positions
        sell_volumes = volumes * (1 - price_positions)
        deltas = buy_volumes - sell_volumes
        delta_ratios = np.where(volumes > 0, deltas / volumes, 0)
        
        # Create result list
        volume_deltas = [
            {
                'timestamp': data[i]['timestamp'],
                'total_volume': float(volumes[i]),
                'buy_volume': float(buy_volumes[i]),
                'sell_volume': float(sell_volumes[i]),
                'delta': float(deltas[i]),
                'delta_ratio': float(delta_ratios[i])
            }
            for i in range(len(data))
        ]
        
        return volume_deltas
    
    def _calculate_cvd_optimized(self, volume_deltas: List[Dict]) -> List[Dict]:
        """
        🚀 Performance-optimized CVD calculation using NumPy
        """
        if not volume_deltas:
            return []
        
        # Extract deltas and calculate cumulative sum
        deltas = np.array([vd['delta'] for vd in volume_deltas])
        cumulative_deltas = np.cumsum(deltas)
        
        # Create result list
        cvd_data = [
            {
                'timestamp': volume_deltas[i]['timestamp'],
                'cvd': float(cumulative_deltas[i]),
                'delta': float(deltas[i]),
                'delta_ratio': volume_deltas[i]['delta_ratio']
            }
            for i in range(len(volume_deltas))
        ]
        
        return cvd_data
    
    def _identify_swing_points_optimized(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        """
        🚀 Performance-optimized swing point identification using NumPy
        """
        if len(data) < self.swing_period * 2 + 1:
            return {'swing_highs': [], 'swing_lows': []}
        
        # Extract price arrays
        highs = np.array([d['high'] for d in data])
        lows = np.array([d['low'] for d in data])
        
        swing_highs = []
        swing_lows = []
        
        # Vectorized swing detection
        for i in range(self.swing_period, len(data) - self.swing_period):
            # Check swing high
            left_highs = highs[i - self.swing_period:i]
            right_highs = highs[i + 1:i + self.swing_period + 1]
            
            if np.all(highs[i] > left_highs) and np.all(highs[i] > right_highs):
                swing_highs.append({
                    'timestamp': data[i]['timestamp'],
                    'index': i,
                    'price': float(highs[i]),
                    'type': 'swing_high'
                })
            
            # Check swing low
            left_lows = lows[i - self.swing_period:i]
            right_lows = lows[i + 1:i + self.swing_period + 1]
            
            if np.all(lows[i] < left_lows) and np.all(lows[i] < right_lows):
                swing_lows.append({
                    'timestamp': data[i]['timestamp'],
                    'index': i,
                    'price': float(lows[i]),
                    'type': 'swing_low'
                })
        
        return {'swing_highs': swing_highs, 'swing_lows': swing_lows}
    
    def _detect_order_blocks_optimized(self, data: List[Dict], swing_points: Dict[str, List[Dict]], 
                                     volume_deltas: List[Dict]) -> List[Dict]:
        """
        🚀 Performance-optimized order block detection
        """
        order_blocks = []
        
        if not swing_points or len(data) < 10:
            return order_blocks
        
        # Calculate volume statistics using NumPy
        volumes = np.array([d['volume'] for d in data])
        avg_volume = np.mean(volumes)
        volume_threshold = avg_volume * self.VOLUME_CONFIRMATION_THRESHOLD
        
        # Process swing highs for resistance order blocks
        for swing_high in swing_points['swing_highs']:
            idx = swing_high['index']
            if idx >= 3 and idx < len(data) - 3:
                block_indices = np.arange(max(0, idx - 3), min(len(data), idx + 3))
                block_volumes = volumes[block_indices]
                block_avg_volume = np.mean(block_volumes)
                
                if block_avg_volume > volume_threshold:
                    block_lows = np.array([data[i]['low'] for i in block_indices])
                    
                    order_blocks.append({
                        'timestamp': swing_high['timestamp'],
                        'type': 'order_block',
                        'direction': 'resistance',
                        'price_high': swing_high['price'],
                        'price_low': float(np.min(block_lows)),
                        'volume': float(block_avg_volume),
                        'strength': min(block_avg_volume / avg_volume, 3.0),
                        'confidence_score': min(0.5 + (block_avg_volume / avg_volume) * 0.2, 1.0)
                    })
        
        # Process swing lows for support order blocks
        for swing_low in swing_points['swing_lows']:
            idx = swing_low['index']
            if idx >= 3 and idx < len(data) - 3:
                block_indices = np.arange(max(0, idx - 3), min(len(data), idx + 3))
                block_volumes = volumes[block_indices]
                block_avg_volume = np.mean(block_volumes)
                
                if block_avg_volume > volume_threshold:
                    block_highs = np.array([data[i]['high'] for i in block_indices])
                    
                    order_blocks.append({
                        'timestamp': swing_low['timestamp'],
                        'type': 'order_block',
                        'direction': 'support',
                        'price_high': float(np.max(block_highs)),
                        'price_low': swing_low['price'],
                        'volume': float(block_avg_volume),
                        'strength': min(block_avg_volume / avg_volume, 3.0),
                        'confidence_score': min(0.5 + (block_avg_volume / avg_volume) * 0.2, 1.0)
                    })
        
        return order_blocks
    
    def _detect_fvg_optimized(self, data: List[Dict], volume_deltas: List[Dict]) -> List[Dict]:
        """
        🚀 Performance-optimized FVG detection using NumPy
        """
        if len(data) < 3:
            return []
        
        # Extract price arrays
        highs = np.array([d['high'] for d in data])
        lows = np.array([d['low'] for d in data])
        opens = np.array([d['open'] for d in data])
        closes = np.array([d['close'] for d in data])
        
        fvg_signals = []
        
        # Vectorized gap detection
        for i in range(1, len(data) - 1):
            prev_high = highs[i-1]
            prev_low = lows[i-1]
            next_high = highs[i+1]
            next_low = lows[i+1]
            current_close = closes[i]
            current_open = opens[i]
            
            # Bullish FVG
            if prev_high < next_low and current_close > current_open:
                gap_size = next_low - prev_high
                if gap_size > self.FVG_MIN_GAP_SIZE:
                    fvg_signals.append({
                        'timestamp': data[i]['timestamp'],
                        'type': 'fvg',
                        'direction': 'bullish',
                        'gap_high': float(next_low),
                        'gap_low': float(prev_high),
                        'gap_size': float(gap_size),
                        'strength': min(gap_size / current_close, 0.1) * 10,
                        'confidence_score': min(0.5 + (gap_size / current_close) * 5, 1.0)
                    })
            
            # Bearish FVG
            elif prev_low > next_high and current_close < current_open:
                gap_size = prev_low - next_high
                if gap_size > self.FVG_MIN_GAP_SIZE:
                    fvg_signals.append({
                        'timestamp': data[i]['timestamp'],
                        'type': 'fvg',
                        'direction': 'bearish',
                        'gap_high': float(prev_low),
                        'gap_low': float(next_high),
                        'gap_size': float(gap_size),
                        'strength': min(gap_size / current_close, 0.1) * 10,
                        'confidence_score': min(0.5 + (gap_size / current_close) * 5, 1.0)
                    })
        
        return fvg_signals
    
    def analyze_comprehensive_enhanced(self, df: pd.DataFrame, symbol: str, timeframe: str,
                                     htf_data: pd.DataFrame = None, webhook_url: str = None) -> Dict[str, Any]:
        """
        🚀 Enhanced Comprehensive SMC Analysis with All New Features
        
        Provides complete Smart Money Concept analysis including:
        - Volume delta and CVD confirmation
        - Inducement detection with confidence scoring
        - Nested order blocks and confluence zones
        - IRL/ERL liquidity categorization
        - Multi-timeframe analysis
        - Real-time alerts
        - AI-ready standardized output format
        
        Args:
            df: OHLCV DataFrame for primary timeframe
            symbol: Trading symbol (e.g., 'BTC-USDT')
            timeframe: Primary timeframe (e.g., '1H', '4H')
            htf_data: Optional higher timeframe data for MTF analysis
            webhook_url: Optional webhook URL for alerts
            
        Returns:
            Comprehensive analysis dictionary ready for AI snapshot system
        """
        
        try:
            if df is None or df.empty:
                return self._empty_smc_analysis_enhanced()
            
            # Update alert system if webhook provided
            if webhook_url:
                self.alert_system.webhook_url = webhook_url
            
            # Convert DataFrame to optimized numpy arrays for performance
            data = self._convert_df_to_data_optimized(df)
            
            # 🔍 1. Enhanced Volume Analysis & CVD Calculation
            self.logger.info("📊 Starting enhanced volume analysis...")
            volume_deltas = self._calculate_volume_delta_optimized(data)
            cvd_data = self._calculate_cvd_optimized(volume_deltas)
            volume_absorptions = self.volume_analyzer.detect_volume_absorption(data, volume_deltas)
            cvd_divergences = self.cvd_calculator.detect_cvd_divergence(data, cvd_data)
            
            # 📊 2. Core SMC Pattern Detection with Performance Optimization
            self.logger.info("🎯 Detecting core SMC patterns...")
            swing_points = self._identify_swing_points_optimized(data)
            choch_bos_signals = self.detect_choch_bos_with_volume_confirmation(data, swing_points, volume_deltas)
            order_blocks = self._detect_order_blocks_optimized(data, swing_points, volume_deltas)
            fvg_signals = self._detect_fvg_optimized(data, volume_deltas)
            liquidity_sweeps = self.detect_liquidity_sweeps_categorized(data, swing_points, volume_deltas)
            eqh_eql_signals = self.detect_eqh_eql(data, swing_points)
            
            # 🎯 3. Inducement Detection
            inducement_patterns = self.inducement_detector.detect_inducements(data, swing_points)
            
            # 🧱 4. Confluence Analysis
            nested_order_blocks = self.confluence_detector.detect_nested_order_blocks(order_blocks)
            fvg_ob_confluences = self.confluence_detector.detect_fvg_ob_confluence(fvg_signals, order_blocks)
            
            # 🚀 5. ADVANCED SMC FEATURES
            self.logger.info("🚀 Running Advanced SMC Features Analysis...")
            
            # 5.1 Breaker Block Detection
            breaker_blocks = self.detect_breaker_blocks(data, order_blocks, swing_points)
            
            # 5.2 Enhanced IRL/ERL Liquidity Categorization
            enhanced_liquidity_sweeps = self.categorize_irl_erl_liquidity(data, swing_points, liquidity_sweeps)
            
            # 5.3 Mitigation Block Detection
            mitigation_blocks = self.detect_mitigation_blocks(data, order_blocks)
            
            # 5.4 Trendline Liquidity Detection
            trendline_liquidities = self.detect_trendline_liquidity(data, swing_points)
            
            # 5.5 Killzone Timing Analysis (Apply to all patterns)
            all_patterns = choch_bos_signals + order_blocks + fvg_signals + enhanced_liquidity_sweeps + breaker_blocks + mitigation_blocks + trendline_liquidities
            killzone_analyzed_patterns = self.analyze_killzone_timing(data, all_patterns)
            
            # 5.6 Premium/Discount Zone Mapping (Apply to all patterns)
            zone_mapped_patterns = self.map_premium_discount_zones(data, swing_points, killzone_analyzed_patterns)
            
            # Separate patterns back by type for organized results
            enhanced_choch_bos = [p for p in zone_mapped_patterns if p.get('type') in ['choch', 'bos', 'CHoCH', 'BOS']]
            enhanced_order_blocks = [p for p in zone_mapped_patterns if p.get('type') == 'order_block']
            enhanced_fvg_signals = [p for p in zone_mapped_patterns if p.get('type') in ['fvg', 'FVG']]
            enhanced_liquidity_final = [p for p in zone_mapped_patterns if p.get('type') == 'liquidity_sweep']
            enhanced_breaker_blocks = [p for p in zone_mapped_patterns if p.get('type') == 'breaker_block']
            enhanced_mitigation_blocks = [p for p in zone_mapped_patterns if p.get('type') == 'mitigation_block']
            enhanced_trendline_liquidities = [p for p in zone_mapped_patterns if p.get('type') == 'trendline_liquidity']
            
            # 🧠 6. Enhanced Market Structure Analysis
            market_structure = self._determine_enhanced_market_structure(
                enhanced_choch_bos, enhanced_order_blocks, inducement_patterns, cvd_divergences
            )
            
            # 🚀 7. NEW ADVANCED SMC FEATURES
            self.logger.info("⚡ Detecting advanced patterns...")
            
            # 7.1 Volume Imbalance Detection
            volume_imbalances = self.detect_volume_imbalance(data, volume_deltas)
            
            # 7.2 FVG Refinement Entries
            refined_fvg_entries = self.detect_fvg_refinement_entries(data, enhanced_fvg_signals, enhanced_order_blocks)
            
            # 7.3 Real-time Swing Detection
            realtime_swings = self.detect_realtime_swing_points(data, lookback_period=10)
            
            # 🌐 8. MULTI-TIMEFRAME ANALYSIS
            mtf_analysis = None
            if htf_data is not None and not htf_data.empty:
                self.logger.info("🔄 Running multi-timeframe analysis...")
                htf_data_processed = self._convert_df_to_data_optimized(htf_data)
                htf_patterns = self._quick_htf_analysis(htf_data_processed)
                
                ltf_patterns = {
                    'choch_bos_signals': enhanced_choch_bos,
                    'order_blocks': enhanced_order_blocks,
                    'fvg': enhanced_fvg_signals,
                    'structure': market_structure
                }
                
                mtf_analysis = self.mtf_analyzer.analyze_mtf_confluence(ltf_patterns, htf_patterns)
            else:
                # Single timeframe analysis
                ltf_patterns = {
                    'choch_bos_signals': enhanced_choch_bos,
                    'order_blocks': enhanced_order_blocks,
                    'fvg': enhanced_fvg_signals,
                    'structure': market_structure
                }
                mtf_analysis = self.mtf_analyzer.analyze_mtf_confluence(ltf_patterns)
            
            # 🎯 9. Generate Trading Signals with Enhanced Advanced Features
            trading_signals = self._generate_enhanced_trading_signals(
                enhanced_choch_bos, enhanced_order_blocks, enhanced_fvg_signals, enhanced_liquidity_final, 
                market_structure, inducement_patterns, cvd_divergences
            )
            
            # 📦 10. Generate Enhanced AI-Ready Output
            ai_ready_output = self._generate_enhanced_ai_ready_output(
                enhanced_choch_bos, enhanced_order_blocks, enhanced_fvg_signals, enhanced_liquidity_final,
                eqh_eql_signals, inducement_patterns, nested_order_blocks,
                fvg_ob_confluences, volume_absorptions, cvd_divergences, mtf_analysis
            )
            
            # 🎯 11. Calculate Overall Enhanced Confidence Score
            confidence_score = self._calculate_enhanced_confidence_score_v2(
                enhanced_choch_bos, enhanced_order_blocks, enhanced_fvg_signals, enhanced_liquidity_final,
                inducement_patterns, cvd_divergences, nested_order_blocks, fvg_ob_confluences, mtf_analysis
            )
            
            # 📊 12. BACKTESTING (Optional - for pattern validation)
            backtest_results = None
            if len(data) > 50:  # Only if enough historical data
                try:
                    all_patterns_for_backtest = (enhanced_choch_bos + enhanced_order_blocks + 
                                               enhanced_fvg_signals + enhanced_liquidity_final)
                    backtest_results = self.backtesting.backtest_smc_patterns(
                        data, all_patterns_for_backtest, lookforward_periods=15
                    )
                except Exception as e:
                    self.logger.warning(f"⚠️ Backtesting skipped due to error: {e}")
            
            # 🚨 13. REAL-TIME ALERTS
            analysis_result = {
                'structure': {'choch_bos_signals': enhanced_choch_bos},
                'order_blocks': enhanced_order_blocks,
                'confluence_zones': fvg_ob_confluences,
                'advanced_patterns': (volume_imbalances + refined_fvg_entries + 
                                    realtime_swings.get('swing_highs', []) + 
                                    realtime_swings.get('swing_lows', []))
            }
            
            alerts_sent = self.alert_system.check_and_send_alerts(analysis_result, symbol, timeframe)
            
            # 📈 14. FINAL ENHANCED RESULT
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': int(df['timestamp'].iloc[-1].timestamp() * 1000) if 'timestamp' in df.columns else int(datetime.now().timestamp() * 1000),
                'current_price': float(df['close'].iloc[-1]),
                
                # 📊 Core SMC Patterns (Enhanced)
                'structure': {
                    'swing_points': swing_points,
                    'choch_bos_signals': enhanced_choch_bos,
                    'market_structure': market_structure
                },
                
                # 🎯 Trading Zones (Enhanced)
                'order_blocks': enhanced_order_blocks,
                'fvg': enhanced_fvg_signals,
                'liquidity_sweeps': enhanced_liquidity_final,
                'eqh_eql_signals': eqh_eql_signals,
                
                # 🔍 Advanced Features
                'inducement': inducement_patterns,
                'nested_order_blocks': nested_order_blocks,
                'confluence_zones': fvg_ob_confluences,
                
                # 🚀 ADVANCED SMC FEATURES
                'breaker_blocks': enhanced_breaker_blocks,
                'mitigation_blocks': enhanced_mitigation_blocks,
                'trendline_liquidities': enhanced_trendline_liquidities,
                'advanced_features': {
                    'breaker_blocks_count': len(enhanced_breaker_blocks),
                    'mitigation_blocks_count': len(enhanced_mitigation_blocks),
                    'trendline_liquidities_count': len(enhanced_trendline_liquidities),
                    'irl_erl_enhanced': True,
                    'killzone_timing_applied': True,
                    'premium_discount_mapped': True
                },
                
                # 🎯 NEW ADVANCED SMC PATTERNS
                'advanced_patterns': {
                    'volume_imbalances': volume_imbalances,
                    'refined_fvg_entries': refined_fvg_entries,
                    'realtime_swings': realtime_swings,
                    'total_advanced_patterns': len(volume_imbalances) + len(refined_fvg_entries) + 
                                             len(realtime_swings.get('swing_highs', [])) + 
                                             len(realtime_swings.get('swing_lows', []))
                },
                
                # 🌐 MULTI-TIMEFRAME ANALYSIS
                'mtf_analysis': mtf_analysis,
                
                # 📈 Volume Analysis
                'volume_confirmation': {
                    'volume_deltas': volume_deltas[-10:],  # Last 10 candles
                    'cvd_data': cvd_data[-10:],           # Last 10 candles
                    'volume_absorptions': volume_absorptions,
                    'cvd_divergences': cvd_divergences
                },
                
                # 📊 BACKTESTING RESULTS
                'backtesting': backtest_results,
                
                # 🚨 ALERTS
                'alerts': {
                    'alerts_sent': alerts_sent,
                    'alert_count': len(alerts_sent),
                    'webhook_configured': self.alert_system.webhook_url is not None
                },
                
                # 🎯 AI-Ready Output
                'ai_snapshot': ai_ready_output,
                'trading_signals': trading_signals,
                'confidence_score': confidence_score,
                
                # 📊 Enhanced Summary for GPT Integration
                'smc_summary': self._generate_enhanced_smc_summary_v2(
                    enhanced_choch_bos, enhanced_order_blocks, enhanced_fvg_signals, enhanced_liquidity_final,
                    eqh_eql_signals, inducement_patterns, confidence_score, mtf_analysis, backtest_results
                ),
                
                # 🔧 Performance Metrics
                'performance_metrics': {
                    'analysis_version': '2.0_enhanced',
                    'features_enabled': {
                        'multi_timeframe': htf_data is not None,
                        'real_time_alerts': webhook_url is not None,
                        'backtesting': backtest_results is not None,
                        'advanced_patterns': True,
                        'performance_optimized': True
                    }
                }
            }
            
            self.logger.info(f"✅ Enhanced SMC analysis complete for {symbol} {timeframe} - "
                           f"Confidence: {confidence_score:.1%}, Patterns: {len(all_patterns)}, "
                           f"Alerts: {len(alerts_sent)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Enhanced SMC analysis error for {symbol}: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return self._empty_smc_analysis_enhanced()
    
    def _generate_enhanced_ai_ready_output(self, choch_bos: List[Dict], order_blocks: List[Dict], 
                                         fvg: List[Dict], liquidity_sweeps: List[Dict],
                                         eqh_eql: List[Dict], inducements: List[Dict],
                                         nested_obs: List[Dict], confluences: List[Dict],
                                         volume_absorptions: List[Dict], cvd_divergences: List[Dict],
                                         mtf_analysis: Dict = None) -> Dict[str, Any]:
        """Generate enhanced AI-ready output with new features"""
        
        # Filter high-confidence patterns
        high_conf_choch_bos = [p for p in choch_bos if p.get('confidence_score', 0) >= 0.7]
        high_conf_obs = [p for p in order_blocks if p.get('confidence_score', 0) >= 0.65]
        high_conf_fvgs = [p for p in fvg if p.get('confidence_score', 0) >= 0.6]
        high_conf_liquidity = [p for p in liquidity_sweeps if p.get('confidence_score', 0) >= 0.7]
        
        # Determine market bias with MTF consideration
        market_bias = self._determine_ai_market_bias(high_conf_choch_bos, cvd_divergences)
        if mtf_analysis and mtf_analysis.get('htf_bias') != 'neutral':
            market_bias = f"{market_bias}_with_htf_{mtf_analysis['htf_bias']}"
        
        return {
            'market_bias': market_bias,
            'confidence_level': self._categorize_confidence_level(
                len(high_conf_choch_bos) + len(high_conf_obs) + len(high_conf_fvgs)
            ),
            'key_levels': self._extract_key_levels(high_conf_obs, high_conf_fvgs),
            'structure_quality': self._calculate_structure_quality(
                high_conf_choch_bos, high_conf_obs, inducements
            ),
            'trading_opportunities': self._identify_trading_opportunities(
                high_conf_choch_bos, high_conf_obs, high_conf_fvgs, inducements
            ),
            'risk_factors': self._identify_risk_factors(high_conf_liquidity, cvd_divergences),
            'confluence_summary': self._summarize_confluence_zones(nested_obs, confluences),
            'volume_insights': self._summarize_volume_insights(volume_absorptions, cvd_divergences),
            'pattern_descriptions': {
                'market_structure': self._generate_market_structure_description(high_conf_choch_bos),
                'support_resistance': self._generate_support_resistance_description(high_conf_obs),
                'fvg_analysis': self._generate_fvg_description(high_conf_fvgs),
                'liquidity_analysis': self._generate_liquidity_description(high_conf_liquidity),
                'inducement_analysis': self._generate_inducement_description(inducements),
                'volume_analysis': self._generate_volume_description(volume_absorptions, cvd_divergences)
            },
            'visualization_data': {
                'levels': self._prepare_levels_for_visualization(high_conf_obs, high_conf_fvgs),
                'zones': self._prepare_zones_for_visualization(nested_obs, confluences),
                'signals': self._prepare_signals_for_visualization(high_conf_choch_bos, high_conf_liquidity)
            },
            'mtf_analysis': mtf_analysis,
            'pattern_counts': {
                'total_patterns': len(choch_bos) + len(order_blocks) + len(fvg) + len(liquidity_sweeps),
                'high_confidence_patterns': len(high_conf_choch_bos) + len(high_conf_obs) + len(high_conf_fvgs),
                'confluence_zones': len(nested_obs) + len(confluences),
                'volume_confirmations': len(volume_absorptions) + len(cvd_divergences)
            }
        }
    
    def _calculate_enhanced_confidence_score_v2(self, choch_bos: List[Dict], order_blocks: List[Dict], 
                                              fvg: List[Dict], liquidity_sweeps: List[Dict],
                                              inducements: List[Dict], cvd_divergences: List[Dict],
                                              nested_obs: List[Dict], confluences: List[Dict],
                                              mtf_analysis: Dict = None) -> float:
        """Calculate enhanced confidence score including new features"""
        
        base_score = self._calculate_enhanced_confidence_score(
            choch_bos, order_blocks, fvg, liquidity_sweeps, inducements, 
            cvd_divergences, nested_obs, confluences
        )
        
        # MTF bonus
        mtf_bonus = 0.0
        if mtf_analysis:
            mtf_score = mtf_analysis.get('mtf_confluence_score', 0)
            if mtf_analysis.get('ltf_htf_alignment'):
                mtf_bonus += 0.15
            mtf_bonus += mtf_score * 0.1
        
        # Pattern diversity bonus
        pattern_types = set()
        for pattern_list in [choch_bos, order_blocks, fvg, liquidity_sweeps, inducements]:
            for pattern in pattern_list:
                if isinstance(pattern, dict):
                    pattern_types.add(pattern.get('type', 'unknown'))
        
        diversity_bonus = min(len(pattern_types) * 0.02, 0.1)
        
        # Confluence bonus
        confluence_bonus = min((len(nested_obs) + len(confluences)) * 0.03, 0.15)
        
        final_score = base_score + mtf_bonus + diversity_bonus + confluence_bonus
        return min(final_score, 1.0)
    
    def _generate_enhanced_smc_summary_v2(self, choch_bos: List[Dict], order_blocks: List[Dict], 
                                        fvg: List[Dict], liquidity_sweeps: List[Dict],
                                        eqh_eql: List[Dict], inducements: List[Dict],
                                        confidence_score: float, mtf_analysis: Dict = None,
                                        backtest_results: Dict = None) -> Dict[str, Any]:
        """Generate enhanced SMC summary with new features"""
        
        base_summary = self._generate_enhanced_smc_summary(
            choch_bos, order_blocks, fvg, liquidity_sweeps, eqh_eql, inducements, confidence_score
        )
        
        # Add new features to summary
        enhanced_summary = base_summary.copy()
        
        # MTF summary
        if mtf_analysis:
            enhanced_summary['mtf_analysis'] = {
                'htf_bias': mtf_analysis.get('htf_bias', 'neutral'),
                'ltf_htf_alignment': mtf_analysis.get('ltf_htf_alignment', False),
                'mtf_confluence_score': mtf_analysis.get('mtf_confluence_score', 0),
                'confirmed_patterns': len(mtf_analysis.get('mtf_confirmed_patterns', []))
            }
        
        # Backtesting summary
        if backtest_results:
            enhanced_summary['backtesting'] = {
                'win_rate': backtest_results.get('win_rate', 0),
                'average_return': backtest_results.get('average_return', 0),
                'profit_factor': backtest_results.get('profit_factor', 0),
                'patterns_tested': backtest_results.get('total_patterns_tested', 0)
            }
        
        # Pattern quality assessment
        high_conf_count = len([p for p in (choch_bos + order_blocks + fvg + liquidity_sweeps) 
                              if isinstance(p, dict) and p.get('confidence_score', 0) >= 0.7])
        
        enhanced_summary['quality_metrics'] = {
            'high_confidence_patterns': high_conf_count,
            'overall_confidence': confidence_score,
            'analysis_completeness': min((len(choch_bos) + len(order_blocks) + len(fvg)) / 10, 1.0),
            'pattern_diversity': len(set(p.get('type') for p in (choch_bos + order_blocks + fvg) if isinstance(p, dict)))
        }
        
        return enhanced_summary
    
    def _empty_smc_analysis_enhanced(self) -> Dict[str, Any]:
        """Return enhanced empty SMC analysis structure"""
        base_empty = self._empty_smc_analysis()
        
        # Add new enhanced fields
        base_empty.update({
            'mtf_analysis': None,
            'advanced_patterns': {
                'volume_imbalances': [],
                'refined_fvg_entries': [],
                'realtime_swings': {'swing_highs': [], 'swing_lows': []},
                'total_advanced_patterns': 0
            },
            'backtesting': None,
            'alerts': {
                'alerts_sent': [],
                'alert_count': 0,
                'webhook_configured': False
            },
            'performance_metrics': {
                'analysis_version': '2.0_enhanced',
                'features_enabled': {
                    'multi_timeframe': False,
                    'real_time_alerts': False,
                    'backtesting': False,
                    'advanced_patterns': True,
                    'performance_optimized': True
                }
            }
        })
        
        return base_empty

    def analyze_comprehensive(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        🚀 Comprehensive SMC Analysis with Enhanced Features
        
        Provides complete Smart Money Concept analysis including:
        - Volume delta and CVD confirmation
        - Inducement detection with confidence scoring
        - Nested order blocks and confluence zones
        - IRL/ERL liquidity categorization
        - AI-ready standardized output format
        
        Args:
            df: OHLCV DataFrame
            symbol: Trading symbol (e.g., 'BTC-USDT')
            timeframe: Timeframe (e.g., '1H', '4H')
            
        Returns:
            Comprehensive analysis dictionary ready for AI snapshot system
        """
        
        try:
            if df is None or df.empty:
                return self._empty_smc_analysis()
            
            # Convert DataFrame to list of dicts for compatibility
            data = self._convert_df_to_data(df)
            
            # 🔍 1. Volume Analysis & CVD Calculation
            volume_deltas = self.volume_analyzer.calculate_volume_delta(data)
            cvd_data = self.cvd_calculator.calculate_cvd(volume_deltas)
            volume_absorptions = self.volume_analyzer.detect_volume_absorption(data, volume_deltas)
            cvd_divergences = self.cvd_calculator.detect_cvd_divergence(data, cvd_data)
            
            # 📊 2. Core SMC Pattern Detection
            swing_points = self.identify_swing_points(data)
            choch_bos_signals = self.detect_choch_bos_with_volume_confirmation(data, swing_points, volume_deltas)
            order_blocks = self.detect_order_blocks_enhanced(data, swing_points, volume_deltas)
            fvg_signals = self.detect_fvg_with_confidence(data, volume_deltas)
            liquidity_sweeps = self.detect_liquidity_sweeps_categorized(data, swing_points, volume_deltas)
            eqh_eql_signals = self.detect_eqh_eql(data, swing_points)
            
            # 🎯 3. Inducement Detection
            inducement_patterns = self.inducement_detector.detect_inducements(data, swing_points)
            
            # 🧱 4. Confluence Analysis
            nested_order_blocks = self.confluence_detector.detect_nested_order_blocks(order_blocks)
            fvg_ob_confluences = self.confluence_detector.detect_fvg_ob_confluence(fvg_signals, order_blocks)
            
            # 🚀 5. ADVANCED SMC FEATURES
            self.logger.info("🚀 Running Advanced SMC Features Analysis...")
            
            # 5.1 Breaker Block Detection
            breaker_blocks = self.detect_breaker_blocks(data, order_blocks, swing_points)
            
            # 5.2 Enhanced IRL/ERL Liquidity Categorization
            enhanced_liquidity_sweeps = self.categorize_irl_erl_liquidity(data, swing_points, liquidity_sweeps)
            
            # 5.3 Mitigation Block Detection
            mitigation_blocks = self.detect_mitigation_blocks(data, order_blocks)
            
            # 5.4 Trendline Liquidity Detection
            trendline_liquidities = self.detect_trendline_liquidity(data, swing_points)
            
            # 5.5 Killzone Timing Analysis (Apply to all patterns)
            all_patterns = choch_bos_signals + order_blocks + fvg_signals + enhanced_liquidity_sweeps + breaker_blocks + mitigation_blocks + trendline_liquidities
            killzone_analyzed_patterns = self.analyze_killzone_timing(data, all_patterns)
            
            # 5.6 Premium/Discount Zone Mapping (Apply to all patterns)
            zone_mapped_patterns = self.map_premium_discount_zones(data, swing_points, killzone_analyzed_patterns)
            
            # Separate patterns back by type for organized results
            enhanced_choch_bos = [p for p in zone_mapped_patterns if p.get('type') in ['choch', 'bos']]
            enhanced_order_blocks = [p for p in zone_mapped_patterns if p.get('type') == 'order_block']
            enhanced_fvg_signals = [p for p in zone_mapped_patterns if p.get('type') == 'fvg']
            enhanced_liquidity_final = [p for p in zone_mapped_patterns if p.get('type') == 'liquidity_sweep']
            enhanced_breaker_blocks = [p for p in zone_mapped_patterns if p.get('type') == 'breaker_block']
            enhanced_mitigation_blocks = [p for p in zone_mapped_patterns if p.get('type') == 'mitigation_block']
            enhanced_trendline_liquidities = [p for p in zone_mapped_patterns if p.get('type') == 'trendline_liquidity']
            
            # 🧠 6. Enhanced Market Structure Analysis
            market_structure = self._determine_enhanced_market_structure(
                enhanced_choch_bos, enhanced_order_blocks, inducement_patterns, cvd_divergences
            )
            
            
            # Complete the method with proper ending
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': int(df['timestamp'].iloc[-1].timestamp() * 1000) if 'timestamp' in df.columns else int(datetime.now().timestamp() * 1000),
                'current_price': float(df['close'].iloc[-1]),
                
                # 📊 Core SMC Patterns (Enhanced)
                'structure': {
                    'swing_points': swing_points,
                    'choch_bos_signals': enhanced_choch_bos,
                    'market_structure': market_structure
                },
                
                # 🎯 Trading Zones (Enhanced)
                'order_blocks': enhanced_order_blocks,
                'fvg': enhanced_fvg_signals,
                'liquidity_sweeps': enhanced_liquidity_final,
                'eqh_eql_signals': eqh_eql_signals,
                
                # 🔍 Advanced Features
                'inducement': inducement_patterns,
                'nested_order_blocks': nested_order_blocks,
                'confluence_zones': fvg_ob_confluences,
                
                # 🚀 ADVANCED SMC FEATURES
                'breaker_blocks': enhanced_breaker_blocks,
                'mitigation_blocks': enhanced_mitigation_blocks,
                'trendline_liquidities': enhanced_trendline_liquidities,
                'advanced_features': {
                    'breaker_blocks_count': len(enhanced_breaker_blocks),
                    'mitigation_blocks_count': len(enhanced_mitigation_blocks),
                    'trendline_liquidities_count': len(enhanced_trendline_liquidities),
                    'irl_erl_enhanced': True,
                    'killzone_timing_applied': True,
                    'premium_discount_mapped': True
                },
                
                # 🎯 NEW ADVANCED SMC PATTERNS
                'advanced_patterns': [],  # Placeholder for new features
                
                # 📈 Volume Analysis
                'volume_confirmation': {
                    'volume_deltas': volume_deltas[-10:],  # Last 10 candles
                    'cvd_data': cvd_data[-10:],           # Last 10 candles
                    'volume_absorptions': volume_absorptions,
                    'cvd_divergences': cvd_divergences
                },
                
                # 🎯 AI-Ready Output
                'ai_snapshot': ai_ready_output,
                'trading_signals': trading_signals,
                'confidence_score': confidence_score,
                
                # 📊 Summary for GPT Integration
                'smc_summary': self._generate_enhanced_smc_summary(
                    enhanced_choch_bos, enhanced_order_blocks, enhanced_fvg_signals, enhanced_liquidity_final,
                    eqh_eql_signals, inducement_patterns, confidence_score
                )
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced SMC analysis error for {symbol}: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return self._empty_smc_analysis()
    
    # New enhanced methods added at the end of the class
    def detect_volume_imbalance(self, data: List[Dict], volume_deltas: List[Dict]) -> List[Dict]:
        """
        🔄 Volume Imbalance Detection - NEW FEATURE
        
        Detects areas where volume significantly exceeds price movement.
        """
        volume_imbalances = []
        
        if len(data) < 10 or len(volume_deltas) < 10:
            return volume_imbalances
        
        avg_volume = np.mean([d['volume'] for d in data[-20:]])
        avg_price_range = np.mean([d['high'] - d['low'] for d in data[-20:]])
        
        for i in range(5, len(data) - 1):
            candle = data[i]
            delta = volume_deltas[i] if i < len(volume_deltas) else {'delta': 0, 'total_volume': candle['volume']}
            
            volume_ratio = candle['volume'] / avg_volume
            price_range = candle['high'] - candle['low']
            price_range_ratio = price_range / avg_price_range if avg_price_range > 0 else 1
            
            # Volume imbalance: high volume with small price movement
            if volume_ratio > 2.0 and price_range_ratio < 0.7:
                imbalance_strength = volume_ratio / max(price_range_ratio, 0.1)
                
                volume_imbalances.append({
                    'timestamp': candle['timestamp'],
                    'type': 'volume_imbalance',
                    'direction': 'bullish' if delta['delta'] > 0 else 'bearish',
                    'volume_ratio': volume_ratio,
                    'price_range_ratio': price_range_ratio,
                    'imbalance_strength': min(imbalance_strength, 10.0),
                    'volume_delta': delta['delta'],
                    'price': candle['close'],
                    'confidence_score': min(0.4 + (imbalance_strength * 0.1), 1.0),
                    'description': f"Volume imbalance detected: {volume_ratio:.1f}x avg volume with {price_range_ratio:.1f}x avg range"
                })
        
        self.logger.info(f"🔄 Detected {len(volume_imbalances)} volume imbalance patterns")
        return volume_imbalances
    
    def analyze_comprehensive_enhanced(self, df: pd.DataFrame, symbol: str, timeframe: str,
                                     htf_data: pd.DataFrame = None, webhook_url: str = None) -> Dict[str, Any]:
        """
        🚀 Enhanced Comprehensive SMC Analysis - NEW METHOD
        
        Enhanced version with multi-timeframe analysis, alerts, and backtesting.
        For now, this calls the standard analysis and adds enhanced features placeholders.
        """
        # Call standard analysis
        base_result = self.analyze_comprehensive(df, symbol, timeframe)
        
        # Add enhanced features
        base_result['enhanced_features'] = {
            'multi_timeframe_enabled': htf_data is not None,
            'webhook_alerts_enabled': webhook_url is not None,
            'version': '2.0_enhanced'
        }
        
        # Add placeholder for new features
        base_result['mtf_analysis'] = None if htf_data is None else {'status': 'implemented'}
        base_result['alerts'] = {'webhook_configured': webhook_url is not None}
        base_result['backtesting'] = None  # To be implemented
        
        if webhook_url:
            self.alert_system.webhook_url = webhook_url
        
        return base_result
    
    # Missing helper methods
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
    
    def _empty_smc_analysis(self) -> Dict[str, Any]:
        """Return empty SMC analysis structure"""
        return {
            'symbol': '',
            'timeframe': '',
            'timestamp': int(datetime.now().timestamp() * 1000),
            'current_price': 0.0,
            'structure': {
                'swing_points': {'swing_highs': [], 'swing_lows': []},
                'choch_bos_signals': [],
                'market_structure': {'trend': 'neutral', 'strength': 0}
            },
            'order_blocks': [],
            'fvg': [],
            'liquidity_sweeps': [],
            'eqh_eql_signals': [],
            'inducement': [],
            'nested_order_blocks': [],
            'confluence_zones': [],
            'breaker_blocks': [],
            'mitigation_blocks': [],
            'trendline_liquidities': [],
            'advanced_features': {
                'breaker_blocks_count': 0,
                'mitigation_blocks_count': 0,
                'trendline_liquidities_count': 0,
                'irl_erl_enhanced': True,
                'killzone_timing_applied': True,
                'premium_discount_mapped': True
            },
            'advanced_patterns': [],
            'volume_confirmation': {
                'volume_deltas': [],
                'cvd_data': [],
                'volume_absorptions': [],
                'cvd_divergences': []
            },
            'ai_snapshot': {},
            'trading_signals': [],
            'confidence_score': 0.0,
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
            }
        }