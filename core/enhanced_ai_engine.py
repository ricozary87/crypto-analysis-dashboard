"""
Enhanced AI Engine - Professional Trading Analysis Narrative Generator
Integrated from OkxCandleTracker with existing system compatibility
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from openai import OpenAI

# Setup logging
logger = logging.getLogger(__name__)

class EnhancedAIEngine:
    """
    Enhanced AI Engine untuk menghasilkan narasi analitis profesional
    Menggunakan OpenAI GPT-4o dengan prompt engineering yang optimal
    Compatible dengan existing system architecture
    """
    
    def __init__(self):
        """Initialize Enhanced AI Engine with OpenAI client"""
        self.openai_client = None
        self.usage_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'last_request_time': None
        }
        
        # Initialize OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            try:
                self.openai_client = OpenAI(
                    api_key=openai_api_key,
                    timeout=30.0,
                    max_retries=2
                )
                logger.info("Enhanced AI Engine initialized with OpenAI GPT-4o")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            logger.warning("OPENAI_API_KEY not found - Enhanced AI Engine will use fallback narratives")
    
    def generate_enhanced_analysis(self, symbol: str, analysis_data: Dict[str, Any], 
                                  language: str = "indonesian", quick_mode: bool = False) -> str:
        """
        Generate comprehensive analysis narrative using enhanced AI engine
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC-USDT')
            analysis_data: Dictionary containing comprehensive analysis results
            language: Language for narrative ('indonesian' or 'english')
            quick_mode: Enable quick mode for faster response
            
        Returns:
            String containing professional analysis narrative
        """
        
        self.usage_stats['total_requests'] += 1
        self.usage_stats['last_request_time'] = datetime.now()
        
        if not self.openai_client:
            logger.warning("OpenAI client not available. Using enhanced fallback narrative.")
            return self._generate_enhanced_fallback(symbol, analysis_data, language)
        
        try:
            # Build enhanced prompt from analysis data
            prompt = self._build_enhanced_prompt(symbol, analysis_data, language, quick_mode)
            
            # Configure parameters based on mode
            max_tokens = 1000 if quick_mode else 2000
            system_prompt = self._get_enhanced_system_prompt(language)
            
            # Generate analysis using OpenAI GPT-4o
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.4,
                top_p=0.95,
                frequency_penalty=0.1,
                presence_penalty=0.0
            )
            
            narrative = response.choices[0].message.content.strip()
            
            # Update usage statistics
            self.usage_stats['successful_requests'] += 1
            self.usage_stats['total_tokens'] += response.usage.total_tokens
            
            # Validate response
            if not narrative or len(narrative) < 10:
                logger.warning(f"Empty or too short AI response for {symbol}")
                return self._generate_enhanced_fallback(symbol, analysis_data, language)
            
            logger.info(f"Enhanced AI narrative generated successfully for {symbol}")
            return narrative
            
        except Exception as e:
            logger.error(f"Enhanced AI engine error for {symbol}: {str(e)}")
            self.usage_stats['failed_requests'] += 1
            return self._generate_enhanced_fallback(symbol, analysis_data, language)
    
    def _build_enhanced_prompt(self, symbol: str, analysis_data: Dict[str, Any], 
                              language: str, quick_mode: bool) -> str:
        """Build enhanced prompt from analysis data"""
        
        # Extract key analysis components
        smc_analysis = analysis_data.get('smc_analysis', {})
        technical_indicators = analysis_data.get('indicators', {})
        signals = analysis_data.get('signals', {})
        confluence = analysis_data.get('confluence', {})
        
        # Get current price
        current_price = analysis_data.get('current_price', 0)
        
        # Build comprehensive prompt
        if quick_mode:
            prompt = f"""
=== QUICK ANALYSIS REQUEST ===

**{symbol.upper()} Analysis**
**Price: ${current_price:,.2f}**
**Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**

Market Structure: {smc_analysis.get('market_structure', {}).get('trend', 'neutral')}
RSI: {technical_indicators.get('rsi', {}).get('value', 'N/A')}
EMA Trend: {technical_indicators.get('ema', {}).get('trend', 'N/A')}
Volume: {technical_indicators.get('volume', {}).get('current', 'N/A')}
Signal: {signals.get('action', 'HOLD')}
Confidence: {signals.get('confidence', 0):.1f}%

Berikan analisis singkat dalam bahasa {language} yang mencakup:
1. Kondisi pasar saat ini
2. Level-level penting
3. Bias trading
4. Risk management
"""
        else:
            prompt = f"""
=== COMPREHENSIVE ANALYSIS REQUEST ===

**{symbol.upper()} Professional Analysis**
**Current Price: ${current_price:,.2f}**
**Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**

## Smart Money Concepts Analysis
Market Structure: {smc_analysis.get('market_structure', {}).get('trend', 'neutral')}
Swing Points: {len(smc_analysis.get('swing_points', {}).get('swing_highs', []))} highs, {len(smc_analysis.get('swing_points', {}).get('swing_lows', []))} lows
SMC Patterns: {smc_analysis.get('smc_summary', {})}

## Technical Indicators
RSI: {technical_indicators.get('rsi', {}).get('value', 'N/A')} ({"Overbought" if technical_indicators.get('rsi', {}).get('overbought') else "Oversold" if technical_indicators.get('rsi', {}).get('oversold') else "Normal"})
EMA Trend: {technical_indicators.get('ema', {}).get('trend', 'N/A')}
MACD: {technical_indicators.get('macd', {}).get('macd', 'N/A')} ({"Bullish" if technical_indicators.get('macd', {}).get('bullish') else "Bearish"})
Volume: {technical_indicators.get('volume', {}).get('current', 'N/A')} ({"Above Average" if technical_indicators.get('volume', {}).get('above_average') else "Below Average"})

## Trading Signals
Action: {signals.get('action', 'HOLD')}
Confidence: {signals.get('confidence', 0):.1f}%
Entry Price: {signals.get('entry_price', 'N/A')}
Stop Loss: {signals.get('stop_loss', 'N/A')}
Take Profit: {signals.get('take_profit', 'N/A')}

## Confluence Analysis
Level: {confluence.get('confluence_level', 'N/A')}
Score: {confluence.get('confluence_score', 0):.2f}
Supporting Indicators: {confluence.get('supporting_indicators', [])}

Berikan analisis komprehensif dalam bahasa {language} yang mencakup:
1. Executive Summary & Market Bias
2. Smart Money Concepts Analysis
3. Technical Indicators Breakdown
4. Trading Strategy & Levels
5. Risk Management & Scenarios
6. Key Levels & Zones
"""
        
        return prompt
    
    def _get_enhanced_system_prompt(self, language: str) -> str:
        """Get enhanced system prompt based on language"""
        
        if language == "english":
            return """
You are a professional cryptocurrency technical analyst with 10+ years of experience in financial markets.

MAIN TASKS:
- Explain market conditions based on multi-layer technical analysis (SMC, volume, indicators, confluence)
- Provide informative, analytical, and high-quality narratives
- Explain market direction and potential movements even when signals are not yet formed
- Focus on deep observations and professional trader preparation

ANALYSIS PRINCIPLES:
✅ DO:
• Explain market direction based on technical confluence
• Analyze important zones and critical levels
• Provide multiple scenarios (bullish/bearish/neutral)
• Focus on risk management and probabilities
• Use proper technical terminology
• Provide deep insights about market conditions

❌ DON'T:
• Force fake BUY/SELL signals
• Give direct trading recommendations
• Use overly confident language without basis
• Ignore risks or uncertainty

COMMUNICATION STYLE:
- Professional and easy to understand English
- Logical and systematic structure
- Use bullet points and clean formatting
- Provide clear reasoning for each analysis
- Focus on actionable insights

NARRATIVE STRUCTURE:
1. Executive Summary (main bias and confidence level)
2. Multi-Layer Analysis (SMC, Volume, Indicators, Confluence)
3. Trading Scenarios (conditions, entry zones, risk management)
4. Key Levels and Important Zones
5. Risk Assessment and Market Context
"""
        else:
            return """
Anda adalah analis teknikal crypto profesional dengan pengalaman 10+ tahun di pasar finansial.

TUGAS UTAMA:
- Menjelaskan kondisi pasar berdasarkan analisa teknikal multi-layer (SMC, volume, indikator, konfluensi)
- Memberikan narasi yang informatif, analitis, dan berkualitas tinggi
- Tetap menjelaskan arah pasar dan potensi pergerakan meski sinyal belum terbentuk
- Fokus pada observasi mendalam dan persiapan trader profesional

PRINSIP ANALISIS:
✅ LAKUKAN:
• Jelaskan arah pasar berdasarkan konfluensi teknikal
• Analisis zona-zona penting dan level kritis
• Berikan perspektif berbagai skenario (bullish/bearish/neutral)
• Fokus pada risk management dan probabilitas
• Gunakan terminologi teknikal yang tepat
• Berikan insight mendalam tentang kondisi pasar

❌ JANGAN:
• Memaksakan sinyal BUY/SELL palsu
• Memberikan rekomendasi trading langsung
• Menggunakan bahasa yang terlalu yakin tanpa basis
• Mengabaikan risiko atau uncertainty

GAYA KOMUNIKASI:
- Bahasa Indonesia profesional dan mudah dipahami
- Struktur yang logis dan sistematis
- Gunakan bullet points dan formatting yang rapi
- Berikan reasoning yang jelas untuk setiap analisis
- Fokus pada actionable insights

STRUKTUR NARASI:
1. Executive Summary (bias utama dan confidence level)
2. Analisis Multi-Layer (SMC, Volume, Indikator, Konfluensi)
3. Skenario Trading (kondisi, entry zones, risk management)
4. Key Levels dan Zona Penting
5. Risk Assessment dan Market Context
"""
    
    def _generate_enhanced_fallback(self, symbol: str, analysis_data: Dict[str, Any], 
                                   language: str) -> str:
        """Generate enhanced fallback narrative when AI is unavailable"""
        
        current_price = analysis_data.get('current_price', 0)
        signals = analysis_data.get('signals', {})
        smc_analysis = analysis_data.get('smc_analysis', {})
        indicators = analysis_data.get('indicators', {})
        
        if language == "english":
            return f"""
📊 **TECHNICAL ANALYSIS - {symbol.upper()}**
{'='*50}

💰 **Current Price:** ${current_price:,.2f}
📈 **Signal:** {signals.get('action', 'HOLD')}
🎯 **Confidence:** {signals.get('confidence', 0):.1f}%

**Market Structure Analysis:**
• Trend: {smc_analysis.get('market_structure', {}).get('trend', 'Neutral')}
• RSI: {indicators.get('rsi', {}).get('value', 'N/A')}
• EMA Trend: {indicators.get('ema', {}).get('trend', 'N/A')}
• Volume: {indicators.get('volume', {}).get('current', 'N/A')}

**Professional Analysis:**
Market is currently showing {smc_analysis.get('market_structure', {}).get('trend', 'neutral')} bias with {signals.get('action', 'HOLD')} recommendation at {signals.get('confidence', 0):.1f}% confidence level.

**Key Levels:**
• Entry: {signals.get('entry_price', 'N/A')}
• Stop Loss: {signals.get('stop_loss', 'N/A')}
• Take Profit: {signals.get('take_profit', 'N/A')}

**Risk Management:**
Please monitor key support/resistance levels and manage position sizing accordingly.

⚠️ **Note:** Enhanced AI analysis temporarily unavailable. Using fallback analysis.

📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} UTC
"""
        else:
            return f"""
📊 **ANALISIS TEKNIKAL - {symbol.upper()}**
{'='*50}

💰 **Harga Saat Ini:** ${current_price:,.2f}
📈 **Sinyal:** {signals.get('action', 'HOLD')}
🎯 **Confidence:** {signals.get('confidence', 0):.1f}%

**Analisis Struktur Pasar:**
• Trend: {smc_analysis.get('market_structure', {}).get('trend', 'Netral')}
• RSI: {indicators.get('rsi', {}).get('value', 'N/A')}
• EMA Trend: {indicators.get('ema', {}).get('trend', 'N/A')}
• Volume: {indicators.get('volume', {}).get('current', 'N/A')}

**Analisis Profesional:**
Pasar saat ini menunjukkan bias {smc_analysis.get('market_structure', {}).get('trend', 'netral')} dengan rekomendasi {signals.get('action', 'HOLD')} pada tingkat confidence {signals.get('confidence', 0):.1f}%.

**Level-Level Penting:**
• Entry: {signals.get('entry_price', 'N/A')}
• Stop Loss: {signals.get('stop_loss', 'N/A')}
• Take Profit: {signals.get('take_profit', 'N/A')}

**Risk Management:**
Mohon pantau level support/resistance penting dan kelola ukuran posisi sesuai dengan risk tolerance.

⚠️ **Catatan:** Analisis AI Enhanced sementara tidak tersedia. Menggunakan analisis fallback.

📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} WIB
"""
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get AI engine usage statistics"""
        return {
            'total_requests': self.usage_stats['total_requests'],
            'successful_requests': self.usage_stats['successful_requests'],
            'failed_requests': self.usage_stats['failed_requests'],
            'success_rate': (self.usage_stats['successful_requests'] / max(1, self.usage_stats['total_requests'])) * 100,
            'total_tokens': self.usage_stats['total_tokens'],
            'last_request_time': self.usage_stats['last_request_time'],
            'ai_available': self.openai_client is not None
        }
    
    def test_ai_connection(self) -> Dict[str, Any]:
        """Test AI connection and return status"""
        if not self.openai_client:
            return {
                'status': 'unavailable',
                'message': 'OpenAI client not initialized',
                'ai_available': False
            }
        
        try:
            # Test with simple request
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'AI connection test successful'"}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            return {
                'status': 'connected',
                'message': 'AI connection test successful',
                'ai_available': True,
                'response': response.choices[0].message.content.strip()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'AI connection test failed: {str(e)}',
                'ai_available': False
            }