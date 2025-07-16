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

  const getStatusColor = (status) => {
    switch (status) {
      case 'valid':
        return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'invalid':
        return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'pending':
        return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      default:
        return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const IndicatorItem = ({ label, value, isActive, description }) => {
    return (
      <div className={`p-3 rounded-lg border transition-all ${
        isActive 
          ? 'bg-blue-500/10 border-blue-400/30' 
          : 'bg-gray-800/30 border-gray-700/30'
      }`}>
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-medium text-gray-400">{label}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${
            isActive 
              ? 'bg-blue-500/20 text-blue-400' 
              : 'bg-gray-700/50 text-gray-500'
          }`}>
            {isActive ? 'Active' : 'Inactive'}
          </span>
        </div>
        <div className={`text-sm font-semibold ${
          isActive ? 'text-white' : 'text-gray-500'
        }`}>
          {value || '-'}
        </div>
        {description && (
          <div className="text-xs text-gray-500 mt-1">{description}</div>
        )}
      </div>
    );
  };

  const ZoneItem = ({ label, value, color = 'blue' }) => {
    const colorClasses = {
      blue: 'bg-blue-500/10 border-blue-400/30 text-blue-400',
      green: 'bg-green-500/10 border-green-400/30 text-green-400',
      yellow: 'bg-yellow-500/10 border-yellow-400/30 text-yellow-400',
      red: 'bg-red-500/10 border-red-400/30 text-red-400'
    };

    return (
      <div className={`p-3 rounded-lg border ${colorClasses[color]}`}>
        <div className="text-xs font-medium mb-1 opacity-80">{label}</div>
        <div className="text-sm font-semibold">{value || 'Not Detected'}</div>
      </div>
    );
  };

  return (
    <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold text-white">Market Structure</h3>
          <span className="text-xs px-2 py-1 rounded bg-gray-800 text-gray-400">
            {timeframe}
          </span>
        </div>
        <div className={`text-xs px-3 py-1 rounded-full border ${getStatusColor(status)}`}>
          {status.toUpperCase()}
        </div>
      </div>

      {/* SMC Indicators Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <IndicatorItem
          label="BOS (Break of Structure)"
          value={bos ? "Detected" : "Not Detected"}
          isActive={bos}
          description={bos ? "Market structure broken" : "Structure intact"}
        />
        <IndicatorItem
          label="CHoCH (Change of Character)"
          value={choch ? "Confirmed" : "Not Confirmed"}
          isActive={choch}
          description={choch ? "Trend reversal signal" : "Trend continuation"}
        />
        <IndicatorItem
          label="Liquidity Sweep"
          value={liquiditySweep ? "Swept" : "Protected"}
          isActive={liquiditySweep}
          description={liquiditySweep ? "Stop hunt detected" : "No manipulation"}
        />
        <IndicatorItem
          label="Order Block"
          value={ob ? `$${ob.toFixed(2)}` : "None"}
          isActive={!!ob}
          description={ob ? "Institutional level" : "No key level"}
        />
      </div>

      {/* Key Zones */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-400">Key Zones</h4>
        
        {fvgZone && (
          <ZoneItem
            label="Fair Value Gap (FVG)"
            value={fvgZone}
            color="yellow"
          />
        )}

        {/* Market Bias Indicator */}
        <div className="mt-4 p-3 rounded-lg bg-gradient-to-r from-gray-800/50 to-gray-800/30 border border-gray-700/50">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Market Bias</span>
            <div className="flex items-center gap-2">
              {(bos || choch) ? (
                <>
                  <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></span>
                  <span className="text-sm font-medium text-blue-400">
                    {choch ? 'Reversal Expected' : 'Trend Continuation'}
                  </span>
                </>
              ) : (
                <>
                  <span className="w-2 h-2 bg-gray-500 rounded-full"></span>
                  <span className="text-sm font-medium text-gray-500">Neutral</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-2 mt-3">
          <div className="text-center p-2 bg-gray-800/30 rounded-lg">
            <div className="text-xs text-gray-500">Structures</div>
            <div className="text-sm font-semibold text-white">
              {[bos, choch].filter(Boolean).length}/2
            </div>
          </div>
          <div className="text-center p-2 bg-gray-800/30 rounded-lg">
            <div className="text-xs text-gray-500">Zones</div>
            <div className="text-sm font-semibold text-white">
              {[ob, fvgZone].filter(Boolean).length}/2
            </div>
          </div>
          <div className="text-center p-2 bg-gray-800/30 rounded-lg">
            <div className="text-xs text-gray-500">Signals</div>
            <div className="text-sm font-semibold text-white">
              {[bos, choch, liquiditySweep, ob, fvgZone].filter(Boolean).length}/5
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SMCPanel;