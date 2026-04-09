// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.2/firebase-app.js";
import { getAuth, connectAuthEmulator } from "https://www.gstatic.com/firebasejs/10.7.2/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCYPvrlCFMxlkLpp8yZYrxBXAMMDmiOIms",
  authDomain: "pasha-d3ba5.firebaseapp.com",
  databaseURL: "https://pasha-d3ba5-default-rtdb.firebaseio.com",
  projectId: "pasha-d3ba5",
  storageBucket: "pasha-d3ba5.firebasestorage.app",
  messagingSenderId: "887761353241",
  appId: "1:887761353241:web:386edb4753210ccbecc888"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
const auth = getAuth(app);

// Optional: Connect to local emulator for development (comment out for production)
// connectAuthEmulator(auth, "http://localhost:9099", { disableWarnings: true });

// Export for use in other scripts
export { app, auth };
