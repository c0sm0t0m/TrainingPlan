# 🏠 NAS Deployment Checklist - Kinesis

**Status**: ✅ Ready for QNAP NAS  
**Last Updated**: April 12, 2026  

---

## 📋 Pre-Deployment Checklist

### Local Machine (Before Transfer)

- [ ] **Backend verified**
  ```bash
  source backend/venv313/bin/activate
  python3 -c "import fastapi; print('FastAPI ready')"
  # Expected: FastAPI ready
  ```

- [ ] **Frontend verified**
  ```bash
  cd frontend && npm list react 2>&1 | head -3
  # Expected: react@18.x.x
  ```

- [ ] **Docker installed and working**
  ```bash
  docker --version
  docker-compose --version
  # Expected: Both show versions
  ```

- [ ] **Test local startup works**
  ```bash
  ./start-all.sh
  # Or: docker-compose up -d
  # Access: http://localhost:5173
  ```

- [ ] **Verified on local machine**: At least one startup method works
  - [ ] Option A: `./start-all.sh` ✓
  - [ ] Option B: Manual startup (./start-backend.sh + ./start-frontend.sh) ✓
  - [ ] Option C: `docker-compose up -d` ✓

- [ ] **Environment variables confirmed**
  ```bash
  cat backend/.env | grep DATABASE_URL
  cat backend/.env | grep REDIS_URL
  cat backend/.env | grep SECRET_KEY
  # All should have values
  ```

- [ ] **scripts/init-db.sql exists**
  ```bash
  ls -lh scripts/init-db.sql
  # Expected: File exists (for Docker PostgreSQL init)
  ```

---

## 🔧 NAS Preparation (Customize for Your NAS)

### Step 1: Update Configuration Files

**Edit .env** - Update with your NAS IP (example: 192.168.1.100):

```bash
# OLD (localhost for development):
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# NEW (adjust for your NAS IP):
CORS_ORIGINS=http://192.168.1.100:3000,http://192.168.1.100:5173
```

**Edit frontend/.env.local** if it exists:

```bash
# OLD:
VITE_API_URL=http://localhost:8000/api/v1

# NEW:
VITE_API_URL=http://192.168.1.100:8000/api/v1
```

**Docker Compose Customization** (optional - if changing ports):

```yaml
# docker-compose.yml - Modify port mappings if needed:
ports:
  - "8000:8000"    # Backend (change left number to expose different port)
  - "5173:5173"    # Frontend (change left number to expose different port)
  - "5432:5432"    # PostgreSQL (optional - restrict to localhost if on NAS)
```

### Step 2: Prepare Deployment Package

```bash
# Create deployment directory
mkdir -p ~/kinesis-deploy
cd ~/kinesis-deploy

# Copy all necessary files
cp -r /Users/boetthw3/Documents/01_Projects/TrainingPlan/backend .
cp -r /Users/boetthw3/Documents/01_Projects/TrainingPlan/frontend .
cp /Users/boetthw3/Documents/01_Projects/TrainingPlan/docker-compose.yml .
cp /Users/boetthw3/Documents/01_Projects/TrainingPlan/.env .
cp -r /Users/boetthw3/Documents/01_Projects/TrainingPlan/scripts .

# Remove unnecessary files to reduce transfer size
rm -rf backend/venv backend/venv313 backend/.pytest_cache
rm -rf frontend/node_modules frontend/dist
rm -f backend/*.db backend/*.log frontend/*.log

# List what we have
ls -lh ~/kinesis-deploy/
```

### Step 3: Transfer to QNAP NAS

Choose one method:

**Method A: rsync (recommended - shows progress)**
```bash
# Replace 192.168.1.100 with your QNAP IP
# Replace admin with your QNAP username

rsync -avz --progress ~/kinesis-deploy/ admin@192.168.1.100:/share/Container/kinesis/
```

**Method B: SSH + tar (if rsync not available)**
```bash
cd ~/kinesis-deploy
tar czf kinesis-deploy.tar.gz .
scp kinesis-deploy.tar.gz admin@192.168.1.100:/share/Container/

# On QNAP:
ssh admin@192.168.1.100
cd /share/Container
tar xzf kinesis-deploy.tar.gz -C kinesis
rm kinesis-deploy.tar.gz
```

**Method C: SFTP/SCP (GUI based)**
1. Use Cyberduck, FileZilla, or similar
2. Connect to: `admin@192.168.1.100`
3. Upload to: `/share/Container/kinesis/`

---

## 🚀 Deploy on QNAP NAS

### Step 1: SSH into QNAP

```bash
ssh admin@192.168.1.100
```

If prompt for password, enter your QNAP admin password.

### Step 2: Navigate and Verify

```bash
cd /share/Container/kinesis
ls -la
# Should see: backend/, frontend/, docker-compose.yml, .env, scripts/
```

### Step 3: Pre-Flight Checks

```bash
# 1. Verify Docker is installed
docker --version
docker-compose --version

# 2. Verify ports are available
netstat -tuln | grep -E "5432|6379|8000|5173"
# Should show: empty (ports available) or if ports in use, they should be LISTEN

# 3. Verify disk space
df -h /share/
# Check: Avail > 20GB (for database + images)
```

### Step 4: Pull & Build Docker Images

```bash
cd /share/Container/kinesis

# Pull base images (first time, may take 5-10 minutes)
docker-compose pull

# Build custom backend/frontend images
docker-compose build

# Expected output:
# - Building postgres... done
# - Building redis... done  
# - Building backend... done
# - Building frontend... done
# - Building celery_worker... done
# - Building celery_beat... done
```

### Step 5: Initialize Database

```bash
# PostgreSQL will initialize automatically on first start
# The init-db.sql script will run automatically

# Start services
docker-compose up -d

# Watch logs for initialization (should complete in 10-30 seconds)
docker-compose logs -f postgres
# Wait for: "database system is ready to accept connections"
```

### Step 6: Verify All Services Running

```bash
docker-compose ps

# Expected output (all showing "Up"):
# NAME                     STATUS
# trainingplan_postgres    Up (healthy)
# trainingplan_redis       Up (healthy)
# trainingplan_backend     Up
# trainingplan_frontend    Up
# trainingplan_celery_worker Up
# trainingplan_celery_beat Up
```

### Step 7: Check Logs for Issues

```bash
# Backend logs
docker-compose logs backend | tail -20

# Frontend logs
docker-compose logs frontend | tail -20

# Any errors? Examples:
# - "Connection refused": Database not ready, wait 30 seconds
# - "Port already in use": Modify docker-compose.yml port mappings
# - "Pull image failed": Internet connection issue
```

### Step 8: Test Access

From your local machine or another device on LAN:

```bash
# Test backend API
curl http://192.168.1.100:8000/

# Test frontend
curl http://192.168.1.100:5173/

# Or open in browser:
# Frontend: http://192.168.1.100:5173
# API Docs: http://192.168.1.100:8000/docs
```

---

## ✅ Post-Deployment Verification

### On QNAP (via SSH)

```bash
# All services running?
docker-compose ps

# Database initialized?
docker-compose exec postgres psql -U trainingplan_user -d trainingplan \
  -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname='public';"
# Expected: Should return number of tables (e.g., 5)

# Backend responding?
docker-compose exec backend curl localhost:8000/
# Expected: {"message": "TrainingPlan API"}

# Redis working?
docker-compose exec redis redis-cli ping
# Expected: PONG
```

### From Browser/Local Machine

```bash
# Frontend loads?
Open: http://YOUR_NAS_IP:5173
Expected: React app loads (no errors in browser console)

# Backend API accessible?
Open: http://YOUR_NAS_IP:8000/docs
Expected: Swagger UI with API endpoints

# Try creating an account?
Click "Sign Up" and create test user
Expected: User creation succeeds, can login
```

---

## 🧹 Maintenance Commands

### View Live Logs

```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Just frontend  
docker-compose logs -f frontend

# Last 50 lines
docker-compose logs --tail=50
```

### Stop Services (Maintenance)

```bash
# Stop (keeps data)
docker-compose stop

# Resume
docker-compose start

# Full restart
docker-compose restart
```

### Backup Database

```bash
# Backup
docker-compose exec postgres pg_dump -U trainingplan_user trainingplan \
  > trainingplan_backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
cat trainingplan_backup_20260412.sql | \
  docker-compose exec -T postgres psql -U trainingplan_user trainingplan
```

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild images
docker-compose build

# Restart
docker-compose down
docker-compose up -d
```

---

## 🚨 Troubleshooting on NAS

### ❌ Services won't start

**Problem**: `docker-compose up -d` fails

**Solutions**:
```bash
# 1. Check Docker running
docker ps
# If error, restart Docker service on QNAP via Web UI

# 2. Check logs
docker-compose logs | tail -50

# 3. If database issue, reinitialize
docker-compose down -v  # WARNING: Deletes database
docker-compose up -d    # Start fresh
```

### ❌ Can't connect to frontend

**Problem**: Browser can't reach http://NAS_IP:5173

**Solutions**:
```bash
# 1. Check port is exposed
docker-compose ps | grep frontend
# Should show port 5173 mapped

# 2. Check frontend is actually running
docker-compose exec frontend ps aux | grep node
# Should see Vite process

# 3. Check firewall
# QNAP may have firewall blocking port
# Via Web UI: Control Panel > Network > Firewall > Exceptions
#   - Add allow rule for ports 5173 and 8000

# 4. Test from NAS itself
ssh admin@NAS_IP
curl http://localhost:5173
# If this works, it's a network/firewall issue
```

### ❌ Database won't initialize

**Problem**: PostgreSQL logs show error

**Solutions**:
```bash
# 1. Check if init script exists
docker-compose exec postgres ls -l /docker-entrypoint-initdb.d/
# Should show: init.sql

# 2. Check permissions
docker-compose down -v
docker-compose up -d
docker-compose logs postgres | head -50

# 3. Manually initialize if needed
docker-compose exec postgres psql -U trainingplan_user -d trainingplan \
  -f /docker-entrypoint-initdb.d/init.sql
```

### ❌ Backend service crashing

**Problem**: `docker-compose ps` shows backend exited

**Solutions**:
```bash
# 1. Check logs
docker-compose logs backend | tail -50

# 2. Common issues:
# - DATABASE_URL misconfigured in .env
# - Python dependencies missing (rebuild)
# - Port 8000 already in use

# 3. Rebuild and restart
docker-compose build backend
docker-compose up -d backend

# 4. Check Python import errors
docker-compose exec backend python3 -c "import src.main"
```

---

## 📊 Performance Tuning (Optional)

### For Large Training Datasets

**Update docker-compose.yml**:

```yaml
postgres:
  environment:
    POSTGRES_MAX_CONNECTIONS: 200
    SHARED_BUFFERS: 256MB
    WORK_MEM: 64MB

redis:
  command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

### Resource Limits

```yaml
backend:
  deploy:
    resources:
      limits:
        memory: 2G
      reservations:
        memory: 1G

frontend:
  deploy:
    resources:
      limits:
        memory: 512M
      reservations:
        memory: 256M
```

---

## 📝 Monitoring & Alerts

### Health Check Commands

```bash
# Run daily/weekly to verify system health

# 1. All services running?
docker-compose ps | grep -c "Up"
# Expected: 6 (should match number of services)

# 2. Database accessible?
docker-compose exec postgres pg_isready -U trainingplan_user
# Expected: accepting connections

# 3. Disk usage
docker system df
# Warning: If usage > 80%

# 4. Container resource usage
docker stats --no-stream

# 5. Backup database daily
docker-compose exec postgres pg_dump -U trainingplan_user trainingplan | \
  gzip > /share/backups/trainingplan_$(date +%Y%m%d).sql.gz
```

---

## ✅ Success Checklist

- [ ] Deployment package prepared and transferred to NAS
- [ ] .env configured with NAS IP
- [ ] `docker-compose pull` completed successfully
- [ ] `docker-compose build` completed successfully
- [ ] All 6 services showing "Up" in `docker-compose ps`
- [ ] PostgreSQL database initialized (tables exist)
- [ ] Frontend loads at http://NAS_IP:5173
- [ ] Backend API accessible at http://NAS_IP:8000/docs
- [ ] Can create user account (sign up works)
- [ ] Can login (authentication works)
- [ ] Background tasks running (Celery worker active)
- [ ] Backup strategy implemented

---

## 🎓 Reference

- **QNAP NAS Container Station**: Usually at `https://192.168.1.100:8080`
- **NAS SSH**: `ssh admin@192.168.1.100`
- **Key Paths on NAS**:
  - App: `/share/Container/kinesis/`
  - Uploads: `/share/Container/kinesis/backend/uploads/`
  - Backups: `/share/backups/` (create this directory)
  - Logs: View via `docker-compose logs` command

---

**Ready to deploy? Start with "NAS Preparation" section above!** 🚀
