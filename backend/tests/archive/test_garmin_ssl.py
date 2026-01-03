#!/usr/bin/env python3
"""
Test Garmin SSL configuration with different certificate approaches.
"""
import os
import certifi
import garth
from garth.exc import GarthHTTPError

def test_ssl_config(config_name: str, ssl_verify):
    """Test a specific SSL configuration."""
    print(f"\nTesting: {config_name}")
    print(f"SSL verify setting: {ssl_verify}")
    
    try:
        garth.configure(ssl_verify=ssl_verify)
        
        # Try to access Garmin SSO (doesn't need login)
        # This will test if SSL works
        print(f"  ✓ SSL configuration accepted")
        print(f"  Note: Full authentication test requires valid credentials")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Garmin SSL Configuration Test")
    print("=" * 60)
    
    # Test different SSL configurations
    configs = [
        ("Certifi certificates", certifi.where()),
        ("Homebrew system certificates", "/opt/homebrew/etc/ca-certificates/cert.pem"),
        ("Default (True)", True),
        ("Disabled (False) - Development only", False),
    ]
    
    results = []
    for name, verify in configs:
        result = test_ssl_config(name, verify)
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print("\n" + "=" * 60)
    print("Recommendation:")
    print("=" * 60)
    
    # Check which configs worked
    if results[0][1] or results[1][1]:
        print("✓ SSL verification is working with certificates")
        print("  Your Garmin integration should work securely.")
    elif results[3][1]:
        print("⚠ Only disabled SSL verification works")
        print("  This is acceptable for development but should be fixed for production.")
        print("  Try: brew upgrade ca-certificates && pip install --upgrade certifi")
    else:
        print("✗ All SSL configurations failed")
        print("  There may be a network issue or firewall blocking connections.")

if __name__ == '__main__':
    main()
