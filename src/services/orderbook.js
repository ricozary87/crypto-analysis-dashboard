// Generate dummy orderbook data
export function generateDummyOrderbook(currentPrice, depth = 20) {
  const bids = []
  const asks = []
  
  const spread = currentPrice * 0.001 // 0.1% spread
  const bidPrice = currentPrice - spread / 2
  const askPrice = currentPrice + spread / 2
  
  // Generate bids (buy orders) - decreasing price
  for (let i = 0; i < depth; i++) {
    const price = bidPrice - (i * currentPrice * 0.0005)
    const volume = Math.random() * 50 + 10 // 10-60 volume
    bids.push([price.toFixed(2), volume.toFixed(4)])
  }
  
  // Generate asks (sell orders) - increasing price
  for (let i = 0; i < depth; i++) {
    const price = askPrice + (i * currentPrice * 0.0005)
    const volume = Math.random() * 50 + 10 // 10-60 volume
    asks.push([price.toFixed(2), volume.toFixed(4)])
  }
  
  return {
    bids,
    asks,
    timestamp: Date.now()
  }
}

// Generate orderbook with realistic market conditions
export function generateRealisticOrderbook(currentPrice, marketCondition = 'normal') {
  const bids = []
  const asks = []
  
  let spreadMultiplier = 1
  let volumeMultiplier = 1
  
  // Adjust spread and volume based on market conditions
  switch (marketCondition) {
    case 'volatile':
      spreadMultiplier = 2
      volumeMultiplier = 0.5
      break
    case 'liquid':
      spreadMultiplier = 0.5
      volumeMultiplier = 2
      break
    case 'illiquid':
      spreadMultiplier = 3
      volumeMultiplier = 0.3
      break
  }
  
  const spread = currentPrice * 0.001 * spreadMultiplier
  const bidPrice = currentPrice - spread / 2
  const askPrice = currentPrice + spread / 2
  
  // Generate more realistic volume distribution
  for (let i = 0; i < 25; i++) {
    // Bids
    const bidPriceLevel = bidPrice - (i * currentPrice * 0.0003)
    const bidVolume = (Math.random() * 100 + 20) * volumeMultiplier * (1 / (i + 1)) // Decreasing volume with distance
    bids.push([bidPriceLevel.toFixed(2), bidVolume.toFixed(4)])
    
    // Asks
    const askPriceLevel = askPrice + (i * currentPrice * 0.0003)
    const askVolume = (Math.random() * 100 + 20) * volumeMultiplier * (1 / (i + 1)) // Decreasing volume with distance
    asks.push([askPriceLevel.toFixed(2), askVolume.toFixed(4)])
  }
  
  return {
    bids,
    asks,
    timestamp: Date.now(),
    condition: marketCondition
  }
}

// Generate level 2 orderbook with aggregated levels
export function generateLevel2Orderbook(currentPrice, levels = 10) {
  const bids = []
  const asks = []
  
  const spread = currentPrice * 0.001
  const bidPrice = currentPrice - spread / 2
  const askPrice = currentPrice + spread / 2
  
  // Generate aggregated levels
  for (let i = 0; i < levels; i++) {
    const priceStep = currentPrice * 0.002 // 0.2% steps
    
    // Bids
    const bidPriceLevel = bidPrice - (i * priceStep)
    const bidVolume = Math.random() * 200 + 50 // Larger volumes for aggregated levels
    bids.push([bidPriceLevel.toFixed(2), bidVolume.toFixed(4)])
    
    // Asks
    const askPriceLevel = askPrice + (i * priceStep)
    const askVolume = Math.random() * 200 + 50
    asks.push([askPriceLevel.toFixed(2), askVolume.toFixed(4)])
  }
  
  return {
    bids,
    asks,
    timestamp: Date.now(),
    level: 2
  }
}

// Calculate orderbook metrics
export function calculateOrderbookMetrics(orderbook) {
  const { bids, asks } = orderbook
  
  if (!bids || !asks || bids.length === 0 || asks.length === 0) {
    return {
      spread: 0,
      spreadPercent: 0,
      bidVolume: 0,
      askVolume: 0,
      imbalance: 0,
      midPrice: 0
    }
  }
  
  const bestBid = parseFloat(bids[0][0])
  const bestAsk = parseFloat(asks[0][0])
  const spread = bestAsk - bestBid
  const midPrice = (bestBid + bestAsk) / 2
  const spreadPercent = (spread / midPrice) * 100
  
  const bidVolume = bids.reduce((sum, bid) => sum + parseFloat(bid[1]), 0)
  const askVolume = asks.reduce((sum, ask) => sum + parseFloat(ask[1]), 0)
  
  const imbalance = (bidVolume - askVolume) / (bidVolume + askVolume)
  
  return {
    spread,
    spreadPercent,
    bidVolume,
    askVolume,
    imbalance,
    midPrice,
    bestBid,
    bestAsk
  }
}

// Generate orderbook with walls (large orders)
export function generateOrderbookWithWalls(currentPrice, wallSize = 1000) {
  const orderbook = generateDummyOrderbook(currentPrice, 20)
  
  // Add a buy wall (large bid order)
  const buyWallPrice = currentPrice * 0.95 // 5% below current price
  const buyWallIndex = Math.floor(Math.random() * 10) + 5
  orderbook.bids[buyWallIndex] = [buyWallPrice.toFixed(2), wallSize.toFixed(4)]
  
  // Add a sell wall (large ask order)
  const sellWallPrice = currentPrice * 1.05 // 5% above current price
  const sellWallIndex = Math.floor(Math.random() * 10) + 5
  orderbook.asks[sellWallIndex] = [sellWallPrice.toFixed(2), wallSize.toFixed(4)]
  
  return {
    ...orderbook,
    walls: {
      buyWall: { price: buyWallPrice, volume: wallSize },
      sellWall: { price: sellWallPrice, volume: wallSize }
    }
  }
}

// Simulate orderbook updates (for real-time simulation)
export function simulateOrderbookUpdate(currentOrderbook, priceChange = 0) {
  const { bids, asks } = currentOrderbook
  
  // Apply price change to all levels
  const newBids = bids.map(bid => [
    (parseFloat(bid[0]) + priceChange).toFixed(2),
    bid[1]
  ])
  
  const newAsks = asks.map(ask => [
    (parseFloat(ask[0]) + priceChange).toFixed(2),
    ask[1]
  ])
  
  // Randomly update some volume levels
  newBids.forEach(bid => {
    if (Math.random() < 0.3) { // 30% chance of volume change
      const currentVolume = parseFloat(bid[1])
      const volumeChange = (Math.random() - 0.5) * currentVolume * 0.2
      bid[1] = Math.max(0, currentVolume + volumeChange).toFixed(4)
    }
  })
  
  newAsks.forEach(ask => {
    if (Math.random() < 0.3) { // 30% chance of volume change
      const currentVolume = parseFloat(ask[1])
      const volumeChange = (Math.random() - 0.5) * currentVolume * 0.2
      ask[1] = Math.max(0, currentVolume + volumeChange).toFixed(4)
    }
  })
  
  return {
    bids: newBids,
    asks: newAsks,
    timestamp: Date.now()
  }
}