// Firebase Authentication Helper Functions
// Import auth from firebase-config.js where needed using: 
// import { auth } from '/static/js/firebase-config.js';

import { 
  createUserWithEmailAndPassword, 
  signInWithEmailAndPassword, 
  signOut, 
  onAuthStateChanged,
  updateProfile,
  sendPasswordResetEmail
} from "https://www.gstatic.com/firebasejs/10.7.2/firebase-auth.js";

/**
 * Register a new user with Firebase
 * @param {string} email - User's email
 * @param {string} password - User's password
 * @param {string} displayName - User's display name
 * @returns {Promise<Object>} User object or error
 */
export async function registerUser(email, password, displayName) {
  try {
    const { auth } = await import('/static/js/firebase-config.js');
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    
    if (displayName) {
      await updateProfile(userCredential.user, { displayName: displayName });
    }
    
    console.log("User registered successfully:", userCredential.user);
    return { success: true, user: userCredential.user };
  } catch (error) {
    console.error("Registration error:", error);
    return { success: false, error: error.message };
  }
}

/**
 * Sign in a user with Firebase
 * @param {string} email - User's email
 * @param {string} password - User's password
 * @returns {Promise<Object>} User object or error
 */
export async function loginUser(email, password) {
  try {
    const { auth } = await import('/static/js/firebase-config.js');
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    console.log("User logged in successfully:", userCredential.user);
    return { success: true, user: userCredential.user };
  } catch (error) {
    console.error("Login error:", error);
    return { success: false, error: error.message };
  }
}

/**
 * Sign out the current user
 * @returns {Promise<Object>} Success or error
 */
export async function logoutUser() {
  try {
    const { auth } = await import('/static/js/firebase-config.js');
    await signOut(auth);
    console.log("User logged out successfully");
    return { success: true };
  } catch (error) {
    console.error("Logout error:", error);
    return { success: false, error: error.message };
  }
}

/**
 * Monitor authentication state changes
 * @param {Function} callback - Function to call when auth state changes
 */
export function onAuthStateChange(callback) {
  const initFirebase = async () => {
    const { auth } = await import('/static/js/firebase-config.js');
    onAuthStateChanged(auth, (user) => {
      callback(user);
    });
  };
  
  initFirebase();
}

/**
 * Send password reset email
 * @param {string} email - User's email
 * @returns {Promise<Object>} Success or error
 */
export async function sendPasswordReset(email) {
  try {
    const { auth } = await import('/static/js/firebase-config.js');
    await sendPasswordResetEmail(auth, email);
    console.log("Password reset email sent to:", email);
    return { success: true, message: "Check your email for password reset link" };
  } catch (error) {
    console.error("Password reset error:", error);
    return { success: false, error: error.message };
  }
}

/**
 * Get current authenticated user
 * @returns {Promise<Object>} Current user or null
 */
export async function getCurrentUser() {
  const { auth } = await import('/static/js/firebase-config.js');
  return auth.currentUser;
}
