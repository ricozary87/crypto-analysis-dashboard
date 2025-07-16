import React, { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import ChartView from './components/ChartView'
import OverviewPanel from './components/OverviewPanel'
import HeatmapLiquidity from './components/HeatmapLiquidity'
import OrderFlowPanel from './components/OrderFlowPanel'
import IndicatorsPanel from './components/IndicatorsPanel'
import { generateDummyData, getCurrentMarketData } from './services/dummyData'
import { generateDummyOrderbook } from './services/orderbook'
import { wsManager } from './services/api'

function App() {
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
    bollinger: false,
    stoch: false,
    volume: false,
    obv: false
  })
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState(new Date())

  // Initialize data
  useEffect(() => {
    loadInitialData()
    
    // Setup real-time updates
    const interval = setInterval(updateData, 5000) // Update every 5 seconds
    
    return () => clearInterval(interval)
  }, [selectedPair, selectedTimeframe])

  // Load initial data
  const loadInitialData = async () => {
    setIsLoading(true)
    
    try {
      // Generate dummy data for the selected pair and timeframe
      const data = generateDummyData(selectedPair, selectedTimeframe, 200)
      setChartData(data)
      
      // Get current price for orderbook
      const currentPrice = data[data.length - 1]?.close || 45000
      const orderbookData = generateDummyOrderbook(currentPrice)
      setOrderbook(orderbookData)
      
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error loading initial data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Update data periodically
  const updateData = async () => {
    try {
      // Update chart data with new candle
      const newData = generateDummyData(selectedPair, selectedTimeframe, 200)
      setChartData(newData)
      
      // Update orderbook
      const currentPrice = newData[newData.length - 1]?.close || 45000
      const orderbookData = generateDummyOrderbook(currentPrice)
      setOrderbook(orderbookData)
      
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error updating data:', error)
    }
  }

  // Handle pair change
  const handlePairChange = (pair) => {
    setSelectedPair(pair)
  }

  // Handle timeframe change
  const handleTimeframeChange = (timeframe) => {
    setSelectedTimeframe(timeframe)
  }

  // Handle chart type change
  const handleChartTypeChange = (type) => {
    setChartType(type)
  }

  // Handle indicator toggle
  const handleIndicatorToggle = (indicator) => {
    setIndicators(prev => ({
      ...prev,
      [indicator]: !prev[indicator]
    }))
  }

  // Get current price for displays
  const currentPrice = chartData.length > 0 ? chartData[chartData.length - 1].close : 0

  return (
    <div className="h-screen bg-dark-bg flex flex-col">
      {/* Top Bar */}
      <Topbar
        selectedPair={selectedPair}
        selectedTimeframe={selectedTimeframe}
        chartType={chartType}
        onPairChange={handlePairChange}
        onTimeframeChange={handleTimeframeChange}
        onChartTypeChange={handleChartTypeChange}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 flex-shrink-0">
          <Sidebar
            selectedPair={selectedPair}
            onPairChange={handlePairChange}
          />
        </div>

        {/* Main Dashboard */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Chart Section */}
          <div className="flex-1 flex">
            {/* Chart View */}
            <div className="flex-1 p-4">
              {isLoading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-trading-blue"></div>
                </div>
              ) : (
                <ChartView
                  data={chartData}
                  pair={selectedPair}
                  timeframe={selectedTimeframe}
                  chartType={chartType}
                  indicators={indicators}
                />
              )}
            </div>

            {/* Right Panel */}
            <div className="w-80 flex-shrink-0 p-4 space-y-4">
              <OverviewPanel
                pair={selectedPair}
                data={chartData}
                orderbook={orderbook}
              />
              
              <HeatmapLiquidity
                orderbook={orderbook}
                currentPrice={currentPrice}
              />
            </div>
          </div>

          {/* Bottom Panels */}
          <div className="h-80 flex-shrink-0 p-4">
            <div className="grid grid-cols-2 gap-4 h-full">
              <OrderFlowPanel
                data={chartData}
                orderbook={orderbook}
              />
              
              <IndicatorsPanel
                indicators={indicators}
                onToggle={handleIndicatorToggle}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="h-8 bg-dark-surface border-t border-dark-border flex items-center justify-between px-4 text-xs text-dark-muted">
        <div className="flex items-center space-x-4">
          <span>Status: Connected</span>
          <span>Last Update: {lastUpdate.toLocaleTimeString()}</span>
          <span>Data: {chartData.length} candles</span>
        </div>
        <div className="flex items-center space-x-4">
          <span>Crypto Technical Dashboard v1.0</span>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-trading-green rounded-full"></div>
            <span>Live</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App