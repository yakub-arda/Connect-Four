import math
from utility import check_direction, ROWS, COLS, RED, YELLOW


def evaluate(board):
    """
    Evaluation function: Returns a score for the current board position.

    Positive score = good for YELLOW (maximizing player)
    Negative score = good for RED (minimizing player)

    The function counts sequences of pieces to determine board strength:
    - 4 in a row = win condition (very high score)
    - 3 in a row with 1 empty = strong position
    - 2 in a row with 2 empty = developing position
    """
    score = 0

    # Check all possible 4-cell windows on the board
    # Horizontal windows (check each row)
    for r in range(ROWS):
        for c in range(COLS - 3):  # Only check where 4 cells fit horizontally
            window = [board.grid[r][c], board.grid[r][c + 1], board.grid[r][c + 2], board.grid[r][c + 3]]
            score += evaluate_window(window)

    # Vertical windows (check each column)
    for c in range(COLS):
        for r in range(ROWS - 3):  # Only check where 4 cells fit vertically
            window = [board.grid[r][c], board.grid[r + 1][c], board.grid[r + 2][c], board.grid[r + 3][c]]
            score += evaluate_window(window)

    # Diagonal windows (top-left to bottom-right)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board.grid[r][c], board.grid[r + 1][c + 1], board.grid[r + 2][c + 2], board.grid[r + 3][c + 3]]
            score += evaluate_window(window)

    # Diagonal windows (top-right to bottom-left)
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            window = [board.grid[r][c], board.grid[r + 1][c - 1], board.grid[r + 2][c - 2], board.grid[r + 3][c - 3]]
            score += evaluate_window(window)

    return score


def evaluate_window(window):
    """
    Evaluates a single 4-cell window and returns its score.

    Scoring system:
    - 4 YELLOW pieces = +100 (YELLOW wins)
    - 3 YELLOW + 1 empty = +5 (strong offensive position)
    - 2 YELLOW + 2 empty = +2 (developing position)

    - 4 RED pieces = -100 (RED wins)
    - 3 RED + 1 empty = -5 (strong offensive position)
    - 2 RED + 2 empty = -2 (developing position)

    - Mixed pieces or blocked = 0 (no value)
    """
    score = 0

    # Count how many of each type in this window
    yellow_count = window.count(YELLOW)  # Count YELLOW pieces
    red_count = window.count(RED)  # Count RED pieces
    empty_count = window.count(0)  # Count empty spaces

    # Evaluate for YELLOW (positive scores)
    if yellow_count == 4:
        score += 100  # Four in a row - winning position
    elif yellow_count == 3 and empty_count == 1:
        score += 5  # Three in a row with space to complete - very good
    elif yellow_count == 2 and empty_count == 2:
        score += 2  # Two in a row with space to develop - good

    # Evaluate for RED (negative scores)
    if red_count == 4:
        score -= 100  # Four in a row - winning position
    elif red_count == 3 and empty_count == 1:
        score -= 5  # Three in a row with space to complete - very good
    elif red_count == 2 and empty_count == 2:
        score -= 2  # Two in a row with space to develop - good

    # If window has both colors, it's blocked and worthless (score stays 0)

    return score


def minimax(board, depth, maximizing):
    """
    Minimax algorithm: Recursively searches the game tree to find the best move.

    Parameters:
    - board: Current game state
    - depth: How many moves ahead to look (search depth)
    - maximizing: True if YELLOW's turn (wants high score), False if RED's turn (wants low score)

    Returns: The best score achievable from this position
    """

    # Base case 1: Check if YELLOW won
    if board.check_win(YELLOW):
        return 10000 + depth  # Return high score (good for YELLOW). Add depth to prefer faster wins

    # Base case 2: Check if RED won
    if board.check_win(RED):
        return -10000 - depth  # Return low score (good for RED). Subtract depth to prefer faster wins

    # Base case 3: Get all valid moves (columns that aren't full)
    moves = board.valid_moves()

    # If we've reached the depth limit or no moves left, evaluate the position
    if depth == 0 or not moves:
        return evaluate(board)  # Return heuristic score of current position

    # Recursive case: Try all possible moves
    if maximizing:
        # YELLOW's turn: wants to maximize the score
        best_score = -math.inf  # Start with worst possible score for maximizer

        # Try each valid column
        for col in moves:
            board.make_move(col, YELLOW)  # Make the move
            score = minimax(board, depth - 1, False)  # Recursively evaluate (now RED's turn)
            board.undo_move(col)  # Undo the move to try next option
            best_score = max(best_score, score)  # Keep the highest score found

        return best_score  # Return the best score YELLOW can achieve

    else:
        # RED's turn: wants to minimize the score
        best_score = math.inf  # Start with worst possible score for minimizer

        # Try each valid column
        for col in moves:
            board.make_move(col, RED)  # Make the move
            score = minimax(board, depth - 1, True)  # Recursively evaluate (now YELLOW's turn)
            board.undo_move(col)  # Undo the move to try next option
            best_score = min(best_score, score)  # Keep the lowest score found

        return best_score  # Return the best score RED can achieve


def best_move(board, depth, player):
    """
    Finds the best column to play for the given player.

    This function calls minimax for each possible move and picks the one
    with the best score for the current player.
    """
    if player == YELLOW:
        # YELLOW wants to maximize score
        best_score = -math.inf  # Start with worst possible score
        best_col = None

        # Try each valid column
        for col in board.valid_moves():
            board.make_move(col, YELLOW)  # Try this move
            score = minimax(board, depth - 1, False)  # See what score it leads to
            board.undo_move(col)  # Undo the move

            # If this move is better than previous best, remember it
            if score > best_score:
                best_score = score
                best_col = col

    else:  # RED
        # RED wants to minimize score
        best_score = math.inf  # Start with worst possible score
        best_col = None

        # Try each valid column
        for col in board.valid_moves():
            board.make_move(col, RED)  # Try this move
            score = minimax(board, depth - 1, True)  # See what score it leads to
            board.undo_move(col)  # Undo the move

            # If this move is better than previous best, remember it
            if score < best_score:
                best_score = score
                best_col = col

    return best_col  # Return the column number of the best move