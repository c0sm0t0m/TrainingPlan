import { Grid, Card, CardContent, CardActions, Skeleton, Box } from '@mui/material';

export default function TrainingPlansSkeleton() {
  return (
    <Grid container spacing={3}>
      {[1, 2, 3].map((i) => (
        <Grid item xs={12} md={6} lg={4} key={i}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Skeleton variant="text" width="60%" height={28} />
                <Skeleton variant="circular" width={24} height={24} />
              </Box>
              <Skeleton variant="text" width="40%" height={20} sx={{ mb: 1 }} />
              <Skeleton variant="text" width="90%" height={16} />
              <Skeleton variant="text" width="80%" height={16} />
              <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                <Skeleton variant="rectangular" width={60} height={24} sx={{ borderRadius: 1 }} />
                <Skeleton variant="rectangular" width={80} height={24} sx={{ borderRadius: 1 }} />
              </Box>
            </CardContent>
            <CardActions>
              <Skeleton variant="rectangular" width={80} height={32} sx={{ borderRadius: 1 }} />
              <Box sx={{ flexGrow: 1 }} />
              <Skeleton variant="circular" width={32} height={32} />
              <Skeleton variant="circular" width={32} height={32} />
            </CardActions>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}
