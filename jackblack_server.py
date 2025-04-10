from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import random

app = FastAPI()

# Card deck for Blackjack
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
}

# Game state
player_hand = []
dealer_hand = []
game_over = False

# Function to start a new game
def new_game():
    global player_hand, dealer_hand, game_over
    player_hand = [draw_card(), draw_card()]
    dealer_hand = [draw_card(), draw_card()]
    game_over = False

# Function to draw a card
def draw_card():
    return random.choice(RANKS)

# Function to calculate the total value of a hand
def calculate_hand_value(hand):
    value = sum(VALUES[card] for card in hand)
    # Adjust for aces if necessary
    ace_count = hand.count('Ace')
    while value > 21 and ace_count:
        value -= 10  # Adjust one ace to count as 1
        ace_count -= 1
    return value

# WebSocket endpoint for interacting with the game
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Receive player's name
    player_name = await websocket.receive_text()
    
    # Start a new game
    new_game()
    await websocket.send_text(f"Welcome {player_name}! The game has started.")
    
    # Show the initial hands
    await websocket.send_text(f"Your hand: {player_hand} - Value: {calculate_hand_value(player_hand)}")
    await websocket.send_text(f"Dealer's hand: {dealer_hand[0]} and a hidden card.")

    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "hit":
                player_hand.append(draw_card())
                player_value = calculate_hand_value(player_hand)
                await websocket.send_text(f"Your hand: {player_hand} - Value: {player_value}")
                
                if player_value > 21:
                    await websocket.send_text(f"Sorry, {player_name}, you busted! Your hand value is over 21.")
                    game_over = True
                    await websocket.send_text("Game Over.")
                    break

            elif data == "stand":
                dealer_value = calculate_hand_value(dealer_hand)
                
                # Dealer's turn
                while dealer_value < 17:
                    dealer_hand.append(draw_card())
                    dealer_value = calculate_hand_value(dealer_hand)
                
                await websocket.send_text(f"Dealer's hand: {dealer_hand} - Value: {dealer_value}")
                
                # Compare hands
                player_value = calculate_hand_value(player_hand)
                if dealer_value > 21:
                    await websocket.send_text(f"Dealer busted! You win with {player_value}!")
                elif player_value > dealer_value:
                    await websocket.send_text(f"You win with {player_value} vs {dealer_value}!")
                elif player_value < dealer_value:
                    await websocket.send_text(f"Dealer wins with {dealer_value} vs {player_value}!")
                else:
                    await websocket.send_text(f"It's a tie with {player_value}!")
                
                game_over = True
                await websocket.send_text("Game Over.")
                break
                
    except WebSocketDisconnect:
        print(f"Player {player_name} disconnected.")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await websocket.close()

# Serve HTML page (for testing purposes)
@app.get("/")
async def get():
    with open("index.html", "r") as file:
        return HTMLResponse(content=file.read())

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
