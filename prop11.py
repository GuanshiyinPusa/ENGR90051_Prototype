import streamlit as st
import random
import time
import os
import glob
from PIL import Image
import io
import pandas as pd
import csv
from datetime import datetime

# Set page config
st.set_page_config(page_title="E-Waste Recycling Card Drawing System", layout="wide")

# Initialize session state variables
if "points" not in st.session_state:
    st.session_state.points = 0
if "card_credits" not in st.session_state:
    st.session_state.card_credits = 0
if "cards" not in st.session_state:
    st.session_state.cards = [
        {"flipped": False, "image_index": None, "pool": None} for _ in range(3)
    ]
if "common_card_indices" not in st.session_state:
    st.session_state.common_card_indices = []
if "rare_card_indices" not in st.session_state:
    st.session_state.rare_card_indices = []
if "legendary_card_indices" not in st.session_state:
    st.session_state.legendary_card_indices = []
if "draw_clicked" not in st.session_state:
    st.session_state.draw_clicked = False
if "card_back_image" not in st.session_state:
    st.session_state.card_back_image = None
if "common_images" not in st.session_state:
    st.session_state.common_images = []
if "rare_images" not in st.session_state:
    st.session_state.rare_images = []
if "legendary_images" not in st.session_state:
    st.session_state.legendary_images = []
if "common_filenames" not in st.session_state:
    st.session_state.common_filenames = []
if "rare_filenames" not in st.session_state:
    st.session_state.rare_filenames = []
if "legendary_filenames" not in st.session_state:
    st.session_state.legendary_filenames = []
if "card_history" not in st.session_state:
    st.session_state.card_history = []  # List to store draw history
if "card_values" not in st.session_state:
    # Define card values
    st.session_state.card_values = {"common": 5, "rare": 10, "legendary": 20}
if "student_info" not in st.session_state:
    # Fake student info
    st.session_state.student_info = {
        "name": "Jane Smith",
        "id": "12345678",
        "email": "jane.smith@student.unimelb.edu.au",
    }
if "recycled_items" not in st.session_state:
    # Prepopulate with fake data
    st.session_state.recycled_items = [
        {"item": "Breadboard", "quantity": 5, "points": 50, "date": "2025-04-10"},
        {"item": "Resistors", "quantity": 100, "points": 100, "date": "2025-04-15"},
        {"item": "Arduino", "quantity": 2, "points": 200, "date": "2025-04-20"},
        {"item": "LCD Display", "quantity": 3, "points": 150, "date": "2025-04-25"},
        {"item": "Capacitors", "quantity": 50, "points": 50, "date": "2025-05-01"},
    ]
if "rewards" not in st.session_state:
    st.session_state.rewards = [
        {"id": 1, "name": "USB Drive", "cost": 30, "purchased": False},
        {"id": 2, "name": "Coffee Voucher", "cost": 50, "purchased": False},
        {"id": 3, "name": "Power Bank", "cost": 100, "purchased": False},
        {"id": 4, "name": "Wireless Earbuds", "cost": 150, "purchased": False},
        {
            "id": 5,
            "name": "Engineering Software License",
            "cost": 200,
            "purchased": False,
        },
        {"id": 6, "name": "Lab Equipment Access", "cost": 250, "purchased": False},
    ]
if "purchased_rewards" not in st.session_state:
    st.session_state.purchased_rewards = []

# CSS for card flipping and layout
st.markdown(
    """
<style>
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        text-align: center;
        padding-right: 50px;
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
        justify-content: center;
        margin-bottom: 20px;
    }
    
    .points-container {
        padding: 20px;
        margin-bottom: 30px;
        border-radius: 10px;
        background-color: #f8f9fa;
        text-align: center;
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
        background-color: #FFD700;
        color: black;
    }
    
    .legendary-card {
        background-color: #FF4500;
        color: white;
    }
    
    /* Rewards styling */
    .reward-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .reward-card {
        width: 200px;
        padding: 20px;
        margin: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .reward-disabled {
        opacity: 0.5;
        background-color: #eee;
    }
    
    /* QR code container */
    .qr-container {
        text-align: center;
        margin: 30px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Define paths for card images
CARD_BACK_PATH = "cards/back.png"  # Path to the back image
COMMON_CARDS_PATH = (
    "cards/fronts/common/"  # Path to the folder with common front images
)
RARE_CARDS_PATH = "cards/fronts/rare/"  # Path to the folder with rare front images
LEGENDARY_CARDS_PATH = (
    "cards/fronts/legendary/"  # Path to the folder with legendary front images
)

# Ensure directories exist
os.makedirs(COMMON_CARDS_PATH, exist_ok=True)
os.makedirs(RARE_CARDS_PATH, exist_ok=True)
os.makedirs(LEGENDARY_CARDS_PATH, exist_ok=True)

# CSV paths
RECYCLED_ITEMS_CSV = "recycled_items.csv"
CARD_HISTORY_CSV = "card_history.csv"
REWARDS_CSV = "rewards.csv"

# Check if CSV files exist, if not create them
if not os.path.exists(RECYCLED_ITEMS_CSV):
    with open(RECYCLED_ITEMS_CSV, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["item", "quantity", "points", "date"])
        # Write some initial data
        writer.writerow(["Breadboard", 5, 50, "2025-04-10"])
        writer.writerow(["Resistors", 100, 100, "2025-04-15"])
        writer.writerow(["Arduino", 2, 200, "2025-04-20"])
        writer.writerow(["LCD Display", 3, 150, "2025-04-25"])
        writer.writerow(["Capacitors", 50, 50, "2025-05-01"])

if not os.path.exists(CARD_HISTORY_CSV):
    with open(CARD_HISTORY_CSV, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["card_name", "rarity", "credits", "draw_time"])

if not os.path.exists(REWARDS_CSV):
    with open(REWARDS_CSV, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "cost", "purchased"])
        writer.writerow([1, "USB Drive", 30, False])
        writer.writerow([2, "Coffee Voucher", 50, False])
        writer.writerow([3, "Power Bank", 100, False])
        writer.writerow([4, "Wireless Earbuds", 150, False])
        writer.writerow([5, "Engineering Software License", 200, False])
        writer.writerow([6, "Lab Equipment Access", 250, False])


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
        common_image_paths = (
            glob.glob(os.path.join(COMMON_CARDS_PATH, "*.png"))
            + glob.glob(os.path.join(COMMON_CARDS_PATH, "*.jpg"))
            + glob.glob(os.path.join(COMMON_CARDS_PATH, "*.jpeg"))
        )

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
        rare_image_paths = (
            glob.glob(os.path.join(RARE_CARDS_PATH, "*.png"))
            + glob.glob(os.path.join(RARE_CARDS_PATH, "*.jpg"))
            + glob.glob(os.path.join(RARE_CARDS_PATH, "*.jpeg"))
        )

        for img_path in rare_image_paths:
            st.session_state.rare_images.append(Image.open(img_path))
            # Extract just the filename without path and extension for display
            filename = os.path.basename(img_path)
            name_without_ext = os.path.splitext(filename)[0]
            st.session_state.rare_filenames.append(name_without_ext)

        if not st.session_state.rare_images:
            st.sidebar.warning(f"No rare card images found in {RARE_CARDS_PATH}")

        # Load legendary front images
        st.session_state.legendary_images = []
        st.session_state.legendary_filenames = []
        legendary_image_paths = (
            glob.glob(os.path.join(LEGENDARY_CARDS_PATH, "*.png"))
            + glob.glob(os.path.join(LEGENDARY_CARDS_PATH, "*.jpg"))
            + glob.glob(os.path.join(LEGENDARY_CARDS_PATH, "*.jpeg"))
        )

        for img_path in legendary_image_paths:
            st.session_state.legendary_images.append(Image.open(img_path))
            # Extract just the filename without path and extension for display
            filename = os.path.basename(img_path)
            name_without_ext = os.path.splitext(filename)[0]
            st.session_state.legendary_filenames.append(name_without_ext)

        if not st.session_state.legendary_images:
            st.sidebar.warning(
                f"No legendary card images found in {LEGENDARY_CARDS_PATH}"
            )

        return (
            len(st.session_state.common_images),
            len(st.session_state.rare_images),
            len(st.session_state.legendary_images),
        )
    except Exception as e:
        st.sidebar.error(f"Error loading images: {e}")
        return 0, 0, 0


# Load images if not already loaded
if (
    len(st.session_state.common_card_indices) == 0
    and len(st.session_state.rare_card_indices) == 0
    and len(st.session_state.legendary_card_indices) == 0
):
    num_common, num_rare, num_legendary = load_card_images()
    st.session_state.common_card_indices = list(range(num_common))
    st.session_state.rare_card_indices = list(range(num_rare))
    st.session_state.legendary_card_indices = list(range(num_legendary))
    random.shuffle(st.session_state.common_card_indices)
    random.shuffle(st.session_state.rare_card_indices)
    random.shuffle(st.session_state.legendary_card_indices)


# Function to check if user can draw cards
def can_draw_cards():
    return st.session_state.points >= 100


# Function to draw cards
def draw_cards():
    # Check if user has enough points
    if st.session_state.points < 100:
        st.warning(
            f"You need {100 - st.session_state.points} more points to draw cards."
        )
        return False

    # Deduct points for drawing
    st.session_state.points -= 100

    # User can draw, proceed with drawing cards
    st.session_state.draw_clicked = True

    # Reset cards
    for i in range(3):
        st.session_state.cards[i]["flipped"] = False

    # Draw new cards from the deck based on slot rules
    drawn_cards = []

    # Slot 1: Common cards only
    if st.session_state.common_card_indices and st.session_state.common_images:
        # Get the next card index
        if not st.session_state.common_card_indices:
            # Reshuffle if empty
            st.session_state.common_card_indices = list(
                range(len(st.session_state.common_images))
            )
            random.shuffle(st.session_state.common_card_indices)

        card_index = st.session_state.common_card_indices.pop(0)
        st.session_state.cards[0]["image_index"] = card_index
        st.session_state.cards[0]["pool"] = "common"

        # Record card in history
        if 0 <= card_index < len(st.session_state.common_filenames):
            card_name = st.session_state.common_filenames[card_index]
            drawn_cards.append({"name": card_name, "rarity": "common"})

            # Add to history
            card_entry = {
                "card_name": card_name,
                "rarity": "common",
                "credits": st.session_state.card_values["common"],
                "draw_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            st.session_state.card_history.append(card_entry)
            st.session_state.card_credits += st.session_state.card_values["common"]

            # Add to CSV
            with open(CARD_HISTORY_CSV, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        card_entry["card_name"],
                        card_entry["rarity"],
                        card_entry["credits"],
                        card_entry["draw_time"],
                    ]
                )
    else:
        st.warning("No common cards available. Check your card files.")

    # Slot 2: Common + Rare cards
    pool = (
        random.choice(["common", "rare"]) if st.session_state.rare_images else "common"
    )

    if pool == "common" and st.session_state.common_images:
        if not st.session_state.common_card_indices:
            # Reshuffle if empty
            st.session_state.common_card_indices = list(
                range(len(st.session_state.common_images))
            )
            random.shuffle(st.session_state.common_card_indices)

        card_index = st.session_state.common_card_indices.pop(0)
        st.session_state.cards[1]["image_index"] = card_index
        st.session_state.cards[1]["pool"] = "common"

        # Record card in history
        if 0 <= card_index < len(st.session_state.common_filenames):
            card_name = st.session_state.common_filenames[card_index]
            drawn_cards.append({"name": card_name, "rarity": "common"})

            # Add to history
            card_entry = {
                "card_name": card_name,
                "rarity": "common",
                "credits": st.session_state.card_values["common"],
                "draw_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            st.session_state.card_history.append(card_entry)
            st.session_state.card_credits += st.session_state.card_values["common"]

            # Add to CSV
            with open(CARD_HISTORY_CSV, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        card_entry["card_name"],
                        card_entry["rarity"],
                        card_entry["credits"],
                        card_entry["draw_time"],
                    ]
                )
    elif pool == "rare" and st.session_state.rare_images:
        if not st.session_state.rare_card_indices:
            # Reshuffle if empty
            st.session_state.rare_card_indices = list(
                range(len(st.session_state.rare_images))
            )
            random.shuffle(st.session_state.rare_card_indices)

        card_index = st.session_state.rare_card_indices.pop(0)
        st.session_state.cards[1]["image_index"] = card_index
        st.session_state.cards[1]["pool"] = "rare"

        # Record card in history
        if 0 <= card_index < len(st.session_state.rare_filenames):
            card_name = st.session_state.rare_filenames[card_index]
            drawn_cards.append({"name": card_name, "rarity": "rare"})

            # Add to history
            card_entry = {
                "card_name": card_name,
                "rarity": "rare",
                "credits": st.session_state.card_values["rare"],
                "draw_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            st.session_state.card_history.append(card_entry)
            st.session_state.card_credits += st.session_state.card_values["rare"]

            # Add to CSV
            with open(CARD_HISTORY_CSV, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        card_entry["card_name"],
                        card_entry["rarity"],
                        card_entry["credits"],
                        card_entry["draw_time"],
                    ]
                )
    else:
        st.warning("Issue with card pool for slot 2.")

    # Slot 3: Rare + Legendary cards
    pool = (
        random.choice(["rare", "legendary"])
        if st.session_state.legendary_images
        else "rare"
    )

    if pool == "rare" and st.session_state.rare_images:
        if not st.session_state.rare_card_indices:
            # Reshuffle if empty
            st.session_state.rare_card_indices = list(
                range(len(st.session_state.rare_images))
            )
            random.shuffle(st.session_state.rare_card_indices)

        card_index = st.session_state.rare_card_indices.pop(0)
        st.session_state.cards[2]["image_index"] = card_index
        st.session_state.cards[2]["pool"] = "rare"

        # Record card in history
        if 0 <= card_index < len(st.session_state.rare_filenames):
            card_name = st.session_state.rare_filenames[card_index]
            drawn_cards.append({"name": card_name, "rarity": "rare"})

            # Add to history
            card_entry = {
                "card_name": card_name,
                "rarity": "rare",
                "credits": st.session_state.card_values["rare"],
                "draw_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            st.session_state.card_history.append(card_entry)
            st.session_state.card_credits += st.session_state.card_values["rare"]

            # Add to CSV
            with open(CARD_HISTORY_CSV, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        card_entry["card_name"],
                        card_entry["rarity"],
                        card_entry["credits"],
                        card_entry["draw_time"],
                    ]
                )
    elif pool == "legendary" and st.session_state.legendary_images:
        if not st.session_state.legendary_card_indices:
            # Reshuffle if empty
            st.session_state.legendary_card_indices = list(
                range(len(st.session_state.legendary_images))
            )
            random.shuffle(st.session_state.legendary_card_indices)

        card_index = st.session_state.legendary_card_indices.pop(0)
        st.session_state.cards[2]["image_index"] = card_index
        st.session_state.cards[2]["pool"] = "legendary"

        # Record card in history
        if 0 <= card_index < len(st.session_state.legendary_filenames):
            card_name = st.session_state.legendary_filenames[card_index]
            drawn_cards.append({"name": card_name, "rarity": "legendary"})

            # Add to history
            card_entry = {
                "card_name": card_name,
                "rarity": "legendary",
                "credits": st.session_state.card_values["legendary"],
                "draw_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            st.session_state.card_history.append(card_entry)
            st.session_state.card_credits += st.session_state.card_values["legendary"]

            # Add to CSV
            with open(CARD_HISTORY_CSV, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        card_entry["card_name"],
                        card_entry["rarity"],
                        card_entry["credits"],
                        card_entry["draw_time"],
                    ]
                )
    else:
        st.warning("Issue with card pool for slot 3.")

    return True


# Function to convert PIL image to base64
def get_image_base64(img):
    import base64
    from io import BytesIO

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


# Function to create HTML for cards
def create_cards_html():
    html = ""
    for i, card in enumerate(st.session_state.cards):
        flipped_class = "flipped" if card["flipped"] else ""

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

        if card["image_index"] is not None and card["pool"] is not None:
            # Choose the image based on the pool
            if card["pool"] == "common" and 0 <= card["image_index"] < len(
                st.session_state.common_images
            ):
                front_img_b64 = get_image_base64(
                    st.session_state.common_images[card["image_index"]]
                )
                rarity_badge = '<div class="card-rarity common-card">Common</div>'
            elif card["pool"] == "rare" and 0 <= card["image_index"] < len(
                st.session_state.rare_images
            ):
                front_img_b64 = get_image_base64(
                    st.session_state.rare_images[card["image_index"]]
                )
                rarity_badge = '<div class="card-rarity rare-card">Rare</div>'
            elif card["pool"] == "legendary" and 0 <= card["image_index"] < len(
                st.session_state.legendary_images
            ):
                front_img_b64 = get_image_base64(
                    st.session_state.legendary_images[card["image_index"]]
                )
                rarity_badge = '<div class="card-rarity legendary-card">Legendary</div>'
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


# Function to purchase a reward
def purchase_reward(reward_id):
    for reward in st.session_state.rewards:
        if reward["id"] == reward_id:
            if st.session_state.card_credits >= reward["cost"]:
                # Confirm purchase
                if (
                    st.session_state.show_confirmation
                    and st.session_state.confirm_reward_id == reward_id
                ):
                    st.session_state.card_credits -= reward["cost"]
                    reward["purchased"] = True
                    st.session_state.purchased_rewards.append(
                        {
                            "name": reward["name"],
                            "cost": reward["cost"],
                            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )

                    # Update rewards CSV
                    with open(REWARDS_CSV, "r", newline="") as file:
                        reader = csv.reader(file)
                        rows = list(reader)

                    with open(REWARDS_CSV, "w", newline="") as file:
                        writer = csv.writer(file)
                        for row in rows:
                            if row[0] == str(reward_id):
                                row[3] = "True"  # Update purchased status
                            writer.writerow(row)

                    st.session_state.show_confirmation = False
                    st.session_state.confirm_reward_id = None
                    st.success(f"You have purchased {reward['name']}!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.session_state.show_confirmation = True
                    st.session_state.confirm_reward_id = reward_id
            else:
                st.warning(
                    f"Not enough credits! You need {reward['cost'] - st.session_state.card_credits} more credits."
                )


# Main application layout
if "show_confirmation" not in st.session_state:
    st.session_state.show_confirmation = False
if "confirm_reward_id" not in st.session_state:
    st.session_state.confirm_reward_id = None

# Sidebar with navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Main", "Profile", "Change for Credit", "Rewards"])

# Display card statistics in sidebar
common_count = len(glob.glob(os.path.join(COMMON_CARDS_PATH, "*.png")))
rare_count = len(glob.glob(os.path.join(RARE_CARDS_PATH, "*.png")))
legendary_count = len(glob.glob(os.path.join(LEGENDARY_CARDS_PATH, "*.png")))
total_cards = common_count + rare_count + legendary_count

st.sidebar.markdown("---")
st.sidebar.subheader("Card Information")
st.sidebar.write(f"Total cards loaded: {total_cards}")
st.sidebar.write(f"Common cards: {common_count}")
st.sidebar.write(f"Rare cards: {rare_count}")
st.sidebar.write(f"Legendary cards: {legendary_count}")

# Main page logic
if page == "Main":
    # Create a centered container for the title
    st.markdown('<div class="title-container">', unsafe_allow_html=True)
    st.title("E-Waste Recycling Card Drawing System")
    st.markdown("</div>", unsafe_allow_html=True)

    # Progress bar for points
    progress_percentage = min(100, (st.session_state.points % 100))
    st.progress(progress_percentage / 100)

    st.markdown(
        f"<h3 style='text-align:center;'>Points: {st.session_state.points} (Next draw at {(st.session_state.points // 100 + 1) * 100} points)</h3>",
        unsafe_allow_html=True,
    )

    # Card drawing area
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Draw button
    st.markdown('<div class="draw-button-container">', unsafe_allow_html=True)

    # Draw button with dynamic styling based on whether user can draw
    can_draw = can_draw_cards()
    button_type = "primary" if can_draw else "secondary"
    button_label = (
        "Draw Cards (100 points)"
        if can_draw
        else f"Need {100 - st.session_state.points} more points to draw"
    )

    draw_button = st.button(button_label, type=button_type, disabled=not can_draw)
    if draw_button:
        if st.session_state.common_images:
            success = draw_cards()
            if not success:
                st.error("You need at least 100 points to draw cards.")
        else:
            st.error("No card images loaded. Please check the image directories.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Display cards
    cards_container = st.empty()
    cards_container.markdown(create_cards_html(), unsafe_allow_html=True)

    # Flip cards with animation if draw was clicked
    if st.session_state.draw_clicked:
        for i in range(3):
            time.sleep(0.3)  # Add delay for sequential flipping
            st.session_state.cards[i]["flipped"] = True
            cards_container.markdown(create_cards_html(), unsafe_allow_html=True)

        # Reset flag after animation
        st.session_state.draw_clicked = False

    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Profile":
    st.title("Student Profile")

    # Student information
    st.subheader("Student Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Name:**", st.session_state.student_info["name"])
    with col2:
        st.write("**Student ID:**", st.session_state.student_info["id"])
    with col3:
        st.write("**Email:**", st.session_state.student_info["email"])

    st.markdown("---")

    # Recycling history
    st.subheader("Recycling History")
    if not st.session_state.recycled_items:
        st.info("No recycling history found.")
    else:
        # Convert to DataFrame for display
        df = pd.DataFrame(st.session_state.recycled_items)
        # Calculate total points
        total_points = df["points"].sum()

        # Display the table
        st.dataframe(df, use_container_width=True)
        st.markdown(f"**Total Points Earned from Recycling: {total_points}**")

    st.markdown("---")

    # Card collection
    st.subheader("Card Collection")
    if not st.session_state.card_history:
        st.info("No cards have been drawn yet. Go to the main page to draw cards!")
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
                    "total_credits": credits,
                }
                total_credits += credits
            else:
                history_data[card_name]["count"] += 1
                # Update total credits for this card
                history_data[card_name]["total_credits"] = (
                    history_data[card_name]["count"] * credits
                )
                total_credits += credits

        # Convert to list for table display
        table_data = []
        for card_name, data in history_data.items():
            table_data.append(
                {
                    "Card Name": data["name"],
                    "Rarity": data["rarity"].capitalize(),
                    "Times Drawn": data["count"],
                    "Credits per Card": data["credits"],
                    "Total Credits": data["total_credits"],
                }
            )

        # Display the table
        st.dataframe(pd.DataFrame(table_data), use_container_width=True)
        st.markdown(f"**Total Card Credits Earned: {total_credits}**")

elif page == "Change for Credit":
    st.title("Change for Credit")

    # Fake QR code display
    st.markdown('<div class="qr-container">', unsafe_allow_html=True)

    # Check if QR code image exists
    qr_path = "qr_code.png"
    try:
        if os.path.exists(qr_path):
            st.image(qr_path, width=300, caption="Scan this QR code")
        else:
            # Display a placeholder QR code
            st.markdown(
                """
            <div style="width: 300px; height: 300px; margin: 0 auto; background-color: #f0f0f0; 
                        display: flex; justify-content: center; align-items: center; 
                        border: 1px solid #ccc;">
                <p style="text-align: center;">QR Code Placeholder</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
    except Exception as e:
        st.error(f"Error displaying QR code: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Points input
    st.subheader("Add Points")

    col1, col2 = st.columns([3, 1])

    with col1:
        points_to_add = st.number_input("Enter points to add:", min_value=0, step=10)

    with col2:
        if st.button("Add Points"):
            if points_to_add > 0:
                st.session_state.points += points_to_add
                # Record this addition
                now = datetime.now().strftime("%Y-%m-%d")
                st.session_state.recycled_items.append(
                    {
                        "item": "Manual Addition",
                        "quantity": 1,
                        "points": points_to_add,
                        "date": now,
                    }
                )

                # Add to CSV
                with open(RECYCLED_ITEMS_CSV, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(["Manual Addition", 1, points_to_add, now])

                st.success(f"{points_to_add} points added successfully!")
                st.balloons()
            else:
                st.warning("Please enter a positive number of points to add.")

    # Current points display
    st.markdown(f"**Current total points: {st.session_state.points}**")

    # Progress towards next draw
    points_to_next_draw = 100 - (st.session_state.points % 100)
    if points_to_next_draw == 100:
        st.success(
            "You have enough points for a draw! Go to the main page to draw cards."
        )
    else:
        st.info(f"You need {points_to_next_draw} more points for your next card draw.")

elif page == "Rewards":
    st.title("Rewards")

    # Display current card credits
    st.markdown(
        f"""
    <div style="background-color: #4CAF50; color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
        <h2>Your Card Credits: {st.session_state.card_credits}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Card values information
    st.subheader("Card Values")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
        <div style="background-color: #aaa; color: white; padding: 10px; border-radius: 5px; text-align: center;">
            <h4>Common</h4>
            <p>5 credits per card</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
        <div style="background-color: #FFD700; color: black; padding: 10px; border-radius: 5px; text-align: center;">
            <h4>Rare</h4>
            <p>10 credits per card</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
        <div style="background-color: #FF4500; color: white; padding: 10px; border-radius: 5px; text-align: center;">
            <h4>Legendary</h4>
            <p>20 credits per card</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Available rewards
    st.subheader("Available Rewards")

    # Handle confirmation dialog if active
    if st.session_state.show_confirmation:
        reward = next(
            (
                r
                for r in st.session_state.rewards
                if r["id"] == st.session_state.confirm_reward_id
            ),
            None,
        )
        if reward:
            with st.container():
                st.warning(
                    f"Confirm purchase of {reward['name']} for {reward['cost']} credits?"
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Purchase"):
                        purchase_reward(st.session_state.confirm_reward_id)
                with col2:
                    if st.button("Cancel"):
                        st.session_state.show_confirmation = False
                        st.session_state.confirm_reward_id = None
                        st.rerun()

    # Display rewards in a 3-column grid
    rewards_per_row = 3
    for i in range(0, len(st.session_state.rewards), rewards_per_row):
        cols = st.columns(rewards_per_row)
        for j in range(rewards_per_row):
            if i + j < len(st.session_state.rewards):
                reward = st.session_state.rewards[i + j]
                with cols[j]:
                    disabled = (
                        reward["purchased"]
                        or st.session_state.card_credits < reward["cost"]
                    )

                    # Create reward card with conditional styling
                    if reward["purchased"]:
                        st.markdown(
                            f"""
                        <div class="reward-card reward-disabled">
                            <h3>{reward["name"]}</h3>
                            <p>{reward["cost"]} credits</p>
                            <p><b>PURCHASED</b></p>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"""
                        <div class="reward-card">
                            <h3>{reward["name"]}</h3>
                            <p>{reward["cost"]} credits</p>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                        # Purchase button
                        st.button(
                            "Purchase",
                            key=f"buy_{reward['id']}",
                            on_click=purchase_reward,
                            args=(reward["id"],),
                            disabled=disabled,
                        )

                        if st.session_state.card_credits < reward["cost"]:
                            st.caption(
                                f"Need {reward['cost'] - st.session_state.card_credits} more credits"
                            )

    st.markdown("---")

    # Purchased rewards history
    if st.session_state.purchased_rewards:
        st.subheader("Purchase History")
        purchase_df = pd.DataFrame(st.session_state.purchased_rewards)
        st.dataframe(purchase_df, use_container_width=True)
