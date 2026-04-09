import requests
from urllib.parse import urljoin

base_url = 'http://127.0.0.1:5000'
session = requests.Session()

print('Testing login with customer@test.com...')
login_response = session.post(urljoin(base_url, '/login'), data={
    'email': 'customer@test.com',
    'password': 'password123'
}, allow_redirects=False)

print(f'Status: {login_response.status_code}')
print(f'Location header: {login_response.headers.get("Location")}')
print(f'Content length: {len(login_response.text)}')

if 'Invalid' in login_response.text or 'incorrect' in login_response.text.lower():
    print('Found error message in response')
    # Look for flash messages
    if 'alert-danger' in login_response.text:
        print('Found danger alert - likely authentication failed')
    else:
        print('No danger alert found')

# Try to access dashboard with the session
dashboard_response = session.get(urljoin(base_url, '/dashboard'), allow_redirects=False)
print(f'Dashboard status: {dashboard_response.status_code}')
print(f'Dashboard location: {dashboard_response.headers.get("Location")}')