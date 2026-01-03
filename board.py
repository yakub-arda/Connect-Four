import pygame
from counter import Counter
from utility import check_direction, ROWS, COLS

CELL_SIZE = 100


class Board:
    def __init__(self):
        self.grid = [[0] * COLS for _ in range(ROWS)]
        self.counters = {}

        cell_img = pygame.image.load("assets/Cell.png")
        red_img = pygame.image.load("assets/RedCounter.png")
        yellow_img = pygame.image.load("assets/YellowCounter.png")

        self.cell = pygame.transform.scale(cell_img, (CELL_SIZE, CELL_SIZE))
        self.red = pygame.transform.scale(red_img, (CELL_SIZE, CELL_SIZE))
        self.yellow = pygame.transform.scale(yellow_img, (CELL_SIZE, CELL_SIZE))

    def draw(self, screen):
        for r in range(ROWS):
            for c in range(COLS):
                screen.blit(self.cell, (c * CELL_SIZE, r * CELL_SIZE))

        for counter in self.counters.values():
            counter.draw(screen)

    def valid_moves(self):
        return [c for c in range(COLS) if self.grid[0][c] == 0]

    def is_full(self):
        return len(self.valid_moves()) == 0

    def make_move(self, col, player):
        for r in range(ROWS - 1, -1, -1):
            if self.grid[r][col] == 0:
                self.grid[r][col] = player
                img = self.red if player == 1 else self.yellow
                self.counters[(r, col)] = Counter(player, r, col, img)
                return r, col
        return None

    def undo_move(self, col):
        for r in range(ROWS):
            if self.grid[r][col] != 0:
                self.grid[r][col] = 0
                del self.counters[(r, col)]
                return

    def check_win(self, player):
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] != player:
                    continue
                if (
                        check_direction(self.grid, r, c, 0, 1, player, ROWS, COLS) >= 4 or
                        check_direction(self.grid, r, c, 1, 0, player, ROWS, COLS) >= 4 or
                        check_direction(self.grid, r, c, 1, 1, player, ROWS, COLS) >= 4 or
                        check_direction(self.grid, r, c, 1, -1, player, ROWS, COLS) >= 4
                ):
                    return True
        return False

    def copy(self):
        """Create a deep copy of the board state"""
        new_board = Board()
        new_board.grid = [row[:] for row in self.grid]
        new_board.counters = {}
        for (r, c), counter in self.counters.items():
            img = new_board.red if counter.player == 1 else new_board.yellow
            new_board.counters[(r, c)] = Counter(counter.player, r, c, img)
        return new_board