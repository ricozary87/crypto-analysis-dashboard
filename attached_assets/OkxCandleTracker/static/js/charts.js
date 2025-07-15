// Chart.js configurations and utilities for OKX Market Data Dashboard

class ChartManager {
    constructor() {
        this.charts = {};
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        displayFormats: {
                            minute: 'HH:mm',
                            hour: 'HH:mm',
                            day: 'MMM dd'
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        };
    }

    createCandlestickChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // Prepare data for line chart (since Chart.js doesn't have native candlestick)
        const priceData = data.map(item => ({
            x: new Date(item.timestamp),
            o: item.open,
            h: item.high,
            l: item.low,
            c: item.close
        }));

        const chartData = {
            labels: data.map(item => new Date(item.timestamp)),
            datasets: [
                {
                    label: 'High',
                    data: data.map(item => item.high),
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: false,
                    tension: 0.1
                },
                {
                    label: 'Low',
                    data: data.map(item => item.low),
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: false,
                    tension: 0.1
                },
                {
                    label: 'Close',
                    data: data.map(item => item.close),
                    borderColor: 'rgba(255, 206, 86, 1)',
                    backgroundColor: 'rgba(255, 206, 86, 0.2)',
                    fill: false,
                    tension: 0.1,
                    borderWidth: 2
                }
            ]
        };

        const options = {
            ...this.defaultOptions,
            plugins: {
                ...this.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Price Chart (OHLC)'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            const item = data[index];
                            return [
                                `Open: ${item.open.toFixed(2)}`,
                                `High: ${item.high.toFixed(2)}`,
                                `Low: ${item.low.toFixed(2)}`,
                                `Close: ${item.close.toFixed(2)}`,
                                `Volume: ${item.volume.toFixed(2)}`
                            ];
                        }
                    }
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: options
        });
    }

    createMACDChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const validData = data.filter(item => item.macd !== null);
        
        const chartData = {
            labels: validData.map(item => new Date(item.timestamp)),
            datasets: [
                {
                    label: 'MACD',
                    data: validData.map(item => item.macd),
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    fill: false,
                    tension: 0.1
                },
                {
                    label: 'Signal',
                    data: validData.map(item => item.signal),
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: false,
                    tension: 0.1
                },
                {
                    label: 'Histogram',
                    data: validData.map(item => item.histogram),
                    type: 'bar',
                    backgroundColor: validData.map(item => 
                        item.histogram > 0 ? 'rgba(75, 192, 192, 0.6)' : 'rgba(255, 99, 132, 0.6)'
                    ),
                    borderColor: 'transparent'
                }
            ]
        };

        const options = {
            ...this.defaultOptions,
            plugins: {
                ...this.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'MACD Indicator'
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: options
        });
    }

    createOBVChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const chartData = {
            labels: data.map(item => new Date(item.timestamp)),
            datasets: [
                {
                    label: 'OBV',
                    data: data.map(item => item.obv),
                    borderColor: 'rgba(153, 102, 255, 1)',
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    fill: true,
                    tension: 0.1
                }
            ]
        };

        const options = {
            ...this.defaultOptions,
            plugins: {
                ...this.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'On-Balance Volume (OBV)'
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: options
        });
    }

    createRSIChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const validData = data.filter(item => item.rsi !== null);

        const chartData = {
            labels: validData.map(item => new Date(item.timestamp)),
            datasets: [
                {
                    label: 'RSI',
                    data: validData.map(item => item.rsi),
                    borderColor: 'rgba(255, 159, 64, 1)',
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    fill: false,
                    tension: 0.1
                }
            ]
        };

        const options = {
            ...this.defaultOptions,
            plugins: {
                ...this.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'RSI (Relative Strength Index)'
                },
                annotation: {
                    annotations: {
                        line1: {
                            type: 'line',
                            yMin: 70,
                            yMax: 70,
                            borderColor: 'rgba(255, 99, 132, 0.8)',
                            borderWidth: 2,
                            label: {
                                content: 'Overbought (70)',
                                enabled: true
                            }
                        },
                        line2: {
                            type: 'line',
                            yMin: 30,
                            yMax: 30,
                            borderColor: 'rgba(75, 192, 192, 0.8)',
                            borderWidth: 2,
                            label: {
                                content: 'Oversold (30)',
                                enabled: true
                            }
                        }
                    }
                }
            },
            scales: {
                ...this.defaultOptions.scales,
                y: {
                    ...this.defaultOptions.scales.y,
                    min: 0,
                    max: 100
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: options
        });
    }

    createVolumeChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const chartData = {
            labels: data.map(item => new Date(item.timestamp)),
            datasets: [
                {
                    label: 'Volume',
                    data: data.map(item => item.volume),
                    backgroundColor: data.map(item => 
                        item.close > item.open ? 'rgba(75, 192, 192, 0.6)' : 'rgba(255, 99, 132, 0.6)'
                    ),
                    borderColor: 'transparent'
                }
            ]
        };

        const options = {
            ...this.defaultOptions,
            plugins: {
                ...this.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Volume Chart'
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: options
        });
    }

    createDepthChart(canvasId, orderbook) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        if (!orderbook || !orderbook.bids || !orderbook.asks) {
            return;
        }

        // Calculate cumulative volumes for depth chart
        const bids = orderbook.bids.slice(0, 25); // Top 25 bids
        const asks = orderbook.asks.slice(0, 25); // Top 25 asks
        
        // Calculate cumulative bid volumes (from highest price to lowest)
        let bidCumulative = 0;
        const bidDepth = bids.map(bid => {
            bidCumulative += bid.size;
            return {
                price: bid.price,
                cumulative: bidCumulative
            };
        });
        
        // Calculate cumulative ask volumes (from lowest price to highest)
        let askCumulative = 0;
        const askDepth = asks.map(ask => {
            askCumulative += ask.size;
            return {
                price: ask.price,
                cumulative: askCumulative
            };
        });

        // Combine bid and ask data for chart
        const allPrices = [...bidDepth.map(b => b.price), ...askDepth.map(a => a.price)];
        const allData = [...bidDepth.map(b => b.cumulative), ...askDepth.map(a => a.cumulative)];
        
        const chartData = {
            labels: allPrices.map(price => price.toFixed(2)),
            datasets: [
                {
                    label: 'Bids',
                    data: bidDepth.map(b => ({ x: b.price, y: b.cumulative })),
                    borderColor: '#00cc96',
                    backgroundColor: 'rgba(0, 204, 150, 0.1)',
                    fill: true,
                    tension: 0,
                    pointRadius: 0,
                    pointHoverRadius: 4
                },
                {
                    label: 'Asks', 
                    data: askDepth.map(a => ({ x: a.price, y: a.cumulative })),
                    borderColor: '#ef553b',
                    backgroundColor: 'rgba(239, 85, 59, 0.1)',
                    fill: true,
                    tension: 0,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }
            ]
        };

        const options = {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Market Depth Chart',
                    color: '#fff'
                },
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#fff'
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return `Price: $${context[0].parsed.x.toFixed(2)}`;
                        },
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(4)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Price ($)',
                        color: '#fff'
                    },
                    ticks: {
                        color: '#fff',
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Cumulative Volume',
                        color: '#fff'
                    },
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: options
        });
    }

    destroyChart(canvasId) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
            delete this.charts[canvasId];
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(canvasId => {
            this.destroyChart(canvasId);
        });
    }

    updateChart(canvasId, data) {
        if (this.charts[canvasId]) {
            // Update chart data
            this.charts[canvasId].data = data;
            this.charts[canvasId].update();
        }
    }

    getChart(canvasId) {
        return this.charts[canvasId];
    }
}

// Global chart manager instance
const chartManager = new ChartManager();
