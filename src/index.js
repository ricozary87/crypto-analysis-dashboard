import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles.css';

// Professional Crypto Trading Dashboard Component
const Dashboard = () => {
    const [selectedPair, setSelectedPair] = React.useState('BTC/USDT');
    const [selectedTimeframe, setSelectedTimeframe] = React.useState('1H');
    const [lastUpdate, setLastUpdate] = React.useState(new Date());
    const [chartData, setChartData] = React.useState([]);
    
    React.useEffect(() => {
        // Initialize dashboard
        setLastUpdate(new Date());
        console.log('Dashboard initialized');
    }, []);

    return (
        <div className="min-h-screen bg-gray-900 text-white">
            <div className="container mx-auto p-4">
                <h1 className="text-3xl font-bold mb-6 text-center">
                    🚀 Crypto Trading Dashboard
                </h1>
                
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Symbol Selection */}
                    <div className="bg-gray-800 rounded-lg p-6">
                        <h2 className="text-xl font-semibold mb-4">Symbol Selection</h2>
                        <select 
                            value={selectedPair}
                            onChange={(e) => setSelectedPair(e.target.value)}
                            className="w-full p-2 bg-gray-700 rounded"
                        >
                            <option value="BTC/USDT">BTC/USDT</option>
                            <option value="ETH/USDT">ETH/USDT</option>
                            <option value="SOL/USDT">SOL/USDT</option>
                        </select>
                    </div>

                    {/* Timeframe Selection */}
                    <div className="bg-gray-800 rounded-lg p-6">
                        <h2 className="text-xl font-semibold mb-4">Timeframe</h2>
                        <select 
                            value={selectedTimeframe}
                            onChange={(e) => setSelectedTimeframe(e.target.value)}
                            className="w-full p-2 bg-gray-700 rounded"
                        >
                            <option value="5m">5 Minutes</option>
                            <option value="15m">15 Minutes</option>
                            <option value="1H">1 Hour</option>
                            <option value="4H">4 Hours</option>
                        </select>
                    </div>

                    {/* Status */}
                    <div className="bg-gray-800 rounded-lg p-6">
                        <h2 className="text-xl font-semibold mb-4">Status</h2>
                        <div className="flex items-center">
                            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                            <span>Connected</span>
                        </div>
                        <p className="text-sm text-gray-400 mt-2">
                            Last Update: {lastUpdate.toLocaleTimeString()}
                        </p>
                    </div>
                </div>

                {/* Chart Area */}
                <div className="mt-8 bg-gray-800 rounded-lg p-6">
                    <h2 className="text-xl font-semibold mb-4">Chart Analysis</h2>
                    <div className="h-96 bg-gray-700 rounded flex items-center justify-center">
                        <div className="text-center">
                            <p className="text-lg">Chart for {selectedPair}</p>
                            <p className="text-sm text-gray-400">Timeframe: {selectedTimeframe}</p>
                        </div>
                    </div>
                </div>

                {/* Trading Analysis */}
                <div className="mt-8 bg-gray-800 rounded-lg p-6">
                    <h2 className="text-xl font-semibold mb-4">Trading Analysis</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <h3 className="text-lg font-medium mb-2">SMC Analysis</h3>
                            <p className="text-gray-400">Smart Money Concept analysis coming soon...</p>
                        </div>
                        <div>
                            <h3 className="text-lg font-medium mb-2">AI Insights</h3>
                            <p className="text-gray-400">AI-powered trading insights coming soon...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// React 18 createRoot implementation
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<Dashboard />);