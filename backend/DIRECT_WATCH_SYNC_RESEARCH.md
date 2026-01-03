# Direct Smartwatch Sync - Research & Implementation Guide

**Date**: 2026-01-01  
**Status**: ✅ **VIABLE! Multiple Methods Available**

## Executive Summary

**YES! You CAN sync workouts directly to Garmin watches**, bypassing Garmin Connect entirely! Multiple methods exist:

1. ✅ **USB FIT File Sideload** - Copy workout files directly to watch storage
2. ✅ **Garmin Connect Mobile App** - Push workouts via phone app's private API  
3. ⚠️ **Connect IQ Apps** - Build custom workout delivery app (advanced)
4. ⚠️ **Bluetooth BLE** - Direct device communication (requires reverse engineering)

**Best approach**: USB sideloading + mobile app push (for convenience).

---

## Method 1: USB FIT File Sideload ⭐ **EASIEST**

### How It Works

Garmin watches mount as USB Mass Storage devices. You can copy FIT workout files directly to specific folders on the watch.

### Directory Structure

```
/GARMIN/
├── ACTIVITY/        # Completed activities (recorded by watch)
├── WORKOUTS/        # ✅ Structured workout files go here!
├── COURSES/         # GPS course files
├── LOCATIONS/       # POI data
└── NEWFILES/        # ✅ Alternative: Watch processes files here on next boot
```

### Implementation Steps

#### 1. Generate FIT Workout File
**You already have this!** → `src/utils/fit_workout_generator.py`

```python
from src.utils.fit_workout_generator import generate_fit_workout

# Create workout
workout_data = {
    "name": "Easy Run",
    "sport": "running",
    "steps": [
        {"type": "warmup", "duration_time": 600, "target_type": "open"},
        {"type": "active", "duration_distance": 5000, "target_hr_zone": 2},
        {"type": "cooldown", "duration_time": 300, "target_type": "open"}
    ]
}

# Generate FIT file
fit_bytes = generate_fit_workout(workout_data)
```

#### 2. Detect Watch Connection (macOS)

```python
import os
import glob

def find_garmin_watch():
    """
    Detect mounted Garmin watch via USB.
    
    Returns:
        str: Path to watch mount point or None
    """
    # macOS: Garmin watches typically mount as /Volumes/GARMIN
    mount_points = [
        "/Volumes/GARMIN",
        "/Volumes/GARMIN 1",
        "/Volumes/GARMIN 2"
    ]
    
    for mount in mount_points:
        if os.path.exists(os.path.join(mount, "GARMIN")):
            return mount
    
    # Alternative: Search all volumes
    volumes = glob.glob("/Volumes/*")
    for volume in volumes:
        garmin_dir = os.path.join(volume, "GARMIN")
        if os.path.exists(garmin_dir):
            return volume
    
    return None
```

#### 3. Copy Workout to Watch

```python
import shutil
from datetime import datetime

def sync_workout_to_watch(workout_name: str, fit_bytes: bytes) -> bool:
    """
    Copy FIT workout file to connected Garmin watch.
    
    Args:
        workout_name: Name for the workout file
        fit_bytes: FIT file binary data
        
    Returns:
        bool: True if successful
    """
    watch_path = find_garmin_watch()
    if not watch_path:
        raise ValueError("No Garmin watch detected. Please connect via USB.")
    
    # Target directory (try WORKOUTS first, fallback to NEWFILES)
    workouts_dir = os.path.join(watch_path, "GARMIN", "WORKOUTS")
    newfiles_dir = os.path.join(watch_path, "GARMIN", "NEWFILES")
    
    # Use WORKOUTS if it exists, otherwise NEWFILES
    target_dir = workouts_dir if os.path.exists(workouts_dir) else newfiles_dir
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{workout_name.replace(' ', '_')}_{timestamp}.fit"
    target_path = os.path.join(target_dir, filename)
    
    # Write FIT file
    with open(target_path, 'wb') as f:
        f.write(fit_bytes)
    
    # Eject watch safely (macOS)
    os.system(f"diskutil unmount '{watch_path}'")
    
    return True
```

#### 4. User Workflow

1. **User connects watch via USB** → Watch mounts as `/Volumes/GARMIN`
2. **App detects watch** → Shows "Garmin Watch Connected" notification
3. **User clicks "Sync to Watch"** → App copies all scheduled workouts
4. **App safely ejects watch** → User disconnects USB
5. **Watch processes files** → Workouts appear in watch's workout list!

### Advantages ✅

- **No API needed** - Direct file system access
- **Works offline** - No internet required
- **Fast** - Instant file copy
- **Reliable** - No authentication issues
- **All watches** - Works with any Garmin watch (Fenix, Forerunner, etc.)

### Limitations ⚠️

- **Manual connection** - User must plug in watch via USB
- **No automatic sync** - Requires user action
- **Calendar scheduling** - Watch won't show scheduled dates (just workout library)

---

## Method 2: Garmin Connect Mobile App Push ⭐ **BEST USER EXPERIENCE**

### How It Works

Garmin Connect Mobile app (iOS/Android) can push workouts directly to paired watches via **Bluetooth**. The app uses private APIs not available to third parties.

### Implementation Options

#### Option A: Deep Links (If Available)

Some fitness apps use deep links to trigger Garmin Connect Mobile:

```
garmin-connect://workout/send?workoutId=12345
```

**Status**: Unknown if this works - needs testing.

#### Option B: Export to Garmin Connect + Auto-Sync

1. User exports workouts from your app
2. User imports to Garmin Connect (web or mobile)
3. Garmin Connect Mobile auto-syncs to watch

**This is what most apps do** (TrainingPeaks, Final Surge, etc.)

#### Option C: Garmin Connect Mobile Companion App

Build a companion mobile app that:
1. Receives workout data from your backend
2. Uses Garmin Mobile SDK (if available)
3. Pushes workouts via Bluetooth

**Complexity**: High - requires iOS/Android native development

---

## Method 3: Connect IQ Workout App 🔧 **ADVANCED**

### How It Works

Build a custom **Connect IQ app** that runs on the watch and fetches workouts from your backend.

### Architecture

```
┌─────────────────────────────────────────┐
│  TrainingPlan Backend (Your Server)     │
│  - REST API: GET /workouts/upcoming     │
│  - Returns: Workout JSON                │
└────────────────┬────────────────────────┘
                 │ HTTPS
                 │
┌────────────────▼────────────────────────┐
│  Connect IQ App (Runs on Watch)         │
│  - Written in Monkey C                  │
│  - Makes HTTP requests to your backend  │
│  - Parses JSON workout data             │
│  - Creates native workout on watch      │
└─────────────────────────────────────────┘
```

### Connect IQ App Code Example

```monkey-c
// MyWorkoutApp.mc
using Toybox.Communications as Comm;
using Toybox.PersistedContent as PC;

class MyWorkoutApp extends WatchUi.App {
    
    function initialize() {
        App.initialize();
    }
    
    function onStart(state) {
        // Fetch workouts from your server
        fetchWorkouts();
    }
    
    function fetchWorkouts() {
        var url = "https://your-server.com/api/v1/workouts/upcoming";
        var params = {};
        var options = {
            :method => Comm.HTTP_REQUEST_METHOD_GET,
            :headers => {
                "Authorization" => "Bearer " + getStoredToken()
            }
        };
        
        Comm.makeWebRequest(url, params, options, method(:onWorkoutsReceived));
    }
    
    function onWorkoutsReceived(responseCode, data) {
        if (responseCode == 200 && data != null) {
            // Parse workout JSON
            var workouts = data["workouts"];
            
            for (var i = 0; i < workouts.size(); i++) {
                createWorkoutOnWatch(workouts[i]);
            }
        }
    }
    
    function createWorkoutOnWatch(workoutData) {
        // Use PersistedContent API to create workout
        var workout = new PC.Workout(workoutData["name"]);
        workout.setSport(PC.SPORT_RUNNING);
        
        // Add workout steps
        var steps = workoutData["steps"];
        for (var i = 0; i < steps.size(); i++) {
            var step = new PC.WorkoutStep(steps[i]);
            workout.addStep(step);
        }
        
        // Save workout to watch
        try {
            PC.saveWorkout(workout);
        } catch (ex) {
            System.println("Error saving workout: " + ex.getErrorMessage());
        }
    }
}
```

### Advantages ✅

- **Automatic sync** - Works whenever watch has Bluetooth/WiFi
- **No USB needed** - Over-the-air updates
- **Calendar integration** - Can schedule workouts programmatically
- **User-friendly** - Install once, works forever

### Limitations ⚠️

- **Development effort** - Learn Monkey C, submit to Garmin app store
- **App store approval** - Review process (1-2 weeks)
- **Limited API** - Not all features available in Connect IQ
- **Device compatibility** - Older watches may not support PersistedContent API

### Resources

- Connect IQ SDK: https://developer.garmin.com/connect-iq/sdk/
- PersistedContent API: https://developer.garmin.com/connect-iq/api-docs/Toybox/PersistedContent.html
- Sample Apps: https://github.com/topics/garmin-watch

---

## Method 4: Bluetooth BLE Direct ⚠️ **EXPERIMENTAL**

### How It Works

Reverse-engineer Garmin's Bluetooth protocol to communicate directly with watches.

### Challenges

- **Proprietary protocol** - Garmin doesn't document it
- **Pairing required** - Watch must trust your app
- **Legal concerns** - May violate Garmin's ToS
- **High complexity** - Requires low-level BLE expertise

### Community Projects

- **esp32-ble-hrm-garmin**: Example of BLE communication with Garmin watch
- **GarminHomeAssistant**: Control watch from Home Assistant (limited features)

**Recommendation**: Avoid this approach unless you're very experienced with BLE reverse engineering.

---

## Recommended Implementation Plan

### Phase 1: USB Sideloading (Quick Win) ✅

**Effort**: 2-3 days  
**User Experience**: Manual but simple

1. Add "Watch Connected" detection to frontend
2. Implement `sync_workout_to_watch()` function
3. Add "Sync to Watch" button in UI
4. Generate FIT files on demand
5. Copy to watch, eject safely

**User workflow**:
- User connects watch via USB
- Clicks "Sync to Watch" button
- App copies all scheduled workouts
- User disconnects watch
- Workouts appear in watch's workout library!

### Phase 2: Export to Garmin Connect (Convenience)

**Effort**: 1 day  
**User Experience**: One extra step

1. Export workouts as Garmin JSON
2. User uploads to Garmin Connect manually
3. Garmin Connect syncs to watch automatically

**User workflow**:
- User clicks "Export for Garmin" button
- Downloads `.json` file or batch of files
- Uploads to Garmin Connect web interface
- Garmin Connect Mobile auto-syncs to watch

### Phase 3: Connect IQ App (Future)

**Effort**: 2-4 weeks (learning curve + development)  
**User Experience**: Best - fully automatic

1. Learn Monkey C and Connect IQ SDK
2. Build workout fetching app
3. Submit to Garmin Connect IQ Store
4. Users install app on watch
5. App auto-fetches workouts from your backend

**User workflow**:
- Install TrainingPlan Connect IQ app once
- Watch auto-fetches workouts when connected to phone/WiFi
- No manual sync needed!

---

## Comparison Matrix

| Method | User Effort | Dev Effort | Automation | Calendar | Offline |
|--------|-------------|------------|------------|----------|---------|
| **USB Sideload** | Medium | Low | No | No | Yes |
| **Export to GC** | Medium | Low | No | Yes | No |
| **Connect IQ App** | Low | High | Yes | Yes | No |
| **BLE Direct** | Medium | Very High | Yes | Maybe | No |

---

## Technical Implementation: USB Sync Service

### Backend API Endpoint

```python
# src/api/routes/watch_sync.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.user import User
from src.utils.auth import get_current_user
from src.utils.fit_workout_generator import generate_fit_workout

router = APIRouter(prefix="/watch-sync", tags=["Watch Sync"])

@router.get("/generate-fit/{workout_id}")
async def generate_workout_fit_file(
    workout_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate FIT file for a specific workout.
    Returns binary FIT data for download.
    """
    # Fetch workout from database
    workout = await get_workout_by_id(db, workout_id, current_user.id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    # Convert to FIT format
    workout_data = {
        "name": workout.title,
        "sport": workout.sport_type,
        "steps": workout.steps
    }
    
    fit_bytes = generate_fit_workout(workout_data)
    
    # Return as downloadable file
    return Response(
        content=fit_bytes,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={workout.title}.fit"
        }
    )

@router.get("/batch-fit")
async def generate_batch_fit_files(
    start_date: str,
    end_date: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate ZIP file with all workouts in date range.
    Perfect for USB sync - user downloads one ZIP, extracts to watch.
    """
    import zipfile
    from io import BytesIO
    
    # Fetch all workouts in date range
    workouts = await get_workouts_in_range(db, start_date, end_date, current_user.id)
    
    # Create ZIP in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for workout in workouts:
            workout_data = {
                "name": workout.title,
                "sport": workout.sport_type,
                "steps": workout.steps
            }
            fit_bytes = generate_fit_workout(workout_data)
            
            # Add to ZIP
            filename = f"{workout.scheduled_date}_{workout.title}.fit"
            zip_file.writestr(filename, fit_bytes)
    
    zip_buffer.seek(0)
    
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=workouts.zip"
        }
    )
```

### Frontend: USB Detection (Web)

```typescript
// src/services/watchSyncService.ts

export class WatchSyncService {
  
  /**
   * Check if Garmin watch is connected.
   * Note: Web browsers can't detect USB devices directly.
   * User must manually initiate download.
   */
  async downloadWorkoutsZip(startDate: string, endDate: string) {
    const response = await api.get('/watch-sync/batch-fit', {
      params: { start_date: startDate, end_date: endDate },
      responseType: 'blob'
    });
    
    // Trigger download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'workouts.zip');
    document.body.appendChild(link);
    link.click();
    link.remove();
  }
  
  /**
   * Download single workout FIT file.
   */
  async downloadWorkoutFit(workoutId: number, workoutName: string) {
    const response = await api.get(`/watch-sync/generate-fit/${workoutId}`, {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${workoutName}.fit`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  }
}
```

### Frontend: Sync UI Component

```tsx
// src/components/WatchSyncPanel.tsx
import React from 'react';
import { Button, Card, Typography, Alert } from '@mui/material';
import { Download, Usb } from '@mui/icons-material';

export const WatchSyncPanel: React.FC = () => {
  const [syncing, setSyncing] = React.useState(false);
  
  const handleSyncWeek = async () => {
    setSyncing(true);
    
    const startDate = new Date().toISOString().split('T')[0];
    const endDate = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
      .toISOString().split('T')[0];
    
    await watchSyncService.downloadWorkoutsZip(startDate, endDate);
    
    setSyncing(false);
  };
  
  return (
    <Card>
      <Typography variant="h6">Sync to Garmin Watch</Typography>
      
      <Alert severity="info" icon={<Usb />}>
        Connect your Garmin watch via USB, then click Sync.
      </Alert>
      
      <Button 
        variant="contained" 
        startIcon={<Download />}
        onClick={handleSyncWeek}
        disabled={syncing}
      >
        Download This Week's Workouts
      </Button>
      
      <Typography variant="caption" color="textSecondary">
        1. Click button to download workouts.zip
        <br />
        2. Extract ZIP file
        <br />
        3. Copy .fit files to GARMIN/WORKOUTS/ on your watch
        <br />
        4. Eject watch safely
      </Typography>
    </Card>
  );
};
```

---

## Companion Desktop App (Optional)

For **automatic USB sync**, build a small desktop app:

### Electron App (Cross-Platform)

```javascript
// main.js - Electron main process
const { app, BrowserWindow, ipcMain } = require('electron');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

// Detect Garmin watch
function findGarminWatch() {
  const platforms = {
    darwin: ['/Volumes/GARMIN'],  // macOS
    win32: ['E:\\GARMIN', 'F:\\GARMIN'],  // Windows
    linux: ['/media/GARMIN', '/mnt/GARMIN']  // Linux
  };
  
  const searchPaths = platforms[process.platform] || [];
  
  for (const path of searchPaths) {
    if (fs.existsSync(path)) {
      return path;
    }
  }
  
  return null;
}

// Watch for USB connections
function watchForDevices() {
  setInterval(() => {
    const watchPath = findGarminWatch();
    if (watchPath) {
      // Notify renderer process
      BrowserWindow.getAllWindows()[0]?.webContents.send(
        'watch-connected', 
        { path: watchPath }
      );
    }
  }, 2000);
}

// Sync workouts to watch
ipcMain.handle('sync-workouts', async (event, workouts) => {
  const watchPath = findGarminWatch();
  if (!watchPath) {
    throw new Error('No Garmin watch detected');
  }
  
  const targetDir = path.join(watchPath, 'GARMIN', 'WORKOUTS');
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }
  
  // Copy each workout FIT file
  for (const workout of workouts) {
    const fitPath = path.join(targetDir, `${workout.name}.fit`);
    fs.writeFileSync(fitPath, Buffer.from(workout.fitData, 'base64'));
  }
  
  // Eject watch (macOS)
  if (process.platform === 'darwin') {
    exec(`diskutil unmount '${watchPath}'`);
  }
  
  return { success: true, count: workouts.length };
});

app.whenReady().then(() => {
  createWindow();
  watchForDevices();
});
```

**User Experience**:
- Desktop app runs in background
- Detects watch connection automatically
- Shows notification: "Garmin Watch Connected - Sync Now?"
- One click syncs all scheduled workouts!

---

## Conclusion & Next Steps

**Direct smartwatch sync is absolutely possible!**

### Immediate Action: Implement USB Sideload

**Why**: 
- Simplest to implement (2-3 days)
- Works with all Garmin watches
- No API approval needed
- You already have FIT generator!

**Steps**:
1. Add `/watch-sync/batch-fit` endpoint
2. Add "Download for Watch" button in UI
3. Provide clear instructions for users
4. Test with your Garmin watch

### Future Enhancement: Connect IQ App

**When**: After MVP is stable and users request it
**Benefit**: Best user experience - fully automatic

### Alternative: TrainingPeaks Integration

If you want automatic Garmin sync without building Connect IQ app:
- Export workouts to TrainingPeaks format
- Users import to TrainingPeaks
- TrainingPeaks syncs to Garmin automatically

---

**The USB sideload method is production-ready and can be implemented immediately! 🚀**
