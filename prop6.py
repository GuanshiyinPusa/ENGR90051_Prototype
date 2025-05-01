import streamlit as st
import random
import time
import os
import glob
from PIL import Image

# Set page config
st.set_page_config(
    page_title="Card Drawing System",
    layout="wide"
)

# Initialize session state variables first, before any other code
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'reward_tiers' not in st.session_state:
    st.session_state.reward_tiers = [1000, 2000, 3000, 4000]
if 'can_draw' not in st.session_state:
    st.session_state.can_draw = False
if 'last_tier_claimed' not in st.session_state:
    st.session_state.last_tier_claimed = 0
if 'cards' not in st.session_state:
    st.session_state.cards = [{'flipped': False, 'image_index': None} for _ in range(3)]
if 'card_indices' not in st.session_state:
    st.session_state.card_indices = []
if 'draw_clicked' not in st.session_state:
    st.session_state.draw_clicked = False
if 'card_back_image' not in st.session_state:
    st.session_state.card_back_image = None
if 'front_images' not in st.session_state:
    st.session_state.front_images = []
if 'card_filenames' not in st.session_state:
    st.session_state.card_filenames = []
if 'card_history' not in st.session_state:
    st.session_state.card_history = []  # List to store draw history

# CSS for card flipping with image support
st.markdown("""
<style>
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        text-align: right;
        padding-right: 100px;
    }
    
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
        overflow: hidden;
    }
    
    .card-back {
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
    }
    
    .card-front {
        background: white;
        transform: rotateY(180deg);
    }
    
    .card-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .title-container {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .draw-button-container {
        display: flex;
        justify-content: flex-end;
        margin-right: 170px;
        margin-bottom: 20px;
    }
    
    .points-container {
        padding: 20px;
        margin-bottom: 30px;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    
    .points-buttons {
        display: flex;
        justify-content: space-between;
        margin-top: 20px;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background-color: #4CAF50;
    }
    
    /* Markers for reward tiers */
    .tier-markers {
        display: flex;
        justify-content: space-between;
        position: relative;
        margin-top: -15px;
        width: 100%;
        padding: 0;
    }
    
    .tier-marker {
        position: relative;
        text-align: center;
        flex: 0 0 auto;
    }
    
    .tier-marker-first {
        text-align: left;
        margin-left: 0;
    }
    
    .tier-marker-last {
        text-align: right;
        margin-right: 0;
    }
    
    .tier-marker::before {
        content: '';
        position: absolute;
        top: -10px;
        left: 50%;
        width: 2px;
        height: 10px;
        background-color: #333;
        transform: translateX(-50%);
    }
    
    .tier-marker-first::before {
        left: 0;
        transform: none;
    }
    
    .tier-marker-last::before {
        left: auto;
        right: 0;
        transform: none;
    }
    
    /* Center the app content */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 1200px !important;
    }
</style>
""", unsafe_allow_html=True)

# Define paths for card images
CARD_BACK_PATH = "cards/back.png"  # Path to the back image
CARD_FRONTS_PATH = "cards/fronts/"  # Path to the folder with front images

# Function to load card images from directory
def load_card_images():
    try:
        # Load the back image
        if os.path.exists(CARD_BACK_PATH):
            back_image = Image.open(CARD_BACK_PATH)
            st.session_state.card_back_image = back_image
        else:
            st.session_state.card_back_image = None
            st.sidebar.warning(f"Card back image not found at {CARD_BACK_PATH}")
            
        # Load front images
        st.session_state.front_images = []
        st.session_state.card_filenames = []  # Reset filenames list
        front_image_paths = glob.glob(os.path.join(CARD_FRONTS_PATH, "*.png")) + \
                          glob.glob(os.path.join(CARD_FRONTS_PATH, "*.jpg")) + \
                          glob.glob(os.path.join(CARD_FRONTS_PATH, "*.jpeg"))
        
        for img_path in front_image_paths:
            st.session_state.front_images.append(Image.open(img_path))
            # Extract just the filename without path and extension for display
            filename = os.path.basename(img_path)
            name_without_ext = os.path.splitext(filename)[0]
            st.session_state.card_filenames.append(name_without_ext)
            
        if not st.session_state.front_images:
            st.sidebar.warning(f"No card front images found in {CARD_FRONTS_PATH}")
            
        return len(st.session_state.front_images)
    except Exception as e:
        st.sidebar.error(f"Error loading images: {e}")
        return 0

# Load images if not already loaded
if len(st.session_state.card_indices) == 0 and len(st.session_state.front_images) == 0:
    num_cards = load_card_images()
    st.session_state.card_indices = list(range(num_cards))
    random.shuffle(st.session_state.card_indices)

# Callback functions for buttons
def add_100_points():
    st.session_state.points += 100
    check_reward_eligibility()

def add_500_points():
    st.session_state.points += 500
    check_reward_eligibility()

def check_reward_eligibility():
    # Check if the user has reached a new tier
    current_tier = 0
    for tier in st.session_state.reward_tiers:
        if st.session_state.points >= tier and tier > st.session_state.last_tier_claimed:
            st.session_state.can_draw = True
            break

# Function to draw cards
def draw_cards():
    # Check if user can draw cards
    if not st.session_state.can_draw:
        # Find the next available tier
        next_tier = None
        for tier in st.session_state.reward_tiers:
            if tier > st.session_state.last_tier_claimed:
                next_tier = tier
                break
        
        if next_tier:
            points_needed = next_tier - st.session_state.points
            if points_needed > 0:
                st.warning(f"You need {points_needed} more points to reach the next reward tier ({next_tier}).")
        return False
    
    # User can draw, proceed with drawing cards
    st.session_state.draw_clicked = True
    current_tier = 0
    
    # Find the current tier that was reached
    for tier in st.session_state.reward_tiers:
        if st.session_state.points >= tier and tier > st.session_state.last_tier_claimed:
            current_tier = tier
            break
    
    # Reset cards
    for i in range(3):
        st.session_state.cards[i]['flipped'] = False
    
    # Draw new cards from the deck
    drawn_cards = []
    for i in range(3):
        if st.session_state.card_indices:
            # Get the next card index
            card_index = st.session_state.card_indices.pop(0)
            st.session_state.cards[i]['image_index'] = card_index
            
            # Record card in history
            if 0 <= card_index < len(st.session_state.card_filenames):
                card_name = st.session_state.card_filenames[card_index]
                drawn_cards.append(card_name)
                
                # Add to history
                st.session_state.card_history.append({
                    "card_name": card_name,
                    "tier": current_tier,
                    "draw_time": time.strftime("%Y-%m-%d %H:%M:%S")
                })
        else:
            # Reshuffle the deck if it's empty
            st.warning("Reshuffling the deck...")
            st.session_state.card_indices = list(range(len(st.session_state.front_images)))
            random.shuffle(st.session_state.card_indices)
            
            # Draw a card
            if st.session_state.card_indices:
                card_index = st.session_state.card_indices.pop(0)
                st.session_state.cards[i]['image_index'] = card_index
                
                # Record card in history
                if 0 <= card_index < len(st.session_state.card_filenames):
                    card_name = st.session_state.card_filenames[card_index]
                    drawn_cards.append(card_name)
                    
                    # Add to history
                    st.session_state.card_history.append({
                        "card_name": card_name,
                        "tier": current_tier,
                        "draw_time": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
    
    # Update the last claimed tier
    if current_tier > 0:
        st.session_state.last_tier_claimed = current_tier
        st.session_state.can_draw = False
    
    return True

# Function to convert PIL image to base64
def get_image_base64(img):
    import base64
    from io import BytesIO
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Create HTML for cards
def create_cards_html():
    html = ""
    for i, card in enumerate(st.session_state.cards):
        flipped_class = "flipped" if card['flipped'] else ""
        
        # Back of card
        back_html = ""
        if st.session_state.card_back_image is not None:
            # Use the back image
            back_img_b64 = get_image_base64(st.session_state.card_back_image)
            back_html = f'<img src="data:image/png;base64,{back_img_b64}" class="card-image" alt="Card Back">'
        else:
            # Use a default back
            back_html = '<div style="background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%); width: 100%; height: 100%;"></div>'
        
        # Front of card
        front_html = ""
        if card['image_index'] is not None and 0 <= card['image_index'] < len(st.session_state.front_images):
            # Use the front image
            front_img_b64 = get_image_base64(st.session_state.front_images[card['image_index']])
            front_html = f'<img src="data:image/png;base64,{front_img_b64}" class="card-image" alt="Card Front">'
        else:
            # Use a placeholder
            front_html = '<div style="background: white; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;">?</div>'
        
        html += f"""
        <div class="card-container">
            <div class="card {flipped_class}" id="card-{i}">
                <div class="card-face card-back">
                    {back_html}
                </div>
                <div class="card-face card-front">
                    {front_html}
                </div>
            </div>
        </div>
        """
    return html

# Create a centered container for the title
st.markdown('<div class="title-container">', unsafe_allow_html=True)
st.title("Card Drawing System")
st.markdown('</div>', unsafe_allow_html=True)

# Display card drawing history table
st.markdown("<h3>Card Drawing History</h3>", unsafe_allow_html=True)

if not st.session_state.card_history:
    st.info("No cards have been drawn yet. Reach a reward tier to draw cards!")
else:
    # Process the history data for the table
    history_data = {}
    
    # Count occurrences of each card name
    for entry in st.session_state.card_history:
        card_name = entry["card_name"]
        tier = entry["tier"]
        
        if card_name not in history_data:
            history_data[card_name] = {
                "name": card_name,
                "count": 1,
                "tiers": [tier],
                "last_drawn": entry["draw_time"]
            }
        else:
            history_data[card_name]["count"] += 1
            history_data[card_name]["tiers"].append(tier)
            history_data[card_name]["last_drawn"] = entry["draw_time"]
    
    # Convert to list for table display
    table_data = []
    for card_name, data in history_data.items():
        # Format tiers as a string
        tiers_str = ", ".join([f"{tier} points" for tier in data["tiers"]])
        
        table_data.append({
            "Card Name": data["name"],
            "Draw Count": data["count"],
            "Tiers Drawn At": tiers_str,
            "Last Drawn": data["last_drawn"]
        })
    
    # Display the table
    st.table(table_data)
    
    # Option to clear history
    if st.button("Clear Drawing History"):
        st.session_state.card_history = []
        st.rerun()  # Use st.rerun() instead of experimental_rerun()


# Points system container
st.markdown('<div class="points-container">', unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader(f"Current Points: {st.session_state.points}")
    
    # Progress bar for points (0 to 5000)
    progress = min(st.session_state.points / 5000, 1.0)  # Ensure it doesn't exceed 1.0
    st.progress(progress)
    
    # Tier markers with proper alignment
    tier_markers_html = '<div class="tier-markers">'
    
    # Start marker (0)
    tier_markers_html += '<div class="tier-marker tier-marker-first">0</div>'
    
    # Reward tier markers
    for tier in st.session_state.reward_tiers:
        tier_markers_html += f'<div class="tier-marker">{tier}</div>'
    
    # End marker (5000)
    tier_markers_html += '<div class="tier-marker tier-marker-last">5000</div>'
    tier_markers_html += '</div>'
    
    st.markdown(tier_markers_html, unsafe_allow_html=True)
    
    # Check if user has reached a new tier
    current_tier = 0
    current_tier_index = 0
    for idx, tier in enumerate(st.session_state.reward_tiers):
        if st.session_state.points >= tier and tier > st.session_state.last_tier_claimed:
            current_tier = tier
            current_tier_index = idx + 1
            st.session_state.can_draw = True
    
    if current_tier > 0 and st.session_state.can_draw:
        st.success(f"🎉 You've reached Tier {current_tier_index}! Click 'Draw Cards' to claim your reward.")
    
with col2:
    # Add points buttons
    st.button("Add 100 Points", on_click=add_100_points)
    st.button("Add 500 Points", on_click=add_500_points)

st.markdown('</div>', unsafe_allow_html=True)

# Create the right-aligned container for the card drawing area
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Draw button in a container with right alignment
st.markdown('<div class="draw-button-container">', unsafe_allow_html=True)

# Draw button with dynamic styling based on whether user can draw
button_type = "primary" if st.session_state.can_draw else "secondary"
button_label = "Draw Cards" if st.session_state.can_draw else "Draw Cards (Need More Points)"

draw_button = st.button(button_label, type=button_type, disabled=not st.session_state.can_draw)
if draw_button:
    if len(st.session_state.front_images) > 0:
        success = draw_cards()
        if not success:
            st.error("You need to reach a new tier to draw cards.")
    else:
        st.error("No card images loaded. Please check the image directory.")
        
st.markdown('</div>', unsafe_allow_html=True)

# Display cards
cards_container = st.empty()
cards_container.markdown(create_cards_html(), unsafe_allow_html=True)

# Flip cards with animation if draw was clicked
if st.session_state.draw_clicked:
    for i in range(3):
        time.sleep(0.3)  # Add delay for sequential flipping
        st.session_state.cards[i]['flipped'] = True
        cards_container.markdown(create_cards_html(), unsafe_allow_html=True)
    
    # Reset flag after animation
    st.session_state.draw_clicked = False

st.markdown('</div>', unsafe_allow_html=True)

# Sidebar with information about loaded cards
with st.sidebar:
    st.header("Card Information")
    
    if st.button("Reload Card Images"):
        num_cards = load_card_images()
        st.session_state.card_indices = list(range(num_cards))
        random.shuffle(st.session_state.card_indices)
        st.success(f"Loaded {num_cards} cards")
    
    if len(st.session_state.front_images) > 0:
        st.success(f"Loaded {len(st.session_state.front_images)} card front images")
    else:
        st.warning("No card front images loaded")
        
    st.info(f"""
    Expected directory structure:
    - {CARD_BACK_PATH} (single back image)
    - {CARD_FRONTS_PATH} (folder with all front images)
    """)
