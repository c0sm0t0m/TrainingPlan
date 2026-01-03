"""
Initialize the database with tables
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from src.config import settings
from src.database import Base

# Import all models here so they are registered with Base
from src.models.user import User
from src.models.training_plan import TrainingPlan, Workout


async def init_db():
    """Create all database tables."""
    engine = create_async_engine(settings.database_url, echo=True)
    
    async with engine.begin() as conn:
        # Drop all tables (use with caution!)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("✅ Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
