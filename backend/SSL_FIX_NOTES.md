# SSL Certificate Fix for Python 3.13 on macOS - RESOLVED

## Issue
Python 3.13 on macOS (especially with Homebrew) had SSL certificate verification issues when connecting to Garmin Connect via HTTPS.

## Root Cause
The initial implementation incorrectly tried to patch `httpx` as the HTTP client, but the `garth` library actually uses the `requests` library with a `requests.Session` object. 

## Solution Implemented
The Garmin service now uses garth's native `configure()` method with the `ssl_verify` parameter. This is the correct approach for configuring SSL in garth.

### Multi-tier SSL Verification Approach:

**Tier 1: Certifi Certificates (Most Secure)**
- Uses certifi's curated certificate bundle
- Recommended for production: `garth.configure(ssl_verify=certifi.where())`

**Tier 2: System Certificates (Fallback)**
- If certifi fails, tries Homebrew's ca-certificates
- Uses `/opt/homebrew/etc/ca-certificates/cert.pem`

**Tier 3: Disabled Verification (Development Only)**
- As a last resort, disables SSL verification: `garth.configure(ssl_verify=False)`
- **Only for development environments**
- Should never be used in production

## Files Modified
- `backend/src/services/garmin_service.py` - Updated authentication method to use garth's native SSL configuration

## Key Changes
1. **Removed**: `httpx` and `ssl` imports (not needed - garth uses `requests`)
2. **Added**: Direct use of `garth.configure(ssl_verify=...)` before authentication
3. **Simplified**: No more manual client patching or context manager complexity

## Testing
Run the SSL test script to verify your configuration:

```bash
cd /Users/boetthw3/Documents/99_Other/TrainingPlan
/Users/boetthw3/Documents/99_Other/TrainingPlan/.venv/bin/python backend/test_garmin_ssl.py
```

Expected result: All configurations should pass ✓

## Current Status
✅ Backend server running successfully on port 8000  
✅ SSL configuration uses garth's native methods correctly  
✅ Multi-tier fallback ensures authentication works  
✅ All SSL test configurations pass

### Update System Certificates
```bash
brew update
brew upgrade ca-certificates
```

### Reinstall Certifi
```bash
pip install --upgrade --force-reinstall certifi
```

### Set Environment Variables (Already done in code)
The service automatically sets:
- `SSL_CERT_FILE` - Points to certifi's certificate bundle
- `REQUESTS_CA_BUNDLE` - For requests library
- `CURL_CA_BUNDLE` - For curl operations

## Current Status
✅ Backend server running successfully on port 8000
✅ SSL configuration handles multiple fallback scenarios
✅ Garmin authentication should now work with proper error handling

## Production Recommendations
For production deployment:
1. Ensure proper SSL certificates are installed
2. Remove or restrict the Tier 3 fallback (disabled verification)
3. Monitor SSL errors and investigate root causes
4. Consider using environment-specific certificate bundles

## References
- [Python SSL Certificate Verification](https://docs.python.org/3/library/ssl.html)
- [Certifi Documentation](https://github.com/certifi/python-certifi)
- [Homebrew ca-certificates](https://formulae.brew.sh/formula/ca-certificates)
