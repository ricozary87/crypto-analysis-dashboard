import React, { useEffect, useRef, useState } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, TimeScale, BarElement, LineElement, PointElement, Tooltip, Legend } from 'chart.js'
import { Chart } from 'react-chartjs-2'
import { CandlestickController, CandlestickElement, OhlcController, OhlcElement } from 'chartjs-chart-financial'
import 'chartjs-adapter-date-fns'
import { calculateEMA, calculateRSI, calculateMACD, calculateBollingerBands, calculateStochastic } from '../services/indicators'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  BarElement,
  LineElement,
  PointElement,
  Tooltip,
  Legend,
  CandlestickController,
  CandlestickElement,
  OhlcController,
  OhlcElement
)

export default function ChartView({ data, pair, timeframe, chartType, indicators }) {
  const chartRef = useRef(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (data && data.length > 0) {
      setIsLoading(false)
    }
  }, [data])

  if (isLoading || !data || data.length === 0) {
    return (
      <div className="chart-container h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-trading-blue mb-4"></div>
          <p className="text-dark-muted">Loading chart data...</p>
        </div>
      </div>
    )
  }

  // Prepare chart data
  const chartData = {
    datasets: []
  }

  // Main price data
  const priceData = data.map(candle => ({
    x: candle.time,
    o: candle.open,
    h: candle.high,
    l: candle.low,
    c: candle.close
  }))

  // Volume data
  const volumeData = data.map(candle => ({
    x: candle.time,
    y: candle.volume
  }))

  // Add main price dataset based on chart type
  if (chartType === 'candlestick') {
    chartData.datasets.push({
      type: 'candlestick',
      label: pair,
      data: priceData,
      borderColor: function(context) {
        const dataPoint = context.parsed
        return dataPoint.c >= dataPoint.o ? '#10b981' : '#ef4444'
      },
      backgroundColor: function(context) {
        const dataPoint = context.parsed
        return dataPoint.c >= dataPoint.o ? '#10b981' : '#ef4444'
      },
      borderWidth: 1,
      yAxisID: 'y'
    })
  } else if (chartType === 'ohlc') {
    chartData.datasets.push({
      type: 'ohlc',
      label: pair,
      data: priceData,
      borderColor: function(context) {
        const dataPoint = context.parsed
        return dataPoint.c >= dataPoint.o ? '#10b981' : '#ef4444'
      },
      borderWidth: 2,
      yAxisID: 'y'
    })
  } else if (chartType === 'line') {
    const lineData = data.map(candle => ({
      x: candle.time,
      y: candle.close
    }))
    
    chartData.datasets.push({
      type: 'line',
      label: pair,
      data: lineData,
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderWidth: 2,
      fill: false,
      pointRadius: 0,
      pointHoverRadius: 4,
      yAxisID: 'y'
    })
  }

  // Add volume dataset
  if (indicators.volume) {
    chartData.datasets.push({
      type: 'bar',
      label: 'Volume',
      data: volumeData,
      backgroundColor: 'rgba(59, 130, 246, 0.3)',
      borderColor: '#3b82f6',
      borderWidth: 1,
      yAxisID: 'y1'
    })
  }

  // Add technical indicators
  const closes = data.map(candle => candle.close)
  const highs = data.map(candle => candle.high)
  const lows = data.map(candle => candle.low)
  const volumes = data.map(candle => candle.volume)

  if (indicators.ema9) {
    const ema9 = calculateEMA(closes, 9)
    const ema9Data = data.map((candle, index) => ({
      x: candle.time,
      y: ema9[index]
    })).filter(point => point.y !== null)

    chartData.datasets.push({
      type: 'line',
      label: 'EMA 9',
      data: ema9Data,
      borderColor: '#f59e0b',
      backgroundColor: 'rgba(245, 158, 11, 0.1)',
      borderWidth: 2,
      fill: false,
      pointRadius: 0,
      pointHoverRadius: 4,
      yAxisID: 'y'
    })
  }

  if (indicators.ema200) {
    const ema200 = calculateEMA(closes, 200)
    const ema200Data = data.map((candle, index) => ({
      x: candle.time,
      y: ema200[index]
    })).filter(point => point.y !== null)

    chartData.datasets.push({
      type: 'line',
      label: 'EMA 200',
      data: ema200Data,
      borderColor: '#ec4899',
      backgroundColor: 'rgba(236, 72, 153, 0.1)',
      borderWidth: 2,
      fill: false,
      pointRadius: 0,
      pointHoverRadius: 4,
      yAxisID: 'y'
    })
  }

  if (indicators.bollinger) {
    const bollinger = calculateBollingerBands(closes, 20, 2)
    const upperData = data.map((candle, index) => ({
      x: candle.time,
      y: bollinger.upper[index]
    })).filter(point => point.y !== null)

    const lowerData = data.map((candle, index) => ({
      x: candle.time,
      y: bollinger.lower[index]
    })).filter(point => point.y !== null)

    chartData.datasets.push({
      type: 'line',
      label: 'Bollinger Upper',
      data: upperData,
      borderColor: '#9ca3af',
      backgroundColor: 'rgba(156, 163, 175, 0.1)',
      borderWidth: 1,
      fill: false,
      pointRadius: 0,
      yAxisID: 'y'
    })

    chartData.datasets.push({
      type: 'line',
      label: 'Bollinger Lower',
      data: lowerData,
      borderColor: '#9ca3af',
      backgroundColor: 'rgba(156, 163, 175, 0.1)',
      borderWidth: 1,
      fill: '+1',
      pointRadius: 0,
      yAxisID: 'y'
    })
  }

  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#e5e7eb',
          usePointStyle: true,
          filter: function(item, chart) {
            return !item.text.includes('Bollinger')
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.9)',
        titleColor: '#e5e7eb',
        bodyColor: '#e5e7eb',
        borderColor: '#374151',
        borderWidth: 1,
        callbacks: {
          title: function(context) {
            return new Date(context[0].parsed.x).toLocaleString()
          },
          label: function(context) {
            if (context.dataset.type === 'candlestick' || context.dataset.type === 'ohlc') {
              const data = context.parsed
              return [
                `Open: $${data.o?.toFixed(2)}`,
                `High: $${data.h?.toFixed(2)}`,
                `Low: $${data.l?.toFixed(2)}`,
                `Close: $${data.c?.toFixed(2)}`
              ]
            } else if (context.dataset.label === 'Volume') {
              return `Volume: ${context.parsed.y?.toLocaleString()}`
            } else {
              return `${context.dataset.label}: $${context.parsed.y?.toFixed(2)}`
            }
          }
        }
      }
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: timeframe === '1D' ? 'day' : timeframe === '1W' ? 'week' : 'hour',
          displayFormats: {
            hour: 'HH:mm',
            day: 'MM/dd',
            week: 'MM/dd'
          }
        },
        ticks: {
          color: '#9ca3af',
          maxTicksLimit: 10
        },
        grid: {
          color: 'rgba(55, 65, 81, 0.3)'
        }
      },
      y: {
        type: 'linear',
        position: 'right',
        ticks: {
          color: '#9ca3af',
          callback: function(value) {
            return '$' + value.toFixed(2)
          }
        },
        grid: {
          color: 'rgba(55, 65, 81, 0.3)'
        }
      },
      y1: {
        type: 'linear',
        position: 'left',
        display: indicators.volume,
        ticks: {
          color: '#9ca3af',
          callback: function(value) {
            if (value >= 1e9) return (value / 1e9).toFixed(1) + 'B'
            if (value >= 1e6) return (value / 1e6).toFixed(1) + 'M'
            if (value >= 1e3) return (value / 1e3).toFixed(1) + 'K'
            return value.toFixed(0)
          }
        },
        grid: {
          display: false
        }
      }
    }
  }

  return (
    <div className="chart-container h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-dark-text">
          {pair} - {timeframe}
        </h3>
        <div className="flex items-center space-x-2 text-sm text-dark-muted">
          <span>Last: ${data[data.length - 1]?.close?.toFixed(2)}</span>
          <span>•</span>
          <span>Vol: {(data[data.length - 1]?.volume || 0).toLocaleString()}</span>
        </div>
      </div>
      
      <div className="h-[calc(100%-4rem)]">
        <Chart
          ref={chartRef}
          type="candlestick"
          data={chartData}
          options={options}
        />
      </div>
    </div>
  )
}