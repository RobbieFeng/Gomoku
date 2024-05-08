import pygame
import time
import v1
import v2

# Constants
BOARD_SIZE = 13
GRID_SIZE = 40
WINDOW_WIDTH = BOARD_SIZE * GRID_SIZE
WINDOW_HEIGHT = BOARD_SIZE * GRID_SIZE + 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PLAYER = 'A'
BOT = 'B'
screen = None
count = 0
FirstPlayer = None
SecondPlayer = None

def draw_board():
    screen.fill(WHITE)
    for i in range(BOARD_SIZE):
        pygame.draw.line(screen, BLACK, (i * GRID_SIZE, 0), (i * GRID_SIZE, BOARD_SIZE * GRID_SIZE))
        pygame.draw.line(screen, BLACK, (0, i * GRID_SIZE), (BOARD_SIZE * GRID_SIZE, i * GRID_SIZE))
    pygame.draw.line(screen, BLACK, (0, BOARD_SIZE * GRID_SIZE), (BOARD_SIZE * GRID_SIZE, BOARD_SIZE * GRID_SIZE))
    restart_button_rect = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 90, 140, 40)
    pygame.draw.rect(screen, BLUE, restart_button_rect)
    font = pygame.font.Font(None, 36)
    text = font.render('Restart', True, WHITE)
    text_rect = text.get_rect(center=restart_button_rect.center)
    screen.blit(text, text_rect)

def draw_piece(row, col, color):
    pygame.draw.circle(screen, color, (col * GRID_SIZE + GRID_SIZE // 2, row * GRID_SIZE + GRID_SIZE // 2),
                       GRID_SIZE // 2 - 5)


def draw_timer(player, remaining_time):
    screen = pygame.display.get_surface()
    screen.fill(WHITE, (0, WINDOW_HEIGHT - 70, WINDOW_WIDTH, 70))
    font = pygame.font.Font(None, 36)
    timer_text = font.render(f"{player}'s Turn: Thinking... {remaining_time} sec", True, BLACK)
    screen.blit(timer_text, (10, WINDOW_HEIGHT - 70))
    restart_button_rect = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 90, 140, 40)
    pygame.draw.rect(screen, BLUE, restart_button_rect)
    font = pygame.font.Font(None, 36)
    text = font.render('Restart', True, WHITE)
    text_rect = text.get_rect(center=restart_button_rect.center)
    screen.blit(text, text_rect)
    pygame.display.flip()



def draw_winner(winner):
    font = pygame.font.Font(None, 48)
    winner_text = font.render(f"Player {winner} wins!", True, RED if winner == PLAYER else BLUE)
    screen.blit(winner_text,
                ((WINDOW_WIDTH - winner_text.get_width()) // 2, (WINDOW_HEIGHT - winner_text.get_height()) // 2))


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


def draw_pieces(board):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == PLAYER:
                draw_piece(row, col, RED)
            elif board[row][col] == BOT:
                draw_piece(row, col, BLUE)


def main(firstPlayer, secondPlayer):
    global TimerResetFlag, screen, FirstPlayer, SecondPlayer
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Gomoku')
    clock = pygame.time.Clock()
    player_start_time = time.time()

    FirstPlayer = firstPlayer
    SecondPlayer = secondPlayer


    board = [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    player = firstPlayer
    game_over_flag = (False, None)

    #if bot is first player, plave at the center
    if firstPlayer.isHuman() == False:
        board[BOARD_SIZE//2][BOARD_SIZE//2] = firstPlayer.getSymbol()
        player = secondPlayer
        draw_pieces(board)
        pygame.display.flip()

    while not game_over_flag[0]:
        time.sleep(0.5)
        if player == firstPlayer:
            (row, col) = player.human_move(board) if firstPlayer.isHuman() else player.bot_move(board)
            board[row][col] = player.getSymbol()
            if check_win_board(board, player):
                game_over_flag = (True, player)
            player = secondPlayer
            draw_pieces(board)
            pygame.display.flip()

        elif player == secondPlayer:
            (row, col) = player.human_move(board) if player.isHuman() else player.bot_move(board)
            board[row][col] = player.getSymbol()
            if check_win_board(board, player):
                game_over_flag = (True, player)
            player = firstPlayer
            draw_pieces(board)
            pygame.display.flip()

        draw_board()
        draw_pieces(board)
        draw_timer(player.getSymbol(), int(time.time() - player_start_time))

        if game_over_flag[0]:
            draw_winner(game_over_flag[1])

        pygame.display.flip()
        #clock.tick(30)
    while True:
        # Keep the window open for winner display
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 90, 140,
                                                                    40).collidepoint(event.pos):
                restart()


def restart():
    main(FirstPlayer, SecondPlayer)


if __name__ == '__main__':
    firstPlayer = v1.v1(BOARD_SIZE, PLAYER, BOT)
    secondPlayer = v2.v2(BOARD_SIZE, BOT, PLAYER, 3)
    main(firstPlayer, secondPlayer)
