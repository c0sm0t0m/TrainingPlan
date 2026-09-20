# AI-Powered Training Plan Creation Feature ✅

**Status**: FULLY IMPLEMENTED (Backend + Frontend + Testing)  
**Date Completed**: January 6, 2026  
**Implementation Time**: ~4 hours

## Overview
Enable users to generate comprehensive training plans using external LLMs (ChatGPT, Claude, etc.) by providing them with a structured prompt containing their fitness data, then importing the AI-generated plan directly into the app.

## Why This Approach?
✅ **No API costs** - Users leverage their own ChatGPT/Claude subscriptions  
✅ **Privacy-friendly** - AI processing happens externally, user controls data  
✅ **Platform agnostic** - Works with any LLM (ChatGPT, Claude, Gemini, local models)  
✅ **Transparent** - User sees exactly what data is shared  
✅ **Simple implementation** - Focus on schema design and import/export  

## Feature Flow

### Phase 1: Generate AI Prompt
**User Action**: Click "Generate AI Training Plan" button  
**System Action**: Create a comprehensive prompt containing:

1. **User's Fitness Data** (last 6 weeks)
   - Total volume (hours/distance) by sport
   - Average weekly TSS
   - Current CTL/ATL/TSB values
   - Recent activity types and intensities
   - Personal bests (if available)

2. **Current Fitness Metrics**
   - Running: Threshold pace, threshold HR
   - Cycling: FTP, threshold HR
   - Swimming: Threshold pace
   - Max HR, resting HR

3. **Target Event Details**
   - Event name, date, type (race/competition)
   - Target distance
   - Goal time (if specified)
   - Location

4. **Plan Requirements**
   - Start date (usually today or next Monday)
   - End date (event date)
   - Number of weeks
   - Days per week available for training
   - Preferred training days

5. **Workout Schema Definition**
   ```json
   {
     "trainingPlan": {
       "name": "string",
       "description": "string",
       "startDate": "YYYY-MM-DD",
       "endDate": "YYYY-MM-DD",
       "sportType": "running|cycling|swimming|triathlon",
       "targetEvent": "string",
       "workouts": [
         {
           "date": "YYYY-MM-DD",
           "title": "string",
           "description": "string",
           "sportType": "running|cycling|swimming|strength",
           "workoutType": "easy|tempo|interval|long|recovery|race",
           "durationMinutes": number,
           "distanceKm": number,
           "intensityZone": "zone1|zone2|zone3|zone4|zone5",
           "targetTSS": number,
           "structuredSteps": [
             {
               "stepOrder": number,
               "stepType": "warmup|work|cooldown|rest|repeat",
               "durationType": "time|distance|lap_button",
               "durationValue": number,
               "durationUnit": "seconds|meters",
               "targetType": "pace|heart_rate|power|cadence|open",
               "targetValueLow": number,
               "targetValueHigh": number,
               "targetUnit": "bpm|watts|spm|min_per_km",
               "description": "string",
               "repeatCount": number
             }
           ],
           "notes": "string"
         }
       ]
     }
   }
   ```

6. **Instructions for LLM**
   ```
   You are a professional triathlon coach creating a personalized training plan.
   
   Based on the athlete's current fitness data and target event, create a comprehensive
   training plan following these principles:
   
   - Progressive overload: Gradually increase volume and intensity
   - Periodization: Include base, build, peak, and taper phases
   - Recovery: Include rest days and recovery weeks
   - Specificity: Target the event distance and intensity
   - Variety: Mix workout types to prevent monotony
   - Zone distribution: Follow 80/20 rule (80% easy, 20% hard)
   
   Return ONLY valid JSON matching the schema above. No additional text.
   Include 3-5 workouts per week with detailed structured steps for key workouts.
   ```

**Output**: Copy-pasteable prompt in a dialog/modal with:
- "Copy to Clipboard" button
- Link to ChatGPT/Claude
- Instructions: "Paste this into ChatGPT, copy the JSON response, then upload it here"

---

### Phase 2: User Processes with LLM
**User Action**: 
1. Copy prompt to clipboard
2. Open ChatGPT/Claude
3. Paste prompt
4. Wait for AI response
5. Copy JSON response

**LLM Output**: Complete training plan in JSON format

---

### Phase 3: Import AI-Generated Plan
**User Action**: Click "Upload AI Plan" button  
**System Action**: 

1. **File Upload**
   - Support JSON and XML formats
   - Max file size: 1MB
   - Drag-and-drop or file picker

2. **Validation**
   ```python
   def validate_training_plan(plan_data: dict) -> ValidationResult:
       """Validate imported training plan against schema."""
       required_fields = ["name", "startDate", "endDate", "sportType", "workouts"]
       
       # Check required fields
       for field in required_fields:
           if field not in plan_data:
               return ValidationResult(valid=False, error=f"Missing {field}")
       
       # Validate dates
       start_date = parse_date(plan_data["startDate"])
       end_date = parse_date(plan_data["endDate"])
       if start_date >= end_date:
           return ValidationResult(valid=False, error="End date must be after start date")
       
       # Validate workouts
       if not plan_data["workouts"]:
           return ValidationResult(valid=False, error="Plan must have at least 1 workout")
       
       for workout in plan_data["workouts"]:
           result = validate_workout(workout)
           if not result.valid:
               return result
       
       return ValidationResult(valid=True)
   ```

3. **Preview**
   - Show plan summary (name, dates, sport type, # of workouts)
   - Display calendar preview with workouts by week
   - Show total volume, TSS, workout types
   - Allow user to review before confirming

4. **Confirmation Dialog**
   ```
   Import Training Plan?
   
   Name: Berlin Marathon 16-Week Plan
   Duration: 16 weeks (Jan 8 - Apr 26, 2026)
   Sport: Running
   Workouts: 64 total
   - Easy runs: 32
   - Tempo runs: 12
   - Interval workouts: 10
   - Long runs: 10
   
   Total volume: 480 km
   Estimated TSS: 4,200
   
   [Cancel] [Import Plan]
   ```

5. **Import Process**
   ```python
   async def import_ai_training_plan(user_id: int, plan_data: dict, db: AsyncSession):
       """Import validated training plan into database."""
       
       # Create TrainingPlan
       plan = TrainingPlan(
           user_id=user_id,
           name=plan_data["name"],
           description=plan_data.get("description", ""),
           start_date=plan_data["startDate"],
           end_date=plan_data["endDate"],
           sport_type=plan_data["sportType"],
           is_active=1
       )
       db.add(plan)
       await db.flush()  # Get plan.id
       
       # Create Workouts
       for workout_data in plan_data["workouts"]:
           workout = Workout(
               training_plan_id=plan.id,
               date=workout_data["date"],
               sport_type=workout_data["sportType"],
               workout_type=workout_data["workoutType"],
               title=workout_data["title"],
               description=workout_data.get("description", ""),
               duration_minutes=workout_data.get("durationMinutes"),
               distance_km=workout_data.get("distanceKm"),
               intensity_zone=workout_data.get("intensityZone"),
               tss=workout_data.get("targetTSS"),
               notes=workout_data.get("notes", "")
           )
           db.add(workout)
           
           # Store structured steps as JSON in workout
           if "structuredSteps" in workout_data:
               workout.structured_workout_json = json.dumps(workout_data["structuredSteps"])
       
       await db.commit()
       return plan
   ```

6. **Post-Import Actions**
   - Show success message
   - Navigate to plan detail page
   - Option to sync workouts to Garmin immediately
   - Option to edit plan before syncing

---

## Data Schema Specification

### JSON Schema (Primary Format)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["trainingPlan"],
  "properties": {
    "trainingPlan": {
      "type": "object",
      "required": ["name", "startDate", "endDate", "sportType", "workouts"],
      "properties": {
        "name": {
          "type": "string",
          "description": "Plan name (e.g., 'Berlin Marathon 16-Week Plan')"
        },
        "description": {
          "type": "string",
          "description": "Detailed plan description"
        },
        "startDate": {
          "type": "string",
          "format": "date",
          "description": "Plan start date (YYYY-MM-DD)"
        },
        "endDate": {
          "type": "string",
          "format": "date",
          "description": "Plan end date (YYYY-MM-DD)"
        },
        "sportType": {
          "type": "string",
          "enum": ["running", "cycling", "swimming", "triathlon", "gym"],
          "description": "Primary sport type"
        },
        "targetEvent": {
          "type": "string",
          "description": "Target event name"
        },
        "workouts": {
          "type": "array",
          "minItems": 1,
          "items": {
            "$ref": "#/definitions/workout"
          }
        }
      }
    }
  },
  "definitions": {
    "workout": {
      "type": "object",
      "required": ["date", "title", "sportType", "workoutType"],
      "properties": {
        "date": {
          "type": "string",
          "format": "date"
        },
        "title": {
          "type": "string"
        },
        "description": {
          "type": "string"
        },
        "sportType": {
          "type": "string",
          "enum": ["running", "cycling", "swimming", "strength", "brick"]
        },
        "workoutType": {
          "type": "string",
          "enum": ["easy", "tempo", "interval", "long", "recovery", "race", "brick", "strength"]
        },
        "durationMinutes": {
          "type": "number",
          "minimum": 0
        },
        "distanceKm": {
          "type": "number",
          "minimum": 0
        },
        "intensityZone": {
          "type": "string",
          "enum": ["zone1", "zone2", "zone3", "zone4", "zone5", "zone6"]
        },
        "targetTSS": {
          "type": "number",
          "minimum": 0
        },
        "structuredSteps": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/workoutStep"
          }
        },
        "notes": {
          "type": "string"
        }
      }
    },
    "workoutStep": {
      "type": "object",
      "required": ["stepOrder", "stepType", "durationType"],
      "properties": {
        "stepOrder": {
          "type": "integer",
          "minimum": 1
        },
        "stepType": {
          "type": "string",
          "enum": ["warmup", "work", "cooldown", "rest", "repeat"]
        },
        "durationType": {
          "type": "string",
          "enum": ["time", "distance", "lap_button"]
        },
        "durationValue": {
          "type": "number"
        },
        "durationUnit": {
          "type": "string",
          "enum": ["seconds", "minutes", "meters", "kilometers"]
        },
        "targetType": {
          "type": "string",
          "enum": ["pace", "heart_rate", "power", "cadence", "open"]
        },
        "targetValueLow": {
          "type": "number"
        },
        "targetValueHigh": {
          "type": "number"
        },
        "targetUnit": {
          "type": "string",
          "enum": ["bpm", "watts", "spm", "rpm", "min_per_km", "min_per_mile"]
        },
        "description": {
          "type": "string"
        },
        "repeatCount": {
          "type": "integer",
          "minimum": 1
        }
      }
    }
  }
}
```

### XML Schema Alternative
```xml
<trainingPlan>
  <name>Berlin Marathon 16-Week Plan</name>
  <description>Progressive marathon training</description>
  <startDate>2026-01-08</startDate>
  <endDate>2026-04-26</endDate>
  <sportType>running</sportType>
  <targetEvent>Berlin Marathon 2026</targetEvent>
  
  <workouts>
    <workout>
      <date>2026-01-08</date>
      <title>Easy Run</title>
      <description>Recovery run at conversational pace</description>
      <sportType>running</sportType>
      <workoutType>easy</workoutType>
      <durationMinutes>45</durationMinutes>
      <distanceKm>8</distanceKm>
      <intensityZone>zone2</intensityZone>
      <targetTSS>40</targetTSS>
      <notes>Focus on form and breathing</notes>
    </workout>
    
    <workout>
      <date>2026-01-10</date>
      <title>Tempo Run</title>
      <sportType>running</sportType>
      <workoutType>tempo</workoutType>
      <durationMinutes>60</durationMinutes>
      <targetTSS>75</targetTSS>
      
      <structuredSteps>
        <step>
          <stepOrder>1</stepOrder>
          <stepType>warmup</stepType>
          <durationType>time</durationType>
          <durationValue>600</durationValue>
          <durationUnit>seconds</durationUnit>
          <targetType>heart_rate</targetType>
          <targetValueLow>120</targetValueLow>
          <targetValueHigh>140</targetValueHigh>
          <targetUnit>bpm</targetUnit>
          <description>10 min easy warmup</description>
        </step>
        
        <step>
          <stepOrder>2</stepOrder>
          <stepType>work</stepType>
          <durationType>time</durationType>
          <durationValue>1200</durationValue>
          <durationUnit>seconds</durationUnit>
          <targetType>pace</targetType>
          <targetValueLow>4.5</targetValueLow>
          <targetValueHigh>5.0</targetValueHigh>
          <targetUnit>min_per_km</targetUnit>
          <description>20 min tempo at threshold pace</description>
        </step>
        
        <step>
          <stepOrder>3</stepOrder>
          <stepType>cooldown</stepType>
          <durationType>time</durationType>
          <durationValue>600</durationValue>
          <durationUnit>seconds</durationUnit>
          <targetType>open</targetType>
          <description>10 min easy cooldown</description>
        </step>
      </structuredSteps>
    </workout>
  </workouts>
</trainingPlan>
```

---

## UI/UX Design

### 1. "Generate AI Plan" Button Location
**Primary**: Plans tab, prominent placement  
**Secondary**: Dashboard "Quick Actions" section  
**Design**: Large card or CTA button with sparkle/AI icon ✨

```tsx
<Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
  <CardContent>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
      <AutoAwesome sx={{ fontSize: 48, color: 'white' }} />
      <Box sx={{ flex: 1 }}>
        <Typography variant="h5" sx={{ color: 'white', fontWeight: 'bold' }}>
          Generate AI Training Plan
        </Typography>
        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
          Use ChatGPT or Claude to create a personalized training plan based on your fitness data
        </Typography>
      </Box>
      <Button variant="contained" sx={{ bgcolor: 'white', color: '#667eea' }}>
        Get Started
      </Button>
    </Box>
  </CardContent>
</Card>
```

### 2. Prompt Generation Dialog
**Step 1: Select Target Event**
- Dropdown to select existing event OR create new
- Pre-fill if navigating from event detail page

**Step 2: Configure Plan**
- Start date (default: next Monday)
- Training days per week (3-7)
- Preferred training days (Mon, Tue, Wed, etc.)
- Additional notes/constraints

**Step 3: Review & Copy Prompt**
```tsx
<Dialog open={open} maxWidth="md" fullWidth>
  <DialogTitle>
    <AutoAwesome /> Generate AI Training Plan
  </DialogTitle>
  
  <DialogContent>
    <Stepper activeStep={activeStep}>
      <Step><StepLabel>Select Event</StepLabel></Step>
      <Step><StepLabel>Configure Plan</StepLabel></Step>
      <Step><StepLabel>Get Prompt</StepLabel></Step>
    </Stepper>
    
    {activeStep === 2 && (
      <>
        <Alert severity="info" sx={{ mt: 2, mb: 2 }}>
          <AlertTitle>How to use this prompt</AlertTitle>
          <ol>
            <li>Copy the prompt below</li>
            <li>Open ChatGPT or Claude AI</li>
            <li>Paste and send the prompt</li>
            <li>Wait for AI response (JSON format)</li>
            <li>Copy the JSON and return here to upload</li>
          </ol>
        </Alert>
        
        <Paper sx={{ p: 2, bgcolor: 'grey.100', maxHeight: 400, overflow: 'auto' }}>
          <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
            {generatedPrompt}
          </Typography>
        </Paper>
        
        <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
          <Button 
            variant="contained" 
            startIcon={<ContentCopy />}
            onClick={handleCopyPrompt}
          >
            Copy to Clipboard
          </Button>
          <Button
            variant="outlined"
            startIcon={<OpenInNew />}
            onClick={() => window.open('https://chat.openai.com', '_blank')}
          >
            Open ChatGPT
          </Button>
        </Box>
      </>
    )}
  </DialogContent>
  
  <DialogActions>
    <Button onClick={onClose}>Cancel</Button>
    <Button onClick={handleNext} variant="contained">
      {activeStep === 2 ? 'I have the JSON' : 'Next'}
    </Button>
  </DialogActions>
</Dialog>
```

### 3. Import Dialog
```tsx
<Dialog open={open} maxWidth="lg" fullWidth>
  <DialogTitle>Import AI Training Plan</DialogTitle>
  
  <DialogContent>
    {!fileUploaded ? (
      <Box
        sx={{
          border: '2px dashed',
          borderColor: 'primary.main',
          borderRadius: 2,
          p: 4,
          textAlign: 'center',
          cursor: 'pointer'
        }}
        onDrop={handleFileDrop}
        onDragOver={(e) => e.preventDefault()}
      >
        <CloudUpload sx={{ fontSize: 64, color: 'primary.main' }} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Drop JSON file here or click to browse
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Supports JSON and XML formats
        </Typography>
        <Button variant="contained" sx={{ mt: 2 }} onClick={handleFileSelect}>
          Choose File
        </Button>
      </Box>
    ) : validationResult.valid ? (
      <Box>
        <Alert severity="success" sx={{ mb: 3 }}>
          Training plan validated successfully!
        </Alert>
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6">Plan Summary</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Name" 
                      secondary={planPreview.name} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Duration" 
                      secondary={`${planPreview.weeks} weeks (${planPreview.startDate} to ${planPreview.endDate})`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Sport" 
                      secondary={planPreview.sportType} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Total Workouts" 
                      secondary={planPreview.totalWorkouts} 
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6">Statistics</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Total Volume" 
                      secondary={`${planPreview.totalDistanceKm} km`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Estimated TSS" 
                      secondary={planPreview.totalTSS} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Workout Types" 
                      secondary={Object.entries(planPreview.workoutTypeBreakdown).map(([type, count]) => `${type}: ${count}`).join(', ')} 
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="h6" sx={{ mb: 2 }}>Calendar Preview</Typography>
            <Paper sx={{ p: 2, maxHeight: 400, overflow: 'auto' }}>
              {/* Calendar grid showing workouts by week */}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    ) : (
      <Alert severity="error">
        <AlertTitle>Validation Failed</AlertTitle>
        {validationResult.error}
      </Alert>
    )}
  </DialogContent>
  
  <DialogActions>
    <Button onClick={onClose}>Cancel</Button>
    <Button 
      onClick={handleImport} 
      variant="contained"
      disabled={!validationResult.valid}
    >
      Import Plan
    </Button>
  </DialogActions>
</Dialog>
```

---

## Implementation Plan

### Phase 1: Backend (3-4 hours)
**Priority: HIGH**

1. **Create API Endpoint: Generate Prompt**
   - File: `backend/src/api/routes/ai_training_plan.py`
   - Endpoint: `POST /api/v1/ai-training-plan/generate-prompt`
   - Gathers user data (activities, thresholds, CTL/ATL)
   - Accepts target event ID or inline event data
   - Returns formatted prompt string

2. **Create Pydantic Schemas**
   - File: `backend/src/api/schemas/ai_training_plan.py`
   - Define schemas for prompt generation request/response
   - Define schemas for plan import validation
   - Mirror the JSON schema defined above

3. **Create Import Endpoint**
   - File: `backend/src/api/routes/ai_training_plan.py`
   - Endpoint: `POST /api/v1/ai-training-plan/import`
   - Accepts JSON/XML file upload
   - Validates against schema
   - Returns validation result + preview data

4. **Create Validation Service**
   - File: `backend/src/services/ai_training_plan_validator.py`
   - JSON Schema validation
   - XML Schema validation
   - Business logic validation (dates, values)

5. **Create Import Service**
   - File: `backend/src/services/ai_training_plan_importer.py`
   - Parse validated JSON/XML
   - Create TrainingPlan + Workout models
   - Handle structured steps (store as JSON)
   - Return created plan ID

6. **Add Database Field for Structured Steps**
   - Add `structured_workout_json` TEXT column to `workouts` table
   - Alembic migration

### Phase 2: Frontend (5-6 hours)
**Priority: HIGH**

1. **Create AI Plan Generation Page**
   - File: `frontend/src/pages/AITrainingPlanGenerator.tsx`
   - Multi-step wizard
   - Event selection
   - Plan configuration form
   - Prompt display + copy button

2. **Create Import Component**
   - File: `frontend/src/components/AITrainingPlanImport.tsx`
   - File upload (drag-drop + file picker)
   - Validation feedback
   - Preview display
   - Import confirmation

3. **Add UI to Plans Tab**
   - Add prominent "Generate AI Plan" card
   - Link to AI plan generator page

4. **Add Routes**
   - `/ai-plan/generate` - Generator wizard
   - `/ai-plan/import` - Direct import (if user has JSON already)

5. **API Service Functions**
   - `generateAIPrompt(eventId, config)` - Get prompt
   - `importAITrainingPlan(file)` - Upload and import

### Phase 3: Testing & Documentation (2 hours)
**Priority: MEDIUM**

1. **Create Example Prompts**
   - Generate sample prompts for common scenarios
   - Running marathon
   - Sprint triathlon
   - Cycling century

2. **Create Example JSON Responses**
   - Provide working examples users can reference
   - Include in documentation

3. **User Documentation**
   - File: `docs/AI_TRAINING_PLAN_GUIDE.md`
   - Step-by-step guide with screenshots
   - Tips for working with ChatGPT
   - Common issues and fixes

4. **Integration Tests**
   - Test prompt generation with various user data
   - Test import with valid/invalid JSON
   - Test validation edge cases

### Phase 4: Enhancements (Future)
**Priority: LOW**

1. **Direct LLM Integration (Optional)**
   - Add OpenAI API key setting
   - Generate plan directly in-app
   - Requires OpenAI subscription

2. **Plan Templates Library**
   - Save successful AI plans as templates
   - Community sharing (optional)

3. **Prompt Customization**
   - Allow users to add custom instructions
   - Save prompt preferences

4. **Refinement Workflow**
   - Allow users to regenerate specific weeks
   - Tweak individual workouts post-import

---

## Technical Considerations

### Security
- **File upload**: Limit size to 1MB, validate MIME types
- **JSON parsing**: Use safe parsers, catch malformed data
- **SQL injection**: Use parameterized queries (SQLAlchemy handles this)
- **XSS**: Sanitize user-provided descriptions/notes

### Performance
- **Prompt generation**: Cache user data for 5 minutes
- **Import**: Process in background for large plans (>100 workouts)
- **Validation**: Stream-parse large JSON files

### Error Handling
- **Invalid JSON**: Show specific line/field with error
- **Date conflicts**: Warn if plan overlaps existing workouts
- **Missing data**: Graceful degradation if user has no activities

### Data Privacy
- **User consent**: Clearly state what data is included in prompt
- **External processing**: Disclaimer that AI processing happens on external servers
- **No automatic upload**: User manually copies/pastes (full control)

---

## Example Prompt Output

```
=== AI TRAINING PLAN GENERATION PROMPT ===

You are a professional endurance sports coach. Create a comprehensive, periodized training plan based on the following athlete data.

ATHLETE FITNESS DATA (Last 6 Weeks):
- Average weekly volume: 42 km running
- Average weekly TSS: 285
- Current CTL (Fitness): 45
- Current ATL (Fatigue): 38
- Current TSB (Form): +7 (Fresh)

CURRENT THRESHOLDS:
- Running threshold pace: 4:30 min/km
- Running threshold HR: 165 bpm
- Max HR: 185 bpm
- Resting HR: 52 bpm

TARGET EVENT:
- Event: Berlin Marathon 2026
- Date: 2026-09-27
- Distance: Marathon (42.2 km)
- Goal time: 3:30:00 (4:58 min/km average pace)
- Athlete's current fitness level: Intermediate (1-2 years experience)

PLAN REQUIREMENTS:
- Start date: 2026-01-13 (Monday)
- End date: 2026-09-27 (Event day)
- Duration: 32 weeks
- Training days per week: 5 (Monday, Tuesday, Thursday, Saturday, Sunday)
- Rest days: Wednesday, Friday

TRAINING PHILOSOPHY:
1. Follow 80/20 rule: 80% easy (Zone 1-2), 20% hard (Zone 4-5)
2. Progressive overload: Increase weekly volume by ~10% every 3 weeks
3. Periodization: Base (Weeks 1-12), Build (Weeks 13-24), Peak (Weeks 25-30), Taper (Weeks 31-32)
4. Recovery weeks: Every 4th week reduce volume by 30%
5. Long run progression: Start at 16 km, peak at 32-35 km
6. Include variety: Easy runs, tempo runs, interval workouts, long runs

WORKOUT TYPES TO INCLUDE:
- Easy runs (Zone 2): Majority of workouts
- Tempo runs (Zone 3-4): Once per week in build phase
- Interval workouts (Zone 4-5): Once per week in build phase
- Long runs (Zone 1-2): Once per week, progressive distance
- Recovery runs (Zone 1): Active recovery days

STRUCTURED WORKOUT EXAMPLE:
For interval workouts, include:
- Warmup: 10-15 min easy
- Main set: 6x1000m @ threshold pace with 2 min recovery
- Cooldown: 10 min easy

OUTPUT FORMAT:
Return ONLY a valid JSON object matching this exact schema:

{JSON_SCHEMA_HERE}

CRITICAL INSTRUCTIONS:
- Return ONLY valid JSON, no markdown, no explanations
- All dates must be YYYY-MM-DD format
- All numeric values must be numbers, not strings
- Include "structuredSteps" for tempo and interval workouts
- Set realistic TSS values based on duration and intensity
- Distribute workouts across specified training days only
- End date must match target event date exactly
- Start date must be 2026-01-13

Generate the complete 32-week training plan now.
```

---

## Success Metrics

**Feature Adoption**:
- % of users who try AI plan generation
- % of generated plans that get imported
- Average time from prompt generation to import

**Quality Metrics**:
- % of imported plans with validation errors
- % of users who complete plan after import
- User feedback/ratings on AI plans

**Technical Metrics**:
- Prompt generation time < 2 seconds
- Import validation time < 1 second
- Zero security incidents from file uploads

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM returns invalid JSON | High | Robust validation, clear error messages, examples |
| LLM creates unrealistic plans | Medium | Include constraints in prompt, allow user review |
| Users don't understand workflow | Medium | Clear instructions, video tutorial |
| File upload security | High | Size limits, MIME validation, safe parsing |
| Large plans slow down import | Low | Process in background, show progress |

---

## Future Enhancements

1. **Chat Interface** (Phase 5)
   - Multi-turn conversation with AI
   - Refine plan based on feedback
   - Adjust specific weeks/workouts

2. **Plan Comparison** (Phase 5)
   - Generate multiple plans
   - Compare side-by-side
   - Merge best elements

3. **AI Coach Assistant** (Phase 6)
   - Weekly plan adjustments based on progress
   - Fatigue detection and recovery recommendations
   - Performance predictions

4. **Mobile App** (Phase 7)
   - Generate prompts on mobile
   - Import plans via camera (OCR)

---

## Dependencies

**Backend**:
- `jsonschema` - JSON validation
- `lxml` - XML parsing (if supporting XML)
- `pydantic` - Schema definitions

**Frontend**:
- No new dependencies (use existing Material-UI)

**External**:
- None (user's own ChatGPT/Claude account)

---

## Timeline Estimate

- **Phase 1 (Backend)**: 3-4 hours
- **Phase 2 (Frontend)**: 5-6 hours
- **Phase 3 (Testing)**: 2 hours
- **Total**: 10-12 hours development time

**Recommended Approach**: Implement Phase 1 & 2 first (minimum viable feature), then iterate based on user feedback.

---

## Conclusion

This feature transforms Kinesis from a training log into an intelligent training assistant by leveraging the power of external LLMs without the complexity and cost of direct API integration. Users maintain full control over their data while benefiting from AI-powered planning.

The phased approach allows for quick MVP delivery while leaving room for future enhancements based on user feedback and adoption metrics.
