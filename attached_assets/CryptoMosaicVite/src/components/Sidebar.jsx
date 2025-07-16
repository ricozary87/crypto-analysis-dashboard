export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-800 p-4 hidden md:block">
      <h2 className="text-xl font-bold mb-4">Pairs</h2>
      <ul className="space-y-2">
        <li><button className="hover:text-green-400">SOL/USDT</button></li>
        <li><button className="hover:text-green-400">BTC/USDT</button></li>
        <li><button className="hover:text-green-400">ETH/USDT</button></li>
      </ul>
    </aside>
  );
}
