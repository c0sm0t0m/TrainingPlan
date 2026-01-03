import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import TrainingPlans from './pages/TrainingPlans'
import PlanDetail from './pages/PlanDetail'
import Calendar from './pages/Calendar'
import Settings from './pages/SettingsNew'

// TrainingPeaks-inspired theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2196F3', // Blue (matches TrainingPeaks)
    },
    secondary: {
      main: '#FF9800', // Orange
    },
    success: {
      main: '#4CAF50', // Green (running)
    },
    warning: {
      main: '#FF9800', // Orange (cycling)
    },
    error: {
      main: '#F44336', // Red (high load)
    },
    info: {
      main: '#2196F3', // Blue (swimming)
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h6: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 8,
  },
  spacing: 8,
})

function App() {
  return (
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
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/analytics" element={<Dashboard />} /> {/* Placeholder for now */}
                  <Route path="/profile" element={<Settings />} /> {/* Placeholder for now */}
                </Routes>
              </Layout>
            }
          />
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App
