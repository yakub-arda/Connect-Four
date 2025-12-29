import pygame
from board import Board
from minimax import best_move
from utility import RED, YELLOW, AI_PLAYER1, AI_PLAYER2, AI_PLAYER1_DEPTH, AI_PLAYER2_DEPTH


class ConnectFour:
    def __init__(self):
        pygame.init()
        # Window size: 5 columns x 100px = 500, 4 rows x 100px = 400, plus 150px for buttons/messages
        self.screen = pygame.display.set_mode((500, 550))
        pygame.display.set_caption("5x4 Connect Four")

        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        self.board = Board()
        self.turn = RED
        self.game_over = False
        self.winner = None
        self.ai_thinking = False

        # History tracking for previous/next functionality
        self.history = [self.board.copy()]  # Start with empty board
        self.current_state_index = 0
        self.viewing_history = False

    def show_tree_visualization(self):
        """Open tree visualization in a separate window"""
        from tree_visualizer import TreeVisualizer

        # Determine the board state being viewed
        board_state = self.history[self.current_state_index]

        # FIX: Check whose turn it was at this historical point
        # Index 0 = Start (Red's turn), Index 1 = After 1 move (Yellow's turn)
        if self.current_state_index % 2 == 0:
            eval_player = RED
            depth = AI_PLAYER1_DEPTH
        else:
            eval_player = YELLOW
            depth = AI_PLAYER2_DEPTH

        # Pass board, depth (6), and correct player
        visualizer = TreeVisualizer(board_state, depth, eval_player)
        visualizer.run()

        # Restore main window
        self.screen = pygame.display.set_mode((500, 550))
        pygame.display.set_caption("5x4 Connect Four")

    def run(self):
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.__init__()  # Reset game
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    # Check if previous button clicked (left side)
                    if 50 <= mouse_x <= 150 and 460 <= mouse_y <= 510:
                        if self.current_state_index > 0:
                            self.current_state_index -= 1
                            self.viewing_history = True
                    # Check if show button clicked (middle)
                    elif 200 <= mouse_x <= 300 and 460 <= mouse_y <= 510:
                        self.show_tree_visualization()
                    # Check if next button clicked (right side)
                    elif 350 <= mouse_x <= 450 and 460 <= mouse_y <= 510:
                        if self.current_state_index < len(self.history) - 1:
                            self.current_state_index += 1
                            self.viewing_history = self.current_state_index < len(self.history) - 1

            # Only progress game if not viewing history and game not over
            if not self.game_over and not self.ai_thinking and not self.viewing_history:
                self.ai_thinking = True

                # Determine which depth to use based on current player
                if self.turn == AI_PLAYER1:
                    depth = AI_PLAYER1_DEPTH
                else:
                    depth = AI_PLAYER2_DEPTH

                col = best_move(self.board, depth, self.turn)

                if col is not None:
                    self.board.make_move(col, self.turn)
                    # Save state to history
                    self.history.append(self.board.copy())
                    self.current_state_index = len(self.history) - 1

                    # Check for win
                    if self.board.check_win(self.turn):
                        self.game_over = True
                        self.winner = self.turn
                    elif self.board.is_full():
                        self.game_over = True
                        self.winner = None  # Draw
                    else:
                        # Switch turns
                        self.turn = YELLOW if self.turn == RED else RED

                self.ai_thinking = False

            # Draw everything
            self.screen.fill((25, 25, 25))

            # Draw the board state (current or from history)
            board_to_draw = self.history[self.current_state_index] if self.viewing_history else self.board
            board_to_draw.draw(self.screen)

            # Draw game over message
            if self.game_over and self.current_state_index == len(self.history) - 1:
                if self.winner == RED:
                    text = self.font.render("RED WINS!", True, (255, 100, 100))
                elif self.winner == YELLOW:
                    text = self.font.render("YELLOW WINS!", True, (255, 255, 100))
                else:
                    text = self.font.render("DRAW!", True, (200, 200, 200))

                text_rect = text.get_rect(center=(250, 420))
                self.screen.blit(text, text_rect)

                # Show reset instruction
                reset_text = self.small_font.render("Press R to restart", True, (150, 150, 150))
                reset_rect = reset_text.get_rect(center=(250, 445))
                self.screen.blit(reset_text, reset_rect)

            # Draw Previous/Show/Next buttons
            # Previous button
            prev_color = (70, 70, 70) if self.current_state_index > 0 else (40, 40, 40)
            pygame.draw.rect(self.screen, prev_color, (50, 460, 100, 50))
            pygame.draw.rect(self.screen, (150, 150, 150), (50, 460, 100, 50), 2)
            prev_text = self.small_font.render("< Prev", True, (200, 200, 200))
            prev_rect = prev_text.get_rect(center=(100, 485))
            self.screen.blit(prev_text, prev_rect)

            # Show button (middle)
            show_color = (50, 100, 150)
            pygame.draw.rect(self.screen, show_color, (200, 460, 100, 50))
            pygame.draw.rect(self.screen, (150, 150, 150), (200, 460, 100, 50), 2)
            show_text = self.small_font.render("Show", True, (200, 200, 200))
            show_rect = show_text.get_rect(center=(250, 485))
            self.screen.blit(show_text, show_rect)

            # Next button
            next_color = (70, 70, 70) if self.current_state_index < len(self.history) - 1 else (40, 40, 40)
            pygame.draw.rect(self.screen, next_color, (350, 460, 100, 50))
            pygame.draw.rect(self.screen, (150, 150, 150), (350, 460, 100, 50), 2)
            next_text = self.small_font.render("Next >", True, (200, 200, 200))
            next_rect = next_text.get_rect(center=(400, 485))
            self.screen.blit(next_text, next_rect)

            # Show move counter
            move_text = self.small_font.render(f"Move: {self.current_state_index}/{len(self.history) - 1}", True,
                                               (150, 150, 150))
            move_rect = move_text.get_rect(center=(250, 520))
            self.screen.blit(move_text, move_rect)

            pygame.display.update()