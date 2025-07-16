// TradingView Datafeed Implementation
const Datafeed = {
    // Configuration
    supportedResolutions: ['1', '5', '15', '60', '240', '1D', '1W', '1M'],
    
    // Required methods by TradingView
    onReady: function(callback) {
        console.log('[Datafeed]: onReady called');
        setTimeout(() => {
            callback({
                exchanges: [],
                symbols_types: [],
                supported_resolutions: this.supportedResolutions,
                supports_marks: false,
                supports_timescale_marks: false,
                supports_time: true,
                supports_search: true,
                supports_group_request: false,
            });
        }, 0);
    },
    
    searchSymbols: function(userInput, exchange, symbolType, onResultReadyCallback) {
        console.log('[Datafeed]: searchSymbols called', userInput);
        
        // Predefined crypto symbols
        const symbols = [
            { symbol: 'BTCUSDT', full_name: 'Bitcoin/USDT', description: 'Bitcoin', type: 'crypto', exchange: 'OKX' },
            { symbol: 'ETHUSDT', full_name: 'Ethereum/USDT', description: 'Ethereum', type: 'crypto', exchange: 'OKX' },
            { symbol: 'SOLUSDT', full_name: 'Solana/USDT', description: 'Solana', type: 'crypto', exchange: 'OKX' },
            { symbol: 'BNBUSDT', full_name: 'BNB/USDT', description: 'Binance Coin', type: 'crypto', exchange: 'OKX' },
            { symbol: 'ADAUSDT', full_name: 'Cardano/USDT', description: 'Cardano', type: 'crypto', exchange: 'OKX' },
            { symbol: 'DOTUSDT', full_name: 'Polkadot/USDT', description: 'Polkadot', type: 'crypto', exchange: 'OKX' },
        ];
        
        const results = symbols.filter(s => 
            s.symbol.toLowerCase().includes(userInput.toLowerCase()) ||
            s.description.toLowerCase().includes(userInput.toLowerCase())
        );
        
        onResultReadyCallback(results);
    },
    
    resolveSymbol: function(symbolName, onSymbolResolvedCallback, onResolveErrorCallback) {
        console.log('[Datafeed]: resolveSymbol called', symbolName);
        
        setTimeout(() => {
            const symbolInfo = {
                name: symbolName,
                description: symbolName.replace('USDT', '/USDT'),
                type: 'crypto',
                session: '24x7',
                timezone: 'UTC',
                exchange: 'OKX',
                minmov: 1,
                pricescale: symbolName.includes('BTC') ? 100 : 10000,
                has_intraday: true,
                has_daily: true,
                has_weekly_and_monthly: true,
                supported_resolutions: this.supportedResolutions,
                volume_precision: 8,
                data_status: 'streaming',
                full_name: symbolName,
                listed_exchange: 'OKX',
                format: 'price',
            };
            
            onSymbolResolvedCallback(symbolInfo);
        }, 0);
    },
    
    getBars: async function(symbolInfo, resolution, periodParams, onHistoryCallback, onErrorCallback) {
        console.log('[Datafeed]: getBars called', {
            symbol: symbolInfo.name,
            resolution: resolution,
            from: new Date(periodParams.from * 1000),
            to: new Date(periodParams.to * 1000)
        });
        
        try {
            // Map TradingView resolution to API interval
            const intervalMap = {
                '1': '1m',
                '5': '5m',
                '15': '15m',
                '60': '1h',
                '240': '4h',
                '1D': '1d',
                '1W': '1w',
                '1M': '1M'
            };
            
            const interval = intervalMap[resolution] || '1h';
            const symbol = symbolInfo.name.replace('USDT', '-USDT'); // Convert BTCUSDT to BTC-USDT
            
            // Fetch data from backend
            const response = await fetch(`/api/candles?symbol=${symbol}&interval=${interval}&from=${periodParams.from}&to=${periodParams.to}&limit=1000`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.success || !data.candles || data.candles.length === 0) {
                // No data available
                onHistoryCallback([], { noData: true });
                return;
            }
            
            // Convert backend data to TradingView format
            const bars = data.candles.map(candle => ({
                time: candle.timestamp * 1000, // Convert to milliseconds
                open: parseFloat(candle.open),
                high: parseFloat(candle.high),
                low: parseFloat(candle.low),
                close: parseFloat(candle.close),
                volume: parseFloat(candle.volume)
            }));
            
            // Sort bars by time
            bars.sort((a, b) => a.time - b.time);
            
            console.log(`[Datafeed]: Loaded ${bars.length} bars`);
            onHistoryCallback(bars, { noData: bars.length === 0 });
            
        } catch (error) {
            console.error('[Datafeed]: getBars error', error);
            
            // Return empty data on error
            onHistoryCallback([], { noData: true });
        }
    },
    
    subscribeBars: function(symbolInfo, resolution, onRealtimeCallback, subscriberUID, onResetCacheNeededCallback) {
        console.log('[Datafeed]: subscribeBars called', symbolInfo.name);
        
        // Store subscriber info
        this.subscribers = this.subscribers || {};
        this.subscribers[subscriberUID] = {
            symbolInfo,
            resolution,
            callback: onRealtimeCallback
        };
        
        // Start real-time updates
        this.startRealtimeUpdates(symbolInfo, resolution, onRealtimeCallback);
    },
    
    unsubscribeBars: function(subscriberUID) {
        console.log('[Datafeed]: unsubscribeBars called', subscriberUID);
        
        if (this.subscribers && this.subscribers[subscriberUID]) {
            delete this.subscribers[subscriberUID];
        }
        
        // Stop updates if no more subscribers
        if (!this.subscribers || Object.keys(this.subscribers).length === 0) {
            this.stopRealtimeUpdates();
        }
    },
    
    // Helper methods
    generateMockBars: function(from, to, resolution) {
        const bars = [];
        const resolutionMinutes = {
            '1': 1,
            '5': 5,
            '15': 15,
            '60': 60,
            '240': 240,
            '1D': 1440,
            '1W': 10080,
            '1M': 43200
        };
        
        const interval = resolutionMinutes[resolution] || 60;
        const basePrice = 45000; // Base price for BTC
        let currentTime = from * 1000;
        const endTime = to * 1000;
        
        while (currentTime <= endTime) {
            const random = Math.random();
            const trend = Math.sin(currentTime / 1000000) * 1000;
            const noise = (random - 0.5) * 200;
            
            const open = basePrice + trend + noise;
            const close = open + (Math.random() - 0.5) * 100;
            const high = Math.max(open, close) + Math.random() * 50;
            const low = Math.min(open, close) - Math.random() * 50;
            const volume = Math.random() * 1000 + 100;
            
            bars.push({
                time: currentTime,
                open: open,
                high: high,
                low: low,
                close: close,
                volume: volume
            });
            
            currentTime += interval * 60 * 1000;
        }
        
        return bars;
    },
    
    startRealtimeUpdates: function(symbolInfo, resolution, callback) {
        // Real-time updates every 5 seconds from backend
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        const intervalMap = {
            '1': '1m',
            '5': '5m',
            '15': '15m',
            '60': '1h',
            '240': '4h',
            '1D': '1d',
            '1W': '1w',
            '1M': '1M'
        };
        
        const interval = intervalMap[resolution] || '1h';
        const symbol = symbolInfo.name.replace('USDT', '-USDT');
        
        this.updateInterval = setInterval(async () => {
            try {
                // Fetch latest candle
                const response = await fetch(`/api/candles?symbol=${symbol}&interval=${interval}&limit=1`);
                const data = await response.json();
                
                if (data.success && data.candles && data.candles.length > 0) {
                    const latestCandle = data.candles[0];
                    const bar = {
                        time: latestCandle.timestamp * 1000,
                        open: latestCandle.open,
                        high: latestCandle.high,
                        low: latestCandle.low,
                        close: latestCandle.close,
                        volume: latestCandle.volume
                    };
                    
                    this.lastBar = bar;
                    callback(bar);
                }
            } catch (error) {
                console.error('[Datafeed]: Real-time update error', error);
            }
        }, 5000);
    },
    
    stopRealtimeUpdates: function() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    },
    
    // Optional methods
    getServerTime: function(callback) {
        callback(Math.floor(Date.now() / 1000));
    },
    
    calculateHistoryDepth: function(resolution, resolutionBack, intervalBack) {
        // Calculate how far back we can go
        const resolutionMinutes = {
            '1': 1,
            '5': 5,
            '15': 15,
            '60': 60,
            '240': 240,
            '1D': 1440,
            '1W': 10080,
            '1M': 43200
        };
        
        const minutes = resolutionMinutes[resolution] || 60;
        
        if (resolutionBack === 'D') {
            return {
                resolutionBack: 'D',
                intervalBack: Math.min(intervalBack, 365) // Max 1 year of daily data
            };
        }
        
        return undefined;
    }
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Datafeed;
}

export default Datafeed;