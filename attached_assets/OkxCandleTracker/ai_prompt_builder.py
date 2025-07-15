"""
AI Prompt Builder - Professional Trading Analysis Prompt Generator
Mengubah hasil analisa internal menjadi prompt teks siap kirim ke OpenAI GPT
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime


class AIPromptBuilder:
    """
    Kelas untuk membentuk prompt AI yang komprehensif dari hasil analisis teknikal 7 layer
    """
    
    def __init__(self):
        self.system_prompt = """
Anda adalah analis trading profesional dengan keahlian dalam:
- Smart Money Concepts (SMC)
- Volume Profile Analysis
- Orderbook & Market Microstructure
- Technical Indicators (RSI, EMA, MACD)
- Fibonacci Analysis
- Open Interest & Funding Rate Analysis
- Risk Management & Position Sizing

Berikan analisis yang:
✅ Faktual dan berdasarkan data
✅ Menggunakan terminologi trading yang tepat
✅ Memberikan level-level konkret
✅ Menyertakan skenario utama dan alternatif
✅ Professional dan actionable
"""
    
    def build_ai_analysis_prompt(self, symbol: str, timeframe: str, analysis_result: Dict[str, Any]) -> str:
        """
        Menerima hasil analisa (dict) dan membentuk prompt teks untuk GPT.
        
        Args:
            symbol: Trading pair (e.g., "BTC-USDT")
            timeframe: Time frame (e.g., "5m", "1h")
            analysis_result: Dictionary berisi hasil analisis 7 layer
            
        Returns:
            String prompt yang siap dikirim ke OpenAI
        """
        
        # Extract analysis data with fallbacks
        smc = self._extract_smc_data(analysis_result.get("smc_analysis", {}))
        cvd = self._extract_volume_data(analysis_result.get("volume_analysis", {}))
        vprofile = self._extract_volume_profile(analysis_result.get("volume_analysis", {}))
        orderbook = self._extract_orderbook_data(analysis_result.get("orderbook_analysis", {}))
        rsi_ema = self._extract_rsi_ema_data(analysis_result.get("rsi_ema_analysis", {}))
        fibo = self._extract_fibonacci_data(analysis_result.get("fibonacci_analysis", {}))
        oi_funding = self._extract_oi_funding_data(analysis_result.get("oi_funding_analysis", {}))
        
        # Get current price for context
        current_price = self._get_current_price(analysis_result)
        
        # Build comprehensive prompt
        prompt = f"""
=== TRADING SNAPSHOT ANALYSIS REQUEST ===

**ANALISIS MENDALAM {symbol.upper()} (Timeframe: {timeframe})**
**Current Price: ${current_price}**
**Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC**

Berdasarkan data teknikal berikut, berikan analisis trading profesional:

## 1. 📘 Smart Money Concept (SMC)
{smc}

## 2. 📊 Volume Delta (CVD) & Volume Analysis
{cvd}

## 3. 📈 Volume Profile
{vprofile}

## 4. 🧱 Orderbook & Market Depth
{orderbook}

## 5. 📏 RSI & EMA Confluence
{rsi_ema}

## 6. 🔺 Fibonacci Levels
{fibo}

## 7. 🧮 Open Interest & Funding Rate
{oi_funding}

---

## 🎯 INSTRUKSI ANALISIS:

Berikan analisis profesional dalam bahasa Indonesia yang mencakup:

### A. Executive Summary
- Bias utama (bullish/bearish/neutral) dengan reasoning
- Confidence level (1-5 🔵) berdasarkan confluence

### B. Key Levels & Zones
- Support dan resistance utama
- FVG (Fair Value Gap) penting
- Fibonacci retracement/extension levels
- SMC zones (Order Blocks, Breaker Blocks)

### C. Market Structure Analysis
- Trend saat ini (Higher High/Lower Low pattern)
- Market phase (accumulation/distribution/markup/markdown)
- Volume confirmation atau divergence

### D. Trading Scenarios

**Skenario Utama:**
- Kondisi yang harus dipenuhi
- Entry strategy dan timing
- Stop Loss placement
- Take Profit targets (TP1, TP2)
- Risk/Reward ratio

**Skenario Alternatif:**
- Kondisi invalidasi skenario utama
- Backup plan dan levels
- Risk management adjustments

### E. Risk Assessment
- Faktor risiko utama
- Market sentiment risks
- Technical risks
- Recommended position size

### F. Execution Notes
- Best entry approach (market/limit order)
- Monitoring points
- Exit strategy refinements
- Time-based considerations

**Format:** Gunakan markdown formatting yang rapi dengan bullet points dan emoji yang sesuai.
**Tone:** Professional trading analyst, factual, actionable.
**Length:** Komprehensif namun concise, fokus pada actionable insights.

=== END ANALYSIS REQUEST ===
"""
        
        return prompt.strip()
    
    def _extract_smc_data(self, smc_analysis: Dict[str, Any]) -> str:
        """Extract SMC analysis data"""
        if not smc_analysis:
            return "Data SMC tidak tersedia untuk analisis."
        
        signal = smc_analysis.get('signal', 'neutral')
        strength = smc_analysis.get('strength', 0)
        description = smc_analysis.get('description', 'No description')
        structure = smc_analysis.get('market_structure', 'undefined')
        key_levels = smc_analysis.get('key_levels', [])
        
        smc_text = f"""
📊 Signal: {signal.upper()} (Strength: {strength:.1f}%)
📈 Market Structure: {structure}
🎯 Key Levels: {len(key_levels)} order blocks identified
💡 Analysis: {description}
"""
        
        if key_levels:
            smc_text += "\n🔍 Order Blocks:\n"
            for level in key_levels[:3]:  # Top 3 levels
                smc_text += f"   - {level.get('type', 'OB')} at ${level.get('level', 0):.4f} (Strength: {level.get('strength', 0):.1f}%)\n"
        
        return smc_text.strip()
    
    def _extract_volume_data(self, volume_analysis: Dict[str, Any]) -> str:
        """Extract volume and CVD data"""
        if not volume_analysis:
            return "Data volume tidak tersedia untuk analisis CVD."
        
        signal = volume_analysis.get('signal', 'neutral')
        strength = volume_analysis.get('strength', 0)
        cvd = volume_analysis.get('cvd', 0)
        volume_spike = volume_analysis.get('volume_spike', False)
        description = volume_analysis.get('description', 'No description')
        
        volume_text = f"""
📊 Volume Signal: {signal.upper()} (Strength: {strength:.1f}%)
📈 Cumulative Volume Delta: {cvd:,.0f}
🔥 Volume Spike: {'Yes' if volume_spike else 'No'}
💡 Analysis: {description}
"""
        
        return volume_text.strip()
    
    def _extract_volume_profile(self, volume_analysis: Dict[str, Any]) -> str:
        """Extract volume profile data"""
        volume_profile = volume_analysis.get('volume_profile', {})
        if not volume_profile:
            return "Volume profile data tidak tersedia."
        
        return f"""
📊 Volume Profile: {volume_profile.get('dominant_zone', 'Balanced')}
🎯 POC (Point of Control): ${volume_profile.get('poc', 0):.4f}
📈 Value Area: ${volume_profile.get('value_area_high', 0):.4f} - ${volume_profile.get('value_area_low', 0):.4f}
"""
    
    def _extract_orderbook_data(self, orderbook_analysis: Dict[str, Any]) -> str:
        """Extract orderbook analysis data"""
        if not orderbook_analysis:
            return "Data orderbook tidak tersedia untuk analisis."
        
        signal = orderbook_analysis.get('signal', 'neutral')
        strength = orderbook_analysis.get('strength', 0)
        imbalance = orderbook_analysis.get('imbalance', 0)
        description = orderbook_analysis.get('description', 'No description')
        
        orderbook_text = f"""
📊 Orderbook Signal: {signal.upper()} (Strength: {strength:.1f}%)
⚖️ Bid/Ask Imbalance: {imbalance:+.1f}%
💡 Analysis: {description}
"""
        
        return orderbook_text.strip()
    
    def _extract_rsi_ema_data(self, rsi_ema_analysis: Dict[str, Any]) -> str:
        """Extract RSI and EMA confluence data"""
        if not rsi_ema_analysis:
            return "Data RSI/EMA tidak tersedia untuk analisis."
        
        signal = rsi_ema_analysis.get('signal', 'neutral')
        strength = rsi_ema_analysis.get('strength', 0)
        rsi_value = rsi_ema_analysis.get('rsi_value', 50)
        rsi_condition = rsi_ema_analysis.get('rsi_condition', 'neutral')
        ema_trend = rsi_ema_analysis.get('ema_trend', 'sideways')
        description = rsi_ema_analysis.get('description', 'No description')
        
        rsi_ema_text = f"""
📊 RSI/EMA Signal: {signal.upper()} (Strength: {strength:.1f}%)
📏 RSI Value: {rsi_value:.1f} ({rsi_condition})
📈 EMA Trend: {ema_trend}
💡 Analysis: {description}
"""
        
        return rsi_ema_text.strip()
    
    def _extract_fibonacci_data(self, fibonacci_analysis: Dict[str, Any]) -> str:
        """Extract Fibonacci analysis data"""
        if not fibonacci_analysis:
            return "Data Fibonacci tidak tersedia untuk analisis."
        
        signal = fibonacci_analysis.get('signal', 'neutral')
        strength = fibonacci_analysis.get('strength', 0)
        current_zone = fibonacci_analysis.get('current_zone', 'undefined')
        key_levels = fibonacci_analysis.get('key_levels', [])
        description = fibonacci_analysis.get('description', 'No description')
        
        fibo_text = f"""
📊 Fibonacci Signal: {signal.upper()} (Strength: {strength:.1f}%)
🎯 Current Zone: {current_zone}
📏 Key Levels: {len(key_levels)} levels identified
💡 Analysis: {description}
"""
        
        if key_levels:
            fibo_text += "\n🔍 Key Fibonacci Levels:\n"
            for level in key_levels[:3]:  # Top 3 levels
                fibo_text += f"   - {level.get('level', 0):.1f}% at ${level.get('price', 0):.4f}\n"
        
        return fibo_text.strip()
    
    def _extract_oi_funding_data(self, oi_funding_analysis: Dict[str, Any]) -> str:
        """Extract Open Interest and Funding Rate data"""
        if not oi_funding_analysis:
            return "Data Open Interest/Funding tidak tersedia untuk analisis."
        
        signal = oi_funding_analysis.get('signal', 'neutral')
        strength = oi_funding_analysis.get('strength', 0)
        oi_trend = oi_funding_analysis.get('oi_trend', 'stable')
        funding_rate = oi_funding_analysis.get('funding_rate', 0)
        description = oi_funding_analysis.get('description', 'No description')
        
        oi_funding_text = f"""
📊 OI/Funding Signal: {signal.upper()} (Strength: {strength:.1f}%)
📈 OI Trend: {oi_trend}
💰 Funding Rate: {funding_rate:.4f}%
💡 Analysis: {description}
"""
        
        return oi_funding_text.strip()
    
    def _get_current_price(self, analysis_result: Dict[str, Any]) -> str:
        """Extract current price from analysis result"""
        candlestick_data = analysis_result.get('candlestick', [])
        if candlestick_data:
            return f"{candlestick_data[-1].get('close', 0):.4f}"
        return "N/A"
    
    def build_quick_prompt(self, symbol: str, timeframe: str, key_data: Dict[str, Any]) -> str:
        """
        Build a quick prompt for faster analysis with essential data only
        """
        prompt = f"""
Quick Analysis Request for {symbol.upper()} ({timeframe}):

Current Price: ${key_data.get('current_price', 'N/A')}
SMC Bias: {key_data.get('smc_signal', 'neutral')}
Volume: {key_data.get('volume_signal', 'neutral')}
RSI: {key_data.get('rsi_value', 50)}
EMA Trend: {key_data.get('ema_trend', 'sideways')}

Berikan analisis singkat dalam bahasa Indonesia:
1. Bias utama (bullish/bearish/neutral) dengan reasoning
2. Entry level yang optimal 
3. Stop loss dan take profit
4. Risk/reward ratio
5. Confidence level (1-5)

Format: Bullet points, maksimal 200 kata, professional tone.
"""
        return prompt.strip()
    
    def build_ultra_quick_prompt(self, symbol: str, timeframe: str, confluence_data: Dict[str, Any]) -> str:
        """
        Build ultra-quick prompt for fastest response (under 10 seconds)
        """
        signal = confluence_data.get('overall_signal', 'neutral')
        consensus = confluence_data.get('consensus_level', 0)
        current_price = confluence_data.get('current_price', 'N/A')
        
        prompt = f"""
Ultra-Quick Analysis untuk {symbol.upper()} ({timeframe}):

Signal: {signal.upper()}
Consensus Level: {consensus:.1f}
Current Price: ${current_price}

Berikan analisis singkat dalam bahasa Indonesia (maksimal 100 kata):
• Bias utama dan reasoning
• Entry point optimal
• Stop loss dan take profit
• Confidence level (1-5 🔵)

Format: Bullet points, actionable insights only.
"""
        return prompt.strip()


# Convenience functions for easy integration
def build_ai_analysis_prompt(symbol: str, timeframe: str, analysis_result: Dict[str, Any]) -> str:
    """
    Convenience function for building AI analysis prompt
    """
    builder = AIPromptBuilder()
    return builder.build_ai_analysis_prompt(symbol, timeframe, analysis_result)


def build_quick_prompt(symbol: str, timeframe: str, key_data: Dict[str, Any]) -> str:
    """
    Convenience function for building quick analysis prompt
    """
    builder = AIPromptBuilder()
    return builder.build_quick_prompt(symbol, timeframe, key_data)