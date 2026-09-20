import { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Grid,
  Tooltip,
  useTheme,
  useMediaQuery,
  Skeleton,
  Button,
  Divider,
  IconButton,
} from '@mui/material';
import { ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer, Legend, ReferenceLine } from 'recharts';
import { TrendingUp, TrendingDown, TrendingFlat, Favorite, Info as InfoIcon, Sync as SyncIcon } from '@mui/icons-material';
import api from '../../services/api';

interface HRVStatsWidgetProps {
  daysBack?: number;
}

interface HRVDataPoint {
  date: string;
  rmssd: number;
  ln_rmssd: number;
  ln_rmssd_7day_avg: number | null;
  ln_rmssd_30day_avg: number | null;
  ln_rmssd_30day_upper: number | null;
  ln_rmssd_30day_lower: number | null;
  rmssd_7day_avg: number | null;
  rmssd_30day_avg: number | null;
  rmssd_30day_upper: number | null;
  rmssd_30day_lower: number | null;
  status: string;
}

interface HRVStats {
  current_avg: number;
  trend: number;
  trend_direction: 'up' | 'down' | 'stable';
  balanced_days: number;
  balanced_percent: number;
  data_points: number;
}

export default function HRVStatsWidget({ daysBack = 30 }: HRVStatsWidgetProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [loading, setLoading] = useState(true);
  const [showAllMetrics, setShowAllMetrics] = useState(!isMobile);
  const [error, setError] = useState<string | null>(null);
  const [hrvData, setHrvData] = useState<HRVDataPoint[]>([]);
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [stats, setStats] = useState<HRVStats>({
    current_avg: 0,
    trend: 0,
    trend_direction: 'stable',
    balanced_days: 0,
    balanced_percent: 0,
    data_points: 0,
  });

  const activeData = activeIndex !== null && hrvData[activeIndex] ? hrvData[activeIndex] : null;

  useEffect(() => {
    fetchHRVData();
  }, [daysBack]);

  const fetchHRVData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.get(`/garmin/hrv?days=${daysBack}`);
      
      setHrvData(response.data.data);
      setStats(response.data.stats);
      
      setLoading(false);
    } catch (err: any) {
      console.error('Error fetching HRV data:', err);
      setError(err.response?.data?.detail || 'Failed to load HRV data');
      setLoading(false);
    }
  };

  // Helper to add segment-specific data keys
  const getSegmentedData = () => {
    if (hrvData.length === 0) return [];
    
    const segmentedData = hrvData.map(point => ({ ...point }));
    let segmentIndex = 0;
    let currentIsOutOfRange = false;
    
    segmentedData.forEach((point, index) => {
      const isOutOfRange = 
        point.ln_rmssd_7day_avg !== null &&
        point.ln_rmssd_30day_lower !== null &&
        point.ln_rmssd_30day_upper !== null &&
        (point.ln_rmssd_7day_avg < point.ln_rmssd_30day_lower ||
         point.ln_rmssd_7day_avg > point.ln_rmssd_30day_upper);
      
      if (index === 0) {
        currentIsOutOfRange = isOutOfRange;
        point[`segment_${segmentIndex}`] = point.ln_rmssd_7day_avg;
        point[`segment_${segmentIndex}_out`] = isOutOfRange;
      } else if (isOutOfRange !== currentIsOutOfRange) {
        // Transition point - include in BOTH segments to connect them
        // End previous segment
        point[`segment_${segmentIndex}`] = point.ln_rmssd_7day_avg;
        
        // Start new segment
        segmentIndex++;
        currentIsOutOfRange = isOutOfRange;
        point[`segment_${segmentIndex}`] = point.ln_rmssd_7day_avg;
        point[`segment_${segmentIndex}_out`] = isOutOfRange;
      } else {
        // Continue current segment
        point[`segment_${segmentIndex}`] = point.ln_rmssd_7day_avg;
        point[`segment_${segmentIndex}_out`] = isOutOfRange;
      }
    });
    
    return { data: segmentedData, segmentCount: segmentIndex + 1 };
  };

  const { data: chartData, segmentCount } = hrvData.length > 0 ? getSegmentedData() : { data: [], segmentCount: 0 };

  const getTrendIcon = () => {
    switch (stats.trend_direction) {
      case 'up':
        return <TrendingUp sx={{ color: 'success.main', fontSize: 32 }} />;
      case 'down':
        return <TrendingDown sx={{ color: 'error.main', fontSize: 32 }} />;
      default:
        return <TrendingFlat sx={{ color: 'text.secondary', fontSize: 32 }} />;
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: { xs: 2, sm: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Skeleton variant="circular" width={32} height={32} />
          <Skeleton variant="text" width={200} height={32} />
        </Box>
        
        <Grid container spacing={{ xs: 2, sm: 3 }} sx={{ mb: 3 }}>
          {[...Array(4)].map((_, i) => (
            <Grid item xs={6} sm={6} md={3} key={i}>
              <Skeleton variant="rectangular" height={100} sx={{ borderRadius: 1 }} />
            </Grid>
          ))}
        </Grid>
        
        <Skeleton variant="rectangular" height={350} sx={{ borderRadius: 1 }} />
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Paper>
    );
  }

  if (hrvData.length === 0) {
    return (
      <Paper sx={{ p: { xs: 3, sm: 4 } }}>
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          textAlign: 'center',
          gap: 2
        }}>
          <Favorite sx={{ fontSize: 80, color: 'text.disabled' }} />
          
          <Typography variant="h6" color="text.primary">
            No HRV Data Yet
          </Typography>
          
          <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 400 }}>
            Heart Rate Variability helps track your recovery and readiness to train. 
            Make sure your Garmin device tracks HRV during sleep.
          </Typography>
          
          <Box sx={{ bgcolor: 'background.default', p: 2, borderRadius: 2, mt: 1, maxWidth: 400 }}>
            <Typography variant="caption" color="text.secondary" fontWeight={600} display="block" sx={{ mb: 1 }}>
              📱 To enable HRV tracking:
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary" sx={{ textAlign: 'left' }}>
              1. Open Garmin Connect app
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary" sx={{ textAlign: 'left' }}>
              2. Go to Settings → User Settings → Health Stats
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary" sx={{ textAlign: 'left' }}>
              3. Enable "HRV Status"
            </Typography>
          </Box>
          
          <Button 
            variant="contained" 
            startIcon={<SyncIcon />}
            onClick={() => window.location.reload()}
            sx={{ mt: 2 }}
          >
            Sync from Garmin
          </Button>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: { xs: 2, sm: 3 } }}>
      {/* Header with Info */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: { xs: 2, sm: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1, sm: 1.5 } }}>
          <Favorite sx={{ color: 'primary.main', fontSize: { xs: 28, sm: 32 } }} />
          <Box>
            <Typography variant="h6" sx={{ fontSize: { xs: '1.1rem', sm: '1.25rem' }, fontWeight: 600 }}>
              Heart Rate Variability
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ display: { xs: 'none', sm: 'block' } }}>
              Recovery & Readiness Indicator
            </Typography>
          </Box>
        </Box>
        <Tooltip title="HRV measures the variation in time between heartbeats. Higher values indicate better recovery and readiness to train.">
          <IconButton size="small">
            <InfoIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Summary Stats - Enhanced with Progressive Disclosure */}
      <Grid container spacing={{ xs: 1.5, sm: 2, md: 3 }}>
        {/* Always show: Current Avg */}
        <Grid item xs={6} sm={6} md={3}>
          <Paper 
            elevation={2}
            sx={{ 
              p: 2, 
              textAlign: 'center',
              background: `linear-gradient(135deg, ${theme.palette.primary.main}10 0%, transparent 100%)`
            }}
          >
            <Typography variant="caption" color="text.secondary" fontWeight={600}>
              Current Average
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 700, my: 0.5, fontSize: { xs: '2rem', sm: '2.5rem' } }}>
              {Math.round(stats.current_avg)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              ms (7-day rolling)
            </Typography>
          </Paper>
        </Grid>

        {/* Always show: Trend */}
        <Grid item xs={6} sm={6} md={3}>
          <Paper 
            elevation={stats.trend_direction === 'up' ? 3 : 1}
            sx={{ 
              p: 2, 
              textAlign: 'center',
              ...(stats.trend_direction === 'up' && {
                background: `linear-gradient(135deg, ${theme.palette.success.main}15 0%, transparent 100%)`,
                border: `1px solid ${theme.palette.success.light}40`
              })
            }}
          >
            <Typography variant="caption" color="text.secondary" fontWeight={600}>
              Trend
            </Typography>
            <Box sx={{ my: 0.5 }}>
              {getTrendIcon()}
            </Box>
            <Typography variant="caption" color="text.secondary">
              {stats.trend > 0 ? '+' : ''}{stats.trend.toFixed(1)}% vs last week
            </Typography>
          </Paper>
        </Grid>

        {/* Show on tablet+ or when expanded on mobile */}
        {(showAllMetrics || !isMobile) && (
          <>
            <Grid item xs={6} sm={6} md={3}>
              <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary" fontWeight={600}>
                  Balanced Days
                </Typography>
                <Typography variant="h3" sx={{ fontWeight: 700, color: 'success.main', my: 0.5, fontSize: { xs: '2rem', sm: '2.5rem' } }}>
                  {stats.balanced_days}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {stats.balanced_percent}% of period
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={6} sm={6} md={3}>
              <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary" fontWeight={600}>
                  Data Points
                </Typography>
                <Typography variant="h3" sx={{ fontWeight: 700, my: 0.5, fontSize: { xs: '2rem', sm: '2.5rem' } }}>
                  {stats.data_points}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  days recorded
                </Typography>
              </Paper>
            </Grid>
          </>
        )}
      </Grid>

      {/* Mobile: Expand Button */}
      {isMobile && !showAllMetrics && (
        <Button 
          fullWidth 
          size="small" 
          onClick={() => setShowAllMetrics(true)}
          sx={{ mt: 1.5 }}
        >
          Show More Stats
        </Button>
      )}

      <Divider sx={{ my: { xs: 2, sm: 3 } }} />

      {/* Fixed Tooltip Header (Mobile Only) - Shows Above Chart */}
      {isMobile && (
        <Paper 
          elevation={0}
          sx={{ 
            p: 1.5,
            mb: 2,
            bgcolor: 'background.default',
            borderRadius: 2,
            minHeight: 72,
            border: `1px solid ${theme.palette.divider}`,
          }}
        >
          {activeData ? (
            <>
              <Typography variant="caption" color="text.secondary" fontWeight={600} display="block">
                {new Date(activeData.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
              </Typography>
              <Typography variant="h6" sx={{ my: 0.5, fontSize: '1.25rem', fontWeight: 700 }}>
                Your HRV: {Math.round(activeData.rmssd_7day_avg || activeData.rmssd)} ms
              </Typography>
              {activeData.rmssd_30day_upper && activeData.rmssd_30day_lower && (
                <Typography variant="body2" color="text.secondary" fontSize="0.8rem">
                  Normal Range: {Math.round(activeData.rmssd_30day_lower)}–{Math.round(activeData.rmssd_30day_upper)} ms
                </Typography>
              )}
            </>
          ) : (
            <Box sx={{ display: 'flex', alignItems: 'center', height: '100%' }}>
              <Typography variant="body2" color="text.secondary" fontSize="0.85rem">
                👆 Tap and drag on the chart to explore your HRV data
              </Typography>
            </Box>
          )}
        </Paper>
      )}

      {/* HRV Trend Chart - Area Chart with Shaded Normal Range */}
      <Box sx={{ height: { xs: 300, sm: 350, md: 400 } }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart 
            data={chartData} 
            margin={{ top: 5, right: isMobile ? 10 : 20, left: isMobile ? 0 : 10, bottom: 5 }}
            onMouseMove={(state: any) => {
              if (state && state.isTooltipActive && state.activeTooltipIndex !== undefined) {
                setActiveIndex(state.activeTooltipIndex);
              }
            }}
            onMouseLeave={() => {
              if (!isMobile) setActiveIndex(null);
            }}
            onTouchMove={(state: any) => {
              if (state && state.isTooltipActive && state.activeTooltipIndex !== undefined) {
                setActiveIndex(state.activeTooltipIndex);
              }
            }}
            onTouchEnd={() => {
              // Keep tooltip visible on mobile after touch
              // User can tap elsewhere to change or it stays for reference
            }}
          >
            <defs>
              <linearGradient id="normalRange" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={theme.palette.success.light} stopOpacity={0.3}/>
                <stop offset="100%" stopColor={theme.palette.success.light} stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            
            <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
            <XAxis
              dataKey="date"
              stroke={theme.palette.text.secondary}
              tick={{ fill: theme.palette.text.secondary, fontSize: isMobile ? 9 : 11 }}
              tickFormatter={(value) => {
                const date = new Date(value);
                return isMobile ? `${date.getMonth() + 1}/${date.getDate()}` : date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
              }}
            />
            <YAxis
              stroke={theme.palette.text.secondary}
              tick={{ fill: theme.palette.text.secondary, fontSize: isMobile ? 9 : 11 }}
              label={!isMobile ? { value: 'ln(RMSSD)', angle: -90, position: 'insideLeft', fill: theme.palette.text.secondary } : undefined}
              domain={['auto', 'auto']}
              width={isMobile ? 45 : 55}
            />
            
            {/* Tooltip - Desktop only, hidden on mobile */}
            {!isMobile && (
              <ChartTooltip
                contentStyle={{
                  backgroundColor: theme.palette.background.paper,
                  border: `1px solid ${theme.palette.divider}`,
                  borderRadius: 8,
                }}
                formatter={(value: number, name: string) => {
                  // Convert log back to actual RMSSD for user-friendly display
                  const actualValue = Math.exp(value);
                  return [
                    `${Math.round(actualValue)} ms`,
                    name === 'normalRange' ? 'Normal Range' : 'Your HRV'
                  ];
                }}
                labelFormatter={(label) => new Date(label).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
              />
            )}
            
            {/* Vertical reference line on mobile - shows selected point */}
            {isMobile && activeIndex !== null && activeData && (
              <ReferenceLine 
                x={activeData.date}
                stroke={theme.palette.primary.main}
                strokeWidth={1.5}
                strokeDasharray="3 3"
              />
            )}
            
            <Legend 
              wrapperStyle={{ fontSize: isMobile ? '10px' : '12px' }}
              iconSize={isMobile ? 10 : 14}
              formatter={(value) => {
                if (isMobile) {
                  return value === 'normalRange' ? 'Normal' : 'Your HRV';
                } else {
                  return value === 'normalRange' ? 'Normal Range' : 'Your HRV';
                }
              }}
            />
            
            {/* Shaded normal range area */}
            <Area
              type="monotone"
              dataKey="ln_rmssd_30day_upper"
              stroke="none"
              fill="url(#normalRange)"
              name="normalRange"
            />
            <Area
              type="monotone"
              dataKey="ln_rmssd_30day_lower"
              stroke="none"
              fill={theme.palette.background.paper}
            />
            
            {/* Render each segment with its own color */}
            {Array.from({ length: segmentCount }).map((_, idx) => {
              // Check if this segment is out of range by checking first point in segment
              const firstPointInSegment = chartData.find(p => p[`segment_${idx}`] !== undefined);
              const isOutOfRange = firstPointInSegment?.[`segment_${idx}_out`] || false;
              
              return (
                <Line
                  key={`segment-${idx}`}
                  type="monotone"
                  dataKey={`segment_${idx}`}
                  stroke={isOutOfRange ? theme.palette.warning.main : theme.palette.primary.main}
                  strokeWidth={isMobile ? 1.5 : 2}
                  dot={false}
                  activeDot={{ r: isMobile ? 6 : 5, strokeWidth: 2 }}
                  connectNulls={false}
                  isAnimationActive={false}
                  legendType="none"
                />
              );
            })}
          </ComposedChart>
        </ResponsiveContainer>
      </Box>

      {/* Chart Explanation */}
      <Box sx={{ mt: 2, p: 1.5, bgcolor: 'background.default', borderRadius: 1 }}>
        <Typography variant="caption" color="text.secondary">
          💡 The shaded area shows your "normal range". Values within this zone indicate balanced recovery. 
          Consistently high values suggest good readiness to train.
        </Typography>
      </Box>
    </Paper>
  );
}
