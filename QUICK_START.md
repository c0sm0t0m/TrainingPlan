# 🚀 Quick Start Guide - Kinesis on Local Machine or NAS

**Updated**: April 12, 2026  
**Goal**: Get Kinesis running in 5 minutes

---

## ⚡ TL;DR - Start It NOW

### Pick One Option:

**Option A: Smart Startup Script (Easiest)**
```bash
cd /Users/boetthw3/Documents/01_Projects/TrainingPlan
./start-all.sh
```
Opens Terminal windows automatically. Wait 10 seconds, then open:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs

---

**Option B: Manual Startup (Most Control)**

Terminal 1 (Backend):
```bash
cd /Users/boetthw3/Documents/01_Projects/TrainingPlan
./start-backend.sh
# Wait for: "Uvicorn running on http://0.0.0.0:8000"
```

Terminal 2 (Frontend):
```bash
cd /Users/boetthw3/Documents/01_Projects/TrainingPlan
./start-frontend.sh
# Wait for: "Local: http://localhost:5173"
```

Then open browser: http://localhost:5173

---

**Option C: Docker Stack (Full Production Setup)**
```bash
cd /Users/boetthw3/Documents/01_Projects/TrainingPlan
docker-compose up -d
```

Check status:
```bash
docker-compose ps
```

Access at: http://localhost:5173

---

## ✅ Verify It's Working

### Backend Health Check
```bash
curl http://localhost:8000/docs
# Should show Swagger API documentation

curl http://localhost:8000/
# Should return: {"message": "TrainingPlan API"}
```

### Frontend Health Check
```bash
curl http://localhost:5173
# Should return HTML content
```

### View Logs
```bash
# If started with start-all.sh, check Terminal windows

# If using docker-compose:
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## 🧹 Stop Services

Option A (if using start-all.sh or manual):
```bash
./stop-all.sh
```

Option B (if using Docker):
```bash
docker-compose down
```

---

## 🚨 Troubleshooting

### ❌ "Port 8000 already in use"
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Then restart
./start-backend.sh
```

### ❌ "Python 3.13 not found"
```bash
# Check installed Python versions
python3 --version
python3.13 --version
which python3.13

# If only 3.11 is available, edit start-backend.sh:
# Change: venv313
# To:     venv

# Then: ./start-backend.sh
```

### ❌ "npm not found"
```bash
# Install Node.js
brew install node  # on macOS
# Or download from https://nodejs.org/

# Then: ./start-frontend.sh
```

### ❌ Frontend loads but shows blank page
```bash
# Check browser console for errors (F12 in Chrome)
# Likely issue: Backend not running
# Fix: Make sure backend started successfully

# Also check .env.local in frontend/
cat frontend/.env.local
# Should have: VITE_API_URL=http://localhost:8000/api/v1
```

### ❌ Database connection errors
```bash
# If using Docker and PostgreSQL:
docker-compose logs postgres
# Check for initialization errors

# If using local setup, backend uses SQLite (no DB setup needed)
```

---

## 📊 What Gets Started

### Using `./start-all.sh` or manual startup:
- **Backend**: FastAPI server (port 8000)
- **Frontend**: React dev server (port 5173)
- **Database**: SQLite (local file: `backend/trainingplan.db`)
- **Cache**: None (background tasks won't work)

✅ **Perfect for**: Development, testing features, manual workflows

---

### Using `docker-compose up -d`:
- **PostgreSQL**: Database (port 5432)
- **Redis**: Cache & task queue (port 6379)
- **Backend**: FastAPI server (port 8000)
- **Frontend**: React server (port 5173)
- **Celery Worker**: Background tasks
- **Celery Beat**: Scheduled tasks

✅ **Perfect for**: Production simulation, testing async tasks, NAS deployment

---

## 🎯 Next Steps After Starting

1. **Create an account**
   - Go to http://localhost:5173
   - Sign up with email/password (or use demo account if available)

2. **Test backend API**
   - Open http://localhost:8000/docs
   - Try API endpoints (GET, POST, etc.)

3. **Explore features**
   - Dashboard
   - Training Plans
   - Calendar
   - Garmin Sync (if configured)
   - Analytics

4. **Check logs**
   - Backend: Terminal window or `docker-compose logs -f backend`
   - Frontend: Browser console (F12)

---

## 📝 Environment Notes

### Current Configuration
```
Backend: ./backend/.env (PostgreSQL + Redis for Docker stack)
Frontend: ./frontend/.env.local (VITE_API_URL set)
Database: PostgreSQL (Docker) or SQLite (local dev)
Cache: Redis (Docker) or none (local dev)
```

### For Local SQLite Development:
```bash
# Backend will use SQLite automatically
# No additional setup needed
# Database file: backend/trainingplan.db
```

### For Docker PostgreSQL:
```bash
# Database automatically initializes
# URL: postgres://trainingplan_user:password@postgres:5432/trainingplan
# Check logs: docker-compose logs postgres
```

---

## 🌐 NAS Deployment (After Testing Locally)

Once confirmed working on your local machine:

1. **Read**: [QNAP_DEPLOYMENT_GUIDE.md](QNAP_DEPLOYMENT_GUIDE.md)
2. **Update .env** with your NAS IP
3. **Transfer** deployment package to NAS via rsync
4. **SSH into NAS** and run: `docker-compose up -d`
5. **Access** at: `http://YOUR_NAS_IP:5173`

---

## 📱 Access from Other Devices

### Same Network (LAN)
Backend is configured to listen on `0.0.0.0:8000`:
```
From another computer: http://YOUR_MACHINE_IP:8000/docs
From another computer: http://YOUR_MACHINE_IP:5173
```

### Find Your Machine IP
```bash
# macOS/Linux
ifconfig | grep "inet "

# Or use hostname
hostname -I
```

---

## 💾 Backup & Data

### SQLite (Local Development)
```bash
# Database file location:
backend/trainingplan.db

# Backup:
cp backend/trainingplan.db backend/trainingplan.db.backup
```

### PostgreSQL (Docker)
```bash
# Backup database:
docker-compose exec postgres pg_dump -U trainingplan_user trainingplan > backup.sql

# Restore:
cat backup.sql | docker-compose exec -T postgres psql -U trainingplan_user trainingplan
```

---

## 🆘 Need Help?

Check these files in order:
1. [WORKSPACE_REVIEW_APR2026.md](WORKSPACE_REVIEW_APR2026.md) - Current state & architecture
2. [LOCAL_DEV_SETUP.md](LOCAL_DEV_SETUP.md) - Alternative setup instructions
3. [QNAP_DEPLOYMENT_GUIDE.md](QNAP_DEPLOYMENT_GUIDE.md) - NAS deployment
4. [README.md](README.md) - Project overview
5. Backend logs: Check Terminal output or `docker-compose logs backend`
6. Frontend logs: Browser console (F12)

---

## ✨ Success Signs

When everything is working:
- ✅ Terminal shows: `Uvicorn running on http://0.0.0.0:8000`
- ✅ Terminal shows: `Local: http://localhost:5173`
- ✅ Browser shows React app (no errors in console)
- ✅ API docs load: http://localhost:8000/docs
- ✅ Clicking buttons makes API requests (no CORS errors)

---

**Ready? Run: `./start-all.sh`** 🚀
