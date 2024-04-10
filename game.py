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
    score = 0
    opponent = 'A' if player == 'B' else 'B'
    patterns = {
        'five_in_a_row': 10000000,
        'four_in_a_row_two_open': 10000,
        'four_in_a_row_one_open': 1000,
        'three_in_a_row_two_open': 1000,
        'three_in_a_row_one_open': 100,
        'two_in_a_row_two_open': 100,
        'two_in_a_row_one_open': 10,
    }


    # Check for patterns in all directions and positions
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == player:
                # For each piece belonging to the player, check surrounding patterns
                score += check_patterns_around_piece(board, row, col, player, patterns)
            elif board[row][col] == opponent:
                # Similarly, check patterns for the opponent and subtract scores to prioritize blocking
                score -= check_patterns_around_piece(board, row, col, opponent, patterns)
    print("score: ", score if player == BOT else -score)
    return score

def check_patterns_around_piece(board, row, col, player, patterns):
    score = 0
    # Directions: Horizontal (H), Vertical (V), Diagonal (\) and Diagonal (/)
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # Right, Down, Down-Right, Down-Left

    for d in directions:
        for i in range(-4, 5):  # Check 4 pieces in each direction from the current piece
            consecutive_count = 0
            open_ends = 0

            for j in range(5):  # Check for 5 consecutive pieces
                r, c = row + (i + j) * d[0], col + (i + j) * d[1]

                if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                    break  # Out of bounds

                if board[r][c] == player:
                    consecutive_count += 1
                elif board[r][c] == ' ' or board[r][c] == player:
                    open_ends += 1
                else:
                    break  # Opponent's piece, not a valid pattern

            if consecutive_count == 5:
                return patterns['five_in_a_row']  # Immediate win

            if consecutive_count == 4:
                if open_ends == 2:
                    score += patterns['four_in_a_row_two_open']
                    #print("four_in_a_row_two_open for player ", player)
                elif open_ends == 1:
                    score += patterns['four_in_a_row_one_open']
                    #print("four_in_a_row_one_open for player ", player)
            elif consecutive_count == 3:
                if open_ends == 2:
                    score += patterns['three_in_a_row_two_open']
                    #print("three_in_a_row_two_open for player ", player)
                elif open_ends == 1:
                    score += patterns['three_in_a_row_one_open']
                    #print("three_in_a_row_one_open for player ", player)

            elif consecutive_count == 2:
                if open_ends == 2:
                    score += patterns['two_in_a_row_two_open']
                    #print("two_in_a_row_two_open for player ", player)
                elif open_ends == 1:
                    score += patterns['two_in_a_row_one_open']
                    #print("two_in_a_row_one_open for player ", player)

    return score

def bot_move(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or game_over(board):
        return evaluate_board(board, BOT if maximizing_player else PLAYER), None

    best_move = None
    if maximizing_player:
        max_eval = float('-inf')
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board[row][col] == ' ':
                    board[row][col] = BOT
                    # Somehow bot never tries to win, so add this
                    if check_win_board(board, BOT):
                        board[row][col] = ' '
                        return float('inf'), (row, col)
                    evaluation = bot_move(board, depth - 1, alpha, beta, False)[0]
                    board[row][col] = ' '
                    if evaluation > max_eval:
                        max_eval = evaluation
                        best_move = (row, col)
                    alpha = max(alpha, evaluation)
                    if beta <= alpha:
                        break
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board[row][col] == ' ':
                    board[row][col] = PLAYER
                    evaluation = bot_move(board, depth - 1, alpha, beta, True)[0]
                    board[row][col] = ' '
                    if evaluation < min_eval:
                        min_eval = evaluation
                        best_move = (row, col)
                    beta = min(beta, evaluation)
                    if beta <= alpha:
                        break
            if beta <= alpha:
                break
        return min_eval, best_move

def draw_pieces(screen, board):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == PLAYER:
                draw_piece(screen, row, col, RED)
            elif board[row][col] == BOT:
                draw_piece(screen, row, col, BLUE)
def main(depth, alpha, beta, maximizing_player):
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Gomoku')
    clock = pygame.time.Clock()
    start_time = time.time()

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
            _, (bot_row, bot_col) = bot_move(board, depth, alpha, beta, maximizing_player)
            if bot_row is not None and bot_col is not None:
                board[bot_row][bot_col] = BOT
                if check_win_board(board, BOT):
                    game_over_flag = (True, BOT)
                player = PLAYER
                start_time = time.time()

        draw_board(screen)
        draw_pieces(screen, board)

        if game_over_flag[0]:
            draw_winner(screen, game_over_flag[1])

        draw_timer(screen, player, int(time.time() - start_time))
        pygame.display.flip()
        clock.tick(30)

    while True:
        # Keep the window open for winner display
        pass
if __name__ == '__main__':
    main( 3, -10000000, 10000000, True)
    '''board = [['A', 'A', 'A', 'A', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'A', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', 'A', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'A', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', 'A', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']]
    print(evaluate_board(board, 'A'))'''
