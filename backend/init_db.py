"""
Initialize the database with tables (current model schema).

Used for fresh Postgres installs where Alembic history starts with ALTER
migrations (no baseline create_table for core models).
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings
from src.database import Base

# Register all models on Base.metadata
from src.models import (  # noqa: F401
    User,
    TrainingPlan,
    Workout,
    GarminActivity,
    WeeklyThreshold,
    GarminHRV,
    Event,
)


async def init_db() -> None:
    """Create all database tables from SQLAlchemy models."""
    engine = create_async_engine(settings.database_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    print("Database initialized successfully (create_all).")


if __name__ == "__main__":
    asyncio.run(init_db())
