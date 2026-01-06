import pygame
import sys

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

def main():
    # Pygame関連
    pygame.init()                                                   # 初期化
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # 画面作成
    pygame.display.set_caption("PygameSample")                      # 画面タイトル 
    clock = pygame.time.Clock()                                     # 時計作成(FPS制御用)
    font = pygame.font.Font(None, 36)   

# Main関数呼び出し
if __name__ == "__main__":
    main()