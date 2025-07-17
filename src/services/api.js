// API service for backend communication
const API_BASE_URL = 'http://localhost:5000/api'

// Generic API call function with retry mechanism
async function apiCall(endpoint, options = {}, retryCount = 0) {
  const url = `${API_BASE_URL}${endpoint}`
  
  const defaultOptions = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 10000, // 10 second timeout
    ...options
  }
  
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), defaultOptions.timeout)
    
    const response = await fetch(url, {
      ...defaultOptions,
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    
    if (!response.ok) {
      // Specific handling for 503 Service Unavailable
      if (response.status === 503) {
        throw new Error(`Service temporarily unavailable (503)`)
      }
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return data
  } catch (error) {
    console.error(`API call failed for ${endpoint} (attempt ${retryCount + 1}):`, error)
    
    // Retry logic untuk specific errors
    if (retryCount < 3 && (
      error.name === 'AbortError' || 
      error.message.includes('503') || 
      error.message.includes('timeout') ||
      error.message.includes('Failed to fetch')
    )) {
      const delay = Math.min(1000 * Math.pow(2, retryCount), 5000) // Exponential backoff, max 5s
      console.log(`Retrying ${endpoint} in ${delay}ms...`)
      
      await new Promise(resolve => setTimeout(resolve, delay))
      return apiCall(endpoint, options, retryCount + 1)
    }
    
    throw error
  }
}

// Market data API calls
export const marketAPI = {
  // Get market data for a specific symbol
  async getMarketData(symbol, timeframe = '1H', limit = 100) {
    return apiCall(`/market-data/${symbol}?timeframe=${timeframe}&limit=${limit}`)
  },
  
  // Get current price for a symbol
  async getCurrentPrice(symbol) {
    return apiCall(`/price/${symbol}`)
  },
  
  // Get multiple symbols data
  async getMultipleSymbols(symbols) {
    const symbolsParam = symbols.join(',')
    return apiCall(`/market-data/multiple?symbols=${symbolsParam}`)
  },
  
  // Get orderbook data
  async getOrderbook(symbol, depth = 20) {
    return apiCall(`/orderbook/${symbol}?depth=${depth}`)
  }
}

// Trading analysis API calls
export const analysisAPI = {
  // Get technical analysis for a symbol
  async getTechnicalAnalysis(symbol, timeframe = '1H') {
    return apiCall(`/analyze/${symbol}?timeframe=${timeframe}`)
  },
  
  // Get AI narrative analysis
  async getAIAnalysis(symbol, mode = 'comprehensive') {
    return apiCall(`/enhanced-ai/narrative/${symbol}?mode=${mode}`)
  },
  
  // Get trading signals
  async getTradingSignals(symbol, limit = 10) {
    return apiCall(`/signals/${symbol}?limit=${limit}`)
  },
  
  // Get market snapshot
  async getMarketSnapshot(symbol, mode = 'quick') {
    return apiCall(`/snapshot/${symbol}?mode=${mode}`)
  }
}

// Indicators API calls
export const indicatorsAPI = {
  // Get technical indicators
  async getTechnicalIndicators(symbol, timeframe = '1H', indicators = []) {
    const indicatorsParam = indicators.join(',')
    return apiCall(`/technical-indicators/${symbol}?timeframe=${timeframe}&indicators=${indicatorsParam}`)
  },
  
  // Get volume profile
  async getVolumeProfile(symbol, timeframe = '1H') {
    return apiCall(`/volume-profile/${symbol}?timeframe=${timeframe}`)
  },
  
  // Get depth chart data
  async getDepthChart(symbol) {
    return apiCall(`/depth-chart/${symbol}`)
  }
}

// Real-time data API calls
export const realtimeAPI = {
  // Get real-time market overview
  async getMarketOverview() {
    return apiCall('/realtime/market-overview')
  },
  
  // Get streaming statistics
  async getStreamingStats() {
    return apiCall('/realtime/streaming-stats')
  },
  
  // Start real-time streaming
  async startStreaming(symbols = []) {
    const symbolsParam = symbols.join(',')
    return apiCall(`/realtime/start-streaming?symbols=${symbolsParam}`, {
      method: 'POST'
    })
  },
  
  // Stop real-time streaming
  async stopStreaming() {
    return apiCall('/realtime/stop-streaming', {
      method: 'POST'
    })
  }
}

// User preferences API calls
export const userAPI = {
  // Get user preferences
  async getPreferences() {
    return apiCall('/user-preferences')
  },
  
  // Update user preferences
  async updatePreferences(preferences) {
    return apiCall('/user-preferences', {
      method: 'PUT',
      body: JSON.stringify(preferences)
    })
  },
  
  // Get analysis history
  async getAnalysisHistory(limit = 50) {
    return apiCall(`/analysis-history?limit=${limit}`)
  }
}

// Monitoring API calls
export const monitoringAPI = {
  // Get system metrics
  async getSystemMetrics() {
    return apiCall('/monitoring/system')
  },
  
  // Get trading metrics
  async getTradingMetrics() {
    return apiCall('/monitoring/trading')
  },
  
  // Get performance metrics
  async getPerformanceMetrics() {
    return apiCall('/monitoring/performance')
  },
  
  // Get monitoring dashboard
  async getMonitoringDashboard() {
    return apiCall('/monitoring/dashboard')
  }
}

// WebSocket connection for real-time updates
export class WebSocketManager {
  constructor() {
    this.socket = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 1000
    this.listeners = new Map()
  }
  
  connect(url = 'ws://localhost:5000') {
    try {
      this.socket = new WebSocket(url)
      
      this.socket.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        this.emit('connected')
      }
      
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.emit('message', data)
          
          // Emit specific event types
          if (data.type) {
            this.emit(data.type, data)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      this.socket.onclose = () => {
        console.log('WebSocket disconnected')
        this.emit('disconnected')
        this.attemptReconnect()
      }
      
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.emit('error', error)
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      this.attemptReconnect()
    }
  }
  
  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      
      setTimeout(() => {
        this.connect()
      }, this.reconnectInterval * this.reconnectAttempts)
    }
  }
  
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }
  
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }
  
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error)
        }
      })
    }
  }
  
  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket not connected, cannot send data')
    }
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
    this.listeners.clear()
  }
}

// Export a singleton instance
export const wsManager = new WebSocketManager()

// Utility functions
export const utils = {
  // Format currency
  formatCurrency(value, decimals = 2) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value)
  },
  
  // Format percentage
  formatPercentage(value, decimals = 2) {
    return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`
  },
  
  // Format volume
  formatVolume(value) {
    if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`
    if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`
    if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`
    return value.toFixed(0)
  },
  
  // Format timestamp
  formatTimestamp(timestamp, format = 'datetime') {
    const date = new Date(timestamp)
    
    switch (format) {
      case 'time':
        return date.toLocaleTimeString()
      case 'date':
        return date.toLocaleDateString()
      case 'datetime':
        return date.toLocaleString()
      case 'short':
        return date.toLocaleString(undefined, {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      default:
        return date.toLocaleString()
    }
  },
  
  // Debounce function
  debounce(func, wait) {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  },
  
  // Throttle function
  throttle(func, limit) {
    let inThrottle
    return function() {
      const args = arguments
      const context = this
      if (!inThrottle) {
        func.apply(context, args)
        inThrottle = true
        setTimeout(() => inThrottle = false, limit)
      }
    }
  }
}