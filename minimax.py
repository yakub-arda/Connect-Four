import math
from utility import ROWS, COLS, RED, YELLOW, EMPTY

WIN_SCORE = 100000

# Transposition table for memoization
transposition_table = {}


def board_to_key(board):
    """Convert board to a hashable key for caching."""
    return tuple(tuple(row) for row in board.grid)


def get_playable_row(board, col):
    """Find the row where a piece would land in the given column."""
    for r in range(ROWS - 1, -1, -1):
        if board.grid[r][col] == EMPTY:
            return r
    return None


def find_windows_from_cell(r, c):
    """Find all 4-cell windows that include the given cell."""
    windows = []

    directions = [
        (0, 1),  # horizontal
        (1, 0),  # vertical
        (1, 1),  # diagonal \
        (1, -1),  # diagonal /
    ]

    for dr, dc in directions:
        for offset in range(-3, 1):
            window = []
            for i in range(4):
                rr = r + (offset + i) * dr
                cc = c + (offset + i) * dc
                if 0 <= rr < ROWS and 0 <= cc < COLS:
                    window.append((rr, cc))
                else:
                    break
            if len(window) == 4:
                windows.append(window)

    return windows


def evaluate(board):
    """
    Original evaluation function - checks windows from playable positions.
    """
    if board.check_win(YELLOW):
        return WIN_SCORE
    if board.check_win(RED):
        return -WIN_SCORE

    score = 0

    for col in range(COLS):
        row = get_playable_row(board, col)
        if row is None:
            continue

        windows = find_windows_from_cell(row, col)

        for window in windows:
            vals = [board.grid[r][c] for r, c in window]

            y = vals.count(YELLOW)
            r = vals.count(RED)
            e = vals.count(EMPTY)

            # mixed window → useless
            if y > 0 and r > 0:
                continue

            # 1 & 2 — Win / Block
            if e == 1:
                if y == 3:
                    score += 20000
                elif r == 3:
                    score -= 10000

            # 3 — Attack (2 → 3)
            elif e == 2:
                if y == 2:
                    score += 2000
                elif r == 2:
                    score -= 1000

            # 4 — Expand (1 → 2)
            elif e == 3:
                if y == 1:
                    score += 100
                elif r == 1:
                    score -= 50

            # 5 — Search
            elif e == 4:
                score += 5

    return score


def minimax(board, depth, maximizingPlayer):
    """
    Minimax with transposition table optimization.
    Caches already-computed positions for speed.
    """
    # Check for terminal states
    if board.check_win(YELLOW):
        return WIN_SCORE - depth  # FIX: Prefer faster wins
    if board.check_win(RED):
        return -WIN_SCORE + depth  # FIX: Prefer slower losses

    moves = board.valid_moves()

    if not moves:
        return 0  # Draw

    if depth == 0:
        return evaluate(board)

    # Check transposition table
    board_key = board_to_key(board)
    cache_key = (board_key, depth, maximizingPlayer)

    if cache_key in transposition_table:
        return transposition_table[cache_key]

    # Recursive minimax
    if maximizingPlayer:
        value = -math.inf
        for col in moves:
            board.make_move(col, YELLOW)
            value = max(value, minimax(board, depth - 1, False))
            board.undo_move(col)

        transposition_table[cache_key] = value
        return value
    else:
        value = math.inf
        for col in moves:
            board.make_move(col, RED)
            value = min(value, minimax(board, depth - 1, True))
            board.undo_move(col)

        transposition_table[cache_key] = value
        return value


def best_move(board, depth, player):
    """
    Find the best move for the given player.
    """
    valid_moves = board.valid_moves()

    if player == YELLOW:
        best_score = -math.inf
        best_col = valid_moves[0]  # Always have a default

        for col in valid_moves:
            board.make_move(col, YELLOW)
            score = minimax(board, depth - 1, False)
            board.undo_move(col)

            if score > best_score:
                best_score = score
                best_col = col

        return best_col

    else:  # RED
        best_score = math.inf
        best_col = valid_moves[0]  # Always have a default

        for col in valid_moves:
            board.make_move(col, RED)
            score = minimax(board, depth - 1, True)
            board.undo_move(col)

            if score < best_score:
                best_score = score
                best_col = col

        return best_col


def clear_cache():
    """Clear the transposition table (call between games)."""
    global transposition_table
    transposition_table = {}