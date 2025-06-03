import streamlit as st
import numpy as np
import random

st.set_page_config(page_title="2048 Game", layout="centered")

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    .stApp {
        background-color: #faf8ef;
        font-family: Arial, sans-serif;
    }
    .main-header {
        text-align: center;
        color: #776e65;
        font-size: 3em;
        margin-bottom: 20px;
    }
    .score-container {
        text-align: center;
        margin-bottom: 30px;
        font-size: 1.5em;
        color: #776e65;
        font-weight: bold;
    }
    table {
        border-collapse: collapse;
        margin: 0 auto;
        background-color: #bbada0;
        border-radius: 6px;
    }
    td {
        width: 100px;
        height: 100px;
        text-align: center;
        vertical-align: middle;
        font-size: 36px;
        font-weight: bold;
        border-radius: 3px;
        margin: 5px; /* Spacing between cells */
        color: #776e65;
    }
    /* Tile Colors */
    .tile-0 { background-color: #eee4da; }
    .tile-2 { background-color: #eee4da; color: #776e65; }
    .tile-4 { background-color: #ede0c8; color: #776e65; }
    .tile-8 { background-color: #f2b179; color: #f9f6f2; }
    .tile-16 { background-color: #f59563; color: #f9f6f2; }
    .tile-32 { background-color: #f67c5f; color: #f9f6f2; }
    .tile-64 { background-color: #f65e3b; color: #f9f6f2; }
    .tile-128 { background-color: #edcf72; color: #f9f6f2; }
    .tile-256 { background-color: #edcc61; color: #f9f6f2; }
    .tile-512 { background-color: #edc850; color: #f9f6f2; }
    .tile-1024 { background-color: #edc53f; color: #f9f6f2; }
    .tile-2048 { background-color: #edc22e; color: #f9f6f2; }
    /* Larger tiles for higher values (adjust font size if needed) */
    .tile-128, .tile-256, .tile-512, .tile-1024, .tile-2048 {
        font-size: 32px;
    }
    /* Buttons */
    .stButton>button {
        background-color: #8f7a66;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-size: 1.2em;
        margin: 5px;
        cursor: pointer;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #9f8b7b;
    }
    .control-buttons {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: 20px;
    }
    .reset-button-container {
        text-align: center;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Game Logic Functions (defined BEFORE initial state setup) ---
def add_random_tile():
    empty_cells = list(zip(*np.where(st.session_state.board == 0)))
    if empty_cells:
        x, y = random.choice(empty_cells)
        st.session_state.board[x, y] = 2 if random.random() < 0.9 else 4

def reset_game():
    st.session_state.board = np.zeros((4, 4), dtype=int)
    st.session_state.score = 0
    add_random_tile()
    add_random_tile()

def compress(board):
    new_board = np.zeros_like(board)
    moved = False
    for i in range(4):
        pos = 0
        for j in range(4):
            if board[i, j] != 0:
                if new_board[i, pos] != board[i, j]: # Check if actual move happened
                    if new_board[i,pos] != 0 or pos != j: # Check if there is existing cell that can be moved into or if current position is different
                        moved = True
                new_board[i, pos] = board[i, j]
                pos += 1
    if not np.array_equal(board, new_board):
        moved = True
    return new_board, moved

def merge(board):
    merged = False
    for i in range(4):
        for j in range(3):
            if board[i, j] != 0 and board[i, j] == board[i, j+1]:
                board[i, j] *= 2
                st.session_state.score += board[i, j]
                board[i, j+1] = 0
                merged = True
    return board, merged

def is_game_over():
    # Check for empty cells
    if np.any(st.session_state.board == 0):
        return False

    # Check for possible merges horizontally
    for i in range(4):
        for j in range(3):
            if st.session_state.board[i, j] == st.session_state.board[i, j+1]:
                return False
    # Check for possible merges vertically
    for j in range(4):
        for i in range(3):
            if st.session_state.board[i, j] == st.session_state.board[i+1, j]:
                return False
    return True

def move_left():
    old_board = st.session_state.board.copy()
    
    board = st.session_state.board.copy()
    
    # Compress
    board, moved_compress = compress(board)
    
    # Merge
    board, merged_tiles = merge(board)
    
    # Compress again after merge
    board, moved_after_merge_compress = compress(board)
    
    st.session_state.board = board
    
    if not np.array_equal(old_board, st.session_state.board):
        add_random_tile()


def move_right():
    old_board = st.session_state.board.copy()
    st.session_state.board = np.fliplr(st.session_state.board)
    move_left() # This now internally calls add_random_tile if board changed
    st.session_state.board = np.fliplr(st.session_state.board)
    if np.array_equal(old_board, st.session_state.board): # If no overall change, remove tile added by internal move_left
        pass # The logic in move_left now handles add_random_tile correctly

def move_up():
    old_board = st.session_state.board.copy()
    st.session_state.board = st.session_state.board.T
    move_left() # This now internally calls add_random_tile if board changed
    st.session_state.board = st.session_state.board.T
    if np.array_equal(old_board, st.session_state.board): # If no overall change, remove tile added by internal move_left
        pass

def move_down():
    old_board = st.session_state.board.copy()
    st.session_state.board = st.session_state.board.T
    move_right() # This now internally calls add_random_tile if board changed
    st.session_state.board = st.session_state.board.T
    if np.array_equal(old_board, st.session_state.board): # If no overall change, remove tile added by internal move_right
        pass

# --- Initialize Game State ---
if "board" not in st.session_state:
    st.session_state.board = np.zeros((4, 4), dtype=int)
    st.session_state.score = 0
    # Add initial tiles only on first load
    add_random_tile()
    add_random_tile()

# --- Display Board ---
def draw_board():
    st.markdown(f'<div class="score-container">Score: {st.session_state.score}</div>', unsafe_allow_html=True)
    board_html = "<table>"
    for row in st.session_state.board:
        board_html += "<tr>"
        for val in row:
            # Assign a CSS class based on the tile value
            tile_class = f"tile-{val}"
            board_html += f'<td class="{tile_class}">{val if val != 0 else ""}</td>'
        board_html += "</tr>"
    board_html += "</table>"
    st.markdown(board_html, unsafe_allow_html=True)

# --- Controls ---
st.markdown('<div class="main-header">2048</div>', unsafe_allow_html=True)
draw_board()

# Check for game over condition
if is_game_over():
    st.error("### Game Over! No more moves.")

# Controls for movement
col1, col2, col3 = st.columns([1, 2, 1]) # Adjust column ratios for better button placement

with col2: # Central column for up/down/reset
    st.button("⬆️", on_click=move_up, use_container_width=True)

col_left, col_center, col_right = st.columns([1, 1, 1])
with col_left:
    st.button("⬅️", on_click=move_left, use_container_width=True)
with col_center:
    st.button("🔄 Reset", on_click=reset_game, use_container_width=True)
with col_right:
    st.button("➡️", on_click=move_right, use_container_width=True)

with col2: # Central column for up/down/reset
    st.button("⬇️", on_click=move_down, use_container_width=True)