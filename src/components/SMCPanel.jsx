import React from 'react';

const SMCPanel = ({ data }) => {
  const {
    timeframe = '1H',
    bos = false,
    choch = false,
    ob = null,
    fvgZone = null,
    liquiditySweep = false,
    status = 'valid'
  } = data || {};

  const getStatusBadge = (isActive, status) => {
    if (!isActive) return '❌';
    if (status === 'valid') return '✅';
    if (status === 'pending') return '⚠️';
    return '❌';
  };

  const SignalColumn = ({ label, isActive, value, status = 'valid' }) => {
    return (
      <div className={`flex-1 p-3 rounded-lg border transition-all hover:scale-105 ${
        isActive 
          ? status === 'valid' 
            ? 'bg-green-500/10 border-green-400/30' 
            : status === 'pending'
            ? 'bg-yellow-500/10 border-yellow-400/30'
            : 'bg-red-500/10 border-red-400/30'
          : 'bg-gray-800/30 border-gray-700/30'
      }`}>
        <div className="text-center">
          <div className="text-2xl mb-2">{getStatusBadge(isActive, status)}</div>
          <div className="text-xs font-medium text-gray-400 mb-1">{label}</div>
          {value && (
            <div className={`text-sm font-semibold ${
              isActive ? 'text-white' : 'text-gray-500'
            }`}>
              {value}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-gray-900/90 backdrop-blur rounded-xl p-4 border border-gray-800">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">SMC Signal Panel</h3>
        <span className="text-xs px-3 py-1 rounded-full bg-gray-800 text-gray-400">
          {timeframe}
        </span>
      </div>

      {/* Signals Table - 1 column per signal */}
      <div className="flex gap-2 overflow-x-auto scrollbar-thin">
        <SignalColumn 
          label="BOS" 
          isActive={bos} 
          status={status}
        />
        <SignalColumn 
          label="CHoCH" 
          isActive={choch} 
          status={status}
        />
        <SignalColumn 
          label="FVG" 
          isActive={!!fvgZone} 
          value={fvgZone}
          status={status}
        />
        <SignalColumn 
          label="OB" 
          isActive={!!ob} 
          value={ob ? `$${ob.toFixed(2)}` : null}
          status={status}
        />
        <SignalColumn 
          label="Sweep" 
          isActive={liquiditySweep} 
          status={status}
        />
      </div>

      {/* Summary Bar */}
      <div className="mt-4 p-2 rounded-lg bg-gradient-to-r from-gray-800/50 to-gray-800/30 border border-gray-700/50">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Signal Strength</span>
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              {[...Array(5)].map((_, i) => (
                <div 
                  key={i}
                  className={`w-2 h-2 rounded-full ${
                    i < [bos, choch, !!ob, !!fvgZone, liquiditySweep].filter(Boolean).length
                      ? 'bg-green-400'
                      : 'bg-gray-600'
                  }`}
                />
              ))}
            </div>
            <span className="text-xs text-gray-400">
              {[bos, choch, !!ob, !!fvgZone, liquiditySweep].filter(Boolean).length}/5
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SMCPanel;