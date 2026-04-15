# Analyse Logique — `damedemain.py`

Ce document présente en détail la logique du jeu de dames implémentée dans `src/damedemain.py`, avec des diagrammes visuels pour chaque concept.

---

## 1. Structure de données du plateau

Le plateau est stocké dans une liste 3D Python :

```python
L[colonne][ligne] = [couleur_pion, type_pion, couleur_case]
```

Chaque case du plateau contient un triplet de trois valeurs entières :

| Champ | Index | Valeur 0 | Valeur 1 | Valeur 2 |
|-------|-------|----------|----------|----------|
| **couleur_pion** | `[0]` | Case vide | Pion **noir** | Pion **blanc** |
| **type_pion** | `[1]` | Pas de pièce | Pion **normal** | **Dame** (promu) |
| **couleur_case** | `[2]` | Case **blanche** (non jouable) | Case **noire** (jouable) |

### Pourquoi trois informations par case ?

- `couleur_pion` permet de savoir quel joueur occupe la case (ou si elle est vide).
- `type_pion` distingue un pion normal d'une dame (qui a des règles de mouvement différentes).
- `couleur_case` détermine si la case est jouable : au jeu de dames, on ne joue que sur les cases noires.

### Exemples concrets

```python
L[0][1] = [1, 1, 1]   # Colonne A, ligne 2 : pion noir normal sur case noire
L[3][4] = [0, 0, 1]   # Colonne D, ligne 5 : case noire VIDE (pas de pion)
L[7][0] = [2, 2, 1]   # Colonne H, ligne 1 : dame blanche sur case noire
L[2][2] = [0, 0, 0]   # Colonne C, ligne 3 : case BLANCHE (jamais jouable)
```

### Visualisation du plateau initial (8×8, N=3)

Les colonnes vont de gauche à droite (A→H = index 0→7), les lignes de haut en bas (1→8 = index 0→7).

```
       Colonnes
       A   B   C   D   E   F   G   H
     ┌───┬───┬───┬───┬───┬───┬───┬───┐
  1  │   │ ● │   │ ● │   │   │   │   │  ← Lignes
     ├───┼───┼───┼───┼───┼───┼───┼───┤     de pions
  2  │ ● │   │ ● │   │   │   │   │   │     noirs
     ├───┼───┼───┼───┼───┼───┼───┼───┤     (colonnes
  3  │   │ ● │   │ ● │   │   │   │   │      0, 1, 2)
     ├───┼───┼───┼───┼───┼───┼───┼───┤
  4  │   │   │   │   │   │   │   │   │  ← Zone vide
     ├───┼───┼───┼───┼───┼───┼───┼───┤     (séparation
  5  │   │   │   │   │   │   │   │   │      entre camps)
     ├───┼───┼───┼───┼───┼───┼───┼───┤
  6  │   │   │   │   │   │ ○ │   │ ○ │  ← Lignes
     ├───┼───┼───┼───┼───┼───┼───┼───┤     de pions
  7  │   │   │   │   │ ○ │   │ ○ │   │     blancs
     ├───┼───┼───┼───┼───┼───┼───┼───┤     (colonnes
  8  │   │   │   │   │   │ ○ │   │ ○ │      5, 6, 7)
     └───┴───┴───┴───┴───┴───┴───┴───┘

  ● = pion noir (couleur_pion = 1)
  ○ = pion blanc (couleur_pion = 2)
  Les pions ne sont placés que sur les cases noires (couleur_case = 1).
  Les noirs avancent vers la droite (colonnes croissantes).
  Les blancs avancent vers la gauche (colonnes décroissantes).
```

> **Important** : dans ce jeu, les deux camps avancent latéralement (noirs → droite, blancs → gauche), et non verticalement comme dans un damier classique. C'est pourquoi la promotion en dame se fait en atteignant la colonne opposée, pas la ligne opposée.

---

## 2. Le système de coordonnées

L'accès au plateau se fait toujours par `L[colonne][ligne]` :

```
L[ colonne ][ ligne ]
     ↓          ↓
   axe X      axe Y
  (gauche     (haut
   → droite)   → bas)
```

Correspondance entre coordonnées et notation :

```
col = 0 → lettre A       ligne = 0 → numéro 1
col = 1 → lettre B       ligne = 1 → numéro 2
col = 2 → lettre C       ligne = 2 → numéro 3
  ...                       ...
col = 7 → lettre H       ligne = 7 → numéro 8
```

La fonction `cell_name(col, ligne)` convertit `(3, 5)` en `"D6"`.

---

## 3. Les vecteurs diagonaux — explication détaillée

Au jeu de dames, toutes les pièces se déplacent **en diagonale**. Les 4 directions possibles sont représentées par des vecteurs `[Δcolonne, Δligne]` :

```python
diags = [[-1, 1], [1, 1], [-1, -1], [1, -1]]
#          ↑        ↑       ↑         ↑
#        diags[0] diags[1] diags[2]  diags[3]
```

### Signification de chaque vecteur

Chaque vecteur dit « quand on avance d'un pas dans cette direction, de combien change la colonne et la ligne ».

```
diags[0] = [-1, +1]     diags[1] = [+1, +1]
  colonne −1, ligne +1    colonne +1, ligne +1
  → vers le HAUT-GAUCHE   → vers le HAUT-DROITE
  (col diminue,           (col augmente,
   ligne augmente)         ligne augmente)

diags[2] = [-1, −1]     diags[3] = [+1, −1]
  colonne −1, ligne −1    colonne +1, ligne −1
  → vers le BAS-GAUCHE    → vers le BAS-DROITE
  (col diminue,           (col augmente,
   ligne diminue)          ligne diminue)
```

### Visualisation sur le plateau

Prenons un pion en position D4 (col=3, ligne=3). Voici les 4 directions :

```
                col 2   col 3   col 4
                  C       D       E
              ┌───────┬───────┬───────┐
    ligne 4   │ C5    │       │ E5    │
              │diags  │       │diags  │
              │ [0]   │       │ [1]   │
              │[-1,+1]│       │[+1,+1]│
              ├───────┼───────┼───────┤
    ligne 3   │       │  ◉ D4│       │   ◉ = pion en D4
              │       │       │       │
              ├───────┼───────┼───────┤
    ligne 2   │ C3    │       │ E3    │
              │diags  │       │diags  │
              │ [2]   │       │ [3]   │
              │[-1,-1]│       │[+1,-1]│
              └───────┴───────┴───────┘
```

### Quelle direction pour quel joueur ?

Les pions normaux ne peuvent avancer que dans la direction de leur camp adverse :

```
                    diags utilisés
  Joueur     Identifiant   pour AVANCER      Direction
  ─────────  ─────────── ───────────────── ────────────────
  Blancs     v = 0       diags[0], diags[2]  colonnes décroissantes
                                              (vers la gauche)
  Noirs      v = 1       diags[1], diags[3]  colonnes croissantes
                                              (vers la droite)
  Dames      tout        les 4 directions    portée illimitée
```

**En capture**, les pions normaux peuvent sauter dans **les 4 directions** (pas seulement vers l'avant). Seuls les déplacements simples sont restreints à la direction avant.

---

## 4. Fonctions principales

### 4.1 `creation_de_jeu(L, c, l, N)`

Initialise le plateau avec les paramètres du fichier `config/regle.json`.

**Formule du damier :**

```python
couleur_case = (1 + h % 2 - g % 2) % 2
```

Cette formule crée le motif alternant noir/blanc. Pour chaque case `(h, g)`, elle donne 0 (case blanche) ou 1 (case noire). Les pions ne sont placés que sur les cases noires (`couleur_case == 1`).

**Placement des pions :**

```
Colonnes 0 à N−1           → pions noirs (couleur_pion = 1)
Colonnes N à (c−N−1)       → zone vide
Colonnes (c−N) à (c−1)     → pions blancs (couleur_pion = 2)
```

### 4.2 `is_friendly(L, c, l, v)`

Vérifie si le pion en position `(c, l)` appartient au joueur `v`.

```
Joueur v = 0 (blancs)  →  possède les pions de couleur 2
Joueur v = 1 (noirs)   →  possède les pions de couleur 1
```

Ce mapping inversé (v=0 possède couleur=2, v=1 possède couleur=1) est une convention du code original.

### 4.3 `jeu_possible(L, c, l, diags, v, t)` — Fonction centrale

C'est la fonction la plus importante du jeu. Elle prend un pion en position `(c, l)` et retourne quels mouvements sont possibles.

#### Valeurs de retour

Pour un **pion normal**, elle retourne une liste de 4 entiers (un par direction diagonale) :

```python
J = [0, 2, 0, 1]
#    ↑   ↑   ↑   ↑
#  diags[0]  [1]  [2]  [3]
#    │    │    │    │
#    │    │    │    └─ 1 = CAPTURE possible (saut en diags[3])
#    │    │    └───── 0 = mouvement IMPOSSIBLE (hors limites ou bloqué)
#    │    └────────── 2 = DÉPLACEMENT simple possible (case vide en diags[1])
#    └─────────────── 0 = mouvement IMPOSSIBLE
```

Pour une **dame**, elle retourne une matrice 2D `J[col][ligne]` de la taille du plateau, où chaque case contient 0, 1 ou 2.

#### Algorithme pour un pion normal — étape par étape

Exemple : pion noir en D4 (col=3, ligne=3), `v=1`.

```
Pour chaque direction diags[i]:
  1. Calculer la case adjacente :
     new_c = col + diags[i][0]
     new_l = ligne + diags[i][1]

  2. Vérifier les limites du plateau

  3. Si la case adjacente contient un ENNEMI (couleur == 1 + v) :
     → Vérifier si on peut sauter (case derrière l'ennemi vide ?)
     → Si oui : J[i] = 1 (CAPTURE)

  4. Si la case adjacente est VIDE :
     → J[i] = 2 (DÉPLACEMENT SIMPLE)

  5. Sinon (allié ou hors limites) :
     → J[i] = 0 (IMPOSSIBLE)
```

**Visualisation d'une capture :**

```
  Avant capture          Après capture
  ┌───┬───┬───┐          ┌───┬───┬───┐
  │   │   │   │          │   │   │ ● │  ← pion noir atterrit ici
  ├───┼───┼───┤          ├───┼───┼───┤
  │   │ ○ │   │          │   │   │   │  ← pion blanc supprimé
  ├───┼───┼───┤          ├───┼───┼───┤
  │ ● │   │   │          │   │   │   │  ← case d'origine vidée
  └───┴───┴───┘          └───┴───┴───┘

  Le pion noir (●) saute par-dessus le pion blanc (○).
  Le pion blanc est supprimé du plateau.
  Le pion noir atterrit 2 cases plus loin dans la direction du saut.
```

#### Algorithme pour une dame

La dame parcourt chaque diagonale case par case, sans limite de distance :

```
Pour chaque direction d dans diags:
  step = 1, found_enemy = False
  Répéter:
    nc = col + d[0] × step
    nl = ligne + d[1] × step

    Si hors limites → STOP (passer à la diagonale suivante)
    Si case vide :
      → Si found_enemy : J[nc][nl] = 1  (atterrissage après capture)
      → Sinon :          J[nc][nl] = 2  (déplacement simple)
    Si ennemi ET pas encore trouvé d'ennemi :
      → found_enemy = True (marquer qu'on a trouvé un ennemi)
    Si allié OU deuxième ennemi :
      → STOP

    step += 1
```

**Visualisation du parcours d'une dame :**

```
  ◈ = dame blanche en E3 (col=4, ligne=2)
  Parcours de diags[0] = [-1, +1] (haut-gauche) :

       A     B     C     D     E
     ┌─────┬─────┬─────┬─────┬─────┐
  6  │  2  │     │     │     │     │  step=4 : case vide → J=2
     ├─────┼─────┼─────┼─────┼─────┤
  5  │     │  2  │     │     │     │  step=3 : case vide → J=2
     ├─────┼─────┼─────┼─────┼─────┤
  4  │     │     │  2  │     │     │  step=2 : case vide → J=2
     ├─────┼─────┼─────┼─────┼─────┤
  3  │     │     │     │  2  │     │  step=1 : case vide → J=2
     ├─────┼─────┼─────┼─────┼─────┤
  2  │     │     │     │     │  ◈  │  Position de la dame
     └─────┴─────┴─────┴─────┴─────┘

  Si un ennemi se trouvait en C4, les cases après (B5, A6) auraient J=1 (capture).
```

### 4.4 `team_exist(L, v)`

Parcourt toutes les cases du plateau. Retourne `True` dès qu'un pion de la couleur `v` est trouvé, `False` si aucun n'existe. Utilisée pour détecter la fin de partie.

### 4.5 `tour(L, c, l, v)`

Orchestre un tour complet en mode console :

```
  Début du tour
       │
       ▼
  ┌─────────────┐
  │ Sélectionner │ ← Le joueur entre la colonne et la ligne
  │  un pion     │    is_friendly() vérifie la propriété
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  Calculer    │ ← jeu_possible() retourne les directions
  │ mouvements   │    possibles (0, 1 ou 2 par direction)
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  Exécuter    │ ← Le joueur choisit une diagonale
  │ le mouvement │    Le pion est déplacé ou capture un ennemi
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  Changer de  │ ← v = (v + 1) % 2
  │   joueur     │    Vérifie si les deux équipes existent encore
  └─────────────┘
```

---

## 5. Détection de l'ennemi — le bug critique corrigé

La formule originale utilisait `(2 - v)` pour détecter un ennemi :

```
  v = 0 (blancs) → 2 − 0 = 2 → c'est la couleur des blancs = SOI-MÊME !
  v = 1 (noirs)  → 2 − 1 = 1 → c'est la couleur des noirs  = SOI-MÊME !
```

La formule corrigée utilise `(1 + v)` :

```
  v = 0 (blancs) → 1 + 0 = 1 → c'est la couleur des noirs  = ENNEMI ✓
  v = 1 (noirs)  → 1 + 1 = 2 → c'est la couleur des blancs = ENNEMI ✓
```

Ce bug empêchait toute capture dans le jeu.

---

## 6. Flux global du programme

```
  Démarrage
      │
      ▼
  Charger config/regle.json
  (dimensions, lignes de pions)
      │
      ▼
  creation_de_jeu()
  (créer damier, placer pions)
      │
      ▼
  ┌──────────────────────────┐
  │  while team_exist(L, 1)  │ ← Boucle principale
  │    and team_exist(L, 2)  │    tant que les 2 équipes existent
  │         │                │
  │         ▼                │
  │    tour(L, c, l, v)      │ ← Un tour de jeu
  │         │                │
  │         ▼                │
  │    v = (v + 1) % 2       │ ← Alterner les joueurs
  └──────────────────────────┘
      │
      ▼
  Afficher le vainqueur
```
