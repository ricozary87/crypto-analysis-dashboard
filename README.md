# 🚀 Cryptocurrency Trading AI Platform

Platform analisis trading cryptocurrency yang komprehensif dengan AI-powered insights, Smart Money Concept (SMC) analysis, dan real-time market data processing.

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (production) atau SQLite (development)

### 🚀 Deployment Options

#### Docker (Recommended)
```bash
cp .env.example .env
# Edit .env dengan API keys Anda
docker-compose up -d
```

#### Manual Production
```bash
./deploy.sh production
```

#### Systemd Service (Linux VPS)
```bash
# Install as system service
sudo ./install-systemd-service.sh

# Configure environment
sudo nano /opt/crypto-trading-ai/.env

# Start and enable service
sudo systemctl start crypto-trading-ai
sudo systemctl enable crypto-trading-ai
```

#### Local Development
```bash
./start-local.sh
```

## 🔧 Configuration

Copy `.env.example` to `.env` dan isi:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/trading_db

# API Keys
OPENAI_API_KEY=your_openai_key
OKX_API_KEY=your_okx_key
OKX_SECRET_KEY=your_okx_secret
OKX_PASSPHRASE=your_okx_passphrase

# Security
SESSION_SECRET=your_random_secret_key
```

## 🏗️ Features

### 📊 Advanced SMC Analysis
- Change of Character (CHoCH) Detection
- Break of Structure (BOS) Analysis
- Fair Value Gap (FVG) Identification
- Order Block Detection
- Breaker Block Analysis
- Liquidity Analysis (IRL/ERL)
- Killzone Timing

### 🤖 AI-Powered Insights
- OpenAI GPT-4o Integration
- Professional Market Narratives
- Confidence Scoring
- Multi-timeframe Analysis

### 📈 Technical Analysis
- 40+ Technical Indicators
- Price Action Pattern Detection
- Volume Analysis with CVD
- Real-time Signal Generation

### 🔄 Real-time Features
- Live Market Data Streaming
- WebSocket Integration
- Multi-symbol Support
- Automated Alerts

## 📁 Project Structure

```
├── core/                    # Core analysis engines
├── src/                     # React frontend
├── templates/               # Flask templates
├── static/                  # Static assets
├── tests/                   # Test suites
├── docs/                    # Documentation
├── archive/                 # Old files
├── reports/                 # Analysis reports
├── logs/                    # Application logs
├── snapshots/               # Generated reports
└── development/             # Development scripts
```

## 🛠️ Development

### Frontend Development
```bash
cd src/
npm run dev
```

### Backend Development
```bash
python main.py
```

### Running Tests
```bash
python test_deployment.py
```

## 📦 Dependencies

### Backend
- Flask + SocketIO
- SQLAlchemy + PostgreSQL
- Pandas + NumPy
- Technical Analysis Library
- OpenAI API

### Frontend
- React 19
- Chart.js Financial
- TailwindCSS
- Vite Build System

## 🔍 Monitoring

- Prometheus metrics
- Real-time system monitoring
- Performance tracking
- Error logging with Sentry

## 📄 Documentation

- [Deployment Guide](docs/DEPLOYMENT_SUMMARY.md)
- [Architecture Overview](replit.md)
- [API Documentation](docs/)

## 🤝 Support

Untuk bantuan deployment atau konfigurasi, silakan lihat dokumentasi di folder `docs/`.

---

**Status: ✅ Production Ready - VPS Deployment Tested**