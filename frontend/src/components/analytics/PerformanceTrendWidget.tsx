/**
 * Year / multi-month performance trend: run pace or bike NP by week.
 */
import { useEffect, useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
  ToggleButton,
  ToggleButtonGroup,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';
import {
  ComposedChart,
  Line,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import api from '../../services/api';

interface PerformanceTrendPoint {
  week_start: string;
  activity_count: number;
  best_value: number | null;
  avg_value: number | null;
  rolling_avg: number | null;
  metric: string;
  best_activity_id?: number | null;
  best_activity_name?: string | null;
}

interface PerformanceTrendsResponse {
  sport: string;
  metric: string;
  metric_label: string;
  data_points: PerformanceTrendPoint[];
  trend_direction: 'improving' | 'declining' | 'stable' | null;
  trend_pct: number | null;
}

interface Props {
  daysBack?: number;
}

function formatPace(minPerKm: number): string {
  const min = Math.floor(minPerKm);
  const sec = Math.round((minPerKm - min) * 60);
  return `${min}:${String(sec).padStart(2, '0')}`;
}

export default function PerformanceTrendWidget({ daysBack = 365 }: Props) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [sport, setSport] = useState<'running' | 'cycling'>('running');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<PerformanceTrendsResponse | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.get<PerformanceTrendsResponse>('/analytics/performance-trends', {
          params: { sport, days_back: daysBack },
        });
        setData(res.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load performance trends');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [sport, daysBack]);

  const isPace = data?.metric === 'pace_min_per_km';

  const chartData =
    data?.data_points
      .filter((p) => p.avg_value != null || p.best_value != null || p.rolling_avg != null)
      .map((p) => ({
        ...p,
        timestamp: new Date(p.week_start).getTime(),
        label: new Date(p.week_start).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      })) ?? [];

  const TrendIcon =
    data?.trend_direction === 'improving'
      ? TrendingUp
      : data?.trend_direction === 'declining'
        ? TrendingDown
        : TrendingFlat;

  const trendColor =
    data?.trend_direction === 'improving'
      ? theme.palette.success.main
      : data?.trend_direction === 'declining'
        ? theme.palette.error.main
        : theme.palette.text.secondary;

  return (
    <Paper sx={{ p: { xs: 2, sm: 3 } }}>
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 1.5,
          mb: 1,
        }}
      >
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Performance Trend
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Weekly best & average {sport === 'running' ? 'pace' : 'normalized power'} over the selected range
          </Typography>
        </Box>
        <ToggleButtonGroup
          size="small"
          exclusive
          value={sport}
          onChange={(_, v) => v && setSport(v)}
        >
          <ToggleButton value="running">Run</ToggleButton>
          <ToggleButton value="cycling">Bike</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {data?.trend_direction && data.trend_pct != null && (
        <Chip
          icon={<TrendIcon sx={{ color: `${trendColor} !important` }} />}
          label={
            data.trend_direction === 'stable'
              ? 'Stable vs earlier half of period'
              : `${data.trend_direction === 'improving' ? 'Improving' : 'Declining'} ${Math.abs(data.trend_pct)}% vs earlier half`
          }
          size="small"
          sx={{ mb: 2, borderColor: trendColor, color: trendColor }}
          variant="outlined"
        />
      )}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {error && <Alert severity="error">{error}</Alert>}

      {!loading && !error && chartData.length === 0 && (
        <Alert severity="info">
          Not enough {sport} sessions with {sport === 'running' ? 'pace' : 'power'} data in this range.
        </Alert>
      )}

      {!loading && !error && chartData.length > 0 && (
        <Box sx={{ width: '100%', height: isMobile ? 280 : 340, mt: 1 }}>
          <ResponsiveContainer>
            <ComposedChart data={chartData} margin={{ top: 8, right: 12, left: 4, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
              <XAxis
                dataKey="timestamp"
                type="number"
                domain={['dataMin', 'dataMax']}
                tick={{ fontSize: 11 }}
                tickFormatter={(ts) => {
                  const d = new Date(ts);
                  return `${d.getMonth() + 1}/${d.getDate()}`;
                }}
                angle={isMobile ? -35 : 0}
                textAnchor={isMobile ? 'end' : 'middle'}
                height={isMobile ? 50 : 30}
              />
              <YAxis
                tick={{ fontSize: 11 }}
                reversed={isPace}
                domain={isPace ? ['dataMin - 0.15', 'dataMax + 0.15'] : [0, 'auto']}
                tickFormatter={(v) => (isPace ? formatPace(Number(v)) : `${Math.round(Number(v))}`)}
                label={{
                  value: isPace ? 'min/km' : 'W',
                  angle: -90,
                  position: 'insideLeft',
                  fontSize: 11,
                }}
                width={48}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: theme.palette.background.paper,
                  border: `1px solid ${theme.palette.divider}`,
                  borderRadius: 8,
                }}
                labelFormatter={(ts) =>
                  new Date(Number(ts)).toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                  })
                }
                formatter={(value, name) => {
                  const label = name ?? '';
                  if (value == null || typeof value !== 'number') return ['—', label];
                  if (isPace) return [formatPace(value), label];
                  return [`${Math.round(value)} W`, label];
                }}
              />
              <Legend />
              <Scatter
                dataKey="best_value"
                name="Best week"
                fill={theme.palette.primary.main}
                fillOpacity={0.85}
              />
              <Line
                type="monotone"
                dataKey="avg_value"
                name="Weekly avg"
                stroke={theme.palette.info.main}
                strokeWidth={1.5}
                dot={false}
                connectNulls
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="rolling_avg"
                name="4-wk avg"
                stroke={theme.palette.warning.dark}
                strokeWidth={2.5}
                dot={false}
                connectNulls
                isAnimationActive={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </Box>
      )}
    </Paper>
  );
}
