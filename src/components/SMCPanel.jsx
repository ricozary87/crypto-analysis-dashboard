import React, { useState } from 'react';

const SMCPanel = ({ data }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Default values if data is not provided
  const {
    timeframe = '1H',
    bos = false,
    choch = false,
    fvgZone = null,
    ob = null,
    liquiditySweep = false,
    signalStrength = 0,
    narrative = ''
  } = data || {};

  // Calculate actual signal strength if not provided
  const activeSignals = [bos, choch, fvgZone, ob, liquiditySweep].filter(Boolean).length;
  const strength = signalStrength || activeSignals;

  // Helper function to get status badge
  const getStatusBadge = (isActive, value = null) => {
    if (value !== null && value !== undefined) {
      return (
        <div className="flex flex-col items-center">
          <span className="text-green-500 text-lg mb-1">✅</span>
          <span className="text-gray-300 text-xs font-mono">{value}</span>
        </div>
      );
    }
    
    if (isActive === true) {
      return <span className="text-green-500 text-lg">✅</span>;
    } else if (isActive === false) {
      return <span className="text-red-500 text-lg">❌</span>;
    } else {
      return <span className="text-yellow-500 text-lg">⚠️</span>;
    }
  };

  // Truncate narrative for display
  const maxLines = 4;
  const narrativeLines = narrative.split('\n');
  const displayNarrative = isExpanded 
    ? narrative 
    : narrativeLines.slice(0, maxLines).join('\n');
  const needsExpansion = narrativeLines.length > maxLines;

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white text-lg font-semibold">SMC Signal Panel</h3>
        <span className="text-gray-400 text-sm bg-gray-800 px-2 py-1 rounded">
          {timeframe}
        </span>
      </div>

      {/* Signal Table */}
      <div className="grid grid-cols-5 gap-2 mb-4">
        {/* BOS Column */}
        <div className="bg-gray-800 rounded-lg p-3 flex flex-col items-center hover:bg-gray-750 transition-colors">
          <span className="text-gray-400 text-xs mb-2">BOS</span>
          {getStatusBadge(bos)}
        </div>

        {/* CHoCH Column */}
        <div className="bg-gray-800 rounded-lg p-3 flex flex-col items-center hover:bg-gray-750 transition-colors">
          <span className="text-gray-400 text-xs mb-2">CHoCH</span>
          {getStatusBadge(choch)}
        </div>

        {/* FVG Column */}
        <div className="bg-gray-800 rounded-lg p-3 flex flex-col items-center hover:bg-gray-750 transition-colors">
          <span className="text-gray-400 text-xs mb-2">FVG</span>
          {getStatusBadge(fvgZone ? true : false, fvgZone)}
        </div>

        {/* OB Column */}
        <div className="bg-gray-800 rounded-lg p-3 flex flex-col items-center hover:bg-gray-750 transition-colors">
          <span className="text-gray-400 text-xs mb-2">OB</span>
          {getStatusBadge(ob ? true : false, ob ? `$${ob}` : null)}
        </div>

        {/* Sweep Column */}
        <div className="bg-gray-800 rounded-lg p-3 flex flex-col items-center hover:bg-gray-750 transition-colors">
          <span className="text-gray-400 text-xs mb-2">Sweep</span>
          {getStatusBadge(liquiditySweep)}
        </div>
      </div>

      {/* Signal Strength */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-1">
          <span className="text-gray-400 text-sm">Signal Strength</span>
          <span className="text-white text-sm font-medium">{strength}/5 signals</span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-2">
          <div 
            className="h-2 rounded-full transition-all duration-300"
            style={{
              width: `${(strength / 5) * 100}%`,
              backgroundColor: strength >= 4 ? '#10b981' : strength >= 3 ? '#f59e0b' : '#ef4444'
            }}
          />
        </div>
      </div>

      {/* GPT Analysis Narrative */}
      {narrative && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex-1">
          <h4 className="text-gray-300 text-sm font-semibold mb-2">Analisa GPT</h4>
          <p className="text-gray-400 text-sm whitespace-pre-line leading-relaxed">
            {displayNarrative}
          </p>
          {needsExpansion && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="mt-2 text-blue-400 hover:text-blue-300 text-xs font-medium transition-colors"
            >
              {isExpanded ? '▲ Show Less' : '▼ Read More'}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default SMCPanel;