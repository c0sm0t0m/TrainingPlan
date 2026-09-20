import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  useTheme,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import api from '@/services/api';

interface ThresholdDataPoint {
  date: string;
  threshold_hr: number | null;
  threshold_pace: number | null;
  is_interpolated?: boolean;
  is_from_key_session?: boolean;
}

interface ThresholdTrendsResponse {
  data_points: ThresholdDataPoint[];
  date_range_start: string;
  date_range_end: string;
}

interface Props {
  sport?: string;
  daysBack?: number;
}

const ThresholdHRTrendChart: React.FC<Props> = ({ 
  sport = 'running', 
  daysBack = 90 
}) => {
  const theme = useTheme();
  const [data, setData] = useState<ThresholdDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, [sport, daysBack]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get<ThresholdTrendsResponse>(
        `/analytics/threshold-trends`,
        {
          params: {
            sport,
            days_back: daysBack,
          },
        }
      );

      setData(response.data.data_points);
    } catch (err: any) {
      console.error('Error fetching threshold HR trends:', err);
      setError(err.response?.data?.detail || 'Failed to load threshold HR trends');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  // Calculate date range based on daysBack
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - daysBack);
  
  const minTimestamp = startDate.getTime();
  const maxTimestamp = endDate.getTime();

  // Filter data to only include points with HR data and add timestamp
  const chartData = data
    .filter(d => d.threshold_hr !== null)
    .map(d => ({
      date: d.date,
      timestamp: new Date(d.date).getTime(),
      hr: d.threshold_hr,
      isInterpolated: d.is_interpolated || false,
      isFromKeySession: d.is_from_key_session || false,
    }));

  if (chartData.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Threshold Heart Rate Trend
          </Typography>
          <Alert severity="info">
            No threshold HR data available for the selected time range.
            Complete more key training sessions to see trends.
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Threshold Heart Rate Trend
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Weekly threshold derived from key sessions with interpolation
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, mt: 1, mb: 2, flexWrap: 'wrap' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: theme.palette.error.main, border: `2px solid ${theme.palette.background.paper}` }} />
            <Typography variant="caption">Key Session</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: theme.palette.background.paper, border: `2px solid ${theme.palette.error.main}` }} />
            <Typography variant="caption">Interpolated</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: theme.palette.warning.main, border: `2px solid ${theme.palette.background.paper}` }} />
            <Typography variant="caption">Current Setting</Typography>
          </Box>
        </Box>
        
        <Box sx={{ width: '100%', height: 300, mt: 2 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
              <XAxis 
                dataKey="timestamp"
                type="number"
                domain={[minTimestamp, maxTimestamp]}
                stroke={theme.palette.text.secondary}
                tick={{ fill: theme.palette.text.secondary }}
                tickFormatter={(timestamp) => {
                  const date = new Date(timestamp);
                  return `${date.getMonth() + 1}/${date.getDate()}`;
                }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis 
                domain={['dataMin - 5', 'dataMax + 5']}
                stroke={theme.palette.text.secondary}
                tick={{ fill: theme.palette.text.secondary }}
                label={{ value: 'bpm', angle: -90, position: 'insideLeft', fill: theme.palette.text.secondary }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: theme.palette.background.paper,
                  border: `1px solid ${theme.palette.divider}`,
                  borderRadius: 8,
                }}
                labelFormatter={(value) => {
                  const date = new Date(value);
                  return date.toLocaleDateString();
                }}
                formatter={(value: number | undefined) => 
                  value !== undefined ? [`${value} bpm`, 'Threshold HR'] : ['', '']
                }
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="hr" 
                stroke={theme.palette.error.main} 
                strokeWidth={2}
                dot={(props: any) => {
                  const { cx, cy, payload } = props;
                  if (payload.isFromKeySession) {
                    // Solid circle for real key session data
                    return <circle cx={cx} cy={cy} r={5} fill={theme.palette.error.main} stroke={theme.palette.background.paper} strokeWidth={2} />;
                  } else if (payload.isInterpolated) {
                    // Hollow circle for interpolated data
                    return <circle cx={cx} cy={cy} r={4} fill={theme.palette.background.paper} stroke={theme.palette.error.main} strokeWidth={2} />;
                  }
                  // Current setting - star shape
                  return <circle cx={cx} cy={cy} r={4} fill={theme.palette.warning.main} stroke={theme.palette.background.paper} strokeWidth={2} />;
                }}
                name="Threshold HR"
                connectNulls
                strokeDasharray={(entry: any) => entry?.isInterpolated ? "5 5" : "0"}
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ThresholdHRTrendChart;
