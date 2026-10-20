/**
 * Instagram 4:5 share card for an activity.
 * Map tiles + GPS track as background, Eckdaten overlay, optional planned vs actual.
 */
import { forwardRef, useEffect, useRef, useState } from 'react';
import { Box, Typography } from '@mui/material';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';
import { renderShareMapDataUrl } from './renderShareMap';

export interface ShareTrackPoint {
  lat: number;
  lng: number;
}

export interface ShareMatchedWorkout {
  title: string;
  duration_minutes?: number;
  distance_km?: number;
  target_tss?: number;
}

export interface ActivityIgShareCardProps {
  activityName: string;
  activityType: string;
  startTimeLocal: string;
  durationSeconds?: number;
  distanceMeters?: number;
  calculatedTss?: number;
  trackPoints?: ShareTrackPoint[];
  matchedWorkout?: ShareMatchedWorkout | null;
  /** Pixel width of the card (height follows 4:5). Default 1080. */
  width?: number;
  onMapReady?: (ready: boolean) => void;
}

const CARD_RATIO = 5 / 4; // height / width for 4:5 portrait

function formatDuration(seconds?: number): string {
  if (!seconds) return '–';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }
  return `${minutes}:${String(secs).padStart(2, '0')}`;
}

function formatDistanceKm(meters?: number): string {
  if (!meters) return '–';
  return (meters / 1000).toFixed(2);
}

function sportLabel(activityType: string): string {
  const t = activityType.toLowerCase();
  if (t.includes('run')) return 'Run';
  if (t.includes('bik') || t.includes('cycl') || t.includes('ride')) return 'Bike';
  if (t.includes('swim')) return 'Swim';
  if (t.includes('strength') || t.includes('gym')) return 'Strength';
  return activityType;
}

function pctDelta(actual?: number, planned?: number): string | null {
  if (actual == null || planned == null || planned === 0) return null;
  const pct = Math.round(((actual - planned) / planned) * 100);
  if (pct === 0) return '±0%';
  return pct > 0 ? `+${pct}%` : `${pct}%`;
}

const ActivityIgShareCard = forwardRef<HTMLDivElement, ActivityIgShareCardProps>(
  function ActivityIgShareCard(
    {
      activityName: _activityName,
      activityType,
      startTimeLocal,
      durationSeconds,
      distanceMeters,
      calculatedTss,
      trackPoints = [],
      matchedWorkout,
      width = 1080,
      onMapReady,
    },
    ref
  ) {
    void _activityName;
    const height = Math.round(width * CARD_RATIO);
    const [mapUrl, setMapUrl] = useState<string | null>(null);
    const onMapReadyRef = useRef(onMapReady);
    onMapReadyRef.current = onMapReady;

    useEffect(() => {
      let cancelled = false;
      onMapReadyRef.current?.(false);
      if (!trackPoints.length) {
        setMapUrl(null);
        onMapReadyRef.current?.(true);
        return;
      }
      // Snapshot points so we don't depend on array identity churn
      const points = trackPoints.map((p) => ({ lat: p.lat, lng: p.lng }));
      renderShareMapDataUrl(points, width, height)
        .then((url) => {
          if (cancelled) return;
          setMapUrl(url);
          onMapReadyRef.current?.(true);
        })
        .catch(() => {
          if (cancelled) return;
          setMapUrl(null);
          onMapReadyRef.current?.(true);
        });
      return () => {
        cancelled = true;
      };
      // eslint-disable-next-line react-hooks/exhaustive-deps -- re-render when track length/ends change
    }, [trackPoints.length, trackPoints[0]?.lat, trackPoints[0]?.lng, trackPoints[trackPoints.length - 1]?.lat, trackPoints[trackPoints.length - 1]?.lng, width, height]);

    const dateLabel = format(new Date(startTimeLocal), 'EEEE, d. MMM yyyy', { locale: de });
    const actualDistKm = distanceMeters != null ? distanceMeters / 1000 : undefined;
    const actualDurMin = durationSeconds != null ? durationSeconds / 60 : undefined;
    const distDelta = pctDelta(actualDistKm, matchedWorkout?.distance_km);
    const durDelta = pctDelta(actualDurMin, matchedWorkout?.duration_minutes);
    const tssDelta = pctDelta(calculatedTss, matchedWorkout?.target_tss);
    const hasCompare = Boolean(matchedWorkout);

    return (
      <Box
        ref={ref}
        sx={{
          width,
          height,
          position: 'relative',
          overflow: 'hidden',
          borderRadius: 0,
          background: 'linear-gradient(165deg, #0f172a 0%, #1e293b 45%, #0f172a 100%)',
          color: '#f8fafc',
          fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif',
          boxSizing: 'border-box',
        }}
      >
        {mapUrl && (
          <Box
            component="img"
            src={mapUrl}
            alt=""
            sx={{
              position: 'absolute',
              inset: 0,
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              zIndex: 0,
            }}
          />
        )}

        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: height * 0.16,
            background: 'linear-gradient(180deg, rgba(15,23,42,0.55) 0%, transparent 100%)',
            zIndex: 1,
            pointerEvents: 'none',
          }}
        />

        <Box sx={{ position: 'absolute', top: width * 0.055, left: width * 0.06, zIndex: 2 }}>
          <Typography
            sx={{
              fontSize: width * 0.026,
              fontWeight: 600,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'rgba(248,250,252,0.85)',
            }}
          >
            Kinesis
          </Typography>
        </Box>

        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            zIndex: 2,
            px: `${width * 0.06}px`,
            // Extra bottom inset keeps Distanz/Dauer/TSS above IG chrome & mild crop
            pt: `${width * 0.08}px`,
            pb: `${width * 0.12}px`,
            background:
              'linear-gradient(180deg, transparent 0%, rgba(15,23,42,0.72) 18%, #0f172a 42%)',
          }}
        >
          <Typography
            sx={{
              fontSize: width * 0.022,
              color: 'rgba(248,250,252,0.55)',
              mb: `${width * 0.01}px`,
              textTransform: 'capitalize',
              lineHeight: 1.2,
            }}
          >
            {dateLabel}
          </Typography>
          <Typography
            sx={{
              fontSize: width * 0.062,
              fontWeight: 700,
              lineHeight: 1.05,
              mb: `${width * 0.028}px`,
            }}
          >
            {sportLabel(activityType)}
          </Typography>

          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              gap: `${width * 0.03}px`,
              mb: hasCompare ? `${width * 0.028}px` : 0,
            }}
          >
            <Metric
              width={width}
              value={formatDistanceKm(distanceMeters)}
              unit="km"
              label="Distanz"
            />
            <Metric
              width={width}
              value={formatDuration(durationSeconds)}
              unit=""
              label="Dauer"
            />
            <Metric
              width={width}
              value={calculatedTss != null ? Math.round(calculatedTss).toString() : '–'}
              unit=""
              label="TSS"
            />
          </Box>

          {hasCompare && matchedWorkout && (
            <Box
              sx={{
                pt: `${width * 0.022}px`,
                borderTop: '1px solid rgba(248,250,252,0.12)',
              }}
            >
              <Typography
                sx={{
                  fontSize: width * 0.02,
                  fontWeight: 600,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  color: 'rgba(248,250,252,0.45)',
                  mb: `${width * 0.014}px`,
                }}
              >
                Geplant → Ist
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: `${width * 0.008}px` }}>
                {matchedWorkout.distance_km != null && actualDistKm != null && (
                  <CompareRow
                    width={width}
                    label="km"
                    planned={matchedWorkout.distance_km.toFixed(1)}
                    actual={actualDistKm.toFixed(2)}
                    delta={distDelta}
                  />
                )}
                {matchedWorkout.duration_minutes != null && actualDurMin != null && (
                  <CompareRow
                    width={width}
                    label="min"
                    planned={Math.round(matchedWorkout.duration_minutes).toString()}
                    actual={Math.round(actualDurMin).toString()}
                    delta={durDelta}
                  />
                )}
                {matchedWorkout.target_tss != null && calculatedTss != null && (
                  <CompareRow
                    width={width}
                    label="TSS"
                    planned={Math.round(matchedWorkout.target_tss).toString()}
                    actual={Math.round(calculatedTss).toString()}
                    delta={tssDelta}
                  />
                )}
              </Box>
            </Box>
          )}
        </Box>
      </Box>
    );
  }
);

function Metric({
  width,
  value,
  unit,
  label,
}: {
  width: number;
  value: string;
  unit: string;
  label: string;
}) {
  return (
    <Box sx={{ flex: 1, minWidth: 0 }}>
      <Box sx={{ display: 'flex', alignItems: 'baseline', gap: `${width * 0.006}px`, flexWrap: 'nowrap' }}>
        <Typography
          sx={{
            fontSize: width * 0.048,
            fontWeight: 700,
            lineHeight: 1,
            whiteSpace: 'nowrap',
          }}
        >
          {value}
        </Typography>
        {unit && (
          <Typography sx={{ fontSize: width * 0.022, color: 'rgba(248,250,252,0.5)', flexShrink: 0 }}>
            {unit}
          </Typography>
        )}
      </Box>
      <Typography
        sx={{
          fontSize: width * 0.02,
          color: 'rgba(248,250,252,0.45)',
          mt: `${width * 0.01}px`,
          letterSpacing: '0.02em',
        }}
      >
        {label}
      </Typography>
    </Box>
  );
}

function CompareRow({
  width,
  label,
  planned,
  actual,
  delta,
}: {
  width: number;
  label: string;
  planned: string;
  actual: string;
  delta: string | null;
}) {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: width * 0.026,
      }}
    >
      <Typography sx={{ fontSize: 'inherit', color: 'rgba(248,250,252,0.45)', width: width * 0.12 }}>
        {label}
      </Typography>
      <Typography sx={{ fontSize: 'inherit', color: 'rgba(248,250,252,0.65)', flex: 1 }}>
        {planned} → {actual}
      </Typography>
      {delta && (
        <Typography
          sx={{
            fontSize: 'inherit',
            fontWeight: 600,
            color: delta.startsWith('+')
              ? '#fbbf24'
              : delta.startsWith('−') || delta.startsWith('-')
                ? '#86efac'
                : 'rgba(248,250,252,0.55)',
          }}
        >
          {delta}
        </Typography>
      )}
    </Box>
  );
}

export default ActivityIgShareCard;
