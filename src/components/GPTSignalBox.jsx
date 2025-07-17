import React, { useState, useEffect } from 'react';
import { analysisAPI } from '../services/api';

const GPTSignalBox = ({ pair, tf }) => {
  const [aiData, setAiData] = useState({
    bias: 'Neutral',
    entry: 0,
    sl: 0,
    tp: 0,
    confidence: 0,
    narasi: 'Loading AI analysis...'
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showNarrative, setShowNarrative] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    // Reset state when pair changes
    setAiData({
      bias: 'Neutral',
      entry: 0,
      sl: 0,
      tp: 0,
      confidence: 0,
      narasi: 'Loading AI analysis...'
    });
    setError(null);
    setIsLoading(true);
    setShowNarrative(false);
    
    fetchAIAnalysis();
  }, [pair, tf]);

  const fetchAIAnalysis = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Convert pair format (BTC/USDT -> BTC)
      const symbol = pair.split('/')[0];
      
      const response = await analysisAPI.getAIAnalysis(symbol);
      
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
    } catch (error) {
      console.error('Error fetching AI analysis:', error);
      setError(error.message);
      
      // Retry logic for certain errors
      if (retryCount < 3 && (error.message.includes('503') || error.message.includes('timeout'))) {
        setRetryCount(prev => prev + 1);
        setTimeout(() => fetchAIAnalysis(), 2000 * (retryCount + 1));
      } else {
        setAiData({
          bias: 'Error',
          entry: 0,
          sl: 0,
          tp: 0,
          confidence: 0,
          narasi: 'Failed to load AI analysis. Please try again.'
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const calculateRR = () => {
    if (aiData.entry > 0 && aiData.sl > 0 && aiData.tp > 0) {
      const risk = Math.abs(aiData.entry - aiData.sl);
      const reward = Math.abs(aiData.tp - aiData.entry);
      return (reward / risk).toFixed(2);
    }
    return '0.00';
  };

  const getBiasIcon = () => {
    switch (aiData.bias.toLowerCase()) {
      case 'bullish':
        return '📈';
      case 'bearish':
        return '📉';
      default:
        return '➖';
    }
  };

  const getBiasColor = () => {
    switch (aiData.bias.toLowerCase()) {
      case 'bullish':
        return 'text-green-400';
      case 'bearish':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-white font-semibold flex items-center gap-2">
          <span className="text-purple-400">🤖</span>
          AI Trading Plan
        </h3>
        {isLoading && (
          <div className="text-xs text-gray-400">
            Loading{retryCount > 0 && ` (Retry ${retryCount}/3)`}...
          </div>
        )}
      </div>

      {error && !isLoading && (
        <div className="text-xs text-red-400 mb-2">
          Error: {error}
        </div>
      )}

      <div className="space-y-2">
        {/* Bias */}
        <div className="flex justify-between items-center">
          <span className="text-gray-400 text-sm">Market Bias:</span>
          <span className={`font-semibold ${getBiasColor()}`}>
            {getBiasIcon()} {aiData.bias}
          </span>
        </div>

        {/* Entry, SL, TP */}
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div className="bg-gray-700 rounded p-2">
            <div className="text-gray-400">Entry</div>
            <div className="text-white font-medium">
              ${aiData.entry.toLocaleString()}
            </div>
          </div>
          <div className="bg-gray-700 rounded p-2">
            <div className="text-gray-400">Stop Loss</div>
            <div className="text-red-400 font-medium">
              ${aiData.sl.toLocaleString()}
            </div>
          </div>
          <div className="bg-gray-700 rounded p-2">
            <div className="text-gray-400">Take Profit</div>
            <div className="text-green-400 font-medium">
              ${aiData.tp.toLocaleString()}
            </div>
          </div>
        </div>

        {/* R:R Ratio */}
        <div className="flex justify-between items-center">
          <span className="text-gray-400 text-sm">Risk:Reward</span>
          <span className="text-yellow-400 font-semibold">
            1:{calculateRR()}
          </span>
        </div>

        {/* Confidence Bar */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-gray-400 text-sm">Confidence</span>
            <span className="text-white text-sm">{aiData.confidence}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-purple-500 to-purple-400 h-2 rounded-full transition-all duration-300"
              style={{ width: `${aiData.confidence}%` }}
            />
          </div>
        </div>

        {/* AI Narrative Toggle */}
        <button
          onClick={() => setShowNarrative(!showNarrative)}
          className="w-full mt-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-300 transition-colors"
        >
          {showNarrative ? 'Hide' : 'Show'} AI Analysis
        </button>

        {/* AI Narrative */}
        {showNarrative && (
          <div className="mt-3 p-3 bg-gray-700 rounded text-xs text-gray-300 max-h-40 overflow-y-auto">
            {aiData.narasi}
          </div>
        )}
      </div>
    </div>
  );
};

export default GPTSignalBox;