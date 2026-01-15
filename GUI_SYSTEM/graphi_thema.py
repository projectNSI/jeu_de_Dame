# -*- coding:utf-8 -*-
import sys
import pygame
from pygame.locals import *

# 画面サイズ 600×500
SCREEN_SIZE = (600, 500)

# ボードの設定
BOARD_SIZE = 8
SQUARE_SIZE = 50
BOARD_OFFSET_X = (SCREEN_SIZE[0] - BOARD_SIZE * SQUARE_SIZE) // 2
BOARD_OFFSET_Y = (SCREEN_SIZE[1] - BOARD_SIZE * SQUARE_SIZE) // 2

# 色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# ピースの初期配置
def initialize_board():
    board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 1:
                if row < 3:
                    board[row][col] = 1  # 赤ピース
                elif row > 4:
                    board[row][col] = 2  # 青ピース
    return board

def draw_board(screen, board, font):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (BOARD_OFFSET_X + col * SQUARE_SIZE, BOARD_OFFSET_Y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            if board[row][col] == 1:
                pygame.draw.circle(screen, RED, (BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2, BOARD_OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 2 - 5)
            elif board[row][col] == 2:
                pygame.draw.circle(screen, BLUE, (BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2, BOARD_OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 2 - 5)
    
    # 横（列）のラベルを描画（上部）
    for col in range(BOARD_SIZE):
        label = font.render(str(col + 1), True, BLACK)
        screen.blit(label, (BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2 - label.get_width() // 2, BOARD_OFFSET_Y - 30))
    
    # 縦（行）のラベルを描画（左側）
    for row in range(BOARD_SIZE):
        label = font.render(str(row + 1), True, BLACK)
        screen.blit(label, (BOARD_OFFSET_X - 30, BOARD_OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2 - label.get_height() // 2))

def main():
    # Pygameの初期化
    pygame.init() 

    # タイトルバーの設定（大きさ600*500）
    screen = pygame.display.set_mode(SCREEN_SIZE)

    # タイトルバーの設定（表示する文字を「ゲーム」に変更）
    pygame.display.set_caption("Dame Game")  

    # フォントの設定
    font = pygame.font.Font(None, 36)

    # ボードの初期化
    board = initialize_board()

    while True:
        # 画面を緑色に塗りつぶし
        screen.fill(GREEN)

        # ボードを描画
        draw_board(screen, board, font)

        # テキストを表示（オプション）
        text = font.render("Dame Game", True, WHITE)
        screen.blit(text, (10, 10))

        # 画面を更新
        pygame.display.update()  

        # イベント処理
        for event in pygame.event.get():
            # 閉じるボタンが押されたら終了
            if event.type == QUIT:  
                pygame.quit()  # Pygameの終了(画面閉じられる)
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                # クリック位置を取得
                x, y = event.pos
                col = (x - BOARD_OFFSET_X) // SQUARE_SIZE
                row = (y - BOARD_OFFSET_Y) // SQUARE_SIZE
                if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                    print(f"Clicked on row {row}, col {col}")  # デバッグ用


if __name__ == "__main__":
    main()