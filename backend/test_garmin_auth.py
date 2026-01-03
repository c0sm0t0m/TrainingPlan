#!/usr/bin/env python3
"""
Test Garmin authentication with real credentials.
This script tests the actual Garmin Connect authentication flow.

Usage:
    python test_garmin_auth.py
    
Credentials are loaded from environment variables or can be set directly.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.services.garmin_service import garmin_service

# Credentials
GARMIN_EMAIL = os.getenv('GARMIN_EMAIL', 'th.boettger@web.de')
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD', '2025Dpige.2025')


async def test_authentication():
    """Test Garmin authentication."""
    print("=" * 60)
    print("Garmin Authentication Test")
    print("=" * 60)
    print(f"\nEmail: {GARMIN_EMAIL}")
    print("Password: {'*' * len(GARMIN_PASSWORD)}")
    print("\nAttempting authentication...")
    print("-" * 60)
    
    try:
        result = await garmin_service.authenticate(GARMIN_EMAIL, GARMIN_PASSWORD)
        
        print("\n✓ Authentication successful!")
        print("\nReceived tokens:")
        print(f"  - OAuth1 Token: {result['oauth1_token'][:50]}...")
        print(f"  - OAuth2 Token: {result['oauth2_token'][:50]}...")
        print(f"  - Email: {result['email']}")
        
        return True
        
    except ValueError as e:
        print(f"\n✗ Authentication failed!")
        print(f"Error: {e}")
        
        # Provide helpful debugging info
        if 'ssl' in str(e).lower() or 'certificate' in str(e).lower():
            print("\n⚠ SSL/Certificate Error Detected")
            print("The service should have tried 3 different SSL configurations.")
            print("This suggests a network or certificate issue.")
        elif 'credentials' in str(e).lower() or 'password' in str(e).lower():
            print("\n⚠ Credential Error")
            print("Please verify your Garmin email and password are correct.")
        elif 'mfa' in str(e).lower() or '2fa' in str(e).lower():
            print("\n⚠ MFA/2FA may be enabled")
            print("Garmin may require multi-factor authentication.")
        
        return False
        
    except Exception as e:
        print(f"\n✗ Unexpected error!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {e}")
        return False


async def test_connection(oauth1_token: str, oauth2_token: str):
    """Test if the connection is still valid."""
    print("\n" + "=" * 60)
    print("Testing Connection")
    print("=" * 60)
    
    try:
        is_valid = await garmin_service.test_connection(oauth1_token, oauth2_token)
        
        if is_valid:
            print("✓ Connection is valid!")
        else:
            print("✗ Connection is not valid")
        
        return is_valid
        
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False


async def main():
    """Main test function."""
    # Test authentication
    auth_result = await test_authentication()
    
    if not auth_result:
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        print("✗ Authentication failed")
        print("\nTroubleshooting steps:")
        print("1. Verify credentials are correct")
        print("2. Check if 2FA/MFA is enabled on Garmin account")
        print("3. Try logging in via browser at connect.garmin.com")
        print("4. Check backend logs for detailed error messages")
        return 1
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("✓ All tests passed!")
    print("\nGarmin authentication is working correctly.")
    print("The issue in the UI may be related to:")
    print("  - CORS configuration")
    print("  - Frontend error handling")
    print("  - Token storage/retrieval")
    
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
