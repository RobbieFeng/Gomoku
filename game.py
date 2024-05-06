import math

import pygame
import sys
import time

# Constants
BOARD_SIZE = 10
GRID_SIZE = 40
WINDOW_WIDTH = BOARD_SIZE * GRID_SIZE
WINDOW_HEIGHT = BOARD_SIZE * GRID_SIZE + 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PLAYER = 'A'
BOT = 'B'
choise_history = []
Max_depth= -1
def draw_board(screen):
    screen.fill(WHITE)
    for i in range(BOARD_SIZE):
        pygame.draw.line(screen, BLACK, (i * GRID_SIZE, 0), (i * GRID_SIZE, BOARD_SIZE * GRID_SIZE))
        pygame.draw.line(screen, BLACK, (0, i * GRID_SIZE), (BOARD_SIZE * GRID_SIZE, i * GRID_SIZE))
    pygame.draw.line(screen, BLACK, (0, BOARD_SIZE * GRID_SIZE), (BOARD_SIZE * GRID_SIZE, BOARD_SIZE * GRID_SIZE))

def draw_piece(screen, row, col, color):
    pygame.draw.circle(screen, color, (col * GRID_SIZE + GRID_SIZE // 2, row * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 2 - 5)

def draw_timer(screen, player, remaining_time):
    font = pygame.font.Font(None, 36)
    timer_text = font.render(f"Player {player}'s Turn: {remaining_time} sec", True, BLACK)
    screen.blit(timer_text, (10, WINDOW_HEIGHT - 70))

def draw_winner(screen, winner):
    font = pygame.font.Font(None, 48)
    winner_text = font.render(f"Player {winner} wins!", True, RED if winner == PLAYER else BLUE)
    screen.blit(winner_text, ((WINDOW_WIDTH - winner_text.get_width()) // 2, (WINDOW_HEIGHT - winner_text.get_height()) // 2))

def check_win(board, row, col, player):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for d in directions:
        count = 1
        for i in range(1, 5):
            r, c = row + d[0] * i, col + d[1] * i
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
                count += 1
            else:
                break
        if count >= 5:
            return True
    return False

def check_win_board(board, player):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == player:
                if check_win(board, row, col, player):
                    return True
    return False
def game_over(board):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] != ' ':
                if check_win(board, row, col, board[row][col]):
                    return True
    return False


def evaluate_board(board, player):
    BOARD_SIZE = len(board)  # Assuming the board is square
    score = 0
    opponent = 'A' if player == 'B' else 'B'
    patterns = {
        'five_in_a_row': 640,
        'four_in_a_row_two_open': 320,
        'four_in_a_row_one_open': 160,
        'three_in_a_row_two_open': 80,
        'three_in_a_row_one_open': 40,
        'two_in_a_row_two_open': 20,
        'two_in_a_row_one_open': 10,
    }
    urgent_patterns = ['five_in_a_row', 'four_in_a_row_two_open', 'four_in_a_row_one_open']
    checked_positions = set()  # To keep track of positions that have been checked

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row, col) not in checked_positions and board[row][col] in [player, opponent]:
                # Check patterns only for positions that haven't been checked before
                piece_owner = board[row][col]
                score_change, new_checked_positions = check_patterns_around_piece(board, row, col, piece_owner,
                                                                                  patterns, BOARD_SIZE)
                checked_positions.update(new_checked_positions)  # Update checked positions

                if piece_owner == player:
                    score += score_change
                else:
                    score -= score_change
    print("Score:%d for player:%s" % (score, player))
    return score


def check_patterns_around_piece(board, row, col, player, patterns, BOARD_SIZE):
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


import time

def generate_candidate_moves(board, proximity=2):
    candidate_moves = set()
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] != ' ':
                for dr in range(-proximity, proximity + 1):
                    for dc in range(-proximity, proximity + 1):
                        new_row, new_col = row + dr, col + dc
                        if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and board[new_row][new_col] == ' ':
                            candidate_moves.add((new_row, new_col))

    return list(candidate_moves)

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or game_over(board):
        return evaluate_board(board, BOT), None, []
    best_move = None
    if maximizing_player:
        max_eval = float('-inf')
        for move in generate_candidate_moves(board):
            row, col = move
            board[row][col] = BOT
            eval, _, trace = minimax(board, depth - 1, alpha, beta, False)
            board[row][col] = ' '  # Undo the move
            if eval > max_eval:
                max_eval = eval
                best_move = move
                trace.append(move)
                bext_trace = trace
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move, bext_trace
    else:
        min_eval = float('inf')
        for move in generate_candidate_moves(board):
            row, col = move
            board[row][col] = PLAYER
            eval, _ , trace = minimax(board, depth - 1, alpha, beta, True)
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


def bot_move(board, depth):
    score, best_move, best_trace = minimax(board, depth, float('-inf'), float('inf'),True)
    print(f"Best move: {best_move}, Score: {score}, trace: {best_trace}")
    return best_move



def draw_pieces(screen, board):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == PLAYER:
                draw_piece(screen, row, col, RED)
            elif board[row][col] == BOT:
                draw_piece(screen, row, col, BLUE)
def main(depth):
    global Max_depth
    Max_depth = depth
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Gomoku')
    clock = pygame.time.Clock()
    player_start_time = time.time()

    board = [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    player = PLAYER
    game_over_flag = (False, None)

    while not game_over_flag[0]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and player == PLAYER:
                x, y = event.pos
                col, row = x // GRID_SIZE, y // GRID_SIZE
                if board[row][col] == ' ':
                    board[row][col] = player
                    if check_win_board(board, PLAYER):
                        game_over_flag = (True, PLAYER)
                    player = BOT
                    draw_pieces(screen, board)
                    pygame.display.flip()

        if player == BOT and not game_over_flag[0]:
            (bot_row, bot_col) = bot_move(board, depth)
            process_history(depth)
            if bot_row is not None and bot_col is not None:
                board[bot_row][bot_col] = BOT
                if check_win_board(board, BOT):
                    game_over_flag = (True, BOT)
                player = PLAYER
                player_start_time = time.time()

        draw_board(screen)
        draw_pieces(screen, board)

        if game_over_flag[0]:
            draw_winner(screen, game_over_flag[1])

        draw_timer(screen, player, int(time.time() - player_start_time))
        pygame.display.flip()
        clock.tick(30)

    while True:
        # Keep the window open for winner display
        time.sleep(5)
        pass

def process_history(depth):
    global choise_history
    #count number of each piece in the history
    count = {}
    for i in choise_history:
        if i[1] == depth:
            if i[2] in count:
                count[i[2]] += 1
            else:
                count[i[2]] = 1
    print(count)
    choise_history = []

if __name__ == '__main__':
    main(3)