import React, { useState } from 'react'
import { Toggle, TrendingUp, BarChart3, Activity, Zap, Plus, Settings } from 'lucide-react'
import { clsx } from 'clsx'

const indicatorGroups = {
  'Moving Averages': [
    { key: 'ema9', name: 'EMA 9', description: 'Exponential Moving Average (9)', color: '#f59e0b' },
    { key: 'ema200', name: 'EMA 200', description: 'Exponential Moving Average (200)', color: '#ec4899' },
    { key: 'sma20', name: 'SMA 20', description: 'Simple Moving Average (20)', color: '#06b6d4' },
    { key: 'sma50', name: 'SMA 50', description: 'Simple Moving Average (50)', color: '#8b5cf6' },
  ],
  'Oscillators': [
    { key: 'rsi', name: 'RSI', description: 'Relative Strength Index (14)', color: '#8b5cf6' },
    { key: 'macd', name: 'MACD', description: 'Moving Average Convergence Divergence', color: '#06b6d4' },
    { key: 'stoch', name: 'Stochastic', description: 'Stochastic Oscillator', color: '#f97316' },
  ],
  'Volatility': [
    { key: 'bollinger', name: 'Bollinger Bands', description: 'Bollinger Bands (20, 2)', color: '#9ca3af' },
    { key: 'atr', name: 'ATR', description: 'Average True Range', color: '#ef4444' },
  ],
  'Volume': [
    { key: 'volume', name: 'Volume', description: 'Trading Volume', color: '#64b5f6' },
    { key: 'obv', name: 'OBV', description: 'On-Balance Volume', color: '#4caf50' },
  ],
  'Custom': [
    { key: 'vwap', name: 'VWAP', description: 'Volume Weighted Average Price', color: '#ff7043' },
    { key: 'fibonacci', name: 'Fibonacci', description: 'Fibonacci Retracement', color: '#ffeb3b' },
  ]
}

export default function IndicatorsPanel({ indicators, onToggle }) {
  const [activeGroup, setActiveGroup] = useState('Moving Averages')
  const [showCustomModal, setShowCustomModal] = useState(false)

  const ToggleSwitch = ({ enabled, onChange }) => (
    <button
      onClick={onChange}
      className={clsx(
        'relative w-11 h-6 rounded-full transition-colors',
        enabled ? 'bg-trading-blue' : 'bg-gray-600'
      )}
    >
      <div
        className={clsx(
          'absolute w-4 h-4 bg-white rounded-full top-1 transition-transform',
          enabled ? 'translate-x-6' : 'translate-x-1'
        )}
      />
    </button>
  )

  return (
    <div className="panel">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-dark-text">Technical Indicators</h3>
        <button
          onClick={() => setShowCustomModal(true)}
          className="p-2 bg-dark-bg hover:bg-gray-700 rounded-lg border border-dark-border transition-colors"
        >
          <Plus className="w-4 h-4 text-dark-muted" />
        </button>
      </div>

      {/* Indicator Groups */}
      <div className="mb-4">
        <div className="flex flex-wrap gap-2 mb-4">
          {Object.keys(indicatorGroups).map(group => (
            <button
              key={group}
              onClick={() => setActiveGroup(group)}
              className={clsx(
                'px-3 py-1 rounded-lg text-sm font-medium transition-colors',
                activeGroup === group
                  ? 'bg-trading-blue text-white'
                  : 'bg-dark-bg text-dark-muted hover:text-dark-text'
              )}
            >
              {group}
            </button>
          ))}
        </div>

        {/* Indicators List */}
        <div className="space-y-3">
          {indicatorGroups[activeGroup].map(indicator => (
            <div key={indicator.key} className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
              <div className="flex items-center space-x-3">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: indicator.color }}
                />
                <div>
                  <div className="font-medium text-dark-text">{indicator.name}</div>
                  <div className="text-sm text-dark-muted">{indicator.description}</div>
                </div>
              </div>
              <ToggleSwitch
                enabled={indicators[indicator.key] || false}
                onChange={() => onToggle(indicator.key)}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="border-t border-dark-border pt-4">
        <div className="flex space-x-2">
          <button className="flex-1 btn-secondary text-sm">
            <Activity className="w-4 h-4 inline mr-1" />
            Presets
          </button>
          <button className="flex-1 btn-secondary text-sm">
            <Settings className="w-4 h-4 inline mr-1" />
            Settings
          </button>
        </div>
      </div>

      {/* Active Indicators Summary */}
      <div className="border-t border-dark-border pt-4 mt-4">
        <h4 className="text-sm font-medium text-dark-text mb-2">Active Indicators</h4>
        <div className="space-y-2">
          {Object.entries(indicators)
            .filter(([key, enabled]) => enabled)
            .map(([key, enabled]) => {
              const indicator = Object.values(indicatorGroups)
                .flat()
                .find(ind => ind.key === key)
              
              if (!indicator) return null
              
              return (
                <div key={key} className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <div
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: indicator.color }}
                    />
                    <span className="text-dark-text">{indicator.name}</span>
                  </div>
                  <button
                    onClick={() => onToggle(key)}
                    className="text-dark-muted hover:text-trading-red"
                  >
                    ×
                  </button>
                </div>
              )
            })}
        </div>
      </div>

      {/* Custom Indicator Modal */}
      {showCustomModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-dark-surface border border-dark-border rounded-lg p-6 w-96">
            <h3 className="text-lg font-semibold text-dark-text mb-4">Add Custom Indicator</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-dark-text mb-2">
                  Indicator Name
                </label>
                <input
                  type="text"
                  className="input-field w-full"
                  placeholder="Enter indicator name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-dark-text mb-2">
                  Parameters
                </label>
                <input
                  type="text"
                  className="input-field w-full"
                  placeholder="e.g., period=14, multiplier=2"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-dark-text mb-2">
                  Color
                </label>
                <input
                  type="color"
                  className="input-field w-full h-10"
                  defaultValue="#3b82f6"
                />
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowCustomModal(false)}
                className="flex-1 btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowCustomModal(false)}
                className="flex-1 btn-primary"
              >
                Add Indicator
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}