import React, { useState } from 'react';
import GPTSignalBox from './components/GPTSignalBox';

const Dashboard = () => {
  const [selectedPair, setSelectedPair] = useState('SOL/USDT');

  const handleChangePair = (pair) => {
    setSelectedPair(pair);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Tombol pilih pair */}
      <div className="flex gap-2">
        {['SOL/USDT', 'BTC/USDT', 'ETH/USDT', 'DOT/USDT'].map(pair => (
          <button
            key={pair}
            onClick={() => handleChangePair(pair)}
            className={`px-4 py-2 rounded-lg font-semibold ${
              selectedPair === pair ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400'
            }`}
          >
            {pair}
          </button>
        ))}
      </div>

      {/* Komponen GPTSignalBox */}
      <GPTSignalBox key={selectedPair} pair={selectedPair} tf="1H" />
    </div>
  );
};

export default Dashboard;
