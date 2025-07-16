import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import CryptoOverview from './components/CryptoOverview';
import ChartView from './components/ChartView';
import SMCAnalysis from './components/SMCAnalysis';
import AIAnalysis from './components/AIAnalysis';

const API_BASE = 'http://localhost:5000';

function App() {
  const [selectedSymbol, setSelectedSymbol] = useState('SOL');
  const [selectedTimeframe, setSelectedTimeframe] = useState('1H');
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async (pair, tf) => {
    setLoading(true);
    setError(null);
    
    try {
      const symbol = pair.split('/')[0]; // SOL/USDT -> SOL
      const response = await fetch(`${API_BASE}/api/analyze/${symbol}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        setAnalysisData(result);
        setSelectedSymbol(symbol);
        setSelectedTimeframe(tf);
      } else {
        throw new Error(result.error || 'Analysis failed');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Auto-analyze SOL on first load
  useEffect(() => {
    handleAnalyze('SOL/USDT', '1H');
  }, []);

  return (
    <div className="flex min-h-screen bg-gray-900 text-white">
      <Sidebar onSelectPair={(pair) => handleAnalyze(pair, selectedTimeframe)} />
      <main className="flex-1 p-6 overflow-y-auto">
        <Topbar onAnalyze={handleAnalyze} />
        
        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin w-8 h-8 border-2 border-green-400 border-t-transparent rounded-full mx-auto"></div>
            <p className="mt-2 text-gray-400">Analyzing {selectedSymbol}...</p>
          </div>
        )}
        
        {error && (
          <div className="bg-red-900 border border-red-600 p-4 rounded-xl mb-4">
            <p className="text-red-300">Error: {error}</p>
          </div>
        )}
        
        {analysisData && !loading && (
          <>
            <CryptoOverview data={analysisData} />
            <ChartView candles={analysisData.analysis?.chart || []} />
            <SMCAnalysis smcData={analysisData.analysis?.smc_analysis || {}} />
            <AIAnalysis symbol={selectedSymbol} analysisData={analysisData} />
          </>
        )}
      </main>
    </div>
  );
}

export default App;
