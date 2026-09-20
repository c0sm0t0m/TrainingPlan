#!/usr/bin/env python3
"""
Test Data Helper: AI Training Plan Generator

This script loads test data and can be used to:
1. Programmatically test the AI Training Plan API
2. Generate test prompts
3. Validate the configuration

Usage:
    python test-data/test_ai_plan_config.py
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


def get_next_monday():
    """Calculate the next Monday from today."""
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) if today.weekday() != 0 else 7
    next_monday = today + timedelta(days=days_until_monday)
    return next_monday.strftime('%Y-%m-%d')


def load_test_config():
    """Load test configuration from JSON file."""
    config_path = Path(__file__).parent / 'ai-training-plan-config.json'
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Replace AUTO_NEXT_MONDAY with actual date
    if config.get('startDate') == 'AUTO_NEXT_MONDAY':
        config['startDate'] = get_next_monday()
    
    return config


def print_config(config):
    """Pretty print the configuration."""
    print("=" * 60)
    print("AI TRAINING PLAN TEST CONFIGURATION")
    print("=" * 60)
    print(f"\n📅 Event Details:")
    print(f"   Name:          {config['eventName']}")
    print(f"   Date:          {config['eventDate']}")
    print(f"   Distance:      {config['eventDistance']}")
    print(f"   Goal Time:     {config['goalTime']}")
    
    print(f"\n🏋️  Training Plan:")
    print(f"   Start Date:    {config['startDate']}")
    print(f"   Days/Week:     {config['trainingDaysPerWeek']}")
    print(f"   Preferred Days: {', '.join(config['preferredTrainingDays'])}")
    
    print(f"\n📝 Constraints:")
    notes = config['additionalNotes'].split('\n')
    for note in notes:
        print(f"   • {note}")
    
    print("\n" + "=" * 60 + "\n")


def generate_curl_command(config, base_url="http://localhost:8000"):
    """Generate a curl command to test the API."""
    api_url = f"{base_url}/api/v1/ai-training-plan/generate-prompt"
    
    json_payload = json.dumps(config, indent=2)
    
    curl_cmd = f"""curl -X POST "{api_url}" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
  -d '{json_payload}'"""
    
    return curl_cmd


def generate_python_test_code(config):
    """Generate Python code to test the API."""
    code = f"""
import httpx
import asyncio

async def test_generate_prompt():
    async with httpx.AsyncClient() as client:
        config = {json.dumps(config, indent=8)}
        
        response = await client.post(
            "http://localhost:8000/api/v1/ai-training-plan/generate-prompt",
            json=config,
            headers={{"Authorization": "Bearer YOUR_TOKEN_HERE"}}
        )
        
        print(f"Status: {{response.status_code}}")
        print(f"Response: {{response.json()}}")

asyncio.run(test_generate_prompt())
"""
    return code


def main():
    """Main function."""
    print("\n🧪 Loading test data...\n")
    
    # Load and process config
    config = load_test_config()
    
    # Print configuration
    print_config(config)
    
    # Generate test commands
    print("🔧 Testing Tools:\n")
    
    print("1️⃣  Curl Command:")
    print("-" * 60)
    print(generate_curl_command(config))
    print()
    
    print("\n2️⃣  Python Test Code:")
    print("-" * 60)
    print(generate_python_test_code(config))
    print()
    
    print("\n3️⃣  JavaScript Browser Console:")
    print("-" * 60)
    print("Open browser at http://localhost:5173/ai-training-plan")
    print("Then paste the contents of auto-fill-training-plan.js")
    print()
    
    # Calculate training period
    start_date = datetime.strptime(config['startDate'], '%Y-%m-%d')
    event_date = datetime.strptime(config['eventDate'], '%Y-%m-%d')
    training_weeks = (event_date - start_date).days // 7
    
    print("\n📊 Training Period Analysis:")
    print(f"   Start:  {start_date.strftime('%A, %B %d, %Y')}")
    print(f"   Event:  {event_date.strftime('%A, %B %d, %Y')}")
    print(f"   Weeks:  {training_weeks} weeks")
    print(f"   Days:   {(event_date - start_date).days} days")
    print()
    
    if training_weeks < 12:
        print("   ⚠️  Warning: Less than 12 weeks - short training cycle")
    elif training_weeks > 24:
        print("   ⚠️  Warning: More than 24 weeks - very long training cycle")
    else:
        print("   ✅ Good training duration (12-24 weeks)")
    print()


if __name__ == '__main__':
    main()
