import React, { useState } from 'react'
import { Search, Star, TrendingUp, TrendingDown, BarChart3 } from 'lucide-react'
import { clsx } from 'clsx'
import { generateDummyData } from '../services/dummyData'

const tradingPairs = [
  { symbol: 'BTC/USDT', name: 'Bitcoin', price: 45234.12, change: 2.34, volume: 1234567890 },
  { symbol: 'ETH/USDT', name: 'Ethereum', price: 2845.67, change: -1.23, volume: 876543210 },
  { symbol: 'SOL/USDT', name: 'Solana', price: 156.78, change: 5.67, volume: 345678901 },
  { symbol: 'BNB/USDT', name: 'Binance Coin', price: 312.45, change: 1.89, volume: 234567890 },
  { symbol: 'ADA/USDT', name: 'Cardano', price: 0.4523, change: -0.45, volume: 123456789 },
  { symbol: 'DOT/USDT', name: 'Polkadot', price: 7.234, change: 3.12, volume: 98765432 },
  { symbol: 'AVAX/USDT', name: 'Avalanche', price: 38.56, change: 4.23, volume: 87654321 },
  { symbol: 'MATIC/USDT', name: 'Polygon', price: 0.8234, change: -2.11, volume: 76543210 }
]

export default function Sidebar({ selectedPair, onPairChange }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [watchlist, setWatchlist] = useState(['BTC/USDT', 'ETH/USDT'])
  const [activeTab, setActiveTab] = useState('all')

  const filteredPairs = tradingPairs.filter(pair => {
    const matchesSearch = pair.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         pair.name.toLowerCase().includes(searchTerm.toLowerCase())
    
    if (activeTab === 'watchlist') {
      return matchesSearch && watchlist.includes(pair.symbol)
    }
    
    return matchesSearch
  })

  const toggleWatchlist = (symbol) => {
    setWatchlist(prev => 
      prev.includes(symbol) 
        ? prev.filter(s => s !== symbol)
        : [...prev, symbol]
    )
  }

  const formatPrice = (price) => {
    if (price >= 1000) return price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    if (price >= 1) return price.toFixed(4)
    return price.toFixed(6)
  }

  const formatVolume = (volume) => {
    if (volume >= 1e9) return `${(volume / 1e9).toFixed(1)}B`
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M`
    if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K`
    return volume.toString()
  }

  return (
    <div className="h-full bg-dark-surface border-r border-dark-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-dark-border">
        <h2 className="text-lg font-semibold text-dark-text mb-4">Market</h2>
        
        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-dark-muted w-4 h-4" />
          <input
            type="text"
            placeholder="Search pairs..."
            className="w-full pl-10 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text placeholder-dark-muted focus:outline-none focus:ring-2 focus:ring-trading-blue"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Tabs */}
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveTab('all')}
            className={clsx(
              'px-3 py-1 text-sm font-medium rounded-lg transition-colors',
              activeTab === 'all'
                ? 'bg-trading-blue text-white'
                : 'text-dark-muted hover:text-dark-text'
            )}
          >
            All
          </button>
          <button
            onClick={() => setActiveTab('watchlist')}
            className={clsx(
              'px-3 py-1 text-sm font-medium rounded-lg transition-colors',
              activeTab === 'watchlist'
                ? 'bg-trading-blue text-white'
                : 'text-dark-muted hover:text-dark-text'
            )}
          >
            Watchlist ({watchlist.length})
          </button>
        </div>
      </div>

      {/* Pairs List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {filteredPairs.map((pair) => (
          <div
            key={pair.symbol}
            className={clsx(
              'p-4 border-b border-dark-border cursor-pointer transition-colors hover:bg-dark-bg',
              selectedPair === pair.symbol && 'bg-trading-blue bg-opacity-20 border-l-4 border-l-trading-blue'
            )}
            onClick={() => onPairChange(pair.symbol)}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-3">
                <div>
                  <div className="font-medium text-dark-text">{pair.symbol}</div>
                  <div className="text-sm text-dark-muted">{pair.name}</div>
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  toggleWatchlist(pair.symbol)
                }}
                className="p-1 hover:bg-dark-bg rounded transition-colors"
              >
                <Star
                  className={clsx(
                    'w-4 h-4',
                    watchlist.includes(pair.symbol)
                      ? 'text-trading-yellow fill-current'
                      : 'text-dark-muted'
                  )}
                />
              </button>
            </div>

            <div className="flex items-center justify-between">
              <div className="text-right">
                <div className="font-medium text-dark-text">
                  ${formatPrice(pair.price)}
                </div>
                <div className="text-xs text-dark-muted">
                  Vol: {formatVolume(pair.volume)}
                </div>
              </div>
              <div className="text-right">
                <div className={clsx(
                  'flex items-center space-x-1 text-sm font-medium',
                  pair.change >= 0 ? 'text-trading-green' : 'text-trading-red'
                )}>
                  {pair.change >= 0 ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                  <span>{pair.change >= 0 ? '+' : ''}{pair.change.toFixed(2)}%</span>
                </div>
              </div>
            </div>

            {/* Mini Chart */}
            <div className="mt-3 h-8 flex items-end space-x-1">
              {Array.from({ length: 20 }, (_, i) => {
                const height = Math.random() * 20 + 5
                return (
                  <div
                    key={i}
                    className={clsx(
                      'w-1 rounded-t',
                      pair.change >= 0 ? 'bg-trading-green' : 'bg-trading-red'
                    )}
                    style={{ height: `${height}px`, opacity: 0.3 + (height / 25) * 0.7 }}
                  />
                )
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-dark-border">
        <div className="flex items-center justify-between text-sm text-dark-muted">
          <span>Market Cap</span>
          <span>$2.1T</span>
        </div>
        <div className="flex items-center justify-between text-sm text-dark-muted mt-1">
          <span>24h Volume</span>
          <span>$89.2B</span>
        </div>
        <div className="flex items-center justify-between text-sm text-dark-muted mt-1">
          <span>BTC Dom</span>
          <span>42.3%</span>
        </div>
      </div>
    </div>
  )
}