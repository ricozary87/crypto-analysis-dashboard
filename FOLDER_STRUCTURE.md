# 📁 Folder Structure

## Current Clean Organization

```
📦 Cryptocurrency Trading AI Platform
├── 📂 core/                    # Core analysis engines
│   ├── 🤖 ai_engine.py            # AI analysis
│   ├── 📊 professional_smc_analyzer.py  # Smart Money Concepts
│   ├── 📈 analyzer.py             # Technical analysis
│   ├── 🔄 realtime_streamer.py    # Live data streaming
│   └── ... (other core modules)
│
├── 📂 src/                     # React Frontend
│   ├── 📂 components/             # React components
│   ├── 📂 services/               # API services
│   └── 📱 App.jsx                 # Main app
│
├── 📂 templates/               # Flask Templates
│   ├── 🏠 index.html             # Main page
│   └── 📊 react_dashboard.html   # Dashboard
│
├── 📂 static/                  # Static Assets
│   └── 📂 js/                     # JavaScript files
│
├── 📂 tests/                   # Test Suites
│   ├── 🧪 test_smc_detector.py   # SMC tests
│   ├── 🧪 test_analyzer.py       # Analysis tests
│   └── ... (comprehensive tests)
│
├── 📂 docs/                    # Documentation
│   ├── 📋 DEPLOYMENT_SUMMARY.md  # Deployment guide
│   ├── 📊 MONITORING_SETUP.md    # Monitoring setup
│   └── ... (implementation reports)
│
├── 📂 archive/                 # Archived Files
│   ├── 📂 old_tests/             # Old test files
│   ├── 📂 old_configs/           # Old configurations
│   └── 📂 temp_files/            # Temporary files
│
├── 📂 development/             # Development Scripts
│   ├── ⚡ run_all_tests.sh       # Test runner
│   └── 🚀 start_react.sh         # React dev server
│
├── 📂 reports/                 # Analysis Reports
│   └── 📈 *.json                 # Generated reports
│
├── 📂 snapshots/               # Generated Snapshots
│   └── 📂 reports/               # PDF reports
│
├── 📂 logs/                    # Application Logs
│   ├── 📝 access.log             # Access logs
│   └── ❌ error.log              # Error logs
│
├── 📂 sql/                     # Database Scripts
│   └── 🗄️ init.sql               # Database initialization
│
├── 📂 instance/                # Database Files
│   └── 💾 trading_local.db       # SQLite database
│
├── 📂 attached_assets/         # User Assets
│   └── 🖼️ images, archives       # User uploaded files
│
└── 📂 tmp/                     # Temporary Storage
    └── 🗑️ temporary files        # Runtime temp files
```

## Core Application Files

### 🚀 Production Ready
- `wsgi.py` - WSGI entry point
- `gunicorn.conf.py` - Production server config
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-container setup
- `deploy.sh` - Production deployment script
- `start-local.sh` - Local development script

### 🔧 Configuration
- `.env.example` - Environment template
- `requirements-prod.txt` - Production dependencies
- `requirements.txt` - Development dependencies
- `trading_config.yml` - Trading parameters
- `nginx.conf` - Reverse proxy config

### 📱 Application Core
- `app.py` - Flask application factory
- `main.py` - Application entry point
- `routes.py` - API endpoints
- `models.py` - Database models
- `config.py` - Configuration management

## Files Cleaned Up

### ✅ Moved to Archive
- Old test files (comprehensive_*.py, quick_*.py)
- Old configuration files
- Temporary analysis files
- Log files
- Development artifacts

### ✅ Organized into Folders
- Documentation → `docs/`
- Test files → `tests/`
- Development scripts → `development/`
- Analysis reports → `reports/`
- Log files → `logs/`
- Temporary files → `tmp/`

### 🗑️ Removed
- Python cache files (__pycache__)
- Duplicate files
- Unnecessary artifacts
- Coverage reports

## Quick Navigation

### For Development
```bash
cd src/           # Frontend development
cd core/          # Backend core modules
cd tests/         # Run tests
cd development/   # Development tools
```

### For Documentation
```bash
cd docs/          # All documentation
ls *.md           # Quick overview
```

### For Deployment
```bash
./deploy.sh       # Production deployment
./start-local.sh  # Local development
docker-compose up # Container deployment
```

**Total Files Reduced**: ~100+ files → 29 core files in root
**Organization Status**: ✅ Complete - Ready for VPS deployment