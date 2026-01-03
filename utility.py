""" Size """
ROWS = 4
COLS = 5

""" Player """
RED = 1
YELLOW = -1
EMPTY = 0

""" AI """
AI_PLAYER1 = 1
AI_PLAYER2 = -1
AI_PLAYER1_DEPTH = 8
AI_PLAYER2_DEPTH = 4

def check_direction(board, start_r, start_c, dr, dc, player, rows, cols):
    """Count consecutive pieces in a given direction"""
    count = 0
    r, c = start_r, start_c
    while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
        count += 1
        r += dr
        c += dc
    return count