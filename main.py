import pygame
from connect_four import ConnectFour

if __name__ == "__main__":
    game = ConnectFour()
    game.run()
    pygame.quit()