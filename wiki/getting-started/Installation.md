# Installation Guide

> **📍 You are here:** [Home](../Home.md) > Getting Started > Installation

For complete installation instructions, see [LOCAL_DEV_SETUP.md](../../LOCAL_DEV_SETUP.md).

## Installation Methods

### Method 1: Local Development (No Docker)
Perfect for quick development and testing.

See: [LOCAL_DEV_SETUP.md](../../LOCAL_DEV_SETUP.md)

### Method 2: Docker Compose (Production)
Full stack deployment with PostgreSQL, Redis, and services.

See: [docker-compose.yml](../../docker-compose.yml)

## Quick Setup

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

✅ Backend: http://localhost:8000  
✅ Frontend: http://localhost:5173

## Next Steps

- [Development Setup](Development-Setup.md) - Configure your dev environment
- [Contributing](Contributing.md) - Start contributing to the project

---

[← Back to Getting Started](../Home.md#-getting-started) | [Home](../Home.md)
