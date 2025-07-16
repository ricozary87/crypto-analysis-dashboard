export default function CryptoOverview({ data }) {
  if (!data || !data.analysis) {
    return <div className="bg-gray-800 p-4 rounded-xl text-gray-400">Loading market data...</div>;
  }

  const { analysis } = data;
  const price = analysis.current_price || 0;
  const volume = analysis.volume_24h || 0;
  const priceChange = analysis.price_change_24h || 0;
  
  const getTrendColor = (change) => {
    if (change > 0) return 'text-green-400';
    if (change < 0) return 'text-red-400';
    return 'text-gray-400';
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toFixed(2);
  };

  return (
    <div className="bg-gray-800 p-4 rounded-xl mb-4 grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
      <div>
        <p className="text-gray-400 text-sm">Harga</p>
        <p className="text-xl text-green-400 font-bold">${price.toFixed(2)}</p>
        <p className={`text-sm ${getTrendColor(priceChange)}`}>
          {priceChange > 0 ? '+' : ''}{priceChange.toFixed(2)}%
        </p>
      </div>
      <div>
        <p className="text-gray-400 text-sm">Volume 24H</p>
        <p className="text-lg font-semibold">${formatNumber(volume)}</p>
      </div>
      <div>
        <p className="text-gray-400 text-sm">RSI</p>
        <p className="text-lg font-semibold">{analysis.rsi_value?.toFixed(1) || 'N/A'}</p>
      </div>
      <div>
        <p className="text-gray-400 text-sm">Signal</p>
        <p className={`text-lg font-semibold ${analysis.has_signal ? 'text-green-400' : 'text-gray-400'}`}>
          {analysis.has_signal ? analysis.signal_action : 'None'}
        </p>
      </div>
    </div>
  );
}
