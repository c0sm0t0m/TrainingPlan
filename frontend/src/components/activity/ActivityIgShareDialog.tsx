/**
 * Dialog: preview IG share card, download PNG, copy caption.
 */
import React, { useRef, useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack,
  TextField,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Close as CloseIcon,
  Download as DownloadIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';
import { toPng } from 'html-to-image';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';
import ActivityIgShareCard, {
  ShareMatchedWorkout,
  ShareTrackPoint,
} from './ActivityIgShareCard';

const EXPORT_WIDTH = 1080;

export interface ActivityIgShareDialogProps {
  open: boolean;
  onClose: () => void;
  activityName: string;
  activityType: string;
  startTimeLocal: string;
  durationSeconds?: number;
  distanceMeters?: number;
  calculatedTss?: number;
  trackPoints?: ShareTrackPoint[];
  matchedWorkout?: ShareMatchedWorkout | null;
}

function sportLabel(activityType: string): string {
  const t = activityType.toLowerCase();
  if (t.includes('run')) return 'Run';
  if (t.includes('bik') || t.includes('cycl') || t.includes('ride')) return 'Bike';
  if (t.includes('swim')) return 'Swim';
  if (t.includes('strength') || t.includes('gym')) return 'Strength';
  return activityType;
}

function buildCaption(props: ActivityIgShareDialogProps): string {
  const dateLabel = format(new Date(props.startTimeLocal), 'd. MMM', { locale: de });
  const sport = sportLabel(props.activityType);
  const dist =
    props.distanceMeters != null ? `${(props.distanceMeters / 1000).toFixed(1)} km` : null;
  const dur =
    props.durationSeconds != null
      ? (() => {
          const m = Math.round(props.durationSeconds / 60);
          return m >= 60 ? `${Math.floor(m / 60)}:${String(m % 60).padStart(2, '0')} h` : `${m} min`;
        })()
      : null;
  const tss = props.calculatedTss != null ? `${Math.round(props.calculatedTss)} TSS` : null;
  const bits = [dist, dur, tss].filter(Boolean).join(' · ');

  const lines = [
    `${sport} — ${dateLabel}`,
    '',
    bits || 'Session erledigt.',
  ];

  if (props.matchedWorkout) {
    const planned: string[] = [];
    if (props.matchedWorkout.distance_km != null) {
      planned.push(`${props.matchedWorkout.distance_km.toFixed(1)} km`);
    }
    if (props.matchedWorkout.duration_minutes != null) {
      planned.push(`${Math.round(props.matchedWorkout.duration_minutes)} min`);
    }
    if (planned.length) {
      lines.push('');
      lines.push(`Geplant: ${planned.join(' · ')} → so gelaufen.`);
    }
  }

  lines.push('');
  lines.push('Mit Kinesis geplant. 🤍');
  lines.push('');
  lines.push('#triathlon #swimbikerun #kinesis #triathlontraining');

  return lines.join('\n');
}

const ActivityIgShareDialog: React.FC<ActivityIgShareDialogProps> = (props) => {
  const { open, onClose } = props;
  const cardRef = useRef<HTMLDivElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [caption, setCaption] = useState(() => buildCaption(props));
  const [mapReady, setMapReady] = useState(false);

  const handleMapReady = React.useCallback((ready: boolean) => {
    setMapReady(ready);
  }, []);

  React.useEffect(() => {
    if (open) {
      setCaption(buildCaption(props));
      setCopied(false);
      setError(null);
      setMapReady(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- rebuild when dialog opens
  }, [open]);

  const previewScale = 0.32;
  const previewW = EXPORT_WIDTH * previewScale;
  const previewH = Math.round(EXPORT_WIDTH * (5 / 4) * previewScale);

  const handleDownload = async () => {
    if (!cardRef.current) return;
    if (!mapReady) {
      setError('Karte lädt noch… kurz warten.');
      return;
    }
    setBusy(true);
    setError(null);
    try {
      // Brief pause so the map <img> is painted
      await new Promise((r) => setTimeout(r, 80));
      const dataUrl = await toPng(cardRef.current, {
        width: EXPORT_WIDTH,
        height: Math.round(EXPORT_WIDTH * (5 / 4)),
        pixelRatio: 1,
        cacheBust: true,
      });
      const link = document.createElement('a');
      const stamp = format(new Date(props.startTimeLocal), 'yyyy-MM-dd');
      link.download = `kinesis-${stamp}.png`;
      link.href = dataUrl;
      link.click();
    } catch (err) {
      console.error(err);
      setError('Export fehlgeschlagen. Bitte nochmal versuchen.');
    } finally {
      setBusy(false);
    }
  };

  const handleCopyCaption = async () => {
    try {
      await navigator.clipboard.writeText(caption);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError('Caption konnte nicht kopiert werden.');
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        Share for Instagram
        <IconButton onClick={onClose} size="small" aria-label="Close">
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        <Stack spacing={2}>
          {error && <Alert severity="error">{error}</Alert>}

          <Box
            sx={{
              alignSelf: 'center',
              width: previewW,
              height: previewH,
              overflow: 'hidden',
              borderRadius: 1,
              boxShadow: 3,
              position: 'relative',
            }}
          >
            {!mapReady && (
              <Box
                sx={{
                  position: 'absolute',
                  inset: 0,
                  zIndex: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  bgcolor: 'rgba(15,23,42,0.35)',
                }}
              >
                <CircularProgress size={28} />
              </Box>
            )}
            <Box
              sx={{
                width: EXPORT_WIDTH,
                height: Math.round(EXPORT_WIDTH * (5 / 4)),
                transform: `scale(${previewScale})`,
                transformOrigin: 'top left',
              }}
            >
              <ActivityIgShareCard
                ref={cardRef}
                width={EXPORT_WIDTH}
                activityName={props.activityName}
                activityType={props.activityType}
                startTimeLocal={props.startTimeLocal}
                durationSeconds={props.durationSeconds}
                distanceMeters={props.distanceMeters}
                calculatedTss={props.calculatedTss}
                trackPoints={props.trackPoints}
                matchedWorkout={props.matchedWorkout}
                onMapReady={handleMapReady}
              />
            </Box>
          </Box>

          <Typography variant="caption" color="text.secondary">
            4:5 · Safe Zone unten für Instagram · keine Intervalle oder Zonen
          </Typography>

          <TextField
            label="Caption"
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            multiline
            minRows={5}
            fullWidth
            size="small"
          />
        </Stack>
      </DialogContent>
      <DialogActions sx={{ px: 3, py: 2, gap: 1, flexWrap: 'wrap' }}>
        <Button
          startIcon={<CopyIcon />}
          onClick={handleCopyCaption}
          disabled={busy}
        >
          {copied ? 'Kopiert' : 'Caption kopieren'}
        </Button>
        <Button
          variant="contained"
          startIcon={busy ? <CircularProgress size={16} color="inherit" /> : <DownloadIcon />}
          onClick={handleDownload}
          disabled={busy || !mapReady}
        >
          PNG speichern
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ActivityIgShareDialog;
