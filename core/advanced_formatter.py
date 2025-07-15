"""
Advanced formatter for professional trading analysis
Enhanced with AI capabilities from Phase 1 Integration
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AdvancedFormatter:
    """Advanced formatter for professional Indonesian trading analysis with AI capabilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ai_engine = None
        self.signal_engine = None
        
        # Initialize AI Engine
        try:
            from .ai_engine import get_ai_engine
            self.ai_engine = get_ai_engine()
        except ImportError:
            self.logger.warning("AI Engine not available - using fallback formatting")
        
        # Initialize Signal Engine
        try:
            from .signal_engine import SignalEngine
            self.signal_engine = SignalEngine()
        except ImportError:
            self.logger.warning("Signal Engine not available - using basic signals")
    
    def format_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Format comprehensive analysis in professional Indonesian style with AI enhancement"""
        
        try:
            symbol = analysis_data.get('symbol', 'UNKNOWN')
            timeframe = analysis_data.get('timeframe', '1H')
            current_price = analysis_data.get('current_price', 0)
            signals = analysis_data.get('signals', {})
            indicators = analysis_data.get('indicators', {})
            trend = analysis_data.get('trend', 'NEUTRAL')
            
            # Try to get AI-enhanced narrative if available
            ai_narrative = self._get_ai_narrative(symbol, timeframe, analysis_data)
            
            # Generate comprehensive signals if Signal Engine is available
            enhanced_signals = self._get_enhanced_signals(analysis_data)
            
            # Use enhanced signals if available, otherwise fallback to basic signals
            if enhanced_signals and enhanced_signals.get('final_signal'):
                final_signal = enhanced_signals['final_signal']
                signals = {
                    'action': final_signal.get('signal', 'HOLD').upper(),
                    'confidence': final_signal.get('confidence', 0) / 100,
                    'entry_price': enhanced_signals.get('trade_setup', {}).get('entry_price', current_price),
                    'stop_loss': enhanced_signals.get('trade_setup', {}).get('stop_loss', current_price * 0.95),
                    'take_profit': enhanced_signals.get('trade_setup', {}).get('take_profit_1', current_price * 1.05)
                }
            
            # Build formatted analysis with AI enhancement
            if ai_narrative:
                # Use AI narrative as primary content
                analysis = f"""
{ai_narrative}

───────────────────────────────────────
📊 **TECHNICAL SUMMARY**
• Symbol: {symbol} ({timeframe})
• Current Price: ${current_price:,.2f}
• Signal: {signals.get('action', 'HOLD')} 
• Confidence: {signals.get('confidence', 0)*100:.1f}%
• Trend: {trend}

⚡ **TRADING LEVELS**
• Entry: ${signals.get('entry_price', current_price):,.2f}
• Stop Loss: ${signals.get('stop_loss', current_price*0.95):,.2f}
• Take Profit: ${signals.get('take_profit', current_price*1.05):,.2f}
• Risk/Reward: 1:2

⚠️ **RISK MANAGEMENT**
• Maximum 2% portfolio allocation
• Use trailing stops
• Monitor volume breakouts

───────────────────────────────────────"""
            else:
                # Fallback to enhanced traditional formatting
                analysis = f"""
📊 **ANALISIS TEKNIKAL {symbol}**
═══════════════════════════════════════

🎯 **RINGKASAN EKSEKUTIF**
• Harga Saat Ini: ${current_price:,.2f}
• Sinyal: {signals.get('action', 'HOLD')} 
• Confidence: {signals.get('confidence', 0)*100:.1f}%
• Trend: {trend}
• Timeframe: {timeframe}

🔍 **STRUKTUR SMART MONEY CONCEPT**
{self._format_smc_analysis(analysis_data)}

📈 **INDIKATOR TEKNIKAL**
• RSI(14): {indicators.get('rsi', {}).get('value', 50):.1f}
• EMA 20: ${indicators.get('ema', {}).get('ema_20', current_price):,.2f}
• EMA 50: ${indicators.get('ema', {}).get('ema_50', current_price):,.2f}
• MACD: {'Bullish' if indicators.get('macd', {}).get('bullish', False) else 'Bearish'}

📊 **VOLUME & LIKUIDITAS**
{self._format_volume_analysis(analysis_data)}

🌡️ **MARKET SENTIMENT**
{self._format_sentiment_analysis(analysis_data)}

⚡ **STRATEGI POSISI**
• Entry: ${signals.get('entry_price', current_price):,.2f}
• Stop Loss: ${signals.get('stop_loss', current_price*0.95):,.2f}
• Take Profit 1: ${signals.get('take_profit', current_price*1.05):,.2f}
• Risk/Reward: 1:2

⚠️ **MANAJEMEN RISIKO**
• Maksimal 2% dari portfolio
• Gunakan trailing stop
• Monitor volume breakout

💡 **REKOMENDASI**
{self._generate_recommendation(signals, indicators, trend)}

───────────────────────────────────────"""
📅 Analisis: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} WIB
🔄 Update: Real-time monitoring aktif
"""
            
            return analysis.strip()
            
        except Exception as e:
            self.logger.error(f"Error formatting analysis: {e}")
            return self._fallback_format(analysis_data)
    
    def _generate_recommendation(self, signals: Dict[str, Any], indicators: Dict[str, Any], trend: str) -> str:
        """Generate trading recommendation"""
        
        action = signals.get('action', 'HOLD')
        confidence = signals.get('confidence', 0) * 100
        
        if action == 'BUY' and confidence > 70:
            return """
• STRONG BUY: Konfirmasi multiple indikator bullish
• Entry bertahap dengan DCA strategy
• Target profit taking di level resistance
• Stop loss ketat untuk protect capital"""
        
        elif action == 'SELL' and confidence > 70:
            return """
• STRONG SELL: Tekanan bearish dominan
• Consider short position dengan proper risk
• Watch support level untuk potential bounce
• Exit strategy harus clear dan disciplined"""
        
        elif action == 'BUY' and confidence > 50:
            return """
• MODERATE BUY: Setup bullish terbentuk
• Wait for confirmation di breakout level
• Position sizing conservative recommended
• Monitor volume untuk validasi signal"""
        
        elif action == 'SELL' and confidence > 50:
            return """
• MODERATE SELL: Weakness detected
• Consider profit taking jika hold position
• Wait lower entry untuk accumulation
• Risk management tetap priority"""
        
        else:
            return """
• HOLD/WAIT: Market masih consolidation
• Observe key level untuk breakout direction
• No rush untuk entry, patience is key
• Focus pada risk management"""
    
    def _fallback_format(self, analysis_data: Dict[str, Any]) -> str:
        """Fallback format when main formatting fails"""
        
        return f"""
📊 **ANALISIS TEKNIKAL**
═══════════════════════════════════════

🎯 **RINGKASAN**
• Symbol: {analysis_data.get('symbol', 'UNKNOWN')}
• Harga: ${analysis_data.get('current_price', 0):,.2f}
• Status: {analysis_data.get('signals', {}).get('action', 'HOLD')}
• Trend: {analysis_data.get('trend', 'NEUTRAL')}

⚠️ **CATATAN**
Analisis menggunakan format fallback.
Silakan coba kembali untuk analisis lengkap.

📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} WIB
"""
    
    def _get_ai_narrative(self, symbol: str, timeframe: str, analysis_data: Dict[str, Any]) -> Optional[str]:
        """Get AI-enhanced narrative if available"""
        if not self.ai_engine or not self.ai_engine.is_available():
            return None
        
        try:
            # Generate AI narrative with quick mode for faster response
            narrative = self.ai_engine.generate_ai_snapshot(
                symbol=symbol,
                timeframe=timeframe,
                analysis_result=analysis_data,
                quick_mode=True
            )
            return narrative
        except Exception as e:
            self.logger.warning(f"AI narrative generation failed: {e}")
            return None
    
    def _get_enhanced_signals(self, analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get enhanced signals from Signal Engine if available"""
        if not self.signal_engine:
            return None
        
        try:
            # Extract dataframe from analysis_data
            df = analysis_data.get('df')
            if df is None:
                return None
            
            symbol = analysis_data.get('symbol', 'UNKNOWN')
            timeframe = analysis_data.get('timeframe', '1H')
            
            # Generate comprehensive signals
            enhanced_signals = self.signal_engine.generate_comprehensive_signals(
                df=df,
                symbol=symbol,
                timeframe=timeframe
            )
            
            return enhanced_signals
        except Exception as e:
            self.logger.warning(f"Enhanced signals generation failed: {e}")
            return None
    
    def _format_smc_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Format SMC analysis section"""
        smc_data = analysis_data.get('smc_analysis', {})
        
        if not smc_data:
            return """• BOS (Break of Structure): Tidak terdeteksi
• CHoCH (Change of Character): Tidak terdeteksi
• FVG (Fair Value Gap): Tidak ada
• Order Blocks: Tidak teridentifikasi"""
        
        choch_bos = smc_data.get('choch_bos_signals', [])
        order_blocks = smc_data.get('order_blocks', [])
        fvg_signals = smc_data.get('fvg_signals', [])
        
        return f"""• BOS/CHoCH Signals: {len(choch_bos)} terdeteksi
• Order Blocks: {len(order_blocks)} teridentifikasi
• FVG Signals: {len(fvg_signals)} terdeteksi
• Confidence Score: {smc_data.get('confidence_score', 0):.1f}%"""
    
    def _format_volume_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Format volume analysis section"""
        volume_data = analysis_data.get('volume_analysis', {})
        
        if not volume_data:
            return """• Volume Trend: Normal
• Volume Spike: Tidak ada
• Volume Ratio: 1.0x
• CVD: Seimbang"""
        
        return f"""• Volume Signal: {volume_data.get('signal', 'neutral').upper()}
• Volume Ratio: {volume_data.get('volume_ratio', 1.0):.1f}x
• Current Volume: {volume_data.get('current_volume', 0):,.0f}
• Trend: {volume_data.get('trend', 'neutral').upper()}"""
    
    def _format_sentiment_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Format sentiment analysis section"""
        sentiment_data = analysis_data.get('sentiment', {})
        
        return f"""• Long/Short Ratio: {sentiment_data.get('long_short_ratio', '50/50')}
• Funding Rate: {sentiment_data.get('funding_rate', 0.01):.4f}%
• Open Interest: {sentiment_data.get('oi_change', 'Stabil')}
• Market Fear/Greed: {sentiment_data.get('fear_greed', 'Neutral')}"""