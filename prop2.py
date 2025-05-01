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

# CSS for card flipping with image support
st.markdown("""
<style>
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        text-align: center;
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
    
    /* Center the app content */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 1200px !important;
    }
</style>
""", unsafe_allow_html=True)

# Create a centered container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Title
st.title("Card Drawing System")

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
        front_image_paths = glob.glob(os.path.join(CARD_FRONTS_PATH, "*.png")) + \
                          glob.glob(os.path.join(CARD_FRONTS_PATH, "*.jpg")) + \
                          glob.glob(os.path.join(CARD_FRONTS_PATH, "*.jpeg"))
        
        for img_path in front_image_paths:
            st.session_state.front_images.append(Image.open(img_path))
            
        if not st.session_state.front_images:
            st.sidebar.warning(f"No card front images found in {CARD_FRONTS_PATH}")
            
        return len(st.session_state.front_images)
    except Exception as e:
        st.sidebar.error(f"Error loading images: {e}")
        return 0

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.cards = [{'flipped': False, 'image_index': None} for _ in range(3)]
    st.session_state.card_indices = []  # Card indices from the deck
    st.session_state.draw_clicked = False
    st.session_state.card_back_image = None
    st.session_state.front_images = []
    
    # Load images and initialize deck
    num_cards = load_card_images()
    st.session_state.card_indices = list(range(num_cards))
    random.shuffle(st.session_state.card_indices)

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

# Function to draw cards
def draw_cards():
    st.session_state.draw_clicked = True
    # Reset cards
    for i in range(3):
        st.session_state.cards[i]['flipped'] = False
    
    # Draw new cards from the deck
    for i in range(3):
        if st.session_state.card_indices:
            # Get the next card index
            card_index = st.session_state.card_indices.pop(0)
            st.session_state.cards[i]['image_index'] = card_index
        else:
            # Reshuffle the deck if it's empty
            st.warning("Reshuffling the deck...")
            st.session_state.card_indices = list(range(len(st.session_state.front_images)))
            random.shuffle(st.session_state.card_indices)
            
            # Draw a card
            card_index = st.session_state.card_indices.pop(0)
            st.session_state.cards[i]['image_index'] = card_index

# Draw button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Draw Cards", use_container_width=True, type="primary"):
        if len(st.session_state.front_images) > 0:
            draw_cards()
        else:
            st.error("No card images loaded. Please check the image directory.")

# Display cards
cards_container = st.empty()

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
