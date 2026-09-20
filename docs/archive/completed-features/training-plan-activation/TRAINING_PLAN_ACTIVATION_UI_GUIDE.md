# Training Plan Activation UI - Visual Guide

## Plans Tab - Plan Card Layout

### Active Plan Card
```
┌──────────────────────────────────────────────────────────────┐
│                                        ┌──────────────┐       │
│  Marathon Training Plan                │ ✓ ACTIVE    │       │
│                                        └──────────────┘       │
│  ┌──────────┐                                                │
│  │ Running  │                                                │
│  └──────────┘                                                │
│                                                              │
│  12-week progressive plan building to marathon distance     │
│                                                              │
│  2025-01-01 - 2025-03-31                                    │
│                                                              │
│  24 workouts          4 completed                           │
│  ───────────────────────────────────────────────────────    │
│  ◉ Show in Calendar                                         │
│                                                              │
│  [View Details]  [🗑]                                        │
└──────────────────────────────────────────────────────────────┘
```

**Visual Features:**
- 🟦 **Primary colored border (2px)** - Indicates active status
- 🟢 **Green "ACTIVE" badge** with checkmark - Top-right corner
- 🔘 **Toggle switch ON** - "Show in Calendar" label is bold
- 📏 **Divider line** - Separates activation control from workout stats

### Inactive Plan Card
```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  Half Marathon Training                                     │
│  ┌──────────┐                                               │
│  │ Running  │                                               │
│  └──────────┘                                               │
│                                                              │
│  8-week plan for sub-2 hour half marathon                   │
│                                                              │
│  2025-02-01 - 2025-03-31                                    │
│                                                              │
│  16 workouts          0 completed                           │
│  ───────────────────────────────────────────────────────    │
│  ○ Show in Calendar                                         │
│                                                              │
│  [View Details]  [🗑]                                        │
└──────────────────────────────────────────────────────────────┘
```

**Visual Features:**
- ⬜ **Standard border (1px)** - Normal card appearance
- 🚫 **No badge** - Clearly not active
- ⭕ **Toggle switch OFF** - "Show in Calendar" label is regular weight
- 📏 **Divider line** - Consistent with active card

## Info Alert (shown above cards when plans exist)

```
┌──────────────────────────────────────────────────────────────┐
│ ℹ️  Calendar Control: Only workouts from active training    │
│    plans appear in your calendar. Toggle "Show in Calendar" │
│    to control which plan's workouts are displayed. Only one │
│    plan can be active at a time.                            │
└──────────────────────────────────────────────────────────────┘
```

## User Interaction Flow

### Scenario 1: Activating a Plan

**Initial State:**
```
[Plan A] ────────── ACTIVE (border, badge, toggle ON)
[Plan B] ────────── Inactive (no border, no badge, toggle OFF)
```

**User clicks toggle on Plan B:**
```
[Plan A] ────────── Processing... (loading indicator)
[Plan B] ────────── Processing... (loading indicator)
```

**After activation:**
```
[Plan A] ────────── Inactive (border removed, badge gone, toggle OFF)
[Plan B] ────────── ACTIVE (border added, badge shown, toggle ON)
```

### Scenario 2: Deactivating the Active Plan

**Initial State:**
```
[Plan A] ────────── ACTIVE (border, badge, toggle ON)
[Plan B] ────────── Inactive
```

**User clicks toggle on Plan A:**
```
[Plan A] ────────── Processing...
```

**After deactivation:**
```
[Plan A] ────────── Inactive (all active styling removed)
[Plan B] ────────── Inactive
```

**Calendar now shows:**
```
No active training plan - Calendar is empty of planned workouts
(Only completed activities from Garmin will show)
```

## Tooltip Interactions

### Hover over Toggle (Active Plan):
```
┌──────────────────────────────────┐
│ This plan's workouts are shown  │
│ in calendar                      │
└──────────────────────────────────┘
    ↓
   ◉ Show in Calendar
```

### Hover over Toggle (Inactive Plan):
```
┌──────────────────────────────────┐
│ Activate to show workouts in    │
│ calendar                         │
└──────────────────────────────────┘
    ↓
   ○ Show in Calendar
```

## Color Scheme

### Light Mode:
- **Active Border**: Primary Blue (#1976d2)
- **Active Badge**: Success Green (#2e7d32) with white text
- **Active Toggle**: Primary Blue
- **Inactive Border**: Light Grey (#e0e0e0)
- **Info Alert**: Light Blue background (#e3f2fd)

### Dark Mode:
- **Active Border**: Primary Blue (#90caf9)
- **Active Badge**: Success Green (#66bb6a) with dark text
- **Active Toggle**: Primary Blue
- **Inactive Border**: Dark Grey (#424242)
- **Info Alert**: Dark Blue background (#0d47a1)

## Responsive Behavior

### Desktop (≥960px):
- Two columns of plan cards
- Full toggle labels visible
- Info alert spans full width

### Tablet (600px - 959px):
- Two columns (narrower cards)
- Toggle labels remain visible
- Badge may overlap slightly with title

### Mobile (<600px):
- Single column layout
- Full card width
- Toggle switches to smaller size
- Badge positioned to avoid title overlap

## Animation & Transitions

1. **Toggle Switch**: Smooth slide animation (0.2s)
2. **Border Change**: Fade in/out (0.3s)
3. **Badge Appearance**: Fade in + scale (0.3s)
4. **Card Refresh**: Brief opacity change to indicate update

## Accessibility Features

1. **Keyboard Navigation**: Toggle can be activated with Enter/Space
2. **Screen Reader**: "Show in Calendar switch, currently on/off"
3. **Focus Indicators**: Clear focus ring on toggle
4. **ARIA Labels**: Descriptive labels for all interactive elements
5. **Color Contrast**: All text meets WCAG AA standards

## Edge Cases Handled

1. **No Plans**: Info alert not shown (would be redundant)
2. **All Plans Inactive**: Calendar shows only completed activities
3. **Multiple Active Plans**: Backend enforces mutual exclusion
4. **Network Error**: Error message shown, UI reverts to previous state
5. **Rapid Toggling**: Debounce prevents duplicate API calls

## Summary

This UI design provides:
✅ Clear visual distinction between active and inactive plans
✅ Easy-to-use toggle control for activation
✅ Helpful contextual information via tooltips and info alert
✅ Consistent with Material-UI design patterns
✅ Works seamlessly across all device sizes
✅ Accessible to all users
