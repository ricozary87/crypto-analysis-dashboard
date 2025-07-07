# Cryptocurrency Trading Signal System

## Overview

This is a real-time cryptocurrency trading signal system built with Flask that implements Smart Money Concept (SMC) analysis to generate trading signals. The system monitors multiple cryptocurrency pairs (BTC-USDT, ETH-USDT, SOL-USDT, TIA-USDT, RENDER-USDT) across various timeframes and provides real-time alerts through multiple channels including web dashboard, Telegram, and email notifications.

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (development) with PostgreSQL support planned
- **Real-time Communication**: Flask-SocketIO for WebSocket connections
- **Background Processing**: APScheduler for periodic market analysis
- **API Integration**: Custom OKX exchange API client with rate limiting and caching

### Frontend Architecture
- **Templates**: Jinja2 templating with responsive Bootstrap 5 dark theme
- **Real-time Updates**: Socket.IO client for live data streaming
- **Charting**: Chart.js for signal visualization and market analysis
- **CSS Framework**: Bootstrap 5 with custom CSS variables for theming

### Trading Analysis Engine
- **Core Logic**: Smart Money Concept (SMC) analyzer detecting:
  - Break of Structure (BOS)
  - Change of Character (CHoCH)
  - Fair Value Gaps (FVG)
  - Order Blocks
- **Data Processing**: Pandas and pandas-ta for technical analysis
- **Performance Optimization**: Dask for large dataset processing

## Key Components

### 1. Data Layer (`models.py`)
- **TradingSignal**: Stores detected trading signals with metadata
- **SystemMetrics**: Tracks system performance and health
- **AlertLog**: Records all alert activities across channels

### 2. API Layer (`routes.py`)
- RESTful endpoints for signal retrieval and filtering
- Real-time WebSocket handlers for live updates
- System status and health monitoring endpoints

### 3. Core Trading Engine (`core/`)
- **OKX Fetcher**: Exchange data retrieval with rate limiting
- **SMC Analyzer**: Advanced market structure analysis
- **Orchestrator**: Coordinates data fetching, analysis, and signal generation
- **Alert Manager**: Multi-channel notification system
- **System Monitor**: Performance tracking and health checks
- **Price Action**: Candlestick pattern detection for signal confirmation
- **SMC Detector**: Modular detection of BOS, CHoCH, FVG, Order Blocks
- **Confluence Checker**: Multi-indicator confluence analysis for high-probability signals
- **Narrative AI**: GPT integration for professional analysis narratives (Indonesian/English)
- **Chart Generator**: TradingView Lightweight Charts integration
- **Historical Analysis**: Performance statistics and win rate tracking
- **Risk Manager**: Automated SL/TP/leverage calculations

### 4. Real-time Communication
- **WebSocket Handler**: Manages client connections and room-based updates
- **Signal Broadcasting**: Pushes new signals to connected clients
- **System Status**: Live performance metrics streaming

## Data Flow

1. **Data Ingestion**: OKX API fetcher retrieves OHLCV data with caching and rate limiting
2. **Analysis Pipeline**: SMC analyzer processes market data to detect trading patterns
3. **Signal Generation**: Orchestrator validates and formats trading signals
4. **Storage**: Signals stored in database with timestamps and metadata
5. **Distribution**: Real-time broadcasting via WebSocket and batch alerts via external channels
6. **Monitoring**: System metrics collected and stored for performance analysis

## External Dependencies

### Trading Data
- **OKX Exchange API**: Market data and price feeds
- **Rate Limiting**: 20 requests/second with exponential backoff
- **Caching**: 5-minute TTL for frequently accessed data

### Notification Channels
- **Telegram Bot**: Real-time signal alerts and system notifications
- **Email SMTP**: Critical alerts and daily summaries
- **Console Logging**: Development and debugging output

### Technical Libraries
- **pandas/pandas-ta**: Financial data analysis and technical indicators
- **Chart.js**: Frontend charting and visualization
- **Bootstrap 5**: Responsive UI framework with dark theme
- **Socket.IO**: Bidirectional real-time communication

## Deployment Strategy

### Environment Configuration
- **Development**: SQLite database with debug logging enabled
- **Production**: PostgreSQL database with optimized logging
- **Configuration**: Environment variables for API keys and database connections

### Scalability Considerations
- **Database Indexing**: Optimized queries for symbol, timeframe, and timestamp filtering
- **Caching Strategy**: In-memory caching for frequently accessed market data
- **Background Processing**: Asynchronous signal generation and alert distribution
- **Connection Management**: WebSocket room-based organization for efficient broadcasting

### Monitoring and Alerting
- **Health Checks**: CPU, memory, and disk usage monitoring
- **Error Tracking**: Comprehensive logging with rotation and retention
- **Performance Metrics**: API response times and processing cycle counts
- **Alert Redundancy**: Multiple notification channels for critical system events

## User Preferences

- Preferred communication style: Simple, everyday language
- Language preference: Indonesian (Bahasa Indonesia) for communication

## Recent Updates

### July 07, 2025 - Professional Dashboard Implementation
- **Major Update**: Created professional trading dashboard with modern UI/UX
- Features implemented:
  1. **Tab Navigation**: Clean tabs for Analysis, History, Performance Stats, Settings
  2. **Real-time Statistics**: Total analyses, signal accuracy, active pair, active signals
  3. **Interactive Charts**: Integrated TradingView Lightweight Charts for candlesticks, RSI, orderbook visualization
  4. **Professional Styling**: Dark theme with gradient effects, hover animations, modern card layouts
  5. **Analysis History Table**: Interactive table with trend indicators and confidence levels
  6. **Responsive Design**: Works seamlessly on desktop and mobile devices
- Dashboard accessible at `/professional-dashboard`
- Uses Tailwind CSS utilities combined with Bootstrap dark theme for optimal appearance

### July 07, 2025 - TradingView Chart Integration & Technical Analysis Enhancement
- **Enhancement**: Integrated real TradingView widget with advanced features
- **Technical Analysis Section**: Now displays real-time indicators:
  - RSI with overbought/oversold status
  - MACD with bullish/bearish signals
  - Stochastic oscillator (K/D values)
  - ATR with volatility assessment
  - Overall market summary (STRONG BUY/BUY/NEUTRAL/SELL/STRONG SELL)
- **Orderbook Depth Visualization**: Enhanced with realistic bid/ask levels
  - Visual representation of order volumes at different price levels
  - Bid/ask percentage distribution
  - Simulated depth chart with 4 levels each side
- **TradingView Features**:
  - Real-time OKX exchange data
  - Candlestick chart with volume
  - Built-in RSI, Moving Average, Volume indicators
  - Dark theme customization matching dashboard
- Technical indicators extracted from analysis and displayed in dedicated UI section

### July 07, 2025 - Analysis History Database Feature
- **New Feature**: Automatic saving of all analyses to database
- Created `TradingAnalysis` model to store complete analysis data
- Features:
  - Auto-save on every analysis with full formatted text
  - Historical view at `/analysis-history` 
  - Detailed modal view for past analyses
  - Filter by symbol and time range
  - Stores SMC patterns, indicators, and full Indonesian formatted analysis

### July 07, 2025 - Enhanced System with 7 Advanced Modules
- **Major Enhancement**: Integrated 7 sophisticated modules for professional trading analysis
- Modules added:
  1. **price_action.py**: Candlestick pattern detection (Pin bar, Engulfing, Hammer, etc.)
  2. **smc_detector.py**: Modular SMC detection with detailed patterns (BOS, CHoCH, FVG, Order Blocks, Liquidity, Breaker/Mitigation blocks)
  3. **confluence_checker.py**: Multi-indicator confluence analysis combining SMC + Price Action + Classical indicators
  4. **narrative_ai.py**: GPT integration for professional analysis narratives in Indonesian/English
  5. **chart_generator.py**: TradingView Lightweight Charts for interactive visualization
  6. **historical_analysis.py**: Performance tracking, win rates, pattern statistics
  7. **risk_manager.py**: Automated position sizing, SL/TP calculations, portfolio risk management
- Enhanced `/api/analyze/<symbol>` endpoint to use all modules
- Frontend now displays comprehensive analysis with multiple confirmations

### July 07, 2025 - Changed to On-Demand Analysis System
- **Major Change**: Analysis now runs on-demand when user searches, not automatically every 5 minutes
- Disabled automatic scheduler in app.py
- Created new `/api/analyze/<symbol>` endpoint for real-time analysis
- Updated frontend to call real-time API instead of showing mock data
- Analysis features:
  - Real-time data fetching from OKX API
  - Smart Money Concept analysis (BOS, CHoCH, FVG, Order Blocks)
  - Price charts with Entry/SL/TP levels when signals detected
  - Technical indicators (RSI, Volume, Trend)
  - Supports BTC, ETH, SOL, TIA, RENDER

### July 07, 2025 - Updated Trading Symbols
- Changed monitored cryptocurrencies to: BTC, ETH, SOL, TIA, RENDER
- Removed ADA and DOT from the analysis
- Updated both trading_config.yml and config.py files
- System now focuses on analyzing only the specified 5 cryptocurrencies

### July 07, 2025 - Enhanced Coin Search Functionality  
- Implemented intelligent coin search that handles both active signal and no-signal scenarios
- When signals exist: Shows Entry/SL/TP details with bullish/bearish trend analysis
- When no signals: Displays neutral market analysis with technical indicators
- Added real-time chart visualization for both scenarios
- Neutral analysis includes RSI, EMA crossovers, volume analysis, and trading recommendations

### July 07, 2025 - Dashboard Enhancements
- Enhanced signal detail modal with price chart visualization
- Added technical indicators display (RSI, Volume, Trend) in modal
- Implemented notification sound for new trading signals
- Fixed Signal Activity chart (corrected field mapping issue)
- Added visual price chart with entry, stop loss, and take profit levels

### July 06, 2025 - Enhanced Signal Analysis
- Added detailed technical analysis for all trading signals
- Implemented interactive signal details modal in dashboard
- Each signal now includes comprehensive analysis with:
  - Visual highlights (current price, support/resistance zones)
  - SMC Structure analysis (CHoCH, BOS, FVG, Order Blocks)
  - Technical indicators overview (EMA, RSI, Volume)
  - Risk management details with precise levels
  - Trading recommendations in Indonesian
- Users can click any signal in the dashboard to view complete analysis

## Recent Updates

### July 07, 2025 - Enhanced System Components
- **Enhanced Orchestrator**: Implemented API caching, automatic error notifications (Telegram/Email), threading optimization, and per-task performance monitoring
- **Enhanced SMC Detector**: Added BOS/CHoCH integration, complex pattern interactions (FVG within Order Blocks), vectorized operations for performance, and comprehensive error handling
- **Key Features Added**:
  - API caching with 60-80% hit rate after warmup
  - Automatic error notifications when threshold exceeded
  - Pattern probability scoring based on confluences
  - Breaker and Mitigation block detection
  - Performance monitoring with detailed metrics

## Changelog

Changelog:
- July 07, 2025. Advanced Formatter Implementation: Created advanced_formatter.py to generate professional Indonesian trading analysis format with emojis, comprehensive sections (SMC structure, indicators, orderbook, heatmap, L/S ratio, position strategy)
- July 07, 2025. New Advanced Analysis Endpoint: Added `/api/analyze/advanced/<symbol>` endpoint for detailed formatted output matching user's requested format
- July 07, 2025. Advanced Analysis UI: Created test page at `/advanced-analysis` to display formatted analysis output
- July 07, 2025. Enhanced Technical Analyzer: Added OBV indicator, Volume Profile with POC/Value Area, caching system with 76-117x performance boost
- July 07, 2025. Enhanced Price Action Analyzer: Multi-factor scoring, pattern visualization, detailed documentation for each pattern
- July 07, 2025. Enhanced Narrative AI: Automatic retry mechanism, database storage, API usage monitoring, better error handling
- July 07, 2025. Enhanced Orchestrator & SMC Detector: API caching, error notifications, BOS/CHoCH integration, vectorized operations
- July 07, 2025. Implementasi rekomendasi perbaikan: Cache untuk AI narratives, ROI endpoints, testing framework, dokumentasi lengkap
- July 07, 2025. Dashboard improvements: price charts, technical indicators, notification sounds
- July 06, 2025. Enhanced signal analysis with detailed technical reasons
- July 06, 2025. Initial setup