# GUIコアロジック解説

`src/gui_system/dame_gui_ctk.py` の設計と主要ロジックを解説する。

---

## 1. 全体アーキテクチャ

```
┌─────────────────────────────────────────┐
│               DameGUI (CTk)             │
│                                         │
│  _show_menu()  →  _start_game()         │
│       │                │                │
│  メインメニュー    _build_ui()          │
│  (モード/テーマ     ├─ 盤面描画         │
│   ロード/開始)      ├─ 履歴パネル       │
│                     └─ ログパネル       │
│                                         │
│  damedemain.py の関数を呼び出し:        │
│  - is_friendly()  駒の所有者判定        │
│  - jeu_possible() 可能な移動計算        │
│  - team_exist()   チーム存在確認        │
└─────────────────────────────────────────┘
```

## 2. 画面フロー

```
起動 → メインメニュー → ゲーム画面
                ↑           │
                └── 🏠 Menu ─┘
```

1. アプリ起動時に `_show_menu()` でメインメニューを表示
2. 「Commencer la partie」でモードとテーマを選んでゲーム開始
3. 「Charger une partie」でJSON読み込みから復帰
4. ゲーム中に「🏠 Menu」ボタンでメニューに戻れる

## 3. データ構造

### 盤面 `self.L`

```python
L[col][ligne] = [couleur_pion, type_pion, couleur_case]
```

| フィールド | 値 | 意味 |
|-----------|-----|------|
| `couleur_pion` | 0 | 駒なし |
| | 1 | 黒の駒 |
| | 2 | 白の駒 |
| `type_pion` | 0 | 駒なし |
| | 1 | 通常の駒（ポーン） |
| | 2 | ダム（クイーン） |
| `couleur_case` | 0 | 白マス（使用しない） |
| | 1 | 黒マス（駒を置ける） |

### プレイヤーマッピング

| GUI側 | `current_player` | damedemain側 `v` | 駒の色 |
|-------|------------------|------------------|--------|
| 黒（先手） | 1 | 1 | `L[c][l][0] == 1` |
| 白（後手） | 2 | 0 | `L[c][l][0] == 2` |

### 対角線ベクトル

```python
DIAGS = [[-1, 1], [1, 1], [-1, -1], [1, -1]]
#         左上      右上     左下      右下
```

- 白（`v=0`）の前方: DIAGS[0], DIAGS[2]（列が減る方向）
- 黒（`v=1`）の前方: DIAGS[1], DIAGS[3]（列が増える方向）

## 4. ホバーシステム

駒にマウスを乗せると移動可能なマスを表示する仕組み。

### イベントフロー

```
マウスが駒の上に入る
  → _on_enter(col, ligne)
    → _cancel_clear()        # 既存のクリア予約をキャンセル
    → is_friendly() で自分の駒か確認
    → jeu_possible() で移動先を取得
    → get_moves() で座標リストに変換
    → _apply_hover() でハイライト適用

マウスが盤面外に出る
  → board_frame <Leave>
    → _schedule_clear()      # 60ms後にクリア予約
      → 60ms以内に子ボタンのEnterが来なければクリア実行
```

### ハイライト色

| 色 | 定数 | 用途 |
|----|------|------|
| 緑（暗） | `HL_PIECE` | 選択中の駒 |
| 緑（明） | `HL_MOVE` | 移動先/捕獲着地点 |
| オレンジ | `HL_CHAIN` | 連続捕獲中の駒 |
| 金 | `HL_HINT` | ヒント表示 |
| 黄土色 | `HL_LAST_FROM/TO` | 直前の移動元/先 |

### _apply_hover() の差分更新

```python
def _apply_hover(self, piece, moves):
    old = {前回ハイライトされていたセル}
    new_map = {今回ハイライトするセル → 色}
    
    for cell in old:
        if cell not in new_map:
            元の色に戻す
    for cell, color in new_map.items():
        新しい色を適用
```

全マスを再描画するのではなく、変更があったセルのみ更新するためパフォーマンスが良い。

## 5. 移動実行 `_execute_move()`

人間のクリックとAIの両方がこの共通メソッドを使う。

```
_execute_move(fc, fl, tc, tl, is_cap)
  │
  ├─ 状態保存（連鎖中でなければ）
  ├─ ログ記録（is_friendly, jeu_possible）
  ├─ ホバークリア
  ├─ do_move() で盤面更新
  ├─ 捕獲時: スコア加算 + フラッシュ演出
  ├─ 昇格判定（列端に到達したか）
  ├─ 履歴追加
  │
  ├─ 連続捕獲チェック:
  │   └─ 可能 → _chain_piece 設定、ホバー自動表示、return True
  │
  └─ 連続捕獲なし → 効果音 → _next_turn()、return False
```

## 6. 連続捕獲（Rafle）

ジュ・ド・ダムの重要ルール。捕獲後、同じ駒がさらに捕獲できる場合は強制的に続行。

```
捕獲実行
  → _has_captures(新位置) をチェック
  → True の場合:
      _chain_piece = (tc, tl)
      ホバーを自動で捕獲先のみ表示
      _on_enter() は他の駒への切替を無効化
      
  → 人間: 移動先をクリック → 再び _execute_move()
  → AI:   _ai_chain_step() で自動選択、450ms遅延で実行
```

## 7. 強制捕獲ルール

```python
def _on_enter(self, col, ligne):
    ...
    if _any_capture_available(L, v, self.c, self.l):
        moves = [m for m in moves if m[2]]
        if not moves:
            return
```

いずれかの駒で捕獲可能な場合、通常移動は一切表示されない。

## 8. 昇格判定

```python
if (self.current_player == 1 and tc == self.c - 1) or \
   (self.current_player == 2 and tc == 0):
    self.L[tc][tl][1] = 2  # ダムに昇格
```

- 黒（player 1）: 最右列（`tc == c-1`）に到達で昇格
- 白（player 2）: 最左列（`tc == 0`）に到達で昇格

## 9. Undo（待った）システム

```python
_save_state() で保存するデータ:
  (盤面のdeep copy, プレイヤー, 手数, スコア, 最後の移動, 履歴テキスト)

_undo() で復元:
  history_stack.pop()
  前の状態を全て復元
  盤面再描画 + スコア/ラベル更新
```

連鎖捕獲中にUndoした場合、連鎖全体が取り消される。

## 10. セーブ/ロード

JSONファイルに以下を保存:

```json
{
  "board": [[[0,0,0], ...], ...],
  "player": 1,
  "move_number": 15,
  "score": {"1": 3, "2": 2},
  "c": 8, "l": 8, "N": 3,
  "history_text": "#  1  Noir  Pion A2 → B3\n..."
}
```

ロード時はスコアのキーを `int` に変換（JSONは文字列キーのみ対応のため）。
