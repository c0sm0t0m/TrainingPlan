# Trainer Style Selection - User Guide

## Overview
The AI Training Plan Generator now includes **10 world-renowned coaching methodologies** that you can select to customize your training plan generation.

## How to Use

### Step-by-Step Process

#### 1. Navigate to AI Plan Generator
- Go to **Training Plans** → **Generate AI Training Plan** button
- Or click **AI-powered plan** from the dashboard

#### 2. Select Your Event (Step 1)
- Choose an existing target event or enter new event details
- Provide: Event name, date, distance, and goal time

#### 3. Configure Your Plan (Step 2)
- Set start date
- Choose training days per week (3-7)
- Select preferred training days
- Add any general notes/constraints

#### 4. **Choose Your Trainer Style (Step 3)** ← NEW!

This is where you select your coaching methodology:

##### **Option A: Choose a Trainer Style**
Select from 10 professional coaching methodologies:

1. **Joe Friel** - Periodization Pioneer
   - Best for: Structured, data-driven training
   - Focus: TSS/CTL metrics, clear base/build/peak/taper phases
   - Training: 70-80% easy, progressive overload, 3:1 build-to-rest ratio

2. **Matt Fitzgerald** - 80/20 Endurance
   - Best for: Volume-focused runners/triathletes
   - Focus: 80% easy running, 20% hard running (no middle ground)
   - Training: High volume at low intensity, polarized approach

3. **Jack Daniels** - VDOT Training
   - Best for: Science-minded runners who love data
   - Focus: VDOT-calculated training paces (E/M/T/I/R)
   - Training: Every run has a specific physiological purpose

4. **Stephen Seiler** - Polarized Training
   - Best for: Research-backed training
   - Focus: 75-80% very easy, 10-15% very hard, minimal moderate
   - Training: 2-3 hard sessions max per week, avoid "gray zone"

5. **Renato Canova** - Marathon Master
   - Best for: Marathon-focused runners
   - Focus: Long runs with marathon pace segments
   - Training: Aggressive race-pace work in fatigued state

6. **Phil Maffetone** - MAF Training
   - Best for: Building aerobic base, fat adaptation
   - Focus: 180-minus-age heart rate training
   - Training: Months of pure aerobic training before intensity

7. **Brad Hudson** - Adaptive Running
   - Best for: Intuitive runners who train by feel
   - Focus: Medium-long runs (75-90min), run by effort
   - Training: Adjust daily based on how you feel

8. **Greg McMillan** - Goal-Based Training
   - Best for: Race-specific training with precise paces
   - Focus: McMillan calculator paces, goal-oriented
   - Training: Balance endurance, stamina, and speed

9. **Dave Scott** - Triathlon Legend
   - Best for: Triathletes seeking high volume
   - Focus: Brick workouts, multi-sport balance
   - Training: High volume, mental toughness development

10. **Pete Magill** - Masters Specialist
    - Best for: Runners over 40
    - Focus: Recovery first, maintain speed with short bursts
    - Training: Strength work, injury prevention, smart progression

##### **Option B: View Detailed Methodology**
Click **"Show Detailed Methodology"** to see:
- Complete training philosophy
- Key workout types (5-7 signature workouts)
- Periodization structure (base/build/peak/taper phases)
- Recovery strategy
- Special emphasis points

##### **Option C: Add Custom Instructions (Optional)**
In the text area, add your own training philosophy:
- **Example**: "Focus on hill training, prefer 400-800m intervals, include weekly strength session"
- Your custom instructions EXTEND the base trainer methodology
- They don't replace it - they add to it

#### 5. Generate Prompt (Step 4)
- Review all your selections
- Click **"Generate Prompt"**
- Wait for the personalized prompt to be created

#### 6. Use the Prompt (Step 5)
- Copy the generated prompt
- Open ChatGPT or Claude AI
- Paste and send the prompt
- Copy the JSON response
- Import via **Training Plans** → **Import AI Plan**

## Example Use Cases

### Use Case 1: Marathon Training (First-Timer)
**Goal**: Run first marathon in 16 weeks

**Selections**:
- Event: Local Marathon, 16 weeks out
- Training: 5 days/week (Mon, Wed, Thu, Sat, Sun)
- **Trainer**: Joe Friel (structured periodization)
- **Why**: Clear phases, beginner-friendly progression

**Result**: 16-week plan with:
- 4 weeks base building
- 6 weeks building intensity
- 4 weeks peak/race-specific
- 2 weeks taper
- Every workout has warmup/intervals/cooldown details

### Use Case 2: Experienced Runner (Sub-3:00 Marathon)
**Goal**: Break 3 hours in marathon

**Selections**:
- Event: Boston Marathon, 20 weeks out
- Training: 6 days/week
- **Trainer**: Jack Daniels (VDOT Training)
- **Custom**: "Current VDOT: 55, prefer morning runs, access to track"
- **Why**: Science-based pacing, proven for competitive runners

**Result**: 20-week plan with:
- VDOT-calculated training paces
- E/M/T/I/R workouts with exact paces
- Track intervals (e.g., 6x1000m @ I pace)
- Threshold runs (e.g., 3x2 miles @ T pace)

### Use Case 3: Masters Runner (50+ years old)
**Goal**: Stay fit and race occasionally

**Selections**:
- Event: Half Marathon, 12 weeks out
- Training: 4 days/week (Tue, Thu, Sat, Sun)
- **Trainer**: Pete Magill (Masters Specialist)
- **Custom**: "Avoid back-to-back hard days, include strength training"
- **Why**: Recovery-focused, injury prevention, maintains speed

**Result**: 12-week plan with:
- Extra recovery emphasis
- Short speed work (strides, 400m repeats)
- Strength training 2x/week
- Easy runs truly easy
- Reduced taper (2 weeks vs 3)

### Use Case 4: Triathlete (Ironman Training)
**Goal**: Complete first Ironman

**Selections**:
- Event: Ironman, 24 weeks out
- Training: 6 days/week
- **Trainer**: Dave Scott (Triathlon Legend)
- **Custom**: "Weak swimmer, need more pool time, prefer brick sessions"
- **Why**: Multi-sport balance, high volume, mental toughness

**Result**: 24-week plan with:
- Swim/Bike/Run distribution (20%/40%/35%)
- Weekly brick workouts
- Open water swimming emphasis
- Long bike-to-run transitions
- Race nutrition practice

## Tips for Best Results

### 1. Match Trainer to Your Goal
- **Marathon**: Joe Friel, Jack Daniels, Renato Canova, Greg McMillan
- **Triathlon**: Joe Friel, Dave Scott
- **Build Base**: Phil Maffetone, Stephen Seiler
- **Masters**: Pete Magill
- **Feel-Based**: Brad Hudson, Matt Fitzgerald

### 2. Review the Methodology
Always click **"Show Detailed Methodology"** to understand:
- What workouts to expect
- How intensity is distributed
- Recovery philosophy
- Special requirements

### 3. Use Custom Instructions Wisely
Add custom instructions for:
- **Specific constraints**: "No running on Wednesdays (gym day)"
- **Equipment access**: "Have access to track, prefer track intervals"
- **Preferences**: "Morning runner, need 15min warmup"
- **Weaknesses**: "Weak hill climbing, need more hill work"

### 4. Understand the Prompt
The generated prompt will include:
- Your fitness data (last 6 weeks)
- Current thresholds (pace/HR/power)
- Selected trainer methodology
- Custom instructions
- Detailed workout requirements
- JSON format requirements

### 5. Review AI Output
When AI generates your plan:
- Check workout details (warmup/main/cooldown)
- Verify interval specifications (e.g., "6x800m @ Zone 5")
- Confirm taper phase is included (last 2-3 weeks)
- Ensure workout types match trainer philosophy

## Customization Examples

### Example 1: Modify Joe Friel for Hill Focus
**Base Trainer**: Joe Friel (Periodization)
**Custom Instructions**:
```
Add weekly hill repeats in build phase (8-12x90sec hills).
Replace some threshold intervals with hill tempo runs.
Include downhill running drills for quad strength.
```

### Example 2: Adapt Matt Fitzgerald 80/20 for Limited Time
**Base Trainer**: Matt Fitzgerald (80/20)
**Custom Instructions**:
```
Reduce long run from 120min to 90min (time constraints).
Focus on quality over quantity for hard workouts.
Use fast-finish runs (last 15min) instead of separate tempo runs.
```

### Example 3: Combine Seiler Polarized with Race-Specific Work
**Base Trainer**: Stephen Seiler (Polarized)
**Custom Instructions**:
```
Add race-pace segments to long runs in final 6 weeks.
Include 2 race simulations (practice pacing and nutrition).
Maintain polarized approach but add goal marathon pace work.
```

## Frequently Asked Questions

### Q: Can I change trainers mid-plan?
**A**: Generate a new prompt with a different trainer. You can import multiple plans and switch between them.

### Q: Do I need to follow the trainer exactly?
**A**: No! Use custom instructions to modify the approach. The trainer provides the framework, you customize the details.

### Q: What if I don't know which trainer to choose?
**A**: Start with **Joe Friel** (Periodization) - it's versatile and beginner-friendly. You can always regenerate with a different trainer.

### Q: Can I combine multiple trainers?
**A**: Yes! Select a base trainer and use custom instructions to incorporate elements from others. Example: "Use Joe Friel's periodization but apply Matt Fitzgerald's 80/20 intensity distribution."

### Q: Will AI follow my trainer selection?
**A**: Yes, the AI is instructed to follow the trainer methodology closely. The prompt includes explicit instructions, workout types, and periodization structure.

### Q: Do I get interval details now?
**A**: Yes! Every workout includes:
- Warmup (duration + intensity)
- Main work (e.g., "5x1000m @ Zone 4 with 2min recovery")
- Cooldown (duration + intensity)
- Additional notes (form cues, nutrition)

### Q: Is tapering included?
**A**: Yes! All 10 trainers include explicit taper phases (typically 2-3 weeks with reduced volume but maintained intensity).

## Technical Details

### Backend API
```bash
# Get all trainer styles
GET /api/v1/ai-training-plan/trainer-styles

# Get specific trainer details
GET /api/v1/ai-training-plan/trainer-styles/joe_friel
```

### Prompt Generation
```python
# Configuration includes trainer style
{
  "startDate": "2026-02-01",
  "trainingDaysPerWeek": 5,
  "preferredTrainingDays": ["monday", "wednesday", "friday", "saturday", "sunday"],
  "trainerStyle": "joe_friel",
  "customTrainerInstructions": "Focus on hill training...",
  "additionalNotes": "General notes..."
}
```

### Trainer Profile Structure
Each trainer includes:
- Name and tagline
- Description (overview)
- Philosophy (multi-paragraph methodology)
- Training distribution (by phase)
- Key workouts (5-7 signature workouts)
- Periodization structure (phase breakdown)
- Recovery strategy
- Special emphasis (critical points)

## Support

If you have questions or feedback about trainer styles:
1. Check this guide first
2. Review the generated prompt - it shows the full methodology
3. Experiment with different trainers and compare
4. Use custom instructions to fine-tune

**Remember**: The goal is to provide you with world-class coaching methodologies that you can customize to fit your unique situation. No trainer is "perfect" - use them as frameworks and adapt as needed!

---

**Happy Training! 🏃‍♂️🚴‍♂️🏊‍♂️**
