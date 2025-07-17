import React, { useState, useEffect } from 'react';
import { analysisAPI } from '../services/api';

const SignalSummaryBox = ({ pair, timeframe }) => {
  const [signalData, setSignalData] = useState({
    signals: [],
    totalSignals: 0,
    bullishSignals: 0,
    bearishSignals: 0,
    neutralSignals: 0,
    avgConfidence: 0
  });
  const [isLoading, setIsLoading] = useState(false);

  const fetchSignalSummary = async () => {
    setIsLoading(true);
    try {
      const symbol = pair.replace('/', '-');
      const response = await analysisAPI.getTradingSignals(symbol, 20);
      
      if (response && response.signals) {
        const signals = response.signals;
        const bullish = signals.filter(s => s.signal_type === 'BUY').length;
        const bearish = signals.filter(s => s.signal_type === 'SELL').length;
        const neutral = signals.filter(s => s.signal_type === 'HOLD').length;
        const totalConfidence = signals.reduce((sum, s) => sum + (s.confidence || 0), 0);
        
        setSignalData({
          signals,
          totalSignals: signals.length,
          bullishSignals: bullish,
          bearishSignals: bearish,
          neutralSignals: neutral,
          avgConfidence: signals.length > 0 ? (totalConfidence / signals.length) : 0
        });
      }
    } catch (error) {
      console.error('Error fetching signal summary:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSignalSummary();
  }, [pair, timeframe]);

  return (
    <div className="bg-gray-900/90 backdrop-blur rounded-xl p-4 border border-gray-800 h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-semibold">Signal Summary</h3>
        <button
          onClick={fetchSignalSummary}
          disabled={isLoading}
          className="text-gray-400 hover:text-white transition-colors"
        >
          {isLoading ? '⏳' : '🔄'}
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Signal Counts */}
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-green-900/30 rounded-lg p-2 text-center">
              <div className="text-green-400 font-bold text-lg">{signalData.bullishSignals}</div>
              <div className="text-green-300 text-xs">Bullish</div>
            </div>
            <div className="bg-red-900/30 rounded-lg p-2 text-center">
              <div className="text-red-400 font-bold text-lg">{signalData.bearishSignals}</div>
              <div className="text-red-300 text-xs">Bearish</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-2 text-center">
              <div className="text-gray-400 font-bold text-lg">{signalData.neutralSignals}</div>
              <div className="text-gray-300 text-xs">Neutral</div>
            </div>
          </div>

          {/* Average Confidence */}
          <div className="bg-gray-800/50 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Avg Confidence</span>
              <span className="text-white font-semibold">{signalData.avgConfidence.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-500 ${
                  signalData.avgConfidence >= 80 ? 'bg-green-500' : 
                  signalData.avgConfidence >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${signalData.avgConfidence}%` }}
              />
            </div>
          </div>

          {/* Recent Signals */}
          <div className="space-y-2">
            <h4 className="text-gray-400 text-sm">Recent Signals</h4>
            <div className="max-h-24 overflow-y-auto space-y-1">
              {signalData.signals.slice(0, 3).map((signal, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <span className={`font-medium ${
                    signal.signal_type === 'BUY' ? 'text-green-400' : 
                    signal.signal_type === 'SELL' ? 'text-red-400' : 'text-gray-400'
                  }`}>
                    {signal.signal_type}
                  </span>
                  <span className="text-gray-400">{signal.confidence?.toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SignalSummaryBox;