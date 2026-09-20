# Garmin Connect Integration

> **📍 You are here:** [Home](../Home.md) > API Integrations > Garmin Overview

For complete Garmin integration documentation, see:
- [GARMIN_WORKOUT_SYNC_IMPLEMENTATION.md](../../backend/GARMIN_WORKOUT_SYNC_IMPLEMENTATION.md)
- [GARMIN_TRAINING_API.md](../../backend/GARMIN_TRAINING_API.md)

## Features

✅ **OAuth Authentication** - Secure login with Garmin Connect  
✅ **Activity Sync** - Automatic import of completed activities  
✅ **Workout Upload** - Upload structured workouts to Garmin library  
✅ **Calendar Scheduling** - Schedule workouts to your Garmin calendar  
✅ **FIT File Download** - Download original activity files  

## How It Works

### Authentication Flow
1. User clicks "Connect Garmin Account"
2. OAuth flow redirects to Garmin login
3. User authorizes app access
4. OAuth tokens stored securely (encrypted)
5. Tokens used for all subsequent API calls

### Activity Sync
- **Frequency**: Every 6 hours (background job)
- **Data**: GPS tracks, heart rate, power, cadence, pace, elevation
- **Storage**: PostgreSQL with TimescaleDB for time-series optimization
- **Processing**: Automatic TSS calculation, zone analysis

### Workout Upload
1. Create structured workout in Kinesis
2. Convert to Garmin JSON format
3. Upload to Garmin workout library
4. Schedule to calendar (optional)

## Setup Guide

See: [Garmin-Authentication.md](Garmin-Authentication.md)

## Troubleshooting

See: [Garmin Authentication Troubleshooting](Garmin-Authentication.md#troubleshooting)

## Technical Details

See: [GARMIN_WORKOUT_SYNC_IMPLEMENTATION.md](../../backend/GARMIN_WORKOUT_SYNC_IMPLEMENTATION.md)

---

[← Back to API Integrations](../Home.md#-api-integrations) | [Home](../Home.md)
