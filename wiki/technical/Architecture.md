# Architecture Overview

> **📍 You are here:** [Home](../Home.md) > Technical > Architecture

## System Architecture

Kinesis follows a **microservices-lite** architecture pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                        Traefik (Reverse Proxy)              │
│                      SSL Termination, Routing                │
└─────────────────────────────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼────────┐       ┌───────▼────────┐
        │  Frontend (SPA) │       │  Backend API    │
        │  React + TS     │       │  FastAPI        │
        │  Port: 3000     │       │  Port: 8000     │
        └────────────────┘        └───────┬─────────┘
                                          │
                ┌─────────────────────────┼─────────────────┐
                │                         │                 │
        ┌───────▼────────┐       ┌───────▼────────┐  ┌─────▼──────┐
        │  PostgreSQL +   │       │  Redis Cache    │  │  Celery    │
        │  TimescaleDB    │       │  Session Store  │  │  Workers   │
        └────────────────┘        └────────────────┘  └────────────┘
```

## Key Components

### Frontend (React SPA)
- Single Page Application
- Communicates with backend via REST API
- State managed with Zustand
- PWA capabilities (offline support, installable)

### Backend (FastAPI)
- RESTful API with OpenAPI documentation
- Async/await for performance
- JWT authentication
- Pydantic models for validation

### Database (PostgreSQL + TimescaleDB)
- Relational data (users, plans, workouts)
- Time-series data (activities, samples) optimized with TimescaleDB
- Proper indexes for query performance

### Cache (Redis)
- API response caching
- Session storage
- Celery broker and result backend

### Background Jobs (Celery)
- Activity sync from Garmin (every 6 hours)
- Training load calculations (daily)
- File processing (FIT/TCX parsing)

## Data Flow

### Activity Sync Flow
```
1. Celery Beat (scheduler) triggers sync task
2. Celery Worker fetches activities from Garmin API
3. Worker parses FIT files and extracts metrics
4. Worker stores in PostgreSQL (TimescaleDB hypertable)
5. Worker calculates TSS/CTL/ATL/TSB metrics
6. Worker caches results in Redis
7. Frontend fetches updated data on next request
```

### Training Plan Generation Flow
```
1. User fills AI training plan form
2. Frontend sends request to backend API
3. Backend constructs ChatGPT prompt with trainer style
4. Backend calls OpenAI API
5. Backend auto-cleans JSON response
6. Backend creates TrainingPlan and Workout records
7. Backend returns plan ID to frontend
8. Frontend navigates to plan detail page
```

## Security

- **HTTPS only** - Let's Encrypt SSL certificates
- **JWT authentication** - Short-lived access tokens + refresh tokens
- **Password hashing** - bcrypt with cost factor 12
- **CORS protection** - Whitelist frontend origin
- **Rate limiting** - 100 requests/15min per IP
- **Input validation** - Pydantic models prevent injection
- **Encrypted secrets** - OAuth tokens encrypted at rest

## Scalability

Current architecture supports:
- **1-10 users**: Single-instance deployment
- **10-100 users**: Add more Celery workers
- **100+ users**: Multi-instance backend + load balancer

## Related Documentation

- [Technology Stack](Tech-Stack.md) - Detailed technology choices
- [Database Schema](Database-Schema.md) - Data models
- [API Documentation](API-Documentation.md) - REST API reference
- [Deployment Guide](Deployment-Guide.md) - Production deployment

---

[← Back to Technical](../Home.md#-technical-documentation) | [Home](../Home.md)
