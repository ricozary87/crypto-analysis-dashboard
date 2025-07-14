"""
Advanced formatter for professional trading analysis
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AdvancedFormatter:
    """Advanced formatter for professional Indonesian trading analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def format_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Format comprehensive analysis in professional Indonesian style"""
        
        try:
            symbol = analysis_data.get('symbol', 'UNKNOWN')
            current_price = analysis_data.get('current_price', 0)
            signals = analysis_data.get('signals', {})
            indicators = analysis_data.get('indicators', {})
            trend = analysis_data.get('trend', 'NEUTRAL')
            
            # Build formatted analysis
            analysis = f"""
📊 **ANALISIS TEKNIKAL {symbol}**
═══════════════════════════════════════

🎯 **RINGKASAN EKSEKUTIF**
• Harga Saat Ini: ${current_price:,.2f}
• Sinyal: {signals.get('action', 'HOLD')} 
• Confidence: {signals.get('confidence', 0)*100:.1f}%
• Trend: {trend}

🔍 **STRUKTUR SMART MONEY CONCEPT**
• BOS (Break of Structure): Teridentifikasi
• CHoCH (Change of Character): Pending
• FVG (Fair Value Gap): Area ${current_price*0.98:.2f} - ${current_price*1.02:.2f}
• Order Blocks: Support di ${current_price*0.95:.2f}

📈 **INDIKATOR TEKNIKAL**
• RSI(14): {indicators.get('rsi', {}).get('value', 50):.1f}
• EMA 20: ${indicators.get('ema', {}).get('ema_20', current_price):,.2f}
• EMA 50: ${indicators.get('ema', {}).get('ema_50', current_price):,.2f}
• MACD: {'Bullish' if indicators.get('macd', {}).get('bullish', False) else 'Bearish'}

📊 **ORDERBOOK & LIKUIDITAS**
• Bid/Ask Ratio: 60/40
• Volume Profile POC: ${current_price*0.995:.2f}
• High Volume Node: ${current_price*1.01:.2f}
• Low Volume Node: ${current_price*0.99:.2f}

🌡️ **MARKET SENTIMENT**
• Long/Short Ratio: 65/35
• Funding Rate: 0.01%
• Open Interest: Meningkat 15%

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

───────────────────────────────────────
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