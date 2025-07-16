import React, { useEffect, useRef } from 'react';
import Datafeed from '../../public/tv-datafeed.js';

const ChartContainer = ({ symbol = "BTCUSDT", interval = "1" }) => {
    const chartContainerRef = useRef();
    const tvWidgetRef = useRef(null);
    
    useEffect(() => {
        // Initialize TradingView widget
        const initWidget = () => {
            if (window.TradingView && chartContainerRef.current) {
                const widget = new window.TradingView.widget({
                    // Widget configuration
                    debug: false,
                    fullscreen: false,
                    symbol: symbol,
                    interval: interval,
                    container: chartContainerRef.current,
                    datafeed: Datafeed,
                    library_path: "/charting_library/",
                    locale: "en",
                    disabled_features: ["use_localstorage_for_settings"],
                    enabled_features: ["study_templates"],
                    charts_storage_url: 'https://saveload.tradingview.com',
                    charts_storage_api_version: "1.1",
                    client_id: 'tradingview.com',
                    user_id: 'public_user_id',
                    autosize: true,
                    theme: "dark",
                    style: "1",
                    toolbar_bg: "#1a1a1a",
                    enable_publishing: false,
                    allow_symbol_change: true,
                    details: true,
                    hotlist: true,
                    calendar: true,
                    container_id: "tv_chart_container",
                    overrides: {
                        // Dark theme overrides
                        "paneProperties.background": "#0a0a0a",
                        "paneProperties.backgroundType": "solid",
                        "paneProperties.vertGridProperties.color": "#1a1a1a",
                        "paneProperties.horzGridProperties.color": "#1a1a1a",
                        "scalesProperties.textColor": "#9ca3af",
                        "mainSeriesProperties.candleStyle.upColor": "#10b981",
                        "mainSeriesProperties.candleStyle.downColor": "#ef4444",
                        "mainSeriesProperties.candleStyle.borderUpColor": "#10b981",
                        "mainSeriesProperties.candleStyle.borderDownColor": "#ef4444",
                        "mainSeriesProperties.candleStyle.wickUpColor": "#10b981",
                        "mainSeriesProperties.candleStyle.wickDownColor": "#ef4444",
                    },
                    studies_overrides: {
                        "volume.volume.color.0": "#ef4444",
                        "volume.volume.color.1": "#10b981",
                        "volume.volume.transparency": 50,
                    },
                    time_frames: [
                        { text: "1m", resolution: "1", description: "1 Minute" },
                        { text: "5m", resolution: "5", description: "5 Minutes" },
                        { text: "15m", resolution: "15", description: "15 Minutes" },
                        { text: "1h", resolution: "60", description: "1 Hour" },
                        { text: "4h", resolution: "240", description: "4 Hours" },
                        { text: "1d", resolution: "1D", description: "1 Day" },
                    ],
                });
                
                tvWidgetRef.current = widget;
                
                widget.onChartReady(() => {
                    console.log('TradingView Chart is ready');
                    
                    // Add volume indicator by default
                    widget.chart().createStudy('Volume', false, false, { showMA: false });
                });
            }
        };
        
        // Check if TradingView library is loaded
        if (window.TradingView) {
            initWidget();
        } else {
            // If not loaded, wait for it
            const checkInterval = setInterval(() => {
                if (window.TradingView) {
                    clearInterval(checkInterval);
                    initWidget();
                }
            }, 100);
            
            // Cleanup interval on unmount
            return () => clearInterval(checkInterval);
        }
        
        // Cleanup on unmount
        return () => {
            if (tvWidgetRef.current !== null) {
                tvWidgetRef.current.remove();
                tvWidgetRef.current = null;
            }
        };
    }, []); // Empty dependency array - only run once on mount
    
    // Update symbol when prop changes
    useEffect(() => {
        if (tvWidgetRef.current && symbol) {
            tvWidgetRef.current.chart().setSymbol(symbol, () => {
                console.log(`Symbol changed to ${symbol}`);
            });
        }
    }, [symbol]);
    
    // Update interval when prop changes
    useEffect(() => {
        if (tvWidgetRef.current && interval) {
            tvWidgetRef.current.chart().setResolution(interval, () => {
                console.log(`Interval changed to ${interval}`);
            });
        }
    }, [interval]);
    
    return (
        <div className="w-full h-[500px] relative">
            <div 
                ref={chartContainerRef}
                id="tv_chart_container" 
                className="w-full h-full"
            />
        </div>
    );
};

export default ChartContainer;