import math
from utility import ROWS, COLS, RED, YELLOW, EMPTY

WIN_SCORE = 10000

transposition_table = {}


def board_to_key(board):
    """Convert board to a hashable key for caching."""
    return tuple(tuple(row) for row in board.grid)


def evaluate_window(window, piece):
    score = 0
    opponent = RED if piece == YELLOW else YELLOW

    if window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 400
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 20
    elif window.count(piece) == 1 and window.count(EMPTY) == 3:
        score += 1

    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= 350

    return score


def evaluate(board):
    if board.check_win(RED):
        return WIN_SCORE
    elif board.check_win(YELLOW):
        return -WIN_SCORE
    elif board.is_full():
        return 0

    score = 0

    for r in range(ROWS):
        row_array = [board.grid[r][c] for c in range(COLS)]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, RED)

    for c in range(COLS):
        col_array = [board.grid[r][c] for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, RED)

    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board.grid[r - i][c + i] for i in range(4)]
            score += evaluate_window(window, RED)

    for r in range(3, ROWS):
        for c in range(3, COLS):
            window = [board.grid[r - i][c - i] for i in range(4)]
            score += evaluate_window(window, RED)

    return score


def minimax(board, depth, maximizing_player):
    """
    Minimax with transposition table optimization.
    """
    if board.check_win(RED) or board.check_win(YELLOW) or board.is_full():
        return evaluate(board)

    if depth == 0:
        return evaluate(board)

    board_key = board_to_key(board)
    cache_key = (board_key, depth, maximizing_player)

    if cache_key in transposition_table:
        return transposition_table[cache_key]

    if maximizing_player:
        max_eval = -math.inf
        for col in board.valid_moves():
            board.make_move(col, RED)
            eval = minimax(board, depth - 1, False)
            board.undo_move(col)
            max_eval = max(max_eval, eval)

        transposition_table[cache_key] = max_eval
        return max_eval
    else:
        min_eval = math.inf
        for col in board.valid_moves():
            board.make_move(col, YELLOW)
            eval = minimax(board, depth - 1, True)
            board.undo_move(col)
            min_eval = min(min_eval, eval)

        transposition_table[cache_key] = min_eval
        return min_eval


def best_move(board, depth, player):
    """
    Find the best move for the given player.
    Prioritizes center columns when scores are equal: 2, 1, 3, 0, 4
    """
    valid_moves = board.valid_moves()
    column_priority = [2, 1, 3, 0, 4]

    sorted_moves = [col for col in column_priority if col in valid_moves]

    if player == RED:
        best_score = -math.inf
        best_col = sorted_moves[0]

        for col in sorted_moves:
            board.make_move(col, RED)
            score = minimax(board, depth - 1, False)
            board.undo_move(col)

            if score > best_score:
                best_score = score
                best_col = col

        return best_col

    else:
        best_score = math.inf
        best_col = sorted_moves[0]

        for col in sorted_moves:
            board.make_move(col, YELLOW)
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