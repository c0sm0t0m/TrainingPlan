# TrainingPlan - Ranked Improvement Backlog

**Created**: 2026-01-02  
**Last Updated**: 2026-01-06 (Training Plan Activation Enhancements Added)
**Status**: In Progress - 3/4 P0 Complete  
**Total Items**: 35

---

## Priority 0: Critical Issues (Must Fix) - 4 items

### 1. **✅ [P0] [Navigation] - Persistent Global AppBar with Navigation** - COMPLETE

- **Status**: ✅ **IMPLEMENTED** (2026-01-04)

- **Implementation Details**:
  - ✅ Persistent AppBar with sticky positioning
  - ✅ Desktop: Horizontal tabs (Dashboard | Calendar | Plans | Analytics)
  - ✅ Mobile: Hamburger menu → Drawer + Bottom Navigation
  - ✅ Active route highlighting with `useLocation()`
  - ✅ User avatar menu with Settings/Profile/Logout
  - ✅ Dark mode toggle in AppBar
  - ✅ Responsive breakpoints with `useMediaQuery(theme.breakpoints.down('md'))`

- **Files Implemented**:
  - ✅ [frontend/src/components/Layout.tsx](frontend/src/components/Layout.tsx) - Full AppBar, Drawer, BottomNav
  - ✅ Navigation active indicators working
  - ✅ Mobile drawer with sport icons
  - ✅ Bottom navigation for mobile (< 768px)

- **Result**: Navigation works flawlessly. No more orphaned users! 🎉

---

### 2. **⚠️ [P0] [Mobile Experience] - Responsive Calendar for Mobile** - PARTIAL

- **Problem**: Calendar component uses desktop-only layout with 7-column grid. On mobile, tiny cells are unusable, text overlaps, tap targets < 44px, horizontal scroll required.

- **TP Comparison**: TP's mobile calendar uses agenda view (list of days/workouts). Simple but loses weekly overview. They hide most features on mobile = feature parity gap.
### 2. **✅ [P0] [Mobile Experience] - Responsive Calendar for Mobile** - COMPLETE

- **Status**: ✅ **IMPLEMENTED** (2026-01-04)

- **Implementation Details**:
  - ✅ Created `MobileWeekGrid.tsx` - horizontal scrollable 7-day grid
  - ✅ Swipe navigation with `react-swipeable` (left/right to change weeks)
  - ✅ Mobile-specific header with week navigation controls
  - ✅ `WeeklySummaryBar.tsx` - persistent weekly stats (TSS, hours, distance)
  - ✅ Touch targets optimized (56px minimum height)
  - ✅ Responsive breakpoints (`useMediaQuery(theme.breakpoints.down('md'))`)
  - ✅ Separate mobile/desktop render paths
  - ✅ Sport-specific colored workout chips
  - ✅ Completed activities shown in green
  - ✅ Today's date highlighted with primary color
  - ✅ Smooth animations and touch interactions

- **Files Created**:
  - ✅ [frontend/src/pages/calendar/MobileWeekGrid.tsx](frontend/src/pages/calendar/MobileWeekGrid.tsx) - Mobile week grid component
  - ✅ [frontend/src/components/calendar/WeeklySummaryBar.tsx](frontend/src/components/calendar/WeeklySummaryBar.tsx) - Weekly stats header

- **Files Modified**:
  - ✅ [frontend/src/pages/Calendar.tsx](frontend/src/pages/Calendar.tsx) - Added mobile view logic
  - ✅ [frontend/package.json](frontend/package.json) - Added react-swipeable dependency

- **Competitive Advantages**:
  - 🚀 Swipe navigation (TrainingPeaks requires tapping arrows)
  - 🚀 Persistent weekly summary (TP hides stats in submenus)
  - 🚀 Horizontal scroll week grid (TP only has vertical list)
  - 🚀 Visual week planning context (TP loses overview on mobile)
  - 🚀 Touch-optimized (56px targets vs TP's tiny 30-40px buttons)

- **Result**: Mobile calendar now BETTER than TrainingPeaks mobile! Swipeable, visual, fast! 🎉

**Phase 2 Options** (Future Enhancements):
- [ ] Agenda list view tab (alternative to grid)
- [ ] Swipe-to-complete gesture on workout chips  
- [ ] FAB speed dial for quick add workout
- [ ] Pull-to-refresh for Garmin sync
- [ ] Haptic feedback on interactions
- [ ] Bottom sheet workout details (instead of dialog)

---

### 3. **✅ [P0] [Interactions & Feedback] - Empty State Guidance** - COMPLETE

- **Status**: ✅ **IMPLEMENTED** (2026-01-04)

- **Implementation Details**:
  - ✅ Created reusable `EmptyState.tsx` component
  - ✅ Dashboard shows empty state when no activities
  - ✅ TrainingPlans shows empty state with "Create Plan" CTA
  - ✅ Calendar shows empty state when no workouts
  - ✅ Feature flag: `newEmptyStates` for A/B testing
  - ✅ Icons, titles, descriptions, primary & secondary actions
  - ✅ Centered layout with proper spacing

- **Files Implemented**:
  - ✅ [frontend/src/components/EmptyState.tsx](frontend/src/components/EmptyState.tsx) - Reusable component
  - ✅ [frontend/src/pages/Dashboard.tsx](frontend/src/pages/Dashboard.tsx) - Empty state for no activities
  - ✅ [frontend/src/pages/TrainingPlans.tsx](frontend/src/pages/TrainingPlans.tsx) - Empty state for no plans
  - ✅ [frontend/src/pages/Calendar.tsx](frontend/src/pages/Calendar.tsx) - Empty state for no workouts

- **Result**: New users get clear guidance. Onboarding dramatically improved! 🎉

---

### 4. **✅ [P0] [Performance Perception] - Loading States with Skeletons** - COMPLETE
    - MetricCard: `<Skeleton variant="rectangular" height={120} />`
    - PerformanceChart: `<Skeleton variant="rectangular" height={300} />`
  - Use `<Skeleton variant="text" />` for text lines
  - Add subtle pulse animation (default in MUI)
  - Keep loading state for 100-200ms minimum to avoid flash

- **Files**:
  - **Mod✅ [P0] [Performance Perception] - Loading States with Skeletons** - COMPLETE

- **Status**: ✅ **IMPLEMENTED** (2026-01-04)

- **Implementation Details**:
  - ✅ Created skeleton components for all major pages
  - ✅ `DashboardSkeleton.tsx` - Matches MetricCard + chart layouts
  - ✅ `CalendarSkeleton.tsx` - Grid placeholder cells
  - ✅ `TrainingPlansSkeleton.tsx` - Plan card skeletons
  - ✅ Feature flag: `newLoadingSkeletons` for A/B testing
  - ✅ Material-UI Skeleton with pulse animation
  - ✅ Matches actual component dimensions

- **Files Implemented**:
  - ✅ [frontend/src/components/skeletons/DashboardSkeleton.tsx](frontend/src/components/skeletons/DashboardSkeleton.tsx)
  - ✅ [frontend/src/components/skeletons/CalendarSkeleton.tsx](frontend/src/components/skeletons/CalendarSkeleton.tsx)
  - ✅ [frontend/src/components/skeletons/TrainingPlansSkeleton.tsx](frontend/src/components/skeletons/TrainingPlansSkeleton.tsx)
  - ✅ [frontend/src/pages/Dashboard.tsx](frontend/src/pages/Dashboard.tsx) - Uses DashboardSkeleton
  - ✅ [frontend/src/pages/Calendar.tsx](frontend/src/pages/Calendar.tsx) - Uses CalendarSkeleton
  - ✅ [frontend/src/pages/TrainingPlans.tsx](frontend/src/pages/TrainingPlans.tsx) - Uses TrainingPlansSkeleton

- **Result**: App feels 2x faster! No more "Loading..." text. Professional perceived performance! 🎉

- **Files**:
  - **Modify**: [frontend/src/pages/PlanDetail.tsx](frontend/src/pages/PlanDetail.tsx)
  - **Create**: [frontend/src/components/Breadcrumbs.tsx](frontend/src/components/Breadcrumbs.tsx) - Reusable wrapper

---

### 6. **[P1] [Visual Design] - Consistent Card Shadows & Elevation**

- **Problem**: Cards have inconsistent shadows (some elevation={1}, some elevation={3}, some no elevation). Looks unprofessional, lacks visual hierarchy. Hard to distinguish interactive vs static elements.

- **TP Comparison**: TP uses flat design with minimal shadows. Everything looks same priority = no hierarchy. Their approach is outdated (2015-era material design).

- **Impact**: ⭐⭐⭐⭐ (Visual polish, professionalism)

- **Effort**: S (0.5 day)

- **Competitive Advantage**: Yes - modern design vs TP's flat aesthetic

- **Solution**:
  - Standardize Material-UI elevation levels:
    - **Level 0** (flat): Disabled/read-only content
    - **Level 1**: Default cards (Dashboard metrics, plan cards)
    - **Level 2**: Hover state on clickable cards
    - **Level 3**: Active/selected cards, modals
    - **Level 4**: Floating Action Button (FAB)
    - **Level 8**: Dialogs, drawers
  - Add hover effects on interactive cards:
    ```tsx
    sx={{
      transition: 'all 0.2s ease-in-out',
      '&:hover': { 
        elevation: 2,
        transform: 'translateY(-2px)',
        boxShadow: theme.shadows[2]
      }
    }}
    ```
  - Document in theme: Create `cardStyles` constants

- **Files**:
  - **Modify**: [frontend/src/components/MetricCard.tsx](frontend/src/components/MetricCard.tsx)
  - **Modify**: [frontend/src/components/WorkoutCard.tsx](frontend/src/components/WorkoutCard.tsx)
  - **Modify**: [frontend/src/pages/TrainingPlans.tsx](frontend/src/pages/TrainingPlans.tsx#L150-L200)
  - **Create**: [frontend/src/theme/cardStyles.ts](frontend/src/theme/cardStyles.ts) - Standard styles

---

### 7. **[P1] [Data Visualization] - Enhanced Performance Chart with Zones**

- **Problem**: Current PerformanceChart shows CTL/ATL/TSB lines but no context zones (optimal TSB range, overtraining zone). Users don't know if their numbers are good/bad/dangerous.

- **TP Comparison**: TP's Performance Manager Chart (PMC) shows training zones with colored backgrounds (green=good, yellow=caution, red=danger). Helpful but cluttered with too many labels. Chart is their killer feature.

- **Impact**: ⭐⭐⭐⭐⭐ (Core feature, competitive parity)

- **Effort**: M (2-3 days)

- **Competitive Advantage**: Yes if we improve on TP's cluttered approach

- **Solution**:
  - Add colored background zones to chart:
    - **TSB Zones** (horizontal bands):
      - Green: -10 to +5 (optimal)
      - Yellow: -25 to -10, +5 to +15 (caution)
      - Red: < -25 (overtrained), > +15 (detraining)
    - **CTL Zones** (faint vertical bands by time):
      - Base phase, Build phase, Peak phase, Race phase
  - Add zone labels on hover (tooltip)
  - Use Recharts `<ReferenceArea>` for zones
  - Make zones toggleable (settings icon → show/hide zones)
  - Add legend explaining what zones mean
  - Mobile: Simplify to show only TSB zones (drop CTL zones)

- **Files**:
  - **Modify**: [frontend/src/components/PerformanceChart.tsx](frontend/src/components/PerformanceChart.tsx)
  - **Create**: [frontend/src/utils/trainingZones.ts](frontend/src/utils/trainingZones.ts) - Zone calculation logic

---

### 8. **[P1] [Mobile Experience] - Touch-Optimized Workout Cards**

- **Problem**: WorkoutCard component has small tap targets (<44px), crowded layout on mobile, hard to tap edit/delete buttons. Actions require precise taps.

- **TP Comparison**: TP's mobile workout cards are better sized but lack swipe actions. Requires tapping into detail view for all actions = extra steps.

- **Impact**: ⭐⭐⭐⭐ (Mobile usability)

- **Effort**: M (2 days)

- **Competitive Advantage**: Yes - swipe actions beat TP's tap-only

- **Solution**:
  - Increase minimum tap target: 48px (iOS HIG, Material Design guideline)
  - Add swipe gestures (react-swipeable):
    - Swipe left → Reveal delete button (red background)
    - Swipe right → Reveal complete button (green background)
  - Increase card padding on mobile: `theme.spacing(3)`
  - Make entire card tappable (not just title)
  - Add visual feedback: Scale animation on tap
  - Touch ripple effect (Material-UI default)
  - Separate action buttons with more spacing
  - Use `IconButton` with `size="large"` prop

- **Files**:
  - **Modify**: [frontend/src/components/WorkoutCard.tsx](frontend/src/components/WorkoutCard.tsx)
  - **Add dependency**: `react-swipeable` package
  - **Update**: [frontend/package.json](frontend/package.json)

---

### 9. **[P1] [Interactions & Feedback] - Toast Notifications System**

- **Problem**: Success/error messages shown as inline `<Alert>` components that push content down, stay forever, or disappear immediately. No consistent feedback pattern across app.

- **TP Comparison**: TP uses toast notifications but they're slow (3-5 second delay), stack badly, and sometimes block important UI. Message text is too technical ("Error 500: Internal Server Error").

- **Impact**: ⭐⭐⭐⭐ (User feedback, polish)

- **Effort**: M (1.5 days)

- **Competitive Advantage**: Yes - better UX than TP's slow toasts

- **Solution**:
  - Create global `<Snackbar>` system using Zustand store:
    ```tsx
    // Toast store
    interface Toast {
      id: string;
      message: string;
      severity: 'success' | 'error' | 'warning' | 'info';
      duration?: number;
    }
    ```
  - Position: Bottom-center on desktop, top-center on mobile
  - Auto-dismiss: 4 seconds (success), 6 seconds (error)
  - Stack multiple toasts vertically
  - Slide-in animation
  - User-friendly messages:
    - ❌ "Error 500"
    - ✅ "Failed to save workout. Please try again."
  - Action button for errors: "Retry" or "Dismiss"
  - Use Material-UI `<Snackbar>` + `<Alert>` combo

- **Files**:
  - **Create**: [frontend/src/store/toastStore.ts](frontend/src/store/toastStore.ts)
  - **Create**: [frontend/src/components/ToastContainer.tsx](frontend/src/components/ToastContainer.tsx)
  - **Modify**: [frontend/src/App.tsx](frontend/src/App.tsx#L40-L60) - Add ToastContainer
  - **Update**: All API call error handling across pages

---

### 10. **[P1] [Navigation] - Floating Action Button for Primary Actions**

- **Problem**: Primary actions (Add Workout, Create Plan) are in page headers, requiring scroll to top. On mobile, often off-screen. Users don't discover features.

- **TP Comparison**: TP buries "Create" actions in dropdowns and menus. 3-4 clicks to add a workout. Their UX is click-heavy and slow.

- **Impact**: ⭐⭐⭐⭐ (Feature discoverability, mobile UX)

- **Effort**: S (1 day)

- **Competitive Advantage**: Yes - faster than TP's menu-based approach

- **Solution**:
  - Add Material-UI `<Fab>` component to key pages:
    - **Calendar**: FAB with `<AddIcon>` → Add Workout dialog
    - **Plans**: FAB with `<AddIcon>` → Create Plan dialog
    - **Dashboard**: FAB with `<SyncIcon>` → Sync Activities
  - Position: Fixed bottom-right
    - Desktop: `bottom: 24px, right: 24px`
    - Mobile: `bottom: 72px, right: 16px` (above bottom nav)
  - Primary color background
  - Tooltip on hover: "Add Workout"
  - Extended FAB on desktop: Shows text + icon
  - Hide when scrolling down, show when scrolling up

- **Files**:
  - **Modify**: [frontend/src/pages/Calendar.tsx](frontend/src/pages/Calendar.tsx#L400-L500)
  - **Modify**: [frontend/src/pages/TrainingPlans.tsx](frontend/src/pages/TrainingPlans.tsx#L200-L250)
  - **Modify**: [frontend/src/pages/Dashboard.tsx](frontend/src/pages/Dashboard.tsx#L180-L220)
  - **Create**: [frontend/src/hooks/useFabVisibility.ts](frontend/src/hooks/useFabVisibility.ts) - Scroll detection

---

### 11. **[P1] [Visual Design] - Sport-Specific Color Coding System**

- **Problem**: Workouts and activities use generic colors. Can't quickly distinguish running vs cycling vs swimming at a glance. Calendar looks monochrome.

- **TP Comparison**: TP uses sport colors (red=run, orange=bike, blue=swim) but they're inconsistent across pages. Colors are washed out and hard to distinguish.

- **Impact**: ⭐⭐⭐⭐ (Visual hierarchy, quick scanning)

- **Effort**: S (1 day)

- **Competitive Advantage**: Yes - consistent colors vs TP's inconsistency

- **Solution**:
  - Create standardized color palette in theme:
    ```tsx
    const sportColors = {
      running: '#4CAF50',    // Green
      cycling: '#FF9800',     // Orange
      swimming: '#2196F3',    // Blue
      strength: '#9C27B0',    // Purple
      other: '#757575',       // Gray
    }
    ```
  - Apply colors to:
    - WorkoutCard left border (4px colored stripe)
    - Calendar cells (colored background, 10% opacity)
    - Chips/badges (sport type indicators)
    - Chart lines (activity types)
  - Add sport icons with matching colors:
    - 🏃 Run, 🚴 Bike, 🏊 Swim, 💪 Strength
  - Document in style guide

- **Files**:
  - **Modify**: [frontend/src/utils/sportColors.ts](frontend/src/utils/sportColors.ts) - Already exists, enhance
  - **Modify**: [frontend/src/components/WorkoutCard.tsx](frontend/src/components/WorkoutCard.tsx)
  - **Modify**: [frontend/src/pages/Calendar.tsx](frontend/src/pages/Calendar.tsx#L500-L600)
  - **Update**: [frontend/src/App.tsx](frontend/src/App.tsx#L10-L30) - Add to theme

---

### 12. **[P1] [Data Visualization] - Weekly Training Load Bar Chart**

- **Problem**: Dashboard shows CTL/ATL/TSB chart but no weekly breakdown. Users can't see "I did 3 runs, 2 bikes this week, totaling 450 TSS". No granular view of training volume.

- **TP Comparison**: TP has weekly volume chart but it's buried in separate "Reports" section. Requires 3 clicks to access. Not on main dashboard = low discoverability.

- **Impact**: ⭐⭐⭐⭐ (Training tracking, motivation)

- **Effort**: M (2 days)

- **Competitive Advantage**: Yes - better placement than TP

- **Solution**:
  - Add stacked bar chart to Dashboard (below performance chart)
  - X-axis: Weeks (last 12 weeks)
  - Y-axis: TSS
  - Stacked bars by sport type:
    - Green: Running TSS
    - Orange: Cycling TSS
    - Blue: Swimming TSS
    - Purple: Strength TSS
  - Hover tooltip: "Week of Dec 25: 450 TSS (200 run, 150 bike, 100 swim)"
  - Toggle between views: TSS | Hours | Distance
  - Use Recharts `<BarChart>` with `<Bar stackId="a">`
  - Mobile: Show last 6 weeks only

- **Files**:
  - **Create**: [frontend/src/components/WeeklyLoadChart.tsx](frontend/src/components/WeeklyLoadChart.tsx)
  - **Modify**: [frontend/src/pages/Dashboard.tsx](frontend/src/pages/Dashboard.tsx#L180-L220)
  - **Backend**: Create endpoint `/garmin/weekly-volume` - **backend/src/api/routes/garmin.py**

---

### 13. **[P1] [Mobile Experience] - Bottom Navigation for Mobile**

- **Problem**: Mobile navigation requires hamburger menu → drawer → tap link (3 steps). Primary actions buried. Thumb zone at top of screen = uncomfortable reach.

- **TP Comparison**: TP has no bottom nav on mobile. Everything in hamburger menu = poor mobile UX. They treat mobile as afterthought.

- **Impact**: ⭐⭐⭐⭐⭐ (Mobile usability, matches iOS/Android patterns)

- **Effort**: M (1.5 days)

- **Competitive Advantage**: Yes - mobile-first approach vs TP

- **Solution**:
  - Add Material-UI `<BottomNavigation>` for screens < 768px
  - 4 primary tabs (iOS guideline: max 5):
    - Home (Dashboard)
    - Calendar
    - Plans
    - Profile/Settings
  - Fixed position: `bottom: 0`
  - Active indicator: Primary color + icon filled
  - Safe area padding for iPhone notch: `env(safe-area-inset-bottom)`
  - Hide on scroll down (show content), show on scroll up
  - Height: 56px (Material Design spec)
  - Label + icon layout

- **Files**:
  - **Modify**: [frontend/src/components/Layout.tsx](frontend/src/components/Layout.tsx#L200-L300)
  - **Add**: Conditional rendering based on `isMobile`
  - **Update CSS**: [frontend/src/index.css](frontend/src/index.css) - Safe area padding

---

### 14. **[P1] [Interactions & Feedback] - Optimistic UI Updates**

- **Problem**: After completing a workout, UI waits for server response before updating (500-1000ms delay). Feels sluggish. User clicks button, nothing happens, clicks again = duplicate requests.

- **TP Comparison**: TP has slow server updates and no optimistic UI. Every action feels like "submit form → wait → refresh page". Feels like 2010-era web app.

- **Impact**: ⭐⭐⭐⭐ (Perceived performance, responsiveness)

- **Effort**: M (2 days)

- **Competitive Advantage**: Yes - modern SPA feel vs TP's slow updates

- **Solution**:
  - Implement optimistic updates for common actions:
    - **Complete workout**: Update UI immediately, revert on error
    - **Delete workout**: Remove from list, revert on error
    - **Add workout**: Add to list with "pending" state, update on success
  - Pattern:
    ```tsx
    const handleComplete = async (workoutId: number) => {
      // 1. Optimistic update
      setWorkouts(prev => 
        prev.map(w => w.id === workoutId 
          ? { ...w, is_completed: true } 
          : w
        )
      )
      
      try {
        // 2. Server update
        await api.patch(`/workouts/${workoutId}/complete`)
      } catch (error) {
        // 3. Revert on error
        setWorkouts(prev => 
          prev.map(w => w.id === workoutId 
            ? { ...w, is_completed: false } 
            : w
          )
        )
        showToast('Failed to complete workout', 'error')
      }
    }
    ```
  - Add loading indicator for pending items (spinner icon)

- **Files**:
  - **Modify**: [frontend/src/pages/Calendar.tsx](frontend/src/pages/Calendar.tsx#L300-L400)
  - **Modify**: [frontend/src/components/WorkoutCard.tsx](frontend/src/components/WorkoutCard.tsx)
  - **Create**: [frontend/src/hooks/useOptimisticUpdate.ts](frontend/src/hooks/useOptimisticUpdate.ts)

---

### 15. **[P1] [Visual Design] - Dark Mode Support**

- **Problem**: No dark mode option. Bright white screens at night strain eyes. Many athletes train early morning/late evening = painful bright screens.

- **TP Comparison**: TP added dark mode in 2023 but it's incomplete. Many components still use white backgrounds. Inconsistent implementation. Better than nothing.

- **Impact**: ⭐⭐⭐⭐ (User comfort, retention)

- **Effort**: L (3-4 days)

- **Competitive Advantage**: No - table stakes in 2026

- **Solution**:
  - Add theme toggle in Settings page
  - Store preference in localStorage: `theme: 'light' | 'dark'`
  - Create dark theme palette:
    ```tsx
    const darkTheme = createTheme({
      palette: {
        mode: 'dark',
        primary: { main: '#64B5F6' },     // Lighter blue
        secondary: { main: '#FFB74D' },   // Lighter orange
        background: {
          default: '#121212',             // Dark gray
          paper: '#1E1E1E',               // Slightly lighter
        },
        text: {
          primary: '#FFFFFF',
          secondary: '#B0B0B0',
        },
      },
    })
    ```
  - Use Material-UI's `ThemeProvider` toggle
  - Test all components for contrast (WCAG AA: 4.5:1 ratio)
  - Chart colors: Use lighter versions in dark mode

- **Files**:
  - **Modify**: [frontend/src/App.tsx](frontend/src/App.tsx#L10-L50)
  - **Create**: [frontend/src/theme/darkTheme.ts](frontend/src/theme/darkTheme.ts)
  - **Modify**: [frontend/src/pages/SettingsNew.tsx](frontend/src/pages/SettingsNew.tsx)
  - **Create**: [frontend/src/store/themeStore.ts](frontend/src/store/themeStore.ts)

---

## Priority 2: Polish & Improvements - 17 items

### 16. **[P2] [Training Plans] - Smart Plan Activation with Date Selection**

- **Problem**: Current activation is a simple toggle switch, but activating a training plan is a significant action that should include:
  - Start/end date selection (align with events/races)
  - Matching past activities to plan sessions
  - Prognostic TSS calculations for future sessions
  - Clear confirmation of the action's impact

- **TP Comparison**: TP requires selecting a start date when assigning a plan to an athlete, making the commitment explicit. Their approach forces users to think about timing.

- **Impact**: ⭐⭐⭐⭐⭐ (Core workflow, better planning)

- **Effort**: L (4-5 days)

- **Competitive Advantage**: Yes - smarter activation with predictive features

- **Solution**:
  - Replace toggle switch with "Activate Plan" button
  - Show activation dialog with:
    - **Date Selection**:
      - Start date picker (default: today)
      - Optional: Link to event/race (auto-calculate end date)
      - Show plan duration and calculated end date
    - **Impact Preview**:
      - "X sessions will be in the past" warning
      - "System will attempt to match Y existing activities"
      - "Future sessions will contribute Z TSS to weekly forecasts"
    - **Confirmation**: Clear "Activate Plan" and "Cancel" buttons
  - **Backend Processing** (on activation):
    - Match past plan sessions to existing Garmin activities by:
      - Date proximity (within 1-2 days)
      - Sport type matching
      - Duration/distance similarity scoring
      - Manual review/override option (future)
    - Calculate prognostic weekly TSS including planned sessions
    - Store activation metadata (start_date, matched_activities count)
  - **Deactivation**:
    - Show warning dialog: "Planned workouts will disappear from calendar"
    - Confirmation required
  - **Visual Enhancement**:
    - Active plans show start date and progress bar
    - "X days active, Y days remaining" indicator

- **Files**:
  - **Modify**: [frontend/src/pages/TrainingPlans.tsx](frontend/src/pages/TrainingPlans.tsx) - Remove toggle, add dialog
  - **Create**: [frontend/src/components/PlanActivationDialog.tsx](frontend/src/components/PlanActivationDialog.tsx)
  - **Modify**: [backend/src/api/routes/training_plans.py](backend/src/api/routes/training_plans.py) - Accept start_date param
  - **Create**: [backend/src/services/plan_activation_service.py](backend/src/services/plan_activation_service.py) - Matching logic
  - **Modify**: [backend/src/models/training_plan.py](backend/src/models/training_plan.py) - Add activation_date column
  - **Create Migration**: `alembic revision -m "add_activation_date_to_training_plans"`

- **Future Enhancements**:
  - AI-powered activity matching with confidence scores
  - Bulk activity assignment UI
  - "Shift plan dates" tool (adjust all workouts by X days)
  - Integration with calendar drag-drop to reschedule workouts
  - Prognostic TSS shown in calendar tooltips
  - Weekly TSS targets vs actual tracking

---

### 17. **[P2] [Health Data] - Daily Resting Heart Rate Sync**

- **Problem**: Currently syncing HRV data and activity HR data, but missing daily resting HR which Garmin tracks separately. Resting HR is a key recovery indicator that changes gradually and helps predict illness, overtraining, and recovery status.

- **TP Comparison**: TP shows resting HR in health metrics but doesn't track trends or provide insights. Just displays the number without context.

- **Impact**: ⭐⭐⭐⭐ (Recovery tracking, overtraining detection)

- **Effort**: M (2 days)

- **Competitive Advantage**: Yes - trend analysis and insights vs TP's static display

- **Solution**:
  - Add resting HR to health data sync (similar to HRV sync):
    - Fetch daily resting HR from Garmin API
    - Store in new table `garmin_resting_hr` with fields:
      - `calendar_date` (primary key with user_id)
      - `resting_hr` (integer, bpm)
      - `last_night_avg` (from sleep tracking)
      - `user_set_value` (manual override if available)
      - `measurement_time_gmt` (when measured)
      - `raw_data` (JSON for full response)
  - Add to `/sync-health-data` endpoint
  - Display resting HR trend chart on Dashboard/Analytics:
    - Line chart showing 30-day trend
    - Highlight 7-day average as baseline
    - Alert if 5+ bpm above baseline (potential illness/overtraining)
    - Color coding: green (normal), yellow (elevated), red (very high)
  - Show correlation with HRV (both are recovery indicators)

- **Files**:
  - **Backend**:
    - **Create**: [backend/alembic/versions/XXX_add_resting_hr_table.py](backend/alembic/versions/)
    - **Create**: [backend/src/models/garmin_resting_hr.py](backend/src/models/garmin_resting_hr.py)
    - **Modify**: [backend/src/services/garmin_service.py](backend/src/services/garmin_service.py#L400-L500) - Add `sync_resting_hr_data()` method
    - **Modify**: [backend/src/api/routes/garmin.py](backend/src/api/routes/garmin.py#L200-L300) - Update `/sync-health-data` endpoint
  - **Frontend**:
    - **Create**: [frontend/src/components/RestingHRChart.tsx](frontend/src/components/RestingHRChart.tsx)
    - **Modify**: [frontend/src/pages/Dashboard.tsx](frontend/src/pages/Dashboard.tsx) - Add resting HR card
    - **Modify**: [frontend/src/pages/Analytics.tsx](frontend/src/pages/Analytics.tsx) - Add detailed trend analysis

---

### 18. **[P2] [Visual Design] - Typography Hierarchy**

- **Problem**: Inconsistent font sizes, weights across pages. Headings use different variants (h3, h4, h5) for same level. No clear visual hierarchy. Hard to scan pages.

- **TP Comparison**: TP has decent typography but it's generic. System fonts only. No personality or brand.

- **Impact**: ⭐⭐⭐ (Visual polish, readability)

- **Effort**: S (1 day)

- **Competitive Advantage**: Yes - custom font vs TP's generic system fonts

- **Solution**:
  - Standardize Material-UI typography variants:
    - **h3**: Page titles (Dashboard, Calendar, etc.)
    - **h5**: Section headers (Recent Activities, Metrics)
    - **h6**: Card titles
    - **body1**: Main text
    - **body2**: Secondary text
    - **caption**: Metadata, timestamps
  - Add custom font: Inter (Google Fonts) - already configured
  - Set consistent weights:
    - h3-h6: 600 (semibold)
    - body1: 400 (regular)
    - body2: 400
  - Document in style guide

- **Files**:
  - **Modify**: [frontend/src/App.tsx](frontend/src/App.tsx#L20-L40) - Theme typography
  - **Create**: [frontend/docs/STYLE_GUIDE.md](frontend/docs/STYLE_GUIDE.md)
  - **Update**: All page components to use consistent variants

---

### 19. **[P2] [Navigation] - Quick Actions Menu**

- **Problem**: Common actions (Sync Garmin, Create Workout, View Analytics) require navigating to different pages. No shortcuts for power users.

- **TP Comparison**: TP has "Quick Add" button in header but it's limited to workouts only. No shortcuts for other common actions.

- **Impact**: ⭐⭐⭐ (Power user efficiency)

- **Effort**: M (2 days)

- **Competitive Advantage**: Yes - more comprehensive than TP

- **Solution**:
  - Add "Quick Actions" button in AppBar (lightning icon)
  - Click → Menu with common actions:
    - 🔄 Sync Garmin Activities
    - ➕ Add Workout
    - 📅 Create Training Plan
    - 📊 View Reports
    - ⚙️ Settings
  - Keyboard shortcuts:
    - `Cmd/Ctrl + K`: Open quick actions
    - `Cmd/Ctrl + N`: New workout
    - `Cmd/Ctrl + Shift + S`: Sync activities
  - Command palette style (similar to VS Code)

- **Files**:
  - **Create**: [frontend/src/components/QuickActionsMenu.tsx](frontend/src/components/QuickActionsMenu.tsx)
  - **Modify**: [frontend/src/components/Layout.tsx](frontend/src/components/Layout.tsx#L100-L150)
  - **Create**: [frontend/src/hooks/useKeyboardShortcuts.ts](frontend/src/hooks/useKeyboardShortcuts.ts)

---

### 20. **[P2] [Mobile Experience] - Swipe Navigation Between Pages**

- **Problem**: No gesture navigation on mobile. Users must tap back button or bottom nav. Feels less native than mobile apps.

- **TP Comparison**: TP has no swipe navigation. Feels like mobile website, not app.

- **Impact**: ⭐⭐⭐ (Mobile native feel)

- **Effort**: M (2 days)

- **Competitive Advantage**: Yes - native app feel

- **Solution**:
  - Add swipe gestures for page navigation:
    - **Swipe right**: Go back (browser history)
    - **Swipe left on Calendar**: Next week
    - **Swipe right on Calendar**: Previous week
  - Use `react-swipeable` or native touch events
  - Visual feedback: Page slides with finger during swipe
  - Threshold: 50px swipe distance to trigger
  - Velocity-based: Fast swipe = complete action, slow = cancel
  - Disable swipe when:
    - Modal open
    - Drawer open
    - Scrolling horizontally

- **Files**:
  - **Modify**: [frontend/src/pages/Calendar.tsx](frontend/src/pages/Calendar.tsx#L100-L200)
  - **Create**: [frontend/src/hooks/useSwipeNavigation.ts](frontend/src/hooks/useSwipeNavigation.ts)
  - **Add dependency**: `react-swipeable`

---

### 21. **[P2] [Interactions & Feedback] - Confirmation Dialogs for Destructive Actions**

- **Problem**: Deleting workouts/plans has no confirmation. Easy to accidentally delete = data loss. Undo not available.

- **TP Comparison**: TP has confirmation dialogs but they're generic browser alerts (ugly, not branded). Text is too technical.

- **Impact**: ⭐⭐⭐⭐ (Data safety)

- **Effort**: S (1 day)

- **Competitive Advantage**: No - table stakes

- **Solution**:
  - Add Material-UI `<Dialog>` for destructive actions:
    - Delete workout
    - Delete training plan
    - Clear all activities
  - Dialog design:
    - Title: "Delete Workout?"
    - Body: "This will permanently delete [Workout Name]. This cannot be undone."
    - Buttons: "Cancel" (default), "Delete" (red, danger)
  - Keyboard: `Escape` = Cancel, `Enter` = Confirm
  - Focus trap: Can't interact with background
  - Dim background (backdrop)

- **Files**:
  - **Create**: [frontend/src/components/ConfirmDialog.tsx](frontend/src/components/ConfirmDialog.tsx)
  - **Modify**: [frontend/src/pages/Calendar.tsx](frontend/src/pages/Calendar.tsx#L400-L500)
  - **Modify**: [frontend/src/pages/TrainingPlans.tsx](frontend/src/pages/TrainingPlans.tsx#L200-L250)

---

### 22. **[P2] [Performance Perception] - Progressive Image Loading**

- **Problem**: If user profile photos or activity maps added in future, large images will block rendering. No lazy loading strategy.

- **TP Comparison**: TP loads all images immediately = slow page loads. Activity map images are 1-2MB each.

- **Impact**: ⭐⭐⭐ (Performance, perceived speed)

- **Effort**: M (1.5 days)

- **Competitive Advantage**: Yes - faster than TP

- **Solution**:
  - Implement progressive image loading:
    1. Show low-res blur placeholder (inline base64)
    2. Load full image in background
    3. Fade transition when loaded
  - Use Intersection Observer for lazy loading:
    - Only load images when in viewport
    - 200px margin (start loading before visible)
  - Libraries: `react-lazy-load-image-component`
  - Blur-up technique:
    ```tsx
    <LazyLoadImage
      src={fullResUrl}
      placeholderSrc={thumbnailUrl}
      effect="blur"
    />
    ```
  - For activity maps: Use Leaflet tile loading

- **Files**:
  - **Create**: [frontend/src/components/LazyImage.tsx](frontend/src/components/LazyImage.tsx)
  - **Add dependency**: `react-lazy-load-image-component`
  - **Update**: [frontend/package.json](frontend/package.json)

---

### 23. **[P2] [Data Visualization] - Activity Heatmap Calendar**

- **Problem**: No visual representation of training consistency. Can't see "I trained 5 days/week in December". No GitHub-style contribution graph.

- **TP Comparison**: TP has no heatmap view. Their calendar is list-based only.

- **Impact**: ⭐⭐⭐⭐ (Motivation, gamification)

- **Effort**: M (2-3 days)

- **Competitive Advantage**: Yes - Strava has this, TP doesn't

- **Solution**:
  - Add heatmap calendar to Dashboard (similar to GitHub contributions):
    - Grid of days (365 days = 52 weeks × 7 days)
    - Each cell colored by TSS:
      - Gray: 0 TSS (rest day)
      - Light green: 1-50 TSS
      - Green: 51-100 TSS
      - Dark green: 101-200 TSS
      - Very dark green: 200+ TSS
  - Hover tooltip: "Monday, Dec 25: 150 TSS (2 workouts)"
  - Click cell → Jump to that day in Calendar
  - Show last 365 days, scrollable
  - Responsive: Mobile shows last 90 days only

- **Files**:
  - **Create**: [frontend/src/components/ActivityHeatmap.tsx](frontend/src/components/ActivityHeatmap.tsx)
  - **Modify**: [frontend/src/pages/Dashboard.tsx](frontend/src/pages/Dashboard.tsx#L180-L220)
  - **Backend**: Endpoint `/garmin/daily-tss` - **backend/src/api/routes/garmin.py**

---

### 24. **[P2] [Visual Design] - Animated Metric Changes**

- **Problem**: When CTL/ATL/TSB values update, they jump instantly. No visual feedback that change occurred. Easy to miss updates.

- **TP Comparison**: TP has no animations. Values just change. Feels static and unresponsive.

- **Impact**: ⭐⭐⭐ (Polish, user feedback)

- **Effort**: S (1 day)

- **Competitive Advantage**: Yes - modern polish

- **Solution**:
  - Add count-up animation for metric values:
    - When value changes, animate from old → new value
    - Duration: 800ms ease-out
  - Use `react-countup` library
  - Add subtle color flash:
    - Green flash: Value increased
    - Red flash: Value decreased
  - Only animate on user-triggered updates (not initial load)
  - Example:
    ```tsx
    <CountUp
      start={prevValue}
      end={newValue}
      duration={0.8}
      separator=","
      decimals={0}
    />
    ```

- **Files**:
  - **Modify**: [frontend/src/components/MetricCard.tsx](frontend/src/components/MetricCard.tsx)
  - **Add dependency**: `react-countup`
  - **Update**: [frontend/package.json](frontend/package.json)

---

### 25. **[P2] [Interactions & Feedback] - Drag-and-Drop Workout Scheduling**

- **Problem**: Moving workouts between days requires: Click workout → Edit → Change date → Save (4 steps). Slow and cumbersome.

- **TP Comparison**: TP has drag-and-drop on desktop calendar. Implementation is buggy (workouts sometimes disappear). Mobile has no drag-and-drop.

- **Impact**: ⭐⭐⭐⭐ (Workflow efficiency)

- **Effort**: L (3-4 days)

- **Competitive Advantage**: Yes if we make it work reliably

- **Solution**:
  - Implement drag-and-drop on Calendar:
    - Desktop only (mobile uses swipe to edit)
    - Drag workout card to different day cell
    - Visual feedback:
      - Card follows cursor during drag
      - Target cell highlights (blue border)
      - Drop zone indicator
    - On drop: Update workout date via API
    - Optimistic update (instant UI, revert on error)
  - Library: `react-beautiful-dnd` or `dnd-kit`
  - Constraints:
    - Can't drag to past dates
    - Can't drag across different training plans
    - Show warning if date is > 1 week away

- **Files**:
  - **Modify**: [frontend/src/pages/Calendar.tsx](frontend/src/pages/Calendar.tsx#L400-L600)
  - **Add dependency**: `@dnd-kit/core`, `@dnd-kit/sortable`
  - **Update**: [frontend/package.json](frontend/package.json)

---

### 26. **[P2] [Navigation] - Recent Activity Quick View**

- **Problem**: To see latest activity details, must: Dashboard → Scroll to activities list → Click activity (3 steps). No quick preview.

- **TP Comparison**: TP has activity feed but it's in separate tab. Requires navigation. No quick preview in main dashboard.

- **Impact**: ⭐⭐⭐ (Convenience)

- **Effort**: M (2 days)

- **Competitive Advantage**: Yes - better than TP

- **Solution**:
  - Add "Recent Activities" widget to Dashboard:
    - Show last 5 activities
    - Compact card layout:
      - Sport icon + name
      - Date & time
      - Key metrics (distance, TSS)
      - Mini map thumbnail (if GPS data)
    - Click activity → Drawer opens with full details
    - Drawer includes:
      - Full map
      - All metrics
      - Heart rate chart
      - Power chart (if cycling)
      - Edit button
  - Use Material-UI `<Drawer>` component
  - Swipe down to close (mobile)

- **Files**:
  - **Create**: [frontend/src/components/RecentActivitiesWidget.tsx](frontend/src/components/RecentActivitiesWidget.tsx)
  - **Create**: [frontend/src/components/ActivityDetailDrawer.tsx](frontend/src/components/ActivityDetailDrawer.tsx)
  - **Modify**: [frontend/src/pages/Dashboard.tsx](frontend/src/pages/Dashboard.tsx#L180-L220)

---

### 27. **[P2] [Mobile Experience] - Pull-to-Refresh**

- **Problem**: No way to refresh data on mobile without clicking sync button. Native mobile apps use pull-to-refresh pattern.

- **TP Comparison**: TP has no pull-to-refresh. Must manually click refresh button.

- **Impact**: ⭐⭐⭐ (Mobile UX, native feel)

- **Effort**: S (1 day)

- **Competitive Advantage**: Yes - native app feel

- **Solution**:
  - Add pull-to-refresh on mobile pages:
    - Dashboard
    - Calendar
    - Training Plans list
  - Implementation:
    - Pull down from top → Show loading spinner
    - Release → Trigger data refresh
    - Spinner shows progress
    - Haptic feedback on trigger (if supported)
  - Library: `react-pull-to-refresh` or custom implementation
  - Design:
    - Spinner matches app theme (primary color)
    - Smooth animation
    - Works with page scroll (not conflicting)

- **Files**:
  - **Modify**: [frontend/src/pages/Dashboard.tsx](frontend/src/pages/Dashboard.tsx#L50-L100)
  - **Modify**: [frontend/src/pages/Calendar.tsx](frontend/src/pages/Calendar.tsx#L100-L150)
  - **Create**: [frontend/src/hooks/usePullToRefresh.ts](frontend/src/hooks/usePullToRefresh.ts)

---

### 28. **[P2] [Visual Design] - Micro-interactions and Animations**

- **Problem**: UI feels static. No feedback on interactions (button clicks, hovers, state changes). Lacks modern polish.

- **TP Comparison**: TP has minimal animations. Feels dated and unresponsive. No delight factor.

- **Impact**: ⭐⭐⭐ (Polish, perceived quality)

- **Effort**: M (2 days)

- **Competitive Advantage**: Yes - modern feel

- **Solution**:
  - Add subtle animations throughout:
    - **Button clicks**: Scale down (0.95) on press
    - **Card hovers**: Lift up 2px, increase shadow
    - **Page transitions**: Fade in (300ms)
    - **Modal open**: Scale from 0.9 to 1.0 + fade
    - **List items**: Stagger animation (each 50ms delay)
    - **Success actions**: Checkmark animation (SVG path)
  - Use Framer Motion library for complex animations
  - Keep animations fast (<300ms) for responsiveness
  - Respect `prefers-reduced-motion` media query
  - Examples:
    ```tsx
    // Button press
    sx={{
      transition: 'transform 0.1s',
      '&:active': { transform: 'scale(0.95)' }
    }}
    
    // Page transition
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
    ```

- **Files**:
  - **Add dependency**: `framer-motion`
  - **Update**: All button components
  - **Create**: [frontend/src/components/animations/](frontend/src/components/animations/) - Reusable animation variants

---

### 29. **[P2] [Interactions & Feedback] - Undo/Redo for Accidental Deletes**

- **Problem**: After deleting workout, no way to undo. Must recreate from scratch = frustrating. Toast says "Deleted" but no recovery option.

- **TP Comparison**: TP has no undo feature. Once deleted, gone forever (unless you contact support).

- **Impact**: ⭐⭐⭐⭐ (User confidence, safety)

- **Effort**: M (2 days)

- **Competitive Advantage**: Yes - TP doesn't have this

- **Solution**:
  - Add "Undo" action to delete toast:
    - Toast message: "Workout deleted" + "Undo" button
    - Undo available for 10 seconds
    - After 10 seconds → Permanent delete (backend API call)
    - During 10 seconds → Keep in memory, don't call API yet
  - Implementation:
    ```tsx
    const handleDelete = (workout) => {
      // Remove from UI
      setWorkouts(prev => prev.filter(w => w.id !== workout.id))
      
      // Show toast with undo
      showToast({
        message: 'Workout deleted',
        action: {
          label: 'Undo',
          onClick: () => {
            setWorkouts(prev => [...prev, workout])
            clearTimeout(deleteTimer)
          }
        }
      })
      
      // Schedule permanent delete after 10s
      const timer = setTimeout(() => {
        api.delete(`/workouts/${workout.id}`)
      }, 10000)
    }
    ```
  - Visual feedback: Workout fades out, slides back in on undo

- **Files**:
  - **Modify**: [frontend/src/store/toastStore.ts](frontend/src/store/toastStore.ts)
  - **Modify**: [frontend/src/pages/Calendar.tsx](frontend/src/pages/Calendar.tsx#L400-L500)
  - **Create**: [frontend/src/hooks/useUndoableAction.ts](frontend/src/hooks/useUndoableAction.ts)

---

## Priority 3: Future Vision & Innovation - 3 items

### 30. **[P3] [Innovation] - AI Training Plan Generator**

- **Problem**: Creating training plans is time-consuming. Users must manually add 50-100 workouts. No intelligent suggestions based on user's fitness level.

- **TP Comparison**: TP has "Training Plan Builder" but it's manual. They have some pre-made plans but they're generic (not personalized). No AI.

- **Impact**: ⭐⭐⭐⭐⭐ (Killer feature, differentiation)

- **Effort**: L (1-2 weeks)

- **Competitive Advantage**: YES - major differentiator

- **Solution**:
  - AI-powered plan generator with user inputs:
    - Goal: Marathon, Half Marathon, Olympic Tri, etc.
    - Current fitness: CTL score or recent activity data
    - Time available: Hours per week
    - Experience level: Beginner, Intermediate, Advanced
    - Race date: Target event date
  - Use Claude/GPT-4 API to generate periodized plan:
    - Base → Build → Peak → Taper phases
    - Progressive overload
    - Recovery weeks every 3-4 weeks
    - Sport-specific workouts with TSS targets
  - Show preview → User can edit → Save to calendar
  - Backend endpoint: `/training-plans/generate-ai`
  - Cost: ~$0.10-0.50 per plan generation
  - Fallback: Rule-based generator if AI fails

- **Files**:
  - **Create**: [backend/src/services/ai_plan_generator.py](backend/src/services/ai_plan_generator.py)
  - **Create**: [backend/src/api/routes/ai_plans.py](backend/src/api/routes/ai_plans.py)
  - **Create**: [frontend/src/components/AIPlanGenerator.tsx](frontend/src/components/AIPlanGenerator.tsx)
  - **Modify**: [frontend/src/pages/TrainingPlans.tsx](frontend/src/pages/TrainingPlans.tsx#L100-L150)
  - **Add dependency**: OpenAI/Anthropic Python SDK

---

### 31. **[P3] [Innovation] - Social Features & Training Partners**

- **Problem**: Training is isolating. No way to share progress, compete with friends, or find training partners. Strava has this, TrainingPlan doesn't.

- **TP Comparison**: TP has zero social features. It's enterprise software for coaches, not social. Strava dominates social fitness.

- **Impact**: ⭐⭐⭐⭐⭐ (Retention, viral growth)

- **Effort**: L (2-3 weeks)

- **Competitive Advantage**: YES - combine TP analytics + Strava social

- **Solution**:
  - Phase 1: Basic social features
    - User profiles (public/private)
    - Follow/unfollow users
    - Activity feed (see friends' workouts)
    - Kudos/reactions on activities
    - Comments on activities
  - Phase 2: Training partners
    - Find users with similar goals (same race, similar pace)
    - Create training groups
    - Group challenges (most TSS this month)
    - Leaderboards
  - Phase 3: Coach features
    - Coaches can manage multiple athletes
    - Assign workouts to athletes
    - View athlete progress dashboard
  - Database: Add `User.is_public`, `Follow` table, `Activity.privacy`
  - Privacy controls: Public, Friends, Private

- **Files**:
  - **Create**: [backend/src/models/social.py](backend/src/models/social.py) - Follow, ActivityLike models
  - **Create**: [backend/src/api/routes/social.py](backend/src/api/routes/social.py)
  - **Create**: [frontend/src/pages/Profile.tsx](frontend/src/pages/Profile.tsx)
  - **Create**: [frontend/src/pages/Feed.tsx](frontend/src/pages/Feed.tsx)
  - **Modify**: Navigation to add "Feed" tab

---

### 32. **[P3] [Innovation] - Wearable Device Direct Sync**

- **Problem**: Currently requires Garmin Connect as intermediary. Users with Wahoo, Polar, Apple Watch can't sync. Limited to Garmin users only.

- **TP Comparison**: TP syncs with multiple devices (Garmin, Wahoo, Polar) but via their cloud APIs. Slow sync (5-10 minutes delay). No Apple Watch.

- **Impact**: ⭐⭐⭐⭐⭐ (Market expansion, user acquisition)

- **Effort**: L (2-3 weeks per device)

- **Competitive Advantage**: YES if we support Apple Watch (TP doesn't)

- **Solution**:
  - Device integration priority:
    1. **Apple Watch** (HealthKit API) - Largest market
    2. **Wahoo** (Wahoo Cloud API)
    3. **Polar** (Polar Flow API)
    4. **Coros** (Coros API)
    5. **Suunto** (Suunto App API)
  - Implementation per device:
    - OAuth2 authentication flow
    - Webhook for real-time sync (when available)
    - Fallback: Poll for new activities every 15 minutes
    - Parse device-specific FIT/TCX/JSON formats
    - Map to TrainingPlan's unified activity model
  - Backend: Create `DeviceIntegration` model
  - Settings page: "Connected Devices" section
  - Allow multiple devices per user (e.g., Garmin watch + Wahoo bike computer)

- **Files**:
  - **Create**: [backend/src/services/apple_health_service.py](backend/src/services/apple_health_service.py)
  - **Create**: [backend/src/services/wahoo_service.py](backend/src/services/wahoo_service.py)
  - **Create**: [backend/src/models/device_integration.py](backend/src/models/device_integration.py)
  - **Create**: [backend/src/api/routes/devices.py](backend/src/api/routes/devices.py)
  - **Modify**: [frontend/src/pages/SettingsNew.tsx](frontend/src/pages/SettingsNew.tsx) - Add device connections
  - **Research**: Each device API documentation

---

## Summary Statistics

### By Priority
- **P0 (Critical)**: 4 items (13%)
- **P1 (High)**: 11 items (35%)
- **P2 (Medium)**: 13 items (42%)
- **P3 (Future)**: 3 items (10%)

### By Category
- **Navigation**: 5 items (#1, #5, #10, #19, #26)
- **Visual Design**: 6 items (#6, #11, #18, #24, #28, #29)
- **Mobile Experience**: 5 items (#2, #8, #13, #20, #27)
- **Interactions & Feedback**: 6 items (#3, #9, #14, #21, #25, #29)
- **Data Visualization**: 3 items (#7, #12, #23)
- **Performance Perception**: 3 items (#4, #22, #27)
- **Health Data**: 1 item (#16)
- **Innovation/New Features**: 3 items (#30, #31, #32)

### By Effort
- **Small (< 1 day)**: 7 items (23%)
- **Medium (1-3 days)**: 15 items (50%)
- **Large (4+ days)**: 8 items (27%)

### Competitive Advantage
- **Yes (Better than TP)**: 20 items (67%)
- **No (Table stakes)**: 10 items (33%)

### Quick Wins (High Impact, Low Effort)
1. **#3** - Empty State Guidance (P0, S, ⭐⭐⭐⭐⭐)
2. **#5** - Breadcrumbs (P1, S, ⭐⭐⭐⭐)
3. **#6** - Card Shadows (P1, S, ⭐⭐⭐⭐)
4. **#10** - FAB Buttons (P1, S, ⭐⭐⭐⭐)
5. **#11** - Sport Colors (P1, S, ⭐⭐⭐⭐)
6. **#19** - Confirm Dialogs (P2, S, ⭐⭐⭐⭐)
7. **#22** - Animated Metrics (P2, S, ⭐⭐⭐)
8. **#25** - Pull-to-Refresh (P2, S, ⭐⭐⭐)

### Strategic Projects (High Impact, High Effort)
1. **#2** - Mobile Calendar (P0, L, ⭐⭐⭐⭐⭐)
2. **#15** - Dark Mode (P1, L, ⭐⭐⭐⭐)
3. **#23** - Drag-and-Drop (P2, L, ⭐⭐⭐⭐)
4. **#28** - AI Plan Generator (P3, L, ⭐⭐⭐⭐⭐)
5. **#29** - Social Features (P3, L, ⭐⭐⭐⭐⭐)
6. **#30** - Multi-Device Sync (P3, L, ⭐⭐⭐⭐⭐)

---

## Recommended Implementation Order

### Sprint 1 (Week 1): Critical Navigation & Mobile
1. #1 - AppBar Navigation (P0, M)
2. #3 - Empty States (P0, S)
3. #4 - Loading Skeletons (P0, M)

### Sprint 2 (Week 2): Mobile Calendar
1. #2 - Responsive Calendar (P0, L)

### Sprint 3 (Week 3-4): High-Impact Polish
1. #5 - Breadcrumbs (P1, S)
2. #6 - Card Shadows (P1, S)
3. #10 - FAB Buttons (P1, S)
4. #11 - Sport Colors (P1, S)
5. #9 - Toast System (P1, M)
6. #7 - Chart Zones (P1, M)

### Sprint 4 (Week 5-6): Mobile UX
1. #8 - Touch-Optimized Cards (P1, M)
2. #13 - Bottom Navigation (P1, M)
3. #14 - Optimistic UI (P1, M)
4. #12 - Weekly Load Chart (P1, M)

### Sprint 5 (Week 7-8): Dark Mode & Polish
1. #15 - Dark Mode (P1, L)
2. #16 - Typography (P2, S)
3. #22 - Animated Metrics (P2, S)
4. #19 - Confirm Dialogs (P2, S)

### Sprint 6+ (Week 9+): Advanced Features
- Items #17-27 (P2 polish items)
- Items #28-30 (P3 innovation features)

---

**End of Backlog**
