import { Box, Typography, Button, SxProps, Theme } from '@mui/material';
import { ReactNode } from 'react';

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  secondaryActionLabel?: string;
  onSecondaryAction?: () => void;
  sx?: SxProps<Theme>;
}

export default function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
  sx,
}: EmptyStateProps) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        py: 8,
        px: 3,
        ...sx,
      }}
    >
      {icon && (
        <Box
          sx={{
            fontSize: '4rem',
            mb: 2,
            opacity: 0.5,
          }}
        >
          {icon}
        </Box>
      )}

      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
        {title}
      </Typography>

      {description && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mb: 3, maxWidth: 400 }}
        >
          {description}
        </Typography>
      )}

      {actionLabel && onAction && (
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="contained" onClick={onAction} size="large">
            {actionLabel}
          </Button>
          {secondaryActionLabel && onSecondaryAction && (
            <Button variant="outlined" onClick={onSecondaryAction} size="large">
              {secondaryActionLabel}
            </Button>
          )}
        </Box>
      )}
    </Box>
  );
}
