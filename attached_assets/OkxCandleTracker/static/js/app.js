// Main application JavaScript for OKX Market Data Dashboard

class OKXDashboard {
    constructor() {
        this.currentSymbol = 'BTC-USDT';
        this.currentTimeframe = '1h';
        this.currentLimit = 100;
        this.refreshInterval = null;
        this.isLoading = false;
        this.autoRefresh = true;
        
        this.initializeEventListeners();
        this.loadUserPreferences();
    }

    initializeEventListeners() {
        // Control elements
        document.getElementById('loadDataBtn').addEventListener('click', () => this.loadMarketData());
        document.getElementById('refreshBtn').addEventListener('click', () => this.refreshData());
        
        // Symbol and timeframe changes
        document.getElementById('symbolSelect').addEventListener('change', (e) => {
            this.currentSymbol = e.target.value;
            this.saveUserPreferences();
        });
        
        document.getElementById('timeframeSelect').addEventListener('change', (e) => {
            this.currentTimeframe = e.target.value;
            this.saveUserPreferences();
        });
        
        document.getElementById('limitSelect').addEventListener('change', (e) => {
            this.currentLimit = parseInt(e.target.value);
            this.saveUserPreferences();
        });

        // Tab changes
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                this.handleTabChange(e.target.id);
            });
        });
    }

    showLoading() {
        this.isLoading = true;
        document.getElementById('loadingIndicator').classList.remove('d-none');
        document.getElementById('errorAlert').classList.add('d-none');
    }

    hideLoading() {
        this.isLoading = false;
        document.getElementById('loadingIndicator').classList.add('d-none');
    }

    showError(message) {
        document.getElementById('errorMessage').textContent = message;
        document.getElementById('errorAlert').classList.remove('d-none');
        this.hideLoading();
    }

    async loadUserPreferences() {
        try {
            const response = await fetch('/api/preferences');
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    const prefs = result.data;
                    this.currentSymbol = prefs.preferred_symbol || 'BTC-USDT';
                    this.currentTimeframe = prefs.preferred_timeframe || '1h';
                    this.currentLimit = prefs.preferred_limit || 100;
                    this.autoRefresh = prefs.auto_refresh !== false;
                    
                    // Update UI elements
                    document.getElementById('symbolSelect').value = this.currentSymbol;
                    document.getElementById('timeframeSelect').value = this.currentTimeframe;
                    document.getElementById('limitSelect').value = this.currentLimit;
                }
            }
        } catch (error) {
            console.error('Error loading user preferences:', error);
        }
        
        // Load initial data after preferences are loaded
        await this.loadInitialData();
    }

    async saveUserPreferences() {
        try {
            const preferences = {
                symbol: this.currentSymbol,
                timeframe: this.currentTimeframe,
                limit: this.currentLimit,
                auto_refresh: this.autoRefresh
            };
            
            await fetch('/api/preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(preferences)
            });
        } catch (error) {
            console.error('Error saving user preferences:', error);
        }
    }

    async loadInitialData() {
        await this.loadMarketData();
        
        // Set up auto-refresh every 30 seconds if enabled
        if (this.autoRefresh) {
            this.refreshInterval = setInterval(() => {
                if (!this.isLoading) {
                    this.refreshData();
                }
            }, 30000);
        }
    }

    async loadMarketData() {
        this.showLoading();
        
        try {
            // Load comprehensive market data
            const response = await fetch(`/api/market-data/${this.currentSymbol}?timeframe=${this.currentTimeframe}&limit=${this.currentLimit}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Failed to load market data');
            }
            
            this.updateDashboard(result.data);
            this.hideLoading();
            
        } catch (error) {
            console.error('Error loading market data:', error);
            this.showError(error.message);
        }
    }

    async refreshData() {
        // Refresh without showing loading indicator
        try {
            const response = await fetch(`/api/market-data/${this.currentSymbol}?timeframe=${this.currentTimeframe}&limit=${this.currentLimit}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.updateDashboard(result.data);
            }
            
        } catch (error) {
            console.error('Error refreshing data:', error);
        }
    }

    updateDashboard(data) {
        // Update market summary
        this.updateMarketSummary(data.candlestick);
        
        // Update candlestick chart and table
        this.updateCandlestickData(data.candlestick);
        
        // Update orderbook
        if (data.orderbook) {
            this.updateOrderbook(data.orderbook);
        }
        
        // Update technical indicators
        if (data.technical_indicators) {
            this.updateTechnicalIndicators(data.technical_indicators);
        }
        
        // Update open interest
        if (data.open_interest) {
            this.updateOpenInterest(data.open_interest);
        }
    }

    updateMarketSummary(candlestickData) {
        if (!candlestickData || candlestickData.length === 0) return;
        
        const latest = candlestickData[candlestickData.length - 1];
        const previous = candlestickData.length > 1 ? candlestickData[candlestickData.length - 2] : latest;
        
        const currentPrice = latest.close;
        const priceChange = currentPrice - previous.close;
        const priceChangePercent = (priceChange / previous.close) * 100;
        
        document.getElementById('currentPrice').textContent = currentPrice.toFixed(2);
        
        const changeElement = document.getElementById('priceChange');
        changeElement.textContent = `${priceChange >= 0 ? '+' : ''}${priceChange.toFixed(2)} (${priceChangePercent.toFixed(2)}%)`;
        changeElement.className = priceChange >= 0 ? 'fs-4 fw-bold price-up' : 'fs-4 fw-bold price-down';
    }

    updateCandlestickData(data) {
        if (!data || data.length === 0) return;
        
        // Update Plotly.js chart
        this.updatePlotlyChart(data);
        
        // Update volume chart for Volume Analysis tab
        chartManager.createVolumeChart('volumeChart', data);
        
        // Update table
        const tableBody = document.getElementById('candlestickTable');
        tableBody.innerHTML = '';
        
        // Show latest 20 entries
        const displayData = data.slice(-20).reverse();
        
        displayData.forEach(item => {
            const row = document.createElement('tr');
            row.className = 'fade-in';
            
            const priceChangeClass = item.close > item.open ? 'price-up' : 'price-down';
            
            row.innerHTML = `
                <td>${new Date(item.timestamp).toLocaleString()}</td>
                <td class="${priceChangeClass}">${item.open.toFixed(2)}</td>
                <td class="${priceChangeClass}">${item.high.toFixed(2)}</td>
                <td class="${priceChangeClass}">${item.low.toFixed(2)}</td>
                <td class="${priceChangeClass}">${item.close.toFixed(2)}</td>
                <td>${item.volume.toFixed(2)}</td>
            `;
            
            tableBody.appendChild(row);
        });
    }

    updatePlotlyChart(data) {
        if (!data || data.length === 0) return;
        
        // Show loading
        document.getElementById('chartLoading').style.display = 'block';
        document.getElementById('candlestickChart').style.display = 'none';
        
        // Update chart title
        document.getElementById('chartTitle').textContent = `(${this.currentSymbol} - ${this.currentTimeframe})`;
        
        // Prepare data for Plotly with ISO timestamp format
        const x = data.map(d => new Date(d.timestamp).toISOString());
        const open = data.map(d => d.open);
        const high = data.map(d => d.high);
        const low = data.map(d => d.low);
        const close = data.map(d => d.close);
        const volume = data.map(d => d.volume);
        
        // Create candlestick trace
        const candleTrace = {
            x: x,
            open: open,
            high: high,
            low: low,
            close: close,
            type: 'candlestick',
            name: this.currentSymbol,
            increasing: { line: { color: '#00cc96' } }, // hijau
            decreasing: { line: { color: '#ef553b' } }, // merah
            xaxis: 'x',
            yaxis: 'y'
        };

        // Create volume trace
        const volumeTrace = {
            x: x,
            y: volume,
            type: 'bar',
            name: 'Volume',
            marker: {
                color: close.map((c, i) => c > open[i] ? '#00cc96' : '#ef553b')
            },
            xaxis: 'x',
            yaxis: 'y2'
        };

        // Layout configuration
        const layout = {
            title: `${this.currentSymbol} Chart - ${this.currentTimeframe}`,
            dragmode: 'zoom',
            showlegend: false,
            grid: { rows: 2, columns: 1, subplots: [['xy'], ['xy2']], roworder: 'top to bottom' },
            height: 600,
            xaxis: {
                rangeslider: { visible: false },
                tickformat: "%m-%d %H:%M",      // Format tanggal
                tickangle: -45,
                showgrid: false,
                zeroline: false
            },
            yaxis: {
                domain: [0.3, 1], // atas = candle
                title: 'Price'
            },
            yaxis2: {
                domain: [0, 0.25], // bawah = volume
                title: 'Volume',
                showgrid: false
            },
            plot_bgcolor: "#1e1e2f",
            paper_bgcolor: "#1e1e2f",
            font: { color: "#ddd" }
        };

        // Plot the chart
        Plotly.newPlot('candlestickChart', [candleTrace, volumeTrace], layout, { responsive: true })
            .then(() => {
                // Hide loading
                document.getElementById('chartLoading').style.display = 'none';
                document.getElementById('candlestickChart').style.display = 'block';
            })
            .catch(error => {
                console.error('Error creating Plotly chart:', error);
                document.getElementById('chartLoading').style.display = 'none';
                document.getElementById('candlestickChart').style.display = 'block';
            });
    }

    updateOrderbook(data) {
        if (!data) return;
        
        // Update depth chart
        chartManager.createDepthChart('depthChart', data);
        
        // Update bids table
        const bidsTable = document.getElementById('bidsTable');
        bidsTable.innerHTML = '';
        
        let bidTotal = 0;
        data.bids.slice(0, 10).forEach(bid => {
            bidTotal += bid.size;
            const row = document.createElement('tr');
            row.className = 'bid-row fade-in';
            
            row.innerHTML = `
                <td class="price-up">${bid.price.toFixed(2)}</td>
                <td>${bid.size.toFixed(4)}</td>
                <td>${bidTotal.toFixed(4)}</td>
            `;
            
            bidsTable.appendChild(row);
        });
        
        // Update asks table
        const asksTable = document.getElementById('asksTable');
        asksTable.innerHTML = '';
        
        let askTotal = 0;
        data.asks.slice(0, 10).forEach(ask => {
            askTotal += ask.size;
            const row = document.createElement('tr');
            row.className = 'ask-row fade-in';
            
            row.innerHTML = `
                <td class="price-down">${ask.price.toFixed(2)}</td>
                <td>${ask.size.toFixed(4)}</td>
                <td>${askTotal.toFixed(4)}</td>
            `;
            
            asksTable.appendChild(row);
        });
        
        // Update orderbook statistics
        const bestBid = data.bids[0]?.price || 0;
        const bestAsk = data.asks[0]?.price || 0;
        const spread = bestAsk - bestBid;
        const midPrice = (bestBid + bestAsk) / 2;
        
        document.getElementById('bestBid').textContent = bestBid.toFixed(2);
        document.getElementById('bestAsk').textContent = bestAsk.toFixed(2);
        document.getElementById('spreadValue').textContent = spread.toFixed(2);
        document.getElementById('midPrice').textContent = midPrice.toFixed(2);
    }

    updateTechnicalIndicators(indicators) {
        if (!indicators) return;
        
        // Update MACD chart
        if (indicators.macd) {
            chartManager.createMACDChart('macdChart', indicators.macd);
        }
        
        // Update OBV chart
        if (indicators.obv) {
            chartManager.createOBVChart('obvChart', indicators.obv);
        }
        
        // Update RSI chart
        if (indicators.rsi) {
            chartManager.createRSIChart('rsiChart', indicators.rsi);
        }
        
        // Update volume analysis
        if (indicators.volume_analysis) {
            this.updateVolumeAnalysis(indicators.volume_analysis);
        }
    }

    updateVolumeAnalysis(volumeData) {
        if (!volumeData) return;
        
        const volumeStats = document.getElementById('volumeStats');
        volumeStats.innerHTML = `
            <div class="mb-3">
                <div class="indicator-label">Average Volume</div>
                <div class="indicator-value">${volumeData.average_volume.toFixed(2)}</div>
            </div>
            <div class="mb-3">
                <div class="indicator-label">Total Volume</div>
                <div class="indicator-value">${volumeData.total_volume.toFixed(2)}</div>
            </div>
            <div class="mb-3">
                <div class="indicator-label">Volume Trend</div>
                <div class="indicator-value ${volumeData.volume_trend_percent >= 0 ? 'price-up' : 'price-down'}">
                    ${volumeData.volume_trend_percent.toFixed(2)}%
                </div>
            </div>
            <div class="mb-3">
                <div class="indicator-label">Price-Volume Correlation</div>
                <div class="indicator-value">
                    ${volumeData.volume_price_correlation.toFixed(3)}
                </div>
            </div>
        `;
    }

    updateOpenInterest(data) {
        if (!data) return;
        
        const openInterestDiv = document.getElementById('openInterestData');
        openInterestDiv.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="text-center">
                        <div class="fs-6 text-muted">Open Interest</div>
                        <div class="fs-4 fw-bold">${data.open_interest.toFixed(2)}</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="text-center">
                        <div class="fs-6 text-muted">Last Updated</div>
                        <div class="fs-6">${new Date(data.timestamp).toLocaleString()}</div>
                    </div>
                </div>
            </div>
        `;
    }

    handleTabChange(tabId) {
        // Handle specific tab changes if needed
        console.log('Tab changed to:', tabId);
        
        // Load trading signals when signals tab is activated
        if (tabId === 'signals-tab') {
            this.loadTradingSignals();
        }
        
        // Load snapshot analysis when snapshot tab is activated
        if (tabId === 'snapshot-tab') {
            this.loadSnapshotAnalysis();
        }
        
        // Trigger chart resize if needed
        setTimeout(() => {
            Object.keys(chartManager.charts).forEach(canvasId => {
                if (chartManager.charts[canvasId]) {
                    chartManager.charts[canvasId].resize();
                }
            });
        }, 100);
    }

    async loadTradingSignals() {
        try {
            // Show loading in signal analysis section
            document.getElementById('signalAnalysis').innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div class="mt-2">Analyzing market data...</div>
                </div>
            `;
            
            // Fetch comprehensive analysis
            const response = await fetch(`/api/comprehensive-analysis/${this.currentSymbol}/${this.currentTimeframe}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const analysis = await response.json();
            
            if (analysis.error) {
                throw new Error(analysis.error);
            }
            
            // Update UI with analysis results
            this.updateSignalAnalysis(analysis);
            
        } catch (error) {
            console.error('Error loading trading signals:', error);
            document.getElementById('signalAnalysis').innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div class="mt-2">Error loading signals: ${error.message}</div>
                </div>
            `;
        }
    }

    updateSignalAnalysis(analysis) {
        // Update main signal display
        const finalSignal = analysis.final_signal;
        const signalColor = finalSignal.signal === 'buy' ? 'success' : 
                           finalSignal.signal === 'sell' ? 'danger' : 'secondary';
        
        document.getElementById('signalAnalysis').innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <div class="card bg-${signalColor} text-white">
                        <div class="card-body text-center">
                            <h3 class="card-title">${finalSignal.direction.toUpperCase()}</h3>
                            <p class="card-text">
                                Strength: ${finalSignal.strength.toFixed(1)}%<br>
                                Confidence: ${finalSignal.confidence.toFixed(1)}%
                            </p>
                        </div>
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">Signal Composition</h6>
                            <div class="row">
                                <div class="col-md-4">
                                    <small class="text-muted">Buy Signals</small>
                                    <div class="fs-5 fw-bold text-success">${finalSignal.signal_count.buy}</div>
                                </div>
                                <div class="col-md-4">
                                    <small class="text-muted">Sell Signals</small>
                                    <div class="fs-5 fw-bold text-danger">${finalSignal.signal_count.sell}</div>
                                </div>
                                <div class="col-md-4">
                                    <small class="text-muted">Total</small>
                                    <div class="fs-5 fw-bold">${finalSignal.signal_count.total}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Update component signals
        const components = analysis.component_signals;
        
        document.getElementById('technicalSignals').innerHTML = this.formatComponentSignal(components.technical_indicators);
        document.getElementById('smcSignals').innerHTML = this.formatComponentSignal(components.smc_analysis);
        document.getElementById('priceActionSignals').innerHTML = this.formatComponentSignal(components.price_action);
        document.getElementById('volumeSignals').innerHTML = this.formatComponentSignal(components.volume_analysis);
        
        // Update trade setup
        if (analysis.trade_setup) {
            this.updateTradeSetup(analysis.trade_setup);
        }
        
        // Update risk assessment
        if (analysis.risk_assessment) {
            this.updateRiskAssessment(analysis.risk_assessment);
        }
    }

    formatComponentSignal(component) {
        if (!component || !component.signal) {
            return '<div class="text-muted">No data</div>';
        }
        
        const signalBadge = component.signal === 'buy' ? 'success' : 
                           component.signal === 'sell' ? 'danger' : 'secondary';
        
        let html = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="badge bg-${signalBadge}">${component.signal.toUpperCase()}</span>
                <small class="text-muted">${component.strength.toFixed(1)}%</small>
            </div>
        `;
        
        if (component.components && component.components.length > 0) {
            html += '<div class="small">';
            component.components.slice(0, 3).forEach(comp => {
                const compBadge = comp.signal === 'buy' ? 'success' : 
                                 comp.signal === 'sell' ? 'danger' : 'secondary';
                html += `<span class="badge bg-${compBadge} me-1 mb-1">${comp.type}</span>`;
            });
            html += '</div>';
        }
        
        return html;
    }

    updateTradeSetup(setup) {
        if (setup.recommendation) {
            document.getElementById('tradeSetup').innerHTML = `
                <div class="text-center text-muted">${setup.recommendation}</div>
            `;
            return;
        }
        
        const directionColor = setup.direction === 'buy' ? 'success' : 'danger';
        
        document.getElementById('tradeSetup').innerHTML = `
            <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="badge bg-${directionColor}">${setup.direction.toUpperCase()}</span>
                    <small class="text-muted">${setup.confidence.toFixed(1)}% confidence</small>
                </div>
            </div>
            <div class="row text-center">
                <div class="col-12 mb-2">
                    <small class="text-muted">Entry</small>
                    <div class="fw-bold">${setup.entry_price.toFixed(4)}</div>
                </div>
                <div class="col-6">
                    <small class="text-muted">Stop Loss</small>
                    <div class="fw-bold text-danger">${setup.stop_loss.toFixed(4)}</div>
                </div>
                <div class="col-6">
                    <small class="text-muted">Take Profit</small>
                    <div class="fw-bold text-success">${setup.take_profit.toFixed(4)}</div>
                </div>
                <div class="col-12 mt-2">
                    <small class="text-muted">Risk/Reward</small>
                    <div class="fw-bold">1:${setup.risk_reward_ratio.toFixed(2)}</div>
                </div>
                <div class="col-12 mt-2">
                    <small class="text-muted">Position Size</small>
                    <div class="fw-bold">${setup.position_size}</div>
                </div>
            </div>
            <div class="mt-3">
                <small class="text-muted">${setup.notes}</small>
            </div>
        `;
    }

    updateRiskAssessment(risk) {
        const riskColor = risk.risk_level === 'high' ? 'danger' : 
                         risk.risk_level === 'medium' ? 'warning' : 'success';
        
        document.getElementById('riskAssessment').innerHTML = `
            <div class="text-center mb-3">
                <span class="badge bg-${riskColor} fs-6">${risk.risk_level.toUpperCase()}</span>
                <div class="mt-2">
                    <small class="text-muted">Risk Score</small>
                    <div class="fs-5 fw-bold">${risk.risk_score}/100</div>
                </div>
            </div>
            <div class="mb-3">
                <small class="text-muted">Volatility</small>
                <div class="fw-bold">${risk.volatility.toFixed(2)}%</div>
            </div>
            ${risk.risk_factors.length > 0 ? `
                <div>
                    <small class="text-muted">Risk Factors</small>
                    <div class="mt-1">
                        ${risk.risk_factors.map(factor => 
                            `<span class="badge bg-warning me-1 mb-1">${factor.type}</span>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
        `;
    }

    async loadSnapshotAnalysis(quickMode = false) {
        try {
            // Show loading in all snapshot sections
            const loadingMessage = quickMode ? 'Generating quick analysis...' : 'Generating professional analysis...';
            document.getElementById('snapshotNarrative').innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div class="mt-2">${loadingMessage}</div>
                    <div class="mt-2 text-muted small">
                        ${quickMode ? 'Quick mode - fast response (~15 seconds)' : 'Full mode - comprehensive analysis (~30 seconds)'}
                    </div>
                </div>
            `;
            
            // Reset all layer displays
            const layerIds = ['smcLayer', 'volumeLayer', 'orderbookLayer', 'rsiEmaLayer', 'fibonacciLayer', 'oiFundingLayer', 'trendLayer'];
            layerIds.forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    element.innerHTML = '<div class="text-center text-muted">Loading...</div>';
                } else {
                    console.warn(`Element with ID "${id}" not found`);
                }
            });
            
            // Use AI snapshot endpoint instead of regular snapshot
            const url = `/api/snapshot-ai/${this.currentSymbol}/${this.currentTimeframe}${quickMode ? '?quick=true' : ''}`;
            
            // Set timeout for the request
            const timeoutMs = quickMode ? 20000 : 40000; // 20s for quick, 40s for full
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
            
            const response = await fetch(url, {
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.error || !result.success) {
                throw new Error(result.error || 'AI snapshot generation failed');
            }
            
            // Update UI with AI snapshot results
            this.updateAISnapshotAnalysis(result);
            
        } catch (error) {
            console.error('Error loading snapshot analysis:', error);
            let errorMessage = error.message;
            
            if (error.name === 'AbortError') {
                errorMessage = `Request timeout - try ${quickMode ? 'full mode' : 'quick mode'} instead`;
            }
            
            document.getElementById('snapshotNarrative').innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div class="mt-2">Error loading snapshot: ${errorMessage}</div>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-primary me-2" onclick="window.okxDashboard.loadSnapshotAnalysis(true)">
                            <i class="fas fa-bolt me-1"></i>Try Quick Mode
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="window.okxDashboard.loadSnapshotAnalysis(false)">
                            <i class="fas fa-sync-alt me-1"></i>Retry Full Mode
                        </button>
                    </div>
                </div>
            `;
        }
    }

    updateAISnapshotAnalysis(aiSnapshot) {
        // Update narrative analysis with AI-generated content
        document.getElementById('snapshotNarrative').innerHTML = `
            <div class="text-start">
                <div class="narrative-content" style="white-space: pre-wrap; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6;">
                    ${aiSnapshot.ai_narrative || 'No AI narrative available'}
                </div>
            </div>
        `;
        
        // Update confidence score based on AI analysis
        const confidenceLevel = aiSnapshot.confluence_summary?.consensus_level || 0;
        document.getElementById('confidenceScore').textContent = `${(confidenceLevel * 100).toFixed(1)}%`;
        document.getElementById('confidenceText').textContent = `AI Analysis Confidence Level`;
        
        // Update layer analysis if available
        if (aiSnapshot.layer_analysis) {
            this.updateLayerAnalysis(aiSnapshot.layer_analysis);
        }
    }
    
    updateLayerAnalysis(layerAnalysis) {
        // Update individual layer analysis sections
        const layerIds = ['smcLayer', 'volumeLayer', 'orderbookLayer', 'rsiEmaLayer', 'fibonacciLayer', 'oiFundingLayer', 'trendLayer'];
        
        layerIds.forEach(layerId => {
            const element = document.getElementById(layerId);
            if (element) {
                const layerKey = layerId.replace('Layer', '_analysis');
                const layerData = layerAnalysis[layerKey] || {};
                
                element.innerHTML = `
                    <div class="text-center">
                        <div class="mb-2">
                            <span class="badge bg-${this.getSignalColor(layerData.signal || 'neutral')}">
                                ${(layerData.signal || 'neutral').toUpperCase()}
                            </span>
                        </div>
                        <div class="progress mb-2" style="height: 6px;">
                            <div class="progress-bar bg-${this.getSignalColor(layerData.signal || 'neutral')}" 
                                 style="width: ${(layerData.strength || 0) * 100}%"></div>
                        </div>
                        <small class="text-muted">Strength: ${((layerData.strength || 0) * 100).toFixed(1)}%</small>
                    </div>`;
            } else {
                console.warn(`Element with ID "${layerId}" not found`);
            }
        });
    }
    
    getSignalColor(signal) {
        switch(signal?.toLowerCase()) {
            case 'bullish': return 'success';
            case 'bearish': return 'danger';
            case 'neutral': return 'warning';
            default: return 'secondary';
        }
    }
    
    updateSnapshotAnalysis(snapshot) {
        // Legacy function - keeping for backward compatibility
        this.updateAISnapshotAnalysis(snapshot);
        
        // Update 7-layer analysis with null checks
        if (snapshot.smc_analysis) {
            const smcElement = document.getElementById('smcLayer');
            if (smcElement) {
                smcElement.innerHTML = this.formatLayerAnalysis(snapshot.smc_analysis);
            }
        }
        
        if (snapshot.volume_analysis) {
            const volumeElement = document.getElementById('volumeLayer');
            if (volumeElement) {
                volumeElement.innerHTML = this.formatLayerAnalysis(snapshot.volume_analysis);
            }
        }
        
        if (snapshot.orderbook_analysis) {
            const orderbookElement = document.getElementById('orderbookLayer');
            if (orderbookElement) {
                orderbookElement.innerHTML = this.formatLayerAnalysis(snapshot.orderbook_analysis);
            }
        }
        
        if (snapshot.rsi_ema_analysis) {
            const rsiEmaElement = document.getElementById('rsiEmaLayer');
            if (rsiEmaElement) {
                rsiEmaElement.innerHTML = this.formatLayerAnalysis(snapshot.rsi_ema_analysis);
            }
        }
        
        if (snapshot.fibonacci_analysis) {
            document.getElementById('fibonacciLayer').innerHTML = this.formatLayerAnalysis(snapshot.fibonacci_analysis);
        }
        
        if (snapshot.oi_funding_analysis) {
            document.getElementById('oiFundingLayer').innerHTML = this.formatLayerAnalysis(snapshot.oi_funding_analysis);
        }
        
        if (snapshot.trend_structure) {
            document.getElementById('trendLayer').innerHTML = this.formatLayerAnalysis(snapshot.trend_structure);
        }
        
        // Update primary trading plan
        if (snapshot.primary_plan) {
            this.updatePrimaryPlan(snapshot.primary_plan);
        }
        
        // Update alternative scenarios
        if (snapshot.alternative_scenarios) {
            this.updateAlternativeScenarios(snapshot.alternative_scenarios);
        }
        
        // Update risk factors
        if (snapshot.risk_factors) {
            this.updateRiskFactors(snapshot.risk_factors);
        }
    }

    formatLayerAnalysis(layer) {
        if (!layer || !layer.signal) {
            return '<div class="text-muted">No data available</div>';
        }
        
        const signalClass = layer.signal === 'bullish' ? 'bullish' : 
                           layer.signal === 'bearish' ? 'bearish' : 'neutral';
        
        // Generate tooltip content for additional insights
        const tooltipContent = this.generateTooltipContent(layer);
        
        // Get current timestamp
        const lastUpdate = new Date().toLocaleTimeString('id-ID', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        return `
            <div class="tooltip-container">
                <div class="layer-status ${signalClass} mb-2">
                    ${layer.signal.toUpperCase()}
                </div>
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <small class="text-muted">Strength: ${layer.strength.toFixed(1)}%</small>
                    <small class="text-muted">Updated: ${lastUpdate}</small>
                </div>
                <div class="layer-description">${layer.description}</div>
                <div class="tooltip-text">
                    ${tooltipContent}
                </div>
            </div>
        `;
    }
    
    generateTooltipContent(layer) {
        let tooltip = `<strong>Signal: ${layer.signal.toUpperCase()}</strong><br>`;
        tooltip += `<strong>Strength: ${layer.strength.toFixed(1)}%</strong><br><br>`;
        tooltip += `<strong>Analysis:</strong><br>${layer.description}<br><br>`;
        
        // Add specific insights based on layer type
        if (layer.volume_spike) {
            tooltip += `<strong>Volume Spike:</strong> Detected<br>`;
        }
        if (layer.cvd !== undefined) {
            tooltip += `<strong>CVD:</strong> ${layer.cvd > 0 ? '+' : ''}${layer.cvd.toFixed(0)}<br>`;
        }
        if (layer.imbalance !== undefined) {
            tooltip += `<strong>Orderbook Imbalance:</strong> ${layer.imbalance.toFixed(1)}%<br>`;
        }
        if (layer.rsi_value !== undefined) {
            tooltip += `<strong>RSI Value:</strong> ${layer.rsi_value.toFixed(1)}<br>`;
        }
        if (layer.fibonacci_level !== undefined) {
            tooltip += `<strong>Fibonacci Level:</strong> ${layer.fibonacci_level}<br>`;
        }
        if (layer.open_interest_change !== undefined) {
            tooltip += `<strong>OI Change:</strong> ${layer.open_interest_change > 0 ? '+' : ''}${layer.open_interest_change.toFixed(1)}%<br>`;
        }
        
        return tooltip;
    }

    updatePrimaryPlan(plan) {
        if (plan.direction === 'WAIT') {
            document.getElementById('primaryPlan').innerHTML = `
                <div class="text-center text-warning">
                    <i class="fas fa-pause-circle fs-3"></i>
                    <div class="mt-2">
                        <strong>WAIT</strong><br>
                        <small class="text-muted">${plan.reason}</small>
                    </div>
                </div>
            `;
            return;
        }
        
        const directionColor = plan.direction === 'LONG' ? 'success' : 'danger';
        const directionIcon = plan.direction === 'LONG' ? 'fa-arrow-up' : 'fa-arrow-down';
        
        document.getElementById('primaryPlan').innerHTML = `
            <div class="text-center">
                <div class="mb-3">
                    <i class="fas ${directionIcon} fs-3 text-${directionColor}"></i>
                    <div class="mt-1">
                        <span class="badge bg-${directionColor} fs-6">${plan.direction}</span>
                    </div>
                </div>
                <div class="row text-start">
                    <div class="col-12 mb-2">
                        <small class="text-muted">Entry Zone</small>
                        <div class="fw-bold">${plan.entry_zone}</div>
                    </div>
                    <div class="col-6 mb-2">
                        <small class="text-muted">Stop Loss</small>
                        <div class="fw-bold text-danger">${plan.stop_loss}</div>
                    </div>
                    <div class="col-6 mb-2">
                        <small class="text-muted">Take Profit 1</small>
                        <div class="fw-bold text-success">${plan.tp1}</div>
                    </div>
                    <div class="col-6 mb-2">
                        <small class="text-muted">Take Profit 2</small>
                        <div class="fw-bold text-success">${plan.tp2}</div>
                    </div>
                    <div class="col-6 mb-2">
                        <small class="text-muted">Risk/Reward</small>
                        <div class="fw-bold">${plan.risk_reward}</div>
                    </div>
                    <div class="col-12 mb-2">
                        <small class="text-muted">Position Size</small>
                        <div class="fw-bold">${plan.position_size}</div>
                    </div>
                    <div class="col-12">
                        <small class="text-muted">Confidence</small>
                        <div class="fw-bold">${plan.confidence}</div>
                    </div>
                </div>
                ${plan.entry_strategy ? `
                <div class="mt-3">
                    <small class="text-muted">Entry Strategy</small>
                    <div class="small text-info">${plan.entry_strategy}</div>
                </div>
                ` : ''}
                <div class="mt-3">
                    <small class="text-muted">${plan.notes}</small>
                </div>
            </div>
        `;
    }

    updateAlternativeScenarios(scenarios) {
        if (!scenarios || scenarios.length === 0) {
            document.getElementById('alternativeScenarios').innerHTML = 
                '<div class="text-muted">No alternative scenarios available</div>';
            return;
        }
        
        let html = '';
        scenarios.forEach((scenario, index) => {
            const colorClass = scenario.title.includes('BULLISH') ? 'success' : 
                              scenario.title.includes('BEARISH') ? 'danger' : 'warning';
            
            html += `
                <div class="card border-${colorClass} mb-3">
                    <div class="card-body">
                        <h6 class="card-title text-${colorClass}">${scenario.title}</h6>
                        <div class="row">
                            <div class="col-12 mb-2">
                                <small class="text-muted">Probability</small>
                                <div class="fw-bold">${scenario.probability}</div>
                            </div>
                            <div class="col-12 mb-2">
                                <small class="text-muted">Trigger</small>
                                <div class="small">${scenario.trigger}</div>
                            </div>
                            <div class="col-12 mb-2">
                                <small class="text-muted">Target</small>
                                <div class="small">${scenario.target}</div>
                            </div>
                            <div class="col-12 mb-2">
                                <small class="text-muted">Invalidation</small>
                                <div class="small">${scenario.invalidation}</div>
                            </div>
                            <div class="col-12">
                                <small class="text-muted">${scenario.description}</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('alternativeScenarios').innerHTML = html;
    }

    updateRiskFactors(riskFactors) {
        if (!riskFactors || riskFactors.length === 0) {
            document.getElementById('riskFactors').innerHTML = 
                '<div class="text-muted">No risk factors identified</div>';
            return;
        }
        
        let html = '';
        riskFactors.forEach(factor => {
            const severityColor = factor.severity === 'High' ? 'danger' : 
                                 factor.severity === 'Medium' ? 'warning' : 'info';
            
            html += `
                <div class="d-flex align-items-start mb-2">
                    <span class="badge bg-${severityColor} me-2">${factor.severity}</span>
                    <div class="flex-grow-1">
                        <div class="fw-bold">${factor.factor}</div>
                        <small class="text-muted">${factor.description}</small>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('riskFactors').innerHTML = html;
    }

    destroy() {
        // Clean up resources
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        chartManager.destroyAllCharts();
    }
}

// Global function for refreshing signals
function refreshSignals() {
    if (window.okxDashboard) {
        window.okxDashboard.loadTradingSignals();
    }
}

// Global function for refreshing snapshot
function refreshSnapshot() {
    if (window.okxDashboard) {
        window.okxDashboard.loadSnapshotAnalysis(false);
    }
}

// Global function for refreshing snapshot in quick mode
function refreshSnapshotQuick() {
    if (window.okxDashboard) {
        window.okxDashboard.loadSnapshotAnalysis(true);
    }
}

// Global function for copying snapshot
function copySnapshot() {
    const narrativeElement = document.getElementById('snapshotNarrative');
    const confidenceElement = document.getElementById('confidenceScore');
    const planElement = document.getElementById('primaryPlan');
    
    let copyText = "=== TRADING SNAPSHOT ANALYSIS ===\n\n";
    
    // Add narrative
    if (narrativeElement) {
        const narrativeText = narrativeElement.innerText || narrativeElement.textContent;
        copyText += narrativeText + "\n\n";
    }
    
    // Add confidence score
    if (confidenceElement) {
        const confidenceText = confidenceElement.innerText || confidenceElement.textContent;
        copyText += "CONFIDENCE SCORE: " + confidenceText + "\n\n";
    }
    
    // Add primary plan
    if (planElement) {
        const planText = planElement.innerText || planElement.textContent;
        copyText += "PRIMARY TRADING PLAN:\n" + planText + "\n\n";
    }
    
    copyText += "=== END SNAPSHOT ===\n";
    copyText += "Generated by OKX Market Analysis Dashboard";
    
    // Copy to clipboard
    navigator.clipboard.writeText(copyText).then(() => {
        // Show success message
        const btn = document.querySelector('button[onclick="copySnapshot()"]');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
        btn.classList.remove('btn-outline-success');
        btn.classList.add('btn-success');
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.remove('btn-success');
            btn.classList.add('btn-outline-success');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy to clipboard:', err);
        alert('Failed to copy to clipboard. Please try again.');
    });
}

// Export snapshot as PDF
function exportSnapshotPDF() {
    const symbol = document.getElementById('symbolSelect').value;
    const timeframe = document.getElementById('timeframeSelect').value;
    
    // Show loading state
    const exportBtn = document.querySelector('button[onclick="exportSnapshotPDF()"]');
    const originalContent = exportBtn.innerHTML;
    exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Exporting...';
    exportBtn.disabled = true;
    
    // Create form data
    const formData = new FormData();
    formData.append('symbol', symbol);
    formData.append('timeframe', timeframe);
    
    fetch('/export_snapshot_pdf', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to export PDF');
        }
        return response.blob();
    })
    .then(blob => {
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `snapshot_${symbol}_${timeframe}_${new Date().toISOString().slice(0, 10)}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('Error exporting PDF:', error);
        alert('Failed to export PDF. Please try again.');
    })
    .finally(() => {
        // Reset button state
        exportBtn.innerHTML = originalContent;
        exportBtn.disabled = false;
    });
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.okxDashboard = new OKXDashboard();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.okxDashboard) {
        window.okxDashboard.destroy();
    }
});
