"""
Configuration package for Kinesis backend.
"""
# Import from config.py (which exists in parent src/ directory, not this package)
# We need to be careful here - config.py is at src/config.py, not src/config/config.py

# Import trainer styles from this package
from .trainer_styles import (
    TRAINER_STYLES,
    get_all_trainer_styles,
    get_trainer_style,
    build_trainer_specific_prompt,
    get_detailed_workout_instructions
)

__all__ = [
    'TRAINER_STYLES',
    'get_all_trainer_styles',
    'get_trainer_style',
    'build_trainer_specific_prompt',
    'get_detailed_workout_instructions'
]
