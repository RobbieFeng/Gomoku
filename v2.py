import math
import time

import game

count = 0
class v2:
    def __init__(self, board_size, bot, opponent, depth):
        self.board_size = board_size
        self.player = opponent
        self.bot = bot
        self.Max_depth = depth

    def evaluate_board(self, board, player):
        score = 0
        opponent = 'A' if player == 'B' else 'B'
        patterns = {
            'five_in_a_row': 64000,
            'four_in_a_row_two_open': 320,
            'four_in_a_row_one_open': 160,
            'three_in_a_row_two_open': 80,
            'three_in_a_row_one_open': 40,
            'two_in_a_row_two_open': 20,
            'two_in_a_row_one_open': 10,
        }
        urgent_patterns = ['five_in_a_row', 'four_in_a_row_two_open', 'four_in_a_row_one_open']
        checked_positions = set()  # To keep track of positions that have been checked

        for row in range(self.board_size):
            for col in range(self.board_size):
                if (row, col) not in checked_positions and board[row][col] in [player, opponent]:
                    # Check patterns only for positions that haven't been checked before
                    piece_owner = board[row][col]
                    score_change, new_checked_positions = self.check_patterns_around_piece(board, row, col, piece_owner,
                                                                                      patterns, self.board_size)
                    checked_positions.update(new_checked_positions)  # Update checked positions

                    if piece_owner == player:
                        score += score_change
                    else:
                        score -= score_change
        #print("Score:%d for player:%s" % (score, player))
        return score


    def check_patterns_around_piece(self, board, row, col, player, patterns, BOARD_SIZE):
        score = 0
        checked_positions = set()
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for d in directions:
            forward_positions, backward_positions = [], []
            total_count = 1  # Count the current piece
            open_ends = 0

            # Check forward direction
            for i in range(1, 5):
                r, c = row + i * d[0], col + i * d[1]
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    forward_positions.append((r, c))
                    if board[r][c] == player:
                        total_count += 1
                    elif board[r][c] == ' ':
                        open_ends += 1
                        break
                    else:
                        break
                else:
                    break

            # Check backward direction
            for i in range(1, 5):
                r, c = row - i * d[0], col - i * d[1]
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    backward_positions.append((r, c))
                    if board[r][c] == player:
                        total_count += 1
                    elif board[r][c] == ' ' and total_count < 5:
                        open_ends += 1
                        break
                    else:
                        break
                else:
                    break

            # Update score based on pattern found
            pattern_key = ''
            if total_count == 5:
                pattern_key = 'five_in_a_row'
            elif total_count == 4:
                if open_ends == 2:
                    pattern_key = 'four_in_a_row_two_open'
                elif open_ends == 1:
                    pattern_key = 'four_in_a_row_one_open'
            elif total_count == 3:
                if open_ends == 2:
                    pattern_key = 'three_in_a_row_two_open'
                elif open_ends == 1:
                    pattern_key = 'three_in_a_row_one_open'
            elif total_count == 2:
                if open_ends == 2:
                    pattern_key = 'two_in_a_row_two_open'
                elif open_ends == 1:
                    pattern_key = 'two_in_a_row_one_open'
            if pattern_key:
                score += patterns[pattern_key]
                # Add positions part of this pattern to checked_positions to avoid rechecking
                checked_positions.update(forward_positions)
                checked_positions.update(backward_positions)

        # Return the score and the set of checked positions
        return score, checked_positions


    def generate_candidate_moves(self, board, proximity=2):
        candidate_moves = set()
        for row in range(self.board_size):
            for col in range(self.board_size):
                if board[row][col] != ' ':
                    for dr in range(-proximity, proximity + 1):
                        for dc in range(-proximity + abs(dr), proximity + 1 - abs(dr)):
                            new_row, new_col = row + dr, col + dc
                            if 0 <= new_row < self.board_size and 0 <= new_col < self.board_size and board[new_row][new_col] == ' ':
                                candidate_moves.add((new_row, new_col))

        return list(candidate_moves)


    def minimax(self, board, depth, alpha, beta, maximizing_player, start_time):
        global count
        count += 1
        if count % 1000 == 0:
            game.draw_timer(self.bot, int(time.time() - start_time))
        if depth == 0 or game.game_over(board):
            score = self.evaluate_board(board, self.bot)
            score = score / (self.Max_depth + 1) * (depth + 1)
            return score, None, []
        best_move = None
        if maximizing_player:
            max_eval = float('-inf')
            # for fist move, idealy place beside the first player
            candidates = self.generate_candidate_moves(board) if depth != self.Max_depth else self.generate_candidate_moves(board,
                                                                                                             proximity=1)
            for move in candidates:
                row, col = move
                board[row][col] = self.bot
                eval, _, trace = self.minimax(board, depth - 1, alpha, beta, False, start_time)
                board[row][col] = ' '  # Undo the move
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                    trace.append(move)
                    best_trace = trace
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move, best_trace
        else:
            min_eval = float('inf')
            for move in self.generate_candidate_moves(board):
                row, col = move
                board[row][col] = self.player
                eval, _, trace = self.minimax(board, depth - 1, alpha, beta, True, start_time)
                board[row][col] = ' '  # Undo the move
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                    trace.append(move)
                    best_trace = trace
                beta = min(beta, eval)
                if beta <= alpha:
                    break

            return min_eval, best_move, best_trace


    def bot_move(self, board):
        start_time = time.time()
        score, best_move, best_trace = self.minimax(board, self.Max_depth, -math.inf, math.inf, True, start_time)
        #print(f"Best move: {best_move}, Score: {score}, trace: {best_trace}")
        return best_move

    def isHuman(self):
        return False

    def getSymbol(self):
        return self.bot
