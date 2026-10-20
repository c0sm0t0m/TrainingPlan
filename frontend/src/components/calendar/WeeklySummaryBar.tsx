import { Box, Typography, Divider, useTheme } from '@mui/material';
import { getTSSColor } from '../../utils/sportColors';

interface WeeklySummaryBarProps {
  totalTSS: number;
  plannedTSS?: number;
  totalHours: number;
  totalDistance: number;
  last7DaysIF?: number[]; // Optional: Intensity Factor (IF) for each of last 7 days
  last7DaysTSS?: number[]; // Optional: TSS for each of last 7 days (for bar height)
}

export default function WeeklySummaryBar({
  totalTSS,
  plannedTSS,
  totalHours,
  totalDistance,
  last7DaysIF = [],
  last7DaysTSS = [],
}: WeeklySummaryBarProps) {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
        bgcolor: 'primary.dark',
        color: 'primary.contrastText',
        py: 1.5,
        px: 2,
        borderRadius: 1,
      }}
    >
      {/* Main Stats Row */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-around',
          alignItems: 'center',
        }}
      >
        <Box textAlign="center" flex={1}>
          <Typography fontWeight={700} noWrap sx={{ color: 'primary.contrastText', lineHeight: 1.1, fontSize: '1rem' }}>
            {plannedTSS != null ? `${Math.round(totalTSS)} / ${Math.round(plannedTSS)}` : Math.round(totalTSS)}
          </Typography>
          <Typography variant="caption" noWrap sx={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.9)' }}>
            {plannedTSS != null ? 'TSS done / plan' : 'TSS'}
          </Typography>
        </Box>
        
        <Divider
          orientation="vertical"
          flexItem
          sx={{ bgcolor: 'rgba(255,255,255,0.3)', height: 40, alignSelf: 'center' }}
        />
        
        <Box textAlign="center" flex={1}>
          <Typography variant="h6" fontWeight={700} sx={{ color: 'primary.contrastText' }}>
            {totalHours.toFixed(1)}h
          </Typography>
          <Typography variant="caption" sx={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.9)' }}>
            Time
          </Typography>
        </Box>
        
        <Divider
          orientation="vertical"
          flexItem
          sx={{ bgcolor: 'rgba(255,255,255,0.3)', height: 40, alignSelf: 'center' }}
        />
        
        <Box textAlign="center" flex={1}>
          <Typography variant="h6" fontWeight={700} sx={{ color: 'primary.contrastText' }}>
            {totalDistance.toFixed(1)}
          </Typography>
          <Typography variant="caption" sx={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.9)' }}>
            km
          </Typography>
        </Box>
      </Box>

      {/* Training Intensity Sparkline (IF-based color, TSS-based height) */}
      {last7DaysIF.length > 0 && last7DaysTSS.length > 0 && (
        <Box sx={{ px: 1 }}>
          <Typography variant="caption" sx={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.85)', mb: 0.5, display: 'block' }}>
            Last 7 Days Intensity
          </Typography>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'flex-end', 
              gap: 0.5,
              height: 36,
              bgcolor: 'rgba(0,0,0,0.15)',
              borderRadius: 0.5,
              px: 0.5,
            }}
          >
            {last7DaysIF.map((intensity, i) => {
              const tss = last7DaysTSS[i] || 0;
              
              // Color code based on Intensity Factor (IF)
              // IF < 0.75: Easy/recovery (green)
              // IF 0.75-0.85: Endurance (light green)
              // IF 0.85-0.95: Tempo (yellow/orange)
              // IF 0.95-1.05: Threshold (orange)
              // IF > 1.05: VO2max/race (red)
              
              let barColor = 'rgba(255,255,255,0.3)'; // Default light gray for no activity
              if (intensity > 0) {
                if (intensity < 0.75) barColor = 'rgba(76, 175, 80, 0.9)'; // Green - easy
                else if (intensity < 0.85) barColor = 'rgba(139, 195, 74, 0.9)'; // Light green - endurance
                else if (intensity < 0.95) barColor = 'rgba(255, 193, 7, 0.9)'; // Yellow - tempo
                else if (intensity < 1.05) barColor = 'rgba(255, 152, 0, 0.9)'; // Orange - threshold
                else barColor = 'rgba(244, 67, 54, 0.9)'; // Red - hard/race
              }
              
              // Height based on TSS (max at 200 TSS = 100% height)
              const maxTSS = 200;
              const heightPercent = tss === 0 ? 0 : Math.min((tss / maxTSS) * 100, 100);
              
              return (
                <Box
                  key={i}
                  sx={{
                    flex: 1,
                    height: heightPercent === 0 ? '3px' : `${Math.max(heightPercent, 8)}%`,
                    bgcolor: barColor,
                    borderRadius: 0.5,
                    transition: 'all 0.3s ease-in-out',
                    minHeight: '3px',
                  }}
                  title={`IF: ${intensity.toFixed(2)} | TSS: ${Math.round(tss)}`}
                />
              );
            })}
          </Box>
        </Box>
      )}
    </Box>
  );
}
