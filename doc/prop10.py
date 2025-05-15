import streamlit as st
import random
import time
import os
import glob
from PIL import Image
import io

# Set page config
st.set_page_config(
    page_title="Card Drawing System",
    layout="wide"
)

# Initialize session state variables first, before any other code
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'can_draw' not in st.session_state:
    st.session_state.can_draw = True  # Set to True since drawing costs 100 points
if 'cards' not in st.session_state:
    st.session_state.cards = [{'flipped': False, 'image_index': None, 'pool': None} for _ in range(3)]
if 'common_card_indices' not in st.session_state:
    st.session_state.common_card_indices = []
if 'rare_card_indices' not in st.session_state:
    st.session_state.rare_card_indices = []
if 'draw_clicked' not in st.session_state:
    st.session_state.draw_clicked = False
if 'card_back_image' not in st.session_state:
    st.session_state.card_back_image = None
if 'common_images' not in st.session_state:
    st.session_state.common_images = []
if 'rare_images' not in st.session_state:
    st.session_state.rare_images = []
if 'common_filenames' not in st.session_state:
    st.session_state.common_filenames = []
if 'rare_filenames' not in st.session_state:
    st.session_state.rare_filenames = []
if 'card_history' not in st.session_state:
    st.session_state.card_history = []  # List to store draw history
if 'card_values' not in st.session_state:
    # Define card values
    st.session_state.card_values = {
        "common": 10,
        "rare": 20
    }

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
    
    /* Center the app content */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 1200px !important;
    }
    
    /* Card rarity indicator */
    .card-rarity {
        position: absolute;
        top: 5px;
        left: 5px;
        padding: 2px 5px;
        border-radius: 3px;
        font-size: 10px;
        font-weight: bold;
        z-index: 10;
    }
    
    .common-card {
        background-color: #aaa;
        color: white;
    }
    
    .rare-card {
        background-color: gold;
        color: black;
    }
</style>
""", unsafe_allow_html=True)

# Define paths for card images
CARD_BACK_PATH = "cards/back.png"  # Path to the back image
COMMON_CARDS_PATH = "cards/fronts/common/"  # Path to the folder with common front images
RARE_CARDS_PATH = "cards/fronts/rare/"  # Path to the folder with rare front images
UPLOADED_CARDS_PATH = "cards/fronts/common/uploaded/"  # Path for uploaded cards

# Ensure the uploaded cards directory exists
os.makedirs(UPLOADED_CARDS_PATH, exist_ok=True)

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
            
        # Load common front images
        st.session_state.common_images = []
        st.session_state.common_filenames = []
        common_image_paths = glob.glob(os.path.join(COMMON_CARDS_PATH, "*.png")) + \
                          glob.glob(os.path.join(COMMON_CARDS_PATH, "*.jpg")) + \
                          glob.glob(os.path.join(COMMON_CARDS_PATH, "*.jpeg")) + \
                          glob.glob(os.path.join(UPLOADED_CARDS_PATH, "*.png")) + \
                          glob.glob(os.path.join(UPLOADED_CARDS_PATH, "*.jpg")) + \
                          glob.glob(os.path.join(UPLOADED_CARDS_PATH, "*.jpeg"))
        
        for img_path in common_image_paths:
            st.session_state.common_images.append(Image.open(img_path))
            # Extract just the filename without path and extension for display
            filename = os.path.basename(img_path)
            name_without_ext = os.path.splitext(filename)[0]
            st.session_state.common_filenames.append(name_without_ext)
            
        if not st.session_state.common_images:
            st.sidebar.warning(f"No common card images found in {COMMON_CARDS_PATH}")
        
        # Load rare front images
        st.session_state.rare_images = []
        st.session_state.rare_filenames = []
        rare_image_paths = glob.glob(os.path.join(RARE_CARDS_PATH, "*.png")) + \
                        glob.glob(os.path.join(RARE_CARDS_PATH, "*.jpg")) + \
                        glob.glob(os.path.join(RARE_CARDS_PATH, "*.jpeg"))
        
        for img_path in rare_image_paths:
            st.session_state.rare_images.append(Image.open(img_path))
            # Extract just the filename without path and extension for display
            filename = os.path.basename(img_path)
            name_without_ext = os.path.splitext(filename)[0]
            st.session_state.rare_filenames.append(name_without_ext)
            
        if not st.session_state.rare_images:
            st.sidebar.warning(f"No rare card images found in {RARE_CARDS_PATH}")
            
        return len(st.session_state.common_images), len(st.session_state.rare_images)
    except Exception as e:
        st.sidebar.error(f"Error loading images: {e}")
        return 0, 0

# Load images if not already loaded
if len(st.session_state.common_card_indices) == 0 and len(st.session_state.rare_card_indices) == 0:
    num_common, num_rare = load_card_images()
    st.session_state.common_card_indices = list(range(num_common))
    st.session_state.rare_card_indices = list(range(num_rare))
    random.shuffle(st.session_state.common_card_indices)
    random.shuffle(st.session_state.rare_card_indices)

# Callback functions for buttons
def add_100_points():
    st.session_state.points += 100

def add_500_points():
    st.session_state.points += 500

# Function to check if user can draw cards
def can_draw_cards():
    return st.session_state.points >= 100

# Function to draw cards
def draw_cards():
    # Check if user has enough points
    if st.session_state.points < 100:
        st.warning(f"You need {100 - st.session_state.points} more points to draw cards.")
        return False
    
    # Deduct points for drawing
    st.session_state.points -= 100
    
    # User can draw, proceed with drawing cards
    st.session_state.draw_clicked = True
    
    # Reset cards
    for i in range(3):
        st.session_state.cards[i]['flipped'] = False
    
    # Draw new cards from the deck - first two from common pool, last one from rare pool
    drawn_cards = []
    
    # Draw the first two cards from common pool
    for i in range(2):
        if st.session_state.common_card_indices:
            # Get the next card index
            card_index = st.session_state.common_card_indices.pop(0)
            st.session_state.cards[i]['image_index'] = card_index
            st.session_state.cards[i]['pool'] = 'common'
            
            # Record card in history
            if 0 <= card_index < len(st.session_state.common_filenames):
                card_name = st.session_state.common_filenames[card_index]
                drawn_cards.append({"name": card_name, "rarity": "common"})
                
                # Add to history
                st.session_state.card_history.append({
                    "card_name": card_name,
                    "rarity": "common",
                    "credits": st.session_state.card_values["common"],
                    "draw_time": time.strftime("%Y-%m-%d %H:%M:%S")
                })
        else:
            # Reshuffle the common deck if it's empty
            st.warning("Reshuffling the common deck...")
            st.session_state.common_card_indices = list(range(len(st.session_state.common_images)))
            random.shuffle(st.session_state.common_card_indices)
            
            # Draw a card
            if st.session_state.common_card_indices:
                card_index = st.session_state.common_card_indices.pop(0)
                st.session_state.cards[i]['image_index'] = card_index
                st.session_state.cards[i]['pool'] = 'common'
                
                # Record card in history
                if 0 <= card_index < len(st.session_state.common_filenames):
                    card_name = st.session_state.common_filenames[card_index]
                    drawn_cards.append({"name": card_name, "rarity": "common"})
                    
                    # Add to history
                    st.session_state.card_history.append({
                        "card_name": card_name,
                        "rarity": "common",
                        "credits": st.session_state.card_values["common"],
                        "draw_time": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
    
    # Draw the third card from the rare pool
    if st.session_state.rare_card_indices:
        # Get the next card index
        card_index = st.session_state.rare_card_indices.pop(0)
        st.session_state.cards[2]['image_index'] = card_index
        st.session_state.cards[2]['pool'] = 'rare'
        
        # Record card in history
        if 0 <= card_index < len(st.session_state.rare_filenames):
            card_name = st.session_state.rare_filenames[card_index]
            drawn_cards.append({"name": card_name, "rarity": "rare"})
            
            # Add to history
            st.session_state.card_history.append({
                "card_name": card_name,
                "rarity": "rare",
                "credits": st.session_state.card_values["rare"],
                "draw_time": time.strftime("%Y-%m-%d %H:%M:%S")
            })
    else:
        # Reshuffle the rare deck if it's empty
        st.warning("Reshuffling the rare deck...")
        st.session_state.rare_card_indices = list(range(len(st.session_state.rare_images)))
        random.shuffle(st.session_state.rare_card_indices)
        
        # Draw a card
        if st.session_state.rare_card_indices:
            card_index = st.session_state.rare_card_indices.pop(0)
            st.session_state.cards[2]['image_index'] = card_index
            st.session_state.cards[2]['pool'] = 'rare'
            
            # Record card in history
            if 0 <= card_index < len(st.session_state.rare_filenames):
                card_name = st.session_state.rare_filenames[card_index]
                drawn_cards.append({"name": card_name, "rarity": "rare"})
                
                # Add to history
                st.session_state.card_history.append({
                    "card_name": card_name,
                    "rarity": "rare",
                    "credits": st.session_state.card_values["rare"],
                    "draw_time": time.strftime("%Y-%m-%d %H:%M:%S")
                })
    
    return True

# Function to handle image upload
def handle_image_upload(uploaded_file):
    if uploaded_file is not None:
        # Read the image
        image_bytes = uploaded_file.getvalue()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Resize the image to fit card dimensions
        image = image.resize((150, 210), Image.LANCZOS)
        
        # Create a filename from the uploaded file
        filename = os.path.splitext(uploaded_file.name)[0]
        # Ensure filename is unique by adding timestamp if needed
        timestamp = int(time.time())
        filepath = os.path.join(UPLOADED_CARDS_PATH, f"{filename}_{timestamp}.png")
        
        # Save the image
        image.save(filepath)
        
        # Reload the card images to include the new upload
        num_common, num_rare = load_card_images()
        
        # Update the indices
        st.session_state.common_card_indices = list(range(num_common))
        random.shuffle(st.session_state.common_card_indices)
        
        st.success(f"Image uploaded successfully! Added to common card pool.")
        return True
    return False

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
        rarity_badge = ""
        
        if card['image_index'] is not None and card['pool'] is not None:
            # Choose the image based on the pool
            if card['pool'] == 'common' and 0 <= card['image_index'] < len(st.session_state.common_images):
                front_img_b64 = get_image_base64(st.session_state.common_images[card['image_index']])
                rarity_badge = '<div class="card-rarity common-card">Common</div>'
            elif card['pool'] == 'rare' and 0 <= card['image_index'] < len(st.session_state.rare_images):
                front_img_b64 = get_image_base64(st.session_state.rare_images[card['image_index']])
                rarity_badge = '<div class="card-rarity rare-card">Rare</div>'
            else:
                # Use a placeholder if index is invalid
                front_html = '<div style="background: white; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;">?</div>'
                front_img_b64 = None
            
            if front_img_b64:
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
                    {rarity_badge}
                    {front_html}
                </div>
            </div>
        </div>
        """
    return html

# Create a centered container for the title
st.markdown('<div class="title-container">', unsafe_allow_html=True)
st.title("E-Waste Recycling Card Drawing System")
st.markdown('</div>', unsafe_allow_html=True)

# Create two columns for the main layout
col1, col2 = st.columns([7, 3])

with col1:
    # Display card drawing history table
    st.markdown("<h3>Card Drawing History</h3>", unsafe_allow_html=True)
    
    if not st.session_state.card_history:
        st.info("No cards have been drawn yet. Use your points to draw cards!")
    else:
        # Process the history data for the table
        history_data = {}
        total_credits = 0
        
        # Count occurrences of each card name
        for entry in st.session_state.card_history:
            card_name = entry["card_name"]
            rarity = entry["rarity"]
            credits = entry["credits"]
            
            if card_name not in history_data:
                history_data[card_name] = {
                    "name": card_name,
                    "rarity": rarity,
                    "count": 1,
                    "credits": credits,
                    "total_credits": credits
                }
                total_credits += credits
            else:
                history_data[card_name]["count"] += 1
                # Update total credits for this card
                history_data[card_name]["total_credits"] = history_data[card_name]["count"] * credits
                total_credits += credits
        
        # Convert to list for table display
        table_data = []
        for card_name, data in history_data.items():
            table_data.append({
                "Card Name": data["name"],
                "Rarity": data["rarity"].capitalize(),
                "Times Drawn": data["count"],
                "Credits": data["credits"],
                "Total Credits": data["total_credits"]
            })
        
        # Add a total row
        table_data.append({
            "Card Name": "TOTAL",
            "Rarity": "",
            "Times Drawn": "",
            "Credits": "",
            "Total Credits": total_credits
        })
        
        # Display the table
        st.table(table_data)
        
        # Option to clear history
        if st.button("Clear Drawing History"):
            st.session_state.card_history = []
            st.rerun()

    # Points system container
    st.markdown('<div class="points-container">', unsafe_allow_html=True)
    points_col1, points_col2 = st.columns([3, 1])
    
    with points_col1:
        st.subheader(f"Current Points: {st.session_state.points}")
        
        # Information about drawing cost
        st.info("Drawing cards costs 100 points")
        
    with points_col2:
        # Add points buttons
        st.button("Add 100 Points", on_click=add_100_points)
        st.button("Add 500 Points", on_click=add_500_points)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Create the right-aligned container for the card drawing area
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Draw button in a container with right alignment
    st.markdown('<div class="draw-button-container">', unsafe_allow_html=True)
    
    # Draw button with dynamic styling based on whether user can draw
    can_draw = can_draw_cards()
    button_type = "primary" if can_draw else "secondary"
    button_label = "Draw Cards (100 points)" if can_draw else "Draw Cards (Need 100 Points)"
    
    draw_button = st.button(button_label, type=button_type, disabled=not can_draw)
    if draw_button:
        if len(st.session_state.common_images) > 0 and len(st.session_state.rare_images) > 0:
            success = draw_cards()
            if not success:
                st.error("You need at least 100 points to draw cards.")
        else:
            st.error("No card images loaded. Please check the image directories.")
            
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

# Sidebar with image upload and information
with st.sidebar:
    st.header("Upload Your Card")
    
    st.write("Upload an image to add to the common card pool. The image will be resized to fit the card dimensions (150x210).")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if st.button("Upload Image"):
        if uploaded_file is None:
            st.error("Please select an image file first.")
        else:
            success = handle_image_upload(uploaded_file)
            if success:
                st.success("Your card has been added to the common pool!")
    
    st.markdown("---")
    
    st.header("Card Information")
    st.write("Common cards: Worth 10 credits")
    st.write("Rare cards: Worth 20 credits")
    
    st.markdown("---")
    
    st.header("How It Works")
    st.write("1. Earn points by recycling e-waste on campus")
    st.write("2. Each card draw costs 100 points")
    st.write("3. Drawing gives you 2 common cards and 1 rare card")
    st.write("4. Collect credits to exchange for items")
    
    st.markdown("---")
    
    # Add a hidden reload button at the bottom for debugging
    if st.button("Reload Images", key="reload_hidden"):
        num_common, num_rare = load_card_images()
        st.session_state.common_card_indices = list(range(num_common))
        st.session_state.rare_card_indices = list(range(num_rare))
        random.shuffle(st.session_state.common_card_indices)
        random.shuffle(st.session_state.rare_card_indices)
