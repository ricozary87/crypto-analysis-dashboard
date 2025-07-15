// Enhanced Chart Manager using Plotly.js
// Integrated from OkxCandleTracker for professional trading charts

class EnhancedChartManager {
    constructor() {
        this.charts = {};
        this.defaultLayout = {
            paper_bgcolor: '#1a1a1a',
            plot_bgcolor: '#2d2d2d',
            font: {
                color: '#e0e0e0',
                family: 'Arial, sans-serif'
            },
            xaxis: {
                gridcolor: 'rgba(255, 255, 255, 0.1)',
                zerolinecolor: 'rgba(255, 255, 255, 0.2)',
                color: '#e0e0e0'
            },
            yaxis: {
                gridcolor: 'rgba(255, 255, 255, 0.1)',
                zerolinecolor: 'rgba(255, 255, 255, 0.2)',
                color: '#e0e0e0'
            },
            margin: {
                t: 50,
                l: 60,
                r: 20,
                b: 60
            },
            showlegend: true,
            legend: {
                font: {
                    color: '#e0e0e0'
                },
                bgcolor: 'rgba(45, 45, 45, 0.8)',
                bordercolor: 'rgba(64, 64, 64, 0.8)',
                borderwidth: 1
            }
        };
        
        this.defaultConfig = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false,
            toImageButtonOptions: {
                format: 'png',
                filename: 'trading_chart',
                height: 600,
                width: 1200,
                scale: 1
            },
            // Performance optimizations
            staticPlot: false,
            doubleClick: 'reset',
            scrollZoom: true,
            showTips: false,
            frameMargins: 0,
            autosizable: true
        };
        
        // Debounce function for better performance
        this.debounce = (func, wait) => {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        };
        
        // Colors for different chart elements
        this.colors = {
            bullish: '#26a69a',
            bearish: '#ef5350',
            volume: '#64b5f6',
            ma: '#ffa726',
            rsi: '#ab47bc',
            macd: '#66bb6a',
            support: '#4caf50',
            resistance: '#f44336',
            orderblock: '#ffeb3b',
            fvg: '#9c27b0'
        };
    }
    
    // Enhanced TradingView-style candlestick chart
    createCandlestickChart(containerId, data, options = {}) {
        const defaultOptions = {
            showVolume: true,
            showMA: true,
            showOrderBlocks: true,
            showFVG: true,
            limit: 200 // Limit data points for performance
        };
        
        const config = { ...defaultOptions, ...options };
        
        // Limit data for performance
        const limitedData = data.slice(-config.limit);
        
        const traces = [];
        
        // Main candlestick trace
        const candlestickTrace = {
            x: limitedData.map(d => formatTimestamp(d.timestamp)),
            close: limitedData.map(d => d.close),
            decreasing: {line: {color: this.colors.bearish}},
            high: limitedData.map(d => d.high),
            increasing: {line: {color: this.colors.bullish}},
            low: limitedData.map(d => d.low),
            open: limitedData.map(d => d.open),
            type: 'candlestick',
            name: 'Price',
            xaxis: 'x',
            yaxis: 'y'
        };
        
        traces.push(candlestickTrace);
        
        // Volume trace (if enabled)
        if (config.showVolume) {
            const volumeTrace = {
                x: limitedData.map(d => formatTimestamp(d.timestamp)),
                y: limitedData.map(d => d.volume),
                type: 'bar',
                name: 'Volume',
                yaxis: 'y2',
                marker: {
                    color: limitedData.map(d => d.close > d.open ? this.colors.bullish : this.colors.bearish),
                    opacity: 0.6
                }
            };
            traces.push(volumeTrace);
        }
        
        // Moving averages (if enabled)
        if (config.showMA && limitedData.length > 20) {
            const ma20 = this.calculateMA(limitedData.map(d => d.close), 20);
            const ma50 = this.calculateMA(limitedData.map(d => d.close), 50);
            
            if (ma20.length > 0) {
                traces.push({
                    x: limitedData.slice(-ma20.length).map(d => formatTimestamp(d.timestamp)),
                    y: ma20,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'MA20',
                    line: {
                        color: this.colors.ma,
                        width: 2
                    }
                });
            }
            
            if (ma50.length > 0) {
                traces.push({
                    x: limitedData.slice(-ma50.length).map(d => formatTimestamp(d.timestamp)),
                    y: ma50,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'MA50',
                    line: {
                        color: '#ff7043',
                        width: 2
                    }
                });
            }
        }
        
        // Layout configuration
        const layout = {
            ...this.defaultLayout,
            title: {
                text: options.title || 'Price Chart',
                font: {
                    size: 18,
                    color: '#e0e0e0'
                }
            },
            xaxis: {
                ...this.defaultLayout.xaxis,
                rangeslider: {visible: false},
                type: 'date',
                domain: config.showVolume ? [0, 1] : [0, 1]
            },
            yaxis: {
                ...this.defaultLayout.yaxis,
                domain: config.showVolume ? [0.3, 1] : [0, 1],
                title: 'Price ($)'
            },
            height: 600,
            dragmode: 'pan',
            selectdirection: 'horizontal'
        };
        
        // Add volume y-axis if volume is shown
        if (config.showVolume) {
            layout.yaxis2 = {
                ...this.defaultLayout.yaxis,
                domain: [0, 0.25],
                title: 'Volume',
                overlaying: 'y',
                side: 'right'
            };
        }
        
        // Performance optimizations
        const plotConfig = {
            ...this.defaultConfig,
            // Reduce rendering load
            plotGlPixelRatio: 1,
            // Optimize for large datasets
            staticPlot: limitedData.length > 1000
        };
        
        // Create plot
        const plot = Plotly.newPlot(containerId, traces, layout, plotConfig);
        
        // Store reference
        this.charts[containerId] = {
            plot: plot,
            data: limitedData,
            config: config
        };
        
        return plot;
    }
    
    // Create technical indicators chart
    createIndicatorsChart(containerId, data, indicators, options = {}) {
        const traces = [];
        
        // RSI trace
        if (indicators.rsi) {
            const rsiTrace = {
                x: data.map(d => formatTimestamp(d.timestamp)),
                y: indicators.rsi,
                type: 'scatter',
                mode: 'lines',
                name: 'RSI',
                line: {
                    color: this.colors.rsi,
                    width: 2
                },
                yaxis: 'y'
            };
            traces.push(rsiTrace);
            
            // RSI overbought/oversold lines
            traces.push({
                x: data.map(d => formatTimestamp(d.timestamp)),
                y: Array(data.length).fill(70),
                type: 'scatter',
                mode: 'lines',
                name: 'Overbought',
                line: {
                    color: 'rgba(244, 67, 54, 0.5)',
                    width: 1,
                    dash: 'dash'
                },
                showlegend: false
            });
            
            traces.push({
                x: data.map(d => formatTimestamp(d.timestamp)),
                y: Array(data.length).fill(30),
                type: 'scatter',
                mode: 'lines',
                name: 'Oversold',
                line: {
                    color: 'rgba(76, 175, 80, 0.5)',
                    width: 1,
                    dash: 'dash'
                },
                showlegend: false
            });
        }
        
        // MACD trace
        if (indicators.macd) {
            const macdTrace = {
                x: data.map(d => formatTimestamp(d.timestamp)),
                y: indicators.macd.macd,
                type: 'scatter',
                mode: 'lines',
                name: 'MACD',
                line: {
                    color: this.colors.macd,
                    width: 2
                },
                yaxis: 'y2'
            };
            traces.push(macdTrace);
            
            const signalTrace = {
                x: data.map(d => formatTimestamp(d.timestamp)),
                y: indicators.macd.signal,
                type: 'scatter',
                mode: 'lines',
                name: 'Signal',
                line: {
                    color: '#ff7043',
                    width: 2
                },
                yaxis: 'y2'
            };
            traces.push(signalTrace);
            
            const histogramTrace = {
                x: data.map(d => formatTimestamp(d.timestamp)),
                y: indicators.macd.histogram,
                type: 'bar',
                name: 'Histogram',
                yaxis: 'y2',
                marker: {
                    color: indicators.macd.histogram.map(h => h > 0 ? this.colors.bullish : this.colors.bearish),
                    opacity: 0.6
                }
            };
            traces.push(histogramTrace);
        }
        
        const layout = {
            ...this.defaultLayout,
            title: {
                text: 'Technical Indicators',
                font: {
                    size: 18,
                    color: '#e0e0e0'
                }
            },
            xaxis: {
                ...this.defaultLayout.xaxis,
                type: 'date',
                domain: [0, 1]
            },
            yaxis: {
                ...this.defaultLayout.yaxis,
                domain: [0.55, 1],
                title: 'RSI',
                range: [0, 100]
            },
            yaxis2: {
                ...this.defaultLayout.yaxis,
                domain: [0, 0.45],
                title: 'MACD',
                overlaying: 'y',
                side: 'right'
            },
            height: 400
        };
        
        const plot = Plotly.newPlot(containerId, traces, layout, this.defaultConfig);
        
        this.charts[containerId] = {
            plot: plot,
            data: data,
            indicators: indicators
        };
        
        return plot;
    }
    
    // Create volume profile chart
    createVolumeProfileChart(containerId, volumeProfile, options = {}) {
        const traces = [];
        
        // Volume profile bars
        const volumeTrace = {
            x: volumeProfile.volumes,
            y: volumeProfile.price_levels,
            type: 'bar',
            orientation: 'h',
            name: 'Volume Profile',
            marker: {
                color: this.colors.volume,
                opacity: 0.7
            }
        };
        traces.push(volumeTrace);
        
        // POC line
        traces.push({
            x: [0, Math.max(...volumeProfile.volumes)],
            y: [volumeProfile.poc, volumeProfile.poc],
            type: 'scatter',
            mode: 'lines',
            name: 'POC',
            line: {
                color: '#ffeb3b',
                width: 3
            }
        });
        
        // Value Area High/Low
        traces.push({
            x: [0, Math.max(...volumeProfile.volumes)],
            y: [volumeProfile.value_area_high, volumeProfile.value_area_high],
            type: 'scatter',
            mode: 'lines',
            name: 'VAH',
            line: {
                color: 'rgba(255, 235, 59, 0.5)',
                width: 2,
                dash: 'dash'
            }
        });
        
        traces.push({
            x: [0, Math.max(...volumeProfile.volumes)],
            y: [volumeProfile.value_area_low, volumeProfile.value_area_low],
            type: 'scatter',
            mode: 'lines',
            name: 'VAL',
            line: {
                color: 'rgba(255, 235, 59, 0.5)',
                width: 2,
                dash: 'dash'
            }
        });
        
        const layout = {
            ...this.defaultLayout,
            title: {
                text: 'Volume Profile',
                font: {
                    size: 18,
                    color: '#e0e0e0'
                }
            },
            xaxis: {
                ...this.defaultLayout.xaxis,
                title: 'Volume'
            },
            yaxis: {
                ...this.defaultLayout.yaxis,
                title: 'Price ($)'
            },
            height: 400
        };
        
        const plot = Plotly.newPlot(containerId, traces, layout, this.defaultConfig);
        
        this.charts[containerId] = {
            plot: plot,
            data: volumeProfile
        };
        
        return plot;
    }
    
    // Create orderbook depth chart
    createOrderbookChart(containerId, orderbook, options = {}) {
        const traces = [];
        
        // Process orderbook data
        const bids = orderbook.bids || [];
        const asks = orderbook.asks || [];
        
        // Calculate cumulative volumes
        let bidsCumulative = [];
        let asksCumulative = [];
        
        let cumulativeBidVolume = 0;
        for (let i = 0; i < bids.length; i++) {
            cumulativeBidVolume += parseFloat(bids[i][1]);
            bidsCumulative.push([parseFloat(bids[i][0]), cumulativeBidVolume]);
        }
        
        let cumulativeAskVolume = 0;
        for (let i = 0; i < asks.length; i++) {
            cumulativeAskVolume += parseFloat(asks[i][1]);
            asksCumulative.push([parseFloat(asks[i][0]), cumulativeAskVolume]);
        }
        
        // Bids trace
        if (bidsCumulative.length > 0) {
            traces.push({
                x: bidsCumulative.map(b => b[0]),
                y: bidsCumulative.map(b => b[1]),
                type: 'scatter',
                mode: 'lines',
                fill: 'tonexty',
                name: 'Bids',
                line: {
                    color: this.colors.bullish,
                    width: 2
                },
                fillcolor: 'rgba(38, 166, 154, 0.3)'
            });
        }
        
        // Asks trace
        if (asksCumulative.length > 0) {
            traces.push({
                x: asksCumulative.map(a => a[0]),
                y: asksCumulative.map(a => a[1]),
                type: 'scatter',
                mode: 'lines',
                fill: 'tonexty',
                name: 'Asks',
                line: {
                    color: this.colors.bearish,
                    width: 2
                },
                fillcolor: 'rgba(239, 83, 80, 0.3)'
            });
        }
        
        const layout = {
            ...this.defaultLayout,
            title: {
                text: 'Orderbook Depth',
                font: {
                    size: 18,
                    color: '#e0e0e0'
                }
            },
            xaxis: {
                ...this.defaultLayout.xaxis,
                title: 'Price ($)'
            },
            yaxis: {
                ...this.defaultLayout.yaxis,
                title: 'Cumulative Volume'
            },
            height: 400
        };
        
        const plot = Plotly.newPlot(containerId, traces, layout, this.defaultConfig);
        
        this.charts[containerId] = {
            plot: plot,
            data: orderbook
        };
        
        return plot;
    }
    
    // Utility function to calculate moving average
    calculateMA(data, period) {
        if (data.length < period) return [];
        
        const result = [];
        for (let i = period - 1; i < data.length; i++) {
            const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
            result.push(sum / period);
        }
        return result;
    }
    
    // Update chart with new data
    updateChart(containerId, newData) {
        const chart = this.charts[containerId];
        if (!chart) return;
        
        // Implement update logic based on chart type
        // This is a placeholder - implement specific update logic for each chart type
        console.log(`Updating chart ${containerId} with new data`);
    }
    
    // Destroy chart
    destroyChart(containerId) {
        const chart = this.charts[containerId];
        if (chart) {
            Plotly.purge(containerId);
            delete this.charts[containerId];
        }
    }
    
    // Get chart instance
    getChart(containerId) {
        return this.charts[containerId];
    }
    
    // Resize chart
    resizeChart(containerId) {
        const chart = this.charts[containerId];
        if (chart) {
            Plotly.Plots.resize(containerId);
        }
    }
    
    // Export chart as image
    exportChart(containerId, format = 'png') {
        const chart = this.charts[containerId];
        if (chart) {
            return Plotly.toImage(containerId, {
                format: format,
                width: 1200,
                height: 600,
                scale: 2
            });
        }
        return null;
    }

    createAdvancedCandlestickChart(containerId, data, options = {}) {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                console.error(`Container ${containerId} not found`);
                return;
            }

            // Clear previous chart if exists
            if (this.charts[containerId]) {
                Plotly.purge(containerId);
                delete this.charts[containerId];
            }

            // Optimize data - limit to last 200 points for better performance
            const optimizedData = data.slice(-200);

            // Prepare candlestick data with proper date handling
            const candlestickTrace = {
                x: optimizedData.map(item => {
                    const timestamp = item.timestamp || item.time;
                    return formatTimestamp(timestamp);
                }),
                open: optimizedData.map(item => parseFloat(item.open)),
                high: optimizedData.map(item => parseFloat(item.high)),
                low: optimizedData.map(item => parseFloat(item.low)),
                close: optimizedData.map(item => parseFloat(item.close)),
                type: 'candlestick',
                name: options.symbol || 'Price',
                increasing: {
                    line: { color: '#00d68f' },
                    fillcolor: '#00d68f'
                },
                decreasing: {
                    line: { color: '#ff3d71' },
                    fillcolor: '#ff3d71'
                },
                xaxis: 'x',
                yaxis: 'y'
            };

            // Prepare volume data
            const volumeTrace = {
                x: data.map(item => formatTimestamp(item.timestamp || item.time)),
                y: data.map(item => item.volume),
                type: 'bar',
                name: 'Volume',
                marker: {
                    color: data.map(item => item.close > item.open ? '#00d68f' : '#ff3d71'),
                    opacity: 0.6
                },
                xaxis: 'x',
                yaxis: 'y2'
            };

            const traces = [candlestickTrace];
            
            // Add volume if available
            if (data.some(item => item.volume)) {
                traces.push(volumeTrace);
            }

            const layout = {
                ...this.defaultLayout,
                title: {
                    text: options.title || `${options.symbol || 'Crypto'} Trading Chart`,
                    font: { color: '#e0e0e0', size: 16 }
                },
                xaxis: {
                    ...this.defaultLayout.xaxis,
                    domain: [0, 1],
                    rangeslider: { visible: false },
                    type: 'date'
                },
                yaxis: {
                    ...this.defaultLayout.yaxis,
                    domain: [0.3, 1],
                    title: { text: 'Price (USDT)', font: { color: '#e0e0e0' } }
                },
                yaxis2: {
                    ...this.defaultLayout.yaxis,
                    domain: [0, 0.25],
                    title: { text: 'Volume', font: { color: '#e0e0e0' } }
                },
                height: options.height || 600
            };

            // Add support/resistance levels if provided
            if (options.supportLevels && options.supportLevels.length > 0) {
                options.supportLevels.forEach((level, index) => {
                    layout.shapes = layout.shapes || [];
                    layout.shapes.push({
                        type: 'line',
                        x0: data[0].timestamp || data[0].time,
                        x1: data[data.length - 1].timestamp || data[data.length - 1].time,
                        y0: level,
                        y1: level,
                        line: {
                            color: '#00d68f',
                            width: 2,
                            dash: 'dash'
                        }
                    });
                });
            }

            if (options.resistanceLevels && options.resistanceLevels.length > 0) {
                options.resistanceLevels.forEach((level, index) => {
                    layout.shapes = layout.shapes || [];
                    layout.shapes.push({
                        type: 'line',
                        x0: data[0].timestamp || data[0].time,
                        x1: data[data.length - 1].timestamp || data[data.length - 1].time,
                        y0: level,
                        y1: level,
                        line: {
                            color: '#ff3d71',
                            width: 2,
                            dash: 'dash'
                        }
                    });
                });
            }

            // Add SMC levels if provided
            if (options.smcLevels) {
                layout.shapes = layout.shapes || [];
                
                // Order blocks
                if (options.smcLevels.orderBlocks) {
                    options.smcLevels.orderBlocks.forEach(block => {
                        layout.shapes.push({
                            type: 'rect',
                            x0: block.start_time,
                            x1: block.end_time,
                            y0: block.low,
                            y1: block.high,
                            fillcolor: block.type === 'bullish' ? 'rgba(0, 214, 143, 0.2)' : 'rgba(255, 61, 113, 0.2)',
                            line: {
                                color: block.type === 'bullish' ? '#00d68f' : '#ff3d71',
                                width: 1
                            }
                        });
                    });
                }

                // Fair Value Gaps
                if (options.smcLevels.fvgGaps) {
                    options.smcLevels.fvgGaps.forEach(gap => {
                        layout.shapes.push({
                            type: 'rect',
                            x0: gap.start_time,
                            x1: gap.end_time,
                            y0: gap.low,
                            y1: gap.high,
                            fillcolor: 'rgba(255, 193, 7, 0.3)',
                            line: {
                                color: '#ffc107',
                                width: 1,
                                dash: 'dot'
                            }
                        });
                    });
                }
            }

            Plotly.newPlot(containerId, traces, layout, this.defaultConfig);
            this.charts[containerId] = { traces, layout };

            console.log(`Enhanced candlestick chart created for ${containerId}`);
            return true;

        } catch (error) {
            console.error(`Error creating enhanced candlestick chart: ${error}`);
            return false;
        }
    }

    createTechnicalIndicatorChart(containerId, data, indicators, options = {}) {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                console.error(`Container ${containerId} not found`);
                return;
            }

            const traces = [];

            // RSI
            if (indicators.rsi) {
                traces.push({
                    x: data.map(item => item.timestamp || item.time),
                    y: indicators.rsi,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'RSI',
                    line: { color: '#17a2b8' },
                    yaxis: 'y'
                });

                // RSI levels
                const overboughtLine = new Array(data.length).fill(70);
                const oversoldLine = new Array(data.length).fill(30);
                
                traces.push({
                    x: data.map(item => item.timestamp || item.time),
                    y: overboughtLine,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Overbought (70)',
                    line: { color: '#ff3d71', dash: 'dash' },
                    yaxis: 'y'
                });

                traces.push({
                    x: data.map(item => item.timestamp || item.time),
                    y: oversoldLine,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Oversold (30)',
                    line: { color: '#00d68f', dash: 'dash' },
                    yaxis: 'y'
                });
            }

            // MACD
            if (indicators.macd) {
                traces.push({
                    x: data.map(item => item.timestamp || item.time),
                    y: indicators.macd.macd,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'MACD',
                    line: { color: '#6f42c1' },
                    yaxis: 'y2'
                });

                traces.push({
                    x: data.map(item => item.timestamp || item.time),
                    y: indicators.macd.signal,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Signal',
                    line: { color: '#fd7e14' },
                    yaxis: 'y2'
                });

                traces.push({
                    x: data.map(item => item.timestamp || item.time),
                    y: indicators.macd.histogram,
                    type: 'bar',
                    name: 'Histogram',
                    marker: { color: '#6c757d' },
                    yaxis: 'y2'
                });
            }

            const layout = {
                ...this.defaultLayout,
                title: {
                    text: options.title || 'Technical Indicators',
                    font: { color: '#e0e0e0', size: 16 }
                },
                xaxis: {
                    ...this.defaultLayout.xaxis,
                    type: 'date'
                },
                yaxis: {
                    ...this.defaultLayout.yaxis,
                    domain: [0.6, 1],
                    title: { text: 'RSI', font: { color: '#e0e0e0' } },
                    range: [0, 100]
                },
                yaxis2: {
                    ...this.defaultLayout.yaxis,
                    domain: [0, 0.55],
                    title: { text: 'MACD', font: { color: '#e0e0e0' } }
                },
                height: options.height || 400
            };

            Plotly.newPlot(containerId, traces, layout, this.defaultConfig);
            this.charts[containerId] = { traces, layout };

            console.log(`Technical indicator chart created for ${containerId}`);
            return true;

        } catch (error) {
            console.error(`Error creating technical indicator chart: ${error}`);
            return false;
        }
    }

    createVolumeProfileChart(containerId, data, volumeProfile, options = {}) {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                console.error(`Container ${containerId} not found`);
                return;
            }

            const traces = [];

            // Volume profile bars
            if (volumeProfile.price_levels && volumeProfile.volumes) {
                traces.push({
                    x: volumeProfile.volumes,
                    y: volumeProfile.price_levels,
                    type: 'bar',
                    orientation: 'h',
                    name: 'Volume Profile',
                    marker: {
                        color: volumeProfile.volumes.map(v => 
                            v > Math.max(...volumeProfile.volumes) * 0.7 ? '#ffc107' : '#6c757d'
                        ),
                        opacity: 0.7
                    }
                });
            }

            // POC line
            if (volumeProfile.poc) {
                traces.push({
                    x: [0, Math.max(...volumeProfile.volumes)],
                    y: [volumeProfile.poc, volumeProfile.poc],
                    type: 'scatter',
                    mode: 'lines',
                    name: 'POC',
                    line: { color: '#ffc107', width: 3 }
                });
            }

            // Value Area
            if (volumeProfile.value_area_high && volumeProfile.value_area_low) {
                traces.push({
                    x: [0, Math.max(...volumeProfile.volumes)],
                    y: [volumeProfile.value_area_high, volumeProfile.value_area_high],
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Value Area High',
                    line: { color: '#17a2b8', width: 2, dash: 'dash' }
                });

                traces.push({
                    x: [0, Math.max(...volumeProfile.volumes)],
                    y: [volumeProfile.value_area_low, volumeProfile.value_area_low],
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Value Area Low',
                    line: { color: '#17a2b8', width: 2, dash: 'dash' }
                });
            }

            const layout = {
                ...this.defaultLayout,
                title: {
                    text: options.title || 'Volume Profile',
                    font: { color: '#e0e0e0', size: 16 }
                },
                xaxis: {
                    ...this.defaultLayout.xaxis,
                    title: { text: 'Volume', font: { color: '#e0e0e0' } }
                },
                yaxis: {
                    ...this.defaultLayout.yaxis,
                    title: { text: 'Price (USDT)', font: { color: '#e0e0e0' } }
                },
                height: options.height || 400
            };

            Plotly.newPlot(containerId, traces, layout, this.defaultConfig);
            this.charts[containerId] = { traces, layout };

            console.log(`Volume profile chart created for ${containerId}`);
            return true;

        } catch (error) {
            console.error(`Error creating volume profile chart: ${error}`);
            return false;
        }
    }

    updateChart(containerId, newData) {
        try {
            if (!this.charts[containerId]) {
                console.error(`Chart ${containerId} not found`);
                return false;
            }

            // Update the chart with new data
            const update = {
                x: [newData.map(item => item.timestamp || item.time)],
                open: [newData.map(item => item.open)],
                high: [newData.map(item => item.high)],
                low: [newData.map(item => item.low)],
                close: [newData.map(item => item.close)]
            };

            Plotly.restyle(containerId, update, [0]);
            console.log(`Chart ${containerId} updated`);
            return true;

        } catch (error) {
            console.error(`Error updating chart ${containerId}: ${error}`);
            return false;
        }
    }

    destroyChart(containerId) {
        try {
            if (this.charts[containerId]) {
                Plotly.purge(containerId);
                delete this.charts[containerId];
                console.log(`Chart ${containerId} destroyed`);
                return true;
            }
            return false;
        } catch (error) {
            console.error(`Error destroying chart ${containerId}: ${error}`);
            return false;
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(containerId => {
            this.destroyChart(containerId);
        });
    }

    getChartImage(containerId, format = 'png') {
        try {
            if (!this.charts[containerId]) {
                console.error(`Chart ${containerId} not found`);
                return null;
            }

            return Plotly.toImage(containerId, {
                format: format,
                width: 1200,
                height: 600
            });

        } catch (error) {
            console.error(`Error getting chart image: ${error}`);
            return null;
        }
    }
}

// Initialize global chart manager
window.enhancedChartManager = new EnhancedChartManager();

// Enhanced helper function to safely format timestamp
function formatTimestamp(timestamp) {
    try {
        // Handle null/undefined
        if (!timestamp) {
            return new Date().toISOString();
        }
        
        // Handle string timestamps
        if (typeof timestamp === 'string') {
            // Check if it's already a valid ISO string
            if (timestamp.includes('T') && timestamp.includes('Z')) {
                return timestamp;
            }
            // Try to parse as number
            const numTimestamp = parseFloat(timestamp);
            if (!isNaN(numTimestamp) && numTimestamp > 0) {
                timestamp = numTimestamp;
            } else {
                console.warn(`Invalid timestamp string: ${timestamp}`);
                return new Date().toISOString();
            }
        }
        
        // Handle number timestamps
        if (typeof timestamp === 'number') {
            // Filter out invalid small numbers
            if (timestamp < 1000000000) {
                console.warn(`Invalid timestamp number: ${timestamp}`);
                return new Date().toISOString();
            }
            
            // Handle both seconds and milliseconds
            const date = timestamp > 10000000000 ? new Date(timestamp) : new Date(timestamp * 1000);
            
            // Validate the date
            if (isNaN(date.getTime())) {
                console.warn(`Invalid date created from timestamp: ${timestamp}`);
                return new Date().toISOString();
            }
            
            return date.toISOString();
        }
        
        // Fallback for other types
        console.warn(`Unexpected timestamp type: ${typeof timestamp}, value: ${timestamp}`);
        return new Date().toISOString();
        
    } catch (error) {
        console.error(`Error formatting timestamp: ${error}, timestamp: ${timestamp}`);
        return new Date().toISOString();
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedChartManager;
}