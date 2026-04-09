import requests
from urllib.parse import urljoin

base = 'http://127.0.0.1:5000'
with requests.Session() as s:
    login_data = {'email': 'deliveryuser@gmail.com', 'password': 'password123'}
    r = s.post(urljoin(base, '/login'), data=login_data, allow_redirects=True)
    print('login status', r.status_code)
    print('login url', r.url)
    print('login body snippet', r.text[:200])
    r2 = s.get(urljoin(base, '/dashboard'))
    print('dashboard status', r2.status_code)
    print('dashboard url', r2.url)
    r3 = s.post(urljoin(base, '/api/update-location'), json={'lat': 28.7041, 'lng': 77.1025})
    print('update status', r3.status_code)
    print('update headers', r3.headers.get('Content-Type'))
    print('update body', r3.text)
