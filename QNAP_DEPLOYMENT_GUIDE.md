# Kinesis - QNAP NAS Deployment Guide

**Date**: January 16, 2026  
**Status**: Production Deployment Ready

## Overview

This guide walks you through deploying Kinesis to your QNAP NAS using Container Station. The application will run as Docker containers with persistent data storage.

---

## Release (recommended daily path)

From your Mac, in the project root:

```bash
# Optional: tag a release
git tag v0.x.y

# Sync code to NAS, rebuild containers, run migrations
./deploy-qnap.sh
```

What this does:
- Writes a `VERSION` file (git describe + UTC timestamp)
- rsyncs the project to the NAS (does **not** overwrite NAS `.env`, local SQLite DBs, or media)
- Rebuilds with `docker-compose.yml` + `docker-compose.qnap.yml` (static nginx frontend via `frontend/Dockerfile.prod`, not Vite dev)
- Runs `alembic upgrade head` on the NAS backend

Useful flags: `--dry-run`, `--skip-migrations`, `--debug`, `--path /share/Container/kinesis-deploy`

Defaults live in [`scripts/nas-config.sh`](scripts/nas-config.sh) (`NAS_IP`, `NAS_USER`, `NAS_PATH`).

**Deploy never syncs the database.** Use the DB sync commands below when you want to move training data.

### Postgres password mismatch

`POSTGRES_PASSWORD` is applied only when the Postgres volume is first created. If NAS `.env` `DB_PASSWORD` later differs, migrations fail with `password authentication failed`.

`./deploy-qnap.sh` now aligns the role password from `.env` before Alembic. To fix manually on the NAS:

```bash
cd /share/Container/kinesis-deploy
# Use the DB_PASSWORD value from your .env:
docker exec -i trainingplan_postgres \
  psql -U trainingplan_user -d trainingplan \
  -c "ALTER USER trainingplan_user WITH PASSWORD 'YOUR_DB_PASSWORD_FROM_ENV';"
```

---

## Bidirectional DB sync (Mac ↔ NAS)

Both sides must use **Postgres** (NAS already does via Compose). One-time Mac setup if you were on SQLite:

```bash
# Start local Postgres, migrate schema, import backend/trainingplan.db
./scripts/sqlite-to-postgres.sh

# Point local API at Postgres (backend/.env or project .env):
#   DATABASE_URL=postgresql+asyncpg://trainingplan_user:CHANGE_ME@localhost:5432/trainingplan
#   DB_HOST=localhost
```

Then sync explicitly (automatic target backup under `backups/db/`):

```bash
./scripts/db-sync.sh push                      # Mac → NAS (normal; KEEP NAS users/settings)
./scripts/db-sync.sh push --with-uploads
./scripts/db-sync.sh push --full               # also overwrite NAS users (type push-full)
./scripts/db-sync.sh pull --allow-pull         # NAS → Mac (blocked unless --allow-pull)
./scripts/db-sync.sh push --yes                # skip typed confirmation (push only)
```

**Default safeguard:** destination `users` table is restored after sync, so passwords, Garmin/ICU tokens, and zone settings are not overwritten. Use `--full` only when you intentionally want to clone accounts/settings too (confirm by typing `pull-full` / `push-full`).

**Pull is blocked by default** (`NAS → Mac`) so a empty/broken NAS DB cannot wipe a working Mac copy. When you really need it: `./scripts/db-sync.sh pull --allow-pull` and type `overwrite-mac-from-nas`.

---

## Prerequisites

### QNAP Requirements
- ✅ QNAP NAS with Container Station installed
- ✅ Minimum 4GB RAM available
- ✅ 10GB+ free storage space
- ✅ QTS 4.5+ or QuTS hero

### Local Requirements
- ✅ SSH access to QNAP NAS
- ✅ Git installed on local machine (to prepare deployment package)

---

## Deployment Steps (manual / first-time detail)

Prefer `./deploy-qnap.sh` above. The steps below remain as a deeper reference for first-time NAS `.env` setup.

### Step 1: Prepare Deployment Package

On your **local machine**, create a deployment package:

```bash
# Navigate to project directory
cd /Users/boetthw3/Documents/01_Projects/TrainingPlan

# Create a clean deployment directory
mkdir -p ~/kinesis-deploy
cd ~/kinesis-deploy

# Copy necessary files
cp -r /Users/boetthw3/Documents/01_Projects/TrainingPlan/backend .
cp -r /Users/boetthw3/Documents/01_Projects/TrainingPlan/frontend .
cp /Users/boetthw3/Documents/01_Projects/TrainingPlan/docker-compose.yml .
cp /Users/boetthw3/Documents/01_Projects/TrainingPlan/.env.example .env

# Optional: Create scripts directory if init-db.sql exists
mkdir -p scripts
cp /Users/boetthw3/Documents/01_Projects/TrainingPlan/scripts/init-db.sql scripts/ 2>/dev/null || true
```

### Step 2: Configure Environment Variables

Edit the `.env` file with your production settings:

```bash
# Edit .env file
nano .env  # or use your preferred editor
```

**Required Changes**:

```bash
# ============================================================================
# Application Settings
# ============================================================================
ENVIRONMENT=production
DEBUG=false

# ============================================================================
# Database Configuration
# ============================================================================
DB_PASSWORD=<GENERATE_STRONG_PASSWORD_HERE>  # Use: openssl rand -base64 32

# ============================================================================
# Authentication & Security
# ============================================================================
SECRET_KEY=<GENERATE_SECRET_KEY_HERE>  # Use: openssl rand -hex 32

# ============================================================================
# CORS Configuration
# ============================================================================
# Replace with your QNAP's IP or hostname
CORS_ORIGINS=http://192.168.1.100:3000,https://kinesis.your-domain.com

# ============================================================================
# Frontend Configuration
# ============================================================================
# Replace with your QNAP's IP or hostname
VITE_API_URL=http://192.168.1.100:8000/api/v1
```

**Generate secure credentials**:
```bash
# Generate database password
openssl rand -base64 32

# Generate secret key
openssl rand -hex 32
```

### Step 3: Transfer Files to QNAP

Transfer the deployment package to your QNAP NAS:

```bash
# Create app directory on QNAP (replace with your QNAP IP)
ssh admin@192.168.1.100 "mkdir -p /share/Container/kinesis"

# Transfer files via rsync (recommended)
rsync -avz --progress ~/kinesis-deploy/ admin@192.168.1.100:/share/Container/kinesis/

# OR transfer as tar archive (alternative)
cd ~/kinesis-deploy
tar czf kinesis-deploy.tar.gz .
scp kinesis-deploy.tar.gz admin@192.168.1.100:/share/Container/
ssh admin@192.168.1.100 "cd /share/Container && tar xzf kinesis-deploy.tar.gz -C kinesis && rm kinesis-deploy.tar.gz"
```

### Step 4: Deploy on QNAP

SSH into your QNAP NAS:

```bash
ssh admin@192.168.1.100
```

Navigate to the app directory and start services:

```bash
cd /share/Container/kinesis

# Pull base images (first time only)
docker-compose pull

# Build custom images
docker-compose build

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

**Expected output**:
```
NAME                          STATUS
trainingplan_postgres         Up (healthy)
trainingplan_redis            Up (healthy)
trainingplan_backend          Up
trainingplan_frontend         Up
trainingplan_celery_worker    Up
trainingplan_celery_beat      Up
```

### Step 5: Initialize Database

Run database migrations:

```bash
# Enter backend container
docker exec -it trainingplan_backend bash

# Run migrations
alembic upgrade head

# Exit container
exit
```

### Step 6: Verify Deployment

Test the application:

1. **Backend API**: http://192.168.1.100:8000/docs
2. **Frontend UI**: http://192.168.1.100:3000
3. **Health Check**: http://192.168.1.100:8000/health

Check logs if needed:
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## Post-Deployment Configuration

### 1. Setup Port Forwarding (Optional - External Access)

If you want to access Kinesis from outside your home network:

**QNAP Control Panel**:
1. Go to: **myQNAPcloud** > **Auto Router Configuration**
2. Add port forwarding rules:
   - External Port 8080 → Internal Port 3000 (Frontend)
   - External Port 8081 → Internal Port 8000 (Backend)

**Or configure on your router**:
- Forward ports 3000 and 8000 to your QNAP's IP

### 2. Setup SSL/HTTPS (Recommended for Production)

**Option A: Using Traefik (Included)**

Enable Traefik reverse proxy:

```bash
# Edit docker-compose.yml - add labels to frontend service
docker-compose --profile production up -d traefik
```

Update `.env`:
```bash
ACME_EMAIL=your-email@example.com
```

**Option B: Using QNAP's Built-in Reverse Proxy**

1. QNAP Control Panel > **Application** > **Web Server**
2. Enable **Reverse Proxy**
3. Create rules:
   - External: `https://kinesis.yourdomain.com` → Internal: `http://localhost:3000`
   - External: `https://api.kinesis.yourdomain.com` → Internal: `http://localhost:8000`

### 3. Configure Automated Backups

Create backup script on QNAP:

```bash
# Create backup script
cat > /share/Container/kinesis/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/share/Backup/kinesis"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
docker exec trainingplan_postgres pg_dump -U trainingplan_user trainingplan > "$BACKUP_DIR/db_$TIMESTAMP.sql"

# Backup uploaded files
tar czf "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" -C /share/Container/kinesis uploads_data/

# Keep only last 30 days
find "$BACKUP_DIR" -name "db_*.sql" -mtime +30 -delete
find "$BACKUP_DIR" -name "uploads_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
EOF

chmod +x /share/Container/kinesis/backup.sh
```

Add to crontab (daily at 2 AM):
```bash
crontab -e

# Add this line:
0 2 * * * /share/Container/kinesis/backup.sh >> /share/Container/kinesis/backup.log 2>&1
```

---

## Container Management

### Start/Stop Services

```bash
cd /share/Container/kinesis

# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend

# View logs
docker-compose logs -f backend
```

### Update Application

When you have new code to deploy:

1. **On local machine**: Create new deployment package
2. **Transfer to QNAP**: Use rsync or scp
3. **On QNAP**:
   ```bash
   cd /share/Container/kinesis
   
   # Stop services
   docker-compose down
   
   # Rebuild images
   docker-compose build
   
   # Start services
   docker-compose up -d
   
   # Run migrations (if schema changed)
   docker exec -it trainingplan_backend alembic upgrade head
   ```

### Monitor Resources

Check Docker resource usage:
```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up unused data
docker system prune -a --volumes
```

---

## Troubleshooting

### Services Won't Start

**Check logs**:
```bash
docker-compose logs backend
docker-compose logs postgres
```

**Common issues**:
1. **Port conflicts**: Check if ports 3000, 8000, 5432 are available
   ```bash
   netstat -tulpn | grep -E '3000|8000|5432'
   ```

2. **Database connection**: Verify DATABASE_URL in `.env`
3. **Permission issues**: Check file ownership
   ```bash
   chown -R 1000:1000 /share/Container/kinesis
   ```

### Database Migration Failed

Reset database (⚠️ deletes all data):
```bash
docker-compose down -v
docker-compose up -d postgres redis
docker exec -it trainingplan_backend alembic upgrade head
docker-compose up -d
```

### Frontend Can't Connect to Backend

1. Check CORS settings in `.env`:
   ```bash
   CORS_ORIGINS=http://192.168.1.100:3000
   ```

2. Verify frontend API URL:
   ```bash
   VITE_API_URL=http://192.168.1.100:8000/api/v1
   ```

3. Restart services:
   ```bash
   docker-compose restart backend frontend
   ```

### Out of Memory

Reduce container memory limits in `docker-compose.yml`:
```yaml
services:
  backend:
    mem_limit: 1g
    memswap_limit: 1g
```

---

## Security Checklist

- [x] Changed default database password
- [x] Generated secure SECRET_KEY
- [ ] Configured firewall rules
- [ ] Setup SSL/HTTPS
- [ ] Restricted CORS origins
- [ ] Setup automated backups
- [ ] Configured log rotation
- [ ] Disabled DEBUG mode in production

---

## Access URLs

After successful deployment:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://192.168.1.100:3000 | Main application UI |
| API Docs | http://192.168.1.100:8000/docs | Interactive API documentation |
| API Health | http://192.168.1.100:8000/health | Service health check |
| Traefik Dashboard | http://192.168.1.100:8080 | (Optional) Proxy dashboard |

---

## Maintenance Tasks

### Weekly
- Check logs for errors: `docker-compose logs --tail=100`
- Monitor disk usage: `docker system df`

### Monthly
- Update base images: `docker-compose pull && docker-compose up -d`
- Review backup files
- Check certificate expiry (if using Let's Encrypt)

### As Needed
- Update application code
- Scale services if needed
- Review and rotate logs

---

## Support & Documentation

- **Project Documentation**: [README.md](./README.md)
- **Tech Stack**: [TECH_STACK.md](./TECH_STACK.md)
- **API Documentation**: http://your-qnap-ip:8000/docs
- **Garmin Integration**: [backend/GARMIN_WORKOUT_SYNC_IMPLEMENTATION.md](./backend/GARMIN_WORKOUT_SYNC_IMPLEMENTATION.md)

---

## Next Steps

After deployment:

1. **Create First User**: Register at http://192.168.1.100:3000/register
2. **Connect Garmin**: Go to Settings > Integrations > Connect Garmin
3. **Create Training Plan**: Start planning your workouts!
4. **Setup Mobile Access**: Add bookmark to phone home screen (PWA)

**🎉 Your Kinesis training platform is now live on QNAP!**
