# Kinesis 🏃‍♂️🚴‍♂️🏊‍♂️

A self-hosted triathlon and running training management platform. Transform your potential into kinetic achievement - track your training, analyze your progress, and connect with your favorite fitness platforms, all running on your QNAP NAS.

**Docs:** start with this README, `QUICK_START.md`, or `START_HERE.md`. Historical feature/fix notes live in `docs/archive/`. Active backlog: `RANKED_IMPROVEMENT_BACKLOG.md`.

## Features

- 📅 **Training Plan Management** - Create personalized training plans for triathlon and running
- 🔄 **Multi-Platform Sync** - Connect with Garmin, TrainingPeaks, and Strava
- 📊 **Advanced Analytics** - Training load (TSS, CTL, ATL, TSB), fitness trends, zone analysis
- 📱 **Mobile Ready** - Progressive Web App for smartphone access
- 🏠 **Self-Hosted** - Your data stays on your QNAP NAS
- 🔒 **Privacy First** - Full control over your training data

## Quick Start

### Option 1: One-Command Startup (Recommended)
```bash
./start-all.sh
```
This opens two terminal windows - one for backend, one for frontend.

### Option 2: Manual Startup
**Backend** (Terminal 1):
```bash
./start-backend.sh
```

**Frontend** (Terminal 2):
```bash
./start-frontend.sh
```

### Stop Services
```bash
./stop-all.sh
```

### Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## Development Setup

### Prerequisites

- Docker and Docker Compose installed
- QNAP NAS with Container Station (for production)
- Git
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Development Setup

1. **Clone the repository**
   ```bash
   cd /Users/boetthw3/Documents/01_Projects/TrainingPlan
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development (without Docker)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
trainingplan/
├── backend/              # FastAPI backend
├── frontend/             # React TypeScript frontend
├── docker-compose.yml    # Docker services configuration
├── .env.example          # Environment variables template
└── docs/                 # Additional documentation
```

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Database**: PostgreSQL 15 with TimescaleDB
- **Cache/Queue**: Redis, Celery
- **Frontend**: React 18, TypeScript, Material-UI, Vite
- **Deployment**: Docker Compose, Traefik

## Documentation

- [Project Plan](PROJECT_PLAN.md) - Detailed implementation roadmap
- [Tech Stack](TECH_STACK.md) - Technology decisions and architecture
- [Local Dev Setup](LOCAL_DEV_SETUP.md) - Quick start without Docker
- [AI Agent Instructions](.github/copilot-instructions.md) - GitHub Copilot context
- [Garmin Integration](backend/GARMIN_WORKOUT_SYNC_IMPLEMENTATION.md) - Garmin API implementation details

## 🧪 Test Data

Pre-configured test data for the AI Training Plan Generator:

```bash
# View test data options
cd test-data && cat INDEX.md

# Quick demo
./test-data/demo.sh

# Visual editor
open test-data/test-data-editor.html

# API testing
python3 test-data/test_ai_plan_config.py
```

See [test-data/INDEX.md](test-data/INDEX.md) for complete documentation.

**Default test case:**
- Event: Berlin Marathon 2026 (Sep 27)
- Goal: 3:30:00 (sub-3:30)
- Start: Next Monday (auto-calculated)
- Training: 5 days/week
- Constraints: Tuesday track @ 6pm, Thursday swim @ 8pm

## Development Status

🚧 **Phase 1: Foundation** (In Progress)
- [x] Project structure initialized
- [ ] Docker Compose setup
- [ ] Backend core with authentication
- [ ] Frontend shell with routing
- [ ] Database models

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for complete roadmap.

## Integration Support

- ✅ Garmin Connect (OAuth 2.0)
- ✅ TrainingPeaks API v2
- ✅ Strava API v3
- ✅ Manual upload (TCX, FIT, GPX files)

## Contributing

This is a personal project, but contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Support

For questions or issues, please open a GitHub issue.

---

**Current Version**: 0.1.0-alpha (Development)
**Last Updated**: December 31, 2025
