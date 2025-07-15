# OKX Market Data Dashboard

## Overview

This is a Flask-based web application that provides real-time cryptocurrency market data visualization using the OKX exchange API. The application features an interactive dashboard with candlestick charts, orderbook data, and technical indicators for various cryptocurrency trading pairs. The application now includes PostgreSQL database integration for data persistence and user preferences.

## User Preferences

Preferred communication style: Simple, everyday language (Indonesian).

## Recent Changes

### July 14, 2025
- ✅ **Plotly.js Integration Completed**: Successfully replaced Chart.js with Plotly.js for candlestick charts
- ✅ **TradingView-style Charts**: Implemented candlestick with volume bars overlay (green/red color coding)
- ✅ **Optimized Date Format**: Fixed X-axis date format to "%m-%d %H:%M" for better readability
- ✅ **Professional Layout**: Grid subplot layout with price (70%) and volume (25%) sections
- ✅ **Interactive Features**: Zoom, pan, hover tooltips with responsive design
- ✅ **All Menu Features Preserved**: Dashboard tabs (Order Book, Technical Indicators, Volume Analysis) remain functional
- ✅ **Volume Chart Fixed**: Volume Analysis tab now displays Chart.js volume chart with proper bullish/bearish color coding
- ✅ **Market Depth Chart Added**: New depth chart in Order Book tab mimicking Binance/TradingView Pro style
- ✅ **Enhanced Orderbook**: Upgraded to 50-depth orderbook data (from 20) with cumulative volume visualization
- ✅ **Real-time Refresh**: Added refresh button for manual depth chart updates
- ✅ **Snapshot Analysis Enhanced**: Fixed JSON serialization issues and improved error handling
- ✅ **UI/UX Improvements**: Replaced emoji icons with clear text labels in 7-layer analysis boxes
- ✅ **Professional Styling**: Added tooltips, hover effects, and timestamp indicators for better user experience
- ✅ **CSS Enhancements**: Comprehensive styling for layer cards, confidence scores, and narrative sections
- ✅ **OpenAI Integration**: Added AI-powered narrative generation with professional trading analysis
- ✅ **AI Prompt Builder**: Created comprehensive prompt system for technical analysis data conversion
- ✅ **Fallback System**: Implemented fallback narratives when AI is unavailable
- ✅ **Bug Fix**: Fixed UnboundLocalError in volume analysis for stable snapshot generation
- ✅ **Quick Mode Feature**: Added quick mode button for faster analysis (~15 seconds vs ~30 seconds)
- ✅ **Improved Timeout Handling**: Added proper timeout handling and error recovery options
- ✅ **Performance Optimization**: Dual-mode system with quick analysis for impatient users
- ✅ **Enhanced Error Messages**: Better error handling with retry options and mode switching
- ✅ **AI Engine Integration**: Created dedicated ai_engine.py for high-quality narrative generation
- ✅ **Optimized System Prompts**: Enhanced GPT-4o prompts for professional trading analysis
- ✅ **Code Architecture**: Improved separation of concerns with dedicated AI Engine class
- ✅ **Fallback Narratives**: Enhanced fallback system for when AI is unavailable
- ✅ **Critical Timestamp Fix**: Resolved major int/str timestamp comparison issues across all modules
- ✅ **Database Integration**: Fixed Flask application context issues for proper database operations
- ✅ **Component Isolation**: All individual components (OKX, SMC, Database) now work correctly in isolation
- ✅ **AI Narrative Generation**: Successfully working AI-powered analysis with GPT-4o
- ✅ **Comprehensive Testing**: Created test_okx_simple.py for systematic component validation
- ✅ **Error Handling**: Improved error handling throughout the system with proper JSON responses
- ✅ **Technical Indicators**: Enhanced timestamp normalization in TechnicalIndicators class
- ✅ **Signal Engine**: Fixed timestamp handling in signal generation and analysis
- ✅ **Indicator Calculator**: Added comprehensive timestamp normalization for all indicator calculations
- ✅ **Core Functionality**: Basic candlestick data fetching, caching, and display working correctly
- ✅ **AI Narrative Fix**: Resolved API response mapping issue - AI narratives now properly returned
- ✅ **JSON Response Format**: Fixed frontend JSON parsing errors with proper API response structure
- ✅ **Multi-Symbol Support**: AI snapshot generation working for SOL-USDT, BTC-USDT, ETH-USDT
- ✅ **Quick Mode Optimization**: Fast AI analysis (~15-20 seconds) with meaningful trading insights
- ✅ **Professional Analysis**: AI generates comprehensive trading analysis in Indonesian with bias, entry points, stop loss, and take profit levels
- ✅ **Tab Integration Fix**: Fixed snapshot tab to use AI-powered analysis instead of broken regular snapshot
- ✅ **Error Handling**: Enhanced error handling for tab switching and API timeouts
- ✅ **Layer Analysis**: Added proper layer analysis visualization in snapshot tab
- ✅ **Confidence Display**: Improved confidence score display with AI analysis results
- ✅ **Modal Rendering Fixed**: Resolved blank modal issue with proper inline styling and content display
- ✅ **Professional UI**: Enhanced AI snapshot modal with gradient backgrounds and modern styling
- ✅ **Error Handling**: Improved error messages with specific handling for timeouts and server errors
- ✅ **Quick Mode Priority**: Added quick mode fallback for server busy conditions
- ✅ **AI Snapshot Complete**: Successfully working AI snapshot modal with professional UI and comprehensive analysis
- ✅ **Production Ready**: Modal rendering, error handling, and styling all fully functional
- ✅ **Comprehensive Mode**: Long-form AI analysis (2600+ characters) working correctly
- ✅ **Quick Mode**: Fast AI analysis (15-20 seconds) as fallback option
- ✅ **Database Archive System**: Implemented simpan_snapshot_ai function for PostgreSQL Neon database
- ✅ **Confidence Column**: Added confidence column to ai_snapshot_archive table
- ✅ **Archive API Endpoints**: Complete CRUD operations for AI snapshot archival
- ✅ **JavaScript Error Fix**: Fixed null DOM element errors in Trading Signals tab
- ✅ **Error Handling Enhancement**: Added null checks and warning logs for better stability
- ✅ **DOM Element Validation**: Enhanced error resilience for 7-layer confluence analysis

## System Architecture

### Frontend Architecture
- **Framework**: Bootstrap 5 with dark theme for responsive UI
- **Charts**: Chart.js for data visualization with date-fns adapter for time handling
- **JavaScript**: Vanilla JavaScript organized into modular classes (OKXDashboard, ChartManager)
- **Styling**: Custom CSS with Bootstrap overrides for market data specific styling

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Structure**: Modular design with separate service classes
- **API Design**: RESTful endpoints for market data retrieval
- **Error Handling**: Comprehensive logging and error responses

## Key Components

### Core Services
1. **OKXService** (`okx_service.py`)
   - Handles all OKX API interactions
   - Provides candlestick data and orderbook data
   - Includes robust error handling and request management

2. **TechnicalIndicators** (`technical_indicators.py`)
   - Calculates technical analysis indicators (OBV, EMA)
   - Processes market data for analytical insights
   - Uses numpy/pandas for mathematical operations

3. **Flask Application** (`app.py`)
   - Main application entry point
   - API endpoints for frontend data requests
   - Template rendering for dashboard

4. **AIPromptBuilder** (`ai_prompt_builder.py`)
   - Converts 7-layer technical analysis into structured OpenAI prompts
   - Professional trading analysis prompt generation
   - Handles data extraction from SMC, Volume, Orderbook, RSI/EMA, Fibonacci, and OI/Funding
   - Quick analysis mode for faster response

5. **AIEngine** (`ai_engine.py`)
   - Dedicated AI Engine for high-quality narrative generation
   - Optimized system prompts for professional trading analysis
   - Dual-mode operation (quick/comprehensive) with timeout handling
   - Enhanced fallback narratives when AI is unavailable
   - Singleton pattern for efficient resource management

6. **SnapshotGenerator** (`snapshot_generator.py`)
   - Orchestrates comprehensive 7-layer confluence analysis
   - Integrates AIEngine for professional narrative generation
   - Generates trading plans and risk assessments
   - Handles JSON serialization and data processing

7. **SnapshotArchiver** (`snapshot_archiver.py`)
   - Provides simpan_snapshot_ai function for PostgreSQL Neon database
   - Handles AI snapshot archival with confidence scoring
   - Complete CRUD operations for snapshot management
   - Session-based access control and data validation

### Frontend Components
1. **Dashboard Interface** (`templates/index.html`)
   - Trading pair selection
   - Timeframe controls
   - Data visualization containers

2. **Chart Management** (`static/js/charts.js`)
   - Chart.js integration
   - Candlestick chart rendering
   - Real-time data updates

3. **Application Logic** (`static/js/app.js`)
   - Event handling
   - API communication
   - User interaction management

## Data Flow

1. **User Interaction**: User selects trading pair and timeframe through web interface
2. **API Request**: Frontend JavaScript makes AJAX calls to Flask endpoints
3. **Data Retrieval**: Flask routes call OKXService to fetch data from OKX API
4. **Processing**: Technical indicators are calculated if needed
5. **Response**: JSON data is returned to frontend
6. **Visualization**: Chart.js renders the data in interactive charts

## External Dependencies

### Backend Dependencies
- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Database for data persistence (Neon)
- **Requests**: HTTP client for OKX API calls
- **NumPy/Pandas**: Mathematical operations for technical indicators
- **OpenAI**: AI narrative generation with GPT-4o
- **Psycopg2**: PostgreSQL adapter for Python

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme
- **Chart.js**: Data visualization library
- **Font Awesome**: Icons
- **date-fns**: Date handling for charts

### External APIs
- **OKX REST API**: Public market data endpoints
  - Candlestick data endpoint
  - Orderbook data endpoint
  - No authentication required for public data
- **OpenAI API**: AI-powered narrative generation
  - GPT-4o model for professional trading analysis
  - Converts technical analysis into human-readable narratives
  - Requires OPENAI_API_KEY environment variable
  - Quick mode (~15s) and comprehensive mode (~30s) analysis

## Deployment Strategy

### Development Setup
- Environment variables for configuration (SESSION_SECRET)
- Debug logging enabled
- Local development server via Flask

### Production Considerations
- Secret key management through environment variables
- Error logging configuration
- Session management for user preferences
- Static file serving optimization

### Architecture Decisions

1. **Modular Service Design**: Separated OKX API logic and technical indicators into dedicated classes for maintainability and testability

2. **RESTful API Structure**: Clean API endpoints that mirror the data structure needed by the frontend

3. **Client-Side Rendering**: JavaScript handles chart rendering and updates for responsive user experience

4. **Error Handling Strategy**: Comprehensive error handling at both API and service levels with proper HTTP status codes

5. **Real-time Updates**: Frontend polling mechanism for data refresh without page reloads

6. **Responsive Design**: Bootstrap-based layout that works across desktop and mobile devices

The application follows a clean separation of concerns with the backend handling data retrieval and processing while the frontend focuses on user interaction and visualization.

## Database Schema

### AI Snapshot Archive Table
- **Table**: `ai_snapshot_archive`
- **Purpose**: Store AI-generated trading analysis snapshots
- **Key Columns**:
  - `id`: Primary key
  - `symbol`: Trading pair (e.g., BTC-USDT)
  - `timeframe`: Time period (e.g., 1h, 5m)
  - `ai_narrative`: AI-generated analysis content
  - `confidence`: Confidence score (0-1)
  - `session_id`: User session identifier
  - `created_at`: Timestamp
  - `confluence_summary`: JSON analysis summary
  - `layer_analysis`: JSON 7-layer analysis data
  - `snapshot_data`: JSON full snapshot data

### Key Functions
- `simpan_snapshot_ai(symbol, timeframe, content, confidence)`: Save AI snapshot
- `get_snapshot_archive(session_id, symbol, timeframe, limit)`: Retrieve snapshots
- `get_snapshot_by_id(snapshot_id)`: Get specific snapshot
- `delete_snapshot(snapshot_id, session_id)`: Delete snapshot
- `get_snapshot_statistics(session_id)`: Get user statistics