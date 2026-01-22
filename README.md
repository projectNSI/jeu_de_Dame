# Jeu de Dame / チェッカーゲーム / Checkers Game

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.x-green.svg)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🇫🇷 Français | [🇯🇵 日本語](#日本語) | [🇬🇧 English](#english)

### Description

Un jeu de dames implémenté en Python avec Pygame. Ce projet éducatif comprend une interface graphique et une logique de jeu modulaire pour apprendre la programmation de jeux.

### ✨ Fonctionnalités

- **Interface Graphique 8×8** avec Pygame
  - Plateau standard 8×8
  - Affichage graphique des pions (rouge et bleu)
  - Détection des clics souris
  - Étiquettes de coordonnées (1-8)
  - Affichage en temps réel

- **Logique de Jeu Modulaire**
  - Système complet de validation des mouvements
  - Détection de capture (prise)
  - Promotion en dame
  - Vérification des pions amis/ennemis
  - Détection de fin de partie
  - Configuration personnalisable via JSON

- **Documentation Complète**
  - Plans d'intégration détaillés (FR/JP)
  - Analyse logique du code
  - Guide d'implémentation

### 📁 Structure du Projet

```
jeu_de_Dame/
│
├── dame de main.py            # ⚙️ Logique principale du jeu
├── GUI_SYSTEM/
│   └── graphi_thema.py        # 🎨 Interface graphique Pygame
├── règle.json                 # 📋 Configuration du jeu
│
├── logic/
│   ├── How to integrate all/
│   │   ├── integration_plan_fr.md   # Plan d'intégration (FR)
│   │   └── integration_plan_ja.md   # Plan d'intégration (JP)
│   └── System logic/
│       ├── analyse_logique_dame.md      # Analyse détaillée (FR)
│       └── analyse_logique_dame_ja.md   # Analyse détaillée (JP)
│
├── PROJECTnsi.code-workspace  # Workspace VS Code
└── README.md                  # Ce fichier
```

### 🚀 Installation

#### Prérequis

- Python 3.x
- Pygame 2.x

#### Installation des dépendances

```bash
pip install pygame
```

### 🎮 Utilisation

#### Lancer l'Interface Graphique

```bash
python GUI_SYSTEM/graphi_thema.py
```

**Interface :**
- Plateau 8×8 avec damier noir et blanc
- Pions rouges (en haut) et bleus (en bas)
- Coordonnées affichées (colonnes 1-8, lignes 1-8)
- Fond vert

**Fonctionnalités actuelles :**
- Affichage du plateau
- Détection des clics (affichée dans la console)
- Initialisation automatique des pions

#### Tester la Logique du Jeu

```bash
python "dame de main.py"
```

**Fonctionnalités :**
- Configuration interactive du plateau
- Lecture de la configuration depuis `règle.json`
- Validation des mouvements
- Système de capture

### 🎯 Règles du Jeu

1. **Mouvement des pions**
   - Les pions se déplacent d'une case en diagonale vers l'avant
   - Les pions blancs avancent vers le bas
   - Les pions noirs avancent vers le haut

2. **Captures**
   - Un pion peut capturer un adversaire en sautant par-dessus
   - Les captures sont obligatoires quand elles sont possibles
   - Les captures multiples sont permises

3. **Promotion en Dame**
   - Un pion devient dame en atteignant la dernière rangée
   - Les dames se déplacent sur toute la longueur des diagonales
   - Les dames peuvent capturer à distance

4. **Victoire**
   - Éliminer tous les pions adverses
   - Bloquer tous les mouvements adverses

### 📚 Documentation

Des documents détaillés sont disponibles dans le dossier `logic/` :

- **Plans d'intégration** : Guide complet pour intégrer la logique et l'interface
- **Analyse logique** : Analyse détaillée du code avec identification des bugs

### 🛠️ Développement

#### Structure des Données

**Plateau de jeu** (`dame de main.py`) :
```python
L[colonne][ligne] = [couleur_pion, type_pion, couleur_case]
# [0] : 0=vide, 1=noir, 2=blanc
# [1] : 1=pion, 2=dame
# [2] : 0=case blanche, 1=case noire
```

**Plateau de jeu** (`dame_made_by_chqtGPT.py`) :
```python
board[y][x] = 'piece'
# '.' = vide
# 'b' = pion noir, 'B' = dame noire
# 'w' = pion blanc, 'W' = dame blanche
```

### 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

### 📝 License

Ce projet est sous licence MIT.

### 👨‍💻 Auteurs

Projet développé avec l'assistance de l'IA pour l'apprentissage et la démonstration.

---

## 🇯🇵 日本語

### 説明

Pythonとpygameで実装された完全なチェッカーゲーム。インタラクティブなグラフィカルインターフェースを備えた、古典的なチェッカーゲームの複数バージョンを提供します。

### ✨ 機能

- **国際チェッカー 10×10** - 国際ルールに準拠した完全版
  - プロフェッショナルな10×10ボード
  - 最長の取り方を強制する強制取りルール
  - 対角線全体を無制限に移動できるキング（ダマ）
  - メニューとクリック選択を備えた直感的なユーザーインターフェース
  - 可能な手を強調表示するシステム

- **クラシックチェッカー 8×8** - 伝統的バージョン
  - 標準8×8ボード
  - Pygameによるシンプルなグラフィカルインターフェース
  - マウスクリックによる駒の移動
  - 座標ラベル付き表示

- **モジュール型ゲームロジック**
  - 移動検証システム
  - キャプチャ検出
  - キング（ダマ）への昇格
  - ゲーム終了検出

### 📁 プロジェクト構造

```
jeu_de_Dame/
│
├── dame_made_by_chqtGPT.py    # 🎮 完全版10×10ゲーム（推奨）
├── GUI_SYSTEM/
│   └── graphi_thema.py        # 🎨 8×8グラフィカルインターフェース
├── dame de main.py            # ⚙️ ゲームロジック
├── règle.json                 # 📋 ゲーム設定
│
├── logic/
│   ├── How to integrate all/
│   │   ├── integration_plan_fr.md   # 統合計画（仏語）
│   │   └── integration_plan_ja.md   # 統合計画（日本語）
│   └── System logic/
│       ├── analyse_logique_dame.md      # 詳細分析（仏語）
│       └── analyse_logique_dame_ja.md   # 詳細分析（日本語）
│
└── README.md                  # このファイル
```

### 🚀 インストール

#### 必要要件

- Python 3.x
- Pygame 2.x

#### 依存関係のインストール

```bash
pip install pygame
```

### 🎮 使用方法

#### 10×10バージョン（推奨）

```bash
python "dame_made_by_chqtGPT.py"
```

**操作方法：**
- **マウス**：クリックして駒を選択・移動
- **メニュー**：プレイ/終了ボタン
- **ゲーム内ボタン**：リプレイ/終了

**ルール：**
- 黒（⚫）が下から開始
- 白（⚪）が上から開始
- 取りは強制
- 最長の取り方が強制
- ダマは対角線全体を移動可能

#### 8×8バージョン

```bash
python GUI_SYSTEM/graphi_thema.py
```

### 🎯 ゲームルール

1. **駒の移動**
   - 駒は前方の対角線に1マス移動
   - 白の駒は下に向かって進む
   - 黒の駒は上に向かって進む

2. **キャプチャ（取り）**
   - 駒は相手の駒を飛び越えてキャプチャ可能
   - 可能な場合、キャプチャは強制
   - 連続キャプチャが可能

3. **ダマへの昇格**
   - 駒が最後の列に到達するとダマになる
   - ダマは対角線全体を移動可能
   - ダマは遠距離でキャプチャ可能

4. **勝利条件**
   - 相手の駒をすべて取る
   - 相手のすべての動きをブロックする

### 📚 ドキュメント

`logic/`フォルダに詳細なドキュメントがあります：

- **統合計画**：ロジックとインターフェースを統合する完全ガイド
- **ロジック分析**：バグの特定を含むコードの詳細分析

### 🛠️ 開発

#### データ構造

**ゲームボード** (`dame de main.py`)：
```python
L[列][行] = [駒の色, 駒のタイプ, マスの色]
# [0] : 0=空, 1=黒, 2=白
# [1] : 1=駒, 2=ダマ
# [2] : 0=白マス, 1=黒マス
```

**ゲームボード** (`dame_made_by_chqtGPT.py`)：
```python
board[y][x] = '駒'
# '.' = 空
# 'b' = 黒駒, 'B' = 黒ダマ
# 'w' = 白駒, 'W' = 白ダマ
```

### 🤝 貢献

貢献を歓迎します！以下のことができます：
- バグを報告
- 改善を提案
- プルリクエストを送信

### 📝 ライセンス

このプロジェクトはMITライセンスの下にあります。

### 👨‍💻 作成者

学習とデモンストレーションのためのAI支援プロジェクト。

---

## 🇬🇧 English

### Description

A complete checkers game implemented in Python with Pygame. This project offers multiple versions of the classic checkers game with an interactive graphical interface.

### ✨ Features

- **International Draughts 10×10** - Full version with international rules
  - Professional 10×10 board
  - Mandatory captures with longest capture rule
  - Kings with unlimited diagonal movement
  - Intuitive user interface with menu and click selection
  - Highlighting system for possible moves

- **Classic Checkers 8×8** - Traditional version
  - Standard 8×8 board
  - Simple graphical interface with Pygame
  - Mouse click detection for movements
  - Display with coordinate labels

- **Modular game logic**
  - Move validation system
  - Capture detection
  - King promotion
  - Game end detection

### 📁 Project Structure

```
jeu_de_Dame/
│
├── dame_made_by_chqtGPT.py    # 🎮 Complete 10×10 game (recommended)
├── GUI_SYSTEM/
│   └── graphi_thema.py        # 🎨 8×8 graphical interface
├── dame de main.py            # ⚙️ Game logic
├── règle.json                 # 📋 Game configuration
│
├── logic/
│   ├── How to integrate all/
│   │   ├── integration_plan_fr.md   # Integration plan (FR)
│   │   └── integration_plan_ja.md   # Integration plan (JP)
│   └── System logic/
│       ├── analyse_logique_dame.md      # Detailed analysis (FR)
│       └── analyse_logique_dame_ja.md   # Detailed analysis (JP)
│
└── README.md                  # This file
```

### 🚀 Installation

#### Prerequisites

- Python 3.x
- Pygame 2.x

#### Installing Dependencies

```bash
pip install pygame
```

### 🎮 Usage

#### 10×10 Version (Recommended)

```bash
python "dame_made_by_chqtGPT.py"
```

**Controls:**
- **Mouse**: Click to select and move pieces
- **Menu**: Play/Quit buttons
- **In-game buttons**: Replay/Quit

**Rules:**
- Black (⚫) starts at bottom
- White (⚪) starts at top
- Captures are mandatory
- Longest capture is mandatory
- Kings move across entire diagonals

#### 8×8 Version

```bash
python GUI_SYSTEM/graphi_thema.py
```

### 🎯 Game Rules

1. **Piece Movement**
   - Pieces move one square diagonally forward
   - White pieces advance downward
   - Black pieces advance upward

2. **Captures**
   - A piece can capture an opponent by jumping over it
   - Captures are mandatory when possible
   - Multiple captures are allowed

3. **King Promotion**
   - A piece becomes a king when reaching the last row
   - Kings can move across entire diagonals
   - Kings can capture at distance

4. **Victory**
   - Eliminate all opponent pieces
   - Block all opponent moves

### 📚 Documentation

Detailed documents are available in the `logic/` folder:

- **Integration Plans**: Complete guide for integrating logic and interface
- **Logic Analysis**: Detailed code analysis with bug identification

### 🛠️ Development

#### Data Structures

**Game Board** (`dame de main.py`):
```python
L[column][row] = [piece_color, piece_type, square_color]
# [0]: 0=empty, 1=black, 2=white
# [1]: 1=piece, 2=king
# [2]: 0=white square, 1=black square
```

**Game Board** (`dame_made_by_chqtGPT.py`):
```python
board[y][x] = 'piece'
# '.' = empty
# 'b' = black piece, 'B' = black king
# 'w' = white piece, 'W' = white king
```

### 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest improvements
- Submit pull requests

### 📝 License

This project is under the MIT License.

### 👨‍💻 Authors

Project developed with AI assistance for learning and demonstration purposes.

---

## 📸 Screenshots

### 10×10 International Draughts
- Professional board with highlighting
- Menu system
- Capture sequences

### 8×8 Classic Checkers
- Traditional board layout
- Coordinate labels
- Simple interface

---

## 🔧 Technical Details

### Technologies Used
- **Python 3.x**: Main programming language
- **Pygame 2.x**: Graphics and game engine library
- **JSON**: Configuration file format

### Key Components

1. **`dame_made_by_chqtGPT.py`**: Full-featured implementation
   - Complete game loop
   - Menu system
   - Move generation with capture sequences
   - Longest capture rule enforcement
   - King movement and capture logic

2. **`GUI_SYSTEM/graphi_thema.py`**: Visual interface
   - Board rendering
   - Piece drawing
   - Mouse click handling
   - Coordinate labels

3. **`dame de main.py`**: Core game logic
   - Board initialization
   - Move validation
   - Capture detection
   - Win condition checking

### Configuration

Edit `règle.json` to customize game settings:
```json
[
  {
    "Liste": [],
    "colonne": 8,
    "ligne": 8,
    "ligne_de_pion": 3
  }
]
```

---

## 📞 Support

For questions, issues, or suggestions:
- Open an issue on the project repository
- Refer to the detailed documentation in the `logic/` folder

---

**Enjoy the game! / Bon jeu ! / ゲームを楽しんでください！** 🎮