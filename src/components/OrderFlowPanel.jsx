import React, { useMemo } from 'react'
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { clsx } from 'clsx'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

export default function OrderFlowPanel({ data, orderbook }) {
  // Generate order flow data
  const orderFlowData = useMemo(() => {
    if (!data || data.length === 0) return null
    
    const recentData = data.slice(-50) // Last 50 candles
    
    return recentData.map((candle, index) => {
      const volume = candle.volume
      const isGreen = candle.close > candle.open
      
      // Simulate buy/sell volume breakdown
      const buyVolume = isGreen ? volume * 0.6 : volume * 0.4
      const sellVolume = volume - buyVolume
      
      // Simulate footprint data
      const priceRange = candle.high - candle.low
      const priceStep = priceRange / 10
      const footprint = []
      
      for (let i = 0; i < 10; i++) {
        const price = candle.low + (i * priceStep)
        const levelVolume = volume * (Math.random() * 0.2 + 0.05) // Random distribution
        footprint.push({
          price,
          buyVolume: levelVolume * (isGreen ? 0.6 : 0.4),
          sellVolume: levelVolume * (isGreen ? 0.4 : 0.6),
          delta: (levelVolume * (isGreen ? 0.6 : 0.4)) - (levelVolume * (isGreen ? 0.4 : 0.6))
        })
      }
      
      return {
        time: candle.time,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
        volume: volume,
        buyVolume,
        sellVolume,
        delta: buyVolume - sellVolume,
        footprint
      }
    })
  }, [data])

  // Generate volume profile data
  const volumeProfile = useMemo(() => {
    if (!orderFlowData) return null
    
    const allCandles = orderFlowData.slice(-20) // Last 20 candles for profile
    const minPrice = Math.min(...allCandles.map(c => c.low))
    const maxPrice = Math.max(...allCandles.map(c => c.high))
    const priceRange = maxPrice - minPrice
    const levels = 20
    const priceStep = priceRange / levels
    
    const profile = []
    
    for (let i = 0; i < levels; i++) {
      const price = minPrice + (i * priceStep)
      let volume = 0
      
      // Calculate volume at this price level
      allCandles.forEach(candle => {
        if (price >= candle.low && price <= candle.high) {
          volume += candle.volume / levels // Distribute volume evenly
        }
      })
      
      profile.push({
        price,
        volume,
        buyVolume: volume * 0.55, // Slightly more buys
        sellVolume: volume * 0.45
      })
    }
    
    return profile
  }, [orderFlowData])

  const volumeChartData = {
    labels: orderFlowData ? orderFlowData.map(d => new Date(d.time).toLocaleTimeString()) : [],
    datasets: [
      {
        label: 'Buy Volume',
        data: orderFlowData ? orderFlowData.map(d => d.buyVolume) : [],
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 1
      },
      {
        label: 'Sell Volume',
        data: orderFlowData ? orderFlowData.map(d => -d.sellVolume) : [],
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 1
      }
    ]
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#e5e7eb',
          usePointStyle: true
        }
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.9)',
        titleColor: '#e5e7eb',
        bodyColor: '#e5e7eb',
        borderColor: '#374151',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#9ca3af',
          maxTicksLimit: 10
        },
        grid: {
          color: 'rgba(55, 65, 81, 0.3)'
        }
      },
      y: {
        ticks: {
          color: '#9ca3af',
          callback: function(value) {
            return Math.abs(value).toFixed(0)
          }
        },
        grid: {
          color: 'rgba(55, 65, 81, 0.3)'
        }
      }
    }
  }

  const formatVolume = (volume) => {
    if (volume >= 1000000) return (volume / 1000000).toFixed(1) + 'M'
    if (volume >= 1000) return (volume / 1000).toFixed(1) + 'K'
    return volume.toFixed(0)
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Order Flow Chart */}
      <div className="panel">
        <h3 className="text-lg font-semibold text-dark-text mb-4">Order Flow</h3>
        <div className="h-48">
          <Bar data={volumeChartData} options={chartOptions} />
        </div>
      </div>

      {/* Volume Profile */}
      <div className="panel">
        <h3 className="text-lg font-semibold text-dark-text mb-4">Volume Profile</h3>
        <div className="h-48 overflow-y-auto scrollbar-thin">
          {volumeProfile && volumeProfile.map((level, index) => (
            <div key={index} className="flex items-center justify-between py-1 text-xs">
              <div className="w-16 text-right text-dark-muted">
                ${level.price.toFixed(2)}
              </div>
              <div className="flex-1 mx-2 relative">
                <div className="flex">
                  <div 
                    className="bg-trading-green bg-opacity-60 h-4 rounded-l"
                    style={{ width: `${(level.buyVolume / Math.max(...volumeProfile.map(l => l.volume))) * 100}%` }}
                  />
                  <div 
                    className="bg-trading-red bg-opacity-60 h-4 rounded-r"
                    style={{ width: `${(level.sellVolume / Math.max(...volumeProfile.map(l => l.volume))) * 100}%` }}
                  />
                </div>
              </div>
              <div className="w-16 text-left text-dark-muted">
                {formatVolume(level.volume)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Delta Analysis */}
      <div className="panel">
        <h3 className="text-lg font-semibold text-dark-text mb-4">Delta Analysis</h3>
        <div className="space-y-3">
          {orderFlowData && orderFlowData.slice(-10).map((candle, index) => (
            <div key={index} className="flex items-center justify-between">
              <div className="text-sm text-dark-muted">
                {new Date(candle.time).toLocaleTimeString()}
              </div>
              <div className={clsx(
                'text-sm font-medium',
                candle.delta > 0 ? 'text-trading-green' : 'text-trading-red'
              )}>
                {candle.delta > 0 ? '+' : ''}{formatVolume(candle.delta)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footprint Cluster */}
      <div className="panel">
        <h3 className="text-lg font-semibold text-dark-text mb-4">Footprint Cluster</h3>
        <div className="h-48 overflow-y-auto scrollbar-thin">
          {orderFlowData && orderFlowData[orderFlowData.length - 1]?.footprint.map((level, index) => (
            <div key={index} className="flex items-center justify-between py-1 text-xs">
              <div className="w-16 text-right text-dark-muted">
                ${level.price.toFixed(2)}
              </div>
              <div className="flex space-x-2">
                <div className="w-12 text-right text-trading-green">
                  {formatVolume(level.buyVolume)}
                </div>
                <div className="w-12 text-right text-trading-red">
                  {formatVolume(level.sellVolume)}
                </div>
                <div className={clsx(
                  'w-12 text-right font-medium',
                  level.delta > 0 ? 'text-trading-green' : 'text-trading-red'
                )}>
                  {level.delta > 0 ? '+' : ''}{formatVolume(level.delta)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}