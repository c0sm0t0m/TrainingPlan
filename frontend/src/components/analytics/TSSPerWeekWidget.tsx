import { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
  useTheme,
  useMediaQuery,
  Skeleton,
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer, Cell } from 'recharts';
import { FitnessCenter } from '@mui/icons-material';
import api from '../../services/api';

interface TSSPerWeekWidgetProps {
  daysBack?: number;
}

interface WeeklyTSSDataPoint {
  week_start: string;
  week_end: string;
  total_tss: number;
  activity_count: number;
}

interface WeeklyTSSResponse {
  data_points: WeeklyTSSDataPoint[];
  date_range_start: string;
  date_range_end: string;
}

export default function TSSPerWeekWidget({ daysBack = 90 }: TSSPerWeekWidgetProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<WeeklyTSSDataPoint[]>([]);

  useEffect(() => {
    fetchData();
  }, [daysBack]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.get<WeeklyTSSResponse>(`/analytics/tss-per-week?days_back=${daysBack}`);
      setData(response.data.data_points);
      
      setLoading(false);
    } catch (err: any) {
      console.error('Error fetching TSS per week data:', err);
      setError(err.response?.data?.detail || 'Failed to load TSS data');
      setLoading(false);
    }
  };

  // Format week label
  const formatWeekLabel = (weekStart: string) => {
    const date = new Date(weekStart);
    const month = date.toLocaleDateString('en-US', { month: 'short' });
    const day = date.getDate();
    return `${month} ${day}`;
  };

  // Prepare chart data
  const chartData = data.map(point => ({
    week: formatWeekLabel(point.week_start),
    tss: point.total_tss,
    activities: point.activity_count
  }));

  // Color based on TSS value (Friel guidance: <400 light, 400-650 moderate, >650 heavy)
  const getBarColor = (tss: number) => {
    if (tss < 400) return theme.palette.success.main;
    if (tss < 650) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  if (loading) {
    return (
      <Paper sx={{ p: { xs: 2, sm: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Skeleton variant="circular" width={32} height={32} />
          <Skeleton variant="text" width={200} height={32} />
        </Box>
        <Skeleton variant="rectangular" height={300} />
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: { xs: 2, sm: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <FitnessCenter sx={{ color: 'primary.main', fontSize: 32 }} />
          <Typography variant="h6">TSS per Week</Typography>
        </Box>
        <Alert severity="error">{error}</Alert>
      </Paper>
    );
  }

  if (data.length === 0) {
    return (
      <Paper sx={{ p: { xs: 2, sm: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <FitnessCenter sx={{ color: 'primary.main', fontSize: 32 }} />
          <Typography variant="h6">TSS per Week</Typography>
        </Box>
        <Alert severity="info">No TSS data available for this time range</Alert>
      </Paper>
    );
  }

  // Calculate stats
  const totalTSS = data.reduce((sum, point) => sum + point.total_tss, 0);
  const avgTSS = totalTSS / data.length;
  const maxTSS = Math.max(...data.map(p => p.total_tss));

  return (
    <Paper sx={{ p: { xs: 2, sm: 3 } }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <FitnessCenter sx={{ color: 'primary.main', fontSize: 32 }} />
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6">TSS per Week</Typography>
          <Typography variant="caption" color="text.secondary">
            Training Stress Score aggregated by week
          </Typography>
        </Box>
      </Box>

      {/* Summary Stats */}
      <Box sx={{ 
        display: 'flex', 
        gap: 2, 
        mb: 3,
        flexWrap: 'wrap'
      }}>
        <Box sx={{ 
          flex: 1, 
          minWidth: { xs: '45%', sm: 'auto' },
          bgcolor: 'background.default',
          p: 2,
          borderRadius: 1
        }}>
          <Typography variant="caption" color="text.secondary">Average TSS</Typography>
          <Typography variant="h6">{avgTSS.toFixed(0)}</Typography>
        </Box>
        <Box sx={{ 
          flex: 1, 
          minWidth: { xs: '45%', sm: 'auto' },
          bgcolor: 'background.default',
          p: 2,
          borderRadius: 1
        }}>
          <Typography variant="caption" color="text.secondary">Peak Week</Typography>
          <Typography variant="h6">{maxTSS.toFixed(0)}</Typography>
        </Box>
      </Box>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={isMobile ? 250 : 300}>
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: isMobile ? 40 : 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis 
            dataKey="week" 
            stroke={theme.palette.text.secondary}
            angle={isMobile ? -45 : 0}
            textAnchor={isMobile ? 'end' : 'middle'}
            height={isMobile ? 60 : 30}
            tick={{ fontSize: isMobile ? 10 : 12, fill: theme.palette.text.secondary }}
          />
          <YAxis 
            stroke={theme.palette.text.secondary}
            label={{ 
              value: 'TSS', 
              angle: -90, 
              position: 'insideLeft',
              style: { fill: theme.palette.text.secondary }
            }}
            tick={{ fontSize: 12, fill: theme.palette.text.secondary }}
          />
          <ChartTooltip
            contentStyle={{
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: '4px',
              color: theme.palette.text.primary,
            }}
            labelStyle={{ color: theme.palette.text.primary }}
            itemStyle={{ color: theme.palette.text.primary }}
            formatter={(value: any, name: string) => {
              if (name === 'tss') return [value, 'TSS'];
              if (name === 'activities') return [value, 'Activities'];
              return [value, name];
            }}
          />
          <Bar dataKey="tss" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.tss)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        gap: 3, 
        mt: 2,
        flexWrap: 'wrap'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 12, height: 12, bgcolor: theme.palette.success.main, borderRadius: 1 }} />
          <Typography variant="caption" color="text.secondary">Light (&lt;400)</Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 12, height: 12, bgcolor: theme.palette.warning.main, borderRadius: 1 }} />
          <Typography variant="caption" color="text.secondary">Moderate (400-650)</Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 12, height: 12, bgcolor: theme.palette.error.main, borderRadius: 1 }} />
          <Typography variant="caption" color="text.secondary">Heavy (&gt;650)</Typography>
        </Box>
      </Box>
    </Paper>
  );
}
