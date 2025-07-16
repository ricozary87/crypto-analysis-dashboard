import { useState } from 'react';

export default function Topbar({ onAnalyze }) {
  const [pair, setPair] = useState('SOL/USDT');
  const [tf, setTf] = useState('1H');

  return (
    <div className="bg-gray-800 p-4 mb-4 rounded-xl flex flex-col md:flex-row md:items-center md:justify-between">
      <div className="flex items-center gap-4">
        <select className="bg-gray-700 p-2 rounded" value={pair} onChange={(e) => setPair(e.target.value)}>
          <option value="SOL/USDT">SOL/USDT</option>
          <option value="BTC/USDT">BTC/USDT</option>
          <option value="ETH/USDT">ETH/USDT</option>
        </select>
        <select className="bg-gray-700 p-2 rounded" value={tf} onChange={(e) => setTf(e.target.value)}>
          <option value="5m">5m</option>
          <option value="15m">15m</option>
          <option value="1H">1H</option>
          <option value="4H">4H</option>
        </select>
      </div>
      <button onClick={() => onAnalyze(pair, tf)} className="mt-4 md:mt-0 bg-green-600 px-4 py-2 rounded">
        🔍 Analisa Sekarang
      </button>
    </div>
  );
}
