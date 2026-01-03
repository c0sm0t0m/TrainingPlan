"""
Authentication API routes
"""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.models.user import User
from src.api.schemas.auth import UserCreate, UserLogin, User as UserSchema, UserUpdate, Token
from src.utils.auth import verify_password, get_password_hash, create_access_token, decode_access_token

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        token: JWT access token from request header
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get the current active user (checks if user is active).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if active
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    """
    Login and get access token.
    
    Args:
        form_data: OAuth2 login form (username=email, password)
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user by email (username field contains email)
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current user information.
    
    Args:
        current_user: Currently authenticated user
        
    Returns:
        User information
    """
    return current_user


@router.patch("/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's training thresholds.
    
    Args:
        user_update: User threshold updates
        current_user: Currently authenticated user
        db: Database session
        
    Returns:
        Updated user information
    """
    # Update only provided fields
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.get("/zones/{zone_type}")
async def get_training_zones(
    zone_type: str,
    method: str,
    threshold: Optional[float] = None,
    max_hr: Optional[int] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """
    Calculate training zones based on provided thresholds or user's stored thresholds.
    
    Args:
        zone_type: 'power', 'hr_cycling', 'hr_running', 'hr_swimming', 'pace_running', 'pace_swimming'
        method: Calculation method (e.g., 'coggan', 'friel')
        threshold: Optional threshold value (FTP, pace, threshold HR) - overrides stored value
        max_hr: Optional max heart rate - overrides stored value (for HR zones)
        current_user: Current authenticated user
        
    Returns:
        List of training zones with min/max values
    """
    from src.utils.calculations.training_zones import calculate_zones, format_pace_for_display
    
    try:
        if zone_type == 'power':
            # Use provided threshold or fall back to user's FTP
            ftp_value = threshold if threshold is not None else current_user.ftp
            if not ftp_value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="FTP not set. Please configure your cycling thresholds or provide a threshold value."
                )
            zones = calculate_zones('power', method, ftp_value)
            
        elif zone_type == 'hr_cycling':
            # Use provided values or fall back to user's stored values
            threshold_hr = threshold if threshold is not None else current_user.cycling_threshold_hr
            max_hr_value = max_hr if max_hr is not None else current_user.max_hr
            if not threshold_hr or not max_hr_value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cycling threshold HR or max HR not set."
                )
            zones = calculate_zones('hr', method, threshold_hr, max_hr_value)
            
        elif zone_type == 'hr_running':
            # Use provided values or fall back to user's stored values
            threshold_hr = threshold if threshold is not None else current_user.running_threshold_hr
            max_hr_value = max_hr if max_hr is not None else current_user.max_hr
            if not threshold_hr or not max_hr_value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Running threshold HR or max HR not set."
                )
            zones = calculate_zones('hr', method, threshold_hr, max_hr_value)
            
        elif zone_type == 'hr_swimming':
            # Use provided values or fall back to user's stored values
            threshold_hr = threshold if threshold is not None else current_user.swim_threshold_hr
            max_hr_value = max_hr if max_hr is not None else current_user.max_hr
            if not threshold_hr or not max_hr_value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Swimming threshold HR or max HR not set."
                )
            zones = calculate_zones('hr', method, threshold_hr, max_hr_value)
            
        elif zone_type == 'pace_running':
            # Use provided threshold or fall back to user's threshold pace
            pace_value = threshold if threshold is not None else current_user.threshold_pace
            if not pace_value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Running threshold pace not set."
                )
            zones = calculate_zones('pace_running', method, pace_value)
            # Format pace values for display
            for zone in zones:
                zone['min_display'] = format_pace_for_display(zone['min'])
                zone['max_display'] = format_pace_for_display(zone['max'])
            
        elif zone_type == 'pace_swimming':
            # Use provided threshold or fall back to user's swim threshold pace
            pace_value = threshold if threshold is not None else current_user.swim_threshold_pace
            if not pace_value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Swimming threshold pace not set."
                )
            zones = calculate_zones('pace_swimming', method, pace_value)
            # Format pace values for display
            for zone in zones:
                zone['min_display'] = format_pace_for_display(zone['min'])
                zone['max_display'] = format_pace_for_display(zone['max'])
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown zone type: {zone_type}"
            )
        
        return zones
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
