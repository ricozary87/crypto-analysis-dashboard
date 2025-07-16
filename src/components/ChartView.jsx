import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  TimeScale,
  Tooltip,
} from 'chart.js';
import { Chart } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';
import { CandlestickController, CandlestickElement } from 'chartjs-chart-financial';

ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  Tooltip,
  CandlestickController,
  CandlestickElement
);

export default function ChartView({ candles }) {
  // Generate sample data if no candles provided
  const generateSampleData = () => {
    const data = [];
    const now = new Date();
    let price = 147.0;
    
    for (let i = 0; i < 50; i++) {
      const timestamp = new Date(now.getTime() - (50 - i) * 5 * 60 * 1000);
      const change = (Math.random() - 0.5) * 4;
      const open = price;
      const close = price + change;
      const high = Math.max(open, close) + Math.random() * 2;
      const low = Math.min(open, close) - Math.random() * 2;
      
      data.push({
        x: timestamp,
        o: open,
        h: high,
        l: low,
        c: close
      });
      
      price = close;
    }
    
    return data;
  };

  const chartData = {
    datasets: [{
      label: 'Candlestick',
      data: candles && candles.length > 0 ? candles : generateSampleData(),
      color: {
        up: '#10b981',
        down: '#ef4444',
        unchanged: '#999'
      },
    }],
  };

  return (
    <div className="bg-gray-800 p-4 rounded-xl mb-6" style={{ height: '400px' }}>
      <Chart type="candlestick" data={chartData} options={{
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { type: 'time', time: { tooltipFormat: 'MMM dd, HH:mm' }},
          y: { beginAtZero: false }
        }
      }} />
    </div>
  );
}
