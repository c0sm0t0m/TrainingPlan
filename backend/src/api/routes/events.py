"""
Event API Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.database import get_db
from src.models.user import User
from src.models.event import Event
from src.api.schemas.event import (
    EventCreate,
    EventUpdate,
    Event as EventSchema,
)
from src.api.routes.auth import get_current_active_user

router = APIRouter(prefix="/events", tags=["events"])


async def _clear_other_main_goals(
    db: AsyncSession, user_id: int, keep_id: int | None = None
) -> None:
    """Only one event is the main goal."""
    result = await db.execute(
        select(Event).where(
            and_(Event.user_id == user_id, Event.is_main_goal == 1)
        )
    )
    for other in result.scalars().all():
        if keep_id is None or other.id != keep_id:
            other.is_main_goal = 0


@router.get("", response_model=List[EventSchema])
async def list_events(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all events for the current user."""
    result = await db.execute(
        select(Event)
        .where(Event.user_id == current_user.id)
        .order_by(Event.event_date.desc())
        .offset(skip)
        .limit(limit)
    )
    events = result.scalars().all()
    return events


@router.get("/{event_id}", response_model=EventSchema)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific event by ID."""
    result = await db.execute(
        select(Event).where(
            and_(
                Event.id == event_id,
                Event.user_id == current_user.id
            )
        )
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event


@router.post("", response_model=EventSchema, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new event."""
    event = Event(
        user_id=current_user.id,
        name=event_data.name,
        event_date=event_data.event_date,
        event_type=event_data.event_type,
        location=event_data.location,
        description=event_data.description,
        goal_time=event_data.goal_time,
        target_distance=event_data.target_distance,
        registration_link=event_data.registration_link,
        cost=event_data.cost,
        notes=event_data.notes,
        is_main_goal=1 if event_data.is_main_goal else 0,
    )

    if event_data.is_main_goal:
        await _clear_other_main_goals(db, current_user.id)

    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    return event


@router.put("/{event_id}", response_model=EventSchema)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing event."""
    result = await db.execute(
        select(Event).where(
            and_(
                Event.id == event_id,
                Event.user_id == current_user.id
            )
        )
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    update_data = event_data.model_dump(exclude_unset=True)
    if update_data.get("is_main_goal"):
        await _clear_other_main_goals(db, current_user.id, keep_id=event.id)
        update_data["is_main_goal"] = 1
    elif "is_main_goal" in update_data:
        update_data["is_main_goal"] = 0
    for field, value in update_data.items():
        setattr(event, field, value)
    
    await db.commit()
    await db.refresh(event)
    
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an event."""
    result = await db.execute(
        select(Event).where(
            and_(
                Event.id == event_id,
                Event.user_id == current_user.id
            )
        )
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    await db.delete(event)
    await db.commit()
    
    return None
