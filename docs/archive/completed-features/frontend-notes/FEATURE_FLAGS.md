# Feature Flags System

## Overview

The feature flag system allows safe A/B testing and gradual rollout of UI improvements. Toggle features at runtime without code changes.

## Quick Start

### 1. Enable via Settings UI (Easiest)
1. Navigate to **Settings → Beta Features**
2. Toggle switches for features you want to test
3. Changes save automatically to localStorage

### 2. Enable via URL Parameter (Fast Testing)
```
http://localhost:5173?newNavigation=true
http://localhost:5173?newMobileCalendar=true&newEmptyStates=true
```

### 3. Enable via Browser Console
```javascript
// Enable a single feature
localStorage.setItem('feature_newNavigation', 'true')

// Disable a feature
localStorage.setItem('feature_newNavigation', 'false')

// Clear all feature flags
Object.keys(localStorage).forEach(key => {
  if (key.startsWith('feature_')) localStorage.removeItem(key)
})

// Reload page to see changes
location.reload()
```

### 4. Enable via Environment Variable (Development)
```bash
# .env.local
VITE_FEATURE_NEW_NAVIGATION=true
VITE_FEATURE_NEW_MOBILE_CALENDAR=true
```

## Priority Order

Feature flags are resolved in this order (highest priority first):

1. **URL Parameters** - `?newNavigation=true`
2. **localStorage** - User settings from UI
3. **Environment Variables** - `.env.local` defaults
4. **Code Defaults** - Hardcoded in `FeatureFlagsContext.tsx`

## Available Features

### P0: Critical Improvements ⭐⭐⭐⭐⭐

#### `newNavigation`
- **What**: Persistent AppBar with navigation tabs
- **Impact**: Reduces navigation clicks by 60%, eliminates "orphaned" pages
- **Status**: ✅ Implemented (not yet feature-flagged - always visible)
- **Files**: `Layout.tsx` (lines 139-159)
- **Enable**: Settings → Beta Features → "Persistent Navigation"

#### `newMobileCalendar`
- **What**: Responsive calendar with agenda view for mobile
- **Impact**: Makes calendar usable on mobile (40-50% of users)
- **Status**: ⏳ In development
- **Enable**: Settings → Beta Features → "Mobile Calendar"

#### `newEmptyStates`
- **What**: Helpful guidance when no data exists
- **Impact**: Improves onboarding, reduces confusion
- **Status**: ✅ Implemented
- **Files**: 
  - `components/EmptyState.tsx` (reusable component)
  - `Dashboard.tsx` - "No activities yet" with Connect Garmin CTA
  - `TrainingPlans.tsx` - "No training plans yet" with Create Plan CTA
  - `Calendar.tsx` - "No workouts scheduled" with Create Plan CTA
- **Enable**: Settings → Beta Features → "Empty State Guidance"

#### `newLoadingSkeletons`
- **What**: Skeleton screens instead of "Loading..." text
- **Impact**: Feels 2x faster, better perceived performance
- **Status**: ✅ Implemented
- **Files**:
  - `components/skeletons/DashboardSkeleton.tsx`
  - `components/skeletons/TrainingPlansSkeleton.tsx`
  - `components/skeletons/CalendarSkeleton.tsx`
  - Integrated in Dashboard, TrainingPlans, Calendar pages
- **Enable**: Settings → Beta Features → "Loading Skeletons"

### P1: High-Impact Features ⭐⭐⭐⭐

#### `newBreadcrumbs`
- **What**: Breadcrumb navigation for nested pages
- **Impact**: Shows location hierarchy, easier navigation
- **Status**: ✅ Implemented
- **Files**:
  - `components/Breadcrumbs.tsx` - Reusable breadcrumb component with auto-generation from URL
  - `pages/PlanDetail.tsx` - Home > Training Plans > [Plan Name]
  - `pages/SettingsNew.tsx` - Home > Settings
- **Enable**: Settings → Beta Features → "Breadcrumbs"

#### `newQuickActions`
- **What**: Floating Action Button for common tasks
- **Impact**: Faster access to frequent actions
- **Status**: ✅ Implemented
- **Files**:
  - `components/QuickActionsFAB.tsx` - Context-aware FAB with SpeedDial
  - `App.tsx` - Global FAB integrated
- **Context-Aware Actions**:
  - Dashboard: New Plan, View Calendar, Log Activity
  - Training Plans: Create Plan
  - Plan Detail: Add Run/Bike/Swim workouts
  - Calendar: View Plans, Go to Today
  - Activities: View Calendar
  - Settings: Back to Dashboard
- **Enable**: Settings → Beta Features → "Quick Actions FAB"

#### `newChartInteractions`
- **What**: Zoom, pan, and interact with charts
- **Impact**: Better data exploration
- **Status**: ⏳ Planned

#### `newPlanTemplates`
- **What**: Pre-built training plans (Marathon, Tri, etc.)
- **Impact**: Faster onboarding for new users
- **Status**: Planned

### P2: Polish & Enhancement ✨

#### `newDarkMode`
- **What**: Dark theme option
- **Impact**: Better for night use
- **Status**: Planned

#### `newAnimations`
- **What**: Smooth transitions and micro-interactions
- **Impact**: More polished feel
- **Status**: Planned

## Usage in Components

### Simple Check

```typescript
import { useFeature } from '../contexts/FeatureFlagsContext';

function MyComponent() {
  const newNavigationEnabled = useFeature('newNavigation');
  
  return newNavigationEnabled ? (
    <NewAppBar />
  ) : (
    <OldAppBar />
  );
}
```

### Full Context

```typescript
import { useFeatureFlags } from '../contexts/FeatureFlagsContext';

function MyComponent() {
  const { features, toggleFeature } = useFeatureFlags();
  
  return (
    <div>
      {features.newNavigation && <NewNav />}
      {features.newEmptyStates && <EmptyState />}
      
      <button onClick={() => toggleFeature('newNavigation')}>
        Toggle Nav
      </button>
    </div>
  );
}
```

### Conditional Rendering

```typescript
import { useFeature } from '../contexts/FeatureFlagsContext';

function Dashboard() {
  const showSkeletons = useFeature('newLoadingSkeletons');
  const showEmptyStates = useFeature('newEmptyStates');
  
  if (loading) {
    return showSkeletons ? (
      <DashboardSkeleton />
    ) : (
      <CircularProgress />
    );
  }
  
  if (activities.length === 0) {
    return showEmptyStates ? (
      <EmptyStateGuidance />
    ) : (
      <Typography>No activities found</Typography>
    );
  }
  
  return <ActivityList activities={activities} />;
}
```

## Testing Workflow

### A/B Comparison

1. Navigate to page (e.g., Dashboard)
2. Note current UI/behavior
3. Enable feature flag: `?newEmptyStates=true`
4. Compare new UI
5. Toggle off to compare: `?newEmptyStates=false`

### Side-by-Side Testing

Open two browser windows:
- Window 1: `http://localhost:5173` (defaults off)
- Window 2: `http://localhost:5173?newNavigation=true` (feature on)

### Quick Toggle Script

```javascript
// Paste in browser console for instant toggle
function toggleFeature(name) {
  const current = localStorage.getItem(`feature_${name}`) === 'true';
  localStorage.setItem(`feature_${name}`, String(!current));
  console.log(`${name}: ${current ? 'OFF' : 'ON'}`);
  location.reload();
}

// Usage:
toggleFeature('newNavigation')
toggleFeature('newEmptyStates')
```

## Debugging

### Check Active Flags

Open DevTools console - active flags are logged on page load:
```
🚩 Active Feature Flags: ['newNavigation', 'newEmptyStates']
```

### View All Flag States

```javascript
// Browser console
const flags = Object.keys(localStorage)
  .filter(k => k.startsWith('feature_'))
  .map(k => `${k.replace('feature_', '')}: ${localStorage.getItem(k)}`);
console.log(flags);
```

### Reset Everything

```javascript
// Browser console - clear all flags
Object.keys(localStorage).forEach(key => {
  if (key.startsWith('feature_')) localStorage.removeItem(key);
});
location.reload();
```

Or use the **Reset to Defaults** button in Settings → Beta Features.

## Best Practices

### For Development

1. **Test both states**: Always test with flag ON and OFF
2. **Fallback gracefully**: Old UI should still work
3. **Console check**: Verify flags are active via console logs
4. **URL testing**: Use URL params for quick iteration

### For Production

1. **Gradual rollout**: Enable for 10% → 50% → 100%
2. **Monitor errors**: Check for issues with new features
3. **Easy rollback**: Toggle off immediately if problems found
4. **User feedback**: Let users opt-in via Settings

### For Code

1. **Clean conditionals**: Keep flag checks at top level
2. **No nested flags**: Avoid complex flag combinations
3. **Remove old code**: Once rolled out, delete old implementation
4. **Document**: Add comments explaining what flag controls

## Rollout Strategy

### Phase 1: Developer Testing (Now)
- All flags OFF by default
- Enable manually for testing
- Test both states thoroughly

### Phase 2: Beta Users (Week 1-2)
- Enable via Settings UI
- Collect feedback
- Fix issues

### Phase 3: Gradual Rollout (Week 3-4)
- Set environment default to ON
- Monitor for issues
- 100% rollout if stable

### Phase 4: Cleanup (Week 5+)
- Remove feature flag checks
- Delete old code paths
- Simplify components

## Troubleshooting

### Feature not activating?

1. Check console for active flags
2. Hard refresh (Cmd+Shift+R / Ctrl+Shift+F5)
3. Clear localStorage and try again
4. Check URL parameters are spelled correctly

### Wrong feature showing?

Priority order: URL > localStorage > env > defaults
- Clear localStorage to test env defaults
- Remove URL params to test localStorage

### Can't find Settings page?

Navigate directly: `http://localhost:5173/settings`

## Examples

### Test New Navigation

```bash
# Enable via URL
open http://localhost:5173?newNavigation=true

# Or enable in Settings
# Settings → Beta Features → Toggle "Persistent Navigation"

# Compare old vs new
# Window 1: ?newNavigation=false
# Window 2: ?newNavigation=true
```

### Test Multiple Features

```bash
# Enable several at once
open "http://localhost:5173?newNavigation=true&newEmptyStates=true&newLoadingSkeletons=true"
```

### Enable All for Testing

```javascript
// Browser console
['newNavigation', 'newMobileCalendar', 'newEmptyStates', 'newLoadingSkeletons'].forEach(f => {
  localStorage.setItem(`feature_${f}`, 'true');
});
location.reload();
```

---

**Questions?** Check the FeatureFlagsContext.tsx source code or ask in the project chat.
