import React, { useState } from 'react'
import { Star, TrendingUp, Search } from 'lucide-react'
import { clsx } from 'clsx'

const tradingPairs = [
  { symbol: 'BTC/USDT', name: 'Bitcoin', price: 45250.30, change: 2.45, volume: '2.4B' },
  { symbol: 'ETH/USDT', name: 'Ethereum', price: 2850.75, change: -1.25, volume: '1.8B' },
  { symbol: 'SOL/USDT', name: 'Solana', price: 162.45, change: 5.12, volume: '485M' },
  { symbol: 'BNB/USDT', name: 'BNB', price: 315.80, change: 1.85, volume: '320M' },
  { symbol: 'ADA/USDT', name: 'Cardano', price: 0.485, change: -0.75, volume: '125M' },
  { symbol: 'DOT/USDT', name: 'Polkadot', price: 7.25, change: 3.20, volume: '98M' },
  { symbol: 'AVAX/USDT', name: 'Avalanche', price: 38.90, change: -2.15, volume: '156M' },
  { symbol: 'MATIC/USDT', name: 'Polygon', price: 0.825, change: 4.30, volume: '78M' },
]

const watchlist = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']

export default function Sidebar({ selectedPair, onPairChange }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('market')

  const filteredPairs = tradingPairs.filter(pair => 
    pair.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    pair.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="h-full bg-dark-surface border-r border-dark-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-dark-border">
        <h2 className="text-lg font-semibold text-dark-text">Markets</h2>
        
        {/* Search */}
        <div className="mt-3 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-dark-muted w-4 h-4" />
          <input
            type="text"
            placeholder="Search pairs..."
            className="w-full pl-10 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm text-dark-text focus:outline-none focus:ring-2 focus:ring-trading-blue"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-dark-border">
        <button
          className={clsx(
            'flex-1 py-2 px-4 text-sm font-medium transition-colors',
            activeTab === 'market' 
              ? 'text-trading-blue border-b-2 border-trading-blue' 
              : 'text-dark-muted hover:text-dark-text'
          )}
          onClick={() => setActiveTab('market')}
        >
          Market
        </button>
        <button
          className={clsx(
            'flex-1 py-2 px-4 text-sm font-medium transition-colors',
            activeTab === 'watchlist' 
              ? 'text-trading-blue border-b-2 border-trading-blue' 
              : 'text-dark-muted hover:text-dark-text'
          )}
          onClick={() => setActiveTab('watchlist')}
        >
          <Star className="w-4 h-4 inline mr-1" />
          Watchlist
        </button>
      </div>

      {/* Pairs List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {activeTab === 'market' ? (
          <div className="p-2">
            {filteredPairs.map((pair) => (
              <div
                key={pair.symbol}
                className={clsx(
                  'p-3 rounded-lg cursor-pointer transition-colors mb-1',
                  selectedPair === pair.symbol
                    ? 'bg-trading-blue bg-opacity-20 border border-trading-blue'
                    : 'hover:bg-dark-bg'
                )}
                onClick={() => onPairChange(pair.symbol)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-dark-text text-sm">{pair.symbol}</div>
                    <div className="text-xs text-dark-muted">{pair.name}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-dark-text">
                      ${pair.price.toLocaleString()}
                    </div>
                    <div className={clsx(
                      'text-xs flex items-center',
                      pair.change > 0 ? 'text-trading-green' : 'text-trading-red'
                    )}>
                      <TrendingUp className={clsx(
                        'w-3 h-3 mr-1',
                        pair.change < 0 && 'rotate-180'
                      )} />
                      {pair.change > 0 ? '+' : ''}{pair.change.toFixed(2)}%
                    </div>
                  </div>
                </div>
                <div className="mt-2 text-xs text-dark-muted">
                  Vol: {pair.volume}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-2">
            {tradingPairs.filter(pair => watchlist.includes(pair.symbol)).map((pair) => (
              <div
                key={pair.symbol}
                className={clsx(
                  'p-3 rounded-lg cursor-pointer transition-colors mb-1',
                  selectedPair === pair.symbol
                    ? 'bg-trading-blue bg-opacity-20 border border-trading-blue'
                    : 'hover:bg-dark-bg'
                )}
                onClick={() => onPairChange(pair.symbol)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-dark-text text-sm">{pair.symbol}</div>
                    <div className="text-xs text-dark-muted">{pair.name}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-dark-text">
                      ${pair.price.toLocaleString()}
                    </div>
                    <div className={clsx(
                      'text-xs flex items-center',
                      pair.change > 0 ? 'text-trading-green' : 'text-trading-red'
                    )}>
                      <TrendingUp className={clsx(
                        'w-3 h-3 mr-1',
                        pair.change < 0 && 'rotate-180'
                      )} />
                      {pair.change > 0 ? '+' : ''}{pair.change.toFixed(2)}%
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}