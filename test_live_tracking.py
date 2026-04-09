"""
Test script for live delivery tracking functionality.
Run this to test the location tracking APIs.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_location_tracking():
    """Test the location tracking functionality"""

    print("🧪 Testing Live Delivery Tracking System")
    print("=" * 50)

    # Test data - you'll need to replace these with actual values
    test_lat = 28.7041  # Delhi coordinates
    test_lng = 77.1025

    # Note: These tests require authentication. In a real scenario,
    # you'd need to login first and use the session cookies.

    print("\n1. Testing location update API...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/update-location",
            json={"lat": test_lat, "lng": test_lng},
            # Note: In real usage, include authentication cookies
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n2. Testing stop location sharing API...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/stop-location-sharing",
            # Note: In real usage, include authentication cookies
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print("Response:", response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n3. Testing get delivery location API...")
    try:
        # Replace 1 with an actual order ID
        response = requests.get(f"{BASE_URL}/api/get-delivery-location/1")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n4. Testing ETA calculation API...")
    try:
        # Replace 1 with an actual order ID
        response = requests.get(f"{BASE_URL}/api/calculate-eta/1")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n✅ Testing completed!")
    print("\n📝 Notes:")
    print("- These tests require authentication (login as delivery person)")
    print("- Replace order IDs with actual values from your database")
    print("- Test with a real browser for full functionality")
    print("- Check browser console for JavaScript errors")

if __name__ == "__main__":
    test_location_tracking()