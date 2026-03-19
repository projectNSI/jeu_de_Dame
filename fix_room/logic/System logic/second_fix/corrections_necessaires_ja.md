# `dame de main.py` 第2次修正リスト

**作成日:** 2026-01-22  
**前回修正:** 2026-01-22（第1次修正完了）  
**状態:** 14個のバグ中5個修正済み、残り5個要修正

---

## 📊 修正状況サマリー

| カテゴリ | 総数 | 修正済 | 残り | 完了率 |
|---------|------|--------|------|--------|
| 🔴 致命的バグ | 5 | 2 | 3 | 40% |
| 🟡 中程度のバグ | 4 | 2 | 2 | 50% |
| 🟢 軽微な問題 | 5 | 1 | 4 | 20% |
| **合計** | **14** | **5** | **9** | **36%** |

---

## ✅ 第1次修正で完了した項目

### 修正済み（5個）

#### ✅ 1. 論理条件の修正（10、13、16行目）
**状態:** 完了  
**修正内容:**
```python
# 修正前:
if fc != 0 or fc != None:  # 常にTrue

# 修正後:
if fc != 0 and fc:  # 正しい条件
```

#### ✅ 2. プレイヤー交代の修正（164行目）
**状態:** 完了  
**修正内容:**
```python
# 修正前:
v += 1 % 2  # v += 1 と同じ

# 修正後:
v = (v + 1) % 2  # 0と1の間で正しく交代
```

#### ✅ 3. ゲームループの追加（192-194行目）
**状態:** 完了  
**修正内容:**
```python
# 追加されたコード:
while team_exist(L, 1) and team_exist(L, 2):
    resultat = tour(L, c, l, v)
    v = (v + 1) % 2
```

#### ✅ 4. 変数iの再利用問題（回避済み）
**状態:** 完了  
**理由:** 変数名を `ii` に変更することで回避された

#### ✅ 5. 関数戻り値の修正（172行目）
**状態:** 完了  
**修正内容:**
```python
# 修正前:
return ('les', q, 'a gagner')

# 修正後:
return f'Les {q} ont gagné!'
```

---

## 🔴 第2次修正で対応すべき致命的バグ（3個）

これらのバグは**プログラムの実行を妨げる**ため、最優先で修正が必要です。

### ❌ バグ1: リストJが初期化されていない（通常の駒）

**場所:** 55行目  
**優先度:** 🔴 最高  
**影響:** `IndexError: list assignment index out of range` が発生

#### 現在のコード（55-67行目）:
```python
if L[c][l][1]==1:
    J=[]  # ❌ 空リスト
    for i in range(len(diags)):
        try:
            if L[c+diags[i][0]][l+diags[i][1]][0] == (2-v) and L[c+2*diags[i][0]][l+2*diags[i][1]][0]==0:
                J[i]=1  # ❌ IndexError!
            elif 0 <= c+diags[i][0] < len(L) and 0 <= l+diags[i][1] < len(L[0]):
                J[i]=0
            elif L[c+diags[i][0]][l+diags[i][1]][0] == 0:
                J[i]=2
            else:
                J[i]=0
        except IndexError:
            J[i]=0
```

#### 修正後のコード:
```python
if L[c][l][1]==1:
    J = [0] * len(diags)  # ✅ リストを事前に割り当て
    for i in range(len(diags)):
        try:
            # 範囲チェックを先に
            new_c = c + diags[i][0]
            new_l = l + diags[i][1]
            
            # 範囲外チェック
            if not (0 <= new_c < len(L) and 0 <= new_l < len(L[0])):
                J[i] = 0
                continue
            
            # 捕獲可能かチェック
            if L[new_c][new_l][0] == (2-v):
                capture_c = c + 2*diags[i][0]
                capture_l = l + 2*diags[i][1]
                if (0 <= capture_c < len(L) and 
                    0 <= capture_l < len(L[0]) and
                    L[capture_c][capture_l][0] == 0):
                    J[i] = 1  # 捕獲可能
                else:
                    J[i] = 0
            # 通常移動可能かチェック
            elif L[new_c][new_l][0] == 0:
                J[i] = 2  # 通常移動
            else:
                J[i] = 0
        except IndexError:
            J[i] = 0
```

**修正理由:**
- `J = []` は空リストなので、`J[i]` でアクセスするとエラー
- `J = [0] * len(diags)` で4要素のリストを事前に作成
- ロジックの順序も整理（範囲チェック → 捕獲 → 通常移動）

---

### ❌ バグ2: キング用リストJが初期化されていない

**場所:** 68行目  
**優先度:** 🔴 最高  
**影響:** `NameError: name 'J' is not defined` が発生

#### 現在のコード（68-80行目）:
```python
elif L[c][l][1]==2:
    # Jが初期化されていない！❌
    for i in range(len(L)):
        for j in range(len(L[i])):
            try:   
                if L[i][j][0]==(2-v)and ((c-diags[0][0]*(c-i)==i and l-diags[0][1]*(c-j)==j)or(c-diags[1][0]*(c-i)==i and l-diags[1][1]*(c-j)==j)or (c-diags[2][0]*(c-i)==i and l-diags[2][1]*(c-j)==j)or(c-diags[3][0]*(c-i)==i and l-diags[3][1]*(c-j)==j)) : 
                    J[i][j]=1  # ❌ NameError!
                elif L[i][j][0]==0:
                    J[i][j]=2
                else:
                    J[i][j]=0
            except IndexError:
                J[i][j]=0
```

#### 修正後のコード:
```python
elif L[c][l][1]==2:
    # 2次元リストを初期化 ✅
    J = [[0 for _ in range(len(L[0]))] for _ in range(len(L))]
    
    for i in range(len(L)):
        for j in range(len(L[i])):
            try:   
                if L[i][j][0]==(2-v) and ((c-diags[0][0]*(c-i)==i and l-diags[0][1]*(c-j)==j)or(c-diags[1][0]*(c-i)==i and l-diags[1][1]*(c-j)==j)or (c-diags[2][0]*(c-i)==i and l-diags[2][1]*(c-j)==j)or(c-diags[3][0]*(c-i)==i and l-diags[3][1]*(c-j)==j)) : 
                    J[i][j]=1
                elif L[i][j][0]==0:
                    J[i][j]=2
                else:
                    J[i][j]=0
            except IndexError:
                J[i][j]=0
```

#### さらに、関数の最後にデフォルトケースを追加:
```python
    else:
        J = []  # ✅ デフォルトケース
                    
    return J
```

**修正理由:**
- キングの場合、2次元リスト `J[i][j]` が必要
- `[[0]*列数 for _ in range(行数)]` で初期化

---

### ❌ バグ3: インデックス変換がない（1-based → 0-based）

**場所:** 98-99行目  
**優先度:** 🔴 高  
**影響:** ユーザー入力と配列インデックスが1つずれる

#### 現在のコード（98-99行目）:
```python
ii=int(input(f'quelle colone?(1 à {c})'))  # ユーザーは1-8を入力
h=int(input(f'quelle ligne?(1 à {l})'))    # しかし配列は0-7
```

#### 使用箇所（101行目など）:
```python
if is_friendly(L,ii,h,v)==True:  # ❌ インデックスが1つずれている
    # L[8][5] のようにアクセスして IndexError
```

#### 修正後のコード:
```python
ii = int(input(f'quelle colone?(1 à {c})')) - 1  # ✅ 0-basedに変換
h = int(input(f'quelle ligne?(1 à {l})')) - 1    # ✅ 0-basedに変換
```

**修正理由:**
- ユーザーには「1から8」と表示されるが、内部では0-7でインデックス化
- `-1` することで変換が必要

**影響範囲:**
- 98-99行目: 入力時
- 101行目: `is_friendly(L,ii,h,v)` の呼び出し
- 106行目: `jeu_possible(L,ii,h,diags,v)` の呼び出し
- その他、`L[ii][h]` を使用するすべての箇所

---

## 🟡 第2次修正で対応すべき中程度のバグ（2個）

### ❌ バグ4: input内にprint関数がある

**場所:** 117行目  
**優先度:** 🟡 中  
**影響:** 動作は可能だが、`None` が表示され、混乱を招く

#### 現在のコード:
```python
d=int(input(print('quelle diagonale?(1 à 4)')))
```

**問題点:**
1. `print()` は画面に表示して `None` を返す
2. `input(None)` が実行される
3. 結果的に動くが、意図した動作ではない

#### 修正後のコード:
```python
d = int(input('quelle diagonale?(1 à 4)'))  # ✅ printを削除
```

---

### ❌ バグ5: 条件ロジックが逆

**場所:** 110行目  
**優先度:** 🟡 中  
**影響:** メッセージが逆の意味で表示される

#### 現在のコード（109-115行目）:
```python
for i in range(len(J)):
    if J == [0] * len(diags):  # ❌ 全て0 = 移動不可
        print('une attaque est possible sur la',i+1,'eme diagonale')  # ❌ 逆！
    elif J[i] ==2:
        print('un deplacement est possible sur la',i+1,'eme diagonale')
    else:
        print('aucun deplacement n est possible avec ce pion')
```

**問題点:**
- `J == [0] * len(diags)` は「すべての方向が不可」を意味する
- なのに「攻撃可能」と表示している

#### 修正後のコード:
```python
for idx in range(len(J)):  # 変数名も変更
    if J[idx] == 1:  # ✅ 捕獲可能
        print('une attaque est possible sur la', idx+1, 'eme diagonale')
    elif J[idx] == 2:  # ✅ 通常移動可能
        print('un deplacement est possible sur la', idx+1, 'eme diagonale')
    else:  # J[idx] == 0
        print('aucun deplacement n est possible dans cette direction')
```

**修正内容:**
1. `J == [0] * len(diags)` → `J[idx] == 1` に変更
2. 各方向ごとにチェック
3. メッセージを正しい条件に対応させる

---

## 🟢 残っている軽微な問題（4個）

これらは動作に影響しませんが、コード品質向上のために修正を推奨します。

### 💡 改善1: キングへの昇格が未実装

**場所:** `execute_move_gui()` などの移動処理  
**優先度:** 🟢 低  
**推奨修正:**

```python
# 移動処理の後に追加:
# 最終行に到達したらキングに昇格
if L[to_col][to_ligne][1] == 1:  # 通常の駒の場合
    if (player == 1 and to_col == 7) or (player == 2 and to_col == 0):
        L[to_col][to_ligne][1] = 2  # キングに昇格
```

### 💡 改善2: 連続捕獲が未実装

**場所:** 移動処理  
**優先度:** 🟢 低  
**説明:** チェッカーの公式ルールでは、1ターンで複数回捕獲可能

### 💡 改善3: エラーハンドリングの改善

**場所:** 全体  
**優先度:** 🟢 低  
**推奨修正:**

```python
# 入力時の検証
try:
    ii = int(input(...))
    if not (0 < ii <= c):
        print("範囲外です")
        continue
except ValueError:
    print("数値を入力してください")
    continue
```

### 💡 改善4: append()の使い方が間違っている

**場所:** 154、156行目  
**優先度:** 🟢 低  
**現在のコード:**
```python
M[0].append(i,j)  # ❌ append()は1つの引数のみ
```

**修正:**
```python
M[0].append((i, j))  # ✅ タプルとして追加
# または
M[0].append([i, j])  # ✅ リストとして追加
```

---

## 📝 完全な修正版コード

### `jeu_possible` 関数（52-82行目の完全な置き換え）

```python
def jeu_possible(L:list,c:int,l:int,diags:list,v:int,t:int=None)->list:
    """regarde si une mouvement est possible"""
    
    # 通常の駒
    if L[c][l][1]==1:
        J = [0] * len(diags)  # ✅ 修正1: 初期化
        for i in range(len(diags)):
            try:
                # 範囲チェックを先に
                new_c = c + diags[i][0]
                new_l = l + diags[i][1]
                
                # 範囲外チェック
                if not (0 <= new_c < len(L) and 0 <= new_l < len(L[0])):
                    J[i] = 0
                    continue
                
                # 捕獲可能かチェック
                if L[new_c][new_l][0] == (2-v):
                    capture_c = c + 2*diags[i][0]
                    capture_l = l + 2*diags[i][1]
                    if (0 <= capture_c < len(L) and 
                        0 <= capture_l < len(L[0]) and
                        L[capture_c][capture_l][0] == 0):
                        J[i] = 1  # 捕獲可能
                    else:
                        J[i] = 0
                # 通常移動可能かチェック
                elif L[new_c][new_l][0] == 0:
                    J[i] = 2  # 通常移動
                else:
                    J[i] = 0
            except IndexError:
                J[i] = 0
    
    # キング
    elif L[c][l][1]==2:
        J = [[0 for _ in range(len(L[0]))] for _ in range(len(L))]  # ✅ 修正2: 初期化
        for i in range(len(L)):
            for j in range(len(L[i])):
                try:   
                    if L[i][j][0]==(2-v) and ((c-diags[0][0]*(c-i)==i and l-diags[0][1]*(c-j)==j)or(c-diags[1][0]*(c-i)==i and l-diags[1][1]*(c-j)==j)or (c-diags[2][0]*(c-i)==i and l-diags[2][1]*(c-j)==j)or(c-diags[3][0]*(c-i)==i and l-diags[3][1]*(c-j)==j)) : 
                        J[i][j]=1
                    elif L[i][j][0]==0:
                        J[i][j]=2
                    else:
                        J[i][j]=0
                except IndexError:
                    J[i][j]=0
    else:
        J = []  # ✅ デフォルトケース
                    
    return J
```

### `tour` 関数の修正箇所

#### 修正A: インデックス変換（98-99行目）
```python
ii = int(input(f'quelle colone?(1 à {c})')) - 1  # ✅ 修正3
h = int(input(f'quelle ligne?(1 à {l})')) - 1    # ✅ 修正3
```

#### 修正B: メッセージ表示ロジック（109-115行目）
```python
for idx in range(len(J)):  # ✅ 修正5: 変数名変更
    if J[idx] == 1:  # ✅ 修正5: 条件修正
        print('une attaque est possible sur la', idx+1, 'eme diagonale')
    elif J[idx] == 2:
        print('un deplacement est possible sur la', idx+1, 'eme diagonale')
```

#### 修正C: input内のprint削除（117行目）
```python
d = int(input('quelle diagonale?(1 à 4)'))  # ✅ 修正4
```

---

## 🎯 修正作業の優先順位

### フェーズ1: 致命的バグの修正（必須）

1. **バグ1:** リストJ初期化（通常駒） - 55行目
2. **バグ2:** リストJ初期化（キング） - 68行目  
3. **バグ3:** インデックス変換 - 98-99行目

**推定時間:** 30分  
**重要度:** 🔴 最高（これがないとプログラムが動かない）

### フェーズ2: 中程度のバグ修正（推奨）

4. **バグ4:** print in input - 117行目
5. **バグ5:** 条件ロジック修正 - 109-115行目

**推定時間:** 15分  
**重要度:** 🟡 中（動作するが、正しく動作しない）

### フェーズ3: 軽微な改善（オプション）

6. キング昇格の実装
7. 連続捕獲の実装
8. エラーハンドリング強化
9. append()の修正

**推定時間:** 1-2時間  
**重要度:** 🟢 低（機能追加と品質向上）

---

## 📋 チェックリスト

修正作業を進める際のチェックリストです。

### フェーズ1: 致命的バグ修正

- [ ] `jeu_possible()` 関数の55行目に `J = [0] * len(diags)` を追加
- [ ] `jeu_possible()` 関数の68行目に `J = [[0]*列数 for _ in range(行数)]` を追加
- [ ] `jeu_possible()` 関数の最後に `else: J = []` とデフォルトケースを追加
- [ ] `tour()` 関数の98行目に `-1` を追加（インデックス変換）
- [ ] `tour()` 関数の99行目に `-1` を追加（インデックス変換）

### フェーズ2: 中程度のバグ修正

- [ ] `tour()` 関数の117行目から `print()` を削除
- [ ] `tour()` 関数の109-115行目の条件ロジックを修正

### テスト

- [ ] プログラムが起動する
- [ ] 駒を選択できる
- [ ] 移動先が正しく表示される
- [ ] 移動が実行できる
- [ ] ゲームが最後まで進行する

---

## 🔧 修正後のテスト方法

### テストケース1: 基本動作
```
1. プログラムを実行
2. パラメータはデフォルトで「non」を選択
3. 駒を選択（例: colonne=3, ligne=3）
4. 移動可能な方向が表示されることを確認
5. 移動を実行
6. エラーが出ないことを確認
```

### テストケース2: 捕獲
```
1. 敵駒の隣に自分の駒を配置
2. その駒を選択
3. 「une attaque est possible」と表示されることを確認
4. 捕獲を実行
5. 敵駒が削除されることを確認
```

### テストケース3: ゲーム終了
```
1. 一方のプレイヤーの駒をすべて捕獲
2. 「Les [色] ont gagné!」と表示されることを確認
3. ゲームループが終了することを確認
```

---

## 📚 参考資料

- `logic/System logic/analyse_logique_dame_ja.md` - 初回分析（全14個のバグ）
- `logic/System logic/analyse_logique_dame.md` - フランス語版分析
- `dame de main.py` - 現在のソースコード

---

**作成者:** AI Assistant  
**最終更新:** 2026-01-22  
**次回確認:** 修正完了後

