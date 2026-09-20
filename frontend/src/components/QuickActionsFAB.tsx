import { useState } from 'react';
import {
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  Add as AddIcon,
  DirectionsRun as RunIcon,
  DirectionsBike as BikeIcon,
  Pool as SwimIcon,
  Event as EventIcon,
  ListAlt as PlanIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

interface QuickAction {
  icon: React.ReactNode;
  name: string;
  onClick: () => void;
}

export default function QuickActionsFAB() {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [open, setOpen] = useState(false);

  // Get context-aware actions based on current page
  const actions = getContextualActions(location.pathname, navigate);

  // Don't show FAB on login/register pages or when no actions
  if (location.pathname === '/login' || location.pathname === '/register' || actions.length === 0) {
    return null;
  }

  // Simple FAB for single action contexts
  if (actions.length === 1) {
    return (
      <Fab
        color="primary"
        aria-label={actions[0].name}
        onClick={actions[0].onClick}
        sx={{
          position: 'fixed',
          bottom: isMobile ? 16 : 24,
          right: isMobile ? 16 : 24,
          zIndex: 1000,
        }}
      >
        {actions[0].icon}
      </Fab>
    );
  }

  // SpeedDial for multiple actions
  return (
    <SpeedDial
      ariaLabel="Quick actions"
      sx={{
        position: 'fixed',
        bottom: isMobile ? 16 : 24,
        right: isMobile ? 16 : 24,
        zIndex: 1000,
      }}
      icon={<SpeedDialIcon openIcon={<CloseIcon />} />}
      onClose={() => setOpen(false)}
      onOpen={() => setOpen(true)}
      open={open}
      direction="up"
    >
      {actions.map((action) => (
        <SpeedDialAction
          key={action.name}
          icon={action.icon}
          tooltipTitle={action.name}
          tooltipOpen
          onClick={() => {
            action.onClick();
            setOpen(false);
          }}
        />
      ))}
    </SpeedDial>
  );
}

// Get context-aware actions based on current page
function getContextualActions(pathname: string, navigate: (path: string) => void): QuickAction[] {
  // Dashboard page - no FAB needed (navigation tabs already available)
  if (pathname === '/dashboard' || pathname === '/') {
    return [];
  }

  // Training Plans page - has dedicated "New Plan" button, no FAB needed
  if (pathname === '/plans') {
    return [];
  }

  // Plan Detail page
  if (pathname.startsWith('/plans/') && pathname !== '/plans') {
    return [
      {
        icon: <RunIcon />,
        name: 'Add Run',
        onClick: () => {
          // Trigger add workout dialog
          const addButton = document.querySelector('[aria-label="Add workout"]') as HTMLElement;
          if (addButton) addButton.click();
        },
      },
      {
        icon: <BikeIcon />,
        name: 'Add Ride',
        onClick: () => {
          const addButton = document.querySelector('[aria-label="Add workout"]') as HTMLElement;
          if (addButton) addButton.click();
        },
      },
      {
        icon: <SwimIcon />,
        name: 'Add Swim',
        onClick: () => {
          const addButton = document.querySelector('[aria-label="Add workout"]') as HTMLElement;
          if (addButton) addButton.click();
        },
      },
    ];
  }

  // Calendar page - no FAB needed
  if (pathname === '/calendar') {
    return [];
  }

  // Activities page
  if (pathname === '/activities') {
    return [
      {
        icon: <EventIcon />,
        name: 'View Calendar',
        onClick: () => navigate('/calendar'),
      },
    ];
  }

  // Settings page
  if (pathname.startsWith('/settings')) {
    return [
      {
        icon: <EventIcon />,
        name: 'Back to Dashboard',
        onClick: () => navigate('/dashboard'),
      },
    ];
  }

  // Default actions
  return [
    {
      icon: <PlanIcon />,
      name: 'Training Plans',
      onClick: () => navigate('/plans'),
    },
    {
      icon: <EventIcon />,
      name: 'Calendar',
      onClick: () => navigate('/calendar'),
    },
  ];
}
