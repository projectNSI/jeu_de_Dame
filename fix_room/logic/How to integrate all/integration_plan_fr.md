# Plan d'Intégration GUI-Logic
## Projet Jeu de Dame

**Date de création:** 2026-01-15  
**Objectif:** Intégration de `dame de main.py` (logique) et `graphi_thema.py` (GUI)

---

## 📋 Table des matières

1. [Analyse de l'État Actuel](#analyse-de-létat-actuel)
2. [Stratégie d'Intégration](#stratégie-dintégration)
3. [Unification des Structures de Données](#unification-des-structures-de-données)
4. [Étapes d'Implémentation](#étapes-dimplémentation)
5. [Structure des Fichiers](#structure-des-fichiers)
6. [Liste des Corrections Nécessaires](#liste-des-corrections-nécessaires)
7. [Code d'Implémentation](#code-dimplémentation)
8. [Plan de Test](#plan-de-test)
9. [Calendrier](#calendrier)

---

## 1. Analyse de l'État Actuel

### 1.1 État des Fichiers Existants

#### `dame de main.py` (190 lignes)
- **Rôle:** Logique du jeu
- **Points forts:**
  - ✅ Logique de mouvement (`jeu_possible`)
  - ✅ Vérification de propriété (`is_friendly`)
  - ✅ Détection de victoire (`team_exist`)
  - ✅ Fonctionnalité Dame
- **Points faibles:**
  - ❌ 14 bugs identifiés
  - ❌ Entrée interactive avec `input()`
  - ❌ Structure de données complexe (liste 3D)
  - ❌ Confusion d'indexation (col/ligne)

#### `GUI_SYSTEM/graphi_thema.py` (100 lignes)
- **Rôle:** Affichage graphique
- **Points forts:**
  - ✅ Rendu avec Pygame
  - ✅ Affichage du plateau
  - ✅ Détection des clics souris
  - ✅ Structure de données simple
- **Points faibles:**
  - ❌ Pas de logique de jeu
  - ❌ Pas de fonctionnalité de mouvement
  - ❌ Pas de détection de victoire
  - ❌ Pas de fonctionnalité Dame

### 1.2 Différences Principales

| Aspect | dame de main.py | graphi_thema.py |
|--------|-----------------|-----------------|
| **Structure de données** | `L[col][ligne][3 éléments]` | `board[row][col]` |
| **Ordre d'indexation** | colonne → ligne | ligne → colonne |
| **Couleur des pions** | 1=noir, 2=blanc | 1=rouge, 2=bleu |
| **Info case** | `[couleur, type, couleur_case]` | couleur du pion uniquement |
| **Mode d'entrée** | `input()` | clics souris |
| **Dame** | oui (type=2) | non |

---

## 2. Stratégie d'Intégration

### 2.1 Approche Choisie: **Méthode Wrapper**

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  dame_gui.py (nouveau fichier)                 │
│  ┌──────────────────────────────────────┐      │
│  │  Boucle principale Pygame            │      │
│  │  - Rendu graphique                   │      │
│  │  - Gestion des événements            │      │
│  │  - Gestion de l'état du jeu          │      │
│  └────────┬──────────────────┬───────────┘      │
│           │                  │                  │
│           ↓                  ↓                  │
│  ┌────────────────┐  ┌────────────────┐        │
│  │ Fonctions      │  │ Fonctions de   │        │
│  │ Helper GUI     │  │ rendu          │        │
│  └────────┬───────┘  │ - draw_board   │        │
│           │          │ - draw_pieces  │        │
│           ↓          └────────────────┘        │
│  ┌─────────────────────────────────────┐       │
│  │  Import dame de main.py             │       │
│  │  import dame_de_main as logic       │       │
│  └────────┬────────────────────────────┘       │
│           ↓                                     │
└───────────┼─────────────────────────────────────┘
            │
            ↓
┌───────────────────────────────────────────────┐
│  dame de main.py (existant + ajouts)          │
│  ┌─────────────────────────────────────┐     │
│  │ Fonctions logiques existantes       │     │
│  │ (aucune modification)               │     │
│  │ - creation_de_jeu()                 │     │
│  │ - is_friendly()                     │     │
│  │ - jeu_possible()                    │     │
│  │ - team_exist()                      │     │
│  │ - tour() ※non utilisé               │     │
│  └─────────────────────────────────────┘     │
│                                               │
│  ┌─────────────────────────────────────┐     │
│  │ 【NOUVEAUX】Interface pour GUI      │     │
│  │ - get_valid_moves_gui()             │     │
│  │ - execute_move_gui()                │     │
│  │ - check_game_status()               │     │
│  │ - init_board_gui()                  │     │
│  └─────────────────────────────────────┘     │
└───────────────────────────────────────────────┘
```

### 2.2 Raisons de l'Intégration

1. **Protection du code existant**: Pas de modification de la logique de `dame de main.py`
2. **Implémentation progressive**: Ajout de fonctionnalités étape par étape
3. **Facilité de test**: Tests séparés GUI et logique
4. **Maintenabilité**: Séparation des responsabilités (GUI=affichage, Logic=calcul)

---

## 3. Unification des Structures de Données

### 3.1 Problème

Les structures de données diffèrent entre `dame de main.py` et `graphi_thema.py`.

**dame de main.py:**
```python
L[col][ligne] = [couleur_pion, type_pion, couleur_case]
# Exemple: L[3][5] = [1, 1, 1]  # pion noir, normal, case noire
```

**graphi_thema.py:**
```python
board[row][col] = couleur_pion
# Exemple: board[5][3] = 1  # pion rouge
```

### 3.2 Solution: Pattern Adaptateur

Conversion de données dans la couche GUI.

```python
class BoardAdapter:
    """Utilise la structure de dame de main.py dans le GUI"""
    
    def __init__(self):
        # Utilise le format de dame de main.py
        # L[col][ligne] = [couleur, type, couleur_case]
        self.L = self._init_logic_board()
    
    def _init_logic_board(self):
        """Initialise le plateau au format logique"""
        L = [[[0, 0, (1 + h % 2 - g % 2) % 2] 
              for g in range(8)] 
              for h in range(8)]
        
        N = 3
        for col in range(8):
            for ligne in range(8):
                if col < N and L[col][ligne][2] == 1:
                    L[col][ligne][0] = 1  # pion noir
                    L[col][ligne][1] = 1  # pion normal
                elif col > 8 - N - 1 and L[col][ligne][2] == 1:
                    L[col][ligne][0] = 2  # pion blanc
                    L[col][ligne][1] = 1
        return L
    
    def get_piece_at(self, row, col):
        """Obtient les infos du pion depuis coordonnées GUI"""
        # GUI utilise row, col
        # Logique utilise col, ligne
        return self.L[col][row]
    
    def set_piece_at(self, row, col, couleur, type_pion=1):
        """Définit un pion avec coordonnées GUI"""
        self.L[col][row][0] = couleur
        self.L[col][row][1] = type_pion
```

### 3.3 Mapping de Conversion de Coordonnées

```
Rendu GUI:        Traitement logique:
row, col    →    col, ligne

Exemple:
GUI: board[5][3]  →  Logic: L[3][5]
     ↑    ↑               ↑    ↑
    row  col            col  ligne
```

---

## 4. Étapes d'Implémentation

### Phase 1: Construction de la Base (Priorité: Haute)

#### Étape 1.1: Correction des Bugs de `dame de main.py`
**Durée:** 2 heures

Bugs critiques à corriger (5):
1. Initialiser la liste J dans `jeu_possible()`
2. Corriger les conditions logiques (`or` → `and`)
3. Conversion d'index (1-based → 0-based) ※Pas nécessaire pour fonctions GUI
4. Corriger la réutilisation de la variable i
5. Initialiser la liste J pour les Dames

```python
# Exemple de correction:
def jeu_possible(L, c, l, diags, v, t=None):
    """Détermine les mouvements possibles"""
    # Correction 1: Initialiser la liste
    if L[c][l][1] == 1:  # pion normal
        J = [0] * len(diags)  # ← AJOUT
        for i in range(len(diags)):
            try:
                # Ajouter vérification de plage
                new_c = c + diags[i][0]
                new_l = l + diags[i][1]
                if not (0 <= new_c < len(L) and 0 <= new_l < len(L[0])):
                    J[i] = 0
                    continue
                
                if L[new_c][new_l][0] == (2 - v):
                    # Vérifier possibilité de capture
                    capture_c = c + 2 * diags[i][0]
                    capture_l = l + 2 * diags[i][1]
                    if (0 <= capture_c < len(L) and 
                        0 <= capture_l < len(L[0]) and
                        L[capture_c][capture_l][0] == 0):
                        J[i] = 1  # capture possible
                    else:
                        J[i] = 0
                elif L[new_c][new_l][0] == 0:
                    J[i] = 2  # mouvement normal
                else:
                    J[i] = 0
            except IndexError:
                J[i] = 0
        return J
    
    elif L[c][l][1] == 2:  # Dame
        J = [[0 for _ in range(len(L[0]))] for _ in range(len(L))]  # ← AJOUT
        # Logique Dame...
        return J
    
    return []  # Par défaut
```

#### Étape 1.2: Ajouter les Fonctions d'Interface GUI
**Durée:** 3 heures

Ajouter à la fin de `dame de main.py`:

```python
# ============================================
# Fonctions d'Interface GUI (NOUVEAUX AJOUTS)
# ============================================

def init_board_gui(board_size=8, num_rows=3):
    """
    Pour GUI: Initialiser le plateau
    
    Returns:
        L[col][ligne] = [couleur, type, couleur_case]
    """
    L = [[[0, 0, (1 + h % 2 - g % 2) % 2] 
          for g in range(board_size)] 
          for h in range(board_size)]
    
    for col in range(board_size):
        for ligne in range(board_size):
            if col < num_rows:
                if L[col][ligne][2] == 1:  # case noire
                    L[col][ligne][0] = 1  # pion noir
                    L[col][ligne][1] = 1  # pion normal
            elif col > board_size - num_rows - 1:
                if L[col][ligne][2] == 1:
                    L[col][ligne][0] = 2  # pion blanc
                    L[col][ligne][1] = 1
    
    return L


def get_valid_moves_gui(L, col, ligne, joueur):
    """
    Pour GUI: Obtenir les mouvements possibles pour un pion
    
    Parameters:
        L: Plateau
        col, ligne: Position du pion (0-based)
        joueur: 1=noir, 2=blanc
    
    Returns:
        [(col, ligne, type_mouvement), ...]
        type_mouvement: 'capture' ou 'move'
    """
    v = 0 if joueur == 2 else 1  # Convertir numéro de joueur
    
    # Vérifier si c'est son pion
    if not is_friendly(L, col, ligne, v):
        return []
    
    diags = [[-1, 1], [1, 1], [-1, -1], [1, -1]]
    
    try:
        J = jeu_possible(L, col, ligne, diags, v, None)
    except:
        return []
    
    moves = []
    
    # Pion normal
    if L[col][ligne][1] == 1:
        if not isinstance(J, list) or len(J) == 0:
            return []
        
        for i in range(len(J)):
            if J[i] == 1:  # Capture possible
                new_col = col + 2 * diags[i][0]
                new_ligne = ligne + 2 * diags[i][1]
                if 0 <= new_col < len(L) and 0 <= new_ligne < len(L[0]):
                    moves.append((new_col, new_ligne, 'capture'))
            elif J[i] == 2:  # Mouvement normal
                new_col = col + diags[i][0]
                new_ligne = ligne + diags[i][1]
                if 0 <= new_col < len(L) and 0 <= new_ligne < len(L[0]):
                    # Vérifier restriction de direction
                    if joueur == 1 and i in [0, 1]:  # Noir va vers l'avant
                        moves.append((new_col, new_ligne, 'move'))
                    elif joueur == 2 and i in [2, 3]:  # Blanc va vers l'arrière
                        moves.append((new_col, new_ligne, 'move'))
    
    # Dame
    elif L[col][ligne][1] == 2:
        # Dame peut se déplacer dans toutes les directions
        if isinstance(J, list) and len(J) > 0:
            for i in range(len(J)):
                for j in range(len(J[i])):
                    if J[i][j] == 1:  # Capture
                        moves.append((i, j, 'capture'))
                    elif J[i][j] == 2:  # Mouvement
                        moves.append((i, j, 'move'))
    
    return moves


def execute_move_gui(L, from_col, from_ligne, to_col, to_ligne, joueur):
    """
    Pour GUI: Déplacer un pion
    
    Parameters:
        L: Plateau
        from_col, from_ligne: Position d'origine
        to_col, to_ligne: Position de destination
        joueur: 1=noir, 2=blanc
    
    Returns:
        bool: True si le mouvement a réussi
    """
    # Obtenir les mouvements valides
    valid_moves = get_valid_moves_gui(L, from_col, from_ligne, joueur)
    
    # Vérifier si la destination est valide
    for move in valid_moves:
        if move[0] == to_col and move[1] == to_ligne:
            move_type = move[2]
            
            # Si capture, supprimer le pion intermédiaire
            if move_type == 'capture':
                mid_col = (from_col + to_col) // 2
                mid_ligne = (from_ligne + to_ligne) // 2
                L[mid_col][mid_ligne][0] = 0
                L[mid_col][mid_ligne][1] = 0
            
            # Déplacer le pion
            L[to_col][to_ligne][0] = L[from_col][from_ligne][0]
            L[to_col][to_ligne][1] = L[from_col][from_ligne][1]
            L[from_col][from_ligne][0] = 0
            L[from_col][from_ligne][1] = 0
            
            # Vérifier promotion en Dame
            if L[to_col][to_ligne][1] == 1:  # Pion normal
                if (joueur == 1 and to_col == 7) or (joueur == 2 and to_col == 0):
                    L[to_col][to_ligne][1] = 2  # Promouvoir en Dame
            
            return True
    
    return False


def check_game_status_gui(L):
    """
    Pour GUI: Vérifier l'état du jeu
    
    Returns:
        0: Jeu en cours
        1: Victoire noirs (joueur 1)
        2: Victoire blancs (joueur 2)
    """
    black_exists = team_exist(L, 1)
    white_exists = team_exist(L, 2)
    
    if not black_exists:
        return 2  # Victoire blancs
    elif not white_exists:
        return 1  # Victoire noirs
    else:
        return 0  # Jeu continue
```

#### Étape 1.3: Créer le Nouveau Fichier GUI
**Durée:** 4 heures

Créer `dame_gui.py` (voir code d'implémentation ci-dessous)

---

### Phase 2: Implémentation des Fonctionnalités de Base (Priorité: Haute)

#### Étape 2.1: Rendu du Plateau
- Dessin du damier
- Dessin des pions
- Affichage des étiquettes

#### Étape 2.2: Sélection des Pions
- Sélection de pion par clic souris
- Mise en surbrillance du pion sélectionné
- Affichage des destinations possibles

#### Étape 2.3: Mouvement des Pions
- Spécification de destination par clic
- Exécution du mouvement
- Alternance des joueurs

#### Étape 2.4: Fonctionnalité de Capture
- Déplacement par-dessus un pion ennemi
- Suppression du pion capturé

---

### Phase 3: Fonctionnalités Avancées (Priorité: Moyenne)

#### Étape 3.1: Fonctionnalité Dame
- Promotion en atteignant la dernière ligne
- Affichage de la Dame (double cercle, etc.)
- Portée de mouvement de la Dame

#### Étape 3.2: Détection de Victoire
- Fin lorsqu'il n'y a plus de pions
- Affichage du vainqueur
- Fonction de réinitialisation du jeu

#### Étape 3.3: Améliorations UI
- Affichage du joueur actuel
- Historique des mouvements
- Animations

---

### Phase 4: Fonctionnalités Supplémentaires (Priorité: Basse)

#### Étape 4.1: Paramètres du Jeu
- Modification de la taille du plateau
- Modification du nombre de lignes de pions
- Personnalisation des couleurs

#### Étape 4.2: Captures Consécutives
- Captures multiples en un tour
- Règle de capture obligatoire

#### Étape 4.3: Sauvegarde/Chargement
- Sauvegarde de l'état du jeu
- Sauvegarde au format JSON

---

## 5. Structure des Fichiers

```
jeu_de_Dame/
│
├── dame de main.py          # Logique existante + fonctions GUI ajoutées
│   ├── [Existant] creation_de_jeu()
│   ├── [Existant] is_friendly()
│   ├── [Existant] jeu_possible()  ← Bugs corrigés
│   ├── [Existant] team_exist()
│   ├── [Existant] tour()
│   ├── [NOUVEAU] init_board_gui()
│   ├── [NOUVEAU] get_valid_moves_gui()
│   ├── [NOUVEAU] execute_move_gui()
│   └── [NOUVEAU] check_game_status_gui()
│
├── dame_gui.py              # Nouvelle création: GUI principal
│   ├── Classe DameGUI
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
│   └── graphi_thema.py      # GUI existant (référence, non utilisé)
│
├── logic/
│   ├── System logic/
│   │   ├── analyse_logique_dame.md
│   │   └── analyse_logique_dame_ja.md
│   └── integration_plan.md  # Ce document
│
└── règle.json               # Configuration du jeu
```

---

## 6. Liste des Corrections Nécessaires

### 6.1 Corrections de dame de main.py

| Priorité | Ligne | Problème | Correction |
|----------|-------|----------|------------|
| 🔴 Haute | 55 | J non initialisé | Ajouter `J = [0] * len(diags)` |
| 🔴 Haute | 66 | J non initialisé (Dame) | `J = [[0]*len(L[0]) for _ in range(len(L))]` |
| 🔴 Haute | 10,13,16 | Condition toujours True | Changer `or` → `and` |
| 🔴 Haute | 107 | Réutilisation de variable i | Changer variable de boucle en `idx` |
| 🟡 Moyenne | 156 | Alternance joueur | Corriger en `v = (v + 1) % 2` |
| 🟡 Moyenne | 96-97 | print dans input | Retirer `print()` de `input()` |
| 🟢 Basse | Global | Gestion d'exceptions | Ajouter try-except |

### 6.2 Nouveaux Fichiers à Créer

- `dame_gui.py`: Création complète
- `integration_plan.md`: Ce document

---

## 7. Code d'Implémentation

### 7.1 dame_gui.py (Version Complète)

```python
# -*- coding:utf-8 -*-
"""
Jeu de Dame - Version GUI
Interface graphique utilisant la logique de dame de main.py
"""

import sys
import pygame
from pygame.locals import *

# Importer la logique
try:
    import dame_de_main as logic
except ImportError:
    print("Erreur: dame de main.py introuvable")
    sys.exit(1)

# ============================================
# Définition des Constantes
# ============================================

# Configuration écran
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Configuration plateau
BOARD_SIZE = 8
SQUARE_SIZE = 60
BOARD_OFFSET_X = (SCREEN_WIDTH - BOARD_SIZE * SQUARE_SIZE) // 2
BOARD_OFFSET_Y = (SCREEN_HEIGHT - BOARD_SIZE * SQUARE_SIZE) // 2

# Définition des couleurs
COLOR_WHITE_SQUARE = (240, 217, 181)  # Beige
COLOR_BLACK_SQUARE = (181, 136, 99)   # Marron
COLOR_BG = (34, 139, 34)              # Vert
COLOR_HIGHLIGHT = (255, 255, 0)       # Jaune (sélectionné)
COLOR_VALID_MOVE = (0, 255, 0)        # Vert (mouvement possible)
COLOR_VALID_CAPTURE = (255, 165, 0)   # Orange (capture possible)
COLOR_PIECE_BLACK = (255, 0, 0)       # Rouge (pion noir)
COLOR_PIECE_WHITE = (0, 0, 255)       # Bleu (pion blanc)
COLOR_KING_MARK = (255, 215, 0)       # Or (marque Dame)
COLOR_TEXT = (255, 255, 255)          # Blanc (texte)

# Configuration police
FONT_SIZE = 32
SMALL_FONT_SIZE = 24


# ============================================
# Classe DameGUI
# ============================================

class DameGUI:
    """Classe GUI pour le jeu de dames"""
    
    def __init__(self):
        """Initialisation"""
        # Initialisation Pygame
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Jeu de Dame - Dames")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
        
        # État du jeu
        self.L = logic.init_board_gui(BOARD_SIZE, 3)
        self.current_player = 1  # 1=noir(rouge), 2=blanc(bleu)
        self.selected = None     # (col, ligne) ou None
        self.valid_moves = []    # [(col, ligne, type_mouvement), ...]
        self.game_over = False
        self.winner = None
        
    def get_square_from_pos(self, pos):
        """
        Obtenir coordonnées plateau depuis coordonnées écran
        
        Parameters:
            pos: (x, y) coordonnées écran
        
        Returns:
            (col, ligne) ou None
        """
        x, y = pos
        
        # Vérifier hors du plateau
        if (x < BOARD_OFFSET_X or x >= BOARD_OFFSET_X + BOARD_SIZE * SQUARE_SIZE or
            y < BOARD_OFFSET_Y or y >= BOARD_OFFSET_Y + BOARD_SIZE * SQUARE_SIZE):
            return None
        
        # Coordonnée x écran → col, coordonnée y → ligne
        col = (x - BOARD_OFFSET_X) // SQUARE_SIZE
        ligne = (y - BOARD_OFFSET_Y) // SQUARE_SIZE
        
        return (col, ligne)
    
    def draw_board(self):
        """Dessiner le plateau"""
        for col in range(BOARD_SIZE):
            for ligne in range(BOARD_SIZE):
                # Position de la case
                x = BOARD_OFFSET_X + col * SQUARE_SIZE
                y = BOARD_OFFSET_Y + ligne * SQUARE_SIZE
                
                # Couleur de la case (motif damier)
                square_color = self.L[col][ligne][2]
                if square_color == 0:
                    color = COLOR_WHITE_SQUARE
                else:
                    color = COLOR_BLACK_SQUARE
                
                # Dessiner la case
                pygame.draw.rect(self.screen, color, 
                               (x, y, SQUARE_SIZE, SQUARE_SIZE))
                
                # Bordure
                pygame.draw.rect(self.screen, (0, 0, 0), 
                               (x, y, SQUARE_SIZE, SQUARE_SIZE), 1)
    
    def draw_highlights(self):
        """Mettre en surbrillance case sélectionnée et destinations possibles"""
        # Case sélectionnée
        if self.selected:
            col, ligne = self.selected
            x = BOARD_OFFSET_X + col * SQUARE_SIZE
            y = BOARD_OFFSET_Y + ligne * SQUARE_SIZE
            pygame.draw.rect(self.screen, COLOR_HIGHLIGHT, 
                           (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)
        
        # Destinations possibles
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
        """Dessiner les pions"""
        for col in range(BOARD_SIZE):
            for ligne in range(BOARD_SIZE):
                piece_color = self.L[col][ligne][0]
                piece_type = self.L[col][ligne][1]
                
                if piece_color == 0:  # Case vide
                    continue
                
                # Coordonnées centre du pion
                x = BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
                y = BOARD_OFFSET_Y + ligne * SQUARE_SIZE + SQUARE_SIZE // 2
                radius = SQUARE_SIZE // 2 - 8
                
                # Couleur du pion
                if piece_color == 1:
                    color = COLOR_PIECE_BLACK
                else:
                    color = COLOR_PIECE_WHITE
                
                # Dessiner le pion
                pygame.draw.circle(self.screen, color, (x, y), radius)
                pygame.draw.circle(self.screen, (0, 0, 0), (x, y), radius, 2)
                
                # Si Dame, ajouter une marque
                if piece_type == 2:
                    pygame.draw.circle(self.screen, COLOR_KING_MARK, 
                                     (x, y), radius // 2)
                    # Marque couronne simplifiée
                    pygame.draw.circle(self.screen, color, 
                                     (x, y), radius // 2 - 3)
    
    def draw_ui(self):
        """Dessiner éléments UI"""
        # Affichage joueur actuel
        if not self.game_over:
            player_name = "Rouge (Noir)" if self.current_player == 1 else "Bleu (Blanc)"
            text = self.font.render(f"Tour: {player_name}", True, COLOR_TEXT)
            self.screen.blit(text, (10, 10))
        else:
            # Fin du jeu
            winner_name = "Rouge (Noir)" if self.winner == 1 else "Bleu (Blanc)"
            text = self.font.render(f"{winner_name} gagne!", True, COLOR_TEXT)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 30))
            self.screen.blit(text, text_rect)
            
            # Instructions redémarrage
            restart_text = self.small_font.render("Appuyez sur R pour rejouer", 
                                                 True, COLOR_TEXT)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            self.screen.blit(restart_text, restart_rect)
    
    def handle_click(self, pos):
        """Gérer clic souris"""
        if self.game_over:
            return
        
        square = self.get_square_from_pos(pos)
        if square is None:
            return
        
        col, ligne = square
        
        # Si aucun pion sélectionné
        if self.selected is None:
            piece_color = self.L[col][ligne][0]
            
            # Vérifier si c'est son pion
            if piece_color == self.current_player:
                self.selected = (col, ligne)
                # Obtenir mouvements possibles
                self.valid_moves = logic.get_valid_moves_gui(
                    self.L, col, ligne, self.current_player
                )
                print(f"Pion sélectionné: {square}, mouvements possibles: {len(self.valid_moves)}")
        else:
            # Si pion sélectionné
            from_col, from_ligne = self.selected
            
            # Même pion cliqué→désélectionner
            if (col, ligne) == self.selected:
                self.selected = None
                self.valid_moves = []
                print("Désélectionné")
                return
            
            # Autre pion à soi cliqué→changer sélection
            if self.L[col][ligne][0] == self.current_player:
                self.selected = (col, ligne)
                self.valid_moves = logic.get_valid_moves_gui(
                    self.L, col, ligne, self.current_player
                )
                print(f"Pion resélectionné: {square}")
                return
            
            # Tenter mouvement
            success = logic.execute_move_gui(
                self.L, from_col, from_ligne, col, ligne, self.current_player
            )
            
            if success:
                print(f"Mouvement réussi: {self.selected} → {square}")
                
                # Alterner joueur
                self.current_player = 3 - self.current_player
                self.selected = None
                self.valid_moves = []
                
                # Vérifier victoire
                status = logic.check_game_status_gui(self.L)
                if status != 0:
                    self.game_over = True
                    self.winner = status
                    print(f"Fin du jeu: Victoire joueur {status}")
            else:
                print(f"Mouvement échoué: {square} n'est pas une destination valide")
    
    def reset_game(self):
        """Réinitialiser le jeu"""
        self.L = logic.init_board_gui(BOARD_SIZE, 3)
        self.current_player = 1
        self.selected = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        print("Jeu réinitialisé")
    
    def run(self):
        """Boucle principale du jeu"""
        running = True
        
        while running:
            # Remplir arrière-plan
            self.screen.fill(COLOR_BG)
            
            # Dessiner
            self.draw_board()
            self.draw_highlights()
            self.draw_pieces()
            self.draw_ui()
            
            # Gestion événements
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                
                elif event.type == MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                
                elif event.type == KEYDOWN:
                    # Touche R pour redémarrer
                    if event.key == K_r:
                        self.reset_game()
            
            # Mise à jour écran
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS
        
        # Fin
        pygame.quit()
        sys.exit()


# ============================================
# Principal
# ============================================

def main():
    """Fonction principale"""
    game = DameGUI()
    game.run()


if __name__ == "__main__":
    main()
```

---

## 8. Plan de Test

### 8.1 Tests Unitaires

| Élément de test | Fonction cible | Contenu du test |
|-----------------|----------------|-----------------|
| Initialisation plateau | `init_board_gui()` | Pions placés aux bonnes positions |
| Vérification propriété | `is_friendly()` | Identifie correctement les pions du joueur |
| Possibilité mouvement | `get_valid_moves_gui()` | Calcule correctement mouvement/capture |
| Exécution mouvement | `execute_move_gui()` | Pion se déplace correctement |
| Promotion Dame | `execute_move_gui()` | Promotion en dernière ligne |
| Détection victoire | `check_game_status_gui()` | Victoire détectée quand plus de pions |

### 8.2 Tests d'Intégration

1. **Flux de base**
   - Démarrage jeu → sélection pion → mouvement → alternance joueur

2. **Flux de capture**
   - Sélection pion → saut par-dessus ennemi → suppression pion ennemi

3. **Flux Dame**
   - Pion normal atteint dernière ligne → promotion Dame → mouvement omnidirectionnel

4. **Flux victoire**
   - Capture tous pions ennemis → affichage victoire → réinitialisation

### 8.3 Tests UI

- Réactivité clics souris
- Affichage surbrillance
- Dessin pions
- Affichage texte

---

## 9. Calendrier

### Semaine 1: Construction base
- **Jour 1-2**: Correction bugs `dame de main.py`
- **Jour 3-4**: Ajout fonctions interface GUI
- **Jour 5-7**: Implémentation de base `dame_gui.py`

### Semaine 2: Implémentation fonctionnalités
- **Jour 1-2**: Dessin plateau et pions
- **Jour 3-4**: Sélection et mouvement pions
- **Jour 5-7**: Fonctionnalité capture et alternance joueurs

### Semaine 3: Fonctionnalités avancées
- **Jour 1-3**: Fonctionnalité Dame
- **Jour 4-5**: Détection victoire
- **Jour 6-7**: Améliorations UI

### Semaine 4: Tests et ajustements
- **Jour 1-3**: Tests unitaires
- **Jour 4-5**: Tests d'intégration
- **Jour 6-7**: Corrections bugs et ajustements finaux

---

## 10. Problèmes Connus et Contre-mesures

### Problème 1: Différence de structure de données
**Problème:** `L[col][ligne]` vs `board[row][col]`  
**Contre-mesure:** Conversion avec pattern adaptateur

### Problème 2: Confusion d'indexation
**Problème:** 0-based vs 1-based  
**Contre-mesure:** Unification à 0-based dans couche GUI

### Problème 3: Portée de mouvement Dame
**Problème:** Traitement Dame dans `jeu_possible()` complexe  
**Contre-mesure:** D'abord vérifier fonctionnement pion normal, puis implémenter Dame

### Problème 4: Captures consécutives
**Problème:** Règle de captures multiples en un tour  
**Contre-mesure:** Implémentation en Phase 4 (fonctionnalité optionnelle)

---

## 11. Actions Suivantes

### Exécution immédiate

1. ✅ Création de ce document (terminé)
2. ⬜ Commencer correction bugs `dame de main.py`
3. ⬜ Ajouter fonctions interface GUI
4. ⬜ Créer `dame_gui.py` et implémenter fonctionnalités de base

### Points de vérification

- [ ] Commenter main() existant de `dame de main.py`?
- [ ] Vérifier structure de `règle.json` (si utilisé)
- [ ] Modifier couleurs pions? (rouge/bleu vs noir/blanc)

---

## 12. Références

- `logic/System logic/analyse_logique_dame.md` - Analyse détaillée logique
- `logic/System logic/analyse_logique_dame_ja.md` - Version japonaise
- `GUI_SYSTEM/graphi_thema.py` - Implémentation GUI existante
- `dame de main.py` - Implémentation logique existante

---

**Auteur:** AI Assistant  
**Dernière mise à jour:** 2026-01-15  
**Version:** 1.0

