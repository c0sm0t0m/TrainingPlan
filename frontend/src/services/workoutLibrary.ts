import api from './api';

export interface WorkoutTemplateSummary {
  id: string;
  name: string;
  category?: string;
  description?: string;
  sportType: string;
  workoutType?: string;
  durationMinutes?: number;
  intensityZone?: string;
  targetTSS?: number;
  stepCount: number;
}

export interface LibraryPreferences {
  enabled_ids: string[] | null;
  using_defaults: boolean;
  default_ids: string[];
}

export interface ScheduleTemplateResult {
  workout_id: number;
  plan_id: number;
  date: string;
  title: string;
  icu_synced: boolean;
  icu_message?: string | null;
}

export async function listWorkoutTemplates(options?: {
  category?: string;
  forCalendar?: boolean;
}): Promise<WorkoutTemplateSummary[]> {
  const { data } = await api.get('/workout-library/templates', {
    params: {
      ...(options?.category ? { category: options.category } : {}),
      ...(options?.forCalendar ? { for_calendar: true } : {}),
    },
  });
  return data;
}

export async function getLibraryPreferences(): Promise<LibraryPreferences> {
  const { data } = await api.get('/workout-library/preferences');
  return data;
}

export async function updateLibraryPreferences(
  enabledIds: string[]
): Promise<LibraryPreferences> {
  const { data } = await api.put('/workout-library/preferences', {
    enabled_ids: enabledIds,
  });
  return data;
}

export async function scheduleWorkoutTemplate(
  templateId: string,
  payload: { date: string; plan_id?: number; sync_to_icu?: boolean }
): Promise<ScheduleTemplateResult> {
  const { data } = await api.post(`/workout-library/templates/${templateId}/schedule`, payload);
  return data;
}
