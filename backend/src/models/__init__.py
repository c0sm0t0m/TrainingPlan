"""Init package markers"""
from src.models.user import User
from src.models.training_plan import TrainingPlan, Workout
from src.models.garmin_activity import GarminActivity

__all__ = ["User", "TrainingPlan", "Workout", "GarminActivity"]

