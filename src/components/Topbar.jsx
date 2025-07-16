import React, { useState } from 'react'
import { ChevronDown, Settings, Bell, BarChart3, TrendingUp, Zap } from 'lucide-react'
import { clsx } from 'clsx'

const timeframes = [
  { value: '5m', label: '5m' },
  { value: '15m', label: '15m' },
  { value: '1H', label: '1H' },
  { value: '4H', label: '4H' },
  { value: '1D', label: '1D' },
  { value: '1W', label: '1W' }
]

const chartTypes = [
  { value: 'candlestick', label: 'Candlestick', icon: BarChart3 },
  { value: 'ohlc', label: 'OHLC', icon: TrendingUp },
  { value: 'line', label: 'Line', icon: Zap }
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

  const tradingPairs = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'ADA/USDT', 'DOT/USDT'
  ]

  const currentChartType = chartTypes.find(type => type.value === chartType) || chartTypes[0]

  return (
    <div className="h-16 bg-dark-surface border-b border-dark-border flex items-center justify-between px-4">
      {/* Left Side - Pair Selection */}
      <div className="flex items-center space-x-4">
        {/* Pair Selector */}
        <div className="relative">
          <button
            onClick={() => setShowPairDropdown(!showPairDropdown)}
            className="flex items-center space-x-2 px-4 py-2 bg-dark-bg border border-dark-border rounded-lg hover:bg-gray-700 transition-colors"
          >
            <span className="font-medium text-dark-text">{selectedPair}</span>
            <ChevronDown className="w-4 h-4 text-dark-muted" />
          </button>
          
          {showPairDropdown && (
            <div className="absolute top-full left-0 mt-1 bg-dark-surface border border-dark-border rounded-lg shadow-lg z-50 min-w-[120px]">
              {tradingPairs.map(pair => (
                <button
                  key={pair}
                  onClick={() => {
                    onPairChange(pair)
                    setShowPairDropdown(false)
                  }}
                  className={clsx(
                    'w-full px-4 py-2 text-left hover:bg-dark-bg transition-colors',
                    selectedPair === pair ? 'text-trading-blue bg-trading-blue bg-opacity-20' : 'text-dark-text'
                  )}
                >
                  {pair}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Current Price Display */}
        <div className="flex items-center space-x-4">
          <div>
            <div className="text-lg font-bold text-dark-text">$45,234.12</div>
            <div className="text-sm text-trading-green">+2.34%</div>
          </div>
          <div className="text-sm text-dark-muted">
            <div>24h High: $46,123.45</div>
            <div>24h Low: $44,567.89</div>
          </div>
        </div>
      </div>

      {/* Center - Timeframe Selection */}
      <div className="flex items-center space-x-2">
        {timeframes.map(tf => (
          <button
            key={tf.value}
            onClick={() => onTimeframeChange(tf.value)}
            className={clsx(
              'px-3 py-1 text-sm font-medium rounded-lg transition-colors',
              selectedTimeframe === tf.value
                ? 'bg-trading-blue text-white'
                : 'text-dark-muted hover:text-dark-text hover:bg-dark-bg'
            )}
          >
            {tf.label}
          </button>
        ))}
      </div>

      {/* Right Side - Chart Type & Controls */}
      <div className="flex items-center space-x-4">
        {/* Chart Type Selector */}
        <div className="relative">
          <button
            onClick={() => setShowChartTypeDropdown(!showChartTypeDropdown)}
            className="flex items-center space-x-2 px-4 py-2 bg-dark-bg border border-dark-border rounded-lg hover:bg-gray-700 transition-colors"
          >
            <currentChartType.icon className="w-4 h-4 text-dark-muted" />
            <span className="text-dark-text">{currentChartType.label}</span>
            <ChevronDown className="w-4 h-4 text-dark-muted" />
          </button>
          
          {showChartTypeDropdown && (
            <div className="absolute top-full right-0 mt-1 bg-dark-surface border border-dark-border rounded-lg shadow-lg z-50 min-w-[140px]">
              {chartTypes.map(type => (
                <button
                  key={type.value}
                  onClick={() => {
                    onChartTypeChange(type.value)
                    setShowChartTypeDropdown(false)
                  }}
                  className={clsx(
                    'w-full px-4 py-2 text-left hover:bg-dark-bg transition-colors flex items-center space-x-2',
                    chartType === type.value ? 'text-trading-blue bg-trading-blue bg-opacity-20' : 'text-dark-text'
                  )}
                >
                  <type.icon className="w-4 h-4" />
                  <span>{type.label}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-2">
          <button className="p-2 bg-dark-bg border border-dark-border rounded-lg hover:bg-gray-700 transition-colors">
            <Bell className="w-4 h-4 text-dark-muted" />
          </button>
          <button className="p-2 bg-dark-bg border border-dark-border rounded-lg hover:bg-gray-700 transition-colors">
            <Settings className="w-4 h-4 text-dark-muted" />
          </button>
        </div>

        {/* Trading Controls */}
        <div className="flex items-center space-x-2">
          <button className="px-4 py-2 bg-trading-green hover:bg-green-600 text-white rounded-lg font-medium transition-colors">
            Buy
          </button>
          <button className="px-4 py-2 bg-trading-red hover:bg-red-600 text-white rounded-lg font-medium transition-colors">
            Sell
          </button>
        </div>
      </div>
    </div>
  )
}