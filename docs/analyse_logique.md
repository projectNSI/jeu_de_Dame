# Analyse Logique - Jeu de Dames

## Vue d'ensemble

Ce document présente l'analyse détaillée de la logique du jeu de dames implémentée dans `damedemain.py`.

## Structure des Données

### Représentation du Plateau

Le plateau est représenté par une liste 3D :
```python
L[colonne][ligne] = [couleur_pion, type_pion, couleur_case]
```

**Indices :**
- `[0]` : Couleur du pion (0 = vide, 1 = noir, 2 = blanc)
- `[1]` : Type de pion (1 = normal, 2 = dame)
- `[2]` : Couleur de la case (0 = blanche, 1 = noire)

**Exemple :**
```python
L[3][2] = [1, 1, 1]  # Pion noir normal sur case noire
L[5][4] = [0, 0, 1]  # Case noire vide
L[2][1] = [2, 2, 1]  # Dame blanche sur case noire
```

## Fonctions Principales

### 1. creation_de_jeu(L, c, l, N)

**Objectif :** Initialiser le plateau avec paramètres personnalisables.

**Paramètres :**
- `L` : Liste du plateau
- `c` : Nombre de colonnes
- `l` : Nombre de lignes  
- `N` : Nombre de lignes de pions par joueur

**Logique :**
1. Configuration interactive des paramètres
2. Validation (assure espace entre camps)
3. Création du damier avec motif alternant
4. Placement initial des pions

**Formule du damier :** `(1+h%2-g%2)%2` crée le motif alternant

### 2. is_friendly(L, c, l, v)

**Objectif :** Vérifier si le pion appartient au joueur actuel.

**Paramètres :**
- `v` : Joueur actuel (0 = blancs, 1 = noirs)

**Logique :**
```python
if v == 0:  # Blancs
    return L[c][l][0] == 2
else:  # Noirs
    return L[c][l][0] == 1
```

### 3. jeu_possible(L, c, l, diags, v, t)

**Objectif :** Calculer les mouvements possibles pour un pion.

**Paramètres :**
- `diags` : Vecteurs diagonaux `[[-1,1], [1,1], [-1,-1], [1,-1]]`

**Codes de retour :**
- `0` : Mouvement impossible
- `1` : Capture possible (saut par-dessus ennemi)
- `2` : Déplacement simple

**Pour pion normal :**
- Vérifie les 4 directions diagonales
- Détecte capture si ennemi adjacent et case vide après
- Détecte déplacement si case adjacente vide

**Pour dame :**
- Parcourt tout le plateau
- Portée illimitée sur diagonales
- Utilise formules mathématiques pour alignement

### 4. team_exist(L, v)

**Objectif :** Vérifier si une équipe a encore des pions.

**Logique :**
```python
for i in range(len(L)):
    for j in range(len(L[i])):
        if L[i][j][0] == v:
            return True
return False
```

### 5. tour(L, c, l, v)

**Objectif :** Gérer un tour complet de jeu.

**Étapes :**

1. **Sélection du pion**
   - Demande position au joueur
   - Vérifie propriété avec `is_friendly()`

2. **Calcul des mouvements**
   - Appelle `jeu_possible()`
   - Affiche options disponibles

3. **Exécution du mouvement**
   - Capture : supprime ennemi, déplace de 2 cases
   - Déplacement : déplace de 1 case

4. **Changement de joueur**
   - Alterne avec `v = (v + 1) % 2`

5. **Vérification victoire**
   - Appelle `team_exist()`

## Directions Diagonales

```
Plateau :          Indices diags:

  ↖  ↑  ↗         [-1,-1] [0] [1,-1]
   \ | /              \    |    /
← ← ◉ → →          [-1,1] ◉  [1,1]
   / | \              /    |    \
  ↙  ↓  ↘          [-1,1] [0]  [1,1]

diags[0] = [-1, 1]  # Haut-gauche
diags[1] = [ 1, 1]  # Haut-droite
diags[2] = [-1,-1]  # Bas-gauche
diags[3] = [ 1,-1]  # Bas-droite

Noirs (v=0) : diags[0] et diags[1] (vers le haut)
Blancs (v=1) : diags[2] et diags[3] (vers le bas)
Dames : toutes les directions
```

## Flux du Jeu

1. Chargement de `regle.json`
2. Initialisation du plateau (`creation_de_jeu`)
3. Boucle de jeu :
   - Tant que les deux équipes existent
   - Exécuter un tour (`tour`)
   - Alterner les joueurs
4. Affichage du vainqueur

## Corrections Effectuées

### Corrections Critiques

1. **Initialisation des listes**
   - Pions normaux : `J = [0] * len(diags)`
   - Dames : `J = [[0]*l for _ in range(c)]`

2. **Conversion d'index**
   - Ajout de `-1` aux entrées utilisateur
   - Conversion 1-based vers 0-based

3. **Conditions logiques**
   - Changement `or` en `and`
   - Correction des vérifications

4. **Boucle de jeu**
   - Ajout du `while` principal
   - Vérification continue des équipes

5. **Alternance joueurs**
   - Correction : `v = (v + 1) % 2`

### Améliorations Apportées

- Commentaires en français
- Validation des limites du plateau
- Gestion d'erreurs améliorée
- Code plus lisible et maintenable

## Compatibilité GUI

### Différences avec graphi_thema.py

| Aspect | damedemain.py | graphi_thema.py |
|--------|--------------|-----------------|
| Structure | `L[col][ligne][3]` | `board[row][col]` |
| Indexation | colonne → ligne | ligne → colonne |
| Couleurs | 1=noir, 2=blanc | 1=rouge, 2=bleu |
| Entrée | `input()` | clics souris |
| Dame | oui (type=2) | non |

### Stratégie d'Intégration

Pour intégrer avec l'interface graphique :

1. Unifier structure de données
2. Adapter fonctions (inverser row/col)
3. Créer classe Game
4. Mapper événements souris
5. Ajouter visualisation des mouvements

## Conclusion

Le code implémente la logique fonctionnelle d'un jeu de dames avec :

- Validation complète des mouvements
- Détection de capture
- Alternance des joueurs
- Détection de victoire
- Support des dames (partiellement)

Les corrections effectuées assurent l'exécution correcte du programme et une base solide pour l'intégration GUI future.
