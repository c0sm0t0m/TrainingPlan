import { Card, CardContent, Skeleton, Box, Grid } from '@mui/material';

export default function CalendarSkeleton() {
  return (
    <Card>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Skeleton variant="text" width={200} height={40} />
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Skeleton variant="circular" width={40} height={40} />
            <Skeleton variant="circular" width={40} height={40} />
          </Box>
        </Box>

        {/* Day headers */}
        <Grid container spacing={0} sx={{ mb: 1 }}>
          {[1, 2, 3, 4, 5, 6, 7].map((i) => (
            <Grid item xs key={i}>
              <Skeleton variant="rectangular" height={40} />
            </Grid>
          ))}
        </Grid>

        {/* Calendar grid */}
        {[1, 2, 3, 4].map((week) => (
          <Grid container spacing={0} key={week} sx={{ mb: 1 }}>
            {[1, 2, 3, 4, 5, 6, 7].map((day) => (
              <Grid item xs key={day}>
                <Skeleton variant="rectangular" height={120} sx={{ m: 0.5 }} />
              </Grid>
            ))}
          </Grid>
        ))}
      </CardContent>
    </Card>
  );
}
