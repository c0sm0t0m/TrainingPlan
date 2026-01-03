#!/usr/bin/env python3
"""
Quick diagnostic for Garmin sync issues
"""
import sys
import os

print("🔍 Garmin Sync Diagnostic")
print("=" * 50)
print()

# Check if backend files have syntax errors
print("1. Checking Python syntax...")
try:
    import py_compile
    py_compile.compile('backend/src/api/routes/garmin.py', doraise=True)
    print("   ✅ garmin.py syntax OK")
except Exception as e:
    print(f"   ❌ Syntax error: {e}")
    sys.exit(1)

# Check if model is correct
try:
    sys.path.insert(0, 'backend')
    from src.models.garmin_activity import GarminActivity
    print("   ✅ GarminActivity model loads OK")
    
    # Check for power fields
    if hasattr(GarminActivity, 'average_power_watts'):
        print("   ✅ Power fields present in model")
    else:
        print("   ⚠️  Power fields not in model (migration may not be applied)")
        
except Exception as e:
    print(f"   ❌ Model error: {e}")
    sys.exit(1)

print()
print("2. Common issues to check:")
print("   - Is backend running? (./status.sh)")
print("   - Is Garmin connected? (Check Settings page)")
print("   - Did database migration run? (Check alembic current)")
print()
print("3. To test sync manually:")
print("   ./test-sync.sh")
print()
