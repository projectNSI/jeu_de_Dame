# Liste des corrections et bugs résolus

Ce document recense les 14 bugs identifiés et corrigés durant le développement.

---

## Erreurs critiques (crashes)

### 1. Initialisation des listes (`damedemain.py`)

**Symptôme :** `IndexError: list assignment index out of range`

```python
# Avant : liste vide, accès impossible
J = []
J[i] = 1  # IndexError

# Après : pré-allocation
J = [0] * len(diags)
J[i] = 1  # OK
```

### 2. Liste 2D pour les dames non initialisée (`damedemain.py`)

La fonction `jeu_possible()` n'initialisait pas la matrice pour les dames.

```python
# Ajouté
J = [[0 for _ in range(len(L[0]))] for _ in range(len(L))]
```

### 3. Décalage d'index utilisateur (`damedemain.py`)

L'utilisateur entre 1-8, les indices sont 0-7. Le `-1` manquait.

```python
ii = int(input('Quelle colonne?')) - 1  # Ajouté -1
```

---

## Erreurs logiques (jeu incorrect)

### 4. Détection d'ennemi inversée — BUG LE PLUS CRITIQUE

La formule `(2-v)` retournait la couleur du joueur actuel au lieu de l'ennemi :

```python
# Avant : v=0 → 2-0=2 (blancs = soi-même !)
if L[new_c][new_l][0] == (2 - v):

# Après : v=0 → 1+0=1 (noirs = ennemi ✓)
if L[new_c][new_l][0] == (1 + v):
```

**Impact :** toutes les captures étaient impossibles. Corrigé pour les pions et les dames.

### 5. Alternance des joueurs

```python
# Avant : v augmente indéfiniment
v += 1 % 2  # = v += 1

# Après : alterne entre 0 et 1
v = (v + 1) % 2
```

### 6. Condition toujours vraie

```python
# Avant : toujours True (loi de De Morgan)
if fc != 0 or fc != None:

# Après : logique correcte
if fc != 0 and fc:
```

### 7. Promotion en dame basée sur les mauvais axes (`dame_gui_ctk.py`)

La promotion se déclenchait au bord haut/bas (lignes) au lieu du côté adverse (colonnes).

```python
# Avant : basé sur les lignes (incorrect)
if to_ligne == 0 or to_ligne == self.l - 1:

# Après : basé sur les colonnes (correct)
if (player == 1 and tc == self.c - 1) or (player == 2 and tc == 0):
```

### 8. Logique de déplacement des dames (`damedemain.py`)

La dame ne parcourait pas correctement les diagonales. Réécriture complète avec parcours case par case :

```python
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

### 9. Calcul de la position capturée pour les dames (`dame_gui_ctk.py`)

`(fc+tc)//2` ne fonctionne que pour les sauts d'une case. Pour les dames qui sautent plusieurs cases, parcours de la diagonale nécessaire.

### 10. Direction de capture des pions (`dame_gui_ctk.py`)

Les captures étaient restreintes à la direction avant. En jeu de dames, les captures sont permises dans les 4 directions.

---

## Problèmes UX/GUI

### 11. Hover qui disparaît sur la destination

Le `<Leave>` du cadre parent se déclenchait avant le `<Enter>` du bouton enfant. Solution : temporisation de 60 ms avec annulation.

### 12. Highlights persistants après déplacement

Appel à `_apply_hover(None, [])` ajouté avant l'exécution du mouvement.

### 13. Lenteur du GUI (lag)

Chaque `<Enter>` redessinait les 64 cases. Solution : mise à jour différentielle (`_apply_hover`) qui ne modifie que les cellules changées.

---

## Erreur d'environnement

### 14. Module `customtkinter` manquant

Ajout de `requirements.txt` avec `customtkinter>=5.2.0`.

---

## Résumé

| Type | Nombre |
|------|--------|
| Crashes | 3 |
| Logique | 7 |
| UX/GUI | 3 |
| Environnement | 1 |
| **Total** | **14** |
