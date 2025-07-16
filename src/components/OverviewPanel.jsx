import React from 'react'
import { TrendingUp, TrendingDown, Activity, Volume, DollarSign, Clock } from 'lucide-react'
import { clsx } from 'clsx'
import { calculateOrderbookMetrics } from '../services/orderbook'

export default function OverviewPanel({ pair, data, orderbook }) {
  // Calculate metrics
  const currentCandle = data && data.length > 0 ? data[data.length - 1] : null
  const previousCandle = data && data.length > 1 ? data[data.length - 2] : null
  
  const currentPrice = currentCandle?.close || 0
  const previousPrice = previousCandle?.close || 0
  const priceChange = currentPrice - previousPrice
  const priceChangePercent = previousPrice > 0 ? (priceChange / previousPrice) * 100 : 0
  
  const volume24h = data?.reduce((sum, candle) => sum + candle.volume, 0) || 0
  const high24h = data?.reduce((max, candle) => Math.max(max, candle.high), 0) || 0
  const low24h = data?.reduce((min, candle) => Math.min(min, candle.low), Infinity) || 0
  
  const orderbookMetrics = calculateOrderbookMetrics(orderbook)

  const formatPrice = (price) => {
    if (price >= 1000) return price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    if (price >= 1) return price.toFixed(4)
    return price.toFixed(6)
  }

  const formatVolume = (volume) => {
    if (volume >= 1e9) return `${(volume / 1e9).toFixed(1)}B`
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M`
    if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K`
    return volume.toFixed(0)
  }

  const formatPercent = (percent) => {
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`
  }

  return (
    <div className="panel">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-dark-text">Market Overview</h3>
        <div className="flex items-center space-x-1 text-xs text-dark-muted">
          <Clock className="w-3 h-3" />
          <span>Real-time</span>
        </div>
      </div>

      {/* Current Price */}
      <div className="mb-6">
        <div className="text-2xl font-bold text-dark-text mb-1">
          ${formatPrice(currentPrice)}
        </div>
        <div className={clsx(
          'flex items-center space-x-1 text-sm font-medium',
          priceChange >= 0 ? 'text-trading-green' : 'text-trading-red'
        )}>
          {priceChange >= 0 ? (
            <TrendingUp className="w-4 h-4" />
          ) : (
            <TrendingDown className="w-4 h-4" />
          )}
          <span>{formatPercent(priceChangePercent)}</span>
          <span className="text-dark-muted">
            (${Math.abs(priceChange).toFixed(2)})
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-dark-bg rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-dark-muted">24h High</span>
            <TrendingUp className="w-4 h-4 text-trading-green" />
          </div>
          <div className="text-lg font-semibold text-dark-text">
            ${formatPrice(high24h)}
          </div>
        </div>

        <div className="bg-dark-bg rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-dark-muted">24h Low</span>
            <TrendingDown className="w-4 h-4 text-trading-red" />
          </div>
          <div className="text-lg font-semibold text-dark-text">
            ${formatPrice(low24h)}
          </div>
        </div>
      </div>

      {/* Volume & Trading */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-dark-muted">24h Volume</span>
          <Volume className="w-4 h-4 text-trading-blue" />
        </div>
        <div className="text-lg font-semibold text-dark-text">
          {formatVolume(volume24h)}
        </div>
        <div className="text-sm text-dark-muted">
          ≈ ${formatVolume(volume24h * currentPrice)}
        </div>
      </div>

      {/* Orderbook Summary */}
      <div className="border-t border-dark-border pt-4">
        <h4 className="text-sm font-medium text-dark-text mb-3">Orderbook</h4>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-dark-muted">Best Bid</span>
            <span className="text-sm font-medium text-trading-green">
              ${formatPrice(orderbookMetrics.bestBid)}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-dark-muted">Best Ask</span>
            <span className="text-sm font-medium text-trading-red">
              ${formatPrice(orderbookMetrics.bestAsk)}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-dark-muted">Spread</span>
            <span className="text-sm font-medium text-dark-text">
              ${orderbookMetrics.spread.toFixed(2)} ({orderbookMetrics.spreadPercent.toFixed(3)}%)
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-dark-muted">Bid Volume</span>
            <span className="text-sm font-medium text-trading-green">
              {formatVolume(orderbookMetrics.bidVolume)}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-dark-muted">Ask Volume</span>
            <span className="text-sm font-medium text-trading-red">
              {formatVolume(orderbookMetrics.askVolume)}
            </span>
          </div>
        </div>
      </div>

      {/* Market Sentiment */}
      <div className="border-t border-dark-border pt-4 mt-4">
        <h4 className="text-sm font-medium text-dark-text mb-3">Market Sentiment</h4>
        
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-dark-muted">Order Imbalance</span>
          <span className={clsx(
            'text-sm font-medium',
            orderbookMetrics.imbalance > 0 ? 'text-trading-green' : 'text-trading-red'
          )}>
            {(orderbookMetrics.imbalance * 100).toFixed(1)}%
          </span>
        </div>
        
        {/* Imbalance Bar */}
        <div className="w-full bg-dark-bg rounded-full h-2 mb-3">
          <div 
            className={clsx(
              'h-2 rounded-full transition-all duration-300',
              orderbookMetrics.imbalance > 0 ? 'bg-trading-green' : 'bg-trading-red'
            )}
            style={{ 
              width: `${Math.abs(orderbookMetrics.imbalance) * 100}%`,
              marginLeft: orderbookMetrics.imbalance < 0 ? `${(1 + orderbookMetrics.imbalance) * 100}%` : '0'
            }}
          />
        </div>
        
        <div className="text-xs text-dark-muted text-center">
          {orderbookMetrics.imbalance > 0.1 ? 'Bullish' : 
           orderbookMetrics.imbalance < -0.1 ? 'Bearish' : 'Neutral'}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="border-t border-dark-border pt-4 mt-4">
        <div className="grid grid-cols-2 gap-2">
          <button className="flex items-center justify-center space-x-2 px-3 py-2 bg-trading-green hover:bg-green-600 text-white rounded-lg text-sm font-medium transition-colors">
            <TrendingUp className="w-4 h-4" />
            <span>Buy</span>
          </button>
          <button className="flex items-center justify-center space-x-2 px-3 py-2 bg-trading-red hover:bg-red-600 text-white rounded-lg text-sm font-medium transition-colors">
            <TrendingDown className="w-4 h-4" />
            <span>Sell</span>
          </button>
        </div>
      </div>
    </div>
  )
}