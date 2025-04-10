from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketState
import uvicorn

app = FastAPI()

players = []
game_started = False

# Function to play the blackjack game (can be expanded later)
async def play_blackjack(player_name: str, websocket: WebSocket):
    print(f"Starting Blackjack game for {player_name}...")
    await websocket.send_text(f"Game started for {player_name}!")

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
        <head>
            <title>Blackjack Game</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #2c3e50;
                    color: white;
                    text-align: center;
                    padding: 50px;
                }
                h1 {
                    font-size: 2.5em;
                    margin-bottom: 20px;
                }
                input[type="text"] {
                    padding: 10px;
                    font-size: 1em;
                    border: none;
                    border-radius: 5px;
                    width: 250px;
                    margin-bottom: 20px;
                }
                button {
                    padding: 10px 20px;
                    font-size: 1.2em;
                    border: none;
                    border-radius: 5px;
                    background-color: #27ae60;
                    color: white;
                    cursor: pointer;
                    margin: 10px;
                }
                button:hover {
                    background-color: #2ecc71;
                }
                #gameMessage {
                    margin-top: 20px;
                    font-size: 1.5em;
                    color: #f39c12;
                }
            </style>
        </head>
        <body>
            <h1>Welcome to Blackjack!</h1>
            <input id="username" type="text" placeholder="Enter your name">
            <button onclick="connect()">Connect</button>
            <button id="voteButton" style="display: none;" onclick="voteToStart()">Vote to Start Game</button>
            <div id="gameMessage"></div>
            <script>
                let ws;
                let playerName = "";
                
                function connect() {
                    playerName = document.getElementById("username").value;
                    if (!playerName) {
                        alert("Please enter a name.");
                        return;
                    }

                    ws = new WebSocket("ws://127.0.0.1:8000/ws"); // Use this for local testing
                    // Update WebSocket URL if hosted publicly
                    // ws = new WebSocket("ws://YOUR_PUBLIC_IP:8000/ws");

                    ws.onopen = () => {
                        console.log("Connected to the server");
                        ws.send(playerName);  // Send player name to server when connected
                        document.getElementById("voteButton").style.display = "inline-block"; // Show vote button
                    };

                    ws.onmessage = (message) => {
                        console.log("Message from server:", message.data);
                        document.getElementById("gameMessage").innerText = message.data;
                    };
                }

                function voteToStart() {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send("vote_start");  // Send vote to start the game
                        console.log("Voted to start the game.");
                    }
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
