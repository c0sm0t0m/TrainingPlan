"""
Training Plan API Routes
"""
from typing import List
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.database import get_db
from src.models.user import User
from src.models.training_plan import TrainingPlan, Workout
from src.api.schemas.training_plan import (
    TrainingPlanCreate,
    TrainingPlanUpdate,
    TrainingPlan as TrainingPlanSchema,
    TrainingPlanSummary,
    WorkoutCreate,
    WorkoutUpdate,
    Workout as WorkoutSchema,
)
from src.api.routes.auth import get_current_active_user
from src.utils.workout_xml import parse_workout_xml, validate_workout_data

router = APIRouter(prefix="/training-plans", tags=["training-plans"])


@router.get("", response_model=List[TrainingPlanSummary])
async def list_training_plans(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all training plans for the current user.
    
    Args:
        active_only: If True, only return plans where is_active = 1
    """
    query = select(TrainingPlan).where(TrainingPlan.user_id == current_user.id)
    
    if active_only:
        query = query.where(TrainingPlan.is_active == 1)
    
    result = await db.execute(
        query.offset(skip).limit(limit)
    )
    plans = result.scalars().all()
    
    # Add workout counts
    plan_summaries = []
    for plan in plans:
        workout_result = await db.execute(
            select(func.count(Workout.id))
            .where(Workout.training_plan_id == plan.id)
        )
        workout_count = workout_result.scalar()
        
        completed_result = await db.execute(
            select(func.count(Workout.id))
            .where(Workout.training_plan_id == plan.id)
            .where(Workout.is_completed == 1)
        )
        completed_count = completed_result.scalar()
        
        plan_dict = {
            "id": plan.id,
            "user_id": plan.user_id,
            "name": plan.name,
            "description": plan.description,
            "start_date": plan.start_date,
            "end_date": plan.end_date,
            "sport_type": plan.sport_type,
            "is_active": bool(plan.is_active),
            "activation_date": plan.activation_date,
            "created_at": plan.created_at,
            "updated_at": plan.updated_at,
            "workout_count": workout_count or 0,
            "completed_count": completed_count or 0,
        }
        plan_summaries.append(TrainingPlanSummary(**plan_dict))
    
    return plan_summaries


@router.post("", response_model=TrainingPlanSummary, status_code=status.HTTP_201_CREATED)
async def create_training_plan(
    plan_data: TrainingPlanCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new training plan."""
    plan = TrainingPlan(
        user_id=current_user.id,
        name=plan_data.name,
        description=plan_data.description,
        start_date=plan_data.start_date,
        end_date=plan_data.end_date,
        sport_type=plan_data.sport_type.value,
    )
    
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    
    return TrainingPlanSummary(
        id=plan.id,
        user_id=plan.user_id,
        name=plan.name,
        description=plan.description,
        start_date=plan.start_date,
        end_date=plan.end_date,
        sport_type=plan.sport_type,
        is_active=bool(plan.is_active),
        activation_date=plan.activation_date,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        workout_count=0,
        completed_count=0,
    )


@router.get("/{plan_id}", response_model=TrainingPlanSchema)
async def get_training_plan(
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific training plan with all workouts."""
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.id == plan_id,
            TrainingPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training plan not found"
        )
    
    # Fetch workouts
    workouts_result = await db.execute(
        select(Workout).where(Workout.training_plan_id == plan_id)
    )
    workouts = workouts_result.scalars().all()
    
    return TrainingPlanSchema(
        id=plan.id,
        user_id=plan.user_id,
        name=plan.name,
        description=plan.description,
        start_date=plan.start_date,
        end_date=plan.end_date,
        sport_type=plan.sport_type,
        is_active=bool(plan.is_active),
        activation_date=plan.activation_date,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        workouts=[
            WorkoutSchema(
                id=w.id,
                training_plan_id=w.training_plan_id,
                date=w.date,
                sport_type=w.sport_type,
                workout_type=w.workout_type,
                title=w.title,
                description=w.description,
                duration_minutes=w.duration_minutes,
                distance_km=w.distance_km,
                intensity_zone=w.intensity_zone,
                target_tss=w.target_tss,
                is_completed=bool(w.is_completed),
                actual_duration_minutes=w.actual_duration_minutes,
                actual_distance_km=w.actual_distance_km,
                notes=w.notes,
                created_at=w.created_at,
                updated_at=w.updated_at,
            )
            for w in workouts
        ]
    )


@router.put("/{plan_id}", response_model=TrainingPlanSchema)
async def update_training_plan(
    plan_id: int,
    plan_data: TrainingPlanUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a training plan."""
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.id == plan_id,
            TrainingPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training plan not found"
        )
    
    # Update fields
    if plan_data.name is not None:
        plan.name = plan_data.name
    if plan_data.description is not None:
        plan.description = plan_data.description
    if plan_data.start_date is not None:
        plan.start_date = plan_data.start_date
    if plan_data.end_date is not None:
        plan.end_date = plan_data.end_date
    if plan_data.sport_type is not None:
        plan.sport_type = plan_data.sport_type.value
    if plan_data.is_active is not None:
        plan.is_active = 1 if plan_data.is_active else 0
    
    await db.commit()
    await db.refresh(plan)
    
    # Fetch workouts
    workouts_result = await db.execute(
        select(Workout).where(Workout.training_plan_id == plan_id)
    )
    workouts = workouts_result.scalars().all()
    
    return TrainingPlanSchema(
        id=plan.id,
        user_id=plan.user_id,
        name=plan.name,
        description=plan.description,
        start_date=plan.start_date,
        end_date=plan.end_date,
        sport_type=plan.sport_type,
        is_active=bool(plan.is_active),
        activation_date=plan.activation_date,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        workouts=[
            WorkoutSchema(
                id=w.id,
                training_plan_id=w.training_plan_id,
                date=w.date,
                sport_type=w.sport_type,
                workout_type=w.workout_type,
                title=w.title,
                description=w.description,
                duration_minutes=w.duration_minutes,
                distance_km=w.distance_km,
                intensity_zone=w.intensity_zone,
                target_tss=w.target_tss,
                is_completed=bool(w.is_completed),
                actual_duration_minutes=w.actual_duration_minutes,
                actual_distance_km=w.actual_distance_km,
                notes=w.notes,
                created_at=w.created_at,
                updated_at=w.updated_at,
            )
            for w in workouts
        ]
    )


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_plan(
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a training plan."""
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.id == plan_id,
            TrainingPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training plan not found"
        )
    
    await db.delete(plan)
    await db.commit()
    
    return None


@router.post("/{plan_id}/activate", response_model=TrainingPlanSchema)
async def activate_training_plan(
    plan_id: int,
    activation_date: date = Body(default=None, embed=True),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Activate a training plan with optional activation date.
    Deactivates all other plans for the user to ensure only one plan is active at a time.
    
    Args:
        activation_date: Optional date when the plan should be considered as starting.
                        If not provided, uses today's date.
    """
    # Use today if no activation date provided
    if activation_date is None:
        activation_date = date.today()
    
    # First, verify the plan exists and belongs to the user
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.id == plan_id,
            TrainingPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training plan not found"
        )
    
    # Deactivate all other plans for this user
    await db.execute(
        select(TrainingPlan)
        .where(TrainingPlan.user_id == current_user.id)
    )
    all_plans_result = await db.execute(
        select(TrainingPlan).where(TrainingPlan.user_id == current_user.id)
    )
    all_plans = all_plans_result.scalars().all()
    
    for p in all_plans:
        p.is_active = 0
        if p.id != plan_id:
            p.activation_date = None
    
    # Activate the selected plan
    plan.is_active = 1
    plan.activation_date = activation_date
    
    await db.commit()
    await db.refresh(plan)
    
    # Fetch workouts
    workouts_result = await db.execute(
        select(Workout).where(Workout.training_plan_id == plan_id)
    )
    workouts = workouts_result.scalars().all()
    
    return TrainingPlanSchema(
        id=plan.id,
        user_id=plan.user_id,
        name=plan.name,
        description=plan.description,
        start_date=plan.start_date,
        end_date=plan.end_date,
        sport_type=plan.sport_type,
        is_active=bool(plan.is_active),
        activation_date=plan.activation_date,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        workouts=[
            WorkoutSchema(
                id=w.id,
                training_plan_id=w.training_plan_id,
                date=w.date,
                sport_type=w.sport_type,
                workout_type=w.workout_type,
                title=w.title,
                description=w.description,
                duration_minutes=w.duration_minutes,
                distance_km=w.distance_km,
                intensity_zone=w.intensity_zone,
                target_tss=w.target_tss,
                is_completed=bool(w.is_completed),
                actual_duration_minutes=w.actual_duration_minutes,
                actual_distance_km=w.actual_distance_km,
                notes=w.notes,
                created_at=w.created_at,
                updated_at=w.updated_at,
            )
            for w in workouts
        ]
    )


@router.post("/{plan_id}/deactivate", response_model=TrainingPlanSchema)
async def deactivate_training_plan(
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a training plan."""
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.id == plan_id,
            TrainingPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training plan not found"
        )
    
    plan.is_active = 0
    
    await db.commit()
    await db.refresh(plan)
    
    # Fetch workouts
    workouts_result = await db.execute(
        select(Workout).where(Workout.training_plan_id == plan_id)
    )
    workouts = workouts_result.scalars().all()
    
    return TrainingPlanSchema(
        id=plan.id,
        user_id=plan.user_id,
        name=plan.name,
        description=plan.description,
        start_date=plan.start_date,
        end_date=plan.end_date,
        sport_type=plan.sport_type,
        is_active=bool(plan.is_active),
        activation_date=plan.activation_date,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        workouts=[
            WorkoutSchema(
                id=w.id,
                training_plan_id=w.training_plan_id,
                date=w.date,
                sport_type=w.sport_type,
                workout_type=w.workout_type,
                title=w.title,
                description=w.description,
                duration_minutes=w.duration_minutes,
                distance_km=w.distance_km,
                intensity_zone=w.intensity_zone,
                target_tss=w.target_tss,
                is_completed=bool(w.is_completed),
                actual_duration_minutes=w.actual_duration_minutes,
                actual_distance_km=w.actual_distance_km,
                notes=w.notes,
                created_at=w.created_at,
                updated_at=w.updated_at,
            )
            for w in workouts
        ]
    )


# Workout endpoints
@router.post("/{plan_id}/workouts", response_model=WorkoutSchema, status_code=status.HTTP_201_CREATED)
async def create_workout(
    plan_id: int,
    workout_data: WorkoutCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a workout to a training plan."""
    # Verify plan ownership
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.id == plan_id,
            TrainingPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training plan not found"
        )
    
    workout = Workout(
        training_plan_id=plan_id,
        date=workout_data.date,
        sport_type=workout_data.sport_type.value,
        workout_type=workout_data.workout_type.value,
        title=workout_data.title,
        description=workout_data.description,
        duration_minutes=workout_data.duration_minutes,
        distance_km=workout_data.distance_km,
        intensity_zone=workout_data.intensity_zone.value if workout_data.intensity_zone else None,
        target_tss=workout_data.target_tss,
    )
    
    db.add(workout)
    await db.commit()
    await db.refresh(workout)
    
    return workout


@router.put("/{plan_id}/workouts/{workout_id}", response_model=WorkoutSchema)
async def update_workout(
    plan_id: int,
    workout_id: int,
    workout_data: WorkoutUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a workout."""
    # Verify plan ownership
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.id == plan_id,
            TrainingPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training plan not found"
        )
    
    # Get workout
    workout_result = await db.execute(
        select(Workout).where(
            Workout.id == workout_id,
            Workout.training_plan_id == plan_id
        )
    )
    workout = workout_result.scalar_one_or_none()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    # Update fields
    if workout_data.date is not None:
        workout.date = workout_data.date
    if workout_data.sport_type is not None:
        workout.sport_type = workout_data.sport_type.value
    if workout_data.workout_type is not None:
        workout.workout_type = workout_data.workout_type.value
    if workout_data.title is not None:
        workout.title = workout_data.title
    if workout_data.description is not None:
        workout.description = workout_data.description
    if workout_data.duration_minutes is not None:
        workout.duration_minutes = workout_data.duration_minutes
    if workout_data.distance_km is not None:
        workout.distance_km = workout_data.distance_km
    if workout_data.intensity_zone is not None:
        workout.intensity_zone = workout_data.intensity_zone.value
    if workout_data.target_tss is not None:
        workout.target_tss = workout_data.target_tss
    if workout_data.is_completed is not None:
        workout.is_completed = 1 if workout_data.is_completed else 0
    if workout_data.actual_duration_minutes is not None:
        workout.actual_duration_minutes = workout_data.actual_duration_minutes
    if workout_data.actual_distance_km is not None:
        workout.actual_distance_km = workout_data.actual_distance_km
    if workout_data.notes is not None:
        workout.notes = workout_data.notes
    
    await db.commit()
    await db.refresh(workout)
    
    return workout


@router.delete("/{plan_id}/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    plan_id: int,
    workout_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a workout."""
    # Verify plan ownership
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.id == plan_id,
            TrainingPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training plan not found"
        )
    
    # Get workout
    workout_result = await db.execute(
        select(Workout).where(
            Workout.id == workout_id,
            Workout.training_plan_id == plan_id
        )
    )
    workout = workout_result.scalar_one_or_none()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    await db.delete(workout)
    await db.commit()
    
    return None


@router.post("/{plan_id}/workouts/import-xml", response_model=WorkoutSchema, status_code=status.HTTP_201_CREATED)
async def import_workout_from_xml(
    plan_id: int,
    workout_date: str = Body(..., embed=True),
    xml_content: str = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Import a workout from XML format.
    
    Args:
        plan_id: Training plan ID
        workout_date: Date to schedule the workout (YYYY-MM-DD)
        xml_content: XML workout definition
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created workout
    """
    # Verify plan ownership
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.id == plan_id,
            TrainingPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training plan not found"
        )
    
    # Parse XML
    try:
        workout_data = parse_workout_xml(xml_content)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid XML format: {str(e)}"
        )
    
    # Validate data
    if not validate_workout_data(workout_data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required workout fields"
        )
    
    # Convert date string to date object
    if isinstance(workout_date, str):
        workout_date = datetime.strptime(workout_date, "%Y-%m-%d").date()
    
    # Create workout
    workout = Workout(
        training_plan_id=plan_id,
        date=workout_date,
        sport_type=workout_data['sport_type'],
        workout_type=workout_data['workout_type'],
        title=workout_data['title'],
        description=workout_data.get('description'),
        duration_minutes=workout_data.get('duration_minutes'),
        distance_km=workout_data.get('distance_km'),
        intensity_zone=workout_data.get('intensity_zone'),
    )
    
    db.add(workout)
    await db.commit()
    await db.refresh(workout)
    
    return workout
