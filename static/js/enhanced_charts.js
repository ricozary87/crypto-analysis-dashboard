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
            }
        };
    }

    createAdvancedCandlestickChart(containerId, data, options = {}) {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                console.error(`Container ${containerId} not found`);
                return;
            }

            // Prepare candlestick data
            const candlestickTrace = {
                x: data.map(item => item.timestamp || item.time),
                open: data.map(item => item.open),
                high: data.map(item => item.high),
                low: data.map(item => item.low),
                close: data.map(item => item.close),
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
                x: data.map(item => item.timestamp || item.time),
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

// Helper function to format timestamp
function formatTimestamp(timestamp) {
    if (typeof timestamp === 'number') {
        return new Date(timestamp * 1000).toISOString();
    }
    return timestamp;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedChartManager;
}