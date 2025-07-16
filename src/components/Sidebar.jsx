export default function Sidebar({ onSelectPair }) {
  const pairs = ['SOL/USDT', 'BTC/USDT', 'ETH/USDT', 'TIA/USDT', 'RENDER/USDT'];
  
  return (
    <aside className="w-64 bg-gray-800 p-4 hidden md:block">
      <h2 className="text-xl font-bold mb-4">Pairs</h2>
      <ul className="space-y-2">
        {pairs.map(pair => (
          <li key={pair}>
            <button 
              className="w-full text-left hover:text-green-400 transition-colors"
              onClick={() => onSelectPair && onSelectPair(pair)}
            >
              {pair}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
