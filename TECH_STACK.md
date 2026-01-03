# TrainingPlan - Technology Stack Documentation

## Overview
This document details the complete technology stack for the TrainingPlan application, including rationale for each choice and alternatives considered.

## Architecture Pattern
**Microservices-lite with API Gateway**
- Frontend SPA communicates with backend via REST API
- Background workers handle async tasks (activity sync, calculations)
- Reverse proxy handles routing and SSL termination

## Backend Technologies

### Runtime & Framework
**Primary: Python 3.11+ with FastAPI**

#### FastAPI Benefits
- **Performance**: Async/await support, comparable to Node.js
- **Type Safety**: Pydantic models with automatic validation
- **Auto Documentation**: OpenAPI/Swagger UI out of the box
- **Developer Experience**: Fast development with less boilerplate
- **Ecosystem**: Rich libraries for ML, data science, file parsing

#### Key Libraries
```python
# Core Framework
fastapi = "^0.104.0"
uvicorn[standard] = "^0.24.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"

# Database
sqlalchemy = "^2.0.23"
alembic = "^1.13.0"
asyncpg = "^0.29.0"  # Async PostgreSQL driver
psycopg2-binary = "^2.9.9"  # Sync PostgreSQL driver

# Authentication & Security
python-jose[cryptography] = "^3.3.0"  # JWT handling
passlib[bcrypt] = "^1.7.4"  # Password hashing
python-multipart = "^0.0.6"  # Form data parsing

# Integrations & HTTP
httpx = "^0.25.2"  # Async HTTP client
oauthlib = "^3.2.2"  # OAuth 2.0
requests-oauthlib = "^1.3.1"

# File Parsing
fitparse = "^1.2.0"  # FIT file parser
gpxpy = "^1.6.1"  # GPX file parser
lxml = "^4.9.3"  # TCX file parser (XML)

# Task Queue
celery = "^5.3.4"
redis = "^5.0.1"

# Utilities
python-dateutil = "^2.8.2"
pytz = "^2023.3"
```

#### Alternative: Node.js + NestJS
**Pros**: Great TypeScript DX, fast, unified language with frontend
**Cons**: Weaker ML/data science libraries, FIT parsing options limited
**Verdict**: Python chosen for superior file parsing and analytics capabilities

### Database

**Primary: PostgreSQL 15.x with TimescaleDB Extension**

#### PostgreSQL Benefits
- **Mature & Reliable**: Battle-tested RDBMS
- **ACID Compliance**: Transaction safety for critical data
- **JSON Support**: JSONB for flexible activity metadata
- **Full-Text Search**: Built-in search capabilities
- **Extensions**: TimescaleDB for time-series optimization

#### TimescaleDB Benefits
- **Time-Series Optimization**: Automatic partitioning by time
- **Compression**: Reduce storage for old activity data
- **Continuous Aggregates**: Pre-computed rollups for analytics
- **Hypertables**: Transparent time-series table management

#### Schema Design Principles
- Separate tables for activities (time-series) and plans (relational)
- Use hypertables for `activities` and `activity_samples` (HR, power streams)
- Indexes on: user_id, activity_date, sport_type
- Partial indexes for common queries (e.g., completed workouts)

#### Alternative: MongoDB
**Pros**: Flexible schema, good for nested workout structures
**Cons**: No time-series optimization, weaker analytics, less mature
**Verdict**: PostgreSQL + TimescaleDB offers best of both worlds

### Caching & Session Store

**Redis 7.x**

#### Use Cases
- **Session Storage**: JWT refresh tokens
- **API Response Cache**: Analytics queries, user preferences
- **Rate Limiting**: Track API call counts per user/IP
- **Task Queue Backend**: Celery broker and result backend
- **Real-Time Data**: Pub/sub for live updates (future)

#### Configuration
```python
# Redis connection pools
cache_redis = Redis(host='redis', port=6379, db=0)  # General cache
session_redis = Redis(host='redis', port=6379, db=1)  # Sessions
celery_redis = Redis(host='redis', port=6379, db=2)  # Celery
```

### Task Queue & Background Jobs

**Celery with Redis Broker**

#### Background Tasks
1. **Activity Sync**: Fetch new activities from Garmin/Strava (every 6 hours)
2. **Training Load Calculation**: Update CTL/ATL/TSB (daily)
3. **File Processing**: Parse uploaded FIT/TCX files asynchronously
4. **Notifications**: Send workout reminders (optional)
5. **Data Cleanup**: Archive old activities (monthly)

#### Celery Configuration
```python
# celery_config.py
broker_url = 'redis://redis:6379/2'
result_backend = 'redis://redis:6379/2'
task_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Berlin'
enable_utc = True

# Task schedules
beat_schedule = {
    'sync-garmin-activities': {
        'task': 'tasks.sync_garmin',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
    'calculate-training-load': {
        'task': 'tasks.calculate_load',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

#### Alternative: APScheduler
**Pros**: Simpler, no Redis dependency
**Cons**: No distributed task support, less scalable
**Verdict**: Celery chosen for robustness and future scaling

## Frontend Technologies

### Framework & Build Tool

**React 18.x + TypeScript + Vite**

#### React Benefits
- **Component Ecosystem**: Massive library of components
- **PWA Support**: Service workers, offline support
- **Mobile Libraries**: React Native compatibility (future)
- **Developer Tools**: Excellent debugging, profiling
- **Community**: Largest frontend community

#### Vite Benefits
- **Fast Dev Server**: ESbuild-based, instant HMR
- **Optimized Builds**: Rollup-based production builds
- **Zero Config**: Works out of the box
- **TypeScript**: First-class support

#### TypeScript Benefits
- **Type Safety**: Catch errors at compile time
- **IntelliSense**: Better IDE support
- **Refactoring**: Safer code changes
- **Documentation**: Types serve as inline docs

#### Alternative: Vue.js or Svelte
**Vue Pros**: Simpler learning curve, lighter bundle
**Svelte Pros**: Smallest bundle, fastest runtime
**Verdict**: React chosen for ecosystem and PWA maturity

### State Management

**Zustand**

#### Benefits
- **Simple API**: Less boilerplate than Redux
- **TypeScript**: Excellent type inference
- **DevTools**: Redux DevTools compatible
- **Performance**: Minimal re-renders
- **Size**: Only 2.5kb

#### Store Structure
```typescript
// stores/authStore.ts
interface AuthState {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

// stores/trainingStore.ts
interface TrainingState {
  plans: TrainingPlan[];
  selectedPlan: TrainingPlan | null;
  workouts: Workout[];
  fetchPlans: () => Promise<void>;
  createWorkout: (workout: WorkoutInput) => Promise<void>;
}
```

#### Alternative: Redux Toolkit
**Pros**: More structured, great for large teams
**Cons**: More boilerplate, steeper learning curve
**Verdict**: Zustand sufficient for single-developer project

### UI Component Library

**Material-UI (MUI) v5**

#### Benefits
- **Comprehensive**: 60+ components
- **Customizable**: Theming system
- **Accessible**: ARIA compliant
- **Mobile-Ready**: Responsive by default
- **Icons**: 2000+ Material icons included
- **TypeScript**: Full type support

#### Key Components Used
- `DataGrid`: Activity lists with sorting/filtering
- `DatePicker`: Workout scheduling
- `Drawer`: Mobile navigation
- `Tabs`: Dashboard sections
- `Charts`: Activity detail views
- `Autocomplete`: Search and filters

#### Alternative: Chakra UI or Ant Design
**Chakra Pros**: Modern, better accessibility
**Ant Design Pros**: Enterprise-ready, more components
**Verdict**: MUI chosen for maturity and theming

### Data Visualization

**Chart.js with react-chartjs-2**

#### Chart Types Used
1. **Line Charts**: Pace, heart rate, power over time
2. **Bar Charts**: Weekly training volume, TSS
3. **Stacked Bar**: Training distribution by zone
4. **Pie Chart**: Volume by sport
5. **Scatter Plot**: Pace vs heart rate analysis

#### Alternative: Recharts or D3.js
**Recharts Pros**: React-native, declarative
**D3 Pros**: Maximum flexibility
**Verdict**: Chart.js chosen for balance of simplicity and features

### Mapping

**Leaflet with react-leaflet**

#### Features
- **Activity Routes**: Display GPS tracks
- **Markers**: Start/end points, lap markers
- **Heatmaps**: Activity density over time
- **Elevation Profile**: Integrated with charts
- **Offline Tiles**: Cache map tiles for PWA

#### Alternative: Mapbox GL JS
**Pros**: Better 3D, smoother animations
**Cons**: Requires API key, usage limits
**Verdict**: Leaflet chosen for self-hosted freedom

### Routing

**React Router v6**

#### Routes Structure
```typescript
/                         → Dashboard
/login                    → Login page
/register                 → Registration
/training-plans           → Plan list
/training-plans/:id       → Plan detail/edit
/calendar                 → Calendar view
/activities               → Activity list
/activities/:id           → Activity detail
/analytics                → Analytics dashboard
/settings                 → User settings
/settings/integrations    → Connect Garmin/Strava
```

### HTTP Client

**Axios**

#### Features
- **Interceptors**: Global error handling, auth headers
- **Request/Response Transform**: Automatic JSON parsing
- **Timeout Support**: Prevent hanging requests
- **Cancel Requests**: Abort in-flight requests on navigation

#### API Client Structure
```typescript
// services/api.ts
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
    }
    return Promise.reject(error);
  }
);
```

### PWA Support

**Vite Plugin PWA (workbox)**

#### Features
- **Offline Support**: Cache API responses
- **Install Prompt**: Add to home screen
- **Background Sync**: Upload activities when online
- **Push Notifications**: Workout reminders
- **Update Prompt**: Notify user of new version

## Infrastructure & DevOps

### Containerization

**Docker with Docker Compose**

#### Services
```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: trainingplan
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/trainingplan
      REDIS_URL: redis://redis:6379/0

  celery_worker:
    build: ./backend
    command: celery -A src.tasks worker --loglevel=info
    depends_on:
      - postgres
      - redis

  celery_beat:
    build: ./backend
    command: celery -A src.tasks beat --loglevel=info
    depends_on:
      - redis

  frontend:
    build: ./frontend
    depends_on:
      - backend

  traefik:
    image: traefik:v2.10
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./traefik/acme.json:/acme.json
```

### Reverse Proxy & SSL

**Traefik v2.10**

#### Features
- **Automatic SSL**: Let's Encrypt integration
- **Docker Integration**: Auto-discovery of services
- **Middleware**: Compression, rate limiting, redirects
- **Dashboard**: Service monitoring
- **Load Balancing**: If services are scaled

#### Configuration
```yaml
# traefik.yml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: your@email.com
      storage: /acme.json
      httpChallenge:
        entryPoint: web
```

### Backup Strategy

**Automated PostgreSQL Backups**

#### Backup Script
```bash
#!/bin/bash
# backup.sh - Run via cron daily

BACKUP_DIR="/volume1/backups/trainingplan"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Database backup
docker exec trainingplan_postgres pg_dump -U trainingplan > \
  "${BACKUP_DIR}/db_${TIMESTAMP}.sql"

# Keep only last 30 days
find "${BACKUP_DIR}" -name "db_*.sql" -mtime +30 -delete

# Docker volumes backup
tar czf "${BACKUP_DIR}/volumes_${TIMESTAMP}.tar.gz" \
  /var/lib/docker/volumes/trainingplan_postgres_data \
  /var/lib/docker/volumes/trainingplan_redis_data
```

## Development Tools

### Code Quality

#### Backend (Python)
- **Ruff**: Linting and formatting (replaces Black, Flake8, isort)
- **mypy**: Static type checking
- **pytest**: Testing framework
- **pytest-cov**: Code coverage
- **pre-commit**: Git hooks for quality checks

#### Frontend (TypeScript)
- **ESLint**: Linting with TypeScript rules
- **Prettier**: Code formatting
- **TypeScript**: Type checking
- **Vitest**: Unit testing
- **React Testing Library**: Component testing
- **Playwright**: E2E testing (optional)

### API Documentation

**FastAPI Built-in Swagger UI**
- Interactive API documentation at `/docs`
- ReDoc alternative at `/redoc`
- OpenAPI JSON schema at `/openapi.json`

### Version Control

**Git with Conventional Commits**

#### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Feature branches
- `hotfix/*`: Emergency fixes

#### Commit Convention
```
feat: add Garmin OAuth integration
fix: correct TSS calculation for swimming
docs: update API documentation
chore: upgrade dependencies
test: add unit tests for training load
```

## External APIs & Integrations

### Garmin Connect API
- **Auth**: OAuth 2.0 with PKCE
- **Endpoints**: Activities, activity details, user profile
- **Rate Limits**: ~100 requests/hour
- **Data**: TCX, FIT files

### TrainingPeaks API v2
- **Auth**: API key (requires paid account)
- **Endpoints**: Workouts, workout library, athlete data
- **Format**: JSON
- **TSS**: Native support for TSS values

### Strava API v3
- **Auth**: OAuth 2.0
- **Endpoints**: Activities, activity streams, athlete
- **Rate Limits**: 100/15min, 1000/day
- **Webhook**: Real-time activity updates

## Performance Optimization

### Backend
- **Connection Pooling**: SQLAlchemy with asyncpg (20 connections)
- **Query Optimization**: Indexes, select specific columns
- **Response Caching**: Redis for expensive queries (TTL: 5-60min)
- **Pagination**: Limit results to 50 per page
- **Async I/O**: Use httpx for external API calls

### Frontend
- **Code Splitting**: Lazy load routes with React.lazy()
- **Image Optimization**: WebP format, lazy loading
- **Bundle Size**: Tree shaking, analyze with rollup-plugin-visualizer
- **Caching**: Service worker caches API responses
- **Memoization**: React.memo for expensive components

### Database
- **Indexes**: user_id, activity_date, sport_type
- **Continuous Aggregates**: Pre-computed daily/weekly stats
- **Compression**: TimescaleDB compression for old data (>90 days)
- **Vacuuming**: Auto-vacuum enabled

## Security Measures

1. **Authentication**: JWT with short expiry (15min) + refresh tokens
2. **Password Hashing**: bcrypt with cost factor 12
3. **HTTPS Only**: Force redirect, HSTS header
4. **CORS**: Whitelist frontend origin only
5. **Rate Limiting**: 100 requests/15min per IP
6. **Input Validation**: Pydantic models, SQL injection prevention
7. **Secrets Management**: Environment variables, never commit
8. **API Credentials**: Encrypted storage (Fernet)
9. **CSP Headers**: Prevent XSS attacks
10. **Dependency Scanning**: Dependabot alerts

## Monitoring & Logging

### Logging
- **Structured Logs**: JSON format with context
- **Log Levels**: DEBUG (dev), INFO (prod), WARNING, ERROR
- **Centralized**: All logs to stdout, collected by Docker
- **Sensitive Data**: Never log passwords, tokens

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": await check_db(),
        "redis": await check_redis(),
        "celery": await check_celery_workers(),
    }
```

### Optional: Prometheus + Grafana
- **Metrics**: Request latency, error rate, active users
- **Dashboards**: System resources, API performance
- **Alerts**: Database connection failures, high error rates

## Summary

This technology stack provides:
✅ **Performance**: Async Python, TimescaleDB, Redis caching
✅ **Developer Experience**: FastAPI, React, TypeScript, hot reload
✅ **Scalability**: Celery workers, database indexes, caching
✅ **Reliability**: Docker, automated backups, health checks
✅ **Security**: JWT, HTTPS, input validation, secrets management
✅ **Maintainability**: Type safety, testing, linting, documentation

**Total Stack Complexity**: Medium - appropriate for a solo developer with good documentation and modern tooling.
