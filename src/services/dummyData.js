// Generate dummy candlestick data for testing
export function generateDummyData(pair, timeframe, count = 100) {
  const data = []
  const now = new Date()
  
  // Define starting prices for different pairs
  const startingPrices = {
    'BTC/USDT': 45000,
    'ETH/USDT': 2800,
    'SOL/USDT': 160,
    'BNB/USDT': 310,
    'ADA/USDT': 0.48,
    'DOT/USDT': 7.2,
    'AVAX/USDT': 38,
    'MATIC/USDT': 0.82
  }
  
  // Timeframe intervals in milliseconds
  const intervals = {
    '5m': 5 * 60 * 1000,
    '15m': 15 * 60 * 1000,
    '1H': 60 * 60 * 1000,
    '4H': 4 * 60 * 60 * 1000,
    '1D': 24 * 60 * 60 * 1000,
    '1W': 7 * 24 * 60 * 60 * 1000
  }
  
  const interval = intervals[timeframe] || intervals['1H']
  const basePrice = startingPrices[pair] || 45000
  
  let currentPrice = basePrice
  
  for (let i = count - 1; i >= 0; i--) {
    const time = now.getTime() - (i * interval)
    
    // Generate realistic price movement
    const volatility = 0.02 // 2% volatility
    const trend = Math.random() - 0.5 // Random trend
    const priceChange = currentPrice * volatility * trend
    
    const open = currentPrice
    const close = Math.max(0, currentPrice + priceChange)
    const high = Math.max(open, close) * (1 + Math.random() * 0.01)
    const low = Math.min(open, close) * (1 - Math.random() * 0.01)
    
    // Generate volume (higher volume on bigger price movements)
    const volumeMultiplier = Math.abs(priceChange) / currentPrice * 100 + 1
    const volume = Math.random() * 1000000 * volumeMultiplier
    
    data.push({
      time,
      open,
      high,
      low,
      close,
      volume
    })
    
    currentPrice = close
  }
  
  return data
}

// Generate realistic price movements with trends
export function generateTrendingData(pair, timeframe, count = 100, trend = 'sideways') {
  const data = []
  const now = new Date()
  
  const startingPrices = {
    'BTC/USDT': 45000,
    'ETH/USDT': 2800,
    'SOL/USDT': 160,
    'BNB/USDT': 310,
    'ADA/USDT': 0.48
  }
  
  const intervals = {
    '5m': 5 * 60 * 1000,
    '15m': 15 * 60 * 1000,
    '1H': 60 * 60 * 1000,
    '4H': 4 * 60 * 60 * 1000,
    '1D': 24 * 60 * 60 * 1000
  }
  
  const interval = intervals[timeframe] || intervals['1H']
  const basePrice = startingPrices[pair] || 45000
  
  let currentPrice = basePrice
  
  // Trend multipliers
  const trendMultipliers = {
    'bullish': 0.3,
    'bearish': -0.3,
    'sideways': 0
  }
  
  const trendBias = trendMultipliers[trend] || 0
  
  for (let i = count - 1; i >= 0; i--) {
    const time = now.getTime() - (i * interval)
    
    // Add trend bias to random movement
    const volatility = 0.015
    const randomMovement = (Math.random() - 0.5) * volatility
    const trendMovement = trendBias * 0.001 // Small trend bias
    const totalMovement = randomMovement + trendMovement
    
    const open = currentPrice
    const close = Math.max(0, currentPrice * (1 + totalMovement))
    const high = Math.max(open, close) * (1 + Math.random() * 0.005)
    const low = Math.min(open, close) * (1 - Math.random() * 0.005)
    
    // Higher volume during trend changes
    const volumeBase = 500000
    const volumeVariation = Math.random() * 500000
    const trendVolume = Math.abs(totalMovement) * 10000000
    const volume = volumeBase + volumeVariation + trendVolume
    
    data.push({
      time,
      open,
      high,
      low,
      close,
      volume
    })
    
    currentPrice = close
  }
  
  return data
}

// Generate data with specific patterns (breakouts, reversals, etc.)
export function generatePatternData(pair, pattern = 'breakout', count = 100) {
  const data = []
  const now = new Date()
  const interval = 60 * 60 * 1000 // 1 hour
  
  const startingPrices = {
    'BTC/USDT': 45000,
    'ETH/USDT': 2800,
    'SOL/USDT': 160
  }
  
  const basePrice = startingPrices[pair] || 45000
  let currentPrice = basePrice
  
  for (let i = count - 1; i >= 0; i--) {
    const time = now.getTime() - (i * interval)
    const position = (count - i) / count // 0 to 1
    
    let movement = 0
    
    switch (pattern) {
      case 'breakout':
        // Consolidation then breakout
        if (position < 0.7) {
          movement = (Math.random() - 0.5) * 0.005 // Tight range
        } else {
          movement = 0.02 // Strong breakout
        }
        break
        
      case 'reversal':
        // Downtrend then reversal
        if (position < 0.6) {
          movement = -0.015 // Downtrend
        } else {
          movement = 0.025 // Strong reversal
        }
        break
        
      case 'flag':
        // Uptrend, consolidation, continuation
        if (position < 0.3) {
          movement = 0.02 // Initial uptrend
        } else if (position < 0.7) {
          movement = (Math.random() - 0.5) * 0.005 // Flag consolidation
        } else {
          movement = 0.015 // Continuation
        }
        break
        
      default:
        movement = (Math.random() - 0.5) * 0.015
    }
    
    const open = currentPrice
    const close = Math.max(0, currentPrice * (1 + movement))
    const high = Math.max(open, close) * (1 + Math.random() * 0.003)
    const low = Math.min(open, close) * (1 - Math.random() * 0.003)
    
    // Volume increases during pattern completion
    const volumeBase = 300000
    const patternVolume = Math.abs(movement) * 20000000
    const volume = volumeBase + Math.random() * 200000 + patternVolume
    
    data.push({
      time,
      open,
      high,
      low,
      close,
      volume
    })
    
    currentPrice = close
  }
  
  return data
}

// Get current market data (simulated)
export function getCurrentMarketData(pair) {
  const data = generateDummyData(pair, '1H', 1)
  const current = data[0]
  
  return {
    pair,
    price: current.close,
    change24h: ((current.close - current.open) / current.open) * 100,
    volume24h: current.volume * 24,
    high24h: current.high,
    low24h: current.low,
    timestamp: current.time
  }
}