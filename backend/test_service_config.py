#!/usr/bin/env python3
"""
Quick test to verify the Garmin service SSL configuration works correctly.
This tests that the service can be imported and SSL is configured properly.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

def test_service_import():
    """Test that the service can be imported without errors."""
    print("Testing service import...")
    try:
        from src.services.garmin_service import garmin_service
        print("✓ GarminService imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import: {e}")
        return False

def test_ssl_environment():
    """Test that SSL environment variables are set."""
    print("\nTesting SSL environment configuration...")
    
    ssl_vars = ['SSL_CERT_FILE', 'REQUESTS_CA_BUNDLE']
    all_set = True
    
    for var in ssl_vars:
        if var in os.environ:
            value = os.environ[var]
            exists = os.path.exists(value) if value else False
            status = "✓" if exists else "⚠"
            print(f"  {status} {var} = {value}")
            if not exists:
                print(f"      Warning: File does not exist")
        else:
            print(f"  ✗ {var} not set")
            all_set = False
    
    return all_set

def test_garth_configuration():
    """Test that garth can be configured with different SSL settings."""
    print("\nTesting garth SSL configuration...")
    
    try:
        import garth
        import certifi
        
        # Test configuration methods
        tests = [
            ("certifi", certifi.where()),
            ("system", "/opt/homebrew/etc/ca-certificates/cert.pem"),
            ("disabled", False),
        ]
        
        for name, ssl_verify in tests:
            try:
                garth.configure(ssl_verify=ssl_verify)
                print(f"  ✓ {name}: Can configure with ssl_verify={ssl_verify}")
            except Exception as e:
                print(f"  ✗ {name}: Failed - {e}")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Garmin Service Configuration Test")
    print("=" * 60)
    print()
    
    results = []
    results.append(("Service Import", test_service_import()))
    results.append(("SSL Environment", test_ssl_environment()))
    results.append(("Garth Configuration", test_garth_configuration()))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! Garmin authentication should work.")
        print("  The service will try certifi, then system certs, then disabled SSL.")
        return 0
    else:
        print("✗ Some tests failed. Review the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
