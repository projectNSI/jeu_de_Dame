# GUI-Logic 統合計画書
## Jeu de Dame プロジェクト

**作成日:** 2026-01-15  
**目的:** `dame de main.py`（ロジック）と`graphi_thema.py`（GUI）の統合

---

## 📋 目次

1. [現状分析](#現状分析)
2. [統合戦略](#統合戦略)
3. [データ構造の統一](#データ構造の統一)
4. [実装ステップ](#実装ステップ)
5. [ファイル構成](#ファイル構成)
6. [必要な修正リスト](#必要な修正リスト)
7. [実装コード](#実装コード)
8. [テスト計画](#テスト計画)
9. [タイムライン](#タイムライン)

---

## 1. 現状分析

### 1.1 既存ファイルの状態

#### `dame de main.py` (190行)
- **役割:** ゲームロジック
- **強み:**
  - ✅ 移動判定ロジック（`jeu_possible`）
  - ✅ 所有権確認（`is_friendly`）
  - ✅ 勝敗判定（`team_exist`）
  - ✅ キング機能あり
- **弱点:**
  - ❌ 14個のバグが存在
  - ❌ `input()`による対話型入力
  - ❌ データ構造が複雑（3次元リスト）
  - ❌ インデックスが混乱（col/ligne）

#### `GUI_SYSTEM/graphi_thema.py` (100行)
- **役割:** グラフィカル表示
- **強み:**
  - ✅ Pygameによる描画
  - ✅ ボード表示
  - ✅ マウスクリック検知
  - ✅ シンプルなデータ構造
- **弱点:**
  - ❌ ゲームロジックなし
  - ❌ 駒の移動機能なし
  - ❌ 勝敗判定なし
  - ❌ キング機能なし

### 1.2 主な違い

| 項目 | dame de main.py | graphi_thema.py |
|------|-----------------|-----------------|
| **データ構造** | `L[col][ligne][3要素]` | `board[row][col]` |
| **インデックス順** | 列 → 行 | 行 → 列 |
| **駒の色** | 1=黒, 2=白 | 1=赤, 2=青 |
| **マス情報** | `[色, タイプ, マス色]` | 駒の色のみ |
| **入力方式** | `input()` | マウスクリック |
| **キング** | あり（type=2） | なし |

---

## 2. 統合戦略

### 2.1 選択したアプローチ: **ラッパー方式**

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  dame_gui.py (新規作成)                         │
│  ┌──────────────────────────────────────┐      │
│  │  Pygameメインループ                  │      │
│  │  - 画面描画                           │      │
│  │  - イベント処理                       │      │
│  │  - ゲーム状態管理                     │      │
│  └────────┬──────────────────┬───────────┘      │
│           │                  │                  │
│           ↓                  ↓                  │
│  ┌────────────────┐  ┌────────────────┐        │
│  │ GUI Helper     │  │ 描画機能       │        │
│  │ Functions      │  │ - draw_board   │        │
│  └────────┬───────┘  │ - draw_pieces  │        │
│           │          └────────────────┘        │
│           ↓                                     │
│  ┌─────────────────────────────────────┐       │
│  │  dame de main.py をインポート        │       │
│  │  import dame_de_main as logic       │       │
│  └────────┬────────────────────────────┘       │
│           ↓                                     │
└───────────┼─────────────────────────────────────┘
            │
            ↓
┌───────────────────────────────────────────────┐
│  dame de main.py (既存 + 追加)                │
│  ┌─────────────────────────────────────┐     │
│  │ 既存のロジック関数（変更なし）       │     │
│  │ - creation_de_jeu()                 │     │
│  │ - is_friendly()                     │     │
│  │ - jeu_possible()                    │     │
│  │ - team_exist()                      │     │
│  │ - tour() ※使用しない                │     │
│  └─────────────────────────────────────┘     │
│                                               │
│  ┌─────────────────────────────────────┐     │
│  │ 【新規追加】GUI用インターフェース   │     │
│  │ - get_valid_moves_gui()             │     │
│  │ - execute_move_gui()                │     │
│  │ - check_game_status()               │     │
│  │ - init_board_gui()                  │     │
│  └─────────────────────────────────────┘     │
└───────────────────────────────────────────────┘
```

### 2.2 統合の理由

1. **既存コードの保護**: `dame de main.py` のロジックを変更しない
2. **段階的実装**: 少しずつ機能を追加できる
3. **テスト容易性**: GUI とロジックを個別にテスト可能
4. **保守性**: 責任を分離（GUI=表示、Logic=計算）

---

## 3. データ構造の統一

### 3.1 問題点

`dame de main.py` と `graphi_thema.py` でデータ構造が異なります。

**dame de main.py:**
```python
L[col][ligne] = [駒の色, 駒のタイプ, マスの色]
# 例: L[3][5] = [1, 1, 1]  # 黒い駒、通常、黒マス
```

**graphi_thema.py:**
```python
board[row][col] = 駒の色
# 例: board[5][3] = 1  # 赤い駒
```

### 3.2 解決策: アダプターパターン

GUI層でデータ変換を行います。

```python
class BoardAdapter:
    """dame de main.pyの構造をGUIで使用"""
    
    def __init__(self):
        # dame de main.pyの形式を使用
        # L[col][ligne] = [color, type, square_color]
        self.L = self._init_logic_board()
    
    def _init_logic_board(self):
        """ロジック形式でボードを初期化"""
        L = [[[0, 0, (1 + h % 2 - g % 2) % 2] 
              for g in range(8)] 
              for h in range(8)]
        
        N = 3
        for col in range(8):
            for ligne in range(8):
                if col < N and L[col][ligne][2] == 1:
                    L[col][ligne][0] = 1  # 黒い駒
                    L[col][ligne][1] = 1  # 通常の駒
                elif col > 8 - N - 1 and L[col][ligne][2] == 1:
                    L[col][ligne][0] = 2  # 白い駒
                    L[col][ligne][1] = 1
        return L
    
    def get_piece_at(self, row, col):
        """GUI座標(row, col)から駒情報を取得"""
        # GUIは row, col の順
        # ロジックは col, ligne の順
        return self.L[col][row]
    
    def set_piece_at(self, row, col, color, piece_type=1):
        """GUI座標で駒を設定"""
        self.L[col][row][0] = color
        self.L[col][row][1] = piece_type
```

### 3.3 座標変換マッピング

```
GUI描画:          ロジック処理:
row, col    →    col, ligne

例:
GUI: board[5][3]  →  Logic: L[3][5]
     ↑    ↑               ↑    ↑
    row  col            col  ligne
```

---

## 4. 実装ステップ

### フェーズ1: 基盤構築（優先度：高）

#### ステップ 1.1: `dame de main.py` のバグ修正
**時間:** 2時間

修正が必要な致命的バグ（5個）:
1. `jeu_possible()` でリストJを初期化
2. 論理条件を修正（`or` → `and`）
3. インデックス変換（1-based → 0-based）※GUI用関数では不要
4. 変数iの再利用を修正
5. キング用のリストJを初期化

```python
# 修正例:
def jeu_possible(L, c, l, diags, v, t=None):
    """移動可能性を判定"""
    # 修正1: リストを初期化
    if L[c][l][1] == 1:  # 通常の駒
        J = [0] * len(diags)  # ← 追加
        for i in range(len(diags)):
            try:
                # 範囲チェックを追加
                new_c = c + diags[i][0]
                new_l = l + diags[i][1]
                if not (0 <= new_c < len(L) and 0 <= new_l < len(L[0])):
                    J[i] = 0
                    continue
                
                if L[new_c][new_l][0] == (2 - v):
                    # 捕獲可能かチェック
                    capture_c = c + 2 * diags[i][0]
                    capture_l = l + 2 * diags[i][1]
                    if (0 <= capture_c < len(L) and 
                        0 <= capture_l < len(L[0]) and
                        L[capture_c][capture_l][0] == 0):
                        J[i] = 1  # 捕獲可能
                    else:
                        J[i] = 0
                elif L[new_c][new_l][0] == 0:
                    J[i] = 2  # 通常移動
                else:
                    J[i] = 0
            except IndexError:
                J[i] = 0
        return J
    
    elif L[c][l][1] == 2:  # キング
        J = [[0 for _ in range(len(L[0]))] for _ in range(len(L))]  # ← 追加
        # キングのロジック...
        return J
    
    return []  # デフォルト
```

#### ステップ 1.2: GUI用インターフェース関数を追加
**時間:** 3時間

`dame de main.py` の末尾に追加:

```python
# ============================================
# GUI用インターフェース関数（新規追加）
# ============================================

def init_board_gui(board_size=8, num_rows=3):
    """
    GUI用：ボードを初期化
    
    Returns:
        L[col][ligne] = [color, type, square_color]
    """
    L = [[[0, 0, (1 + h % 2 - g % 2) % 2] 
          for g in range(board_size)] 
          for h in range(board_size)]
    
    for col in range(board_size):
        for ligne in range(board_size):
            if col < num_rows:
                if L[col][ligne][2] == 1:  # 黒いマス
                    L[col][ligne][0] = 1  # 黒い駒
                    L[col][ligne][1] = 1  # 通常の駒
            elif col > board_size - num_rows - 1:
                if L[col][ligne][2] == 1:
                    L[col][ligne][0] = 2  # 白い駒
                    L[col][ligne][1] = 1
    
    return L


def get_valid_moves_gui(L, col, ligne, player):
    """
    GUI用：指定した駒の可能な移動を取得
    
    Parameters:
        L: ボード
        col, ligne: 駒の位置（0-based）
        player: 1=黒, 2=白
    
    Returns:
        [(col, ligne, move_type), ...]
        move_type: 'capture' または 'move'
    """
    v = 0 if player == 2 else 1  # プレイヤー番号を変換
    
    # 自分の駒かチェック
    if not is_friendly(L, col, ligne, v):
        return []
    
    diags = [[-1, 1], [1, 1], [-1, -1], [1, -1]]
    
    try:
        J = jeu_possible(L, col, ligne, diags, v, None)
    except:
        return []
    
    moves = []
    
    # 通常の駒
    if L[col][ligne][1] == 1:
        if not isinstance(J, list) or len(J) == 0:
            return []
        
        for i in range(len(J)):
            if J[i] == 1:  # 捕獲可能
                new_col = col + 2 * diags[i][0]
                new_ligne = ligne + 2 * diags[i][1]
                if 0 <= new_col < len(L) and 0 <= new_ligne < len(L[0]):
                    moves.append((new_col, new_ligne, 'capture'))
            elif J[i] == 2:  # 通常移動
                new_col = col + diags[i][0]
                new_ligne = ligne + diags[i][1]
                if 0 <= new_col < len(L) and 0 <= new_ligne < len(L[0]):
                    # 方向制限をチェック
                    if player == 1 and i in [0, 1]:  # 黒は前方のみ
                        moves.append((new_col, new_ligne, 'move'))
                    elif player == 2 and i in [2, 3]:  # 白は後方のみ
                        moves.append((new_col, new_ligne, 'move'))
    
    # キング
    elif L[col][ligne][1] == 2:
        # キングは全方向に移動可能
        if isinstance(J, list) and len(J) > 0:
            for i in range(len(J)):
                for j in range(len(J[i])):
                    if J[i][j] == 1:  # 捕獲
                        moves.append((i, j, 'capture'))
                    elif J[i][j] == 2:  # 移動
                        moves.append((i, j, 'move'))
    
    return moves


def execute_move_gui(L, from_col, from_ligne, to_col, to_ligne, player):
    """
    GUI用：駒を移動する
    
    Parameters:
        L: ボード
        from_col, from_ligne: 元の位置
        to_col, to_ligne: 移動先
        player: 1=黒, 2=白
    
    Returns:
        bool: 移動が成功したか
    """
    # 可能な移動を取得
    valid_moves = get_valid_moves_gui(L, from_col, from_ligne, player)
    
    # 目的地が有効な移動先かチェック
    for move in valid_moves:
        if move[0] == to_col and move[1] == to_ligne:
            move_type = move[2]
            
            # 捕獲の場合、中間の駒を削除
            if move_type == 'capture':
                mid_col = (from_col + to_col) // 2
                mid_ligne = (from_ligne + to_ligne) // 2
                L[mid_col][mid_ligne][0] = 0
                L[mid_col][mid_ligne][1] = 0
            
            # 駒を移動
            L[to_col][to_ligne][0] = L[from_col][from_ligne][0]
            L[to_col][to_ligne][1] = L[from_col][from_ligne][1]
            L[from_col][from_ligne][0] = 0
            L[from_col][from_ligne][1] = 0
            
            # キングへの昇格チェック
            if L[to_col][to_ligne][1] == 1:  # 通常の駒
                if (player == 1 and to_col == 7) or (player == 2 and to_col == 0):
                    L[to_col][to_ligne][1] = 2  # キングに昇格
            
            return True
    
    return False


def check_game_status_gui(L):
    """
    GUI用：ゲームの状態をチェック
    
    Returns:
        0: ゲーム継続
        1: 黒（player 1）の勝利
        2: 白（player 2）の勝利
    """
    black_exists = team_exist(L, 1)
    white_exists = team_exist(L, 2)
    
    if not black_exists:
        return 2  # 白の勝利
    elif not white_exists:
        return 1  # 黒の勝利
    else:
        return 0  # ゲーム継続
```

#### ステップ 1.3: 新規GUIファイルを作成
**時間:** 4時間

`dame_gui.py` を作成（後述の実装コード参照）

---

### フェーズ2: 基本機能実装（優先度：高）

#### ステップ 2.1: ボード描画
- チェッカーボードの描画
- 駒の描画
- ラベルの表示

#### ステップ 2.2: 駒の選択
- マウスクリックで駒を選択
- 選択した駒をハイライト
- 可能な移動先を表示

#### ステップ 2.3: 駒の移動
- クリックで移動先を指定
- 移動の実行
- プレイヤーの交代

#### ステップ 2.4: 捕獲機能
- 敵駒を飛び越えて移動
- 捕獲した駒を削除

---

### フェーズ3: 高度な機能（優先度：中）

#### ステップ 3.1: キング機能
- 最終行到達時に昇格
- キングの表示（二重円など）
- キングの移動範囲

#### ステップ 3.2: 勝敗判定
- 駒がなくなったら終了
- 勝者の表示
- ゲームリセット機能

#### ステップ 3.3: UI改善
- 現在のプレイヤー表示
- 移動履歴
- アニメーション

---

### フェーズ4: 追加機能（優先度：低）

#### ステップ 4.1: ゲーム設定
- ボードサイズの変更
- 駒の配置行数の変更
- 色のカスタマイズ

#### ステップ 4.2: 連続捕獲
- 1ターンで複数回捕獲
- 強制捕獲ルール

#### ステップ 4.3: セーブ/ロード
- ゲーム状態の保存
- JSON形式での保存

---

## 5. ファイル構成

```
jeu_de_Dame/
│
├── dame de main.py          # 既存ロジック + GUI用関数追加
│   ├── [既存] creation_de_jeu()
│   ├── [既存] is_friendly()
│   ├── [既存] jeu_possible()  ← バグ修正
│   ├── [既存] team_exist()
│   ├── [既存] tour()
│   ├── [新規] init_board_gui()
│   ├── [新規] get_valid_moves_gui()
│   ├── [新規] execute_move_gui()
│   └── [新規] check_game_status_gui()
│
├── dame_gui.py              # 新規作成：GUIメイン
│   ├── DameGUI クラス
│   │   ├── __init__()
│   │   ├── init_board()
│   │   ├── draw_board()
│   │   ├── draw_pieces()
│   │   ├── highlight_selection()
│   │   ├── show_valid_moves()
│   │   ├── handle_click()
│   │   ├── update_game_state()
│   │   └── run()
│   └── main()
│
├── GUI_SYSTEM/
│   └── graphi_thema.py      # 既存GUI（参考用、使用しない）
│
├── logic/
│   ├── analyse_logique_dame.md
│   └── analyse_logique_dame_ja.md
│
├── integration_plan_ja.md   # 本ドキュメント
│
└── règle.json               # ゲーム設定
```

---

## 6. 必要な修正リスト

### 6.1 dame de main.py の修正

| 優先度 | 行番号 | 問題 | 修正内容 |
|--------|--------|------|----------|
| 🔴 高 | 55 | Jが未初期化 | `J = [0] * len(diags)` を追加 |
| 🔴 高 | 66 | Jが未初期化（キング） | `J = [[0]*len(L[0]) for _ in range(len(L))]` |
| 🔴 高 | 10,13,16 | 条件式が常にTrue | `or` → `and` に変更 |
| 🔴 高 | 107 | 変数iの再利用 | ループ変数を `idx` に変更 |
| 🟡 中 | 156 | プレイヤー交代 | `v = (v + 1) % 2` に修正 |
| 🟡 中 | 96-97 | print in input | `input()` から `print()` を削除 |
| 🟢 低 | 全体 | 例外処理不足 | try-except を追加 |

### 6.2 新規作成ファイル

- `dame_gui.py`: 完全に新規作成
- `integration_plan_ja.md`: 本ドキュメント

---

## 7. 実装コード

### 7.1 dame_gui.py（完全版）

```python
# -*- coding:utf-8 -*-
"""
Jeu de Dame - GUI版
dame de main.py のロジックを使用したグラフィカルインターフェース
"""

import sys
import pygame
from pygame.locals import *

# ロジックをインポート
try:
    import dame_de_main as logic
except ImportError:
    print("エラー: dame de main.py が見つかりません")
    sys.exit(1)

# ============================================
# 定数定義
# ============================================

# 画面設定
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# ボード設定
BOARD_SIZE = 8
SQUARE_SIZE = 60
BOARD_OFFSET_X = (SCREEN_WIDTH - BOARD_SIZE * SQUARE_SIZE) // 2
BOARD_OFFSET_Y = (SCREEN_HEIGHT - BOARD_SIZE * SQUARE_SIZE) // 2

# 色定義
COLOR_WHITE_SQUARE = (240, 217, 181)  # ベージュ
COLOR_BLACK_SQUARE = (181, 136, 99)   # ブラウン
COLOR_BG = (34, 139, 34)              # 緑
COLOR_HIGHLIGHT = (255, 255, 0)       # 黄色（選択中）
COLOR_VALID_MOVE = (0, 255, 0)        # 緑（移動可能）
COLOR_VALID_CAPTURE = (255, 165, 0)   # オレンジ（捕獲可能）
COLOR_PIECE_BLACK = (255, 0, 0)       # 赤（黒駒）
COLOR_PIECE_WHITE = (0, 0, 255)       # 青（白駒）
COLOR_KING_MARK = (255, 215, 0)       # 金（キングマーク）
COLOR_TEXT = (255, 255, 255)          # 白（テキスト）

# フォント設定
FONT_SIZE = 32
SMALL_FONT_SIZE = 24


# ============================================
# DameGUI クラス
# ============================================

class DameGUI:
    """チェッカーゲームのGUIクラス"""
    
    def __init__(self):
        """初期化"""
        # Pygame初期化
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Jeu de Dame - チェッカー")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
        
        # ゲーム状態
        self.L = logic.init_board_gui(BOARD_SIZE, 3)
        self.current_player = 1  # 1=黒（赤）, 2=白（青）
        self.selected = None     # (col, ligne) または None
        self.valid_moves = []    # [(col, ligne, move_type), ...]
        self.game_over = False
        self.winner = None
        
    def get_square_from_pos(self, pos):
        """
        画面座標からボード座標を取得
        
        Parameters:
            pos: (x, y) 画面座標
        
        Returns:
            (col, ligne) または None
        """
        x, y = pos
        
        # ボード範囲外チェック
        if (x < BOARD_OFFSET_X or x >= BOARD_OFFSET_X + BOARD_SIZE * SQUARE_SIZE or
            y < BOARD_OFFSET_Y or y >= BOARD_OFFSET_Y + BOARD_SIZE * SQUARE_SIZE):
            return None
        
        # GUIは row, col だが、ロジックは col, ligne
        # 画面のx座標 → col, y座標 → ligne
        col = (x - BOARD_OFFSET_X) // SQUARE_SIZE
        ligne = (y - BOARD_OFFSET_Y) // SQUARE_SIZE
        
        # 実際には、画面の行はligneに対応
        # 修正: row → ligne (y方向), col → col (x方向)
        # しかし dame de main.py は L[col][ligne]
        # 画面上: 上から下が ligne (row相当), 左から右が col
        
        # 正しいマッピング:
        # 画面x → col (横方向)
        # 画面y → ligne (縦方向)
        # しかし、L[col][ligne]なので変換不要
        
        return (col, ligne)
    
    def draw_board(self):
        """ボードを描画"""
        for col in range(BOARD_SIZE):
            for ligne in range(BOARD_SIZE):
                # マスの位置
                x = BOARD_OFFSET_X + col * SQUARE_SIZE
                y = BOARD_OFFSET_Y + ligne * SQUARE_SIZE
                
                # マスの色（チェッカーパターン）
                square_color = self.L[col][ligne][2]
                if square_color == 0:
                    color = COLOR_WHITE_SQUARE
                else:
                    color = COLOR_BLACK_SQUARE
                
                # マスを描画
                pygame.draw.rect(self.screen, color, 
                               (x, y, SQUARE_SIZE, SQUARE_SIZE))
                
                # 枠線
                pygame.draw.rect(self.screen, (0, 0, 0), 
                               (x, y, SQUARE_SIZE, SQUARE_SIZE), 1)
    
    def draw_highlights(self):
        """選択中のマスと可能な移動先をハイライト"""
        # 選択中のマス
        if self.selected:
            col, ligne = self.selected
            x = BOARD_OFFSET_X + col * SQUARE_SIZE
            y = BOARD_OFFSET_Y + ligne * SQUARE_SIZE
            pygame.draw.rect(self.screen, COLOR_HIGHLIGHT, 
                           (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)
        
        # 可能な移動先
        for move in self.valid_moves:
            col, ligne, move_type = move
            x = BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
            y = BOARD_OFFSET_Y + ligne * SQUARE_SIZE + SQUARE_SIZE // 2
            
            if move_type == 'capture':
                color = COLOR_VALID_CAPTURE
                radius = 15
            else:
                color = COLOR_VALID_MOVE
                radius = 12
            
            pygame.draw.circle(self.screen, color, (x, y), radius)
    
    def draw_pieces(self):
        """駒を描画"""
        for col in range(BOARD_SIZE):
            for ligne in range(BOARD_SIZE):
                piece_color = self.L[col][ligne][0]
                piece_type = self.L[col][ligne][1]
                
                if piece_color == 0:  # 空のマス
                    continue
                
                # 駒の中心座標
                x = BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
                y = BOARD_OFFSET_Y + ligne * SQUARE_SIZE + SQUARE_SIZE // 2
                radius = SQUARE_SIZE // 2 - 8
                
                # 駒の色
                if piece_color == 1:
                    color = COLOR_PIECE_BLACK
                else:
                    color = COLOR_PIECE_WHITE
                
                # 駒を描画
                pygame.draw.circle(self.screen, color, (x, y), radius)
                pygame.draw.circle(self.screen, (0, 0, 0), (x, y), radius, 2)
                
                # キングの場合、マークを追加
                if piece_type == 2:
                    pygame.draw.circle(self.screen, COLOR_KING_MARK, 
                                     (x, y), radius // 2)
                    # 王冠マークを簡易的に
                    pygame.draw.circle(self.screen, color, 
                                     (x, y), radius // 2 - 3)
    
    def draw_ui(self):
        """UI要素を描画"""
        # 現在のプレイヤー表示
        if not self.game_over:
            player_name = "Rouge (Noir)" if self.current_player == 1 else "Bleu (Blanc)"
            text = self.font.render(f"Tour: {player_name}", True, COLOR_TEXT)
            self.screen.blit(text, (10, 10))
        else:
            # ゲーム終了時
            winner_name = "Rouge (Noir)" if self.winner == 1 else "Bleu (Blanc)"
            text = self.font.render(f"{winner_name} gagne!", True, COLOR_TEXT)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 30))
            self.screen.blit(text, text_rect)
            
            # リスタートの案内
            restart_text = self.small_font.render("Appuyez sur R pour rejouer", 
                                                 True, COLOR_TEXT)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            self.screen.blit(restart_text, restart_rect)
    
    def handle_click(self, pos):
        """マウスクリックを処理"""
        if self.game_over:
            return
        
        square = self.get_square_from_pos(pos)
        if square is None:
            return
        
        col, ligne = square
        
        # 駒が選択されていない場合
        if self.selected is None:
            piece_color = self.L[col][ligne][0]
            
            # 自分の駒をクリックしたか確認
            if piece_color == self.current_player:
                self.selected = (col, ligne)
                # 可能な移動を取得
                self.valid_moves = logic.get_valid_moves_gui(
                    self.L, col, ligne, self.current_player
                )
                print(f"駒を選択: {square}, 可能な移動: {len(self.valid_moves)}個")
        else:
            # 駒が選択されている場合
            from_col, from_ligne = self.selected
            
            # 同じ駒をクリック→選択解除
            if (col, ligne) == self.selected:
                self.selected = None
                self.valid_moves = []
                print("選択を解除")
                return
            
            # 別の自分の駒をクリック→選択を変更
            if self.L[col][ligne][0] == self.current_player:
                self.selected = (col, ligne)
                self.valid_moves = logic.get_valid_moves_gui(
                    self.L, col, ligne, self.current_player
                )
                print(f"駒を再選択: {square}")
                return
            
            # 移動を試みる
            success = logic.execute_move_gui(
                self.L, from_col, from_ligne, col, ligne, self.current_player
            )
            
            if success:
                print(f"移動成功: {self.selected} → {square}")
                
                # プレイヤーを交代
                self.current_player = 3 - self.current_player
                self.selected = None
                self.valid_moves = []
                
                # 勝敗チェック
                status = logic.check_game_status_gui(self.L)
                if status != 0:
                    self.game_over = True
                    self.winner = status
                    print(f"ゲーム終了: プレイヤー{status}の勝利")
            else:
                print(f"移動失敗: {square} は有効な移動先ではありません")
    
    def reset_game(self):
        """ゲームをリセット"""
        self.L = logic.init_board_gui(BOARD_SIZE, 3)
        self.current_player = 1
        self.selected = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        print("ゲームをリセットしました")
    
    def run(self):
        """メインゲームループ"""
        running = True
        
        while running:
            # 背景を塗りつぶし
            self.screen.fill(COLOR_BG)
            
            # 描画
            self.draw_board()
            self.draw_highlights()
            self.draw_pieces()
            self.draw_ui()
            
            # イベント処理
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                
                elif event.type == MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                
                elif event.type == KEYDOWN:
                    # Rキーでリスタート
                    if event.key == K_r:
                        self.reset_game()
            
            # 画面更新
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS
        
        # 終了
        pygame.quit()
        sys.exit()


# ============================================
# メイン
# ============================================

def main():
    """メイン関数"""
    game = DameGUI()
    game.run()


if __name__ == "__main__":
    main()
```

---

## 8. テスト計画

### 8.1 単体テスト

| テスト項目 | 対象関数 | テスト内容 |
|-----------|---------|-----------|
| ボード初期化 | `init_board_gui()` | 正しい位置に駒が配置されているか |
| 所有権確認 | `is_friendly()` | 正しいプレイヤーの駒を識別できるか |
| 移動可能性 | `get_valid_moves_gui()` | 通常移動/捕獲が正しく計算されるか |
| 移動実行 | `execute_move_gui()` | 駒が正しく移動するか |
| キング昇格 | `execute_move_gui()` | 最終行で昇格するか |
| 勝敗判定 | `check_game_status_gui()` | 駒がなくなったら勝利判定されるか |

### 8.2 統合テスト

1. **基本フロー**
   - ゲーム開始 → 駒選択 → 移動 → プレイヤー交代

2. **捕獲フロー**
   - 駒選択 → 敵を飛び越えて移動 → 敵駒が削除される

3. **キングフロー**
   - 通常駒で最終行到達 → キングに昇格 → 全方向移動可能

4. **勝利フロー**
   - すべての敵駒を捕獲 → 勝利表示 → リセット

### 8.3 UIテスト

- マウスクリックの反応
- ハイライトの表示
- 駒の描画
- テキスト表示

---

## 9. タイムライン

### Week 1: 基盤構築
- **Day 1-2**: `dame de main.py` のバグ修正
- **Day 3-4**: GUI用インターフェース関数の追加
- **Day 5-7**: `dame_gui.py` の基本実装

### Week 2: 機能実装
- **Day 1-2**: ボード描画と駒の表示
- **Day 3-4**: 駒の選択と移動
- **Day 5-7**: 捕獲機能とプレイヤー交代

### Week 3: 高度な機能
- **Day 1-3**: キング機能
- **Day 4-5**: 勝敗判定
- **Day 6-7**: UI改善

### Week 4: テストと調整
- **Day 1-3**: 単体テスト
- **Day 4-5**: 統合テスト
- **Day 6-7**: バグ修正と最終調整

---

## 10. 既知の課題と対策

### 課題 1: データ構造の違い
**問題:** `L[col][ligne]` vs `board[row][col]`  
**対策:** アダプターパターンで変換

### 課題 2: インデックスの混乱
**問題:** 0-based vs 1-based  
**対策:** GUI層ですべて0-basedに統一

### 課題 3: キングの移動範囲
**問題:** `jeu_possible()` のキング処理が複雑  
**対策:** まずは通常駒で動作確認、その後キングを実装

### 課題 4: 連続捕獲
**問題:** 1ターンで複数回捕獲するルール  
**対策:** フェーズ4で実装（オプション機能）

---

## 11. 次のアクション

### 即座に実行

1. ✅ 本ドキュメントの作成（完了）
2. ⬜ `dame de main.py` のバグ修正を開始
3. ⬜ GUI用インターフェース関数を追加
4. ⬜ `dame_gui.py` を作成して基本機能を実装

### 確認事項

- [ ] `dame de main.py` の既存main()をコメントアウトするか？
- [ ] `règle.json` の構造を確認（使用する場合）
- [ ] 駒の色を変更するか？（赤/青 vs 黒/白）

---

## 12. 参考資料

- `logic/analyse_logique_dame_ja.md` - ロジックの詳細分析
- `GUI_SYSTEM/graphi_thema.py` - 既存GUI実装
- `dame de main.py` - 既存ロジック実装

---

**作成者:** AI Assistant  
**最終更新:** 2026-01-15  
**バージョン:** 1.0

