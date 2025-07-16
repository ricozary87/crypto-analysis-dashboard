// Technical indicator calculations

// Simple Moving Average
export function calculateSMA(data, period) {
  const sma = []
  
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      sma.push(null)
    } else {
      const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0)
      sma.push(sum / period)
    }
  }
  
  return sma
}

// Exponential Moving Average
export function calculateEMA(data, period) {
  const ema = []
  const multiplier = 2 / (period + 1)
  
  // First EMA value is SMA
  let sum = 0
  for (let i = 0; i < period; i++) {
    sum += data[i]
  }
  ema[period - 1] = sum / period
  
  // Calculate EMA for the rest
  for (let i = period; i < data.length; i++) {
    ema[i] = (data[i] * multiplier) + (ema[i - 1] * (1 - multiplier))
  }
  
  // Fill initial values with null
  for (let i = 0; i < period - 1; i++) {
    ema[i] = null
  }
  
  return ema
}

// Relative Strength Index
export function calculateRSI(data, period = 14) {
  const rsi = []
  const gains = []
  const losses = []
  
  // Calculate initial gains and losses
  for (let i = 1; i < data.length; i++) {
    const change = data[i] - data[i - 1]
    gains.push(change > 0 ? change : 0)
    losses.push(change < 0 ? Math.abs(change) : 0)
  }
  
  // Calculate RSI
  for (let i = 0; i < gains.length; i++) {
    if (i < period - 1) {
      rsi.push(null)
    } else {
      const avgGain = gains.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0) / period
      const avgLoss = losses.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0) / period
      
      if (avgLoss === 0) {
        rsi.push(100)
      } else {
        const rs = avgGain / avgLoss
        rsi.push(100 - (100 / (1 + rs)))
      }
    }
  }
  
  // Add initial null for first data point
  rsi.unshift(null)
  
  return rsi
}

// MACD (Moving Average Convergence Divergence)
export function calculateMACD(data, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) {
  const fastEMA = calculateEMA(data, fastPeriod)
  const slowEMA = calculateEMA(data, slowPeriod)
  
  const macd = []
  const signal = []
  const histogram = []
  
  // Calculate MACD line
  for (let i = 0; i < data.length; i++) {
    if (fastEMA[i] !== null && slowEMA[i] !== null) {
      macd.push(fastEMA[i] - slowEMA[i])
    } else {
      macd.push(null)
    }
  }
  
  // Calculate signal line (EMA of MACD)
  const macdValues = macd.filter(val => val !== null)
  const signalEMA = calculateEMA(macdValues, signalPeriod)
  
  let signalIndex = 0
  for (let i = 0; i < macd.length; i++) {
    if (macd[i] !== null) {
      signal.push(signalEMA[signalIndex] || null)
      signalIndex++
    } else {
      signal.push(null)
    }
  }
  
  // Calculate histogram
  for (let i = 0; i < macd.length; i++) {
    if (macd[i] !== null && signal[i] !== null) {
      histogram.push(macd[i] - signal[i])
    } else {
      histogram.push(null)
    }
  }
  
  return {
    macd,
    signal,
    histogram
  }
}

// Bollinger Bands
export function calculateBollingerBands(data, period = 20, multiplier = 2) {
  const sma = calculateSMA(data, period)
  const upper = []
  const lower = []
  
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      upper.push(null)
      lower.push(null)
    } else {
      const slice = data.slice(i - period + 1, i + 1)
      const mean = sma[i]
      const variance = slice.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / period
      const stdDev = Math.sqrt(variance)
      
      upper.push(mean + (multiplier * stdDev))
      lower.push(mean - (multiplier * stdDev))
    }
  }
  
  return {
    upper,
    middle: sma,
    lower
  }
}

// Stochastic Oscillator
export function calculateStochastic(highs, lows, closes, kPeriod = 14, dPeriod = 3) {
  const k = []
  const d = []
  
  for (let i = 0; i < closes.length; i++) {
    if (i < kPeriod - 1) {
      k.push(null)
    } else {
      const highSlice = highs.slice(i - kPeriod + 1, i + 1)
      const lowSlice = lows.slice(i - kPeriod + 1, i + 1)
      
      const highestHigh = Math.max(...highSlice)
      const lowestLow = Math.min(...lowSlice)
      
      if (highestHigh === lowestLow) {
        k.push(50)
      } else {
        k.push(((closes[i] - lowestLow) / (highestHigh - lowestLow)) * 100)
      }
    }
  }
  
  // Calculate %D (SMA of %K)
  const kValues = k.filter(val => val !== null)
  const dSMA = calculateSMA(kValues, dPeriod)
  
  let dIndex = 0
  for (let i = 0; i < k.length; i++) {
    if (k[i] !== null) {
      d.push(dSMA[dIndex] || null)
      dIndex++
    } else {
      d.push(null)
    }
  }
  
  return { k, d }
}

// Average True Range (ATR)
export function calculateATR(highs, lows, closes, period = 14) {
  const trueRanges = []
  
  for (let i = 1; i < closes.length; i++) {
    const tr1 = highs[i] - lows[i]
    const tr2 = Math.abs(highs[i] - closes[i - 1])
    const tr3 = Math.abs(lows[i] - closes[i - 1])
    
    trueRanges.push(Math.max(tr1, tr2, tr3))
  }
  
  const atr = calculateSMA(trueRanges, period)
  
  // Add null for first data point
  atr.unshift(null)
  
  return atr
}

// On-Balance Volume (OBV)
export function calculateOBV(closes, volumes) {
  const obv = [volumes[0]]
  
  for (let i = 1; i < closes.length; i++) {
    if (closes[i] > closes[i - 1]) {
      obv.push(obv[i - 1] + volumes[i])
    } else if (closes[i] < closes[i - 1]) {
      obv.push(obv[i - 1] - volumes[i])
    } else {
      obv.push(obv[i - 1])
    }
  }
  
  return obv
}

// Volume Weighted Average Price (VWAP)
export function calculateVWAP(highs, lows, closes, volumes) {
  const vwap = []
  let cumulativeVolume = 0
  let cumulativeVolumePrice = 0
  
  for (let i = 0; i < closes.length; i++) {
    const typicalPrice = (highs[i] + lows[i] + closes[i]) / 3
    const volumePrice = typicalPrice * volumes[i]
    
    cumulativeVolume += volumes[i]
    cumulativeVolumePrice += volumePrice
    
    vwap.push(cumulativeVolumePrice / cumulativeVolume)
  }
  
  return vwap
}

// Commodity Channel Index (CCI)
export function calculateCCI(highs, lows, closes, period = 20) {
  const cci = []
  
  for (let i = 0; i < closes.length; i++) {
    if (i < period - 1) {
      cci.push(null)
    } else {
      const typicalPrices = []
      
      for (let j = i - period + 1; j <= i; j++) {
        typicalPrices.push((highs[j] + lows[j] + closes[j]) / 3)
      }
      
      const sma = typicalPrices.reduce((sum, tp) => sum + tp, 0) / period
      const meanDeviation = typicalPrices.reduce((sum, tp) => sum + Math.abs(tp - sma), 0) / period
      
      if (meanDeviation === 0) {
        cci.push(0)
      } else {
        const currentTypicalPrice = (highs[i] + lows[i] + closes[i]) / 3
        cci.push((currentTypicalPrice - sma) / (0.015 * meanDeviation))
      }
    }
  }
  
  return cci
}

// Williams %R
export function calculateWilliamsR(highs, lows, closes, period = 14) {
  const williamsR = []
  
  for (let i = 0; i < closes.length; i++) {
    if (i < period - 1) {
      williamsR.push(null)
    } else {
      const highSlice = highs.slice(i - period + 1, i + 1)
      const lowSlice = lows.slice(i - period + 1, i + 1)
      
      const highestHigh = Math.max(...highSlice)
      const lowestLow = Math.min(...lowSlice)
      
      if (highestHigh === lowestLow) {
        williamsR.push(-50)
      } else {
        williamsR.push(((highestHigh - closes[i]) / (highestHigh - lowestLow)) * -100)
      }
    }
  }
  
  return williamsR
}

// Money Flow Index (MFI)
export function calculateMFI(highs, lows, closes, volumes, period = 14) {
  const mfi = []
  const typicalPrices = []
  const moneyFlows = []
  
  // Calculate typical prices and money flows
  for (let i = 0; i < closes.length; i++) {
    const typicalPrice = (highs[i] + lows[i] + closes[i]) / 3
    typicalPrices.push(typicalPrice)
    
    if (i > 0) {
      const moneyFlow = typicalPrice * volumes[i]
      moneyFlows.push({
        value: moneyFlow,
        positive: typicalPrice > typicalPrices[i - 1]
      })
    }
  }
  
  // Calculate MFI
  for (let i = 0; i < closes.length; i++) {
    if (i < period) {
      mfi.push(null)
    } else {
      const periodFlows = moneyFlows.slice(i - period, i)
      const positiveFlow = periodFlows.filter(f => f.positive).reduce((sum, f) => sum + f.value, 0)
      const negativeFlow = periodFlows.filter(f => !f.positive).reduce((sum, f) => sum + f.value, 0)
      
      if (negativeFlow === 0) {
        mfi.push(100)
      } else {
        const moneyRatio = positiveFlow / negativeFlow
        mfi.push(100 - (100 / (1 + moneyRatio)))
      }
    }
  }
  
  return mfi
}