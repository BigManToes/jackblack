import express from 'express';
import cors from 'cors';
import admin from 'firebase-admin';
import fetch from 'node-fetch';

const app = express();
app.use(cors());
app.use(express.json());

// Initialize Firebase Admin with environment variables
admin.initializeApp({
  credential: admin.credential.cert({
    projectId: process.env.FIREBASE_PROJECT_ID,
    clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
    privateKey: process.env.FIREBASE_PRIVATE_KEY.replace(/\\n/g, '\n'),
  }),
  databaseURL: process.env.FIREBASE_DATABASE_URL
});

// Endpoint to exchange Google ID token for Firebase custom token
app.post('/signIn', async (req, res) => {
  try {
    const { idToken } = req.body;
    if (!idToken) return res.status(400).json({ error: 'No ID token provided' });

    // Verify Google token
    const googleRes = await fetch(`https://oauth2.googleapis.com/tokeninfo?id_token=${idToken}`);
    const googleUser = await googleRes.json();

    if (!googleUser || googleUser.aud !== process.env.GOOGLE_CLIENT_ID) {
      return res.status(401).json({ error: 'Invalid Google ID token' });
    }

    // Create Firebase custom token
    const customToken = await admin.auth().createCustomToken(googleUser.sub, {
      name: googleUser.name,
      email: googleUser.email
    });

    res.json({ customToken });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Sign-in failed' });
  }
});

