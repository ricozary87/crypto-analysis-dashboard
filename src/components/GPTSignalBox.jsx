import React, { useState, useEffect } from 'react';
import { analysisAPI } from '../services/api';

const GPTSignalBox = ({ 
  pair = 'SOL/USDT',
  tf = '1H'
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copyText, setCopyText] = useState('Copy Plan');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  
  // State untuk data AI Trading Plan
  const [aiData, setAiData] = useState({
    bias: 'Neutral',
    entry: 0,
    sl: 0,
    tp: 0,
    confidence: 0,
    narasi: 'Menunggu analisis...'
  });

  // Fetch AI analysis dengan retry mechanism
  const fetchAIAnalysis = async (attempt = 0) => {
    if (attempt === 0) {
      setIsLoading(true);
      setError(null);
    }

    try {
      const symbol = pair.replace('/', '-'); // Convert BTC/USDT to BTC-USDT
      
      // Fetch AI analysis from backend
      const response = await analysisAPI.getAIAnalysis(symbol, 'comprehensive');
      
      if (response && response.analysis) {
        // Parse response and extract trading plan
        const analysis = response.analysis;
        
        setAiData({
          bias: analysis.bias || 'Neutral',
          entry: analysis.entry_price || 0,
          sl: analysis.stop_loss || 0,
          tp: analysis.take_profit || 0,
          confidence: analysis.confidence || 0,
          narasi: analysis.narrative || 'Analisis tidak tersedia'
        });
        
        setRetryCount(0);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      console.error(`AI Analysis error (attempt ${attempt + 1}):`, err);
      
      // Retry logic untuk 503 dan timeout errors
      if (attempt < 3 && (err.message.includes('503') || err.message.includes('timeout'))) {
        setRetryCount(attempt + 1);
        setTimeout(() => fetchAIAnalysis(attempt + 1), 2000 * (attempt + 1)); // Exponential backoff
      } else {
        setError(err.message);
        setAiData({
          bias: 'Error',
          entry: 0,
          sl: 0,
          tp: 0,
          confidence: 0,
          narasi: `Gagal mendapatkan analisis: ${err.message}`
        });
      }
    } finally {
      if (attempt === 0) {
        setIsLoading(false);
      }
    }
  };

  // Effect untuk auto-update saat pair berubah
  useEffect(() => {
    // Reset state sebelum fetch untuk menghindari ghost data
    setAiData({
      bias: 'Loading...',
      entry: 0,
      sl: 0,
      tp: 0,
      confidence: 0,
      narasi: 'Mengambil data analisis...'
    });
    
    fetchAIAnalysis();
  }, [pair, tf]); // Trigger saat pair atau timeframe berubah

  const getBiasColor = () => {
    if (aiData.bias.toLowerCase() === 'bullish') return 'text-green-400';
    if (aiData.bias.toLowerCase() === 'bearish') return 'text-red-400';
    return 'text-gray-400';
  };

  const getConfidenceColor = () => {
    if (aiData.confidence >= 80) return 'bg-green-500';
    if (aiData.confidence >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const calculateRR = () => {
    const risk = Math.abs(aiData.entry - aiData.sl);
    const reward = Math.abs(aiData.tp - aiData.entry);
    return risk > 0 ? (reward / risk).toFixed(2) : '0.00';
  };

  const handleCopyPlan = () => {
    const tradingPlan = `📊 Trading Plan - ${pair} ${tf}
📈 Bias: ${aiData.bias}
💰 Entry: $${aiData.entry.toFixed(2)}
🛡️ SL: $${aiData.sl.toFixed(2)}
🎯 TP: $${aiData.tp.toFixed(2)}
📏 RR: 1:${calculateRR()}
🎯 Confidence: ${aiData.confidence}%

📝 AI Analysis:
${aiData.narasi}`;

    navigator.clipboard.writeText(tradingPlan);
    setCopyText('Copied! ✅');
    setTimeout(() => setCopyText('Copy Plan'), 2000);
  };

  const truncateNarasi = (text, maxLines = 3) => {
    const words = text.split(' ');
    const wordsPerLine = 10;
    const maxWords = wordsPerLine * maxLines;
    
    if (words.length <= maxWords || isExpanded) {
      return text;
    }
    
    return words.slice(0, maxWords).join(' ') + '...';
  };

  // Manual refresh function
  const handleRefresh = () => {
    fetchAIAnalysis();
  };

  return (
    <div className="bg-gray-900/90 backdrop-blur rounded-xl p-5 border border-gray-800 hover:border-gray-700 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold text-white">AI Trading Plan</h3>
          <span className="text-sm px-3 py-1 rounded-full bg-gray-800 text-gray-400">
            {pair} • {tf}
          </span>
          {/* Refresh button */}
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="text-gray-400 hover:text-white transition-colors"
            title="Refresh Analysis"
          >
            <div className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`}>
              🔄
            </div>
          </button>
        </div>
        <div className={`text-lg font-bold ${getBiasColor()}`}>
          {aiData.bias === 'Bullish' ? '📈' : aiData.bias === 'Bearish' ? '📉' : '➖'} {aiData.bias}
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-2 text-gray-400">
            {retryCount > 0 ? `Retry ${retryCount}/3...` : 'Menganalisis...'}
          </span>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-700 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-red-400 text-sm">❌ {error}</span>
            <button
              onClick={handleRefresh}
              className="text-red-400 hover:text-red-300 text-sm"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Content - Hidden saat loading */}
      {!isLoading && (
        <>

        {/* Trading Levels */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="bg-gray-800/50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-400 mb-1">Entry</div>
            <div className="text-lg font-bold text-blue-400">${aiData.entry.toFixed(2)}</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-400 mb-1">Stop Loss</div>
            <div className="text-lg font-bold text-red-400">${aiData.sl.toFixed(2)}</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-400 mb-1">Take Profit</div>
            <div className="text-lg font-bold text-green-400">${aiData.tp.toFixed(2)}</div>
          </div>
        </div>

      {/* Risk Reward */}
      <div className="mb-4 p-3 bg-gray-800/30 rounded-lg">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-gray-400">Risk/Reward Ratio</span>
          <span className="font-semibold text-white">1 : {calculateRR()}</span>
        </div>
      </div>

        {/* Confidence Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-gray-400">AI Confidence</span>
            <span className="font-semibold text-white">{aiData.confidence}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
            <div 
              className={`h-full ${getConfidenceColor()} transition-all duration-500`}
              style={{ width: `${aiData.confidence}%` }}
            />
          </div>
        </div>

        {/* AI Narasi */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">AI Analysis</span>
            {aiData.narasi.split(' ').length > 30 && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-xs text-blue-400 hover:text-blue-300"
              >
                {isExpanded ? 'Show less' : 'Show more'}
              </button>
            )}
          </div>
          <p className="text-sm text-gray-300 leading-relaxed">
            {truncateNarasi(aiData.narasi)}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <button
            onClick={handleCopyPlan}
            className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all duration-200 hover:scale-105"
          >
            {copyText}
          </button>
          <button
            className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition-all duration-200 hover:scale-105"
          >
            Lihat di Chart
          </button>
        </div>
      )}
    </div>
  );
};

export default GPTSignalBox;
