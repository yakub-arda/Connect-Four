import pygame
import math
from board import Board
from minimax import minimax, evaluate
from utility import RED, YELLOW, AI_PLAYER1_DEPTH


class TreeNode:
    """Represents a node in the minimax tree - lazy loading with genuine eval"""

    def __init__(self, board, depth, player, move_col=None, parent=None, max_depth=6):
        self.board = board.copy()
        self.depth = depth
        self.player = player
        self.move_col = move_col
        self.parent = parent
        self.max_depth = max_depth
        self.children = None
        self.is_terminal = False

        if board.check_win(RED) or board.check_win(YELLOW) or depth >= max_depth or not board.valid_moves():
            self.is_terminal = True
            self.score = evaluate(board)
        else:
            remaining_depth = max_depth - depth
            self.score = minimax(self.board, remaining_depth, player == RED)

    def load_children(self):
        """Builds children on demand to save memory and prevent crashes"""
        if self.children is not None:
            return self.children

        if self.is_terminal:
            self.children = []
            return self.children

        self.children = []
        next_player = RED if self.player == YELLOW else YELLOW
        for col in self.board.valid_moves():
            self.board.make_move(col, self.player)
            child = TreeNode(self.board, self.depth + 1, next_player, col, self, self.max_depth)
            self.children.append(child)
            self.board.undo_move(col)
        return self.children


def draw_arrow(surface, color, start, end, width=3):
    """Draw an arrow from start to end"""
    dx, dy = end[0] - start[0], end[1] - start[1]
    angle = math.atan2(dy, dx)
    pygame.draw.line(surface, color, start, end, width)
    arrow_length, arrow_angle = 10, math.pi / 6
    left_x = end[0] - arrow_length * math.cos(angle - arrow_angle)
    left_y = end[1] - arrow_length * math.sin(angle - arrow_angle)
    right_x = end[0] - arrow_length * math.cos(angle + arrow_angle)
    right_y = end[1] - arrow_length * math.sin(angle + arrow_angle)
    pygame.draw.polygon(surface, color, [end, (left_x, left_y), (right_x, right_y)])


class TreeVisualizer:
    def __init__(self, root_board, depth, starting_player):
        self.screen = pygame.display.set_mode((1000, 600))
        pygame.display.set_caption("Minimax Tree Visualization")
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        self.root = TreeNode(root_board, 0, starting_player, max_depth=depth)
        self.current_node = self.root

    def move_to_parent(self):
        if self.current_node.parent:
            self.current_node = self.current_node.parent

    def move_to_child(self, index):
        children = self.current_node.load_children()
        if index < len(children):
            self.current_node = children[index]

    def draw_board(self, board, x, y, size):
        cell_size = size // 5
        for r in range(4):
            for c in range(5):
                rect = pygame.Rect(x + c * cell_size, y + r * cell_size, cell_size, cell_size)
                pygame.draw.rect(self.screen, (240, 240, 240), rect)
                pygame.draw.rect(self.screen, (100, 100, 100), rect, 1)
                if board.grid[r][c] == RED:
                    pygame.draw.circle(self.screen, (220, 50, 50),
                                       (x + c * cell_size + cell_size // 2, y + r * cell_size + cell_size // 2),
                                       cell_size // 3)
                elif board.grid[r][c] == YELLOW:
                    pygame.draw.circle(self.screen, (255, 215, 0),
                                       (x + c * cell_size + cell_size // 2, y + r * cell_size + cell_size // 2),
                                       cell_size // 3)

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.move_to_parent()
                    elif event.key == pygame.K_ESCAPE:
                        return
                    elif pygame.K_1 <= event.key <= pygame.K_5:
                        self.move_to_child(event.key - pygame.K_1)

            self.screen.fill((25, 25, 25))

            board_x, board_y = 50, 100
            self.draw_board(self.current_node.board, board_x, board_y, 200)
            self.screen.blit(self.font.render("CURRENT NODE", True, (255, 255, 255)), (board_x + 40, 60))

            info_x, info_y = board_x + 220, board_y + 20
            p_name = 'RED' if self.current_node.player == RED else 'YELLOW'
            strategy = "(Maximizing)" if self.current_node.player == RED else "(Minimizing)"
            p_color = (255, 100, 100) if self.current_node.player == RED else (255, 215, 0)

            self.screen.blit(self.font.render(f"Depth: {self.current_node.depth}", True, (200, 200, 200)),
                             (info_x, info_y))
            self.screen.blit(self.font.render(f"Player: {p_name}", True, p_color), (info_x, info_y + 30))
            self.screen.blit(self.small_font.render(strategy, True, (150, 150, 150)), (info_x + 140, info_y + 35))

            score = self.current_node.score
            eval_color = (200, 200, 200)
            if (self.current_node.player == RED and score > 0) or (self.current_node.player == YELLOW and score < 0):
                eval_color = (100, 255, 100)
            elif (self.current_node.player == RED and score < 0) or (self.current_node.player == YELLOW and score > 0):
                eval_color = (255, 100, 100)

            self.screen.blit(self.font.render(f"Evaluation: {score}", True, eval_color), (info_x, info_y + 60))
            status_text = "Leaf Node" if self.current_node.is_terminal else "Child Node"
            self.screen.blit(self.font.render(f"Status: {status_text}", True, (100, 200, 255)), (info_x, info_y + 90))

            if self.current_node.parent:
                px, py = board_x + 600, board_y
                self.screen.blit(self.font.render("PARENT", True, (100, 150, 255)), (px + 60, py - 25))
                self.draw_board(self.current_node.parent.board, px, py, 150)
                draw_arrow(self.screen, (100, 150, 255), (px - 50, py - 20), (board_x + 200, board_y - 30), 4)
                self.screen.blit(
                    self.small_font.render(f"Eval: {self.current_node.parent.score}", True, (100, 255, 100)),
                    (px + 160, py + 60))

            children = self.current_node.load_children()
            if children:
                cy = board_y + 250
                self.screen.blit(self.font.render("CHILDREN", True, (255, 150, 100)), (50, cy - 30))
                num_c = len(children)
                total_w = min(num_c * 160, 900)
                start_x = (1000 - total_w) // 2
                spacing = total_w // max(num_c, 1)

                for i, child in enumerate(children):
                    cx, c_y = start_x + i * spacing + 40, cy + 40
                    self.draw_board(child.board, cx, c_y, 110)
                    draw_arrow(self.screen, (255, 150, 100), (board_x + 100, board_y + 165), (cx + 25, c_y - 55), 3)

                    self.screen.blit(self.font.render(f"Col {child.move_col + 1}", True, (255, 255, 255)),
                                     (cx + 25, c_y - 50))
                    self.screen.blit(self.small_font.render(f"Press {i + 1}", True, (150, 150, 255)),
                                     (cx + 25, c_y - 25))
                    self.screen.blit(self.small_font.render(f"Eval: {child.score}", True, (255, 255, 255)),
                                     (cx + 10, c_y + 120))

            pygame.draw.rect(self.screen, (40, 40, 40), (0, 540, 1000, 60))
            pygame.draw.line(self.screen, (100, 100, 100), (0, 540), (1000, 540), 2)
            self.screen.blit(self.font.render("CONTROLS:", True, (255, 255, 255)), (20, 550))

            up_txt = "UP ARROW = Go to parent" if self.current_node.parent else "UP ARROW = (No parent)"
            self.screen.blit(
                self.small_font.render(up_txt, True, (150, 255, 150) if self.current_node.parent else (100, 100, 100)),
                (150, 555))

            child_txt = f"Press 1-{len(children)} = Go to child" if children else "(No children)"
            self.screen.blit(self.small_font.render(child_txt, True, (255, 200, 150) if children else (100, 100, 100)),
                             (450, 555))
            self.screen.blit(self.small_font.render("ESC = Close window", True, (200, 200, 200)), (750, 555))

            pygame.display.update()
            clock.tick(60)