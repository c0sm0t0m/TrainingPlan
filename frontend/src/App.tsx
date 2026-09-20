import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import { FeatureFlagsProvider, useFeatureFlags } from './contexts/FeatureFlagsContext'
import Layout from './components/Layout'
import QuickActionsFAB from './components/QuickActionsFAB'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import TrainingPlans from './pages/TrainingPlans'
import PlanDetail from './pages/PlanDetail'
import Calendar from './pages/Calendar'
import ActivityDetail from './pages/ActivityDetail'
import EventDetail from './pages/EventDetail'
import AITrainingPlanGenerator from './pages/AITrainingPlanGenerator'
import Settings from './pages/SettingsNew'
import Analytics from './pages/Analytics'
import { useMemo, useState, useEffect, createContext, useContext } from 'react'

// Dark mode context
interface ThemeContextType {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  darkMode: false,
  toggleDarkMode: () => {},
});

export const useThemeMode = () => useContext(ThemeContext);

// Create theme based on mode and feature flags
const createAppTheme = (mode: 'light' | 'dark', useNewColorTheme: boolean = false) => createTheme({
  palette: {
    mode,
    primary: {
      main: useNewColorTheme ? '#0A7AFF' : '#2196F3',
      dark: useNewColorTheme ? '#0856B3' : '#1976D2',
      light: useNewColorTheme ? '#4D9FFF' : '#64B5F6',
    },
    secondary: {
      main: useNewColorTheme ? '#FF6B35' : '#FF9800',
      dark: useNewColorTheme ? '#E85A28' : '#F57C00',
      light: useNewColorTheme ? '#FF8F66' : '#FFB74D',
    },
    success: {
      main: useNewColorTheme ? '#00D9A3' : '#4CAF50',
      dark: useNewColorTheme ? '#00B386' : '#388E3C',
      light: useNewColorTheme ? '#33E5B8' : '#81C784',
    },
    warning: {
      main: '#FFB800',
    },
    error: {
      main: '#F44336',
    },
    info: {
      main: '#2196F3',
    },
    ...(mode === 'dark' && useNewColorTheme ? {
      background: {
        default: '#0A0E1A',
        paper: '#141B2D',
      },
      text: {
        primary: '#E8EAED',
        secondary: '#9CA3AF',
      },
    } : {}),
    ...(mode === 'light' && useNewColorTheme ? {
      background: {
        default: '#F8F9FA',
        paper: '#FFFFFF',
      },
      text: {
        primary: '#1A1A1A',
        secondary: '#6B7280',
      },
    } : {}),
  },
  typography: {
    fontFamily: useNewColorTheme 
      ? '"Inter Tight", "Inter", "SF Pro Display", system-ui, -apple-system, sans-serif'
      : '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: useNewColorTheme ? { fontWeight: 800, fontSize: '3rem', letterSpacing: '-0.02em' } : undefined,
    h2: useNewColorTheme ? { fontWeight: 700, fontSize: '2.25rem', letterSpacing: '-0.01em' } : undefined,
    h3: useNewColorTheme ? { fontWeight: 700, fontSize: '1.75rem', letterSpacing: '-0.01em' } : undefined,
    h4: useNewColorTheme ? { fontWeight: 600, fontSize: '1.5rem' } : undefined,
    h5: useNewColorTheme ? { fontWeight: 600, fontSize: '1.25rem' } : undefined,
    h6: {
      fontWeight: 600,
    },
    button: useNewColorTheme ? {
      fontWeight: 600,
      letterSpacing: '0.05em',
      textTransform: 'uppercase',
    } : undefined,
  },
  shape: {
    borderRadius: useNewColorTheme ? 12 : 8,
  },
  spacing: 8,
  ...(useNewColorTheme ? {
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 16,
            boxShadow: mode === 'dark' 
              ? '0 4px 12px rgba(0,0,0,0.3)'
              : '0 4px 12px rgba(0,0,0,0.05)',
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              boxShadow: mode === 'dark'
                ? '0 8px 24px rgba(0,0,0,0.4)'
                : '0 8px 24px rgba(0,0,0,0.08)',
            },
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          contained: {
            boxShadow: '0 4px 12px rgba(10,122,255,0.3)',
            '&:hover': {
              boxShadow: '0 8px 24px rgba(10,122,255,0.4)',
            },
          },
        },
      },
    },
  } : {}),
})

// Inner component that can access feature flags
function AppContent() {
  const { features } = useFeatureFlags();
  
  // Get dark mode preference from localStorage
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved === 'true';
  });

  // Save to localStorage when changed
  useEffect(() => {
    localStorage.setItem('darkMode', String(darkMode));
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(prev => !prev);
  };

  const theme = useMemo(
    () => createAppTheme(darkMode ? 'dark' : 'light', features.newColorTheme),
    [darkMode, features.newColorTheme]
  )

  return (
    <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
        <Routes>
          {/* Public routes (no layout) */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected routes (with layout) */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route
            path="/*"
            element={
              <Layout>
                <Routes>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/calendar" element={<Calendar />} />
                  <Route path="/plans" element={<TrainingPlans />} />
                  <Route path="/plans/:planId" element={<PlanDetail />} />
                  <Route path="/events/:eventId" element={<EventDetail />} />
                  <Route path="/ai-plan/generate" element={<AITrainingPlanGenerator />} />
                  <Route path="/activities/:activityId" element={<ActivityDetail />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/profile" element={<Settings />} /> {/* Placeholder for now */}
                </Routes>
              </Layout>
            }
          />
        </Routes>
      </Router>
      </ThemeProvider>
    </ThemeContext.Provider>
  )
}

function App() {
  return (
    <FeatureFlagsProvider>
      <AppContent />
    </FeatureFlagsProvider>
  )
}

export default App
