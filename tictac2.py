import sys
import pygame
import numpy as np

pygame.init()

#colorts
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

#PROPERTIES

WIDTH = 300
HEIGHT = 300
LINE_WIDTH = 5
BOARD_ROWS = 3
BOARD_COLS = 3
SQARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe AI")
screen.fill(BLACK)

board = np.zeros((BOARD_ROWS, BOARD_COLS), dtype=int)

def draw_lines(color=WHITE):
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(screen, color, (0, i * SQARE_SIZE), (WIDTH, i * SQARE_SIZE), LINE_WIDTH)
    for i in range(1, BOARD_COLS):
        pygame.draw.line(screen, color, (i * SQARE_SIZE, 0), (i * SQARE_SIZE, HEIGHT), LINE_WIDTH)

def draw_figures(color_override=None):
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 1:
                color = color_override if color_override is not None else GREEN
                pygame.draw.circle(screen, color, (int(col * SQARE_SIZE + SQARE_SIZE // 2), int(row * SQARE_SIZE + SQARE_SIZE // 2)), CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[row][col] == 2:
                color = color_override if color_override is not None else RED
                pygame.draw.line(screen, color, (col * SQARE_SIZE + CROSS_WIDTH // 2, row * SQARE_SIZE + CROSS_WIDTH // 2), (col * SQARE_SIZE + SQARE_SIZE - CROSS_WIDTH // 2, row * SQARE_SIZE + SQARE_SIZE - CROSS_WIDTH // 2), CROSS_WIDTH)     
                pygame.draw.line(screen, color, (col * SQARE_SIZE + CROSS_WIDTH // 2, row * SQARE_SIZE + SQARE_SIZE - CROSS_WIDTH // 2), (col * SQARE_SIZE + SQARE_SIZE - CROSS_WIDTH // 2, row * SQARE_SIZE + CROSS_WIDTH // 2), CROSS_WIDTH)


def mark_square(row, col, player):
    board[row][col] = player

def available_square(row, col):
    return board[row][col] == 0

def is_board_full(check_board=board):
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if check_board[row][col] == 0:
                return False
    return True

def check_win(player, check_board=board):
    for row in range(BOARD_ROWS):
        if check_board[row][0] == player and check_board[row][1] == player and check_board[row][2] == player:
            return True
    for col in range(BOARD_COLS):
        if check_board[0][col] == player and check_board[1][col] == player and check_board[2][col] == player:
            return True
    if check_board[0][0] == player and check_board[1][1] == player and check_board[2][2] == player:
        return True
    if check_board[0][2] == player and check_board[1][1] == player and check_board[2][0] == player:
        return True
    return False

def minimax(check_board, depth, is_max):
    if check_win(2, check_board):
        return 1
    elif check_win(1, check_board):
        return -1
    elif is_board_full(check_board):
        return 0

    if is_max:
        best_score = -float('inf')
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if check_board[row][col] == 0:
                    check_board[row][col] = 2
                    score = minimax(check_board, depth + 1, False)
                    check_board[row][col] = 0
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if check_board[row][col] == 0:
                    check_board[row][col] = 1
                    score = minimax(check_board, depth + 1, True)
                    check_board[row][col] = 0
                    best_score = min(score, best_score)
        return best_score
def restart_game():
    screen.fill(BLACK)
    draw_lines()
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            board[row][col] = 0

def best_move():
    best_score = -float('inf')
    move = None
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 0:
                board[row][col] = 2
                score = minimax(board, 0, False)
                board[row][col] = 0
                if score > best_score:
                    best_score = score
                    move = (row, col)
    return move
player = 1
game_over = False

draw_lines()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mouseX = event.pos[0] // SQARE_SIZE
            mouseY = event.pos[1] // SQARE_SIZE

            if available_square(mouseY, mouseX):
                mark_square(mouseY, mouseX, player)
                if check_win(player):
                    game_over = True
                player = player % 2 + 1

                # AI move
                if not game_over:
                    move = best_move()
                    if move is not None:
                        mark_square(move[0], move[1], 2)
                        if check_win(2):
                            game_over = True
                        player = player % 2 + 1

                if not game_over:
                    if is_board_full():
                        game_over = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                restart_game()
                player = 1
                game_over = False

    # redraw board every frame
    screen.fill(BLACK)
    draw_lines()
    if not game_over:
        draw_figures()
    else:
        if check_win(1):
            draw_figures(GREEN)
            draw_lines(GREEN)
        elif check_win(2):
            draw_figures(RED)
            draw_lines(RED)
        else:
            draw_figures(GRAY)
            draw_lines(GRAY)
    pygame.display.update()