# Rapport d'Analyse Logique - Jeu de Dame

## 1. Vue d'ensemble

Ce rapport analyse les erreurs logiques et de syntaxe identifiées dans le fichier `damedemain.py` du jeu de Dame. Il fournit également les corrections nécessaires pour assurer le fonctionnement correct du programme.

---

## 2. Erreurs identifiées

### 2.1 Erreurs d'indentation dans `creation_de_jeu()`

**Localisation**: Lignes 19-27

**Problème**:
```python
if i<N:
#je regarde les cases où des pion peuvent etre poser
    if L[i][k][2]==1:
        
elif i>c-N:
    if L[i][k][2]==1:
```

Les blocs `if` et `elif` n'ont pas de corps d'instruction. Les commentaires et les conditions suivantes ne sont pas correctement indentés.

**Impact**: SyntaxError lors de l'exécution.

---

### 2.2 Initialisation incorrecte de listes dans `jeu_possible()`

**Localisation**: Ligne 45 et ligne 60

**Problème**:
```python
J=[]  # Liste vide
for i in range(len(diags)):
    J[i]=1  # Tentative d'accès à un index inexistant
```

**Impact**: IndexError - impossible d'assigner une valeur à un index qui n'existe pas.

**Solution**: Initialiser `J` avec une taille prédéfinie:
```python
J = [0] * len(diags)
```

---

### 2.3 Problèmes dans la fonction `tour()`

#### 2.3.1 Erreur `print()` dans `input()`

**Localisation**: Ligne 120

**Problème**:
```python
d=int(input(print('quelle diagonale?(1 à 4)')))
```

`print()` retourne `None`, ce qui rend le code invalide.

**Solution**:
```python
d=int(input('quelle diagonale?(1 à 4)'))
```

#### 2.3.2 Condition incomplète dans la boucle

**Localisation**: Ligne 148-150

**Problème**:
```python
for i in range(len(M)):
    if L[i*diags[0][0]][i*diags[0][1]]:
        
```

La condition est incomplète et les calculs d'indices risquent de sortir des limites.

**Impact**: SyntaxError et possibilité d'IndexError.

---

### 2.4 Logique manquante pour le traitement des positions

**Localisation**: Lignes 148-152

**Problème**: La logique pour afficher et traiter les positions possibles de déplacement est absente ou incomplète.

---

## 3. Structure de la liste `M`

La liste `M` est initialisée comme `M=[[],[],[]]` et doit contenir:

| Index | Signification | Description |
|-------|---------------|-------------|
| `M[0]` | Positions d'attaque | Où le pion peut capturer un pion adverse |
| `M[1]` | Positions de déplacement | Où le pion peut se déplacer normalement |
| `M[2]` | Positions non accessibles | Pour débogage (optionnel) |

---

## 4. Logique à implémenter

### 4.1 Pour les pions normaux (niveau 1)

```python
if L[ii][h][1] == 1:
    # Parcourir les résultats possibles pour chaque diagonale
    for i in range(len(J)):
        if J[i] == 1:  # Attaque possible
            M[0].append([ii + diags[i][0], h + diags[i][1]])
        elif J[i] == 2:  # Déplacement possible
            M[1].append([ii + diags[i][0], h + diags[i][1]])
    
    # Afficher les options disponibles
    print("Attaques possibles:", M[0])
    print("Déplacements possibles:", M[1])
```

### 4.2 Pour les dames (niveau 2)

```python
elif L[ii][h][1] == 2:
    # Parcourir toutes les positions possibles
    for i in range(len(J)):
        for j in range(len(J[i])):
            if J[i][j] == 1:  # Attaque possible
                M[0].append([i, j])
            elif J[i][j] == 2:  # Déplacement possible
                M[1].append([i, j])
    
    # Afficher les options disponibles
    print("Attaques possibles:", M[0])
    print("Déplacements possibles:", M[1])
```

### 4.3 Sélection de la destination et validation

```python
# Demander au joueur de choisir sa destination
target_col = int(input('Colonne de destination (0 à ' + str(c-1) + ')?'))
target_row = int(input('Ligne de destination (0 à ' + str(l-1) + ')?'))

# Vérifier si la destination est valide
if [target_col, target_row] in M[0]:
    # Effectuer une attaque (capture du pion adverse)
    L[target_col][target_row][0] = L[ii][h][0]
    L[ii][h][0] = 0
    print("Attaque réussie!")
    Y = False
elif [target_col, target_row] in M[1]:
    # Effectuer un déplacement normal
    L[target_col][target_row][0] = L[ii][h][0]
    L[ii][h][0] = 0
    print("Déplacement réussi!")
    Y = False
else:
    print('Ce déplacement n\'est pas possible')
```

---

## 5. Flux d'exécution du tour

```
1. Saisir la position du pion (colonne, ligne)
2. Vérifier que le pion appartient au joueur (is_friendly)
3. Calculer les mouvements possibles (jeu_possible)
4. Stocker les positions valides dans M[0] et M[1]
5. Afficher les options disponibles
6. Demander au joueur sa destination
7. Valider et effectuer le mouvement
8. Passer au tour suivant
```

---

## 6. Problèmes supplémentaires

### 6.1 Décalage d'indexation (1-based vs 0-based)

Le code demande les indices aux utilisateurs avec une plage 1 à `c` et 1 à `l`, mais Python utilise des indices 0-based. Il faut convertir:

```python
ii = int(input(f'quelle colone?(1 à {c})')) - 1  # Soustraire 1
h = int(input(f'quelle ligne?(1 à {l})')) - 1    # Soustraire 1
```

### 6.2 Manque d'importation

Le fichier utilise `json.load()` mais n'importe pas le module `json`:

```python
import json
```

---

## 7. Recommandations

1. **Corriger toutes les erreurs d'indentation** dans `creation_de_jeu()`
2. **Initialiser correctement les listes** `J` et `M`
3. **Implémenter la logique manquante** pour le traitement des positions
4. **Valider les entrées utilisateur** (vérifier les plages)
5. **Gérer les cas limites** (sortie de plateau, pas de mouvement possible)
6. **Ajouter les imports manquants** (`import json`)
7. **Tester chaque fonction** indépendamment avant intégration

---

## Conclusion

Le code contient plusieurs erreurs de syntaxe et de logique qui empêchent son exécution. Les corrections proposées dans ce rapport doivent être appliquées systématiquement pour assurer le bon fonctionnement du jeu de Dame.
