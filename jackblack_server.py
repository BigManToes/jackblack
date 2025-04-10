from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Middleware to handle CORS for the frontend (replace with your actual frontend URL if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify your frontend URL here (e.g., "https://jackblack-gamma.vercel.app")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active players and their WebSocket connections
players = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Receive player name
    player_name = await websocket.receive_text()
    players.append({"name": player_name, "websocket": websocket})
    
    try:
        while True:
            message = await websocket.receive_text()
            if message == "start_game":
                # Start the game when the 'start_game' message is received
                await start_game()
    except WebSocketDisconnect:
        # Remove player from the list when they disconnect
        players.remove({"name": player_name, "websocket": websocket})

async def start_game():
    # Notify all players that the game is starting
    for player in players:
        await player["websocket"].send_text("The game is starting!")
    # Your game logic can go here (e.g., dealing cards, game rules)
    print("Game has started!")
