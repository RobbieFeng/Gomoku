import pygame
import sys
import time

# Constants
BOARD_SIZE = 15
GRID_SIZE = 40  # Adjust grid size as needed
WINDOW_WIDTH = BOARD_SIZE * GRID_SIZE
WINDOW_HEIGHT = BOARD_SIZE * GRID_SIZE + 100  # Extra space for timer and player info
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


def draw_board(screen):
    screen.fill(WHITE)
    for i in range(BOARD_SIZE):
        pygame.draw.line(screen, BLACK, (i * GRID_SIZE, 0), (i * GRID_SIZE, BOARD_SIZE * GRID_SIZE))
        pygame.draw.line(screen, BLACK, (0, i * GRID_SIZE), (BOARD_SIZE * GRID_SIZE, i * GRID_SIZE))
    pygame.draw.line(screen, BLACK, (0, (BOARD_SIZE) * GRID_SIZE), (BOARD_SIZE * GRID_SIZE, (BOARD_SIZE) * GRID_SIZE))

def draw_piece(screen, row, col, color):
    pygame.draw.circle(screen, color, (col * GRID_SIZE + GRID_SIZE // 2, row * GRID_SIZE + GRID_SIZE // 2),
                       GRID_SIZE // 2 - 5)


def check_win(board, row, col, player):
    # Check horizontal
    count = 0
    for i in range(max(0, col - 4), min(BOARD_SIZE, col + 5)):
        if board[row][i] == player:
            count += 1
            if count == 5:
                return True
        else:
            count = 0

    # Check vertical
    count = 0
    for i in range(max(0, row - 4), min(BOARD_SIZE, row + 5)):
        if board[i][col] == player:
            count += 1
            if count == 5:
                return True
        else:
            count = 0

    # Check diagonal (top-left to bottom-right)
    count = 0
    for i in range(-4, 5):
        if 0 <= row + i < BOARD_SIZE and 0 <= col + i < BOARD_SIZE:
            if board[row + i][col + i] == player:
                count += 1
                if count == 5:
                    return True
            else:
                count = 0

    # Check diagonal (top-right to bottom-left)
    count = 0
    for i in range(-4, 5):
        if 0 <= row + i < BOARD_SIZE and 0 <= col - i < BOARD_SIZE:
            if board[row + i][col - i] == player:
                count += 1
                if count == 5:
                    return True
            else:
                count = 0

    return False


def draw_timer(screen, player, remaining_time):
    font = pygame.font.Font(None, 36)
    timer_text = font.render(f"Player {player}'s Turn: {remaining_time} sec", True, BLACK)
    screen.blit(timer_text, (10, WINDOW_HEIGHT - 70))


def draw_winner(screen, winner):
    font = pygame.font.Font(None, 48)
    winner_text = font.render(f"Player {winner} wins!", True, BLACK)
    screen.blit(winner_text,
                ((WINDOW_WIDTH - winner_text.get_width()) // 2, (WINDOW_HEIGHT - winner_text.get_height()) // 2))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Gomoku')
    clock = pygame.time.Clock()

    board = [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    player = 'A'
    game_over = False
    start_time = time.time()
    winner = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                col = event.pos[0] // GRID_SIZE
                row = event.pos[1] // GRID_SIZE

                if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and board[row][col] == ' ':
                    board[row][col] = player

                    if check_win(board, row, col, player):
                        winner = player
                        game_over = True

                    player = 'B' if player == 'A' else 'A'
                    start_time = time.time()

        draw_board(screen)

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board[row][col] == 'A':
                    draw_piece(screen, row, col, RED)
                elif board[row][col] == 'B':
                    draw_piece(screen, row, col, BLUE)

        if game_over:
            draw_winner(screen, winner)
        else:
            draw_timer(screen, player, max(0, int(time.time() - start_time)))

        pygame.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    main()
