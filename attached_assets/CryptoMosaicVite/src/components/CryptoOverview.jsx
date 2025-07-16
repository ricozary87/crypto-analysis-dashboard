export default function CryptoOverview({ data }) {
  if (!data) return <div className="bg-gray-800 p-4 rounded-xl text-gray-400">Menunggu data...</div>;

  return (
    <div className="bg-gray-800 p-4 rounded-xl mb-4 grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
      <div><p className="text-gray-400 text-sm">Harga</p><p className="text-xl text-green-400 font-bold">${data.price}</p></div>
      <div><p className="text-gray-400 text-sm">Volume 24H</p><p className="text-lg font-semibold">${data.volume}M</p></div>
      <div><p className="text-gray-400 text-sm">Funding Rate</p><p className="text-lg font-semibold">{data.fundingRate}%</p></div>
      <div><p className="text-gray-400 text-sm">Open Interest</p><p className="text-lg font-semibold">${data.openInterest}M</p></div>
    </div>
  );
}
