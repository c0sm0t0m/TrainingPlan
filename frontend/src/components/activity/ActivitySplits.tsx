/**
 * Lap splits table for activity detail.
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Box,
} from '@mui/material';
import api from '../../services/api';
import { isCyclingSport } from '../../utils/sportTypes';

interface LapSplit {
  lap_number: number;
  distance_meters: number;
  duration_seconds: number;
  average_speed_mps?: number | null;
  average_hr?: number | null;
  max_hr?: number | null;
  average_power?: number | null;
  elevation_gain_meters?: number | null;
  average_cadence?: number | null;
}

interface Props {
  activityId: number;
  activityType: string;
}

function formatDuration(seconds: number): string {
  if (!seconds) return '—';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  if (m >= 60) {
    const h = Math.floor(m / 60);
    return `${h}:${String(m % 60).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }
  return `${m}:${String(s).padStart(2, '0')}`;
}

function formatPace(speedMps?: number | null): string {
  if (!speedMps || speedMps <= 0) return '—';
  const minPerKm = (1000 / speedMps) / 60;
  const min = Math.floor(minPerKm);
  const sec = Math.round((minPerKm - min) * 60);
  return `${min}:${String(sec).padStart(2, '0')}`;
}

function formatSpeed(speedMps?: number | null): string {
  if (!speedMps || speedMps <= 0) return '—';
  return `${(speedMps * 3.6).toFixed(1)}`;
}

const ActivitySplits: React.FC<Props> = ({ activityId, activityType }) => {
  const cycling = isCyclingSport(activityType);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [splits, setSplits] = useState<LapSplit[]>([]);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.get<{ splits: LapSplit[]; total_laps: number }>(
          `/activities/${activityId}/splits`
        );
        if (!cancelled) setSplits(res.data.splits || []);
      } catch (err: any) {
        if (!cancelled) setError(err.response?.data?.detail || 'Failed to load splits');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [activityId]);

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={28} />
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

  if (splits.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Lap Splits
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No lap data from Garmin for this activity. See per-km bars in the charts.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const showPower = cycling || splits.some((s) => s.average_power != null);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Lap Splits
        </Typography>
        <TableContainer sx={{ maxHeight: 420 }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>#</TableCell>
                <TableCell align="right">Dist</TableCell>
                <TableCell align="right">Time</TableCell>
                <TableCell align="right">{cycling ? 'km/h' : 'Pace'}</TableCell>
                {showPower && <TableCell align="right">W</TableCell>}
                <TableCell align="right">HR</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {splits.map((lap) => (
                <TableRow key={lap.lap_number} hover>
                  <TableCell>{lap.lap_number}</TableCell>
                  <TableCell align="right">
                    {lap.distance_meters
                      ? lap.distance_meters >= 1000
                        ? `${(lap.distance_meters / 1000).toFixed(2)}`
                        : `${Math.round(lap.distance_meters)} m`
                      : '—'}
                  </TableCell>
                  <TableCell align="right">{formatDuration(lap.duration_seconds)}</TableCell>
                  <TableCell align="right">
                    {cycling
                      ? formatSpeed(lap.average_speed_mps)
                      : formatPace(lap.average_speed_mps)}
                  </TableCell>
                  {showPower && (
                    <TableCell align="right">
                      {lap.average_power != null ? Math.round(lap.average_power) : '—'}
                    </TableCell>
                  )}
                  <TableCell align="right">{lap.average_hr ?? '—'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

export default ActivitySplits;
