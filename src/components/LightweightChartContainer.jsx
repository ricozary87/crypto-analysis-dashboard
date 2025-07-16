import React, { useEffect, useRef, useState } from 'react';

const LightweightChartContainer = ({ symbol = "BTCUSDT", interval = "1" }) => {
    const chartContainerRef = useRef();
    const chartRef = useRef(null);
    const candlestickSeriesRef = useRef(null);
    const volumeSeriesRef = useRef(null);
    const [isLoading, setIsLoading] = useState(true);
    
    // Convert symbol format from BTCUSDT to BTC-USDT
    const formatSymbol = (sym) => {
        return sym.replace('USDT', '-USDT');
    };
    
    // Convert interval to API format
    const intervalMap = {
        '1': '1m',
        '5': '5m',
        '15': '15m',
        '60': '1h',
        '240': '4h',
        '1D': '1d',
        '1W': '1w'
    };
    
    const fetchCandles = async () => {
        try {
            const apiInterval = intervalMap[interval] || '1h';
            const formattedSymbol = formatSymbol(symbol);
            
            const response = await fetch(`/api/candles?symbol=${formattedSymbol}&interval=${apiInterval}&limit=300`);
            const data = await response.json();
            
            if (data.success && data.candles && data.candles.length > 0) {
                // Convert data to Lightweight Charts format
                const candleData = data.candles.map(candle => ({
                    time: candle.timestamp,
                    open: candle.open,
                    high: candle.high,
                    low: candle.low,
                    close: candle.close
                }));
                
                const volumeData = data.candles.map(candle => ({
                    time: candle.timestamp,
                    value: candle.volume,
                    color: candle.close >= candle.open ? '#10b98180' : '#ef444480'
                }));
                
                // Sort by time
                candleData.sort((a, b) => a.time - b.time);
                volumeData.sort((a, b) => a.time - b.time);
                
                return { candleData, volumeData };
            }
            
            return { candleData: [], volumeData: [] };
        } catch (error) {
            console.error('Error fetching candles:', error);
            return { candleData: [], volumeData: [] };
        }
    };
    
    const initChart = async () => {
        if (!chartContainerRef.current || !window.LightweightCharts) return;
        
        setIsLoading(true);
        
        // Create chart
        const chart = window.LightweightCharts.createChart(chartContainerRef.current, {
            width: chartContainerRef.current.clientWidth,
            height: 500,
            layout: {
                background: { type: 'solid', color: '#0a0a0a' },
                textColor: '#9ca3af',
            },
            grid: {
                vertLines: { color: '#1a1a1a' },
                horzLines: { color: '#1a1a1a' },
            },
            crosshair: {
                mode: window.LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: '#1a1a1a',
            },
            timeScale: {
                borderColor: '#1a1a1a',
                timeVisible: true,
                secondsVisible: false,
            },
        });
        
        // Create candlestick series
        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#ef4444',
            borderDownColor: '#ef4444',
            borderUpColor: '#10b981',
            wickDownColor: '#ef4444',
            wickUpColor: '#10b981',
        });
        
        // Create volume series
        const volumeSeries = chart.addHistogramSeries({
            color: '#26a69a',
            priceFormat: {
                type: 'volume',
            },
            priceScaleId: '',
            scaleMargins: {
                top: 0.8,
                bottom: 0,
            },
        });
        
        // Fetch and set data
        const { candleData, volumeData } = await fetchCandles();
        
        if (candleData.length > 0) {
            candlestickSeries.setData(candleData);
            volumeSeries.setData(volumeData);
            
            // Fit content
            chart.timeScale().fitContent();
        }
        
        // Store references
        chartRef.current = chart;
        candlestickSeriesRef.current = candlestickSeries;
        volumeSeriesRef.current = volumeSeries;
        
        setIsLoading(false);
        
        // Handle resize
        const handleResize = () => {
            if (chartContainerRef.current) {
                chart.applyOptions({ 
                    width: chartContainerRef.current.clientWidth 
                });
            }
        };
        
        window.addEventListener('resize', handleResize);
        
        // Set up real-time updates
        const updateInterval = setInterval(async () => {
            const { candleData, volumeData } = await fetchCandles();
            if (candleData.length > 0) {
                candlestickSeries.setData(candleData);
                volumeSeries.setData(volumeData);
            }
        }, 5000);
        
        return () => {
            window.removeEventListener('resize', handleResize);
            clearInterval(updateInterval);
            chart.remove();
        };
    };
    
    useEffect(() => {
        const cleanup = initChart();
        return () => {
            cleanup && cleanup();
        };
    }, []); // Run once on mount
    
    // Update when symbol or interval changes
    useEffect(() => {
        if (chartRef.current && candlestickSeriesRef.current && volumeSeriesRef.current) {
            const updateData = async () => {
                setIsLoading(true);
                const { candleData, volumeData } = await fetchCandles();
                
                if (candleData.length > 0) {
                    candlestickSeriesRef.current.setData(candleData);
                    volumeSeriesRef.current.setData(volumeData);
                    chartRef.current.timeScale().fitContent();
                }
                setIsLoading(false);
            };
            
            updateData();
        }
    }, [symbol, interval]);
    
    return (
        <div className="w-full h-[500px] relative bg-[#0a0a0a] rounded-lg overflow-hidden">
            {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-[#0a0a0a] bg-opacity-75 z-10">
                    <div className="text-gray-400">Loading chart...</div>
                </div>
            )}
            <div 
                ref={chartContainerRef}
                className="w-full h-full"
            />
        </div>
    );
};

export default LightweightChartContainer;