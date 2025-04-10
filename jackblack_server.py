import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
import json
import random

app = FastAPI()

# Store player data (username, connection, votes, etc.)
players = []
game_started = False
votes = {}

@app.get("/")
async def get_html():
    return HTMLResponse(content=open("index.html").read(), status_code=200)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global game_started
    player_id = None
    player_name = None
    player_vote = False
    await websocket.accept()

    try:
        # Wait for player to send their username
        while True:
            data = await websocket.receive_text()
            if player_name is None and len(players) < 4:
                # Lock in the player's username
                if data not in [p['name'] for p in players]:
                    player_name = data
                    player_id = len(players) + 1
                    players.append({"id": player_id, "name": player_name, "websocket": websocket})
                    await websocket.send_text(f"Welcome Player {player_id}! Your username is {player_name}.")
                    await update_players()
                    break
                else:
                    await websocket.send_text("Username already taken, please choose another one.")

        # Handle the game state and player communication
        while True:
            if game_started:
                await play_blackjack(player_name, websocket)

            # Receive a vote to start the game
            data = await websocket.receive_text()
            if data == "vote_start":
                votes[player_name] = True
                await websocket.send_text("Your vote has been registered.")
                await check_votes()

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        if player_name:
            # Remove player upon disconnect
            players[:] = [p for p in players if p['name'] != player_name]
            votes.pop(player_name, None)
            await update_players()
            print(f"Player {player_name} disconnected.")
            await check_votes()

# Function to update the list of players to all connected clients
async def update_players():
    global game_started
    player_names = [player["name"] for player in players]
    for player in players:
        await player["websocket"].send_text(json.dumps({"players": player_names, "votes": votes}))

    if len(players) >= 2 and len(votes) >= 2 and not game_started:
        await start_game()

# Function to handle the vote system
async def check_votes():
    global game_started
    if len(votes) >= 2:
        if all(vote == True for vote in votes.values()):
            await start_game()

# Start the game when the condition is met
async def start_game():
    global game_started
    game_started = True
    for player in players:
        await player["websocket"].send_text("The game is starting!")

    # Handle Blackjack gameplay here after game starts
    await play_blackjack()

# Blackjack logic (simplified)
async def play_blackjack(player_name, websocket):
    # Initial game setup
    deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
    random.shuffle(deck)
    
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    
    # Send initial hands
    await websocket.send_text(f"Your hand: {player_hand}, Dealer's hand: {dealer_hand[0]}")

    # Player's turn
    while sum(player_hand) < 21:
        # Wait for the player to choose "hit" or "stand"
        action = await websocket.receive_text()
        if action == "hit":
            player_hand.append(deck.pop())
            await websocket.send_text(f"Your hand: {player_hand}")
        elif action == "stand":
            break

    # Dealer's turn
    while sum(dealer_hand) < 17:
        dealer_hand.append(deck.pop())

    # Game result
    player_total = sum(player_hand)
    dealer_total = sum(dealer_hand)

    if player_total > 21:
        result = "You busted! Dealer wins!"
    elif dealer_total > 21:
        result = "Dealer busted! You win!"
    elif player_total > dealer_total:
        result = "You win!"
    elif player_total < dealer_total:
        result = "Dealer wins!"
    else:
        result = "It's a tie!"

    await websocket.send_text(f"Game Over! {result}")
    game_started = False
    await update_players()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

