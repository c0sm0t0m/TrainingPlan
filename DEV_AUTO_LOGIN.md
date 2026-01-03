# Development Auto-Login Setup

## What Changed

### 1. Extended Token Lifetime (Backend)
- **Production**: Tokens expire after 15 minutes
- **Development**: Tokens now last **7 days** 
- File: `backend/src/config.py` - Added `effective_token_expire_minutes` property

### 2. Auto-Login on Startup (Frontend)
- Automatically logs you in when you open the app
- Uses credentials from `.env.local`
- File: `frontend/src/store/authStore.ts`

### 3. Token Caching
- Already implemented via localStorage
- Tokens persist across browser refreshes
- Combined with 7-day expiry = minimal re-logins

## How to Use

1. **Edit `frontend/.env.local`** (already created for you):
   ```bash
   VITE_DEV_AUTO_LOGIN=true
   VITE_DEV_EMAIL=tboettger@gmail.com
   VITE_DEV_PASSWORD=your_actual_password  # ← Change this!
   ```

2. **Restart the frontend dev server**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **That's it!** The app will:
   - Auto-login on first load
   - Store token in localStorage (lasts 7 days)
   - Auto-login again if token expires or is cleared

## Security Notes

⚠️ **NEVER commit `.env.local`** - It's already in `.gitignore`  
⚠️ **Only use in development** - Production still uses 15-minute tokens  
✅ **Safe for local development** - No external exposure  

## Disable Auto-Login

Set in `.env.local`:
```bash
VITE_DEV_AUTO_LOGIN=false
```

## Troubleshooting

**"Auto-login failed"** in console:
- Check credentials in `.env.local` are correct
- Make sure backend is running
- Check backend logs for auth errors

**Still being logged out:**
- Clear browser localStorage
- Restart frontend dev server
- Verify `.env.local` is in `frontend/` directory (not root)
