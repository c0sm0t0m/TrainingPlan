"""
TrainingPlan FastAPI Application Entry Point
"""
# Setup SSL certificates using truststore first
try:
    import truststore
    truststore.inject_into_ssl()
    print("✓ Truststore injected into SSL")
except ImportError:
    print("⚠ Truststore not available")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Self-hosted triathlon and running training management platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Log CORS configuration in development
if settings.environment == "development":
    print(f"✓ CORS enabled for origins: {settings.cors_origins_list}")



# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API status."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


# API v1 routes
from src.api.routes import auth, training_plans, garmin, analytics, activities, events, ai_training_plan, icu, workout_library

app.include_router(auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["Authentication"])
app.include_router(training_plans.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(garmin.router, prefix=f"{settings.api_v1_prefix}", tags=["Garmin Connect"])
app.include_router(icu.router, prefix=f"{settings.api_v1_prefix}", tags=["Intervals.icu"])
app.include_router(workout_library.router, prefix=f"{settings.api_v1_prefix}", tags=["Workout Library"])
app.include_router(analytics.router, prefix=f"{settings.api_v1_prefix}", tags=["Analytics"])
app.include_router(activities.router, prefix=f"{settings.api_v1_prefix}", tags=["Activities"])
app.include_router(events.router, prefix=f"{settings.api_v1_prefix}", tags=["Events"])
app.include_router(ai_training_plan.router, prefix=f"{settings.api_v1_prefix}", tags=["AI Training Plan"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
