import React from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { clsx } from 'clsx';

const ResultCard = ({ analysisResult, isLoading, error }) => {
  if (isLoading) {
    return (
      <div className="bg-dark-surface border border-dark-border rounded-lg p-4 mt-4">
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>
          <span className="text-dark-text">Menganalisa...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-dark-surface border border-red-500 rounded-lg p-4 mt-4">
        <div className="flex items-center space-x-2">
          <XCircle className="w-5 h-5 text-red-400" />
          <span className="text-red-400 font-medium">Error</span>
        </div>
        <p className="text-dark-muted mt-2">{error}</p>
      </div>
    );
  }

  if (!analysisResult) {
    return null;
  }

  const { narrative, confidence, signals, patterns, marketStructure } = analysisResult;

  // Determine confidence color
  const getConfidenceColor = (score) => {
    if (score >= 70) return 'text-green-400';
    if (score >= 40) return 'text-yellow-400';
    return 'text-red-400';
  };

  // Determine market bias
  const getMarketBias = () => {
    if (marketStructure?.bias === 'bullish') return { icon: TrendingUp, text: 'Bullish', color: 'text-green-400' };
    if (marketStructure?.bias === 'bearish') return { icon: TrendingDown, text: 'Bearish', color: 'text-red-400' };
    return { icon: AlertTriangle, text: 'Neutral', color: 'text-yellow-400' };
  };

  const bias = getMarketBias();
  const BiasIcon = bias.icon;

  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg p-4 mt-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <BiasIcon className={clsx("w-5 h-5", bias.color)} />
          <span className={clsx("font-medium", bias.color)}>{bias.text}</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-dark-muted text-sm">Confidence:</span>
          <span className={clsx("font-medium", getConfidenceColor(confidence))}>
            {confidence.toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Narrative */}
      {narrative && (
        <div className="bg-dark-bg border border-dark-border rounded-lg p-3">
          <h4 className="text-dark-text font-medium mb-2">Analisa SMC</h4>
          <p className="text-dark-muted text-sm leading-relaxed">{narrative}</p>
        </div>
      )}

      {/* Trading Signals */}
      {signals && signals.length > 0 && (
        <div className="bg-dark-bg border border-dark-border rounded-lg p-3">
          <h4 className="text-dark-text font-medium mb-2">Trading Signals</h4>
          <div className="space-y-2">
            {signals.slice(0, 3).map((signal, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <span className="text-dark-muted">{signal.pattern_type}</span>
                <span className={clsx(
                  "font-medium px-2 py-1 rounded",
                  signal.action === 'BUY' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
                )}>
                  {signal.action}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Advanced Patterns */}
      {patterns && patterns.length > 0 && (
        <div className="bg-dark-bg border border-dark-border rounded-lg p-3">
          <h4 className="text-dark-text font-medium mb-2">Advanced Patterns</h4>
          <div className="flex flex-wrap gap-2">
            {patterns.slice(0, 5).map((pattern, index) => (
              <div key={index} className="flex items-center space-x-1 bg-dark-surface px-2 py-1 rounded text-xs">
                <CheckCircle className="w-3 h-3 text-green-400" />
                <span className="text-dark-text">{pattern.type}</span>
                <span className="text-dark-muted">({pattern.confidence_score?.toFixed(1)}%)</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultCard;