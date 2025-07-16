import React, { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import ChartView from './components/ChartView'
import OverviewPanel from './components/OverviewPanel'
import HeatmapLiquidity from './components/HeatmapLiquidity'
import OrderFlowPanel from './components/OrderFlowPanel'
import IndicatorsPanel from './components/IndicatorsPanel'
import { generateDummyData } from './services/dummyData'
import { generateDummyOrderbook } from './services/orderbook'

export default function App() {
  const [selectedPair, setSelectedPair] = useState('BTC/USDT')
  const [selectedTimeframe, setSelectedTimeframe] = useState('1H')
  const [chartType, setChartType] = useState('candlestick')
  const [chartData, setChartData] = useState([])
  const [orderbook, setOrderbook] = useState({ bids: [], asks: [] })
  const [indicators, setIndicators] = useState({
    ema9: true,
    ema200: true,
    rsi: false,
    macd: false,
    bollinger: false
  })

  // Simulate real-time data updates
  useEffect(() => {
    const updateData = () => {
      const newData = generateDummyData(selectedPair, selectedTimeframe, 200)
      setChartData(newData)
      setOrderbook(generateDummyOrderbook(newData[newData.length - 1]?.close || 45000))
    }

    updateData()
    const interval = setInterval(updateData, 5000) // Update every 5 seconds

    return () => clearInterval(interval)
  }, [selectedPair, selectedTimeframe])

  const handlePairChange = (pair) => {
    setSelectedPair(pair)
  }

  const handleTimeframeChange = (timeframe) => {
    setSelectedTimeframe(timeframe)
  }

  const handleChartTypeChange = (type) => {
    setChartType(type)
  }

  const handleIndicatorToggle = (indicator) => {
    setIndicators(prev => ({
      ...prev,
      [indicator]: !prev[indicator]
    }))
  }

  return (
    <div className="min-h-screen bg-dark-bg text-dark-text">
      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-64 flex-shrink-0">
          <Sidebar 
            selectedPair={selectedPair}
            onPairChange={handlePairChange}
          />
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Topbar */}
          <Topbar 
            selectedPair={selectedPair}
            selectedTimeframe={selectedTimeframe}
            chartType={chartType}
            onPairChange={handlePairChange}
            onTimeframeChange={handleTimeframeChange}
            onChartTypeChange={handleChartTypeChange}
          />

          {/* Content Area */}
          <div className="flex-1 grid grid-cols-12 gap-4 p-4">
            {/* Left Column - Overview & Indicators */}
            <div className="col-span-3 space-y-4">
              <OverviewPanel 
                pair={selectedPair}
                data={chartData}
                orderbook={orderbook}
              />
              <IndicatorsPanel 
                indicators={indicators}
                onToggle={handleIndicatorToggle}
              />
            </div>

            {/* Main Chart Area */}
            <div className="col-span-6 space-y-4">
              <ChartView 
                data={chartData}
                pair={selectedPair}
                timeframe={selectedTimeframe}
                chartType={chartType}
                indicators={indicators}
              />
              
              {/* Order Flow Panel */}
              <OrderFlowPanel 
                data={chartData}
                orderbook={orderbook}
              />
            </div>

            {/* Right Column - Heatmap & Additional Tools */}
            <div className="col-span-3 space-y-4">
              <HeatmapLiquidity 
                orderbook={orderbook}
                currentPrice={chartData[chartData.length - 1]?.close || 45000}
              />
              
              {/* Future: SMC Analysis Panel */}
              <div className="panel">
                <h3 className="font-semibold mb-4">SMC Analysis</h3>
                <div className="text-dark-muted text-sm">
                  <p>• Order Blocks: Ready for integration</p>
                  <p>• Fair Value Gaps: Ready for integration</p>
                  <p>• Liquidity Sweeps: Ready for integration</p>
                </div>
              </div>

              {/* Future: AI Panel */}
              <div className="panel">
                <h3 className="font-semibold mb-4">AI Analysis</h3>
                <div className="text-dark-muted text-sm">
                  <p>• GPT Signals: Ready for integration</p>
                  <p>• AI Recommendations: Ready for integration</p>
                  <p>• Sentiment Analysis: Ready for integration</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}