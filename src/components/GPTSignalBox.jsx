import React, { useState } from 'react';

const GPTSignalBox = ({ 
  pair = 'SOL/USDT',
  tf = '1H',
  bias = 'Bullish',
  entry = 147.20,
  sl = 144.80,
  tp = 152.90,
  confidence = 87,
  narasi = 'Market menunjukkan BOS kuat di 1H, valid CHoCH di 5m...'
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copyText, setCopyText] = useState('Copy Plan');

  const getBiasColor = () => {
    if (bias.toLowerCase() === 'bullish') return 'text-green-400';
    if (bias.toLowerCase() === 'bearish') return 'text-red-400';
    return 'text-gray-400';
  };

  const getConfidenceColor = () => {
    if (confidence >= 80) return 'bg-green-500';
    if (confidence >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const calculateRR = () => {
    const risk = Math.abs(entry - sl);
    const reward = Math.abs(tp - entry);
    return (reward / risk).toFixed(2);
  };

  const handleCopyPlan = () => {
    const tradingPlan = `📊 Trading Plan - ${pair} ${tf}
📈 Bias: ${bias}
💰 Entry: $${entry.toFixed(2)}
🛡️ SL: $${sl.toFixed(2)}
🎯 TP: $${tp.toFixed(2)}
📏 RR: 1:${calculateRR()}
🎯 Confidence: ${confidence}%

📝 AI Analysis:
${narasi}`;

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

  return (
    <div className="bg-gray-900/90 backdrop-blur rounded-xl p-5 border border-gray-800 hover:border-gray-700 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold text-white">AI Trading Plan</h3>
          <span className="text-sm px-3 py-1 rounded-full bg-gray-800 text-gray-400">
            {pair} • {tf}
          </span>
        </div>
        <div className={`text-lg font-bold ${getBiasColor()}`}>
          {bias === 'Bullish' ? '📈' : '📉'} {bias}
        </div>
      </div>

      {/* Trading Levels */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-gray-800/50 rounded-lg p-3 text-center">
          <div className="text-xs text-gray-400 mb-1">Entry</div>
          <div className="text-lg font-bold text-blue-400">${entry.toFixed(2)}</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-3 text-center">
          <div className="text-xs text-gray-400 mb-1">Stop Loss</div>
          <div className="text-lg font-bold text-red-400">${sl.toFixed(2)}</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-3 text-center">
          <div className="text-xs text-gray-400 mb-1">Take Profit</div>
          <div className="text-lg font-bold text-green-400">${tp.toFixed(2)}</div>
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
          <span className="font-semibold text-white">{confidence}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
          <div 
            className={`h-full ${getConfidenceColor()} transition-all duration-500`}
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      {/* AI Narasi */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">AI Analysis</span>
          {narasi.split(' ').length > 30 && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-xs text-blue-400 hover:text-blue-300"
            >
              {isExpanded ? 'Show less' : 'Show more'}
            </button>
          )}
        </div>
        <p className="text-sm text-gray-300 leading-relaxed">
          {truncateNarasi(narasi)}
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
    </div>
  );
};

export default GPTSignalBox;