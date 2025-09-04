const express = require('express');
const admin = require('firebase-admin');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize Firebase Admin SDK
const serviceAccount = require('./serviceAccountKey.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://<YOUR-FIREBASE-PROJECT-ID>.firebaseio.com',
});

app.use(bodyParser.json());

// REST endpoint to add a player to a room
app.post('/rooms/:roomId/players', async (req, res) => {
    const { roomId } = req.params;
    const playerData = req.body;

    try {
        const roomRef = admin.database().ref(`rooms/${roomId}/players`);
        await roomRef.push(playerData);
        res.status(201).send('Player added');
    } catch (error) {
        res.status(500).send('Error adding player: ' + error.message);
    }
});

// REST endpoint to get players in a room
app.get('/rooms/:roomId/players', async (req, res) => {
    const { roomId } = req.params;

    try {
        const roomRef = admin.database().ref(`rooms/${roomId}/players`);
        const snapshot = await roomRef.once('value');
        const players = snapshot.val() || {};
        res.status(200).json(players);
    } catch (error) {
        res.status(500).send('Error retrieving players: ' + error.message);
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
