# -*- coding:utf-8 -*-
import sys
import os
import importlib.util
import pygame
from pygame.locals import *

# dame de main.py をインポート（ファイル名に空白があるため特別な処理が必要）
dame_main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dame de main.py")
spec = importlib.util.spec_from_file_location("dame_de_main", dame_main_path)
dame_de_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(damedemain.py)

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

# 座標変換関数
def gui_to_logic(row, col):
    """GUI座標(row, col) → ロジック座標(col, ligne)"""
    return col, row

def logic_to_gui(col, ligne):
    """ロジック座標(col, ligne) → GUI座標(row, col)"""
    return ligne, col

# ピースの初期配置
def initialize_board():
    """dame de main.py の形式でボードを初期化"""
    c = BOARD_SIZE  # colonne
    l = BOARD_SIZE  # ligne
    N = 3  # ligne_de_pion
    
    # dame de main.py の形式: L[col][ligne] = [color, type, square_color]
    L = [[[0, 0, (1 + h % 2 - g % 2) % 2] for g in range(l)] for h in range(c)]
    
    for col in range(c):
        for ligne in range(l):
            if col < N:
                if L[col][ligne][2] == 1:  # 黒マス
                    L[col][ligne][0] = 1  # 黒い駒
                    L[col][ligne][1] = 1  # 通常の駒
            elif col > c - N - 1:
                if L[col][ligne][2] == 1:  # 黒マス
                    L[col][ligne][0] = 2  # 白い駒
                    L[col][ligne][1] = 1  # 通常の駒
    
    return L

def draw_board(screen, L, font):
    """L[col][ligne] 形式のボードを描画"""
    for col in range(BOARD_SIZE):
        for ligne in range(BOARD_SIZE):
            # マスの色
            square_color = L[col][ligne][2]
            color = WHITE if square_color == 0 else BLACK
            
            # 描画位置（GUI座標: col=x方向, ligne=y方向）
            x = BOARD_OFFSET_X + col * SQUARE_SIZE
            y = BOARD_OFFSET_Y + ligne * SQUARE_SIZE
            
            pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
            
            # 駒の描画
            piece_color = L[col][ligne][0]
            if piece_color != 0:
                center_x = x + SQUARE_SIZE // 2
                center_y = y + SQUARE_SIZE // 2
                radius = SQUARE_SIZE // 2 - 5
                
                # 色のマッピング: 1=黒→赤、2=白→青
                draw_color = RED if piece_color == 1 else BLUE
                pygame.draw.circle(screen, draw_color, (center_x, center_y), radius)
                
                # キングの場合、マークを追加（type == 2）
                piece_type = L[col][ligne][1]
                if piece_type == 2:
                    # キングマーク（小さな円）
                    pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), radius // 2)
    
    # 横（列）のラベルを描画（上部）
    for col in range(BOARD_SIZE):
        label = font.render(str(col + 1), True, BLACK)
        screen.blit(label, (BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2 - label.get_width() // 2, BOARD_OFFSET_Y - 30))
    
    # 縦（行）のラベルを描画（左側）
    for ligne in range(BOARD_SIZE):
        label = font.render(str(ligne + 1), True, BLACK)
        screen.blit(label, (BOARD_OFFSET_X - 30, BOARD_OFFSET_Y + ligne * SQUARE_SIZE + SQUARE_SIZE // 2 - label.get_height() // 2))

def run_gui():
    """GUI版のゲームを実行"""
    # Pygameの初期化
    pygame.init() 

    # タイトルバーの設定（大きさ600*500）
    screen = pygame.display.set_mode(SCREEN_SIZE)

    # タイトルバーの設定（表示する文字を「ゲーム」に変更）
    pygame.display.set_caption("Dame Game")  

    # フォントの設定
    font = pygame.font.Font(None, 36)

    # ボードの初期化（L[col][ligne] 形式）
    L = initialize_board()
    
    # ゲーム状態（dame de main.py の命名規則に合わせる）
    c = BOARD_SIZE  # colonne
    l = BOARD_SIZE  # ligne
    v = 0  # joueur (0=白、1=黒)

    while True:
        # 画面を緑色に塗りつぶし
        screen.fill(GREEN)

        # ボードを描画
        draw_board(screen, L, font)

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
                # クリック位置を取得（GUI座標）
                x, y = event.pos
                col = (x - BOARD_OFFSET_X) // SQUARE_SIZE
                row = (y - BOARD_OFFSET_Y) // SQUARE_SIZE
                if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                    # GUI座標をロジック座標に変換
                    col_logic, ligne_logic = gui_to_logic(row, col)
                    print(f"Clicked on GUI: row {row}, col {col} -> Logic: col {col_logic}, ligne {ligne_logic}")  # デバッグ用


def run_terminal():
    """ターミナル版のゲームを実行"""
    import json
    
    # règle.json を読み込む
    règle_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "règle.json")
    with open(règle_path, 'r', encoding='utf-8') as f:
        LJ = json.load(f)[0]
        L = LJ['Liste']
        c = LJ['colonne']
        l = LJ['ligne']
        N = LJ['ligne_de_pion']
    
    print(L, c, l, N)
    L, c, l, N = dame_de_main.creation_de_jeu(L, c, l, N)
    
    J = [L, c, l, N]
    v = 0
    
    while dame_de_main.team_exist(L, 1) and dame_de_main.team_exist(L, 2):
        resultat = dame_de_main.tour(L, c, l, v)
        v = (v + 1) % 2


def show_menu():
    """起動時に表示されるメニュー"""
    print("=" * 50)
    print("     Jeu de Dame - ダマゲーム")
    print("=" * 50)
    print()
    print("遊び方を選択してください:")
    print("  1. ターミナル版 (Terminal)")
    print("  2. GUI版 (Graphical)")
    print("  0. 終了 (Exit)")
    print()
    
    while True:
        try:
            choice = input("選択してください (1/2/0): ").strip()
            
            if choice == "1":
                print("\nターミナル版を起動します...\n")
                run_terminal()
                break
            elif choice == "2":
                print("\nGUI版を起動します...\n")
                run_gui()
                break
            elif choice == "0":
                print("終了します。")
                sys.exit(0)
            else:
                print("無効な選択です。1、2、または0を入力してください。")
        except KeyboardInterrupt:
            print("\n\n終了します。")
            sys.exit(0)
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            print("もう一度お試しください。")


def main():
    """メインエントリーポイント"""
    show_menu()


if __name__ == "__main__":
    main()