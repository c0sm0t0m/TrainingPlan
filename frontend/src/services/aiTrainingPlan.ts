/**
 * AI Training Plan API Service
 */
import api from './api';

export interface PromptGenerationConfig {
  targetEventId?: number;
  eventName?: string;
  eventDate?: string;
  eventDistance?: string;
  goalTime?: string;
  startDate: string;
  trainingDaysPerWeek: number;
  preferredTrainingDays: string[];
  trainerStyle: string;
  customTrainerInstructions?: string;
  additionalNotes?: string;
}

export interface TrainerStyle {
  id: string;
  name: string;
  tagline: string;
  description: string;
}

export interface TrainerStyleDetail extends TrainerStyle {
  philosophy: string;
  training_distribution: Record<string, string>;
  key_workouts: string[];
  periodization_structure: Record<string, string>;
  recovery_strategy: string;
  special_emphasis: string[];
}

export interface PromptGenerationResponse {
  prompt: string;
  athleteData: any;
  eventDetails: any;
  planConfig: any;
}

export interface ValidationResponse {
  validation: {
    valid: boolean;
    errors: string[];
    warnings: string[];
  };
  preview: {
    name: string;
    startDate: string;
    endDate: string;
    sportType: string;
    weeks: number;
    totalWorkouts: number;
    totalDistanceKm: number;
    totalTss: number;
    workoutTypeBreakdown: Record<string, number>;
  } | null;
}

export interface ImportResponse {
  planId: number;
  name: string;
  workoutsCreated: number;
  message: string;
}

/**
 * Generate AI prompt for training plan creation
 */
export const generateAIPrompt = async (
  config: PromptGenerationConfig
): Promise<PromptGenerationResponse> => {
  const response = await api.post('/ai-training-plan/generate-prompt', config, {
    timeout: 30000, // 30 seconds for AI prompt generation (needs to fetch activities)
  });
  return response.data;
};

/**
 * Validate AI-generated training plan JSON
 */
export const validateAIPlan = async (file: File): Promise<ValidationResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/ai-training-plan/validate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

/**
 * Import AI-generated training plan
 */
export const importAIPlan = async (file: File): Promise<ImportResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/ai-training-plan/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

/**
 * Get all available trainer styles
 */
export const getTrainerStyles = async (): Promise<TrainerStyle[]> => {
  console.log('[aiTrainingPlan Service] Calling GET /ai-training-plan/trainer-styles');
  const response = await api.get('/ai-training-plan/trainer-styles');
  console.log('[aiTrainingPlan Service] Response received:', response.data);
  console.log('[aiTrainingPlan Service] Trainers array:', response.data.trainers);
  return response.data.trainers;
};

/**
 * Get detailed information about a specific trainer style
 */
export const getTrainerStyleDetails = async (styleId: string): Promise<TrainerStyleDetail> => {
  const response = await api.get(`/ai-training-plan/trainer-styles/${styleId}`);
  return response.data;
};
