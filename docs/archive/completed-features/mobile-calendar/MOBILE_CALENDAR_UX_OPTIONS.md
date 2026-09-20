# Mobile Calendar UX - Implementation Options

**Date**: 2026-01-06  
**Status**: Research Complete - Ready for Implementation

---

## Current Issues

1. **Week view too tight** - Can't see much information in mobile portrait mode
2. **Week selector not centered** - Selected week should be centered for better context
3. **No day view option** - No dedicated single-day detail view
4. **Week navigation vs summary** - Should week navigation be at top, summary at bottom?
5. **No horizontal scrolling** - Current implementation might benefit from horizontal navigation

---

## Industry Research Findings

### Key Patterns from Leading Apps

**TrainingPeaks Mobile**: Week view primary, centered week selector, horizontal swipe, color-coded workouts
**Strava**: Week overview, tap day for detail, no explicit day view
**Garmin Connect**: Month picker modal, week view primary
**Apple Calendar**: Horizontal day swipe, vertical week scroll
**Fantastical**: Centered day ticker, natural gestures

### Critical Insights

✅ **Week view is optimal for training apps** (best balance of detail and overview)  
✅ **Horizontal swipe for temporal navigation** (matches mental model)  
✅ **Centered selected week** provides temporal context  
✅ **Tap day cell → Day detail** (progressive disclosure)  
✅ **Single primary metric in week view** (TSS or duration, not both)  

❌ **Don't use vertical scrolling for week navigation** (confusing)  
❌ **Don't show all details in week grid** (too cramped)  
❌ **Don't left-align selected week** (disorienting)  

---

## Implementation Options

### **Option A: Horizontal Week Scroll (RECOMMENDED)**

#### Layout Structure
```
┌──────────────────────────────────────────┐
│  ← [Dec 30][Jan 6][Jan 13][Jan 20] →    │ Week Picker (centered)
├──────────────────────────────────────────┤
│  Mon  Tue  Wed  Thu  Fri  Sat  Sun      │ Day Headers
│   6    7    8    9   10   11   12       │ Dates
│  🟦   🟧   🟦   ⚪   🟩   🟪   ⚪       │ Workout Indicators
│  85   45   92    -  120   60    -       │ TSS Values
├──────────────────────────────────────────┤
│  📊 Week Summary: 402 TSS | 12.5 hrs    │ Summary Bar
└──────────────────────────────────────────┘
```

#### Features
- **Horizontal swipe** changes weeks (natural gesture)
- **Snap scrolling** - weeks snap into place
- **Momentum scrolling** - fling to jump multiple weeks
- **Centered week selector** shows 1-2 adjacent weeks
- **Fixed week header** - stays at top during day content scroll
- **Week summary at bottom** (less visual priority)

#### Pros
✅ Natural time navigation (left = past, right = future)  
✅ Preserves vertical space for day content  
✅ Matches TrainingPeaks/Strava patterns  
✅ Clear temporal context with centered week  
✅ Fast navigation via fling gesture  

#### Cons
⚠️ Slightly more complex implementation  
⚠️ Need to handle snap points and momentum  
⚠️ Requires gesture coordination with vertical scroll  

#### Implementation Complexity
**Medium** - Requires react-swipeable for horizontal gestures, CSS scroll-snap

---

### **Option B: Enhanced Vertical Scroll (Current, Improved)**

#### Layout Structure
```
┌──────────────────────────────────────────┐
│  ← [Jan 6] →  | Week | Month | Day      │ Navigation + View Toggle
├──────────────────────────────────────────┤
│  📊 Week Summary: 402 TSS | 12.5 hrs    │ Summary Bar (top priority)
├──────────────────────────────────────────┤
│  Mon  Tue  Wed  Thu  Fri  Sat  Sun      │ Week Grid
│   6    7    8    9   10   11   12       │
│  🟦   🟧   🟦   ⚪   🟩   🟪   ⚪       │
│  85   45   92    -  120   60    -       │
├──────────────────────────────────────────┤
│  ← [Dec 30][Jan 6][Jan 13][Jan 20] →    │ Week Picker (centered)
└──────────────────────────────────────────┘
```

#### Features
- **Vertical navigation** (keep current approach)
- **Move summary to top** (higher priority than week picker)
- **Center week selector** at bottom
- **Add Day view toggle** in header
- **Larger day cells** in week grid (more space now)

#### Pros
✅ Minimal changes to current code  
✅ Summary more prominent at top  
✅ Centered week selector improves context  
✅ Day view adds missing functionality  

#### Cons
⚠️ Vertical navigation less intuitive for time  
⚠️ Takes more vertical space (summary + picker)  
⚠️ Still feels cramped on small screens  

#### Implementation Complexity
**Low** - Mostly layout reorganization

---

### **Option C: Day View Primary + Week Context Bar**

#### Layout Structure
```
┌──────────────────────────────────────────┐
│  ← Monday, Jan 6, 2026 →                 │ Day Navigation
├──────────────────────────────────────────┤
│  M  T  W  T  F  S  S  (mini week bar)   │ Week Context
│  6  7  8  9 10 11 12                     │
│  ●  ○  ●  ○  ●  ●  ○                     │ Activity Dots
├──────────────────────────────────────────┤
│  🏃 Morning Run                          │
│  TSS: 85 | 60 min | 10K                  │
│  ─────────────────────────                │
│  🚴 Evening Ride                         │
│  TSS: 120 | 90 min | 40K                 │
├──────────────────────────────────────────┤
│  📊 Day Total: 205 TSS | 2.5 hrs         │
└──────────────────────────────────────────┘
```

#### Features
- **Day view as primary** interface
- **Horizontal swipe** changes days
- **Mini week bar** shows context (which day in week)
- **Full workout details** visible in day view
- **Week/Month toggle** in header for overview

#### Pros
✅ Maximum detail visibility  
✅ Horizontal swipe feels natural  
✅ Week context bar shows position  
✅ Less information density issues  

#### Cons
⚠️ Loses week-at-a-glance overview  
⚠️ More navigation required (swipe 7x to see week)  
⚠️ Doesn't match training app conventions  

#### Implementation Complexity
**Medium-High** - New day view component, swipe coordination

---

### **Option D: Hybrid Collapsible (Advanced)**

#### Layout Structure
```
┌──────────────────────────────────────────┐
│  ← January 2026 → | 📅 Week | Day       │ Header + Toggle
├──────────────────────────────────────────┤
│  [Collapsed Week View]                   │
│  M  T  W  T  F  S  S                     │ Compact
│  6  7  8  9 10 11 12                     │
│  ●  ●  ●  ○  ●  ●  ○                     │ Dots only
│  ▼ Expand                                │
├──────────────────────────────────────────┤
│  [OR Expanded Week View]                 │
│  Mon  Tue  Wed  Thu  Fri  Sat  Sun      │ Full detail
│   6    7    8    9   10   11   12       │
│  🟦   🟧   🟦   ⚪   🟩   🟪   ⚪       │
│  85   45   92    -  120   60    -       │
│  ▲ Collapse                              │
└──────────────────────────────────────────┘
```

#### Features
- **Collapsible week view** - compact by default
- **Expand for detail** - tap to see full week grid
- **Horizontal swipe** in both modes
- **Saves space** when navigating multiple weeks
- **Full detail on demand**

#### Pros
✅ Flexible - users choose information density  
✅ Space-efficient for navigation  
✅ Full detail when needed  
✅ Innovative approach  

#### Cons
⚠️ More complex interaction model  
⚠️ State management complexity  
⚠️ May confuse users (two modes)  
⚠️ Non-standard pattern  

#### Implementation Complexity
**High** - Multiple view states, animation, gesture handling

---

## Recommended Solution: **Option A (Horizontal Week Scroll)**

### Why This Wins

1. **Industry Standard** - Matches TrainingPeaks, Strava, Apple Calendar patterns
2. **Natural Gestures** - Horizontal swipe for time navigation feels intuitive
3. **Solves Space Issues** - Frees vertical space for day content
4. **Temporal Context** - Centered week selector shows "where you are"
5. **Fast Navigation** - Momentum scrolling lets users jump weeks quickly
6. **Proven UX** - Used by millions in fitness apps daily

### Phase 1 Implementation (Quick Win)

**Changes to Current Code:**

1. **Reorder Header Components**
   - Move week summary to bottom of AppBar (or remove from header entirely)
   - Move week picker to top (higher priority)
   - Add Day/Week/Month toggle in top row

2. **Enable Horizontal Scrolling for Week Grid**
   - Change MobileWeekGrid to horizontal scroll container
   - Add scroll-snap CSS for week boundaries
   - Keep vertical scroll for day content WITHIN each week

3. **Center Selected Week in Picker**
   - Show current week + 2 weeks on each side (5 total)
   - Scroll picker to center selected week on mount
   - Add subtle fade edges to indicate more content

4. **Improve Week Grid Spacing**
   - Since summary moves out of way, increase cell height
   - Show 2 metrics per day (TSS + duration OR distance)
   - Larger touch targets for day cells

### Phase 2 Enhancements (Future)

5. **Add Day View**
   - Tap day cell → slide up day detail panel
   - Show all workouts/activities for that day
   - Allow quick actions (add workout, reschedule, etc.)

6. **Momentum/Fling Scrolling**
   - Add velocity-based scrolling for week picker
   - Snap to week boundaries after fling
   - Haptic feedback on week change (iOS)

7. **Advanced Gestures**
   - Long-press day → quick action menu
   - Pull-to-refresh → sync latest data
   - Pinch on week → zoom to day view (experimental)

---

## Alternative: Quick Fix (Option B - Enhanced Vertical)

If horizontal scrolling is too complex right now, do this:

### Immediate Changes (30 min)

1. **Reorder AppBar:**
   ```tsx
   <AppBar>
     <Toolbar>← [Jan 6] → | Week | Month | Day</Toolbar>
     <WeeklySummaryBar /> {/* Move to top */}
     <WeekPicker /> {/* Move to bottom, CENTER it */}
   </AppBar>
   ```

2. **Center Week Picker:**
   ```tsx
   <Box sx={{ 
     display: 'flex', 
     justifyContent: 'center', // Center the picker
     overflowX: 'auto',
     scrollSnapType: 'x mandatory', // Snap to weeks
   }}>
   ```

3. **Add Day View Toggle:**
   ```tsx
   <ToggleButtonGroup>
     <ToggleButton value="day">Day</ToggleButton>
     <ToggleButton value="week">Week</ToggleButton>
     <ToggleButton value="month">Month</ToggleButton>
   </ToggleButtonGroup>
   ```

4. **Increase Week Grid Cell Size:**
   - Change minHeight from 130 to 150px
   - Show 2 lines of info per day instead of 1

---

## Feature Toggle Strategy (A/B Testing)

Add both patterns behind feature flags:

```tsx
// FeatureFlagsContext.tsx
export interface FeatureFlags {
  mobileCalendarHorizontalScroll: boolean; // Option A
  mobileCalendarDayView: boolean; // Day view toggle
  mobileCalendarSummaryTop: boolean; // Summary at top vs bottom
}
```

### Test Variants

**Variant A**: Horizontal scroll, centered week, summary bottom  
**Variant B**: Vertical scroll, centered week, summary top  
**Control**: Current implementation  

Users can switch in Settings → Experimental Features.

After 2 weeks, check:
- Which variant has higher engagement (DAU, sessions per user)?
- Which variant has longer session duration?
- User feedback via in-app survey

---

## Decision Matrix

| Criteria | Option A (Horizontal) | Option B (Vertical) | Option C (Day View) | Option D (Hybrid) |
|----------|----------------------|---------------------|---------------------|-------------------|
| **Matches Industry Patterns** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Natural Gestures** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Information Density** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Implementation Effort** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Week Context** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Navigation Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Learning Curve** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Total Score** | **32/35** | **26/35** | **27/35** | **26/35** |

---

## Implementation Roadmap

### **Recommended Path: Option A with fallback to Option B**

#### Week 1: Research & Design
- ✅ Complete (this document)
- Create Figma mockups for Option A
- User testing with mockups (optional)

#### Week 2: Quick Fix (Option B)
- Reorder AppBar components
- Center week selector
- Add Day view toggle (shell only)
- Test on real devices

#### Week 3-4: Full Implementation (Option A)
- Implement horizontal scroll container
- Add scroll-snap for weeks
- Implement momentum/fling scrolling
- Add haptic feedback
- Build Day view component
- Test gestures on multiple devices

#### Week 5: Polish & Feature Flags
- Add A/B testing infrastructure
- Deploy both variants behind flags
- Collect analytics
- User feedback survey

#### Week 6: Decide & Ship
- Analyze A/B test results
- Choose winning variant
- Remove losing variant
- Ship to production

---

## Technical Implementation Notes

### Horizontal Scroll Setup

```tsx
// Container with snap points
<Box
  sx={{
    display: 'flex',
    overflowX: 'auto',
    scrollSnapType: 'x mandatory',
    WebkitOverflowScrolling: 'touch',
    '&::-webkit-scrollbar': { display: 'none' },
  }}
>
  {weeks.map((week) => (
    <Box
      key={week.getTime()}
      sx={{
        flex: '0 0 100%', // Each week takes full width
        scrollSnapAlign: 'start',
      }}
    >
      <MobileWeekGrid week={week} />
    </Box>
  ))}
</Box>
```

### Swipe Gesture Handler

```tsx
import { useSwipeable } from 'react-swipeable';

const swipeHandlers = useSwipeable({
  onSwipedLeft: () => nextWeek(),
  onSwipedRight: () => prevWeek(),
  delta: 50, // Minimum swipe distance
  trackMouse: false, // Touch only
  preventScrollOnSwipe: false, // Allow vertical scroll
});
```

### Centered Week Picker Scroll

```tsx
useEffect(() => {
  const pickerContainer = pickerRef.current;
  if (!pickerContainer) return;
  
  // Find selected week element
  const selectedWeek = document.querySelector('[data-selected="true"]');
  if (!selectedWeek) return;
  
  // Scroll to center
  const containerWidth = pickerContainer.offsetWidth;
  const weekLeft = selectedWeek.offsetLeft;
  const weekWidth = selectedWeek.offsetWidth;
  const scrollTo = weekLeft - (containerWidth / 2) + (weekWidth / 2);
  
  pickerContainer.scrollTo({ left: scrollTo, behavior: 'smooth' });
}, [currentWeekStart]);
```

---

## Success Metrics

Track these to measure improvement:

1. **User Engagement**
   - Daily active users (DAU)
   - Session duration
   - Calendar page views per session

2. **Navigation Efficiency**
   - Average time to reach desired week
   - Number of swipes/taps per session
   - Bounce rate from calendar page

3. **User Satisfaction**
   - In-app feedback score
   - Feature request mentions
   - Bug reports related to calendar

4. **Technical Performance**
   - Page load time
   - Gesture response time (< 16ms for 60fps)
   - Memory usage

---

## Next Steps

**Choose your path:**

1. **Fast & Safe**: Implement Option B (30 min) → Ship today
2. **Best UX**: Implement Option A (1 week) → Ship next week
3. **Data-Driven**: Implement both behind feature flags → A/B test for 2 weeks

**My recommendation**: Start with Option B quick fix TODAY, then build Option A properly over next week. This gives users immediate improvement while you work on the optimal solution.

Ready to implement? Let me know which option you want to proceed with!
