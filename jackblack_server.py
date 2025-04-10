import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketState  # <-- This is the missing import
import uvicorn

app = FastAPI()

players = []
game_started = False

# This is just an example function for handling a game round
async def play_blackjack(player_name: str, websocket: WebSocket):
    # Example of playing a round of blackjack
    print(f"Starting Blackjack game for {player_name}...")
    # Add game logic here
    await websocket.send_text(f"Game started for {player_name}!")
    # Simulate game logic and send messages during game play
    await websocket.send_text(f"Good luck, {player_name}!")

# Function to check if all players have voted to start
async def check_votes():
    global game_started
    if all(player['voted'] for player in players):
        game_started = True
        await start_game()

# Function to start the game
async def start_game():
    global game_started
    if game_started:
        for player in players:
            if player["websocket"].client_state == WebSocketState.CONNECTED:
                await player["websocket"].send_text("The game is starting!")
                await play_blackjack(player["name"], player["websocket"])
            else:
                print(f"Player {player['name']} is no longer connected.")
    else:
        print("Game has not started yet!")

# WebSocket endpoint for connecting players
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    player_name = await websocket.receive_text()  # Receive the player name
    player = {"name": player_name, "websocket": websocket, "voted": False}

    players.append(player)
    
    try:
        # Loop to receive votes or other messages from players
        while True:
            data = await websocket.receive_text()
            
            if data == "vote_start":  # Example vote to start the game
                player["voted"] = True
                await websocket.send_text(f"{player_name} voted to start!")
                await check_votes()

    except WebSocketDisconnect:
        print(f"Player {player_name} disconnected.")
        players.remove(player)  # Remove disconnected player

    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await websocket.close()

# Simple HTML page to connect to WebSocket (for testing purposes)
@app.get("/")
async def get():
    html_content = """
    <html>
        <body>
            <h1>Welcome to Blackjack!</h1>
            <input id="username" type="text" placeholder="Enter your name">
            <button onclick="connect()">Connect</button>
            <script>
                let ws;
                function connect() {
                    const name = document.getElementById("username").value;
                    ws = new WebSocket("ws://127.0.0.1:8000/ws");
                    ws.onopen = () => {
                        console.log("Connected to the server");
                        ws.send(name);  // Send player name to server
                    };
                    ws.onmessage = (message) => {
                        console.log("Message from server:", message.data);
                    };
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
