# Crypto Technical Dashboard

Professional cryptocurrency trading dashboard dengan React + Vite + Tailwind CSS + Chart.js

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

Access dashboard: `http://localhost:3000`

## 📦 Tech Stack

- **React 18.2.0** - UI Framework
- **Vite** - Build Tool & Dev Server
- **Tailwind CSS** - Styling Framework
- **Chart.js 4 + Financial Plugin** - Advanced Charting
- **React-ChartJS-2** - React Chart Integration
- **Lucide React** - Icons
- **Date-fns** - Date Utilities

## 🎯 Features

### Core Dashboard
- **Sidebar**: Trading pairs list dengan search, watchlist, dan market data
- **Topbar**: Pair selection, timeframe controls, chart type switcher
- **Main Chart**: Interactive candlestick/OHLC/line charts dengan professional styling
- **Overview Panel**: Real-time price, volume, statistics, orderbook summary
- **Technical Indicators**: 40+ indicators dengan toggle controls
- **Liquidity Heatmap**: Visual orderbook depth dengan color coding
- **Order Flow**: Volume profile analysis dan footprint cluster

### Chart Types
- **Candlestick** (default)
- **OHLC** bars
- **Line** charts
- **Renko** (ready for plugin)
- **Kagi** (ready for plugin)

### Technical Indicators
- **Moving Averages**: EMA-9, EMA-200, SMA-20, SMA-50
- **Oscillators**: RSI, MACD, Stochastic
- **Volatility**: Bollinger Bands, ATR
- **Volume**: OBV, Volume Profile
- **Custom**: VWAP, Fibonacci

### Real-time Features
- Auto-updating price data (5 second intervals)
- WebSocket ready untuk live streaming
- Responsive design untuk mobile/desktop
- Dark mode optimized

## 📁 Structure

```
src/
├── components/
│   ├── Sidebar.jsx           # Trading pairs & watchlist
│   ├── Topbar.jsx            # Controls & pair selection
│   ├── ChartView.jsx         # Main chart dengan indicators
│   ├── OverviewPanel.jsx     # Market statistics
│   ├── HeatmapLiquidity.jsx  # Orderbook heatmap
│   ├── OrderFlowPanel.jsx    # Volume analysis
│   └── IndicatorsPanel.jsx   # Technical indicators
├── services/
│   ├── api.js                # Backend API integration
│   ├── dummyData.js          # Chart data generator
│   ├── orderbook.js          # Orderbook utilities
│   └── indicators.js         # Technical calculations
├── App.jsx                   # Main app component
├── main.jsx                  # React entry point
└── index.css                 # Tailwind & custom styles
```

## 🔧 Configuration

### Chart Settings
- Default timeframe: 1H
- Default chart type: Candlestick
- Default indicators: EMA-9, EMA-200
- Data points: 200 candles

### Supported Pairs
- BTC/USDT, ETH/USDT, SOL/USDT
- BNB/USDT, ADA/USDT, DOT/USDT
- AVAX/USDT, MATIC/USDT

### Timeframes
- 5m, 15m, 1H, 4H, 1D, 1W

## 🎨 UI/UX

- **Dark Mode**: Professional trading theme
- **Responsive**: Mobile-first design
- **Accessibility**: Keyboard navigation support
- **Performance**: Optimized rendering
- **Animations**: Smooth transitions

## 📊 Data Integration

Currently menggunakan dummy data untuk testing. Ready untuk integrasi dengan:
- Flask backend API
- OKX exchange data
- Real-time WebSocket streams
- AI analysis endpoints

## 🔮 Future Enhancements

### Ready for Integration
- **SMC Analysis Panel**: Order blocks, fair value gaps
- **AI Panel**: GPT signals, sentiment analysis
- **Drawing Tools**: 40+ technical drawing tools
- **Alerts System**: Price & indicator alerts

### Modular Architecture
Dashboard didesain modular untuk easy integration:
- Components dapat di-extend
- Services dapat di-customize
- API endpoints siap untuk backend
- WebSocket manager untuk real-time

## 🛠️ Development

### Add New Indicator
1. Add calculation di `services/indicators.js`
2. Update `components/IndicatorsPanel.jsx`
3. Implement display di `components/ChartView.jsx`

### Add New Chart Type
1. Register controller di `ChartView.jsx`
2. Add option di `components/Topbar.jsx`
3. Update chart data generator

### Customize Styling
- Edit `tailwind.config.js` untuk colors
- Modify `src/index.css` untuk components
- Update theme variables

## 📱 Mobile Support

- Touch-friendly controls
- Responsive grid layout
- Optimized chart rendering
- Swipe gestures ready

## 🔒 Security

- No API keys di frontend
- Secure WebSocket connections
- Input validation
- Error handling

## 📈 Performance

- Lazy loading components
- Chart data optimization
- Memory management
- Efficient re-renders

---

**Ready to use!** Dashboard siap untuk development dan production deployment.