import streamlit as st
import numpy as np

st.set_page_config(page_title="Minesweeper", layout="centered")

# -----------------------------
# Helpers
# -----------------------------
def generate_board(rows, cols, mines):
    board = np.zeros((rows, cols), dtype=int)
    mine_positions = set()

    # Place mines
    while len(mine_positions) < mines:
        r = np.random.randint(rows)
        c = np.random.randint(cols)
        mine_positions.add((r, c))

    for (r, c) in mine_positions:
        board[r, c] = -1

    # Calculate numbers
    for r in range(rows):
        for c in range(cols):
            if board[r, c] == -1:
                continue
            neighbors = [
                (r+i, c+j)
                for i in (-1, 0, 1)
                for j in (-1, 0, 1)
                if 0 <= r+i < rows and 0 <= c+j < cols and not (i == 0 and j == 0)
            ]
            board[r, c] = sum(board[nr, nc] == -1 for nr, nc in neighbors)

    return board


def reveal_cell(visible, r, c, board):
    """Flood-fill reveal."""
    if visible[r][c] != " ":
        return

    visible[r][c] = str(board[r][c]) if board[r][c] != 0 else ""

    if board[r][c] == 0:
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                nr, nc = r+i, c+j
                if 0 <= nr < visible.shape[0] and 0 <= nc < visible.shape[1]:
                    if visible[nr][nc] == " ":
                        reveal_cell(visible, nr, nc, board)


# -----------------------------
# App State
# -----------------------------
if "board" not in st.session_state:
    st.session_state.rows = 8
    st.session_state.cols = 8
    st.session_state.mines = 10
    st.session_state.board = generate_board(8, 8, 10)
    st.session_state.visible = np.array([[" "] * 8 for _ in range(8)])
    st.session_state.game_over = False
    st.session_state.win = False


# -----------------------------
# Sidebar Settings
# -----------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    rows = st.number_input("Rows", 5, 20, st.session_state.rows)
    cols = st.number_input("Cols", 5, 20, st.session_state.cols)
    mines = st.number_input("Mines", 1, 200, st.session_state.mines)

    if st.button("New Game"):
        st.session_state.rows = rows
        st.session_state.cols = cols
        st.session_state.mines = mines
        st.session_state.board = generate_board(rows, cols, mines)
        st.session_state.visible = np.array([[" "] * cols for _ in range(rows)])
        st.session_state.game_over = False
        st.session_state.win = False
        st.experimental_rerun()


# -----------------------------
# Game UI
# -----------------------------
st.title("💣 Minesweeper")

if st.session_state.game_over:
    st.error("💥 You hit a mine!")
elif st.session_state.win:
    st.success("🎉 You win! All safe cells uncovered.")


# Render grid
for r in range(st.session_state.rows):
    cols_ui = st.columns(st.session_state.cols)
    for c in range(st.session_state.cols):
        cell_val = st.session_state.visible[r][c]

        if cell_val == " " and not st.session_state.game_over:
            if cols_ui[c].button(" ", key=f"{r}-{c}"):
                if st.session_state.board[r][c] == -1:
                    # Mine hit
                    st.session_state.game_over = True
                    st.session_state.visible = np.where(
                        st.session_state.board == -1, "X", st.session_state.visible
                    )
                else:
                    reveal_cell(
                        st.session_state.visible, r, c, st.session_state.board
                    )
                st.experimental_rerun()
        else:
            # Show revealed cell
            style = (
                "background-color:#ff4d4d;color:white;"
                if cell_val == "X"
                else "background-color:#e0e0e0;"
            )
            cols_ui[c].markdown(
                f"<div style='text-align:center;padding:8px;{style}'>{cell_val}</div>",
                unsafe_allow_html=True,
            )

# Check win
if not st.session_state.game_over:
    unrevealed = (st.session_state.visible == " ").sum()
    if unrevealed == st.session_state.mines:
        st.session_state.win = True
        st.session_state.visible = np.where(
            st.session_state.board == -1, "X", st.session_state.visible
        )
        st.experimental_rerun()
