from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import random

app = FastAPI()

# Function to deal cards
def deal_card():
    cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]  # Jack, Queen, King are all 10, Ace is 11
    return random.choice(cards)

# Function to calculate the score
def calculate_score(hand):
    if sum(hand) == 21 and len(hand) == 2:
        return 0  # Blackjack
    if sum(hand) > 21 and 11 in hand:
        hand.remove(11)
        hand.append(1)
    return sum(hand)

# Function to check if the player has lost
def is_busted(hand):
    return sum(hand) > 21

# FastAPI endpoint to serve the game page
@app.get("/")
async def get():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Single Player Blackjack</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #1e1e1e;
                color: white;
                text-align: center;
                padding-top: 50px;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #45a049;
            }
            .game-info {
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
    
    <h1>Welcome to Single-Player Blackjack</h1>
    <p>Press Start to begin playing!</p>
    
    <button onclick="startGame()">Start Game</button>
    <button id="hitButton" style="display:none" onclick="hit()">Hit</button>
    <button id="standButton" style="display:none" onclick="stand()">Stand</button>
    
    <div class="game-info" id="gameInfo"></div>
    <div id="playerHand"></div>
    <div id="dealerHand"></div>
    
    <script>
        let playerHand = [];
        let dealerHand = [];
    
        async function startGame() {
            const response = await fetch('/start_game');
            const data = await response.json();
    
            document.getElementById('gameInfo').innerText = data.message;
            document.getElementById('playerHand').innerText = `Your Hand: ${data.player_hand.join(", ")}`;
            document.getElementById('dealerHand').innerText = `Dealer's Hand: ${data.dealer_hand}`;
    
            document.getElementById('hitButton').style.display = 'inline-block';
            document.getElementById('standButton').style.display = 'inline-block';
        }
    
        async function hit() {
            const response = await fetch('/hit');
            const data = await response.json();
    
            document.getElementById('gameInfo').innerText = data.message;
            document.getElementById('playerHand').innerText = `Your Hand: ${data.player_hand.join(", ")}`;
        }
    
        async function stand() {
            const response = await fetch('/stand');
            const data = await response.json();
    
            document.getElementById('gameInfo').innerText = data.message;
            document.getElementById('playerHand').innerText = `Your Hand: ${data.player_hand.join(", ")}`;
            document.getElementById('dealerHand').innerText = `Dealer's Hand: ${data.dealer_hand.join(", ")}`;
            
            document.getElementById('hitButton').style.display = 'none';
            document.getElementById('standButton').style.display = 'none';
        }
    </script>
    
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/start_game")
async def start_game():
    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]
    
    # Display initial hands
    return {
        "message": "Game Started! You are dealt two cards.",
        "player_hand": player_hand,
        "dealer_hand": dealer_hand[0],  # Show one dealer card
    }

@app.get("/hit")
async def hit():
    # Simulate the player hitting and receiving another card
    player_hand = [deal_card() for _ in range(2)]  # Sample initial hand
    player_hand.append(deal_card())  # Add another card when the player hits
    return {"message": "You hit!", "player_hand": player_hand}

@app.get("/stand")
async def stand():
    # Simulate standing and revealing the dealer's hand
    player_hand = [deal_card() for _ in range(2)]  # Sample initial hand
    dealer_hand = [deal_card(), deal_card()]
    
    while calculate_score(dealer_hand) < 17:
        dealer_hand.append(deal_card())
    
    player_score = calculate_score(player_hand)
    dealer_score = calculate_score(dealer_hand)
    
    if is_busted(player_hand):
        return {"message": "You busted! Dealer wins.", "player_hand": player_hand, "dealer_hand": dealer_hand}
    if is_busted(dealer_hand):
        return {"message": "Dealer busted! You win!", "player_hand": player_hand, "dealer_hand": dealer_hand}
    if player_score > dealer_score:
        return {"message": "You win!", "player_hand": player_hand, "dealer_hand": dealer_hand}
    elif player_score < dealer_score:
        return {"message": "Dealer wins.", "player_hand": player_hand, "dealer_hand": dealer_hand}
    else:
        return {"message": "It's a tie.", "player_hand": player_hand, "dealer_hand": dealer_hand}
