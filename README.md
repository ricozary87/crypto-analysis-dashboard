# Cryptocurrency Trading Signal System

## Overview

Advanced cryptocurrency trading signal detection system leveraging Smart Money Concept (SMC) analysis with AI-powered insights. The system monitors 5 cryptocurrencies (BTC, ETH, SOL, TIA, RENDER) with on-demand analysis.

## Features

### Core Trading Engine
- **Smart Money Concept Analysis**: BOS, CHoCH, FVG, Order Blocks detection
- **Price Action Patterns**: Pin bar, Engulfing, Hammer detection
- **Multi-Timeframe Analysis**: 1m, 5m, 15m, 1H, 4H
- **AI-Powered Narratives**: Professional trading explanations in Indonesian/English
- **Risk Management**: Automated SL/TP calculations with position sizing
- **Real-time Data**: OKX Exchange API integration with rate limiting

### 7 Advanced Modules
1. **Price Action** (`core/price_action.py`) - Candlestick pattern detection
2. **SMC Detector** (`core/smc_detector.py`) - Modular SMC pattern detection
3. **Confluence Checker** (`core/confluence_checker.py`) - Multi-indicator analysis
4. **Narrative AI** (`core/narrative_ai.py`) - GPT-powered analysis narratives
5. **Chart Generator** (`core/chart_generator.py`) - Interactive TradingView charts
6. **Historical Analysis** (`core/historical_analysis.py`) - Performance tracking
7. **Risk Manager** (`core/risk_manager.py`) - Portfolio risk management

### Web Interface
- Real-time dashboard with WebSocket updates
- Interactive charts with technical indicators
- Signal notifications with sound alerts
- System health monitoring
- Dark theme Bootstrap 5 UI

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL database
- OKX Exchange API credentials
- OpenAI API key (for AI narratives)

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# OKX Exchange API
OKX_API_KEY=your_api_key
OKX_SECRET_KEY=your_secret_key
OKX_PASSPHRASE=your_passphrase

# OpenAI API (for AI narratives)
OPENAI_API_KEY=your_openai_key

# Optional: Notification channels
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_password
```

### Setup
```bash
# Install dependencies (handled automatically by Replit)
# Dependencies are managed via packager_tool in pyproject.toml

# Start the application
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Usage

### Dashboard
Navigate to `/dashboard` to access the main trading interface:
- View real-time signals
- Search specific coins (BTC, ETH, SOL, TIA, RENDER)
- Monitor system performance
- View detailed analysis with charts

### API Endpoints

#### Analyze Coin
```
GET /api/analyze/<symbol>
```
Returns comprehensive analysis including:
- SMC patterns
- Price action signals
- Technical indicators
- AI-generated narrative
- Risk management levels

#### Get Signals
```
GET /api/signals
```
Returns recent trading signals with filtering options:
- `?symbol=BTC-USDT` - Filter by symbol
- `?action=BUY` - Filter by action (BUY/SELL)
- `?limit=10` - Limit results

#### System Status
```
GET /api/metrics
```
Returns system health metrics:
- CPU/Memory usage
- API response times
- Active connections

## Architecture

### Backend
- **Framework**: Flask with SQLAlchemy ORM
- **Real-time**: Flask-SocketIO for WebSocket
- **Scheduler**: APScheduler for background tasks
- **Database**: PostgreSQL with optimized indexing

### Analysis Pipeline
1. Data fetching from OKX API (with caching)
2. SMC pattern detection
3. Price action analysis
4. Confluence checking
5. Risk calculation
6. AI narrative generation
7. Signal broadcasting

### Frontend
- **UI Framework**: Bootstrap 5 (Dark theme)
- **Charts**: Chart.js + TradingView Lightweight Charts
- **Real-time**: Socket.IO client
- **Notifications**: Audio alerts for new signals

## Development

### Testing
```bash
# Run OKX API connection test
python test_okx_api.py

# Run signal generation test
python test_signal_gen.py

# Trigger immediate analysis
python trigger_analysis.py
```

### Project Structure
```
├── core/               # Trading engine modules
│   ├── analyzer.py     # SMC analysis
│   ├── price_action.py # Candlestick patterns
│   ├── smc_detector.py # SMC pattern detection
│   ├── confluence_checker.py # Multi-indicator
│   ├── narrative_ai.py # AI narratives
│   ├── chart_generator.py # Chart generation
│   ├── historical_analysis.py # Performance tracking
│   ├── risk_manager.py # Risk calculations
│   ├── signal_generator.py # Signal orchestration
│   ├── okx_fetcher.py  # Exchange data
│   ├── alert_manager.py # Multi-channel alerts
│   └── system_monitor.py # Health monitoring
├── templates/          # HTML templates
├── static/            # CSS, JS, images
├── models.py          # Database models
├── routes.py          # API endpoints
├── app.py             # Flask app setup
├── config.py          # Configuration
└── main.py            # Entry point
```

## Performance Optimization
- Database indexing on symbol, timeframe, timestamp
- In-memory caching for market data (5-min TTL)
- Connection pooling for database
- Rate limiting for API calls (20 req/sec)
- WebSocket rooms for efficient broadcasting

## Security
- Environment variables for sensitive data
- CSRF protection enabled
- SQL injection prevention via ORM
- Rate limiting on API endpoints
- Secure WebSocket connections

## Monitoring
- System metrics tracked every cycle
- Error logging with rotation
- Alert logs stored in database
- Real-time health status via WebSocket

## License
Proprietary - All rights reserved

## Support
For issues or questions, contact the development team.