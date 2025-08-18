import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-app.js";
import { getDatabase } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-database.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyDxjT3GJNt7ZwvpmJEYCDR39uX96wPwCJ4",
  authDomain: "jackblack-95dbd.firebaseapp.com",
  databaseURL: "https://jackblack-95dbd-default-rtdb.firebaseio.com",
  projectId: "jackblack-95dbd",
  storageBucket: "jackblack-95dbd.firebasestorage.app",
  messagingSenderId: "321007761489",
  appId: "1:321007761489:web:e62d122547783bd86ea070",
  measurementId: "G-08KQXFNB5X"
};

export const app = initializeApp(firebaseConfig);
export const db = getDatabase(app);
export const auth = getAuth(app);
