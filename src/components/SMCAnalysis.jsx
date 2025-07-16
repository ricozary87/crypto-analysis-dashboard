import React from 'react';

export default function SMCAnalysis({ smcData }) {
  if (!smcData || Object.keys(smcData).length === 0) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mt-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Smart Money Concepts (SMC) Analysis
        </h3>
        <p className="text-gray-400">No SMC data available</p>
      </div>
    );
  }

  const {
    swing_points = [],
    order_blocks = [],
    fair_value_gaps = [],
    liquidity_sweeps = [],
    market_structure = "Unknown",
    trend_direction = "Unknown",
    pattern_strength = 0
  } = smcData;

  const getTrendColor = (trend) => {
    if (trend === "bullish") return "text-green-400";
    if (trend === "bearish") return "text-red-400";
    return "text-gray-400";
  };

  const getPatternStrengthColor = (strength) => {
    if (strength > 0.7) return "text-green-400";
    if (strength > 0.5) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mt-6">
      <h3 className="text-lg font-semibold text-white mb-4">
        Smart Money Concepts (SMC) Analysis
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Market Structure */}
        <div className="space-y-4">
          <h4 className="text-green-400 font-medium">Market Structure</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Structure:</span>
              <span className="text-white">{market_structure}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Trend Direction:</span>
              <span className={getTrendColor(trend_direction)}>{trend_direction}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Pattern Strength:</span>
              <span className={getPatternStrengthColor(pattern_strength)}>
                {(pattern_strength * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        {/* Swing Points */}
        <div className="space-y-4">
          <h4 className="text-green-400 font-medium">Swing Points</h4>
          <div className="space-y-2">
            {swing_points.length > 0 ? (
              swing_points.slice(0, 3).map((point, index) => (
                <div key={index} className="flex justify-between text-sm">
                  <span className="text-gray-400">{point.type}:</span>
                  <span className="text-white">${point.price?.toFixed(2) || 'N/A'}</span>
                </div>
              ))
            ) : (
              <p className="text-gray-400 text-sm">No swing points detected</p>
            )}
          </div>
        </div>

        {/* Order Blocks */}
        <div className="space-y-4">
          <h4 className="text-green-400 font-medium">Order Blocks</h4>
          <div className="space-y-2">
            {order_blocks.length > 0 ? (
              order_blocks.slice(0, 3).map((block, index) => (
                <div key={index} className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">{block.type}:</span>
                    <span className="text-white">${block.price?.toFixed(2) || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 text-xs">Strength:</span>
                    <span className={getPatternStrengthColor(block.strength)}>
                      {(block.strength * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-400 text-sm">No order blocks detected</p>
            )}
          </div>
        </div>

        {/* Fair Value Gaps */}
        <div className="space-y-4">
          <h4 className="text-green-400 font-medium">Fair Value Gaps</h4>
          <div className="space-y-2">
            {fair_value_gaps.length > 0 ? (
              fair_value_gaps.slice(0, 3).map((gap, index) => (
                <div key={index} className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">{gap.type}:</span>
                    <span className="text-white">${gap.price?.toFixed(2) || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 text-xs">Size:</span>
                    <span className="text-white">${gap.size?.toFixed(2) || 'N/A'}</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-400 text-sm">No fair value gaps detected</p>
            )}
          </div>
        </div>

        {/* Liquidity Sweeps */}
        <div className="space-y-4">
          <h4 className="text-green-400 font-medium">Liquidity Sweeps</h4>
          <div className="space-y-2">
            {liquidity_sweeps.length > 0 ? (
              liquidity_sweeps.slice(0, 3).map((sweep, index) => (
                <div key={index} className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">{sweep.type}:</span>
                    <span className="text-white">${sweep.price?.toFixed(2) || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 text-xs">Volume:</span>
                    <span className="text-white">{sweep.volume?.toFixed(0) || 'N/A'}</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-400 text-sm">No liquidity sweeps detected</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}