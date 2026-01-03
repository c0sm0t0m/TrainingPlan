# Garmin Training API Research

## Summary

The **Garmin Connect Developer Program Training API** is the official way to programmatically schedule workouts to users' Garmin Connect calendars. This is the API that Training Peaks and other platforms use.

## Key Findings

### 1. Official Training API
- **URL**: https://developer.garmin.com/gc-developer-program/training-api/
- **Purpose**: Publish structured workouts and training plans directly to Garmin Connect calendar
- **Architecture**: REST API
- **Access**: Requires business approval (free but application required)

### 2. What It Provides
✅ Publish workouts directly to Garmin Connect calendar (scheduled)
✅ Publish training plans with multiple workouts
✅ Automatic sync to compatible Garmin devices
✅ Multi-project support
✅ Complete control over workout details and steps

### 3. How It Differs from Consumer API
The `garminconnect` library we're currently using accesses the **consumer API** (used by Garmin Connect website/app). The Training API is a separate **business/partner API** with different:
- Authentication (business OAuth credentials)
- Endpoints (dedicated training endpoints)
- Permissions (can schedule directly to calendar)
- Rate limits (throttled during development, higher in production)

### 4. Requirements to Use Training API

#### Application Process
1. Visit: https://www.garmin.com/en-US/forms/GarminConnectDeveloperAccess/
2. Apply as a business developer
3. Provide:
   - Business/app description
   - Use case
   - Expected user volume
   - Integration details

#### What's Included After Approval
- API documentation (not publicly available)
- Production environment access (throttled for testing)
- OAuth credentials specific to Training API
- Sample integration code
- Direct support team access
- Garmin Connect logo/branding usage rights

### 5. Integration Approach

#### Current State (Consumer API)
```python
# Using garminconnect library
api.upload_workout(workout_json)  # Uploads to workout library
# ❌ Cannot schedule to calendar - consumer API limitation
```

#### With Training API (After Approval)
```python
# Using official Training API
POST /training-api/v1/workouts
{
  "workout": {...},
  "scheduledDate": "2026-01-01"  # ✅ Scheduled directly to calendar
}
```

### 6. Recommendation

#### Short Term (Current Implementation)
- ✅ Continue using consumer API for workout upload
- ✅ Document manual calendar step for users
- ✅ Provide clear instructions in UI

#### Long Term (Production Ready)
1. **Apply for Garmin Connect Developer Program**
   - Free but requires business justification
   - Approval timeline: typically 1-2 weeks
   
2. **Implement Training API Integration**
   - New OAuth flow with business credentials
   - New endpoints for workout scheduling
   - Automatic calendar scheduling
   
3. **Maintain Consumer API as Fallback**
   - For users who haven't granted business-level permissions
   - For testing/development

### 7. Alternative: FIT Files

If Training API approval is not feasible, FIT workout files with scheduling data can be uploaded via consumer API, but this is more complex:
- Requires FIT encoder library
- Requires proper FIT message structure for workouts
- Schedule field may not be honored by consumer upload endpoint

## Next Steps

### Option 1: Apply for Training API (Recommended)
1. Prepare business case
2. Submit application
3. Wait for approval
4. Implement official API integration

### Option 2: Document Current Limitation
1. Update UI to show workout upload success
2. Provide clear manual calendar instructions
3. Add link to Garmin Connect workouts page
4. Consider in-app tutorial for calendar scheduling

### Option 3: Community OAuth Scopes Research
1. Research if consumer OAuth can request additional scopes
2. Check if `training-write` scope exists for consumer apps
3. Test alternate endpoints with consumer credentials

## References

- [Garmin Connect Developer Program](https://developer.garmin.com/gc-developer-program/)
- [Training API Overview](https://developer.garmin.com/gc-developer-program/training-api/)
- [Application Form](https://www.garmin.com/en-US/forms/GarminConnectDeveloperAccess/)
- [Contact Support](mailto:connect-support@developer.garmin.com)

## Conclusion

**The Training API is the correct solution for scheduled workout uploads.** The consumer API (`garminconnect` library) cannot schedule workouts to the calendar - this is a deliberate limitation to protect the Garmin ecosystem.

Training Peaks and similar platforms have business partnerships with Garmin and use the official Training API. We need to follow the same path for production use.
