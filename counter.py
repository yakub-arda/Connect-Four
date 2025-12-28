class Counter:
    def __init__(self, player, row, col, image):
        self.player = player
        self.row = row
        self.col = col
        self.image = image
        self.x = col * 100  # CELL_SIZE is 100
        self.y = row * 100

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))