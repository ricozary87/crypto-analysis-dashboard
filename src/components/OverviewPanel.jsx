import React from 'react'
import { TrendingUp, TrendingDown, Volume, DollarSign, Activity, Users } from 'lucide-react'
import { clsx } from 'clsx'

export default function OverviewPanel({ pair, data, orderbook }) {
  const currentData = data && data.length > 0 ? data[data.length - 1] : null
  const prevData = data && data.length > 1 ? data[data.length - 2] : null
  
  const currentPrice = currentData?.close || 0
  const priceChange = currentData && prevData ? currentData.close - prevData.close : 0
  const priceChangePercent = prevData ? (priceChange / prevData.close) * 100 : 0
  
  const volume24h = data ? data.reduce((sum, d) => sum + d.volume, 0) : 0
  const high24h = data ? Math.max(...data.map(d => d.high)) : 0
  const low24h = data ? Math.min(...data.map(d => d.low)) : 0
  
  // Calculate orderbook metrics
  const totalBids = orderbook.bids?.reduce((sum, bid) => sum + parseFloat(bid[1]), 0) || 0
  const totalAsks = orderbook.asks?.reduce((sum, ask) => sum + parseFloat(ask[1]), 0) || 0
  const spread = orderbook.asks?.[0] && orderbook.bids?.[0] 
    ? parseFloat(orderbook.asks[0][0]) - parseFloat(orderbook.bids[0][0])
    : 0
  
  const formatNumber = (num) => {
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B'
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M'
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K'
    return num.toFixed(2)
  }

  return (
    <div className="panel space-y-4">
      <div className="border-b border-dark-border pb-4">
        <h3 className="text-lg font-semibold text-dark-text mb-2">{pair}</h3>
        
        {/* Current Price */}
        <div className="flex items-center space-x-3">
          <div className="text-2xl font-bold text-dark-text">
            ${currentPrice.toLocaleString()}
          </div>
          <div className={clsx(
            'flex items-center space-x-1 px-2 py-1 rounded text-sm font-medium',
            priceChange >= 0 
              ? 'bg-trading-green bg-opacity-20 text-trading-green'
              : 'bg-trading-red bg-opacity-20 text-trading-red'
          )}>
            {priceChange >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            <span>{priceChange >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%</span>
          </div>
        </div>
        
        {/* 24h Change */}
        <div className="text-sm text-dark-muted mt-1">
          {priceChange >= 0 ? '+' : ''}${priceChange.toFixed(2)} (24h)
        </div>
      </div>

      {/* Price Statistics */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="flex items-center space-x-2 text-sm text-dark-muted mb-1">
            <TrendingUp className="w-4 h-4" />
            <span>24h High</span>
          </div>
          <div className="text-lg font-semibold text-trading-green">
            ${high24h.toLocaleString()}
          </div>
        </div>
        
        <div>
          <div className="flex items-center space-x-2 text-sm text-dark-muted mb-1">
            <TrendingDown className="w-4 h-4" />
            <span>24h Low</span>
          </div>
          <div className="text-lg font-semibold text-trading-red">
            ${low24h.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Volume & Trading Info */}
      <div className="space-y-3">
        <div>
          <div className="flex items-center space-x-2 text-sm text-dark-muted mb-1">
            <Volume className="w-4 h-4" />
            <span>24h Volume</span>
          </div>
          <div className="text-lg font-semibold text-dark-text">
            {formatNumber(volume24h)}
          </div>
        </div>

        <div>
          <div className="flex items-center space-x-2 text-sm text-dark-muted mb-1">
            <DollarSign className="w-4 h-4" />
            <span>Market Cap</span>
          </div>
          <div className="text-lg font-semibold text-dark-text">
            $890.2B
          </div>
        </div>

        <div>
          <div className="flex items-center space-x-2 text-sm text-dark-muted mb-1">
            <Activity className="w-4 h-4" />
            <span>Spread</span>
          </div>
          <div className="text-lg font-semibold text-dark-text">
            ${spread.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Orderbook Summary */}
      <div className="border-t border-dark-border pt-4">
        <h4 className="text-sm font-medium text-dark-text mb-3">Orderbook</h4>
        
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-dark-muted">Total Bids</span>
            <span className="text-sm font-medium text-trading-green">
              {formatNumber(totalBids)}
            </span>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-sm text-dark-muted">Total Asks</span>
            <span className="text-sm font-medium text-trading-red">
              {formatNumber(totalAsks)}
            </span>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-sm text-dark-muted">Bid/Ask Ratio</span>
            <span className="text-sm font-medium text-dark-text">
              {totalAsks > 0 ? (totalBids / totalAsks).toFixed(2) : '0.00'}
            </span>
          </div>
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="border-t border-dark-border pt-4">
        <h4 className="text-sm font-medium text-dark-text mb-3">Trading Metrics</h4>
        
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <div className="text-dark-muted">Funding Rate</div>
            <div className="font-medium text-trading-green">0.0125%</div>
          </div>
          
          <div>
            <div className="text-dark-muted">Open Interest</div>
            <div className="font-medium text-dark-text">$2.1B</div>
          </div>
          
          <div>
            <div className="text-dark-muted">Long/Short</div>
            <div className="font-medium text-dark-text">52.3% / 47.7%</div>
          </div>
          
          <div>
            <div className="text-dark-muted">Fear & Greed</div>
            <div className="font-medium text-trading-yellow">Neutral (50)</div>
          </div>
        </div>
      </div>
    </div>
  )
}