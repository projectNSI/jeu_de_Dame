# Liste des corrections et bugs résolus

Ce document recense les 14 bugs identifiés et corrigés durant le développement.

**Légende testeurs :** B = Billy (tests utilisateur), R = Renan (tests GUI), F = Fumimaro (correction)

---

## Erreurs critiques (crashes)

### 1. Initialisation des listes (`damedemain.py` — ligne 116)

**Détecté par :** Fumimaro (revue de code)
**Symptôme :** `IndexError: list assignment index out of range` au premier accès à `J[i]`

```python
# Avant : liste vide, accès impossible
J = []
J[i] = 1  # IndexError: list assignment index out of range

# Après : pré-allocation explicite (damedemain.py, ligne 119)
J = [0] * len(diags)  # Crée [0, 0, 0, 0]
J[i] = 1  # OK
```

> Trace dans le code : commentaire `# Correction bug #1` à la ligne 116 de `damedemain.py`.

### 2. Liste 2D pour les dames non initialisée (`damedemain.py` — ligne 164)

**Détecté par :** Fumimaro (revue de code)
La fonction `jeu_possible()` n'initialisait pas la matrice pour les dames, causant un `NameError`.

```python
# Avant : J non défini pour le cas dame → NameError à return J
# (pas de J = ... pour le type 2)

# Après (damedemain.py, ligne 168)
J = [[0 for _ in range(len(L[0]))] for _ in range(len(L))]
```

> Trace dans le code : commentaire `# Correction bug #8` à la ligne 164 de `damedemain.py`.

### 3. Décalage d'index utilisateur (`damedemain.py`)

**Détecté par :** Fumimaro (revue de code)
L'utilisateur entre 1-8, les indices Python sont 0-7. Le `-1` manquait.

```python
# Avant
ii = int(input('Quelle colonne?'))

# Après
ii = int(input('Quelle colonne?')) - 1  # Ajouté -1
```

---

## Erreurs logiques (jeu incorrect)

### 4. Détection d'ennemi inversée — BUG LE PLUS CRITIQUE (`damedemain.py` — ligne 132)

**Détecté par :** Billy (tests de capture en partie réelle)
**Corrigé par :** Fumimaro
La formule `(2-v)` retournait la couleur du joueur actuel au lieu de celle de l'ennemi.

```python
# Avant : v=1 (noirs) → 2-1=1 → les noirs cherchaient leurs propres pions comme ennemis!
#         aucune capture possible pour les noirs
if L[new_c][new_l][0] == (2 - v):

# Après (damedemain.py, ligne 138) : v=0 → 1+0=1 (noirs) ✓ ; v=1 → 1+1=2 (blancs) ✓
ennemi = 1 + v
if L[new_c][new_l][0] == ennemi:
```

**Impact :** toutes les captures étaient impossibles pour les noirs. Corrigé pour les pions et les dames.

> Trace dans le code : commentaire `# Correction bug #4` aux lignes 132–138 de `damedemain.py`.
> Assert de précondition ajouté à la ligne 110 : `assert v in (0, 1)`.

### 5. Alternance des joueurs (`damedemain.py`)

**Détecté par :** Fumimaro (revue de code)

```python
# Avant : v augmente indéfiniment (v += 1 à chaque tour)
v += 1 % 2  # équivaut à v += 1

# Après : alterne correctement entre 0 et 1
v = (v + 1) % 2
```

### 6. Condition toujours vraie (`damedemain.py`)

**Détecté par :** Fumimaro (revue de code)

```python
# Avant : toujours True par loi de De Morgan (fc != 0 ou fc != None est toujours vrai)
if fc != 0 or fc != None:

# Après : logique correcte
if fc != 0 and fc:
```

### 7. Promotion en dame basée sur le mauvais axe (`ffdje.py` — ligne 87)

**Détecté par :** Renan (tests de partie)
**Corrigé par :** Fumimaro
La promotion se déclenchait au bord haut/bas (lignes) au lieu du côté adverse (colonnes).

```python
# Avant : basé sur les lignes — incorrect pour un jeu à déplacement horizontal
if to_ligne == 0 or to_ligne == self.l - 1:

# Après (ffdje.py, fonctions apply_quiet_move et maybe_promote_end_of_turn) :
# noirs (1) promus à la dernière colonne ; blancs (2) promus à la première colonne
if (color == 1 and tc == c_max - 1) or (color == 2 and tc == 0):
```

> Trace dans le code : docstring `Correction bug #7 / Renan bug #3` dans `apply_quiet_move`
> et `maybe_promote_end_of_turn` (ffdje.py, lignes 87 et 104).

### 8. Logique de déplacement des dames (`damedemain.py` — ligne 164)

**Détecté par :** Fumimaro (revue de code)
La dame s'arrêtait après la première case au lieu de parcourir toute la diagonale.

```python
# Après : boucle case par case avec flag found_enemy (damedemain.py, ligne 172+)
for d in diags:
    step = 1
    found_enemy = False
    while True:
        nc, nl = c + d[0]*step, l + d[1]*step
        if hors_limites: break
        if case_vide: J[nc][nl] = 1 if found_enemy else 2
        elif ennemi et pas encore trouvé: found_enemy = True
        else: break
        step += 1
```

> Trace dans le code : commentaire `# Correction bug #8` à la ligne 164 de `damedemain.py`.

### 9. Calcul de la position capturée pour les dames (`ffdje.py`)

**Détecté par :** Fumimaro (revue de code)
`(fc+tc)//2` ne fonctionne que pour les sauts d'une case. Pour les dames qui sautent
plusieurs cases, un parcours de la diagonale est nécessaire (voir `_enemy_sq` dans `ffdje.py`).

### 10. Direction de capture des pions (`ffdje.py`)

**Détecté par :** Fumimaro (revue de code)
Les captures étaient restreintes à la direction avant. En jeu de dames, les captures sont
permises dans les 4 directions (géré par `get_moves` dans `ffdje.py`).

---

## Problèmes UX/GUI

### 11. Hover qui disparaît sur la destination (`dame_gui_ctk.py` — ligne 672)

**Détecté par :** Renan (tests GUI en partie réelle)
**Corrigé par :** Fumimaro
Le `<Leave>` du cadre parent se déclenchait avant le `<Enter>` du bouton enfant.

```python
# Avant : effacement immédiat → cases vertes disparaissaient avant d'arriver sur la destination

# Après (dame_gui_ctk.py, ligne 672) : temporisation de 60 ms
def _schedule_clear(self):
    self._clear_timer = self.after(60, self._do_scheduled_clear)

# Annulation si <Enter> arrive à temps (dame_gui_ctk.py, ligne 691)
def _cancel_clear(self):
    if self._clear_timer:
        self.after_cancel(self._clear_timer)
        self._clear_timer = None
```

> Trace dans le code : commentaire `# Correction bug #11 / Renan bug #1` aux lignes 673 et 691
> de `dame_gui_ctk.py`.

### 12. Highlights persistants après déplacement (`dame_gui_ctk.py` — ligne 744)

**Détecté par :** Renan (tests GUI en partie réelle)
**Corrigé par :** Fumimaro
Les variables `hover_piece` et `hover_moves` n'étaient pas réinitialisées avant le redessin.

```python
# Avant : _draw_cell() redessinait en vert car hover_piece/hover_moves encore actifs

# Après (dame_gui_ctk.py, ligne 750) : une ligne ajoutée avant _draw_cell()
self._apply_hover(None, [])  # Nettoie hover_piece=None, hover_moves=[] avant redessin
```

> Trace dans le code : commentaire `# Correction bug #12 / Renan bug #2` à la ligne 744
> de `dame_gui_ctk.py`.

### 13. Lenteur du GUI — lag (`dame_gui_ctk.py` — ligne 641)

**Détecté par :** Billy (tests utilisateur sur plusieurs parties consécutives)
**Corrigé par :** Fumimaro
Chaque événement `<Enter>` redessinait les 64 cases. Ralentissement progressif visible dès 20 coups.

```python
# Avant : redessiner toutes les cases à chaque mouvement de souris (64 opérations)

# Après (dame_gui_ctk.py, _apply_hover, ligne 641) : mise à jour différentielle
# On calcule (old - new_map) et on ne redessine que les 2-4 cases qui changent réellement.
for cell in old:
    if cell not in new_map:
        self._set_bg(cell[0], cell[1])  # Efface seulement ce qui n'est plus surligné
for cell, color in new_map.items():
    self._set_bg(cell[0], cell[1], color)  # Colorie seulement les nouvelles cases
```

> Trace dans le code : commentaire `# Correction bug #11 / Billy bug #4` à la ligne 641
> de `dame_gui_ctk.py`.

---

## Erreur d'environnement

### 14. Module `customtkinter` manquant

**Détecté par :** Fumimaro (configuration du projet)
Ajout de `requirements.txt` avec `customtkinter>=5.2.0`.

---

## Résumé

| # | Type | Fichier | Ligne | Détecteur | Correcteur |
|---|------|---------|-------|-----------|------------|
| 1 | Crash: IndexError J=[] | damedemain.py | 116 | Fumimaro | Fumimaro |
| 2 | Crash: J dame non init | damedemain.py | 164 | Fumimaro | Fumimaro |
| 3 | Crash: index 1-based | damedemain.py | — | Fumimaro | Fumimaro |
| 4 | Logique: ennemi (2-v) | damedemain.py | 132 | **Billy** | Fumimaro |
| 5 | Logique: alternance v | damedemain.py | — | Fumimaro | Fumimaro |
| 6 | Logique: condition OR | damedemain.py | — | Fumimaro | Fumimaro |
| 7 | Logique: promotion axe | ffdje.py | 87 | **Renan** | Fumimaro |
| 8 | Logique: dame diag | damedemain.py | 164 | Fumimaro | Fumimaro |
| 9 | Logique: capture dame pos | ffdje.py | — | Fumimaro | Fumimaro |
| 10 | Logique: capture direction | ffdje.py | — | Fumimaro | Fumimaro |
| 11 | GUI: hover disparaît | dame_gui_ctk.py | 672 | **Renan** | Fumimaro |
| 12 | GUI: highlights fantômes | dame_gui_ctk.py | 744 | **Renan** | Fumimaro |
| 13 | GUI: lag | dame_gui_ctk.py | 641 | **Billy** | Fumimaro |
| 14 | Env: module manquant | requirements.txt | — | Fumimaro | Fumimaro |

| Type | Nombre |
|------|--------|
| Crashes | 3 |
| Logique | 7 |
| UX/GUI | 3 |
| Environnement | 1 |
| **Total** | **14** |
