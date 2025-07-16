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
  const chartData = {
    datasets: [{
      label: 'Candlestick',
      data: candles,
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
        scales: {
          x: { type: 'time', time: { tooltipFormat: 'MMM dd, HH:mm' }},
          y: { beginAtZero: false }
        }
      }} />
    </div>
  );
}
