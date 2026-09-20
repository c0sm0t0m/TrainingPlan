import { Grid, Card, CardContent, Skeleton, Box } from '@mui/material';

export default function DashboardSkeleton() {
  return (
    <Grid container spacing={3}>
      {/* Metric Cards */}
      {[1, 2, 3, 4].map((i) => (
        <Grid item xs={12} sm={6} md={3} key={i}>
          <Card>
            <CardContent>
              <Skeleton variant="text" width="60%" height={20} />
              <Skeleton variant="text" width="40%" height={40} sx={{ mt: 1 }} />
              <Skeleton variant="text" width="50%" height={16} sx={{ mt: 0.5 }} />
            </CardContent>
          </Card>
        </Grid>
      ))}

      {/* Chart */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Skeleton variant="text" width="30%" height={24} sx={{ mb: 2 }} />
            <Skeleton variant="rectangular" height={300} />
          </CardContent>
        </Card>
      </Grid>

      {/* Sport Widgets */}
      {[1, 2, 3].map((i) => (
        <Grid item xs={12} md={4} key={`sport-${i}`}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Skeleton variant="circular" width={32} height={32} sx={{ mr: 1 }} />
                <Skeleton variant="text" width="40%" height={24} />
              </Box>
              <Grid container spacing={1} sx={{ mb: 2 }}>
                {[1, 2, 3].map((j) => (
                  <Grid item xs={4} key={j}>
                    <Skeleton variant="rectangular" height={60} />
                  </Grid>
                ))}
              </Grid>
              <Grid container spacing={1}>
                {[1, 2, 3, 4].map((j) => (
                  <Grid item xs={3} key={j}>
                    <Skeleton variant="rectangular" height={50} />
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}
