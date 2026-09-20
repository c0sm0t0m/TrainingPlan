# Kinesis - Detailed Project Plan

## Executive Summary
Build a self-hosted triathlon training management platform that rivals commercial solutions like TrainingPeaks, providing personalized training plans, multi-platform integrations, and comprehensive analytics - all running on your QNAP NAS.

## Requirements Analysis

### Functional Requirements

#### 1. Training Plan Management
- Create individualized training plans for triathlon and running
- Support multi-sport workouts (swim, bike, run, strength, brick sessions)
- Define structured workouts with intervals, zones, and targets
- Schedule workouts on calendar with drag-and-drop interface
- Template library for common workout types
- Plan phases (base, build, peak, taper, recovery)
- Clone and modify existing plans

#### 2. Integrations
- **Garmin Connect**: OAuth authentication, automatic activity sync
- **TrainingPeaks**: Import/export training plans, import completed workouts
- **Strava**: Import activities and convert to training sessions
- **File Support**: Import TCX, FIT, GPX files manually
- **Export**: Generate plans in multiple formats (ICS, TrainingPeaks)

#### 3. Activity Tracking
- Automatic sync from Garmin (daily background job)
- Manual activity entry
- Display activity details: map, pace/HR/power charts, splits, zones
- Match activities to planned workouts
- Activity metadata: weather, equipment, notes, feelings

#### 4. Analytics & Insights
- Training load calculations (TSS, CTL, ATL, TSB)
- Fitness/Fatigue/Form chart
- Weekly/monthly volume summaries
- Training distribution (time by sport, by intensity zone)
- Personal records tracking
- VO2max and FTP estimation
- Goal tracking and progress

#### 5. Mobile Access
- Responsive web design (mobile-first)
- PWA for offline access and home screen install
- Quick workout logging
- Today's workout view
- Calendar overview
- Activity detail view

### Non-Functional Requirements

#### Performance
- Page load time: <2 seconds
- API response time: <500ms (p95)
- Background sync: complete in <5 minutes
- Support 1000+ activities per user

#### Security
- HTTPS only (Let's Encrypt SSL)
- JWT authentication with refresh tokens
- API rate limiting
- Encrypted credential storage for integrations
- CORS protection
- Input validation and sanitization

#### Reliability
- 99% uptime on local network
- Automatic backup (daily database dumps)
- Graceful degradation when integrations fail
- Transaction rollback on errors
- Health check endpoints

#### Usability
- Intuitive UI matching modern fitness apps
- Mobile-responsive design
- Dark mode support
- Localization support (initially English/German)
- Comprehensive error messages

## Technology Stack Decision Matrix

### Backend Framework
| Option | Pros | Cons | Score |
|--------|------|------|-------|
| **FastAPI (Python)** | Fast, async, type hints, ML libraries, FIT parsing | Python overhead | ⭐⭐⭐⭐⭐ |
| NestJS (Node.js) | TypeScript, great DX, fast | Limited ML libraries | ⭐⭐⭐⭐ |
| Django | Mature, admin panel, ORM | Heavier, more opinionated | ⭐⭐⭐ |

**Decision: FastAPI** - Best balance of performance, ML capabilities, and file parsing

### Database
| Option | Pros | Cons | Score |
|--------|------|------|-------|
| **PostgreSQL + TimescaleDB** | Relational + time-series, mature, QNAP support | Setup complexity | ⭐⭐⭐⭐⭐ |
| MongoDB | Flexible schema | No time-series optimization | ⭐⭐⭐ |
| SQLite | Simple, embedded | Limited concurrency | ⭐⭐ |

**Decision: PostgreSQL with TimescaleDB** - Optimal for time-series workout data

### Frontend
| Option | Pros | Cons | Score |
|--------|------|------|-------|
| **React + TypeScript** | Large ecosystem, PWA support, mobile libraries | Bundle size | ⭐⭐⭐⭐⭐ |
| Vue.js | Simpler learning curve | Smaller ecosystem | ⭐⭐⭐⭐ |
| Svelte | Smaller bundle | Less mature | ⭐⭐⭐ |

**Decision: React + TypeScript** - Best ecosystem and mobile support

### Deployment
| Option | Pros | Cons | Score |
|--------|------|------|-------|
| **Docker Compose** | Simple, QNAP native, easy backup | Limited orchestration | ⭐⭐⭐⭐⭐ |
| Kubernetes | Scalable | Overkill for single-user | ⭐⭐ |

**Decision: Docker Compose** - Perfect for QNAP Container Station

## Detailed Implementation Roadmap

### Phase 1: Foundation & Infrastructure (3 weeks)

#### Week 1: Project Setup
- [ ] Initialize Git repository with feature branch workflow
- [ ] Create Docker Compose configuration
  - PostgreSQL 15 with TimescaleDB
  - Redis 7
  - Backend (FastAPI)
  - Frontend (React dev server)
  - Traefik reverse proxy
- [ ] Set up development environment
  - Python virtual environment
  - Node.js/npm setup
  - Pre-commit hooks (linting, formatting)
- [ ] Configure environment variables (.env.example)
- [ ] Create initial documentation (README, CONTRIBUTING)

#### Week 2: Backend Core
- [ ] FastAPI project structure
- [ ] SQLAlchemy models
  - User (auth, profile)
  - TrainingPlan
  - Workout (planned)
  - Activity (completed)
  - Integration (OAuth tokens)
- [ ] Alembic migrations setup
- [ ] JWT authentication endpoints (login, register, refresh)
- [ ] Basic CRUD API for training plans
- [ ] Unit tests setup (pytest)
- [ ] API documentation (OpenAPI/Swagger)

#### Week 3: Frontend Foundation
- [ ] React + TypeScript + Vite project
- [ ] Routing setup (React Router)
- [ ] State management (Zustand)
- [ ] Material-UI integration
- [ ] Authentication flow (login, register, protected routes)
- [ ] API client service with axios
- [ ] Basic layout (header, sidebar, main content)
- [ ] Home dashboard skeleton

**Milestone 1**: Running app with user authentication and basic UI

### Phase 2: Training Plan Management (3 weeks)

#### Week 4: Plan Creation
- [ ] Training plan CRUD API endpoints
- [ ] Workout CRUD API endpoints
- [ ] Training plan form UI (name, dates, sport type)
- [ ] Workout template library (seeded data)
- [ ] Workout builder UI
  - Sport selection
  - Duration/distance input
  - Intensity/zone selection
  - Description/notes
- [ ] Plan list view with cards

#### Week 5: Calendar Interface
- [ ] Calendar view component (FullCalendar or custom)
- [ ] Drag-and-drop workout scheduling
- [ ] Weekly/monthly calendar views
- [ ] Workout detail modal
- [ ] Copy/paste workouts
- [ ] Recurring workout creation
- [ ] Calendar filtering (by sport)

#### Week 6: Zones & Structure
- [ ] Training zones configuration (HR, power, pace)
- [ ] Structured workout builder
  - Warmup/cooldown
  - Intervals with repeats
  - Target zones per interval
- [ ] Workout preview display
- [ ] Plan phases (base, build, peak, taper)
- [ ] Training plan export (ICS format)

**Milestone 2**: Complete training plan creation and scheduling

### Phase 3: Garmin Integration (3 weeks)

#### Week 7: OAuth & API Setup
- [ ] Garmin Developer account setup
- [ ] OAuth 2.0 flow implementation (PKCE)
- [ ] Integration model for storing tokens
- [ ] Token refresh logic
- [ ] Garmin API client service
- [ ] Integration settings UI (connect/disconnect)

#### Week 8: Activity Sync
- [ ] Celery task queue setup
- [ ] Background job: sync Garmin activities
- [ ] Activity model expansion (detailed metrics)
- [ ] FIT file parser (fitparse library)
- [ ] Store activity data (time-series in TimescaleDB)
- [ ] Activity sync status tracking
- [ ] Manual sync trigger UI

#### Week 9: Activity Display
- [ ] Activity list view (sortable, filterable)
- [ ] Activity detail page
  - Summary stats
  - GPS map (Leaflet or Mapbox)
  - Pace/HR/power charts (Chart.js)
  - Lap splits table
- [ ] Match activity to planned workout
- [ ] Activity editing (title, description, equipment)

**Milestone 3**: Automatic Garmin sync and activity display

### Phase 4: Calendar & Activity Display (2 weeks)

#### Week 10: Enhanced Calendar View
- [ ] Display completed activities on calendar
- [ ] Differentiate planned vs completed workouts visually
- [ ] Activity markers with sport icons
- [ ] Click activity to view details
- [ ] Filter calendar by sport type
- [ ] Weekly/monthly summary stats on calendar
- [ ] Color coding by intensity/zones

#### Week 11: Complete Garmin Data Import
- [ ] Verify all activity metrics are imported
  - Heart rate data (avg, max, zones)
  - Power data (avg, normalized, zones)
  - Cadence data
  - Pace/speed data
  - Elevation gain/loss
  - Temperature
  - Training effect
- [ ] Import activity laps and splits
- [ ] Import GPS track points for mapping
- [ ] Verify TimescaleDB optimization for activity data
- [ ] Add missing activity fields if needed

**Milestone 4**: Calendar displays full activity history with complete metrics

### Phase 5: Analytics Dashboard (3 weeks)

#### Week 12: Training Load Calculations
- [ ] TSS calculation service
  - Running TSS (rTSS) using pace and HR
  - Cycling TSS (from power or HR-based estimate)
  - Swimming TSS (sTSS) using pace
- [ ] CTL (Chronic Training Load) calculation (42-day exponential average)
- [ ] ATL (Acute Training Load) calculation (7-day exponential average)
- [ ] TSB (Training Stress Balance) calculation (CTL - ATL)
- [ ] TRIMP calculation as alternative metric
- [ ] Background job to calculate daily metrics
- [ ] Store calculated metrics in database

#### Week 13: Dashboard Core Metrics
- [ ] Fitness/Fatigue/Form (CTL/ATL/TSB) chart with time series
- [ ] Training load chart (daily/weekly TSS bars + CTL/ATL lines)
- [ ] Current fitness indicators (CTL, ATL, TSB values)
- [ ] Weekly summary cards (total distance, time, TSS, activities)
- [ ] Recent activities list (last 7 days)
- [ ] Upcoming planned workouts (next 7 days)
- [ ] Activity streak counter
- [ ] Volume by sport breakdown (pie chart)

#### Week 14: Additional Analytics & Metrics
- [ ] Training distribution by intensity zones (stacked bar)
- [ ] Monthly volume comparison chart
- [ ] Personal records tracking (fastest 5K, longest ride, etc.)
- [ ] Activity frequency heatmap (calendar view)
- [ ] VO2max estimation from activities (optional)
- [ ] FTP/threshold pace estimates (optional)
- [ ] Export dashboard data (CSV format)

**Milestone 5**: Functional analytics dashboard with TSS/CTL/ATL/TSB metrics

### Phase 6: UI/UX Polish & Navigation (2 weeks)

#### Week 15: Navigation Improvements
- [ ] Add back button to all subpages (PlanDetail, Settings, etc.)
- [ ] Breadcrumb navigation for nested pages
- [ ] Consistent navigation patterns across app
- [ ] Keyboard shortcuts for power users
- [ ] Quick navigation menu (Cmd+K / Ctrl+K)
- [ ] Improve sidebar active state indicators
- [ ] Add loading states and skeleton screens
- [ ] Better error messages and empty states

#### Week 16: Responsive Design & Mobile
- [ ] Mobile-first CSS refactoring
- [ ] Touch-optimized components
- [ ] Bottom navigation for mobile
- [ ] Swipeable calendar on mobile
- [ ] Collapsible sections for better mobile UX
- [ ] Responsive charts (adapt to screen size)
- [ ] Mobile workout detail view
- [ ] Test on various screen sizes

**Milestone 6**: Polished UI with excellent navigation and mobile support

### Phase 7: Deployment & Production (2 weeks)

#### Week 17: QNAP Deployment
- [ ] Production Docker Compose configuration
- [ ] Traefik setup with Let's Encrypt
- [ ] QNAP Container Station deployment guide
- [ ] Environment variable configuration
- [ ] Database initialization scripts
- [ ] Health check endpoints
- [ ] Logging setup (structured logs)

#### Week 18: Operations & Polish
- [ ] Automated backup script (cron job)
- [ ] Database restore procedure
- [ ] Monitoring setup (optional: Prometheus + Grafana)
- [ ] Performance optimization
  - Query optimization
  - Response caching
  - Image optimization
- [ ] Security audit
- [ ] User documentation
- [ ] Video tutorials (optional)

**Milestone 7**: Production-ready deployment on QNAP

## Risk Management

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Garmin API rate limits | High | Medium | Implement intelligent sync (delta only), cache data |
| TrainingPeaks API cost | Medium | Low | Make optional, provide alternative import |
| QNAP resource constraints | High | Medium | Optimize Docker memory limits, use Redis caching |
| Integration API changes | Medium | Medium | Abstract API clients, version lock dependencies |
| Data loss | High | Low | Automated daily backups, transaction safety |
| Complex workout matching | Medium | High | Start with simple matching, iterate |

## Success Metrics

### Technical Metrics
- API response time p95 < 500ms
- Page load time < 2s
- Database queries < 50ms average
- Test coverage > 80%
- Zero critical security vulnerabilities

### User Experience Metrics
- Can create training plan in < 5 minutes
- Garmin sync completes in < 2 minutes
- Mobile usable (Lighthouse score > 90)
- Dark mode available
- Documentation complete

### Feature Completeness
- ✅ Create/edit/delete training plans
- ✅ Sync workouts to Garmin calendar
- ✅ Import activities from Garmin
- ✅ View training load metrics (TSS, CTL, ATL, TSB)
- ✅ Calendar with planned and completed activities
- ✅ Analytics dashboard
- ✅ Mobile responsive
- ✅ Runs on QNAP
- ✅ Automated backups

## Resource Requirements

### Development
- **Time**: ~20 weeks part-time (10-15 hours/week)
- **Skills**: Python, TypeScript/React, Docker, REST APIs, OAuth
- **Tools**: VS Code, Docker Desktop, Postman, Git

### Infrastructure
- **QNAP NAS**: Minimum 4GB RAM, Container Station enabled
- **Storage**: ~10GB for application + database
- **Network**: Static IP or DDNS for external access (optional)

### External Services
- Garmin Developer Account (free)
- TrainingPeaks API key (optional, requires paid account)
- Strava API application (free)
- Domain name for SSL (optional)

## Future Enhancements (Post-MVP)

### Phase 8+: Multi-Platform Integration
- [ ] **TrainingPeaks Integration**
  - Import/export training plans
  - Import completed workouts
  - Two-way sync
- [ ] **Strava Integration**
  - OAuth authentication
  - Activity import with detailed streams
  - Webhook for real-time sync
- [ ] **File Upload & Manual Entry**
  - TCX, GPX, FIT file upload
  - Manual activity entry form
  - Bulk import functionality

### Phase 9+: Advanced Features
- [ ] PWA features (offline support, push notifications)
- [ ] Race planning and taper recommendations
- [ ] AI-powered workout suggestions
- [ ] Social features (share workouts with coach/friends)
- [ ] Native mobile app (React Native)
- [ ] Apple Health / Google Fit integration
- [ ] Nutrition tracking
- [ ] Equipment management (bike, shoes mileage)
- [ ] Video analysis integration
- [ ] Multi-user support (family/team)
- [ ] Coach/athlete relationship features
- [ ] Workout library marketplace
- [ ] Advanced periodization models (Coggan, Friel)
- [ ] Recovery metrics (HRV integration)
- [ ] Weather integration (forecast for planned workouts)
- [ ] Zwift/TrainerRoad integration

## Getting Started

1. **Review this plan** and adjust timeline based on your availability
2. **Set up development environment** (Docker, Python, Node.js)
3. **Start Phase 1, Week 1** with project initialization
4. **Commit to regular development** (2-3 sessions per week)
5. **Iterate based on feedback** (use it yourself, adjust priorities)

## Notes
- This is an ambitious project; prioritize MVP features first
- Consider starting with running-only, then adding triathlon support
- You can deploy after Phase 3 for personal use while continuing development
- The phased approach allows for early feedback and course correction
- Don't let perfect be the enemy of good - iterate based on actual usage

**Good luck building your training platform! 🏃‍♂️🚴‍♂️🏊‍♂️**
