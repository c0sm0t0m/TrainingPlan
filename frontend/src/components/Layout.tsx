import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  AppBar,
  Toolbar,
  Tabs,
  Tab,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Badge,
  Box,
  Typography,
  useMediaQuery,
  useTheme,
  Drawer,
  List,
  ListItem,
  BottomNavigation,
  BottomNavigationAction,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  CalendarMonth,
  FitnessCenter,
  Assessment,
  Notifications,
  Settings as SettingsIcon,
  AccountCircle,
  Logout,
  Menu as MenuIcon,
  Home,
} from '@mui/icons-material'
import { useAuthStore } from '../store/authStore'

const Layout = ({ children }: { children: React.ReactNode }) => {
  const theme = useTheme()
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const menuOpen = Boolean(anchorEl)

  // Determine active tab based on current route
  const getCurrentTab = () => {
    if (location.pathname.startsWith('/dashboard')) return 0
    if (location.pathname.startsWith('/calendar')) return 1
    if (location.pathname.startsWith('/plans')) return 2
    if (location.pathname.startsWith('/analytics')) return 3
    return 0
  }

  // Navigation items
  const navItems = [
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard', value: 0 },
    { label: 'Calendar', icon: <CalendarMonth />, path: '/calendar', value: 1 },
    { label: 'Plans', icon: <FitnessCenter />, path: '/plans', value: 2 },
    { label: 'Analytics', icon: <Assessment />, path: '/analytics', value: 3 },
  ]

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    const item = navItems.find(item => item.value === newValue)
    if (item) navigate(item.path)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Desktop/Tablet AppBar */}
      <AppBar 
        position="sticky" 
        color="default" 
        elevation={1}
        sx={{ 
          bgcolor: 'background.paper',
          borderBottom: 1,
          borderColor: 'divider'
        }}
      >
        <Toolbar>
          {/* Mobile Menu Icon */}
          {isMobile && (
            <IconButton
              color="inherit"
              edge="start"
              onClick={() => setDrawerOpen(true)}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}

          {/* Logo */}
          <Box
            sx={{
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              mr: isMobile ? 0 : 4,
            }}
            onClick={() => navigate('/dashboard')}
          >
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                color: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
              }}
            >
              <span style={{ fontSize: '1.5rem' }}>🏃</span>
              {!isMobile && 'TrainingPlan'}
            </Typography>
          </Box>

          {/* Desktop Navigation Tabs */}
          {!isMobile && (
            <Tabs
              value={getCurrentTab()}
              onChange={handleTabChange}
              sx={{ flexGrow: 1 }}
              TabIndicatorProps={{
                style: {
                  height: 3,
                  borderRadius: '3px 3px 0 0',
                },
              }}
            >
              {navItems.map((item) => (
                <Tab
                  key={item.value}
                  icon={item.icon}
                  iconPosition="start"
                  label={item.label}
                  sx={{
                    minHeight: 64,
                    textTransform: 'none',
                    fontSize: '0.9rem',
                    fontWeight: location.pathname.startsWith(item.path) ? 600 : 400,
                  }}
                />
              ))}
            </Tabs>
          )}

          <Box sx={{ flexGrow: isMobile ? 1 : 0 }} />

          {/* Right Side Icons */}
          {!isMobile && (
            <IconButton color="inherit" sx={{ mr: 1 }}>
              <Badge badgeContent={0} color="error">
                <Notifications />
              </Badge>
            </IconButton>
          )}

          {/* User Avatar Menu */}
          <IconButton
            onClick={(e) => setAnchorEl(e.currentTarget)}
            sx={{ ml: 1 }}
          >
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: 'primary.main',
                fontSize: '0.9rem',
              }}
            >
              {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
            </Avatar>
          </IconButton>

          {/* User Menu Dropdown */}
          <Menu
            anchorEl={anchorEl}
            open={menuOpen}
            onClose={() => setAnchorEl(null)}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            PaperProps={{
              elevation: 3,
              sx: { mt: 1, minWidth: 200 },
            }}
          >
            <Box sx={{ px: 2, py: 1.5, borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="subtitle2" fontWeight={600}>
                {user?.full_name || 'User'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user?.email}
              </Typography>
            </Box>
            <MenuItem
              onClick={() => {
                navigate('/settings')
                setAnchorEl(null)
              }}
            >
              <ListItemIcon>
                <SettingsIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Settings</ListItemText>
            </MenuItem>
            <MenuItem
              onClick={() => {
                navigate('/profile')
                setAnchorEl(null)
              }}
            >
              <ListItemIcon>
                <AccountCircle fontSize="small" />
              </ListItemIcon>
              <ListItemText>Profile</ListItemText>
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <Logout fontSize="small" />
              </ListItemIcon>
              <ListItemText>Logout</ListItemText>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        sx={{
          '& .MuiDrawer-paper': {
            width: 250,
          },
        }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6" fontWeight={700} color="primary.main">
            🏃 TrainingPlan
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {user?.email}
          </Typography>
        </Box>
        <List>
          {navItems.map((item) => (
            <ListItem
              button
              key={item.value}
              onClick={() => {
                navigate(item.path)
                setDrawerOpen(false)
              }}
              sx={{
                bgcolor: location.pathname.startsWith(item.path)
                  ? 'primary.light'
                  : 'transparent',
                '&:hover': {
                  bgcolor: 'action.hover',
                },
              }}
            >
              <ListItemIcon sx={{ color: 'primary.main' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{
                  fontWeight: location.pathname.startsWith(item.path) ? 600 : 400,
                }}
              />
            </ListItem>
          ))}
          <Divider sx={{ my: 1 }} />
          <ListItem
            button
            onClick={() => {
              navigate('/settings')
              setDrawerOpen(false)
            }}
          >
            <ListItemIcon>
              <SettingsIcon />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </ListItem>
          <ListItem button onClick={handleLogout}>
            <ListItemIcon>
              <Logout />
            </ListItemIcon>
            <ListItemText primary="Logout" />
          </ListItem>
        </List>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: isMobile ? 2 : 3,
          pb: isMobile ? 10 : 3, // Extra padding for bottom nav on mobile
        }}
      >
        {children}
      </Box>

      {/* Mobile Bottom Navigation */}
      {isMobile && (
        <BottomNavigation
          value={getCurrentTab()}
          onChange={handleTabChange}
          showLabels
          sx={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            borderTop: 1,
            borderColor: 'divider',
            bgcolor: 'background.paper',
            zIndex: 1000,
          }}
        >
          {navItems.map((item) => (
            <BottomNavigationAction
              key={item.value}
              label={item.label}
              icon={item.icon}
              value={item.value}
            />
          ))}
        </BottomNavigation>
      )}
    </Box>
  )
}

export default Layout
