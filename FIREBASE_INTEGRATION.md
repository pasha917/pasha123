# Firebase Integration Guide

## Overview
Your Rapid Delivery application now has Firebase Authentication integrated. The Firebase configuration files are located in `static/js/`:

- **firebase-config.js** - Main Firebase initialization (automatically loaded on all pages)
- **firebase-auth-helper.js** - Helper functions for authentication

## Setup

### 1. Firebase Configuration (Already Done ✓)
The `firebase-config.js` file contains your Firebase project credentials and is automatically loaded on all pages via `base.html`.

### 2. Using Firebase Authentication

#### Example: User Registration
```javascript
import { registerUser } from '/static/js/firebase-auth-helper.js';

// In your registration handler
async function handleFirebaseRegister(email, password, name) {
  const result = await registerUser(email, password, name);
  
  if (result.success) {
    console.log("Firebase user created:", result.user.uid);
    // Then submit to Flask backend to create UserModel
  } else {
    console.error("Registration failed:", result.error);
  }
}
```

#### Example: User Login
```javascript
import { loginUser } from '/static/js/firebase-auth-helper.js';

async function handleFirebaseLogin(email, password) {
  const result = await loginUser(email, password);
  
  if (result.success) {
    console.log("Firebase user logged in:", result.user.uid);
    // You can use Firebase ID token for backend verification
    const idToken = await result.user.getIdToken();
    // Send idToken to Flask for verification
  } else {
    console.error("Login failed:", result.error);
  }
}
```

#### Example: Monitor Auth State
```javascript
import { onAuthStateChange } from '/static/js/firebase-auth-helper.js';

// Run when page loads
onAuthStateChange((user) => {
  if (user) {
    console.log("User is logged in:", user.email);
    // Update UI to show logged-in state
  } else {
    console.log("User is logged out");
    // Update UI to show logged-out state
  }
});
```

#### Example: Password Reset
```javascript
import { sendPasswordReset } from '/static/js/firebase-auth-helper.js';

async function handlePasswordReset(email) {
  const result = await sendPasswordReset(email);
  
  if (result.success) {
    console.log(result.message);
  } else {
    console.error(result.error);
  }
}
```

## Integration with Flask Backend

Your Flask app currently uses its own authentication system. You have two options:

### Option 1: Replace Flask Auth with Firebase (Recommended for new features)
1. Use `firebase-auth-helper.js` functions for client-side auth
2. In Python, verify Firebase ID tokens using Flask-Firebase or similar
3. Gradually migrate existing user system if needed

### Option 2: Keep Both Systems Running
1. Use Firebase for supplementary features only
2. Keep your existing Flask SQLAlchemy authentication
3. Link Firebase users with Flask User model using `firebase_uid` field

## Flask-Firebase Setup (if using Option 1)

Install the package:
```bash
pip install firebase-admin
```

Initialize in your `app.py`:
```python
import firebase_admin
from firebase_admin import credentials

# Download service account key from Firebase Console
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred)
```

Verify Firebase ID tokens:
```python
from firebase_admin import auth

@app.route('/verify-firebase-token', methods=['POST'])
def verify_token():
    token = request.json.get('idToken')
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        return jsonify({'success': True, 'uid': uid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```

## Important Notes

1. **Firebase is client-side**: Authentication happens in the browser
2. **Security**: Never expose your private Firebase keys
3. **Existing System**: Your Flask OTP and password-based auth still works
4. **Future Enhancement**: You can add other Firebase services (Firestore, Storage, etc.)

## File Structure
```
templates/
  base.html (✓ Firebase config auto-loaded)
static/js/
  firebase-config.js (✓ Configuration)
  firebase-auth-helper.js (✓ Helper functions)
  tracking.js (Your existing code)
```

## Testing

Open browser DevTools (F12) and test:
```javascript
import { getCurrentUser } from '/static/js/firebase-auth-helper.js';

getCurrentUser().then(user => {
  console.log("Current user:", user);
});
```

## Support
For more info: https://firebase.google.com/docs/auth/web/start
