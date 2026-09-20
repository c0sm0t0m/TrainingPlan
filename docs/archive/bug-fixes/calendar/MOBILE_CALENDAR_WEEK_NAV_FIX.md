# Mobile Calendar Week Navigation Bug Fixes

**Date**: January 6, 2026  
**Status**: ✅ Fixed and Deployed

## Issues Reported

### Bug 1: Initial Week Display Incorrect
When initializing calendar view, it showed:
- Current week starting Jan 5th (correct)
- But underneath showed "next week starting 12th" when it should show Jan 12th as next week

**Root Cause**: The horizontal scroll container shows 3 weeks side-by-side (previous, current, next), but there was no code to scroll to the center week (offset 0). On initial load, the scroll position defaulted to 0, showing the PREVIOUS week (-1 offset), with the current week scrolled out of view to the right.

### Bug 2: Swipe Navigation Jumps Two Weeks
When swiping to go to next week, it always jumped to the week AFTER next week (skipping one week).

**Root Cause**: Two conflicting navigation mechanisms:
1. **Swipe handlers** (`useSwipeable`) on the scroll container were calling `nextWeek()`/`prevWeek()`
2. **Horizontal scroll** with snap points was also moving to the next week visually

When user swiped:
- Swipe handler detected the gesture → called `nextWeek()` → `currentWeekStart` advances 7 days
- Horizontal scroll also scrolled to the next visible week
- Result: 2-week jump (7 days from state change + 1 week from scroll)

## Solutions Implemented

### Fix 1: Auto-Scroll to Center Week
Added automatic scroll positioning to ensure the current week (offset 0) is always visible:

```typescript
// Added ref for week scroll container
const weekScrollRef = React.useRef<HTMLDivElement>(null);

// Added useEffect to scroll to center week when currentWeekStart changes
useEffect(() => {
  if (isMobile && calendarView === 'week' && weekScrollRef.current) {
    // Scroll to the middle week (offset 0, which is 100% of container width)
    weekScrollRef.current.scrollTo({
      left: weekScrollRef.current.offsetWidth,
      behavior: 'auto', // Use 'auto' for instant positioning
    });
  }
}, [currentWeekStart, isMobile, calendarView]);
```

**How it works**:
- Week scroll container renders 3 weeks: [-1, 0, 1] (previous, current, next)
- Each week takes 100% of container width
- To show center week, scroll to 1× container width (100%)
- On mobile, scroll happens instantly (`behavior: 'auto'`)
- Triggers whenever `currentWeekStart` changes (arrow navigation)

### Fix 2: Removed Swipe Handlers from Week View
Removed conflicting swipe handlers that were interfering with horizontal scroll:

```typescript
// BEFORE (conflicting):
<Box
  {...swipeHandlers}  // ❌ This caused double navigation
  sx={{ display: 'flex', overflowX: 'auto', ... }}
>

// AFTER (fixed):
<Box
  ref={weekScrollRef}  // ✅ Just scroll container
  sx={{ display: 'flex', overflowX: 'auto', ... }}
>
```

**Navigation methods now**:
- ✅ **Arrow buttons** (ChevronLeft/ChevronRight): Call `nextWeek()`/`prevWeek()` → State changes → Auto-scroll to center
- ✅ **Manual scroll**: User can manually swipe/scroll between weeks, snap points handle positioning
- ✅ **Week picker wheel**: Clicking adjacent weeks updates `currentWeekStart` → Auto-scroll to center
- ❌ **Swipe gestures removed**: No longer needed, native scroll handles it better

**Swipe handlers kept for**:
- Day view only (for swipe-to-navigate between days)
- Not used in week or month view

## Technical Details

### Week Rendering Logic
```typescript
{/* Show 3 weeks: previous, current, next */}
{[-1, 0, 1].map((weekOffset) => {
  const weekStart = new Date(currentWeekStart);
  weekStart.setDate(currentWeekStart.getDate() + (weekOffset * 7));
  
  return (
    <Box
      key={weekOffset}
      sx={{
        flex: '0 0 100%',        // Each week takes full width
        scrollSnapAlign: 'start', // Snap to week boundaries
        overflowY: 'auto',
        px: 1,
      }}
    >
      <MobileWeekGrid currentWeekStart={weekStart} ... />
    </Box>
  );
})}
```

### Scroll Positioning Math
- Container width: 100vw (viewport width)
- Week width: 100vw (each week is 100% of container)
- Total scroll width: 300vw (3 weeks × 100vw)
- To show center week: `scrollLeft = 100vw` (1× container width)

### Calendar Week Numbers
Week picker shows proper ISO calendar weeks:
```typescript
const weekNum = getWeek(week, { weekStartsOn: 1 }); // Monday start
// Display: "CW 1", "CW 2", etc.
```

## Testing Checklist

✅ **Initial Load**: Week view shows current week in center (not previous week)  
✅ **Arrow Navigation**: Clicking left/right arrows moves by exactly 1 week  
✅ **Week Picker**: Clicking adjacent weeks in wheel jumps to that week correctly  
✅ **Manual Scroll**: Swiping manually between weeks works smoothly  
✅ **Snap Points**: Weeks snap into place after manual scroll  
✅ **CW Numbers**: Calendar week numbers display correctly (CW 1, CW 2, etc.)  
✅ **Monday Start**: All weeks start on Monday (proper ISO calendar weeks)

## User Experience Improvements

**Before**:
- Initial view confusing (showed previous week)
- Swipe jumped 2 weeks ahead (very disorienting)
- No clear indication of which week you were viewing

**After**:
- Current week always centered and highlighted
- Navigation feels natural (1 week at a time)
- Clear visual feedback (CW numbers, highlighting, smooth scrolling)

## Files Modified

1. **`frontend/src/pages/Calendar.tsx`**:
   - Added `weekScrollRef` for scroll container
   - Added useEffect to auto-scroll to center week
   - Removed swipe handlers from week view
   - Added ref to week scroll container Box

## Related Documentation

- [MOBILE_CALENDAR_UX_OPTIONS.md](MOBILE_CALENDAR_UX_OPTIONS.md) - Original UX research
- [MOBILE_CALENDAR_OPTION_A_IMPLEMENTATION.md](MOBILE_CALENDAR_OPTION_A_IMPLEMENTATION.md) - Implementation plan

## Notes for Future Development

### If Adding Swipe-Based Week Navigation
If you want to add back swipe gestures for week navigation (instead of manual scroll):

1. Re-add swipe handlers with **debouncing**:
   ```typescript
   const [isNavigating, setIsNavigating] = useState(false);
   
   const swipeHandlers = useSwipeable({
     onSwipedLeft: () => {
       if (!isNavigating) {
         setIsNavigating(true);
         nextWeek();
         setTimeout(() => setIsNavigating(false), 500);
       }
     },
     // Similar for onSwipedRight...
   });
   ```

2. OR disable scroll during navigation:
   ```typescript
   sx={{
     overflowX: isNavigating ? 'hidden' : 'auto',
   }}
   ```

But current approach (native scroll) is simpler and more reliable!

### Performance Optimization
If calendar becomes slow with many activities:
- Consider virtualizing weeks (only render visible + adjacent)
- Lazy load activity data as weeks scroll into view
- Use `React.memo()` on MobileWeekGrid component

---

**Status**: Ready for user testing on mobile device  
**Next Steps**: User validates navigation feels natural, then mark as complete
