import React, { useState } from 'react'
import { ChevronDown, BarChart3, Candlestick, TrendingUp, Settings } from 'lucide-react'
import { clsx } from 'clsx'

const timeframes = ['5m', '15m', '1H', '4H', '1D', '1W']
const chartTypes = [
  { id: 'candlestick', name: 'Candlestick', icon: Candlestick },
  { id: 'ohlc', name: 'OHLC', icon: BarChart3 },
  { id: 'line', name: 'Line', icon: TrendingUp }
]

export default function Topbar({ 
  selectedPair, 
  selectedTimeframe, 
  chartType,
  onPairChange, 
  onTimeframeChange,
  onChartTypeChange 
}) {
  const [showPairDropdown, setShowPairDropdown] = useState(false)
  const [showTimeframeDropdown, setShowTimeframeDropdown] = useState(false)
  const [showChartTypeDropdown, setShowChartTypeDropdown] = useState(false)

  return (
    <div className="h-16 bg-dark-surface border-b border-dark-border flex items-center justify-between px-6">
      {/* Left Section - Pair Selection */}
      <div className="flex items-center space-x-4">
        <div className="relative">
          <button
            className="flex items-center space-x-2 bg-dark-bg hover:bg-gray-700 px-4 py-2 rounded-lg border border-dark-border transition-colors"
            onClick={() => setShowPairDropdown(!showPairDropdown)}
          >
            <span className="font-semibold text-dark-text">{selectedPair}</span>
            <ChevronDown className="w-4 h-4 text-dark-muted" />
          </button>
          
          {showPairDropdown && (
            <div className="absolute top-full left-0 mt-2 w-48 dropdown z-50">
              <div className="py-2">
                {['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'ADA/USDT'].map(pair => (
                  <button
                    key={pair}
                    className={clsx(
                      'w-full text-left dropdown-item',
                      selectedPair === pair && 'bg-trading-blue bg-opacity-20 text-trading-blue'
                    )}
                    onClick={() => {
                      onPairChange(pair)
                      setShowPairDropdown(false)
                    }}
                  >
                    {pair}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Price Info */}
        <div className="flex items-center space-x-6 text-sm">
          <div>
            <span className="text-dark-muted">Price: </span>
            <span className="font-medium text-dark-text">$45,250.30</span>
          </div>
          <div>
            <span className="text-dark-muted">24h: </span>
            <span className="font-medium text-trading-green">+2.45%</span>
          </div>
          <div>
            <span className="text-dark-muted">Vol: </span>
            <span className="font-medium text-dark-text">2.4B</span>
          </div>
        </div>
      </div>

      {/* Right Section - Controls */}
      <div className="flex items-center space-x-4">
        {/* Timeframe Selection */}
        <div className="relative">
          <button
            className="flex items-center space-x-2 bg-dark-bg hover:bg-gray-700 px-4 py-2 rounded-lg border border-dark-border transition-colors"
            onClick={() => setShowTimeframeDropdown(!showTimeframeDropdown)}
          >
            <span className="font-medium text-dark-text">{selectedTimeframe}</span>
            <ChevronDown className="w-4 h-4 text-dark-muted" />
          </button>
          
          {showTimeframeDropdown && (
            <div className="absolute top-full right-0 mt-2 w-24 dropdown z-50">
              <div className="py-2">
                {timeframes.map(tf => (
                  <button
                    key={tf}
                    className={clsx(
                      'w-full text-left dropdown-item',
                      selectedTimeframe === tf && 'bg-trading-blue bg-opacity-20 text-trading-blue'
                    )}
                    onClick={() => {
                      onTimeframeChange(tf)
                      setShowTimeframeDropdown(false)
                    }}
                  >
                    {tf}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Chart Type Selection */}
        <div className="relative">
          <button
            className="flex items-center space-x-2 bg-dark-bg hover:bg-gray-700 px-4 py-2 rounded-lg border border-dark-border transition-colors"
            onClick={() => setShowChartTypeDropdown(!showChartTypeDropdown)}
          >
            {React.createElement(chartTypes.find(ct => ct.id === chartType)?.icon || Candlestick, {
              className: "w-4 h-4"
            })}
            <ChevronDown className="w-4 h-4 text-dark-muted" />
          </button>
          
          {showChartTypeDropdown && (
            <div className="absolute top-full right-0 mt-2 w-40 dropdown z-50">
              <div className="py-2">
                {chartTypes.map(ct => (
                  <button
                    key={ct.id}
                    className={clsx(
                      'w-full text-left dropdown-item flex items-center space-x-2',
                      chartType === ct.id && 'bg-trading-blue bg-opacity-20 text-trading-blue'
                    )}
                    onClick={() => {
                      onChartTypeChange(ct.id)
                      setShowChartTypeDropdown(false)
                    }}
                  >
                    <ct.icon className="w-4 h-4" />
                    <span>{ct.name}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Settings */}
        <button className="p-2 bg-dark-bg hover:bg-gray-700 rounded-lg border border-dark-border transition-colors">
          <Settings className="w-5 h-5 text-dark-muted" />
        </button>
      </div>
    </div>
  )
}