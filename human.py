import sys
import time

import pygame
import game


class human:
    def __init__(self, board_size, player, opponent):
        self.board_size = board_size
        self.player = player
        self.bot = opponent

    def human_move(self, board):
        start_time = time.time()
        while True:
            for event in pygame.event.get():
                game.draw_timer("Player", int(time.time() - start_time))
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.Rect(game.WINDOW_WIDTH - 150, game.WINDOW_HEIGHT - 90, 140, 40).collidepoint(event.pos):
                        return "Restart", None  # Call the restart function
                    x, y = event.pos
                    col, row = x // game.GRID_SIZE, y // game.GRID_SIZE
                    try:
                        if board[row][col] == ' ':
                            move = (row, col)
                            return move
                    except IndexError:
                        pass

    def isHuman(self):
        return True

    def getSymbol(self):
        return self.player
