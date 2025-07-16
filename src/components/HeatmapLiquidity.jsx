import React, { useMemo } from 'react'
import { clsx } from 'clsx'

export default function HeatmapLiquidity({ orderbook, currentPrice }) {
  // Generate heatmap data based on orderbook
  const heatmapData = useMemo(() => {
    if (!orderbook.bids || !orderbook.asks) return []
    
    const priceRange = currentPrice * 0.02 // 2% range around current price
    const minPrice = currentPrice - priceRange
    const maxPrice = currentPrice + priceRange
    const gridSize = 20
    const priceStep = (maxPrice - minPrice) / gridSize
    
    const grid = []
    
    for (let i = 0; i < gridSize; i++) {
      const price = minPrice + (i * priceStep)
      const row = []
      
      for (let j = 0; j < gridSize; j++) {
        const timeOffset = j * 5 // 5 minute intervals
        
        // Find closest bid/ask for this price level
        const closestBid = orderbook.bids.find(bid => Math.abs(parseFloat(bid[0]) - price) < priceStep)
        const closestAsk = orderbook.asks.find(ask => Math.abs(parseFloat(ask[0]) - price) < priceStep)
        
        let intensity = 0
        let type = 'neutral'
        
        if (closestBid) {
          intensity = Math.min(parseFloat(closestBid[1]) / 100, 1) // Normalize volume
          type = 'bid'
        } else if (closestAsk) {
          intensity = Math.min(parseFloat(closestAsk[1]) / 100, 1) // Normalize volume
          type = 'ask'
        }
        
        // Add some randomness for visualization
        intensity = Math.max(intensity, Math.random() * 0.3)
        
        row.push({
          price,
          time: timeOffset,
          intensity,
          type,
          volume: intensity * 1000
        })
      }
      
      grid.push(row)
    }
    
    return grid
  }, [orderbook, currentPrice])

  const getCellColor = (cell) => {
    const alpha = Math.max(0.1, cell.intensity)
    
    if (cell.type === 'bid') {
      return `rgba(16, 185, 129, ${alpha})` // Green for bids
    } else if (cell.type === 'ask') {
      return `rgba(239, 68, 68, ${alpha})` // Red for asks
    }
    
    return `rgba(107, 114, 128, ${alpha})` // Gray for neutral
  }

  const formatPrice = (price) => {
    return price.toFixed(2)
  }

  const formatVolume = (volume) => {
    if (volume >= 1000) return (volume / 1000).toFixed(1) + 'K'
    return volume.toFixed(0)
  }

  return (
    <div className="panel">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-dark-text">Liquidity Heatmap</h3>
        <div className="flex items-center space-x-2 text-xs text-dark-muted">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-sm bg-trading-green bg-opacity-60"></div>
            <span>Bids</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-sm bg-trading-red bg-opacity-60"></div>
            <span>Asks</span>
          </div>
        </div>
      </div>

      {/* Current Price Indicator */}
      <div className="mb-4 text-center">
        <div className="text-sm text-dark-muted">Current Price</div>
        <div className="text-xl font-bold text-trading-blue">
          ${currentPrice.toLocaleString()}
        </div>
      </div>

      {/* Heatmap Grid */}
      <div className="relative">
        <div className="grid grid-cols-20 gap-px bg-dark-border rounded-lg overflow-hidden">
          {heatmapData.map((row, rowIndex) => 
            row.map((cell, colIndex) => (
              <div
                key={`${rowIndex}-${colIndex}`}
                className="heatmap-cell aspect-square relative group cursor-pointer"
                style={{
                  backgroundColor: getCellColor(cell),
                  border: `1px solid ${cell.type === 'bid' ? '#10b981' : cell.type === 'ask' ? '#ef4444' : '#374151'}`
                }}
                title={`Price: $${formatPrice(cell.price)}\nVolume: ${formatVolume(cell.volume)}\nType: ${cell.type}`}
              >
                {/* Tooltip on hover */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 whitespace-nowrap">
                  <div>${formatPrice(cell.price)}</div>
                  <div>{formatVolume(cell.volume)}</div>
                  <div className="capitalize">{cell.type}</div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Price Scale */}
        <div className="absolute -left-16 top-0 h-full flex flex-col justify-between text-xs text-dark-muted">
          {Array.from({ length: 5 }, (_, i) => {
            const price = currentPrice + (currentPrice * 0.02) - (i * currentPrice * 0.01)
            return (
              <div key={i} className="text-right">
                ${formatPrice(price)}
              </div>
            )
          })}
        </div>

        {/* Time Scale */}
        <div className="flex justify-between mt-2 text-xs text-dark-muted">
          <span>Now</span>
          <span>5m</span>
          <span>10m</span>
          <span>15m</span>
          <span>20m</span>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 p-3 bg-dark-bg rounded-lg">
        <div className="text-sm font-medium text-dark-text mb-2">Liquidity Intensity</div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-dark-muted">Low</span>
          <div className="flex space-x-1">
            {[0.2, 0.4, 0.6, 0.8, 1.0].map((intensity, i) => (
              <div
                key={i}
                className="w-4 h-4 rounded-sm"
                style={{
                  backgroundColor: `rgba(16, 185, 129, ${intensity})`
                }}
              />
            ))}
          </div>
          <span className="text-xs text-dark-muted">High</span>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-dark-muted">Bid Liquidity</div>
          <div className="font-medium text-trading-green">
            {formatVolume(orderbook.bids?.reduce((sum, bid) => sum + parseFloat(bid[1]), 0) || 0)}
          </div>
        </div>
        <div>
          <div className="text-dark-muted">Ask Liquidity</div>
          <div className="font-medium text-trading-red">
            {formatVolume(orderbook.asks?.reduce((sum, ask) => sum + parseFloat(ask[1]), 0) || 0)}
          </div>
        </div>
      </div>
    </div>
  )
}