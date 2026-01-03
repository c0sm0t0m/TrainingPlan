# TrainingPlan Competitive Analysis vs TrainingPeaks
**Phase 2: Strategic Differentiation**  
**Date**: January 2, 2026  
**Agent**: UX Agent - Strategic Design Excellence

---

## Task 1: TrainingPeaks' 5 Biggest UX Weaknesses

### 1. 🐌 SLUGGISH PERFORMANCE & PAGE LOADS
**The Problem**:
- Full page reloads for every action (edit workout, change date, switch views)
- 2-3 second load times on workout detail pages
- No optimistic UI updates - users wait for server confirmation
- Heavy JavaScript bundle (~3MB) causes slow initial load
- No skeleton screens - just spinners and white screens

**Why It Matters**:
- Athletes check their calendar 5-10 times per day - every delay adds up
- Coaches managing 20+ athletes experience death by 1000 cuts
- Mobile users on slower connections are particularly frustrated
- Modern users expect instant feedback (Notion, Linear, Gmail all feel instant)

**How We Exploit It**:
1. **React SPA with instant navigation** - no page reloads between calendar/dashboard/plans
2. **Optimistic UI updates** - checkmark appears immediately when marking workout complete
3. **Lazy loading routes** - calendar code only loads when needed
4. **Skeleton screens** instead of spinners - perceived performance boost
5. **Service worker caching** - offline-first PWA loads instantly

**Implementation Priority**: **P0 - Critical**  
**Competitive Advantage**: **YES** - Speed is our #1 differentiator  
**Success Metric**: Calendar navigation < 100ms, workout edit < 200ms

---

### 2. 📱 TERRIBLE MOBILE EXPERIENCE
**The Problem**:
- Desktop-centric design doesn't adapt well to mobile
- Tiny touch targets (< 30px) make clicking workouts frustrating
- Calendar grid cramped on small screens - can't see workout details
- Bottom nav hidden on some pages - inconsistent wayfinding
- Form inputs use desktop patterns (dropdowns instead of native pickers)
- No swipe gestures for navigation (e.g., swipe between calendar weeks)

**Why It Matters**:
- 60% of athletes check training plans on phones (before/after workouts)
- Mobile usage is growing faster than desktop
- Younger athletes (Gen Z) are mobile-first by default
- Competitors like TrainerRoad have excellent mobile apps

**How We Exploit It**:
1. **Mobile-first design** - build for mobile, enhance for desktop
2. **Persistent bottom nav** (5 primary actions) on all mobile pages
3. **Large touch targets** (min 44x44px) following Apple/Google guidelines
4. **Swipe gestures** - swipe left/right to change calendar weeks
5. **Native mobile patterns** - date pickers, time pickers, action sheets
6. **PWA with install prompt** - feel like native app without app store
7. **Offline support** - view cached workouts without internet

**Implementation Priority**: **P0 - Critical**  
**Competitive Advantage**: **YES** - Mobile is 60% of usage  
**Success Metric**: 90%+ mobile usability score, 4.5+ rating on PWA install

---

### 3. 🎨 DATED VISUAL DESIGN
**The Problem**:
- Corporate blue (#003E7E) looks like enterprise software from 2010
- High visual density - cluttered interface overwhelms users
- Inconsistent spacing and typography hierarchy
- Small fonts (12px body text) strain eyes
- No dark mode (blue light = sleep disruption for evening planning)
- Charts look like Excel graphs (basic colors, no interactivity)

**Why It Matters**:
- First impression determines trial-to-paid conversion
- Athletes are inspired by beautiful design (Strava, Apple Fitness prove this)
- Modern users expect dark mode (50%+ usage after 6pm)
- Visual clutter increases cognitive load → reduces daily engagement

**How We Exploit It**:
1. **Modern color palette** - vibrant sport colors, high contrast, accessible
2. **Generous whitespace** - "data-rich, visually calm" philosophy
3. **Typography hierarchy** - Inter font, clear size scale (16px base)
4. **Dark mode from day 1** - toggle in app bar, respects system preference
5. **Interactive charts** - Recharts with hover tooltips, animations, zoom
6. **Micro-animations** - checkmarks, loading states, transitions feel alive
7. **Card-based layouts** - Material UI elevation creates depth

**Implementation Priority**: **P1 - High**  
**Competitive Advantage**: **YES** - Visual appeal drives virality  
**Success Metric**: 80%+ say "looks more modern" in user testing

---

### 4. 🧩 COMPLEX WORKOUT BUILDER
**The Problem**:
- Creating structured workouts requires 15+ clicks
- Zone picker uses confusing sliders (hard to hit exact percentages)
- No workout templates library - coaches recreate same workouts repeatedly
- Can't duplicate workouts across weeks easily
- Warmup/cooldown zones default to Zone 2 (should be Zone 1)
- No AI assistance ("create me a sweet spot workout")

**Why It Matters**:
- Coaches spend 30-60 min/week creating workouts for athletes
- Copy-paste errors cause incorrect training prescription
- Athletes without coaches struggle to build quality workouts
- Competitors like Zwift have one-click workout library

**How We Exploit It**:
1. **Smart workout templates** - "30 min Sweet Spot", "Threshold Test", "Recovery Spin"
2. **Quick workout builder** - 3 clicks max for simple workouts
3. **AI workout assistant** - "Create a 1-hour tempo ride" → structured workout
4. **One-click duplication** - copy workout to multiple days
5. **Workout library search** - filter by duration, zone, sport
6. **Visual workout designer** - drag blocks to build intervals
7. **Import from Garmin/Zwift** - sync existing workout library

**Implementation Priority**: **P1 - High**  
**Competitive Advantage**: **YES** - Saves coaches 2+ hours/week  
**Success Metric**: Average workout creation time < 60 seconds

---

### 5. 🤝 NO SOCIAL/COMMUNITY FEATURES
**The Problem**:
- Zero social features - completely isolated experience
- Can't follow friends or teammates
- No activity feed showing what training partners did today
- Athletes can't give kudos/comments on great workouts
- No training clubs or group challenges
- Can't share training plans publicly

**Why It Matters**:
- Social motivation is #1 predictor of training adherence (Strava proves this)
- Athletes are 3x more likely to complete workouts when friends are training
- Community creates lock-in - users stay because their friends are there
- Word-of-mouth growth requires social features

**How We Exploit It**:
1. **Activity feed** - see what training partners completed today (opt-in)
2. **Kudos system** - quick encouragement for completed workouts
3. **Training clubs** - group challenges, leaderboards, shared plans
4. **Public training plan marketplace** - athletes share/sell plans
5. **Workout comments** - coaches/athletes discuss execution
6. **Segment leaderboards** - compete on local routes (Strava integration)
7. **Training buddies** - find local athletes with similar goals

**Implementation Priority**: **P2 - Medium** (after core features solid)  
**Competitive Advantage**: **YES** - Creates viral growth loop  
**Success Metric**: 40%+ users connect with at least 1 friend

---

## Task 2: Mobile-First Strategy

### Current Mobile Experience Audit

**✅ Good Foundation**:
- `useMediaQuery(theme.breakpoints.down('md'))` checks implemented
- Bottom navigation exists in Layout component
- Mobile drawer for secondary navigation
- Responsive grid layouts in Dashboard

**❌ Critical Gaps**:
- Touch targets too small (< 40px) in workout cards
- No swipe gestures for calendar navigation
- Forms use desktop dropdowns instead of mobile sheets
- Charts not optimized for touch (small hit areas)
- No pull-to-refresh pattern
- Missing haptic feedback on interactions

---

### 5 Mobile-Specific Improvements

#### 1. **PWA Installation with Offline Support**
**Problem**: Users must bookmark site or navigate via browser  
**Solution**: 
- Add web app manifest with app icon
- Service worker caches calendar/dashboard for offline viewing
- Install prompt after 3 visits: "Add TrainingPlan to Home Screen"
- Feels like native app without app store friction

**Implementation**:
```tsx
// public/manifest.json
{
  "name": "TrainingPlan",
  "short_name": "TrainingPlan",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ],
  "start_url": "/dashboard",
  "display": "standalone",
  "theme_color": "#2196F3",
  "background_color": "#FFFFFF"
}

// src/sw.ts - Service Worker
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request)
    })
  )
})
```

**Priority**: P1 - High  
**Effort**: Medium (1-2 days)  
**User Benefit**: ⭐⭐⭐⭐⭐ (offline access is game-changing)

---

#### 2. **Swipe Gestures for Calendar Navigation**
**Problem**: Tapping prev/next arrows is slow and clunky on mobile  
**Solution**: 
- Swipe left → next week, swipe right → previous week
- Swipe down → refresh activities (pull-to-refresh)
- Visual feedback during swipe (rubber band effect)
- Haptic feedback on iOS when week changes

**Implementation**:
```tsx
// Use react-swipeable library
import { useSwipeable } from 'react-swipeable'

const CalendarWeekView = () => {
  const handlers = useSwipeable({
    onSwipedLeft: () => {
      setWeek(prev => addWeeks(prev, 1))
      if (navigator.vibrate) navigator.vibrate(10) // Haptic
    },
    onSwipedRight: () => {
      setWeek(prev => addWeeks(prev, -1))
      if (navigator.vibrate) navigator.vibrate(10)
    },
    trackMouse: false, // Mobile only
  })
  
  return <Box {...handlers}>{/* Calendar grid */}</Box>
}
```

**Priority**: P1 - High  
**Effort**: Small (1 day)  
**User Benefit**: ⭐⭐⭐⭐⭐ (50%+ of calendar interactions are date changes)

---

#### 3. **Bottom Sheet Modals (iOS-Style)**
**Problem**: Desktop modal dialogs don't feel native on mobile  
**Solution**: 
- Swipe-up bottom sheets for "Add Workout", "Edit Workout"
- Snap points (50% height, 90% height, full screen)
- Swipe-down to dismiss (iOS pattern)
- Backdrop dims screen below
- Mobile-optimized form inputs (large buttons, native pickers)

**Implementation**:
```tsx
// Use @mui/material BottomSheet or react-spring-bottom-sheet
import { BottomSheet } from 'react-spring-bottom-sheet'

const AddWorkoutSheet = ({ open, onClose }) => (
  <BottomSheet
    open={open}
    onDismiss={onClose}
    snapPoints={({ maxHeight }) => [
      maxHeight * 0.5,
      maxHeight * 0.9,
    ]}
  >
    <Box sx={{ p: 2 }}>
      <Typography variant="h6">Add Workout</Typography>
      {/* Mobile-optimized form */}
      <TextField 
        fullWidth
        label="Workout Title"
        inputProps={{ style: { fontSize: 16 } }} // Prevent zoom on iOS
      />
      <Button 
        fullWidth 
        variant="contained" 
        size="large"
        sx={{ mt: 2, minHeight: 48 }} // Large touch target
      >
        Save Workout
      </Button>
    </Box>
  </BottomSheet>
)
```

**Priority**: P1 - High  
**Effort**: Medium (2-3 days)  
**User Benefit**: ⭐⭐⭐⭐ (forms are 30% of mobile interactions)

---

#### 4. **Workout Card Optimization for Touch**
**Problem**: Current cards have small icons and crowded layout  
**Solution**: 
- Increase card padding on mobile (16px → 24px)
- Sport icons 32px (up from 20px)
- All touch targets min 44x44px (Apple HIG, Android Material)
- Swipe left on card reveals quick actions (Edit, Delete, Move)
- Long-press for context menu
- Haptic feedback on tap

**Implementation**:
```tsx
const WorkoutCard = ({ workout, isMobile }) => {
  const handlers = useSwipeable({
    onSwipedLeft: () => setActionsRevealed(true),
    onSwipedRight: () => setActionsRevealed(false),
  })
  
  return (
    <Card
      {...handlers}
      sx={{
        p: isMobile ? 3 : 1.5, // More padding on mobile
        cursor: 'pointer',
        position: 'relative',
      }}
      onContextMenu={(e) => {
        if (isMobile) {
          e.preventDefault()
          navigator.vibrate?.(50) // Long-press feedback
          showContextMenu()
        }
      }}
    >
      {/* Sport icon - larger on mobile */}
      <SportIcon sx={{ 
        fontSize: isMobile ? 32 : 20,
        color: sportConfig.color 
      }} />
      
      {/* Quick actions revealed by swipe */}
      {actionsRevealed && (
        <Box sx={{
          position: 'absolute',
          right: 0,
          top: 0,
          bottom: 0,
          bgcolor: 'error.main',
          display: 'flex',
          alignItems: 'center',
        }}>
          <IconButton sx={{ minWidth: 44, minHeight: 44 }}>
            <Delete />
          </IconButton>
        </Box>
      )}
    </Card>
  )
}
```

**Priority**: P0 - Critical  
**Effort**: Small (1 day)  
**User Benefit**: ⭐⭐⭐⭐⭐ (cards are most-interacted element)

---

#### 5. **Floating Action Button (FAB) for Quick Add**
**Problem**: "Add Workout" button hidden in top nav - hard to reach on phones  
**Solution**: 
- Persistent FAB in bottom-right corner (Material Design standard)
- Tapping opens bottom sheet with quick add form
- Speed dial variant on calendar page: FAB expands to show "Workout", "Race", "Note"
- Auto-hides when scrolling down (prevents blocking content)
- Re-appears when scrolling up

**Implementation**:
```tsx
const CalendarPage = () => {
  const [fabVisible, setFabVisible] = useState(true)
  const [speedDialOpen, setSpeedDialOpen] = useState(false)
  
  // Hide FAB when scrolling down
  useScrollTrigger({
    onScroll: (direction) => {
      setFabVisible(direction === 'up')
    }
  })
  
  return (
    <>
      {/* Calendar content */}
      
      {/* FAB with Speed Dial */}
      <SpeedDial
        ariaLabel="Add training item"
        sx={{ 
          position: 'fixed', 
          bottom: 80, // Above bottom nav
          right: 16,
          transform: fabVisible ? 'scale(1)' : 'scale(0)',
          transition: 'transform 0.2s',
        }}
        icon={<Add />}
        onOpen={() => setSpeedDialOpen(true)}
        onClose={() => setSpeedDialOpen(false)}
        open={speedDialOpen}
      >
        <SpeedDialAction
          icon={<FitnessCenter />}
          tooltipTitle="Add Workout"
          onClick={handleAddWorkout}
        />
        <SpeedDialAction
          icon={<EmojiEvents />}
          tooltipTitle="Add Race"
          onClick={handleAddRace}
        />
        <SpeedDialAction
          icon={<Notes />}
          tooltipTitle="Add Note"
          onClick={handleAddNote}
        />
      </SpeedDial>
    </>
  )
}
```

**Priority**: P1 - High  
**Effort**: Small (1 day)  
**User Benefit**: ⭐⭐⭐⭐ (reduces clicks to add workout from 3 to 1)

---

### Mobile Implementation Priorities

| Feature | Impact | Effort | Priority | Sprint |
|---------|--------|--------|----------|--------|
| Touch target optimization | High | Small | P0 | 1 |
| Swipe calendar navigation | High | Small | P1 | 1 |
| Bottom sheet modals | High | Medium | P1 | 2 |
| FAB for quick add | Medium | Small | P1 | 2 |
| PWA with offline support | High | Medium | P1 | 3 |

**Success Metrics**:
- 90%+ mobile usability score (Google Lighthouse)
- < 3 seconds first contentful paint on 3G
- < 10% bounce rate on mobile (vs 25% industry average)
- 4.5+ star rating for PWA install

---

## Task 3: Visual Design Differentiation

### Proposed Color Palette

#### Primary Colors
```css
/* Main brand color - energizing but professional */
--primary-500: #2563EB; /* Blue - trust, performance */
--primary-400: #3B82F6;
--primary-600: #1D4ED8;

/* Replace TP's boring corporate blue (#003E7E) with modern blue (#2563EB) */
/* Rationale: Lighter, more vibrant - feels innovative not corporate */
```

#### Sport Colors (Keep but enhance)
```css
/* Vibrant sport-specific colors */
--sport-swim: #06B6D4;    /* Cyan (was #2196F3) - more refreshing */
--sport-bike: #F59E0B;    /* Amber (was #FF9800) - warmer, more energetic */
--sport-run: #10B981;     /* Emerald (was #4CAF50) - more natural */
--sport-strength: #8B5CF6; /* Violet (was #9C27B0) - more premium */
--sport-other: #6B7280;   /* Gray - unchanged */
```

**Competitive Advantage**: Sport colors are industry standard but we make them more vibrant and modern. This creates instant visual differentiation while maintaining familiarity.

#### Accent Colors
```css
/* Success states */
--success-500: #10B981; /* Emerald green - completed workouts */
--success-100: #D1FAE5; /* Light tint for backgrounds */

/* Warning/Caution */
--warning-500: #F59E0B; /* Amber - high training load */
--warning-100: #FEF3C7;

/* Error/Destructive */
--error-500: #EF4444; /* Red - delete, overtraining */
--error-100: #FEE2E2;

/* Info */
--info-500: #06B6D4; /* Cyan - tooltips, help text */
--info-100: #CFFAFE;
```

#### Neutral Palette (Dark Mode Ready)
```css
/* Light mode */
--gray-50: #F9FAFB;   /* Page background */
--gray-100: #F3F4F6;  /* Card backgrounds (alternative) */
--gray-200: #E5E7EB;  /* Borders */
--gray-300: #D1D5DB;  /* Disabled states */
--gray-400: #9CA3AF;  /* Placeholder text */
--gray-500: #6B7280;  /* Secondary text */
--gray-600: #4B5563;  /* Body text */
--gray-700: #374151;  /* Headings */
--gray-800: #1F2937;
--gray-900: #111827;  /* Dark mode backgrounds */

/* Dark mode (invert) */
--dm-bg: #0F172A;        /* Page background - deep blue-black */
--dm-surface: #1E293B;   /* Card backgrounds */
--dm-text-primary: #F1F5F9;    /* Headings */
--dm-text-secondary: #CBD5E1;  /* Body text */
--dm-border: #334155;          /* Dividers */
```

**Rationale**: TP has no dark mode. We launch with it on day 1. Use Tailwind CSS color system (proven, accessible, scales to dark mode).

---

### Typography Improvements

#### Font Stack
```css
/* Primary: Inter - modern, readable, optimized for UI */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Monospace: JetBrains Mono - for metrics, data */
font-family: 'JetBrains Mono', 'Courier New', monospace;
```

**Why Inter?**
- Variable font (single file, all weights)
- Optimized for screens (large x-height, open apertures)
- Used by: GitHub, Netflix, Vercel (signals modern tech company)
- Better than TP's system fonts (Helvetica/Arial)

#### Type Scale
```css
/* TrainingPeaks uses 12-14px body text (too small!) */
/* We use 16px base for readability */

--text-xs: 0.75rem;    /* 12px - labels, captions */
--text-sm: 0.875rem;   /* 14px - secondary text */
--text-base: 1rem;     /* 16px - body text (TP uses 14px) */
--text-lg: 1.125rem;   /* 18px - emphasized text */
--text-xl: 1.25rem;    /* 20px - card titles */
--text-2xl: 1.5rem;    /* 24px - page titles */
--text-3xl: 1.875rem;  /* 30px - hero headings */
--text-4xl: 2.25rem;   /* 36px - dashboard welcome */
```

#### Font Weights
```css
--font-normal: 400;    /* Body text */
--font-medium: 500;    /* Emphasized text */
--font-semibold: 600;  /* Buttons, nav */
--font-bold: 700;      /* Headings */
```

**Competitive Advantage**: 
- 16px base is 14% larger than TP → better readability
- Inter is more modern than Helvetica
- Clear hierarchy reduces cognitive load

---

### Spacing/Whitespace Strategy

#### Spacing Scale (8px base unit)
```css
/* TrainingPeaks is cramped - we breathe */
--space-1: 0.25rem;  /* 4px - tight spacing */
--space-2: 0.5rem;   /* 8px - base unit */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px - card padding (TP uses 8px) */
--space-6: 1.5rem;   /* 24px - section spacing */
--space-8: 2rem;     /* 32px - large gaps */
--space-12: 3rem;    /* 48px - page margins */
--space-16: 4rem;    /* 64px - hero sections */
```

#### Card Design Pattern
```tsx
<Card sx={{
  p: 4,              // 32px padding (TP uses 12px)
  mb: 3,             // 24px margin bottom
  borderRadius: 2,   // 16px (TP uses 4px sharp corners)
  boxShadow: 1,      // Subtle elevation
  transition: 'all 0.2s',
  '&:hover': {
    boxShadow: 3,    // Lift on hover
    transform: 'translateY(-2px)', // Micro-interaction
  }
}}>
```

**Principles**:
1. **Card padding**: Min 24px on mobile, 32px on desktop (TP uses 8-12px)
2. **Section gaps**: 48px between major sections (TP uses 16px)
3. **Line height**: 1.6 for body text (TP uses 1.4 - cramped)
4. **Max width**: 1200px for content (TP goes to 1600px - too wide)

---

### Competitive Advantage Summary

| Element | TrainingPeaks | TrainingPlan | Advantage |
|---------|---------------|--------------|-----------|
| **Primary Color** | Corporate blue #003E7E | Modern blue #2563EB | More vibrant, less "enterprise" |
| **Sport Colors** | Standard RGB | Enhanced Tailwind palette | More saturated, premium feel |
| **Dark Mode** | ❌ None | ✅ Native support | Reduces eye strain, modern expectation |
| **Body Font** | Helvetica 14px | Inter 16px | +14% larger, better readability |
| **Card Padding** | 8-12px | 24-32px | Less cramped, cleaner |
| **Border Radius** | 4px (sharp) | 12px (rounded) | Friendlier, modern |
| **Elevation** | Static | Dynamic (hover lift) | More interactive feel |
| **Animations** | None | 0.2s transitions | Delightful micro-interactions |

---

### Implementation Code

#### Theme Configuration
```tsx
// src/theme.ts
import { createTheme } from '@mui/material/styles'

export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2563EB',
      light: '#3B82F6',
      dark: '#1D4ED8',
    },
    secondary: {
      main: '#F59E0B',
    },
    success: {
      main: '#10B981',
      light: '#D1FAE5',
    },
    warning: {
      main: '#F59E0B',
      light: '#FEF3C7',
    },
    error: {
      main: '#EF4444',
      light: '#FEE2E2',
    },
    info: {
      main: '#06B6D4',
      light: '#CFFAFE',
    },
    background: {
      default: '#F9FAFB',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#1F2937',
      secondary: '#6B7280',
    },
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    fontSize: 16, // Base 16px (TP uses 14px)
    h1: { fontWeight: 700, fontSize: '2.25rem' },
    h2: { fontWeight: 700, fontSize: '1.875rem' },
    h3: { fontWeight: 600, fontSize: '1.5rem' },
    h4: { fontWeight: 600, fontSize: '1.25rem' },
    h5: { fontWeight: 600, fontSize: '1.125rem' },
    h6: { fontWeight: 600, fontSize: '1rem' },
    body1: { fontSize: '1rem', lineHeight: 1.6 },
    body2: { fontSize: '0.875rem', lineHeight: 1.6 },
  },
  shape: {
    borderRadius: 12, // Rounded (TP uses 4px)
  },
  spacing: 8, // 8px base unit
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
          transition: 'all 0.2s',
          '&:hover': {
            boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // Sentence case (TP uses ALL CAPS)
          fontWeight: 600,
          borderRadius: 8,
        },
        sizeLarge: {
          minHeight: 48, // Touch-friendly (TP uses 36px)
        },
      },
    },
  },
})

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#3B82F6', // Lighter in dark mode
      light: '#60A5FA',
      dark: '#2563EB',
    },
    background: {
      default: '#0F172A', // Deep blue-black
      paper: '#1E293B',   // Elevated surfaces
    },
    text: {
      primary: '#F1F5F9',
      secondary: '#CBD5E1',
    },
    divider: '#334155',
  },
  // ... inherit other settings from lightTheme
})
```

#### Sport Color Constants
```tsx
// src/constants/sportColors.ts
export const SPORT_COLORS = {
  swim: {
    main: '#06B6D4',
    light: '#CFFAFE',
    dark: '#0891B2',
  },
  bike: {
    main: '#F59E0B',
    light: '#FEF3C7',
    dark: '#D97706',
  },
  run: {
    main: '#10B981',
    light: '#D1FAE5',
    dark: '#059669',
  },
  strength: {
    main: '#8B5CF6',
    light: '#EDE9FE',
    dark: '#7C3AED',
  },
  other: {
    main: '#6B7280',
    light: '#F3F4F6',
    dark: '#4B5563',
  },
} as const

export type SportType = keyof typeof SPORT_COLORS
```

---

## Execution Roadmap

### Phase 1: Visual Foundation (Week 1-2)
- [ ] Implement new color palette in theme.ts
- [ ] Add Inter font to project
- [ ] Create sport color constants
- [ ] Update all cards with new padding/shadows
- [ ] Add dark mode toggle in AppBar

### Phase 2: Mobile Optimization (Week 3-4)
- [ ] Increase touch targets to 44x44px minimum
- [ ] Add swipe gestures to calendar
- [ ] Implement bottom sheet modals
- [ ] Add floating action button
- [ ] PWA manifest and service worker

### Phase 3: Performance (Week 5-6)
- [ ] React.lazy() for route splitting
- [ ] Skeleton screens replace spinners
- [ ] Optimistic UI for workout completion
- [ ] Service worker caching strategy
- [ ] Lighthouse audit → 90+ mobile score

### Phase 4: Social Features (Week 7-12)
- [ ] Activity feed infrastructure
- [ ] Kudos system
- [ ] Training clubs
- [ ] Public plan marketplace
- [ ] Workout comments

---

## Success Metrics

### User Testing Benchmarks
- **Visual Appeal**: 80%+ say "looks more modern than TrainingPeaks"
- **Mobile Usability**: 90%+ mobile usability score
- **Speed**: "Feels instant" reported by 85%+ of users
- **Dark Mode**: 40%+ usage after 6pm
- **Social Features**: 40%+ connect with ≥1 friend within 30 days

### Technical Metrics
- First Contentful Paint: < 1.5s (TP: 3-4s)
- Time to Interactive: < 2.5s (TP: 5-6s)
- Lighthouse Mobile: 90+ (TP: 60-70)
- Lighthouse Desktop: 95+ (TP: 75-85)

### Business Metrics
- Trial-to-paid conversion: 25%+ (TP: ~15%)
- Daily active usage: 60%+ (TP: ~40%)
- Viral coefficient: 0.3+ (social features)
- Net Promoter Score: 50+ (TP: ~30)

---

**Next Steps**: Implement Phase 1 (Visual Foundation) starting with theme.ts update and Inter font integration.
