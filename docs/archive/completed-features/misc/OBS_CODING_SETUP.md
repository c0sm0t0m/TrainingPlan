# OBS Studio Setup for Coding Reels

## Initial Setup (First Time)

1. **Launch OBS**
   ```bash
   open -a OBS
   ```

2. **Auto-Configuration Wizard** (will appear on first launch)
   - Select: "Optimize for Recording"
   - Canvas Resolution: **1080x1920** (Portrait for Instagram Reels)
   - FPS: **30** or **60**
   - Click "Apply Settings"

## Manual Configuration for Instagram Reels

### Video Settings
1. **Settings → Video**
   - Base Canvas: **1080x1920** (9:16 portrait)
   - Output Resolution: **1080x1920**
   - FPS: **30** (or 60 for smoother animations)

### Output Settings
1. **Settings → Output → Recording**
   - Recording Path: `~/Movies/OBS_Recordings`
   - Recording Format: **MP4** (best for mobile editing)
   - Encoder: **Apple VT H264 Hardware Encoder** (if available, faster)
   - Quality: **High Quality**
   - Bitrate: **8000-12000 Kbps**

### Hotkeys (Recommended)
1. **Settings → Hotkeys**
   - Start Recording: `⌘ + Shift + R`
   - Stop Recording: `⌘ + Shift + S`
   - Pause Recording: `⌘ + Shift + P`

## Scene Setup for Coding

### Scene 1: Full Screen Code (Main View)
1. Click **"+"** under Sources
2. Add **"Display Capture"** or **"Window Capture"**
   - For Display: Captures entire screen
   - For Window: Select VS Code window (more flexible)
3. **Transform → Fit to Screen** (Right-click source)
4. Add **"Audio Input Capture"** for microphone (optional)

### Scene 2: Code + Webcam (PiP)
1. Copy Scene 1
2. Add **"Video Capture Device"** (your webcam)
3. Resize webcam to small circle in corner
4. Right-click webcam → Filters → Add **"Chroma Key"** (if using green screen)

### Scene 3: Terminal Focus
1. Add **"Window Capture"** → Select Terminal
2. Fit to screen

## Recording Tips for Reels

### Before Recording
- [ ] Clean up desktop/dock (hide distractions)
- [ ] Increase VS Code font size (16-18pt minimum)
- [ ] Use high-contrast theme (Dracula, One Dark Pro, Tokyo Night)
- [ ] Close unnecessary tabs/windows
- [ ] Test audio levels

### During Recording
- **Quick Session** (30-60 seconds of real coding)
- **Time-lapse** (Record 5-10 mins, speed up in editing)
- **Tutorial** (Explain while coding with voiceover)

### Keyboard Shortcuts
```
⌘ + Shift + R - Start Recording
⌘ + Shift + S - Stop Recording
⌘ + Shift + P - Pause Recording
```

## Quick Start Commands

```bash
# Open OBS
open -a OBS

# View recordings folder
open ~/Movies/OBS_Recordings

# Convert to Instagram format (if needed)
# Install ffmpeg: brew install ffmpeg
ffmpeg -i input.mp4 -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k instagram_ready.mp4
```

## Recommended VS Code Extensions for Recording

1. **Peacock** - Color your workspace
2. **Error Lens** - Inline error highlights (looks good)
3. **Bracket Pair Colorizer** - Visual appeal
4. **Material Icon Theme** - Pretty file icons

## Post-Recording Workflow

1. **Export from OBS** → MP4 in `~/Movies/OBS_Recordings`
2. **Edit on CapCut** (free):
   - Import video
   - Speed up (1.5-3x for time-lapse)
   - Add captions/text
   - Add trending music
   - Export 9:16 format
3. **Upload to Instagram Reels**

## Troubleshooting

### OBS Window Not Capturing
- Grant Screen Recording permission: System Settings → Privacy & Security → Screen Recording → Enable OBS

### Low Quality Output
- Increase bitrate in Output settings (try 12000 Kbps)
- Use Apple VT H264 encoder (hardware acceleration)

### Audio Not Recording
- Add "Audio Input Capture" source
- Check audio mixer levels (bottom of OBS window)

## Advanced: Auto-start Recording Profile

Create a shell script to open OBS with your coding profile:

```bash
#!/bin/bash
# ~/bin/start-coding-recording.sh

open -a OBS --args --profile "Coding" --scene "Full Screen Code"
```

Make it executable:
```bash
chmod +x ~/bin/start-coding-recording.sh
```

---

**Ready to start!** Open OBS and follow the setup above. Press `⌘ + Shift + R` to start recording your first coding session! 🎥
