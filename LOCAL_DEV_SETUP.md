# Fast-Track Local Development Setup

Get Kinesis running in 5 minutes without Docker. Start simple, extend iteratively.

## Quick Start (No Docker Required)

### Step 1: Run Backend (2 minutes)

```bash
# Navigate to backend
cd backend

# Create Python virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv

# Start the backend
uvicorn src.main:app --reload --port 8000
```

**✅ Backend now running at http://localhost:8000**

Test it:
- Open browser: http://localhost:8000
- API docs: http://localhost:8000/docs

---

### Step 2: Run Frontend (2 minutes)

Open a **new terminal** (keep backend running):

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**✅ Frontend now running at http://localhost:5173**

Open browser: http://localhost:5173

---

## What You Have Now

✅ **Running Application**: Backend API + Frontend UI  
✅ **Hot Reload**: Changes auto-refresh  
✅ **API Documentation**: Interactive docs at /docs  
⚠️ **No Database Yet**: We'll add this next

---

## Iterative Extension Plan

### Iteration 1: Add Authentication (30 mins)
**Goal**: User login/register

1. **Install auth dependencies**:
   ```bash
   cd backend
   pip install python-jose[cryptography] passlib[bcrypt] python-multipart
   ```

2. **Create User model** (`backend/src/models/user.py`):
   ```python
   from sqlalchemy import Column, Integer, String, Boolean, DateTime
   from datetime import datetime
   from src.database import Base

   class User(Base):
       __tablename__ = "users"
       
       id = Column(Integer, primary_key=True, index=True)
       email = Column(String, unique=True, index=True, nullable=False)
       hashed_password = Column(String, nullable=False)
       full_name = Column(String)
       is_active = Column(Boolean, default=True)
       created_at = Column(DateTime, default=datetime.utcnow)
   ```

3. **Create auth endpoints** (`backend/src/api/routes/auth.py`)
4. **Add login page** (`frontend/src/pages/Login.tsx`)

**Test**: Register user, login, get JWT token

---

### Iteration 2: Add SQLite Database (15 mins)
**Goal**: Persist data locally (no PostgreSQL needed yet)

1. **Update .env**:
   ```bash
   # Change this line:
   DATABASE_URL=sqlite+aiosqlite:///./trainingplan.db
   ```

2. **Install SQLite support**:
   ```bash
   pip install aiosqlite
   ```

3. **Create tables**:
   ```bash
   # In backend directory
   python -c "from src.database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

**Test**: Data now persists between restarts

---

### Iteration 3: Training Plans (45 mins)
**Goal**: Create and view training plans

1. **Create TrainingPlan model** (`backend/src/models/training_plan.py`)
2. **Add CRUD endpoints** (`backend/src/api/routes/training_plans.py`)
3. **Build UI** (`frontend/src/pages/TrainingPlans.tsx`)

**Test**: Create plan, see list, edit plan

---

### Iteration 4: Calendar View (1 hour)
**Goal**: Visual weekly calendar

1. **Install calendar library**:
   ```bash
   cd frontend
   npm install @mui/x-date-pickers date-fns
   ```

2. **Create Workout model**
3. **Build calendar component**
4. **Add drag-and-drop scheduling**

**Test**: Schedule workouts on calendar

---

### Iteration 5: Add PostgreSQL (when Docker ready)
**Goal**: Production database

1. **Start Docker services**:
   ```bash
   docker compose up -d postgres redis
   ```

2. **Update .env back to PostgreSQL**:
   ```bash
   DATABASE_URL=postgresql+asyncpg://trainingplan_user:TraniningPlan.Pwd.2026@localhost:5432/trainingplan
   ```

3. **Run migrations**:
   ```bash
   pip install alembic
   alembic upgrade head
   ```

**Test**: Same app, now with PostgreSQL

---

## Development Workflow

### Making Changes

1. **Backend changes**: Auto-reload (uvicorn --reload)
2. **Frontend changes**: Auto-refresh (Vite HMR)
3. **See changes immediately** in browser

### Adding New Features

**Pattern**: Model → API → Frontend

1. **Create database model** (`backend/src/models/`)
2. **Add API endpoint** (`backend/src/api/routes/`)
3. **Build UI component** (`frontend/src/components/`)
4. **Create page** (`frontend/src/pages/`)
5. **Test in browser**

### Common Tasks

**Add new Python package**:
```bash
cd backend
pip install package-name
pip freeze > requirements.txt  # Save for later
```

**Add new npm package**:
```bash
cd frontend
npm install package-name
```

**View backend logs**: Check terminal running uvicorn

**View frontend logs**: Check browser console (F12)

---

## When Docker is Ready

### Migrate to Docker (5 mins)

1. **Stop local services** (Ctrl+C in both terminals)

2. **Start Docker**:
   ```bash
   docker compose up -d
   ```

3. **Access same URLs**:
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000 (note: port changes to 3000)

**Your code works exactly the same!**

---

## Next Features to Build (Priority Order)

### Week 1-2: Foundation
- ✅ Basic backend/frontend running (NOW)
- [ ] User authentication (register, login, JWT)
- [ ] SQLite database setup
- [ ] Basic UI layout (header, sidebar)

### Week 2-3: Training Plans
- [ ] Training plan CRUD (create, read, update, delete)
- [ ] Workout types (run, bike, swim, strength)
- [ ] Plan list view
- [ ] Plan detail/edit page

### Week 3-4: Calendar
- [ ] Calendar component
- [ ] Schedule workouts
- [ ] Drag-and-drop
- [ ] Weekly/monthly views

### Week 4-5: Activities
- [ ] Manual activity entry
- [ ] Activity list
- [ ] Activity detail view
- [ ] Link activities to planned workouts

### Week 6-8: Garmin Integration
- [ ] OAuth flow
- [ ] Sync activities
- [ ] Parse FIT files
- [ ] Display GPS tracks

---

## Troubleshooting

**Backend won't start**:
```bash
# Check Python version
python3 --version  # Need 3.11+

# Reinstall dependencies
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend won't start**:
```bash
# Check Node version
node --version  # Need 20+

# Clear and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Port already in use**:
```bash
# Change backend port
uvicorn src.main:app --reload --port 8001

# Update frontend .env
VITE_API_URL=http://localhost:8001/api/v1
```

---

## Tips for Iterative Development

1. **Start with static data**: Hardcode in frontend first, add API later
2. **One feature at a time**: Get it working before moving on
3. **Test frequently**: Refresh browser after each change
4. **Commit often**: `git commit -m "Add feature X"` after each working iteration
5. **UI before logic**: Build the interface, then connect backend
6. **Use API docs**: Test endpoints at http://localhost:8000/docs before building UI

---

## File Structure Reference

```
backend/src/
├── models/          ← Add new database tables here
├── api/routes/      ← Add new API endpoints here
├── services/        ← Add business logic here
└── utils/           ← Add helper functions here

frontend/src/
├── components/      ← Add reusable UI components
├── pages/           ← Add new pages/routes here
├── services/        ← Add API calls here
└── store/           ← Add state management here
```

---

## Current Status

**Phase 1, Week 1**: ✅ Complete  
**Phase 1, Week 2**: 🔄 Starting now

**Your path forward**:
1. Get backend + frontend running locally (10 mins)
2. Add authentication (30 mins) 
3. Add training plan model + CRUD (1 hour)
4. Build training plan UI (2 hours)
5. You have a working MVP!

Then continue iterating feature by feature. 🚀
