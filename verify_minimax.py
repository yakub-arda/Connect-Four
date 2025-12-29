"""
Minimax verification tool - helps debug minimax behavior
"""
from board import Board
from minimax import minimax, best_move, evaluate
from utility import RED, YELLOW

def verify_symmetry():
    """Test if minimax treats both players symmetrically"""
    board = Board()

    # Test from empty board
    print("=== SYMMETRY TEST ===")
    print("Empty board evaluation:", evaluate(board))

    # RED's first move from empty board
    print("\nRED's view (minimizing):")
    for col in board.valid_moves():
        board.make_move(col, RED)
        score = minimax(board, 3, True)  # YELLOW's turn next
        board.undo_move(col)
        print(f"  Column {col}: score = {score}")

    # Now test if YELLOW went first (swap the scenario)
    print("\nIf YELLOW went first (maximizing):")
    for col in board.valid_moves():
        board.make_move(col, YELLOW)
        score = minimax(board, 3, False)  # RED's turn next
        board.undo_move(col)
        print(f"  Column {col}: score = {score}")

    print("\nIf scores are negations of each other, the game is symmetric.")
    print("If not, there's a bug in the minimax implementation.")

def trace_game(depth_red, depth_yellow, max_moves=25):
    """Play a game and show the minimax scores at each step"""
    board = Board()
    turn = RED
    move_num = 0

    print(f"\n=== GAME TRACE: RED depth={depth_red}, YELLOW depth={depth_yellow} ===")

    while move_num < max_moves:
        if board.check_win(RED):
            print(f"\n🔴 RED WINS after {move_num} moves")
            return "RED"
        if board.check_win(YELLOW):
            print(f"\n🟡 YELLOW WINS after {move_num} moves")
            return "YELLOW"
        if not board.valid_moves():
            print(f"\n⚪ DRAW after {move_num} moves (board full)")
            return "DRAW"

        # Get move
        if turn == RED:
            depth = depth_red
            col = best_move(board, depth, RED)
            player_name = "RED"
        else:
            depth = depth_yellow
            col = best_move(board, depth, YELLOW)
            player_name = "YELLOW"

        if move_num < 5 or move_num > max_moves - 5:  # Only show early and late game
            # Calculate scores for all moves to see alternatives
            print(f"\nMove {move_num + 1} - {player_name}'s turn (depth {depth}):")
            for c in board.valid_moves():
                board.make_move(c, turn)
                if turn == RED:
                    score = minimax(board, depth - 1, True)
                else:
                    score = minimax(board, depth - 1, False)
                board.undo_move(c)

                marker = " <-- CHOSEN" if c == col else ""
                print(f"  Column {c}: score = {score}{marker}")
        elif move_num == 5:
            print(f"\n... (moves 6-{max_moves-4} hidden for brevity) ...")

        # Make the move
        board.make_move(col, turn)
        move_num += 1

        # Switch turns
        turn = YELLOW if turn == RED else RED

    # Show final board
    print(f"\nFinal board after {max_moves} moves:")
    for row in range(4):
        print("  ", end="")
        for col_idx in range(5):
            cell = board.grid[row][col_idx]
            if cell == RED:
                print("R ", end="")
            elif cell == YELLOW:
                print("Y ", end="")
            else:
                print(". ", end="")
        print()

    print(f"\nGame exceeded {max_moves} moves - likely a theoretical draw")
    return "TIMEOUT"

def test_specific_position():
    """Test a specific known position to verify minimax"""
    board = Board()

    print("\n=== SPECIFIC POSITION TEST ===")
    print("Testing if minimax detects immediate wins/losses")

    # Create a position where YELLOW can win in 1 move
    # R . . . .
    # R . . . .
    # R . Y Y Y
    # R . . . .
    board.make_move(0, RED)
    board.make_move(0, RED)
    board.make_move(0, RED)
    board.make_move(0, RED)

    board.make_move(2, YELLOW)
    board.make_move(3, YELLOW)
    board.make_move(4, YELLOW)

    print("\nBoard state:")
    for row in range(4):
        print("  ", end="")
        for col in range(5):
            cell = board.grid[row][col]
            if cell == RED:
                print("R ", end="")
            elif cell == YELLOW:
                print("Y ", end="")
            else:
                print(". ", end="")
        print()

    print("\nYELLOW to move. Column 1 wins immediately.")
    print("Minimax scores (depth 2):")
    for col in board.valid_moves():
        board.make_move(col, YELLOW)
        score = minimax(board, 2, False)
        board.undo_move(col)
        print(f"  Column {col}: {score}")

    best_col = best_move(board, 2, YELLOW)
    print(f"\nBest move chosen: Column {best_col}")
    print(f"Expected: Column 1 (should be ~1,000,000)")

if __name__ == "__main__":
    print("MINIMAX VERIFICATION TOOL")
    print("=" * 50)

    # Run tests
    verify_symmetry()
    test_specific_position()

    # Trace games at different depth matchups
    print("\n" + "=" * 50)
    result_1v1 = trace_game(depth_red=1, depth_yellow=1, max_moves=25)

    print("\n" + "=" * 50)
    result_2v2 = trace_game(depth_red=2, depth_yellow=2, max_moves=25)

    print("\n" + "=" * 50)
    result_4v2 = trace_game(depth_red=4, depth_yellow=2, max_moves=25)

    print("\n" + "=" * 50)
    result_2v4 = trace_game(depth_red=2, depth_yellow=4, max_moves=25)

    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  1v1: {result_1v1}")
    print(f"  2v2: {result_2v2}")
    print(f"  4v2 (higher depth RED): {result_4v2}")
    print(f"  2v4 (higher depth YELLOW): {result_2v4}")
    print()
    if result_4v2 in ["RED", "DRAW"] and result_2v4 in ["YELLOW", "DRAW"]:
        print("✅ MINIMAX IS WORKING: Higher depth wins or draws")
    else:
        print("❌ PROBLEM: Lower depth is winning")

    # The key insight
    if result_1v1 == result_2v2 == result_4v2 == result_2v4:
        print("\n💡 All games have same outcome - this suggests:")
        print("   5x4 Connect Four is likely a theoretical DRAW with perfect play")
        print("   (Similar to 3x3 Tic-Tac-Toe)")