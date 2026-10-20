/**
 * Coarse sport-family helpers — keep in sync with backend
 * `backend/src/utils/sport_types.py`.
 *
 * Important: Garmin uses `road_biking` (no "bike" substring — use "bik").
 */

export type SportFamily =
  | 'cycling'
  | 'running'
  | 'swimming'
  | 'strength'
  | 'walking'
  | 'triathlon'
  | 'other';

function normalizeKey(raw?: string | null): string {
  return (raw || '').toLowerCase().replace(/[_\-\s]/g, '');
}

export function normalizeSport(raw?: string | null): SportFamily {
  const s = normalizeKey(raw);
  if (['cycl', 'bik', 'ride', 'gravel', 'mtb', 'ebike', 'virtualride'].some((k) => s.includes(k))) {
    return 'cycling';
  }
  if (['run', 'trail', 'treadmill', 'virtualrun'].some((k) => s.includes(k))) {
    return 'running';
  }
  if (s.includes('swim') || s.includes('pool') || s.includes('openwater')) {
    return 'swimming';
  }
  if (['strength', 'weight', 'gym', 'fitness', 'crossfit'].some((k) => s.includes(k))) {
    return 'strength';
  }
  if (s.includes('walk') || s.includes('hike')) {
    return 'walking';
  }
  if (s.includes('tri') || s.includes('multisport')) {
    return 'triathlon';
  }
  return s ? 'other' : 'other';
}

export function isCyclingSport(raw?: string | null): boolean {
  return normalizeSport(raw) === 'cycling';
}

export function isRunningSport(raw?: string | null): boolean {
  return normalizeSport(raw) === 'running';
}
