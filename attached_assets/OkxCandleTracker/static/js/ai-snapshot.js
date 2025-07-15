/**
 * AI Snapshot Management
 * Handles AI-powered market analysis and visualization
 */

class AISnapshotManager {
    constructor() {
        this.aiSnapshotModal = null;
        this.confidenceChart = null;
        this.currentSnapshotData = null;
        this.init();
    }

    init() {
        this.aiSnapshotModal = new bootstrap.Modal(document.getElementById('aiSnapshotModal'));
        
        // Bind event listeners
        document.getElementById('aiSnapshotBtn').addEventListener('click', () => {
            this.generateAISnapshot(false);
        });
        
        document.getElementById('aiSnapshotQuickBtn').addEventListener('click', () => {
            this.generateAISnapshot(true);
        });
        
        document.getElementById('saveSnapshotBtn').addEventListener('click', () => {
            this.saveSnapshot();
        });
    }

    async generateAISnapshot(quickMode = false) {
        const symbolSelect = document.getElementById('symbolSelect');
        const timeframeSelect = document.getElementById('timeframeSelect');
        
        const symbol = symbolSelect.value;
        const timeframe = timeframeSelect.value;
        
        // Show modal with loading state
        this.showLoadingModal();
        
        try {
            console.log(`🚀 Generating AI Snapshot for ${symbol} ${timeframe} (Quick: ${quickMode})`);
            
            // Call AI snapshot API with timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 45000); // 45 second timeout
            
            const response = await fetch(`/api/snapshot-ai/${symbol}/${timeframe}?quick=${quickMode}`, {
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            // Check if response is ok
            if (!response.ok) {
                throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }
            
            // Try to parse JSON
            let data;
            try {
                data = await response.json();
                console.log('✅ API Response received:', data);
            } catch (jsonError) {
                // If JSON parsing fails, the server likely returned HTML error page
                const textResponse = await response.text();
                console.error('Failed to parse JSON response:', textResponse);
                throw new Error('Server returned invalid JSON. This usually means OpenAI API is having issues or the API key is invalid.');
            }
            
            // Check if API response indicates success
            if (!data.success || data.error) {
                throw new Error(data.error || 'AI snapshot generation failed');
            }
            
            // Validate that we have AI narrative content
            if (!data.ai_narrative || data.ai_narrative === 'No AI narrative available') {
                throw new Error('AI narrative generation failed. Please check OpenAI API configuration.');
            }
            
            console.log('✅ AI Narrative Length:', data.ai_narrative.length);
            console.log('✅ AI Narrative Preview:', data.ai_narrative.substring(0, 100) + '...');
            
            // Store current snapshot data
            this.currentSnapshotData = data;
            
            // Display AI narrative
            console.log('🎯 Calling displayAISnapshot...');
            this.displayAISnapshot(data);
            
            // Create confidence radar chart
            console.log('📊 Creating confidence radar chart...');
            this.createConfidenceRadar(data.layer_analysis);
            
            // Display layer analysis
            console.log('📝 Displaying layer analysis...');
            this.displayLayerAnalysis(data.layer_analysis);
            
            console.log('✅ AI Snapshot generation completed successfully!');
            
        } catch (error) {
            console.error('Error generating AI snapshot:', error);
            
            // Handle specific error types
            let errorMessage = error.message;
            let errorType = 'danger';
            
            if (error.name === 'AbortError') {
                errorMessage = 'Request timeout. Try Quick Mode for faster results.';
                errorType = 'warning';
            } else if (error.message.includes('500')) {
                errorMessage = 'Server busy. Please try Quick Mode or wait a moment.';
                errorType = 'warning';
            } else if (error.message.includes('OpenAI')) {
                errorMessage = 'AI service temporarily unavailable. Please try again.';
                errorType = 'info';
            } else if (error.message.includes('NetworkError') || error.message.includes('fetch')) {
                errorMessage = 'Network error. Please check your connection and try again.';
                errorType = 'warning';
            }
            
            this.showErrorModal(errorMessage, errorType);
        }
    }

    showLoadingModal() {
        const content = document.getElementById('aiSnapshotContent');
        content.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Generating AI analysis...</p>
                <small class="text-muted">This may take 15-30 seconds</small>
            </div>
        `;
        
        this.aiSnapshotModal.show();
    }

    showErrorModal(errorMessage, errorType = 'danger') {
        const content = document.getElementById('aiSnapshotContent');
        const alertClass = errorType === 'warning' ? 'alert-warning' : 
                          errorType === 'info' ? 'alert-info' : 'alert-danger';
        const iconClass = errorType === 'warning' ? 'fas fa-exclamation-triangle' : 
                         errorType === 'info' ? 'fas fa-info-circle' : 'fas fa-exclamation-triangle';
        
        content.innerHTML = `
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 25px; border-radius: 12px; margin: 15px;">
                <div class="alert ${alertClass}" role="alert" style="border-radius: 8px;">
                    <i class="${iconClass} me-2"></i>
                    <strong>Notice:</strong> ${errorMessage}
                    <hr>
                    <div class="mt-3">
                        <button class="btn btn-outline-success btn-sm me-2" onclick="aiSnapshotManager.generateAISnapshot(true)">
                            <i class="fas fa-bolt me-1"></i>
                            Try Quick Mode
                        </button>
                    <button class="btn btn-outline-success btn-sm" onclick="this.closest('.modal').querySelector('.btn-close').click()">
                        <i class="fas fa-times me-1"></i>
                        Close
                    </button>
                </div>
                <small class="text-muted mt-2 d-block">
                    If the problem persists, please check your OpenAI API key configuration or try again later.
                </small>
            </div>
        `;
    }

    displayAISnapshot(data) {
        const content = document.getElementById('aiSnapshotContent');
        const modeIcon = data.quick_mode ? '<i class="fas fa-bolt text-warning"></i>' : '<i class="fas fa-brain text-success"></i>';
        const modeText = data.quick_mode ? 'Quick Mode' : 'Comprehensive Mode';
        
        // Ensure AI narrative is available
        const aiNarrative = data.ai_narrative || 'No AI narrative available';
        
        // Create the HTML content (simplified to focus on the narrative)
        const htmlContent = `
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="card-title mb-0">
                        <i class="fas fa-chart-line me-2"></i>
                        ${data.symbol} ${data.timeframe} Analysis
                    </h6>
                    <span class="badge bg-secondary">${modeIcon} ${modeText}</span>
                </div>
                <div class="card-body">
                    <div class="ai-narrative-container mb-3">
                        <h6 class="fw-bold mb-2">
                            <i class="fas fa-robot me-2"></i>
                            AI Analysis
                        </h6>
                        <div class="ai-narrative-text p-3 bg-light rounded" style="white-space: pre-wrap; line-height: 1.6; font-size: 0.95rem;">
                            ${aiNarrative}
                        </div>
                    </div>
                    <hr>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>
                            Generated: ${new Date(data.generated_at).toLocaleString()}
                        </small>
                        <div class="confluence-summary">
                            <span class="badge bg-${this.getConfidenceColor(data.confluence_summary?.overall_signal || 'neutral')}">
                                ${data.confluence_summary?.overall_signal?.toUpperCase() || 'NEUTRAL'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Set the content with professional styling
        content.innerHTML = `
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 25px; border-radius: 12px; margin: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h4 style="color: #212529; margin: 0; font-weight: 600;">
                        <i class="fas fa-brain" style="color: #28a745; margin-right: 10px;"></i>
                        AI Market Analysis
                    </h4>
                    <div>
                        <span style="background: ${data.quick_mode ? 'linear-gradient(135deg, #ffc107, #fd7e14)' : 'linear-gradient(135deg, #28a745, #20c997)'}; 
                                     color: white; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 500;">
                            ${data.quick_mode ? '⚡ Quick Mode' : '🧠 Comprehensive Mode'}
                        </span>
                    </div>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="color: #212529; line-height: 1.8; white-space: pre-wrap; font-size: 14px;">
                        ${aiNarrative}
                    </div>
                </div>
                
                <div style="margin-top: 20px; display: flex; justify-content: space-between; align-items: center; padding-top: 15px; border-top: 1px solid #dee2e6;">
                    <div style="color: #6c757d; font-size: 12px;">
                        <i class="fas fa-clock" style="margin-right: 5px;"></i>
                        Generated: ${new Date(data.generated_at).toLocaleString()}
                    </div>
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <div style="color: #6c757d; font-size: 12px;">
                            Signal Strength: ${Math.round(data.confluence_summary?.signal_strength || 0)}%
                        </div>
                        <span style="background: ${this.getConfidenceColor(data.confluence_summary?.overall_signal || 'neutral') === 'success' ? '#28a745' : 
                                                    this.getConfidenceColor(data.confluence_summary?.overall_signal || 'neutral') === 'danger' ? '#dc3545' : '#ffc107'}; 
                                     color: white; padding: 4px 10px; border-radius: 15px; font-size: 11px; font-weight: 500;">
                            ${data.confluence_summary?.overall_signal?.toUpperCase() || 'NEUTRAL'}
                        </span>
                    </div>
                </div>
            </div>
        `;
        
        // Log for debugging (simplified)
        console.log('✅ AI Snapshot displayed successfully');
        console.log('📊 Narrative length:', aiNarrative.length, 'characters');
        console.log('📈 Signal strength:', Math.round(data.confluence_summary?.signal_strength || 0), '%');
    }

    createConfidenceRadar(layerAnalysis) {
        const ctx = document.getElementById('confidenceRadarChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.confidenceChart) {
            this.confidenceChart.destroy();
        }
        
        const layers = [
            'SMC Analysis',
            'Volume Analysis',
            'Orderbook Analysis',
            'RSI/EMA Analysis',
            'Fibonacci Analysis',
            'OI Analysis',
            'Funding Analysis'
        ];
        
        const confidenceData = layers.map(layer => {
            const layerKey = layer.toLowerCase().replace(' analysis', '_analysis').replace(' ', '_');
            return layerAnalysis?.[layerKey]?.strength || 0;
        });
        
        this.confidenceChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: layers,
                datasets: [{
                    label: 'Confidence Level',
                    data: confidenceData,
                    fill: true,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: {
                            display: false
                        },
                        suggestedMin: 0,
                        suggestedMax: 1
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    displayLayerAnalysis(layerAnalysis) {
        const container = document.getElementById('layerAnalysis');
        
        const layers = [
            { key: 'smc_analysis', name: 'SMC Analysis', icon: 'fas fa-chart-bar' },
            { key: 'volume_analysis', name: 'Volume Analysis', icon: 'fas fa-chart-area' },
            { key: 'orderbook_analysis', name: 'Orderbook Analysis', icon: 'fas fa-list' },
            { key: 'rsi_ema_analysis', name: 'RSI/EMA Analysis', icon: 'fas fa-wave-square' },
            { key: 'fibonacci_analysis', name: 'Fibonacci Analysis', icon: 'fas fa-chart-line' },
            { key: 'oi_analysis', name: 'OI Analysis', icon: 'fas fa-coins' },
            { key: 'funding_analysis', name: 'Funding Analysis', icon: 'fas fa-percentage' }
        ];
        
        let html = '';
        
        layers.forEach(layer => {
            const analysis = layerAnalysis?.[layer.key] || {};
            const signal = analysis.signal || 'neutral';
            const strength = analysis.strength || 0;
            
            html += `
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="fw-bold">
                            <i class="${layer.icon} me-2"></i>
                            ${layer.name}
                        </span>
                        <span class="badge bg-${this.getConfidenceColor(signal)}">
                            ${signal.toUpperCase()}
                        </span>
                    </div>
                    <div class="progress mt-2" style="height: 6px;">
                        <div class="progress-bar bg-${this.getConfidenceColor(signal)}" 
                             role="progressbar" 
                             style="width: ${strength * 100}%"
                             aria-valuenow="${strength * 100}" 
                             aria-valuemin="0" 
                             aria-valuemax="100">
                        </div>
                    </div>
                    <small class="text-muted">Confidence: ${(strength * 100).toFixed(1)}%</small>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }

    getConfidenceColor(signal) {
        switch(signal?.toLowerCase()) {
            case 'bullish':
                return 'success';
            case 'bearish':
                return 'danger';
            case 'neutral':
                return 'warning';
            default:
                return 'secondary';
        }
    }

    async saveSnapshot() {
        if (!this.currentSnapshotData) {
            alert('No snapshot data to save');
            return;
        }
        
        try {
            const response = await fetch('/api/snapshot-archive', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.currentSnapshotData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('Snapshot saved successfully!');
            } else {
                alert('Failed to save snapshot: ' + result.error);
            }
            
        } catch (error) {
            console.error('Error saving snapshot:', error);
            alert('Error saving snapshot: ' + error.message);
        }
    }
}

// Initialize AI Snapshot Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AISnapshotManager();
});