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
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer, Cell } from 'recharts';
import { Favorite } from '@mui/icons-material';
import api from '../../services/api';

interface HRZoneDistributionWidgetProps {
  daysBack?: number;
}

interface HRZoneDataPoint {
  zone_number: number;
  zone_name: string;
  min_hr: number;
  max_hr: number;
  activity_count: number;
  percentage: number;
}

interface HRZoneDistributionResponse {
  data_points: HRZoneDataPoint[];
  total_activities: number;
  date_range_start: string;
  date_range_end: string;
}

export default function HRZoneDistributionWidget({ daysBack = 90 }: HRZoneDistributionWidgetProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<HRZoneDataPoint[]>([]);
  const [totalActivities, setTotalActivities] = useState(0);
  const [sportFilter, setSportFilter] = useState<string>('all');

  useEffect(() => {
    fetchData();
  }, [daysBack, sportFilter]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.get<HRZoneDistributionResponse>(
        `/analytics/hr-zone-distribution?days_back=${daysBack}&sport_filter=${sportFilter}`
      );
      
      setData(response.data.data_points);
      setTotalActivities(response.data.total_activities);
      
      setLoading(false);
    } catch (err: any) {
      console.error('Error fetching HR zone distribution data:', err);
      setError(err.response?.data?.detail || 'Failed to load HR zone data');
      setLoading(false);
    }
  };

  // Format zone label
  const formatZoneLabel = (zone: HRZoneDataPoint) => {
    return `Z${zone.zone_number}`;
  };

  // Prepare chart data
  const chartData = data.map(point => ({
    zone: formatZoneLabel(point),
    zoneName: point.zone_name,
    hrRange: `${point.min_hr}-${point.max_hr}`,
    percentage: point.percentage,
    count: point.activity_count
  }));

  // Color zones progressively from blue (recovery) to red (max)
  const getZoneColor = (zoneNumber: number) => {
    const colors = [
      theme.palette.info.light,      // Zone 1 - Recovery
      theme.palette.info.main,       // Zone 2 - Endurance
      theme.palette.success.main,    // Zone 3 - Tempo
      theme.palette.warning.main,    // Zone 4 - Threshold
      theme.palette.error.main,      // Zone 5 - VO2max
    ];
    return colors[zoneNumber - 1] || theme.palette.grey[500];
  };

  if (loading) {
    return (
      <Paper sx={{ p: { xs: 2, sm: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Skeleton variant="circular" width={32} height={32} />
          <Skeleton variant="text" width={200} height={32} />
        </Box>
        <Skeleton variant="rectangular" height={50} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={300} />
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: { xs: 2, sm: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Favorite sx={{ color: 'error.main', fontSize: 32 }} />
          <Typography variant="h6">HR Zone Distribution</Typography>
        </Box>
        <Alert severity="error">{error}</Alert>
      </Paper>
    );
  }

  if (totalActivities === 0) {
    return (
      <Paper sx={{ p: { xs: 2, sm: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Favorite sx={{ color: 'error.main', fontSize: 32 }} />
          <Typography variant="h6">HR Zone Distribution</Typography>
        </Box>
        
        {/* Sport Filter */}
        <Box sx={{ mb: 3 }}>
          <ToggleButtonGroup
            value={sportFilter}
            exclusive
            onChange={(event, newValue) => {
              if (newValue !== null) {
                setSportFilter(newValue);
              }
            }}
            size="small"
            fullWidth={isMobile}
            sx={{
              '& .MuiToggleButton-root': {
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                py: { xs: 0.5, sm: 1 }
              }
            }}
          >
            <ToggleButton value="all">All</ToggleButton>
            <ToggleButton value="running">Run</ToggleButton>
            <ToggleButton value="cycling">Bike</ToggleButton>
            <ToggleButton value="swimming">Swim</ToggleButton>
            <ToggleButton value="other">Other</ToggleButton>
          </ToggleButtonGroup>
        </Box>
        
        <Alert severity="info">No activities with HR data found for this filter and time range</Alert>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: { xs: 2, sm: 3 } }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Favorite sx={{ color: 'error.main', fontSize: 32 }} />
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6">HR Zone Distribution</Typography>
          <Typography variant="caption" color="text.secondary">
            Based on average HR per activity ({totalActivities} activities)
          </Typography>
        </Box>
      </Box>

      {/* Sport Filter */}
      <Box sx={{ mb: 3 }}>
        <ToggleButtonGroup
          value={sportFilter}
          exclusive
          onChange={(event, newValue) => {
            if (newValue !== null) {
              setSportFilter(newValue);
            }
          }}
          size="small"
          fullWidth={isMobile}
          sx={{
            '& .MuiToggleButton-root': {
              fontSize: { xs: '0.75rem', sm: '0.875rem' },
              py: { xs: 0.5, sm: 1 }
            }
          }}
        >
          <ToggleButton value="all">All</ToggleButton>
          <ToggleButton value="running">Run</ToggleButton>
          <ToggleButton value="cycling">Bike</ToggleButton>
          <ToggleButton value="swimming">Swim</ToggleButton>
          <ToggleButton value="other">Other</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={isMobile ? 280 : 320}>
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis 
            dataKey="zone" 
            stroke={theme.palette.text.secondary}
            tick={(props) => {
              const { x, y, payload } = props;
              const zoneData = data[payload.index];
              if (!zoneData) return null;
              
              return (
                <g transform={`translate(${x},${y})`}>
                  <text
                    x={0}
                    y={0}
                    dy={8}
                    textAnchor="middle"
                    fill={theme.palette.text.primary}
                    fontSize={12}
                    fontWeight="bold"
                  >
                    {payload.value}
                  </text>
                  <text
                    x={0}
                    y={0}
                    dy={24}
                    textAnchor="middle"
                    fill={theme.palette.text.secondary}
                    fontSize={10}
                  >
                    {zoneData.min_hr}-{zoneData.max_hr}
                  </text>
                </g>
              );
            }}
            height={50}
          />
          <YAxis 
            stroke={theme.palette.text.secondary}
            label={{ 
              value: 'Percentage (%)', 
              angle: -90, 
              position: 'insideLeft',
              style: { fill: theme.palette.text.secondary }
            }}
            tick={{ fontSize: 12, fill: theme.palette.text.secondary }}
            domain={[0, 100]}
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
            formatter={(value: any, name: string, props: any) => {
              if (name === 'percentage') {
                return [
                  <Box key="tooltip">
                    <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'text.primary' }}>
                      {props.payload.zoneName}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                      {props.payload.hrRange} bpm
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.primary' }}>
                      {value.toFixed(1)}% ({props.payload.count} activities)
                    </Typography>
                  </Box>,
                  ''
                ];
              }
              return [value, name];
            }}
            labelFormatter={() => ''}
          />
          <Bar dataKey="percentage" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getZoneColor(data[index].zone_number)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Paper>
  );
}
