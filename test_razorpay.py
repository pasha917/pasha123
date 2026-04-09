import requests
from urllib.parse import urljoin

# Test Razorpay integration
def test_razorpay_integration():
    base_url = 'http://127.0.0.1:5000'

    # First, login as customer
    session = requests.Session()
    login_response = session.post(urljoin(base_url, '/login'), data={
        'email': 'customer@gmail.com',
        'password': 'password123'
    })

    if login_response.status_code != 200:
        print("Login failed")
        return

    print("Login successful")

    # Test create Razorpay order (this will fail without pending order, but tests the endpoint)
    order_response = session.post(urljoin(base_url, '/api/create-razorpay-order'))
    print(f"Create order response: {order_response.status_code}")
    print(f"Response: {order_response.text}")

if __name__ == "__main__":
    test_razorpay_integration()