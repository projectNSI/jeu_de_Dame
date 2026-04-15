# AI・追加機能解説

`dame_gui_ctk.py` に実装されたAIシステムおよび差別化機能の技術解説。

---

## 1. AIシステム（`SimpleAI` クラス）

### 1.1 概要

AIは常に白（Blancs, player 2）を担当。3段階の難易度を実装。

| 難易度 | アルゴリズム | 特徴 |
|--------|-------------|------|
| Facile（簡単） | ランダム | 合法手からランダムに選択 |
| Moyen（普通） | 貪欲法 | 各手の盤面評価が最大のものを選択 |
| Difficile（難しい） | Minimax + Alpha-Beta | 2手先を読み、最善手を選択 |

### 1.2 評価関数 `_evaluate()`

```python
def _evaluate(self, L, ai_v):
    score = 0
    for col, ligne の全マス:
        if 駒がある:
            val = 5.0  # ダムの場合
            val = 1.0  # 通常の駒の場合
            
            # 位置ボーナス: 昇格に近い駒ほど高評価
            if 通常の駒:
                if 黒の駒: val += col * 0.15
                if 白の駒: val += (c-1-col) * 0.15
            
            if 自分の駒: score += val
            else:        score -= val
    return score
```

**評価基準**:
- ダムは通常の駒の5倍の価値
- 昇格ラインに近い通常駒には位置ボーナス（最大 `7 × 0.15 = 1.05`）
- 自分の駒は加算、相手の駒は減算

### 1.3 Minimax アルゴリズム

```
minimax_root(盤面, AI側, 全合法手)
  │
  ├─ 各合法手について:
  │   ├─ 盤面コピー作成（_copy_board で高速コピー）
  │   ├─ 手を適用（_sim_move で昇格も処理）
  │   └─ minimax(コピー盤面, 深さ2, 相手番, alpha, beta)
  │       │
  │       ├─ 深さ0 → 評価関数で評価値を返す
  │       ├─ 最大化（AI番）→ 各手の最大値を探索
  │       └─ 最小化（相手番）→ 各手の最小値を探索
  │           └─ Alpha-Beta枝刈りで無駄な探索を打ち切り
  │
  └─ 最高評価の手を返す（同点なら乱択）
```

**Alpha-Beta枝刈り**: 探索空間を大幅に削減。最悪 O(b^d) から最良 O(b^(d/2)) に改善。

### 1.4 高速盤面コピー

```python
def _copy_board(L):
    return [[[cell[0], cell[1], cell[2]] for cell in col] for col in L]
```

`copy.deepcopy()` の代わりにリスト内包表記を使用。10〜100倍高速。

### 1.5 AI連鎖捕獲

```
_ai_move()
  → _ai_execute() → _execute_move() → chain=True
    → 500ms後に _ai_chain_step()
      → difficileモード: 全候補を評価して最善を選択
      → それ以外: ランダム選択
      → 450ms後に _ai_execute()（再帰的に連鎖）
```

---

## 2. メインメニューシステム

```
_show_menu()
  ├─ タイトル「♔ Jeu de Dames ♕」
  ├─ モード選択ドロップダウン
  ├─ テーマ選択ドロップダウン
  ├─ 「▶ Commencer la partie」→ _menu_start()
  ├─ 「📂 Charger une partie」→ _menu_load()
  └─ 「Quitter」→ self.destroy()
```

ゲーム中に「🏠 Menu」ボタンでメニューに戻れる。

---

## 3. ヒント機能

- 貪欲法AIを内部で一時的に使用して最善手を計算
- Ctrl+H または💡ボタンで起動
- 3秒後にハイライト自動消去

---

## 4. 効果音システム

`winsound.Beep(周波数Hz, 持続時間ms)` を使用。非ブロッキングのためスレッドで実行。

| イベント | 周波数パターン | 特徴 |
|----------|---------------|------|
| 通常移動 | 500Hz → 1000Hz | 低→高の上昇音 |
| 捕獲 | 1400Hz → 350Hz | 高→低の急降下 |
| 昇格 | 440→660→880→1100→1400Hz | 5音の上昇スケール |
| Undo | 900Hz → 300Hz | 巻き戻し感 |
| 勝利 | C5→E5→G5→C6→E6→G6 | 音階によるファンファーレ |
| メニュー起動 | 600→800→1000Hz | 3音の起動音 |

---

## 5. タイマー・テーマ・その他

- **タイマー**: ターンごとの経過時間と総対局時間を1秒ごとに更新
- **テーマ**: Classique / Émeraude / Océan / Crépuscule の4種
- **フラッシュ演出**: 捕獲されたマスが赤く4回点滅
- **キーボードショートカット**: Ctrl+Z(undo), Ctrl+N(新規), Ctrl+S(保存), Ctrl+O(読込), Ctrl+H(ヒント)
