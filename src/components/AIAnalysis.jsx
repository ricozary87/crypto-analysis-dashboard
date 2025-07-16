import React, { useState, useEffect } from 'react';

export default function AIAnalysis({ symbol, analysisData }) {
  const [aiNarrative, setAiNarrative] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (symbol) {
      fetchAIAnalysis();
    }
  }, [symbol]);

  const fetchAIAnalysis = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:5000/api/enhanced-ai/narrative/${symbol}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        setAiNarrative(result.narrative);
      } else {
        throw new Error(result.error || 'AI analysis failed');
      }
    } catch (error) {
      console.error('AI analysis error:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mt-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          AI-Powered Analysis
        </h3>
        <div className="flex items-center space-x-3">
          <div className="animate-spin w-5 h-5 border-2 border-green-400 border-t-transparent rounded-full"></div>
          <span className="text-gray-400">Generating AI analysis...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mt-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          AI-Powered Analysis
        </h3>
        <div className="bg-red-900 border border-red-600 p-4 rounded-lg">
          <p className="text-red-300">Error: {error}</p>
          <button
            onClick={fetchAIAnalysis}
            className="mt-2 px-4 py-2 bg-red-700 hover:bg-red-600 text-white rounded transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mt-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">
          AI-Powered Analysis
        </h3>
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 bg-green-400 rounded-full"></span>
          <span className="text-sm text-gray-400">GPT-4o</span>
        </div>
      </div>
      
      {aiNarrative ? (
        <div className="space-y-4">
          <div className="bg-gray-900 border border-gray-600 rounded-lg p-4">
            <div className="whitespace-pre-wrap text-gray-300 leading-relaxed">
              {aiNarrative}
            </div>
          </div>
          
          <div className="flex justify-between items-center text-sm text-gray-400">
            <span>Analysis for {symbol}</span>
            <button
              onClick={fetchAIAnalysis}
              className="px-3 py-1 bg-green-600 hover:bg-green-500 text-white rounded transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-400">No AI analysis available</p>
          <button
            onClick={fetchAIAnalysis}
            className="mt-2 px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded transition-colors"
          >
            Generate Analysis
          </button>
        </div>
      )}
    </div>
  );
}