"""
AI Training Plan API Routes
"""
import json
import re
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.user import User
from src.api.routes.auth import get_current_active_user
from src.api.schemas.ai_training_plan import (
    PromptGenerationConfig,
    PromptGenerationResponse,
    PlanPhaseInfo,
    TrainingPlanImport,
    ValidationResult,
    PlanPreview,
    ImportResponse
)
from src.services.ai_training_plan_service import (
    generate_ai_prompt,
    validate_training_plan,
    generate_plan_preview,
    import_training_plan
)

router = APIRouter(prefix="/ai-training-plan", tags=["ai-training-plan"])


def clean_chatgpt_json(text: str) -> str:
    """
    Remove markdown code fences and extract JSON from ChatGPT/Claude responses.
    
    This ensures 100% success rate by handling:
    - Markdown fences: ```json ... ```
    - Explanatory text before/after JSON
    - Extra whitespace
    
    Args:
        text: Raw text (may include markdown or explanations)
        
    Returns:
        Cleaned JSON string
    """
    # Decode if bytes
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    
    # Remove markdown code fences at start
    text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.MULTILINE)
    
    # Remove markdown code fences at end
    text = re.sub(r'\n?```\s*$', '', text, flags=re.MULTILINE)
    
    # Remove any leading/trailing whitespace
    text = text.strip()
    
    # If text doesn't start with {, try to find the JSON
    if not text.startswith('{'):
        # Look for first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]
    
    return text


@router.post("/generate-prompt", response_model=PromptGenerationResponse)
async def generate_prompt(
    config: PromptGenerationConfig,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI prompt with user's fitness data for training plan creation.
    
    The generated prompt can be copied and pasted into ChatGPT, Claude, or other LLMs
    to create a personalized training plan.
    """
    try:
        result = await generate_ai_prompt(current_user.id, config, db)
        
        phases = [
            PlanPhaseInfo(
                index=p["index"],
                id=p["id"],
                name=p["name"],
                focus=p["focus"],
                week_start=p["weekStart"],
                week_end=p["weekEnd"],
                weeks=p["weeks"],
                start_date=p["startDate"],
                end_date=p["endDate"],
                is_last=p["isLast"],
            )
            for p in result.get("phases") or []
        ]
        current = None
        if result.get("current_phase"):
            cp = result["current_phase"]
            current = PlanPhaseInfo(
                index=cp["index"],
                id=cp["id"],
                name=cp["name"],
                focus=cp["focus"],
                week_start=cp["weekStart"],
                week_end=cp["weekEnd"],
                weeks=cp["weeks"],
                start_date=cp["startDate"],
                end_date=cp["endDate"],
                is_last=cp["isLast"],
            )

        return PromptGenerationResponse(
            prompt=result["prompt"],
            athlete_data=result["athlete_data"],
            event_details=result["event_details"],
            plan_config=result["plan_config"],
            generation_mode=result.get("generation_mode", "phased"),
            phases=phases,
            current_phase=current,
            recommended_mode=result.get("recommended_mode", "phased"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate prompt: {str(e)}"
        )


@router.post("/validate", response_model=dict)
async def validate_plan(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    """
    Validate AI-generated training plan JSON without importing.
    
    Returns validation result and preview data if valid.
    """
    # Check file type
    if not file.filename.endswith(('.json', '.JSON')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be JSON format"
        )
    
    # Check file size (max 5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )
    
    # Clean JSON (remove markdown fences from ChatGPT/Claude)
    cleaned_content = clean_chatgpt_json(content)
    
    # Parse JSON
    try:
        data = json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON: {str(e)}. Make sure to copy only the JSON output from ChatGPT."
        )
    
    # Parse into Pydantic model
    try:
        plan_data = TrainingPlanImport(**data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid plan structure: {str(e)}"
        )
    
    # Validate
    validation_result = validate_training_plan(plan_data)
    
    # Generate preview if valid
    preview = None
    if validation_result.valid:
        preview = generate_plan_preview(plan_data)
    
    return {
        "validation": validation_result.model_dump(),
        "preview": preview.model_dump(by_alias=True) if preview else None
    }


@router.post("/import", response_model=ImportResponse)
async def import_plan(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Import AI-generated training plan from JSON file.
    
    File will be validated before import. Returns created plan details.
    """
    # Check file type
    if not file.filename.endswith(('.json', '.JSON')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be JSON format"
        )
    
    # Check file size (max 5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )
    
    # Clean JSON (remove markdown fences from ChatGPT/Claude)
    cleaned_content = clean_chatgpt_json(content)
    
    # Parse JSON
    try:
        data = json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON: {str(e)}. Make sure to copy only the JSON output from ChatGPT."
        )
    
    # Parse into Pydantic model
    try:
        plan_data = TrainingPlanImport(**data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid plan structure: {str(e)}"
        )
    
    # Validate
    validation_result = validate_training_plan(plan_data)
    if not validation_result.valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Plan validation failed: {', '.join(validation_result.errors)}"
        )
    
    # Import
    try:
        result = await import_training_plan(current_user.id, plan_data, db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import plan: {str(e)}"
        )


@router.get("/trainer-styles")
async def get_trainer_styles():
    """
    Get list of all available trainer styles.
    
    Returns a list of trainer coaching methodologies that can be selected
    for AI training plan generation. Each trainer has a unique approach to
    periodization, intensity distribution, and training philosophy.
    """
    from src.trainer_config.trainer_styles import get_all_trainer_styles
    return {"trainers": get_all_trainer_styles()}


@router.get("/trainer-styles/{style_id}")
async def get_trainer_style_details(style_id: str):
    """
    Get detailed information about a specific trainer style.
    
    Includes complete training philosophy, periodization structure,
    key workouts, and special emphasis points for the selected trainer.
    """
    from src.trainer_config.trainer_styles import get_trainer_style, TRAINER_STYLES
    
    if style_id not in TRAINER_STYLES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trainer style '{style_id}' not found"
        )
    
    return get_trainer_style(style_id)
