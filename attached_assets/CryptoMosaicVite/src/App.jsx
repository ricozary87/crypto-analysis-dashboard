import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import CryptoOverview from './components/CryptoOverview';
import ChartView from './components/ChartView';

function App() {
  const handleAnalyze = (pair, tf) => {
    console.log('Trigger analisa:', pair, tf);
    // nanti disambungkan ke backend
  };

  return (
    <div className="flex min-h-screen bg-gray-900 text-white">
      <Sidebar />
      <main className="flex-1 p-6 overflow-y-auto">
        <Topbar onAnalyze={handleAnalyze} />

        <CryptoOverview
          data={{
            price: 147.20,
            volume: 356,
            fundingRate: 0.03,
            openInterest: 192,
          }}
        />

        <ChartView
          candles={[
            { x: '2025-07-15T10:00:00Z', o: 147, h: 149, l: 145.8, c: 148.5 },
            { x: '2025-07-15T10:05:00Z', o: 148.5, h: 149.3, l: 147.5, c: 148.0 },
            { x: '2025-07-15T10:10:00Z', o: 148.0, h: 148.6, l: 146.9, c: 147.1 },
          ]}
        />
      </main>
    </div>
  );
}

export default App;
