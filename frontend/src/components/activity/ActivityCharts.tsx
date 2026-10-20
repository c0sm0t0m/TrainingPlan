/**
 * Sport-aware time-series charts for a single activity (pace/speed, power, HR, elevation).
 * Bike: power over time is always shown first — no tabs to hunt for.
 */
import React, { useEffect, useMemo, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  ToggleButton,
  ToggleButtonGroup,
  FormControlLabel,
  Switch,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceArea,
  Cell,
} from 'recharts';
import api from '../../services/api';
import { isCyclingSport, isRunningSport } from '../../utils/sportTypes';

interface StreamsPayload {
  activity_id: number;
  total_samples: number;
  streams: {
    timestamps: string[];
    distance_meters?: (number | null)[];
    pace_min_per_km?: (number | null)[];
    heart_rate_bpm?: (number | null)[];
    power_watts?: (number | null)[];
    cadence?: (number | null)[];
    elevation_meters?: (number | null)[];
    speed_mps?: (number | null)[];
  };
}

interface LapSplit {
  lap_number: number;
  distance_meters: number;
  duration_seconds: number;
  average_speed_mps?: number | null;
  average_hr?: number | null;
  average_power?: number | null;
}

interface Props {
  activityId: number;
  activityType: string;
}

type XMode = 'distance' | 'time';

function formatPace(minPerKm: number): string {
  if (!Number.isFinite(minPerKm) || minPerKm <= 0) return '—';
  const min = Math.floor(minPerKm);
  const sec = Math.round((minPerKm - min) * 60);
  return `${min}:${String(sec).padStart(2, '0')}`;
}

function formatElapsed(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  if (m >= 60) {
    const h = Math.floor(m / 60);
    return `${h}:${String(m % 60).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }
  return `${m}:${String(s).padStart(2, '0')}`;
}

function detectEffortBands(
  data: { x: number; power?: number | null; pace?: number | null }[],
  mode: 'power' | 'pace'
): { x1: number; x2: number }[] {
  if (data.length < 20) return [];
  const values = data
    .map((d) => (mode === 'power' ? d.power : d.pace))
    .filter((v): v is number => v != null && Number.isFinite(v) && v > 0);
  if (values.length < 20) return [];

  const sorted = [...values].sort((a, b) => a - b);
  const threshold =
    mode === 'power'
      ? sorted[Math.floor(sorted.length * 0.75)]
      : sorted[Math.floor(sorted.length * 0.25)];

  const isHard = (d: (typeof data)[0]) => {
    if (mode === 'power') return d.power != null && d.power >= threshold;
    return d.pace != null && d.pace > 0 && d.pace <= threshold;
  };

  const bands: { x1: number; x2: number }[] = [];
  let start: number | null = null;
  for (let i = 0; i < data.length; i++) {
    if (isHard(data[i])) {
      if (start == null) start = data[i].x;
    } else if (start != null) {
      const end = data[i - 1]?.x ?? start;
      if (end > start) bands.push({ x1: start, x2: end });
      start = null;
    }
  }
  if (start != null) {
    bands.push({ x1: start, x2: data[data.length - 1].x });
  }

  const span = data[data.length - 1].x - data[0].x;
  const minWidth = span * 0.02;
  return bands.filter((b) => b.x2 - b.x1 >= minWidth).slice(0, 12);
}

function buildKmSplits(
  distances: (number | null)[],
  speeds: (number | null)[],
  powers: (number | null)[],
  cycling: boolean
): { km: number; pace?: number; speedKmh?: number; power?: number }[] {
  const n = Math.min(distances.length, speeds.length || distances.length);
  if (n < 10) return [];

  type Bucket = { speedSum: number; speedN: number; powerSum: number; powerN: number };
  const buckets = new Map<number, Bucket>();

  for (let i = 0; i < n; i++) {
    const d = distances[i];
    if (d == null || d < 0) continue;
    const kmIdx = Math.floor(d / 1000) + 1;
    if (kmIdx < 1 || kmIdx > 200) continue;
    let b = buckets.get(kmIdx);
    if (!b) {
      b = { speedSum: 0, speedN: 0, powerSum: 0, powerN: 0 };
      buckets.set(kmIdx, b);
    }
    const spd = speeds[i];
    if (spd != null && spd > 0) {
      b.speedSum += spd;
      b.speedN += 1;
    }
    const pwr = powers[i];
    if (pwr != null && pwr > 0) {
      b.powerSum += pwr;
      b.powerN += 1;
    }
  }

  return Array.from(buckets.entries())
    .sort((a, b) => a[0] - b[0])
    .map(([km, b]) => {
      const avgSpeed = b.speedN > 0 ? b.speedSum / b.speedN : null;
      return {
        km,
        pace: !cycling && avgSpeed ? (1000 / avgSpeed) / 60 : undefined,
        speedKmh: cycling && avgSpeed ? avgSpeed * 3.6 : undefined,
        power: b.powerN > 0 ? Math.round(b.powerSum / b.powerN) : undefined,
      };
    })
    .filter((row) => row.pace != null || row.speedKmh != null || row.power != null);
}

const ActivityCharts: React.FC<Props> = ({ activityId, activityType }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const cycling = isCyclingSport(activityType);
  const running = isRunningSport(activityType);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [streams, setStreams] = useState<StreamsPayload | null>(null);
  const [splits, setSplits] = useState<LapSplit[]>([]);
  const [xMode, setXMode] = useState<XMode>(() =>
    isCyclingSport(activityType) ? 'time' : 'distance'
  );
  const [showIntervals, setShowIntervals] = useState(false);
  const [weightKg, setWeightKg] = useState<number | null>(null);
  const [ftpWatts, setFtpWatts] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [streamsRes, splitsRes, meRes] = await Promise.all([
          api.get<StreamsPayload>(`/activities/${activityId}/streams`, { timeout: 120000 }),
          api.get<{ splits: LapSplit[] }>(`/activities/${activityId}/splits`).catch(() => ({ data: { splits: [] } })),
          api.get<{ weight_kg?: number | null; ftp?: number | null }>('/auth/me').catch(() => ({ data: {} })),
        ]);
        if (cancelled) return;
        setStreams(streamsRes.data);
        setSplits(splitsRes.data.splits || []);
        const w = meRes.data.weight_kg;
        setWeightKg(typeof w === 'number' && w > 0 ? w : null);
        const ftp = meRes.data.ftp;
        setFtpWatts(typeof ftp === 'number' && ftp > 0 ? ftp : null);
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load activity charts');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [activityId]);

  const series = useMemo(() => {
    if (!streams?.streams?.timestamps?.length) return [];
    const s = streams.streams;
    const t0 = new Date(s.timestamps[0]).getTime();
    const n = s.timestamps.length;
    const rows: {
      x: number;
      xLabel: string;
      pace: number | null;
      speedKmh: number | null;
      power: number | null;
      powerWkg: number | null;
      cadence: number | null;
      hr: number | null;
      elev: number | null;
    }[] = [];

    for (let i = 0; i < n; i++) {
      const dist = s.distance_meters?.[i] ?? null;
      const elapsedSec = Math.max(0, (new Date(s.timestamps[i]).getTime() - t0) / 1000);
      const useDist = xMode === 'distance' && dist != null && Number.isFinite(dist);
      if (xMode === 'distance' && !useDist) continue;
      const x = useDist ? dist / 1000 : elapsedSec;
      if (!Number.isFinite(x)) continue;
      const speed = s.speed_mps?.[i] ?? null;
      const paceRaw = s.pace_min_per_km?.[i] ?? null;
      const pace = paceRaw != null && paceRaw >= 2.5 && paceRaw <= 12 ? paceRaw : null;
      const rawPower = s.power_watts?.[i];
      const power =
        rawPower != null && Number.isFinite(Number(rawPower)) ? Number(rawPower) : null;
      const rawCad = s.cadence?.[i];
      const cadence =
        rawCad != null && Number.isFinite(Number(rawCad)) ? Number(rawCad) : null;
      rows.push({
        x,
        xLabel: useDist ? `${x.toFixed(2)} km` : formatElapsed(elapsedSec),
        pace: running || !cycling ? pace : null,
        speedKmh: speed != null && speed > 0 ? speed * 3.6 : null,
        power,
        powerWkg: power != null && weightKg ? power / weightKg : null,
        cadence,
        hr: s.heart_rate_bpm?.[i] ?? null,
        elev: s.elevation_meters?.[i] ?? null,
      });
    }
    return rows;
  }, [streams, xMode, cycling, running, weightKg]);

  const hasPower = series.some((d) => d.power != null && d.power > 0);
  const hasPace = series.some((d) => d.pace != null);
  const hasSpeed = series.some((d) => d.speedKmh != null);
  const hasHr = series.some((d) => d.hr != null);
  const hasElev = series.some((d) => d.elev != null);
  const hasCadence = series.some((d) => d.cadence != null);
  const hasWkg = Boolean(weightKg && hasPower);

  const powerSummary = useMemo(() => {
    if (!hasPower) return null;
    const vals = series.map((d) => d.power).filter((v): v is number => v != null && v > 0);
    if (!vals.length) return null;
    const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
    const max = Math.max(...vals);
    return { avg, max };
  }, [series, hasPower]);

  const cadenceSummary = useMemo(() => {
    if (!hasCadence) return null;
    // Ignore zeros (coasting) for average
    const vals = series.map((d) => d.cadence).filter((v): v is number => v != null && v > 0);
    if (!vals.length) return null;
    const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
    const max = Math.max(...vals);
    return { avg, max };
  }, [series, hasCadence]);

  const effortBands = useMemo(() => {
    if (!showIntervals || series.length === 0) return [];
    if (hasPower) return detectEffortBands(series, 'power');
    if (hasPace) return detectEffortBands(series, 'pace');
    return [];
  }, [series, showIntervals, hasPower, hasPace]);

  const kmSplits = useMemo(() => {
    if (!streams?.streams) return [];
    const s = streams.streams;
    if (s.distance_meters && s.speed_mps) {
      return buildKmSplits(s.distance_meters, s.speed_mps, s.power_watts || [], cycling);
    }
    return [];
  }, [streams, cycling]);

  const lapBars = useMemo(() => {
    if (!splits.length) return [];
    return splits.map((lap) => {
      const speed = lap.average_speed_mps;
      return {
        lap: lap.lap_number,
        pace: !cycling && speed && speed > 0 ? (1000 / speed) / 60 : undefined,
        speedKmh: cycling && speed && speed > 0 ? speed * 3.6 : undefined,
        power: lap.average_power ?? undefined,
        hr: lap.average_hr ?? undefined,
      };
    });
  }, [splits, cycling]);

  if (loading) {
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {cycling ? 'Power over time' : running ? 'Pace over time' : 'Session charts'}
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {cycling ? 'Power over time' : 'Session charts'}
          </Typography>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (!series.length) {
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {cycling ? 'Power over time' : 'Session charts'}
          </Typography>
          <Alert severity="info">
            No time-series data for this activity yet. Open again after Garmin FIT sync completes.
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const xLabel = xMode === 'distance' ? 'Distance (km)' : 'Elapsed time';
  const chartHeight = isMobile ? 280 : 320;
  const tooltipStyle = {
    backgroundColor: theme.palette.background.paper,
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: 8,
    fontSize: 12,
  };

  const title = cycling
    ? 'Power over time'
    : running
      ? 'Pace over time'
      : 'Session charts';

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 1,
            mb: 1.5,
          }}
        >
          <Typography variant="h5" fontWeight={700}>
            {title}
          </Typography>
          <ToggleButtonGroup
            size="small"
            exclusive
            value={xMode}
            onChange={(_, v) => v && setXMode(v)}
          >
            <ToggleButton value="time">By time</ToggleButton>
            <ToggleButton value="distance">By km</ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {cycling && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
            Orange = power (watts, left)
            {hasCadence ? ' · teal = cadence (rpm, right)' : ''}
            {hasWkg ? ' · W/kg in summary & tooltip' : ' · set weight in Settings for W/kg'}
          </Typography>
        )}

        {cycling && (hasPower || hasCadence) && (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 1.5 }}>
            {powerSummary && (
              <>
                <Typography variant="body2">
                  <strong>Avg</strong> {Math.round(powerSummary.avg)} W
                  {hasWkg ? ` · ${(powerSummary.avg / weightKg!).toFixed(2)} W/kg` : ''}
                </Typography>
                <Typography variant="body2">
                  <strong>Max</strong> {Math.round(powerSummary.max)} W
                  {hasWkg ? ` · ${(powerSummary.max / weightKg!).toFixed(2)} W/kg` : ''}
                </Typography>
              </>
            )}
            {cadenceSummary && (
              <Typography variant="body2">
                <strong>Cadence</strong> {Math.round(cadenceSummary.avg)} rpm avg
                {' · '}
                {Math.round(cadenceSummary.max)} max
              </Typography>
            )}
            {ftpWatts != null && (
              <Typography variant="body2" color="text.secondary">
                <strong>FTP</strong> {ftpWatts} W
                {hasWkg ? ` · ${(ftpWatts / weightKg!).toFixed(2)} W/kg` : ''}
              </Typography>
            )}
          </Box>
        )}

        {(hasPower || hasPace) && (
          <FormControlLabel
            control={
              <Switch
                size="small"
                checked={showIntervals}
                onChange={(_, checked) => setShowIntervals(checked)}
              />
            }
            label={
              <Typography variant="body2" color="text.secondary">
                Highlight harder sections
              </Typography>
            }
            sx={{ mb: 1 }}
          />
        )}

        {/* Primary chart — always visible */}
        <Box sx={{ width: '100%', height: chartHeight, minHeight: chartHeight }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={series} margin={{ top: 8, right: 16, left: 4, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
              <XAxis
                dataKey="x"
                type="number"
                domain={['dataMin', 'dataMax']}
                tick={{ fontSize: 11 }}
                tickFormatter={(v) =>
                  xMode === 'distance' ? Number(v).toFixed(0) : formatElapsed(Number(v))
                }
                label={{ value: xLabel, position: 'insideBottom', offset: -4, fontSize: 11 }}
              />
              {cycling && hasPower ? (
                <YAxis
                  yAxisId="primary"
                  tick={{ fontSize: 11 }}
                  domain={[0, 'auto']}
                  label={{ value: 'Watts', angle: -90, position: 'insideLeft', fontSize: 11 }}
                  width={52}
                />
              ) : hasPace ? (
                <YAxis
                  yAxisId="primary"
                  reversed
                  tick={{ fontSize: 11 }}
                  domain={['dataMin - 0.3', 'dataMax + 0.3']}
                  tickFormatter={(v) => formatPace(Number(v))}
                  label={{ value: 'Pace', angle: -90, position: 'insideLeft', fontSize: 11 }}
                  width={52}
                />
              ) : (
                <YAxis
                  yAxisId="primary"
                  tick={{ fontSize: 11 }}
                  domain={[0, 'auto']}
                  label={{ value: 'km/h', angle: -90, position: 'insideLeft', fontSize: 11 }}
                  width={52}
                />
              )}
              {cycling && hasCadence ? (
                <YAxis
                  yAxisId="cadence"
                  orientation="right"
                  tick={{ fontSize: 11 }}
                  domain={[0, 'auto']}
                  label={{ value: 'rpm', angle: 90, position: 'insideRight', fontSize: 11 }}
                  width={44}
                />
              ) : hasHr ? (
                <YAxis
                  yAxisId="hr"
                  orientation="right"
                  tick={{ fontSize: 11 }}
                  domain={['dataMin - 5', 'dataMax + 5']}
                  label={{ value: 'HR (bpm)', angle: 90, position: 'insideRight', fontSize: 11 }}
                  width={52}
                />
              ) : null}
              <Tooltip
                contentStyle={tooltipStyle}
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null;
                  const row = payload[0].payload as {
                    xLabel?: string;
                    power?: number | null;
                    powerWkg?: number | null;
                    cadence?: number | null;
                    hr?: number | null;
                    pace?: number | null;
                    speedKmh?: number | null;
                  };
                  return (
                    <Box sx={{ ...tooltipStyle, p: 1.25 }}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        {row.xLabel}
                      </Typography>
                      {row.power != null && (
                        <Typography variant="body2">
                          Power: {Math.round(row.power)} W
                          {row.powerWkg != null ? ` · ${row.powerWkg.toFixed(2)} W/kg` : ''}
                        </Typography>
                      )}
                      {row.cadence != null && (
                        <Typography variant="body2">
                          Cadence: {Math.round(row.cadence)} {cycling ? 'rpm' : 'spm'}
                        </Typography>
                      )}
                      {row.pace != null && (
                        <Typography variant="body2">Pace: {formatPace(row.pace)} /km</Typography>
                      )}
                      {row.speedKmh != null && !cycling && (
                        <Typography variant="body2">Speed: {row.speedKmh.toFixed(1)} km/h</Typography>
                      )}
                      {row.hr != null && (
                        <Typography variant="body2">HR: {Math.round(row.hr)} bpm</Typography>
                      )}
                    </Box>
                  );
                }}
              />
              <Legend />
              {showIntervals &&
                effortBands.map((b, i) => (
                  <ReferenceArea
                    key={`band-${i}`}
                    yAxisId="primary"
                    x1={b.x1}
                    x2={b.x2}
                    fill={theme.palette.warning.main}
                    fillOpacity={0.15}
                    strokeOpacity={0}
                  />
                ))}
              {cycling && hasPower && (
                <>
                  <Area
                    yAxisId="primary"
                    type="monotone"
                    dataKey="power"
                    name="Power (W)"
                    stroke={theme.palette.warning.dark}
                    fill={theme.palette.warning.main}
                    fillOpacity={0.35}
                    strokeWidth={2}
                    connectNulls
                    isAnimationActive={false}
                    baseValue={0}
                  />
                  <Line
                    yAxisId="primary"
                    type="monotone"
                    dataKey="power"
                    stroke={theme.palette.warning.dark}
                    strokeWidth={2.5}
                    dot={false}
                    connectNulls
                    isAnimationActive={false}
                    legendType="none"
                  />
                </>
              )}
              {cycling && hasCadence && (
                <Line
                  yAxisId="cadence"
                  type="monotone"
                  dataKey="cadence"
                  name="Cadence (rpm)"
                  stroke={theme.palette.info.dark}
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                  isAnimationActive={false}
                />
              )}
              {!cycling && hasPace && (
                <Line
                  yAxisId="primary"
                  type="monotone"
                  dataKey="pace"
                  name="Pace"
                  stroke={theme.palette.primary.main}
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                  isAnimationActive={false}
                />
              )}
              {((cycling && !hasPower) || (!cycling && !hasPace)) && hasSpeed && (
                <Line
                  yAxisId="primary"
                  type="monotone"
                  dataKey="speedKmh"
                  name="Speed"
                  stroke={theme.palette.info.main}
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                  isAnimationActive={false}
                />
              )}
              {hasHr && !(cycling && hasCadence) && (
                <Line
                  yAxisId="hr"
                  type="monotone"
                  dataKey="hr"
                  name="HR"
                  stroke={theme.palette.error.main}
                  strokeWidth={1.5}
                  dot={false}
                  connectNulls
                  isAnimationActive={false}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </Box>

        {cycling && !hasPower && (
          <Alert severity="warning" sx={{ mt: 1.5 }}>
            No power samples in this activity’s FIT stream (summary may still show avg/NP).
          </Alert>
        )}

        {/* Secondary charts — collapsed, no tabs */}
        {(hasSpeed && cycling) || kmSplits.length > 0 || lapBars.length > 1 || hasElev ? (
          <Box sx={{ mt: 2 }}>
            {cycling && hasSpeed && (
              <Accordion disableGutters elevation={0} sx={{ border: 1, borderColor: 'divider', mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography fontWeight={600}>Speed</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ width: '100%', height: 220 }}>
                    <ResponsiveContainer>
                      <ComposedChart data={series} margin={{ top: 8, right: 12, left: 4, bottom: 8 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                        <XAxis
                          dataKey="x"
                          type="number"
                          domain={['dataMin', 'dataMax']}
                          tick={{ fontSize: 11 }}
                          tickFormatter={(v) =>
                            xMode === 'distance' ? Number(v).toFixed(0) : formatElapsed(Number(v))
                          }
                        />
                        <YAxis tick={{ fontSize: 11 }} domain={[0, 'auto']} unit=" km/h" width={48} />
                        <Tooltip
                          contentStyle={tooltipStyle}
                          formatter={(value) =>
                            typeof value === 'number' ? [`${value.toFixed(1)} km/h`, 'Speed'] : ['—', 'Speed']
                          }
                        />
                        <Area
                          type="monotone"
                          dataKey="speedKmh"
                          stroke={theme.palette.info.main}
                          fill={theme.palette.info.light}
                          fillOpacity={0.35}
                          connectNulls
                          isAnimationActive={false}
                        />
                      </ComposedChart>
                    </ResponsiveContainer>
                  </Box>
                </AccordionDetails>
              </Accordion>
            )}

            {kmSplits.length > 0 && (
              <Accordion disableGutters elevation={0} sx={{ border: 1, borderColor: 'divider', mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography fontWeight={600}>
                    {cycling ? 'Power & speed per km' : 'Pace per km'}
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ width: '100%', height: 220 }}>
                    <ResponsiveContainer>
                      <BarChart data={kmSplits} margin={{ top: 8, right: 12, left: 4, bottom: 8 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} vertical={false} />
                        <XAxis dataKey="km" tick={{ fontSize: 11 }} />
                        {cycling ? (
                          <>
                            <YAxis yAxisId="speed" tick={{ fontSize: 11 }} width={40} />
                            {kmSplits.some((k) => k.power != null) && (
                              <YAxis yAxisId="power" orientation="right" tick={{ fontSize: 11 }} width={40} />
                            )}
                          </>
                        ) : (
                          <YAxis
                            reversed
                            tick={{ fontSize: 11 }}
                            tickFormatter={(v) => formatPace(Number(v))}
                            domain={['dataMin - 0.2', 'dataMax + 0.2']}
                            width={48}
                          />
                        )}
                        <Tooltip contentStyle={tooltipStyle} />
                        <Legend />
                        {cycling ? (
                          <>
                            <Bar yAxisId="speed" dataKey="speedKmh" name="Speed" fill={theme.palette.info.main} />
                            {kmSplits.some((k) => k.power != null) && (
                              <Bar yAxisId="power" dataKey="power" name="Power" fill={theme.palette.warning.main} />
                            )}
                          </>
                        ) : (
                          <Bar dataKey="pace" name="Pace">
                            {kmSplits.map((entry, index) => {
                              const paces = kmSplits.map((k) => k.pace!).filter(Boolean);
                              const avg = paces.reduce((a, b) => a + b, 0) / paces.length;
                              const faster = entry.pace != null && entry.pace < avg;
                              return (
                                <Cell
                                  key={`km-${index}`}
                                  fill={faster ? theme.palette.success.main : theme.palette.primary.main}
                                />
                              );
                            })}
                          </Bar>
                        )}
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </AccordionDetails>
              </Accordion>
            )}

            {lapBars.length > 1 && (
              <Accordion disableGutters elevation={0} sx={{ border: 1, borderColor: 'divider', mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography fontWeight={600}>Lap intervals</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ width: '100%', height: 200 }}>
                    <ResponsiveContainer>
                      <BarChart data={lapBars} margin={{ top: 8, right: 12, left: 4, bottom: 8 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} vertical={false} />
                        <XAxis dataKey="lap" tick={{ fontSize: 11 }} />
                        <YAxis tick={{ fontSize: 11 }} width={48} />
                        <Tooltip contentStyle={tooltipStyle} />
                        {cycling && lapBars.some((l) => l.power != null) ? (
                          <Bar dataKey="power" name="Power" fill={theme.palette.warning.main} />
                        ) : !cycling && lapBars.some((l) => l.pace != null) ? (
                          <Bar dataKey="pace" name="Pace" fill={theme.palette.primary.main} />
                        ) : (
                          <Bar dataKey="speedKmh" name="Speed" fill={theme.palette.info.main} />
                        )}
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </AccordionDetails>
              </Accordion>
            )}

            {hasElev && (
              <Accordion disableGutters elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography fontWeight={600}>Elevation</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ width: '100%', height: 180 }}>
                    <ResponsiveContainer>
                      <ComposedChart data={series} margin={{ top: 8, right: 12, left: 4, bottom: 8 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                        <XAxis
                          dataKey="x"
                          type="number"
                          domain={['dataMin', 'dataMax']}
                          tick={{ fontSize: 11 }}
                          tickFormatter={(v) =>
                            xMode === 'distance' ? Number(v).toFixed(0) : formatElapsed(Number(v))
                          }
                        />
                        <YAxis tick={{ fontSize: 11 }} unit=" m" width={40} />
                        <Tooltip contentStyle={tooltipStyle} />
                        <Area
                          type="monotone"
                          dataKey="elev"
                          stroke={theme.palette.success.dark}
                          fill={theme.palette.success.light}
                          fillOpacity={0.4}
                          connectNulls
                          isAnimationActive={false}
                        />
                      </ComposedChart>
                    </ResponsiveContainer>
                  </Box>
                </AccordionDetails>
              </Accordion>
            )}
          </Box>
        ) : null}
      </CardContent>
    </Card>
  );
};

export default ActivityCharts;
