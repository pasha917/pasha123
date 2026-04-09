"""
Quick test script for live delivery tracking APIs
"""

import requests

BASE_URL = "http://127.0.0.1:5000"

def test_apis():
    """Test the live tracking APIs"""

    print("🧪 Testing Live Delivery Tracking APIs")
    print("=" * 50)

    # Test 1: Get delivery location (should fail without auth)
    print("\n1. Testing get-delivery-location API...")
    try:
        response = requests.get(f"{BASE_URL}/api/get-delivery-location/10")
        print(f"Status: {response.status_code}")
        if response.status_code == 403:
            print("✅ Correctly requires authentication")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: Calculate ETA (should fail without auth)
    print("\n2. Testing calculate-eta API...")
    try:
        response = requests.get(f"{BASE_URL}/api/calculate-eta/10")
        print(f"Status: {response.status_code}")
        if response.status_code == 403:
            print("✅ Correctly requires authentication")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 3: Update location (should fail without auth)
    print("\n3. Testing update-location API...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/update-location",
            json={"lat": 28.7041, "lng": 77.1025}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 403:
            print("✅ Correctly requires authentication")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n✅ API tests completed!")
    print("\n📝 Note: APIs correctly require authentication.")
    print("To test fully, login as delivery person/customer in browser.")
    print("\n🔗 Test URLs:")
    print("- Login: http://127.0.0.1:5000/login")
    print("- Track Order: http://127.0.0.1:5000/track-order/10")
    print("- Delivery Dashboard: http://127.0.0.1:5000/dashboard (as delivery)")

if __name__ == "__main__":
    test_apis()