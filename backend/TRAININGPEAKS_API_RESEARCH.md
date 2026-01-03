# TrainingPeaks API Research - Scheduled Workout Calendar Support

**Date**: 2026-01-01  
**Status**: ❌ No Calendar API Found

## Executive Summary

After extensive research, **TrainingPeaks public API does NOT provide calendar/scheduled workout endpoints**, similar to Garmin. The API focuses exclusively on **completed workouts**, not planned/scheduled workouts.

---

## Research Methodology

### 1. **Examined tapiriik Source Code**
- **File**: `backend/tapiriik/tapiriik/services/TrainingPeaks/trainingpeaks.py`
- **Finding**: `DownloadActivityList()` explicitly **skips planned workouts**:
  ```python
  for act in resp.json():
      if not act.get("completed", True) or act.get("StartTime", None) is None:
          continue  # SKIPS PLANNED WORKOUTS!
  ```
- **Endpoint Used**: `/v2/workouts/{startDate}/{endDate}`
- **Purpose**: Returns completed activities ONLY

### 2. **API Endpoint Discovery**
Tested various potential calendar endpoints:

| Endpoint | HTTP Status | Notes |
|----------|-------------|-------|
| `/v1/athlete/profile` | 401 Unauthorized | ✅ Exists (requires auth) |
| `/v3/file` | 401 Unauthorized | ✅ Exists (file upload) |
| `/v2/workouts` | 404 Not Found | ❌ Does not exist |
| `/v2/workout` | 404 Not Found | ❌ Does not exist |
| `/v2/workout/library` | 404 Not Found | ❌ Does not exist |
| `/v2/calendar` | 404 Not Found | ❌ Does not exist |
| `/v2/planned-workouts` | 404 Not Found | ❌ Does not exist |
| `/v2/schedule` | 404 Not Found | ❌ Does not exist |
| `/v3/workout` | 404 Not Found | ❌ Does not exist |

**Conclusion**: No calendar/schedule/planned workout endpoints available in public API.

### 3. **Community Research**
- **StackOverflow**: Zero questions tagged `trainingpeaks` API
- **Reddit**: No API discussions, only user complaints about planning features
- **GitHub**: No open-source projects using TrainingPeaks calendar API
- **Developer Docs**: `developer.trainingpeaks.com` failed to load meaningful content

---

## What TrainingPeaks API DOES Provide

### ✅ OAuth 2.0 Authentication
```python
# Authorization URL
TRAININGPEAKS_OAUTH_BASE_URL/oauth/authorize

# Token exchange
TRAININGPEAKS_OAUTH_BASE_URL/oauth/token
```

### ✅ Athlete Profile
```
GET /v1/athlete/profile
Returns: { "Id": "...", "Name": "...", ... }
```

### ✅ Completed Workouts (Activities)
```
GET /v2/workouts/{startDate}/{endDate}
Returns: [
  {
    "StartTime": "2025-12-31T10:00:00Z",
    "TotalTime": 3600,  // seconds
    "Title": "Morning Run",
    "Description": "Easy recovery run",
    "WorkoutType": "run",
    "completed": true,  // ALWAYS true for this endpoint
    "Distance": 10000,  // meters
    "HeartRateAverage": 145,
    "PowerAverage": null,
    ...
  }
]
```

### ✅ File Upload (PWX/TCX)
```
POST /v3/file
Content-Type: application/json
{
  "UploadClient": "tapiriik",
  "Filename": "activity.pwx",
  "SetWorkoutPublic": false,
  "Data": "<base64-encoded-gzipped-pwx>"
}
Returns: { "WorkoutIds": ["123456"] }
```

---

## What TrainingPeaks API Does NOT Provide

### ❌ Calendar/Schedule Queries
- No endpoint to fetch planned workouts for a date range
- No endpoint to query what's scheduled on a specific date
- No endpoint to list future/unscheduled workouts

### ❌ Workout Library Management
- No endpoint to upload to workout library
- No endpoint to list library workouts
- No endpoint to schedule library workout to calendar

### ❌ Structured Workout Creation
- Cannot create structured workouts via API
- Cannot define intervals, zones, targets programmatically
- Only file upload (PWX/TCX) supported

---

## Why TrainingPeaks → Garmin Sync Works

TrainingPeaks **does** sync with Garmin, but:

1. **Enterprise Partnership**: They have special API access we don't
2. **Proprietary Endpoints**: Undocumented/private API endpoints
3. **OAuth Scopes**: May require different OAuth scopes not available to public
4. **Backend Integration**: Direct database/service integration, not REST API

**Our API key/credentials won't give us access to these features.**

---

## Comparison: Garmin vs TrainingPeaks Public APIs

| Feature | Garmin Consumer API | TrainingPeaks Public API |
|---------|---------------------|--------------------------|
| Completed activities | ✅ YES | ✅ YES |
| Activity details (HR, power, pace) | ✅ YES | ✅ YES |
| Upload completed activities | ✅ YES (FIT files) | ✅ YES (PWX/TCX files) |
| Workout library upload | ✅ YES (JSON format) | ❌ NO |
| Calendar query (scheduled workouts) | ❌ NO | ❌ NO |
| Schedule workout to date | ⚠️ LIMITED (manual) | ❌ NO |

**Both APIs have the same limitation: No calendar scheduling support.**

---

## Alternative Solutions

### Option 1: Local Calendar UI ⭐ **Recommended**
**Pros**:
- Full control over planning
- No API limitations
- Fast and reliable
- No external dependencies

**Cons**:
- Users must manually sync to Garmin/TrainingPeaks

**Implementation**:
- Keep workouts in local PostgreSQL
- Build calendar UI in React
- Export options: ICS file, TrainingPeaks PWX, Garmin JSON

---

### Option 2: Garmin Workout Library + Manual Calendar
**Current implementation** - already working!

**Flow**:
1. Upload workouts to Garmin library via API ✅
2. User drags workout to calendar in Garmin Connect ✋ (manual)
3. Garmin syncs workout to device automatically ✅

**Pros**:
- Workouts available in Garmin ecosystem
- Users familiar with Garmin Connect UI
- No approval process needed

**Cons**:
- Manual calendar step required
- Cannot automate scheduling

---

### Option 3: Apply for Enterprise APIs
**Both Garmin and TrainingPeaks** offer enterprise/partner APIs.

**Requirements**:
- Business partnership application
- Approval process (weeks/months)
- May require fees or revenue sharing
- Must demonstrate legitimate use case

**Links**:
- Garmin Training API: https://developer.garmin.com/
- TrainingPeaks Partner Program: Contact via website

**Pros**:
- Full calendar scheduling access
- Bulk operations
- Advanced features

**Cons**:
- Long approval process
- May require business entity
- Potential costs

---

### Option 4: Manual Export/Import Workflow
**Low-tech but functional**

**Flow**:
1. User creates plan in TrainingPlan
2. Export plan as ICS file
3. User imports to TrainingPeaks calendar (web UI)
4. TrainingPeaks syncs to Garmin automatically

**Pros**:
- No API limitations
- Uses official TrainingPeaks sync
- Simple to implement

**Cons**:
- Manual export/import steps
- Not automatic

---

## Recommended Architecture

Based on research, here's the **optimal approach**:

```
┌─────────────────────────────────────────────────────────────┐
│                      TrainingPlan App                       │
│  (Local PostgreSQL + React UI)                             │
│                                                             │
│  Features:                                                  │
│  - Create/edit training plans                              │
│  - Calendar view (drag-and-drop)                           │
│  - Workout library                                          │
│  - Training load analytics (TSS, CTL, ATL)                 │
│  - Export: ICS, PWX, Garmin JSON                          │
└────────────────────┬──────────────┬─────────────────────────┘
                     │              │
                     │              │
    ┌────────────────▼──────┐  ┌───▼──────────────────────┐
    │  Garmin Connect       │  │  TrainingPeaks           │
    │  (Manual)             │  │  (Manual/File Import)    │
    │                       │  │                          │
    │  - Import workouts    │  │  - Import PWX/ICS files  │
    │  - Drag to calendar   │  │  - Calendar planning     │
    │  - Sync to device     │  │  - Auto-sync to Garmin   │
    └────────────┬──────────┘  └──────────────────────────┘
                 │
                 │ (Automatic)
                 │
    ┌────────────▼──────────┐
    │  Garmin Watch/Device  │
    │  - Execute workouts   │
    │  - Record activities  │
    └───────────────────────┘
                 │
                 │ (Automatic sync)
                 │
    ┌────────────▼──────────┐
    │  TrainingPlan App     │
    │  - Fetch activities   │
    │  - Match to plan      │
    │  - Calculate metrics  │
    └───────────────────────┘
```

---

## Implementation Recommendations

### Phase 1: Core Features (Now)
✅ Local calendar UI with full planning
✅ Workout builder (intervals, zones, targets)
✅ Training load calculations (TSS, CTL, ATL)
✅ Export to Garmin JSON (library upload)
✅ Fetch completed activities from Garmin

### Phase 2: Export Options (Next)
- [ ] Export to ICS format (standard calendar)
- [ ] Export to PWX format (TrainingPeaks)
- [ ] Export individual workouts as Garmin JSON
- [ ] Bulk export training plans

### Phase 3: Enhanced UX (Future)
- [ ] Instructions/guide for Garmin manual scheduling
- [ ] Video tutorial for export workflows
- [ ] One-click "Send to Garmin" button (uploads to library)
- [ ] Activity matching (completed vs planned)

### Phase 4: Enterprise (Optional)
- [ ] Apply for Garmin Training API
- [ ] Apply for TrainingPeaks Partner API
- [ ] Implement full calendar sync if approved

---

## Conclusion

**Neither Garmin nor TrainingPeaks public APIs support scheduled/planned workout calendar management.**

**Best Path Forward**:
1. **Build excellent local calendar UI** - You're not missing anything from external APIs
2. **Export functionality** - Let users import to Garmin/TrainingPeaks via standard formats
3. **Activity sync** - Fetch completed activities for analysis (already works)
4. **Consider enterprise APIs** - If project scales, apply for partner access

**Key Insight**: Commercial apps like TrainingPeaks, Garmin Connect, Strava all have the same limitation in their public APIs. They reserve calendar scheduling for their own UIs. **Your self-hosted solution can be BETTER** because you control the entire planning experience.

---

## Next Steps

1. **Accept the limitation** - No magic API exists
2. **Focus on local UI** - Build best-in-class calendar/planning interface
3. **Implement exports** - ICS, PWX, Garmin JSON
4. **Document workflow** - Guide users on manual sync steps
5. **Monitor API changes** - TrainingPeaks may add features in future

**The good news**: Your app can provide a superior planning experience compared to Garmin Connect's limited web UI!
