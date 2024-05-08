import random
import time

import game


class v1():

    def __init__(self, board_size, bot, opponent, depth):
        self.board_size = board_size
        self.player = opponent
        self.bot = bot

    def bot_move(self, board):
        best_move = None
        best_score = -1
        start_time = time.time()
        for row in range(self.board_size):
            game.draw_timer(self.getSymbol(), int(time.time() - start_time))
            for col in range(self.board_size):
                if board[row][col] == ' ':
                    board[row][col] = self.player
                    opponent_chain_length = self.evaluate_chain(board, row, col, self.player)
                    board[row][col] = self.bot
                    bot_chain_length = self.evaluate_chain(board, row, col, self.bot)
                    board[row][col] = ' '

                    score = max(opponent_chain_length, bot_chain_length)
                    if score > best_score or (score == best_score and random.random() < 0.5):
                        best_score = score
                        best_move = (row, col)

        return best_move

    def count_chain_length(self, board, row, col, player, drow, dcol):
        length = 0
        while 0 <= row < self.board_size and 0 <= col < self.board_size and board[row][col] == player:
            length += 1
            row += drow
            col += dcol
        return length

    def evaluate_chain(self, board, row, col, player):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        max_length = 0
        for drow, dcol in directions:
            length = 1 + self.count_chain_length(board, row + drow, col + dcol, player, drow,
                                                 dcol) + self.count_chain_length(board, row - drow, col - dcol, player,
                                                                                 -drow, -dcol)
            max_length = max(max_length, length)
        return max_length

    def isHuman(self):
        return False

    def getSymbol(self):
        return self.bot
