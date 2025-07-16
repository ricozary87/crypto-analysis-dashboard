import React, { useEffect, useRef, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
  BarElement,
  LineElement,
  PointElement
} from 'chart.js'
import { Chart } from 'react-chartjs-2'
import 'chartjs-adapter-date-fns'
import { CandlestickController, CandlestickElement, OhlcController, OhlcElement } from 'chartjs-chart-financial'
import { calculateEMA, calculateRSI, calculateMACD, calculateBollingerBands } from '../services/indicators'

ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
  BarElement,
  LineElement,
  PointElement,
  CandlestickController,
  CandlestickElement,
  OhlcController,
  OhlcElement
)

export default function ChartView({ data, pair, timeframe, chartType, indicators }) {
  const chartRef = useRef(null)
  const [chartOptions, setChartOptions] = useState({})

  // Generate chart data based on type and indicators
  const generateChartData = () => {
    if (!data || data.length === 0) return { datasets: [] }

    const datasets = []
    
    // Main price data
    if (chartType === 'candlestick') {
      datasets.push({
        label: pair,
        data: data.map(d => ({
          x: new Date(d.time),
          o: d.open,
          h: d.high,
          l: d.low,
          c: d.close
        })),
        type: 'candlestick',
        color: {
          up: '#10b981',
          down: '#ef4444',
          unchanged: '#6b7280'
        }
      })
    } else if (chartType === 'ohlc') {
      datasets.push({
        label: pair,
        data: data.map(d => ({
          x: new Date(d.time),
          o: d.open,
          h: d.high,
          l: d.low,
          c: d.close
        })),
        type: 'ohlc',
        color: {
          up: '#10b981',
          down: '#ef4444',
          unchanged: '#6b7280'
        }
      })
    } else if (chartType === 'line') {
      datasets.push({
        label: pair,
        data: data.map(d => ({
          x: new Date(d.time),
          y: d.close
        })),
        type: 'line',
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.1
      })
    }

    // Add indicators
    if (indicators.ema9) {
      const ema9Data = calculateEMA(data.map(d => d.close), 9)
      datasets.push({
        label: 'EMA 9',
        data: ema9Data.map((value, index) => ({
          x: new Date(data[index].time),
          y: value
        })),
        type: 'line',
        borderColor: '#f59e0b',
        backgroundColor: 'transparent',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.1
      })
    }

    if (indicators.ema200) {
      const ema200Data = calculateEMA(data.map(d => d.close), 200)
      datasets.push({
        label: 'EMA 200',
        data: ema200Data.map((value, index) => ({
          x: new Date(data[index].time),
          y: value
        })),
        type: 'line',
        borderColor: '#ec4899',
        backgroundColor: 'transparent',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.1
      })
    }

    if (indicators.bollinger) {
      const bollingerData = calculateBollingerBands(data.map(d => d.close), 20, 2)
      
      datasets.push({
        label: 'Bollinger Upper',
        data: bollingerData.upper.map((value, index) => ({
          x: new Date(data[index].time),
          y: value
        })),
        type: 'line',
        borderColor: 'rgba(156, 163, 175, 0.5)',
        backgroundColor: 'transparent',
        borderWidth: 1,
        pointRadius: 0,
        borderDash: [5, 5]
      })

      datasets.push({
        label: 'Bollinger Lower',
        data: bollingerData.lower.map((value, index) => ({
          x: new Date(data[index].time),
          y: value
        })),
        type: 'line',
        borderColor: 'rgba(156, 163, 175, 0.5)',
        backgroundColor: 'transparent',
        borderWidth: 1,
        pointRadius: 0,
        borderDash: [5, 5]
      })
    }

    return { datasets }
  }

  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          color: '#e5e7eb',
          usePointStyle: true,
          pointStyle: 'line'
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(17, 24, 39, 0.9)',
        titleColor: '#e5e7eb',
        bodyColor: '#e5e7eb',
        borderColor: '#374151',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            const label = context.dataset.label || ''
            if (context.parsed.o !== undefined) {
              return `${label}: O: ${context.parsed.o.toFixed(2)}, H: ${context.parsed.h.toFixed(2)}, L: ${context.parsed.l.toFixed(2)}, C: ${context.parsed.c.toFixed(2)}`
            }
            return `${label}: ${context.parsed.y.toFixed(2)}`
          }
        }
      }
    },
    scales: {
      x: {
        type: 'time',
        time: {
          tooltipFormat: 'MMM dd, HH:mm',
          displayFormats: {
            minute: 'HH:mm',
            hour: 'MMM dd HH:mm',
            day: 'MMM dd',
            week: 'MMM dd',
            month: 'MMM yyyy'
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
      }
    },
    animation: {
      duration: 750
    }
  }

  return (
    <div className="chart-container">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-dark-text">{pair} - {timeframe}</h3>
        <div className="flex items-center space-x-2 text-sm text-dark-muted">
          <span>Last updated: {new Date().toLocaleTimeString()}</span>
        </div>
      </div>
      
      <div className="h-96">
        <Chart
          ref={chartRef}
          type={chartType}
          data={generateChartData()}
          options={options}
        />
      </div>

      {/* Sub-charts for RSI and MACD */}
      {(indicators.rsi || indicators.macd) && (
        <div className="mt-4 space-y-4">
          {indicators.rsi && (
            <div className="h-24 bg-dark-bg rounded-lg p-3 border border-dark-border">
              <RSIChart data={data} />
            </div>
          )}
          
          {indicators.macd && (
            <div className="h-24 bg-dark-bg rounded-lg p-3 border border-dark-border">
              <MACDChart data={data} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// RSI Sub-chart Component
function RSIChart({ data }) {
  const rsiData = calculateRSI(data.map(d => d.close), 14)
  
  const chartData = {
    labels: data.map(d => new Date(d.time)),
    datasets: [
      {
        label: 'RSI',
        data: rsiData,
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        fill: true,
        tension: 0.1,
        pointRadius: 0
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      x: { display: false },
      y: {
        min: 0,
        max: 100,
        ticks: {
          color: '#9ca3af',
          stepSize: 20
        },
        grid: {
          color: 'rgba(55, 65, 81, 0.3)'
        }
      }
    }
  }

  return (
    <div className="h-full">
      <div className="text-xs text-dark-muted mb-1">RSI (14)</div>
      <Chart type="line" data={chartData} options={options} />
    </div>
  )
}

// MACD Sub-chart Component
function MACDChart({ data }) {
  const macdData = calculateMACD(data.map(d => d.close), 12, 26, 9)
  
  const chartData = {
    labels: data.map(d => new Date(d.time)),
    datasets: [
      {
        label: 'MACD',
        data: macdData.macd,
        borderColor: '#06b6d4',
        backgroundColor: 'transparent',
        type: 'line',
        tension: 0.1,
        pointRadius: 0
      },
      {
        label: 'Signal',
        data: macdData.signal,
        borderColor: '#f97316',
        backgroundColor: 'transparent',
        type: 'line',
        tension: 0.1,
        pointRadius: 0
      },
      {
        label: 'Histogram',
        data: macdData.histogram,
        backgroundColor: macdData.histogram.map(h => h > 0 ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)'),
        type: 'bar'
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      x: { display: false },
      y: {
        ticks: {
          color: '#9ca3af'
        },
        grid: {
          color: 'rgba(55, 65, 81, 0.3)'
        }
      }
    }
  }

  return (
    <div className="h-full">
      <div className="text-xs text-dark-muted mb-1">MACD (12,26,9)</div>
      <Chart type="line" data={chartData} options={options} />
    </div>
  )
}