# Quick Start Guide

This guide will help you get TrainingPlan up and running quickly.

## Prerequisites

Make sure you have the following installed:
- Docker Desktop (includes Docker Compose)
- Git

## Installation

### 1. Clone or Navigate to Project

```bash
cd /Users/boetthw3/Documents/99_Other/TrainingPlan
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# IMPORTANT: Edit .env and set at least these values:
# - DB_PASSWORD (change from default)
# - SECRET_KEY (generate with: openssl rand -hex 32)
```

### 3. Start All Services

```bash
# Start all containers in detached mode
docker-compose up -d

# View logs
docker-compose logs -f
```

This will start:
- PostgreSQL (with TimescaleDB) on port 5432
- Redis on port 6379
- Backend API on port 8000
- Frontend on port 3000
- Celery worker
- Celery beat scheduler

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc API Docs**: http://localhost:8000/redoc

### 5. Verify Installation

```bash
# Check all services are running
docker-compose ps

# Test backend health
curl http://localhost:8000/health

# Test frontend
open http://localhost:3000
```

## Local Development (Without Docker)

If you prefer to run services locally:

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# You'll need PostgreSQL and Redis running separately
# Then start the backend
uvicorn src.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Next Steps

1. **Initialize the database**
   ```bash
   # Backend will need Alembic migrations (coming in Phase 1, Week 2)
   cd backend
   alembic upgrade head
   ```

2. **Create your first user** (authentication endpoints coming soon)

3. **Explore the API** at http://localhost:8000/docs

4. **Configure integrations** (Garmin, Strava, TrainingPeaks)
   - Get API credentials from respective platforms
   - Add to .env file
   - Configure in settings UI (coming in Phase 3-4)

## Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml or .env
# For example, change "3000:3000" to "3001:3000"
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Reset Everything
```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Start fresh
docker-compose up -d
```

## Development Workflow

1. Make code changes in `backend/` or `frontend/`
2. Changes are automatically detected:
   - Backend: FastAPI auto-reload
   - Frontend: Vite HMR (Hot Module Replacement)
3. View changes at http://localhost:3000

## Stopping Services

```bash
# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (WARNING: deletes data)
docker-compose down -v
```

## What's Next?

- [ ] Complete Phase 1: User authentication, database models
- [ ] Phase 2: Training plan management
- [ ] Phase 3: Garmin integration
- [ ] Phase 4: Multi-platform integrations
- [ ] Phase 5: Analytics dashboard
- [ ] Phase 6: Mobile PWA
- [ ] Phase 7: Production deployment on QNAP

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the complete roadmap.
