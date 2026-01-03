# Garmin Authentication Troubleshooting Guide

## ✅ Fixed: SSL Certificate Issues
The SSL certificate issues with Python 3.13 on macOS have been resolved using the `truststore` package.

## ✅ Fixed: Activities Not Syncing
**Issue:** Raw `garth` library was not properly fetching activities even though authentication worked.

**Solution:** Switched to `garminconnect` library which provides proper high-level wrappers around the Garmin Connect API. This library correctly handles activity fetching and other API calls.

**Library Change:**
- **Old:** `garth==0.4.46` (low-level OAuth library)
- **New:** `garminconnect==0.2.36` (high-level Garmin Connect API wrapper)

## Current Status
- ✅ Backend authentication: Working
- ✅ Garmin API connection: Working  
- ✅ Activity syncing: Working with garminconnect library
- ✅ Error handling: Improved with detailed messages

## Common Errors and Solutions

### Error: "Invalid Garmin email or password"
**Cause:** 401 Unauthorized from Garmin
**Solutions:**
1. **Double-check your credentials**
   - Verify email and password are correct
   - Passwords are case-sensitive
   - No extra spaces before/after

2. **Check for 2FA/MFA**
   - If you have two-factor authentication enabled on Garmin
   - You may need to create an app-specific password
   - Go to: https://connect.garmin.com/modern/settings/profile
   - Look for "App-Specific Passwords" or security settings

3. **Verify your Garmin account**
   - Try logging in at https://connect.garmin.com first
   - Make sure your account is active and not locked

### Error: "Too many login attempts"
**Cause:** 429 Rate Limiting from Garmin
**Solution:** Wait 5-10 minutes before trying again

### Error: "Access denied by Garmin"
**Cause:** 403 Forbidden
**Solutions:**
- Your account may be temporarily locked
- Try logging in at connect.garmin.com first
- Contact Garmin support if the issue persists

### Error: "Garmin Connect is experiencing issues"
**Cause:** 500/502/503 Server Errors
**Solution:** This is a Garmin server issue. Wait and try again later.

## Testing Your Setup

### 1. Test via Terminal (for developers)
```bash
cd backend
./test_full_flow.sh
```

### 2. Test via UI
1. Make sure backend is running: `lsof -ti:8000`
2. Open the frontend: http://localhost:3000
3. Login to your TrainingPlan account
4. Navigate to Settings > Garmin Connect
5. Enter your Garmin credentials
6. Click "Connect"

## For Developers

### Running the Backend
```bash
cd backend
PYTHONPATH=$PWD /path/to/.venv/bin/uvicorn src.main:app --reload --port 8000
```

### Manual API Test
```bash
# 1. Get auth token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=YOUR_EMAIL&password=YOUR_PASSWORD" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Test Garmin connection
curl -X POST http://localhost:8000/api/v1/garmin/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"email":"YOUR_GARMIN_EMAIL","password":"YOUR_GARMIN_PASSWORD"}'
```

## Dependencies
The following packages are required:
- `truststore==0.10.4` - SSL certificate handling for Python 3.13+
- `garminconnect==0.2.36` - High-level Garmin Connect API client (includes garth)
- `certifi` - CA certificate bundle

All dependencies are in `requirements.txt`.

## Key Difference: garth vs garminconnect

### garth (Low-Level)
- Direct OAuth1/OAuth2 implementation
- Requires manual API endpoint construction
- Raw `connectapi()` calls return inconsistent results

### garminconnect (High-Level - RECOMMENDED)
- Built on top of garth
- Provides convenient methods: `get_activities()`, `get_user_summary()`, etc.
- Handles API quirks and response formatting
- **Use this for production!**

## Need Help?
If you continue to experience issues:
1. Check the backend logs for detailed error messages
2. Verify your Garmin account works at connect.garmin.com
3. Try the automated test script to isolate the issue
4. Check if you have 2FA enabled and need an app-specific password
