import streamlit as st
import random
import time

# Set page config
st.set_page_config(
    page_title="Card Drawing System",
    layout="centered"
)

# CSS for card flipping
st.markdown("""
<style>
    .card-container {
        width: 150px;
        height: 210px;
        perspective: 1000px;
        margin: 10px;
        display: inline-block;
    }
    
    .card {
        position: relative;
        width: 100%;
        height: 100%;
        transition: transform 0.6s;
        transform-style: preserve-3d;
    }
    
    .card.flipped {
        transform: rotateY(180deg);
    }
    
    .card-face {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .card-back {
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
    }
    
    .card-front {
        background: white;
        transform: rotateY(180deg);
        color: black;
        font-weight: bold;
        font-size: 24px;
    }
    
    .card-value {
        font-size: 36px;
        font-weight: bold;
    }
    
    .card-suit {
        font-size: 48px;
        margin-top: -15px;
    }
    
    .red {
        color: red;
    }
    
    .black {
        color: black;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cards' not in st.session_state:
    st.session_state.cards = [{'flipped': False, 'value': None, 'suit': None, 'color': None} for _ in range(3)]
if 'deck' not in st.session_state:
    # Create a deck of cards
    suits = ['♥', '♦', '♠', '♣']
    values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    st.session_state.deck = []
    for suit in suits:
        color = 'red' if suit in ['♥', '♦'] else 'black'
        for value in values:
            st.session_state.deck.append({'value': value, 'suit': suit, 'color': color})
    random.shuffle(st.session_state.deck)
if 'draw_clicked' not in st.session_state:
    st.session_state.draw_clicked = False

# Title
st.title("Card Drawing System")

# Function to draw cards
def draw_cards():
    st.session_state.draw_clicked = True
    # Reset cards
    for i in range(3):
        st.session_state.cards[i]['flipped'] = False
    
    # Draw new cards from the deck
    for i in range(3):
        if len(st.session_state.deck) > 0:
            card = st.session_state.deck.pop()
            st.session_state.cards[i]['value'] = card['value']
            st.session_state.cards[i]['suit'] = card['suit']
            st.session_state.cards[i]['color'] = card['color']
        else:
            # Reshuffle the deck if it's empty
            st.warning("Reshuffling the deck...")
            suits = ['♥', '♦', '♠', '♣']
            values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
            st.session_state.deck = []
            for suit in suits:
                color = 'red' if suit in ['♥', '♦'] else 'black'
                for value in values:
                    st.session_state.deck.append({'value': value, 'suit': suit, 'color': color})
            random.shuffle(st.session_state.deck)
            card = st.session_state.deck.pop()
            st.session_state.cards[i]['value'] = card['value']
            st.session_state.cards[i]['suit'] = card['suit']
            st.session_state.cards[i]['color'] = card['color']

# Draw button
if st.button("Draw Cards", use_container_width=True, type="primary"):
    draw_cards()

# Display cards
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
cards_container = st.empty()

# Create HTML for cards
def create_cards_html():
    html = ""
    for i, card in enumerate(st.session_state.cards):
        flipped_class = "flipped" if card['flipped'] else ""
        html += f"""
        <div class="card-container">
            <div class="card {flipped_class}" id="card-{i}">
                <div class="card-face card-back">
                </div>
                <div class="card-face card-front">
                    <div>
                        <div class="card-value {card['color']}">{card['value']}</div>
                        <div class="card-suit {card['color']}">{card['suit']}</div>
                    </div>
                </div>
            </div>
        </div>
        """
    return html

cards_container.markdown(create_cards_html(), unsafe_allow_html=True)

# Flip cards with animation if draw was clicked
if st.session_state.draw_clicked:
    for i in range(3):
        time.sleep(0.3)  # Add delay for sequential flipping
        st.session_state.cards[i]['flipped'] = True
        cards_container.markdown(create_cards_html(), unsafe_allow_html=True)
    
    # Reset flag after animation
    st.session_state.draw_clicked = False

st.markdown("</div>", unsafe_allow_html=True)

# Add instructions
st.markdown("---")
st.markdown("### How to use:")
st.markdown("1. Click the 'Draw Cards' button to draw three random cards")
st.markdown("2. The cards will flip one by one, revealing their values")
st.markdown("3. Each draw takes cards from a standard 52-card deck")
st.markdown("4. When the deck is empty, it will automatically reshuffle")
