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
  generationMode?: 'full' | 'phased';
  phaseIndex?: number;
}

export interface PlanPhaseInfo {
  index: number;
  id: string;
  name: string;
  focus: string;
  weekStart: number;
  weekEnd: number;
  weeks: number;
  startDate: string;
  endDate: string;
  isLast: boolean;
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
  generationMode: 'full' | 'phased';
  phases: PlanPhaseInfo[];
  currentPhase: PlanPhaseInfo | null;
  recommendedMode: 'full' | 'phased';
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
 * Merge multiple phase JSON plan files into one trainingPlan document.
 */
export function mergePhasePlanFiles(parsedPlans: any[]): any {
  if (!parsedPlans.length) {
    throw new Error('No plans to merge');
  }

  const roots = parsedPlans.map((p) => p.trainingPlan || p);
  const allWorkouts = roots.flatMap((r) => r.workouts || []);
  if (!allWorkouts.length) {
    throw new Error('Merged plans contain no workouts');
  }

  allWorkouts.sort((a, b) => String(a.date).localeCompare(String(b.date)));

  const startDates = roots.map((r) => r.startDate).filter(Boolean);
  const endDates = roots.map((r) => r.endDate).filter(Boolean);
  const startDate = startDates.sort()[0];
  const endDate = endDates.sort().slice(-1)[0];

  const baseName = (roots[0].name || 'Training Plan').replace(/\s*[—-]\s*Phase.*/i, '').trim();
  const targetEvent = roots.find((r) => r.targetEvent)?.targetEvent;
  const sportType = roots.find((r) => r.sportType)?.sportType || 'triathlon';

  return {
    trainingPlan: {
      name: roots.length > 1 ? `${baseName} (merged)` : roots[0].name,
      description: roots
        .map((r) => r.description)
        .filter(Boolean)
        .join(' ')
        .slice(0, 2000) || `Merged ${roots.length} phase files`,
      startDate,
      endDate,
      sportType,
      targetEvent,
      workouts: allWorkouts,
    },
  };
}

/**
 * Generate AI prompt for training plan creation
 */
export const generateAIPrompt = async (
  config: PromptGenerationConfig
): Promise<PromptGenerationResponse> => {
  const response = await api.post('/ai-training-plan/generate-prompt', config, {
    timeout: 30000,
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
  const response = await api.get('/ai-training-plan/trainer-styles');
  return response.data.trainers;
};

/**
 * Get detailed information about a specific trainer style
 */
export const getTrainerStyleDetails = async (styleId: string): Promise<TrainerStyleDetail> => {
  const response = await api.get(`/ai-training-plan/trainer-styles/${styleId}`);
  return response.data;
};
