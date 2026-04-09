import requests
from urllib.parse import urljoin

base_url = 'http://127.0.0.1:5000'
session = requests.Session()

print('Login...')
login_response = session.post(urljoin(base_url, '/login'), data={
    'email': 'customerdemo@gmail.com',
    'password': 'password123'
}, allow_redirects=False)

print(f'Login status: {login_response.status_code}')
print(f'Login location: {login_response.headers.get("Location")}')

# Check dashboard access
dashboard_response = session.get(urljoin(base_url, '/dashboard'), allow_redirects=False)
print(f'Dashboard status: {dashboard_response.status_code}')
print(f'Dashboard location: {dashboard_response.headers.get("Location")}')

# Check if we can access the API
api_response = session.post(urljoin(base_url, '/api/create-razorpay-order'), allow_redirects=False)
print(f'API status: {api_response.status_code}')
print(f'API location: {api_response.headers.get("Location")}')
print(f'API response: {api_response.text[:200]}...')