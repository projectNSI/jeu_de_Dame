# Liste de Corrections Seconde Phase - `dame de main.py`

**Date de création:** 2026-01-22  
**Dernière correction:** 2026-01-22 (Première phase terminée)  
**État:** 5 bugs corrigés sur 14, 5 restants à corriger

---

## 📊 Résumé de l'État des Corrections

| Catégorie | Total | Corrigés | Restants | Taux |
|-----------|-------|----------|----------|------|
| 🔴 Bugs critiques | 5 | 2 | 3 | 40% |
| 🟡 Bugs moyens | 4 | 2 | 2 | 50% |
| 🟢 Problèmes mineurs | 5 | 1 | 4 | 20% |
| **Total** | **14** | **5** | **9** | **36%** |

---

## ✅ Corrections Terminées (Première Phase)

### Corrigé (5 éléments)

#### ✅ 1. Correction des conditions logiques (lignes 10, 13, 16)
**État:** Terminé  
**Correction appliquée:**
```python
# Avant:
if fc != 0 or fc != None:  # Toujours True

# Après:
if fc != 0 and fc:  # Condition correcte
```

#### ✅ 2. Correction de l'alternance des joueurs (ligne 164)
**État:** Terminé  
**Correction appliquée:**
```python
# Avant:
v += 1 % 2  # Équivalent à v += 1

# Après:
v = (v + 1) % 2  # Alterne correctement entre 0 et 1
```

#### ✅ 3. Ajout de la boucle de jeu (lignes 192-194)
**État:** Terminé  
**Correction appliquée:**
```python
# Code ajouté:
while team_exist(L, 1) and team_exist(L, 2):
    resultat = tour(L, c, l, v)
    v = (v + 1) % 2
```

#### ✅ 4. Problème de réutilisation de variable i (évité)
**État:** Terminé  
**Raison:** Le nom de variable a été changé en `ii`, évitant le conflit

#### ✅ 5. Correction du retour de fonction (ligne 172)
**État:** Terminé  
**Correction appliquée:**
```python
# Avant:
return ('les', q, 'a gagner')

# Après:
return f'Les {q} ont gagné!'
```

---

## 🔴 Bugs Critiques à Corriger (Seconde Phase - 3 éléments)

Ces bugs **empêchent l'exécution du programme** et doivent être corrigés en priorité absolue.

### ❌ Bug 1: Liste J non initialisée (pions normaux)

**Localisation:** Ligne 55  
**Priorité:** 🔴 Maximale  
**Impact:** `IndexError: list assignment index out of range`

#### Code actuel (lignes 55-67):
```python
if L[c][l][1]==1:
    J=[]  # ❌ Liste vide
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

#### Code corrigé:
```python
if L[c][l][1]==1:
    J = [0] * len(diags)  # ✅ Pré-allocation de la liste
    for i in range(len(diags)):
        try:
            # Vérification de plage d'abord
            new_c = c + diags[i][0]
            new_l = l + diags[i][1]
            
            # Vérification hors limites
            if not (0 <= new_c < len(L) and 0 <= new_l < len(L[0])):
                J[i] = 0
                continue
            
            # Vérifier possibilité de capture
            if L[new_c][new_l][0] == (2-v):
                capture_c = c + 2*diags[i][0]
                capture_l = l + 2*diags[i][1]
                if (0 <= capture_c < len(L) and 
                    0 <= capture_l < len(L[0]) and
                    L[capture_c][capture_l][0] == 0):
                    J[i] = 1  # Capture possible
                else:
                    J[i] = 0
            # Vérifier déplacement normal
            elif L[new_c][new_l][0] == 0:
                J[i] = 2  # Déplacement simple
            else:
                J[i] = 0
        except IndexError:
            J[i] = 0
```

**Raison de la correction:**
- `J = []` crée une liste vide, l'accès à `J[i]` génère une erreur
- `J = [0] * len(diags)` crée une liste de 4 éléments pré-allouée
- L'ordre logique est également réorganisé (vérification de plage → capture → déplacement)

---

### ❌ Bug 2: Liste J non initialisée pour les dames

**Localisation:** Ligne 68  
**Priorité:** 🔴 Maximale  
**Impact:** `NameError: name 'J' is not defined`

#### Code actuel (lignes 68-80):
```python
elif L[c][l][1]==2:
    # J n'est pas initialisé! ❌
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

#### Code corrigé:
```python
elif L[c][l][1]==2:
    # Initialisation de liste 2D ✅
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

#### Ajouter également un cas par défaut à la fin de la fonction:
```python
    else:
        J = []  # ✅ Cas par défaut
                    
    return J
```

**Raison de la correction:**
- Pour les dames, une liste 2D `J[i][j]` est nécessaire
- `[[0]*nb_colonnes for _ in range(nb_lignes)]` initialise correctement

---

### ❌ Bug 3: Pas de conversion d'index (1-based → 0-based)

**Localisation:** Lignes 98-99  
**Priorité:** 🔴 Haute  
**Impact:** Décalage d'index entre entrée utilisateur et tableau

#### Code actuel (lignes 98-99):
```python
ii=int(input(f'quelle colone?(1 à {c})'))  # Utilisateur entre 1-8
h=int(input(f'quelle ligne?(1 à {l})'))    # Mais tableau indexé 0-7
```

#### Utilisation (ligne 101 etc.):
```python
if is_friendly(L,ii,h,v)==True:  # ❌ Index décalé de 1
    # Accès à L[8][5] causant IndexError
```

#### Code corrigé:
```python
ii = int(input(f'quelle colone?(1 à {c})')) - 1  # ✅ Conversion en 0-based
h = int(input(f'quelle ligne?(1 à {l})')) - 1    # ✅ Conversion en 0-based
```

**Raison de la correction:**
- L'utilisateur voit "1 à 8" mais en interne c'est 0-7
- `-1` nécessaire pour la conversion

**Portée de l'impact:**
- Ligne 98-99: Lors de l'entrée
- Ligne 101: Appel `is_friendly(L,ii,h,v)`
- Ligne 106: Appel `jeu_possible(L,ii,h,diags,v)`
- Tous les endroits utilisant `L[ii][h]`

---

## 🟡 Bugs Moyens à Corriger (Seconde Phase - 2 éléments)

### ❌ Bug 4: Fonction print dans input

**Localisation:** Ligne 117  
**Priorité:** 🟡 Moyenne  
**Impact:** Fonctionne mais affiche `None`, source de confusion

#### Code actuel:
```python
d=int(input(print('quelle diagonale?(1 à 4)')))
```

**Problème:**
1. `print()` affiche à l'écran et retourne `None`
2. `input(None)` est exécuté
3. Ça fonctionne mais ce n'est pas l'intention

#### Code corrigé:
```python
d = int(input('quelle diagonale?(1 à 4)'))  # ✅ Suppression de print
```

---

### ❌ Bug 5: Logique conditionnelle inversée

**Localisation:** Ligne 110  
**Priorité:** 🟡 Moyenne  
**Impact:** Messages affichés avec sens inversé

#### Code actuel (lignes 109-115):
```python
for i in range(len(J)):
    if J == [0] * len(diags):  # ❌ Tous 0 = impossible
        print('une attaque est possible sur la',i+1,'eme diagonale')  # ❌ Inversé!
    elif J[i] ==2:
        print('un deplacement est possible sur la',i+1,'eme diagonale')
    else:
        print('aucun deplacement n est possible avec ce pion')
```

**Problème:**
- `J == [0] * len(diags)` signifie "toutes directions impossibles"
- Pourtant le message dit "attaque possible"

#### Code corrigé:
```python
for idx in range(len(J)):  # Changement de nom de variable
    if J[idx] == 1:  # ✅ Capture possible
        print('une attaque est possible sur la', idx+1, 'eme diagonale')
    elif J[idx] == 2:  # ✅ Déplacement simple possible
        print('un deplacement est possible sur la', idx+1, 'eme diagonale')
    else:  # J[idx] == 0
        print('aucun deplacement n est possible dans cette direction')
```

**Corrections appliquées:**
1. `J == [0] * len(diags)` → `J[idx] == 1` 
2. Vérification pour chaque direction
3. Messages correspondant aux bonnes conditions

---

## 🟢 Problèmes Mineurs Restants (4 éléments)

Ces éléments n'impactent pas le fonctionnement mais améliorent la qualité du code.

### 💡 Amélioration 1: Promotion en dame non implémentée

**Localisation:** Fonction de déplacement  
**Priorité:** 🟢 Basse  
**Correction recommandée:**

```python
# Ajouter après le déplacement:
# Promotion en dame si dernière ligne atteinte
if L[to_col][to_ligne][1] == 1:  # Si pion normal
    if (player == 1 and to_col == 7) or (player == 2 and to_col == 0):
        L[to_col][to_ligne][1] = 2  # Promotion en dame
```

### 💡 Amélioration 2: Captures multiples non implémentées

**Localisation:** Logique de déplacement  
**Priorité:** 🟢 Basse  
**Explication:** Selon les règles officielles, plusieurs captures consécutives en un tour sont possibles

### 💡 Amélioration 3: Amélioration de la gestion d'erreurs

**Localisation:** Global  
**Priorité:** 🟢 Basse  
**Correction recommandée:**

```python
# Validation lors de l'entrée
try:
    ii = int(input(...))
    if not (0 < ii <= c):
        print("Hors limites")
        continue
except ValueError:
    print("Veuillez entrer un nombre")
    continue
```

### 💡 Amélioration 4: Utilisation incorrecte de append()

**Localisation:** Lignes 154, 156  
**Priorité:** 🟢 Basse  
**Code actuel:**
```python
M[0].append(i,j)  # ❌ append() n'accepte qu'un argument
```

**Correction:**
```python
M[0].append((i, j))  # ✅ Ajout en tant que tuple
# ou
M[0].append([i, j])  # ✅ Ajout en tant que liste
```

---

## 📝 Code Complet Corrigé

### Fonction `jeu_possible` (remplacement complet lignes 52-82)

```python
def jeu_possible(L:list,c:int,l:int,diags:list,v:int,t:int=None)->list:
    """regarde si une mouvement est possible"""
    
    # Pion normal
    if L[c][l][1]==1:
        J = [0] * len(diags)  # ✅ Correction 1: Initialisation
        for i in range(len(diags)):
            try:
                # Vérification de plage d'abord
                new_c = c + diags[i][0]
                new_l = l + diags[i][1]
                
                # Vérification hors limites
                if not (0 <= new_c < len(L) and 0 <= new_l < len(L[0])):
                    J[i] = 0
                    continue
                
                # Vérifier possibilité de capture
                if L[new_c][new_l][0] == (2-v):
                    capture_c = c + 2*diags[i][0]
                    capture_l = l + 2*diags[i][1]
                    if (0 <= capture_c < len(L) and 
                        0 <= capture_l < len(L[0]) and
                        L[capture_c][capture_l][0] == 0):
                        J[i] = 1  # Capture possible
                    else:
                        J[i] = 0
                # Vérifier déplacement normal
                elif L[new_c][new_l][0] == 0:
                    J[i] = 2  # Déplacement simple
                else:
                    J[i] = 0
            except IndexError:
                J[i] = 0
    
    # Dame
    elif L[c][l][1]==2:
        J = [[0 for _ in range(len(L[0]))] for _ in range(len(L))]  # ✅ Correction 2: Initialisation
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
        J = []  # ✅ Cas par défaut
                    
    return J
```

### Corrections dans la fonction `tour`

#### Correction A: Conversion d'index (lignes 98-99)
```python
ii = int(input(f'quelle colone?(1 à {c})')) - 1  # ✅ Correction 3
h = int(input(f'quelle ligne?(1 à {l})')) - 1    # ✅ Correction 3
```

#### Correction B: Logique d'affichage des messages (lignes 109-115)
```python
for idx in range(len(J)):  # ✅ Correction 5: Changement de nom de variable
    if J[idx] == 1:  # ✅ Correction 5: Condition corrigée
        print('une attaque est possible sur la', idx+1, 'eme diagonale')
    elif J[idx] == 2:
        print('un deplacement est possible sur la', idx+1, 'eme diagonale')
```

#### Correction C: Suppression de print dans input (ligne 117)
```python
d = int(input('quelle diagonale?(1 à 4)'))  # ✅ Correction 4
```

---

## 🎯 Priorités de Correction

### Phase 1: Corrections critiques (obligatoires)

1. **Bug 1:** Initialisation liste J (pions normaux) - ligne 55
2. **Bug 2:** Initialisation liste J (dames) - ligne 68  
3. **Bug 3:** Conversion d'index - lignes 98-99

**Temps estimé:** 30 minutes  
**Importance:** 🔴 Maximale (sans ça le programme ne fonctionne pas)

### Phase 2: Corrections moyennes (recommandées)

4. **Bug 4:** print dans input - ligne 117
5. **Bug 5:** Correction logique conditionnelle - lignes 109-115

**Temps estimé:** 15 minutes  
**Importance:** 🟡 Moyenne (fonctionne mais incorrectement)

### Phase 3: Améliorations mineures (optionnelles)

6. Implémentation promotion en dame
7. Implémentation captures multiples
8. Renforcement gestion d'erreurs
9. Correction de append()

**Temps estimé:** 1-2 heures  
**Importance:** 🟢 Basse (ajout de fonctionnalités et amélioration qualité)

---

## 📋 Liste de Contrôle

Liste de contrôle pour le processus de correction.

### Phase 1: Corrections critiques

- [ ] Ajouter `J = [0] * len(diags)` à la ligne 55 de la fonction `jeu_possible()`
- [ ] Ajouter `J = [[0]*nb_colonnes for _ in range(nb_lignes)]` à la ligne 68 de la fonction `jeu_possible()`
- [ ] Ajouter `else: J = []` comme cas par défaut à la fin de `jeu_possible()`
- [ ] Ajouter `-1` à la ligne 98 de la fonction `tour()` (conversion d'index)
- [ ] Ajouter `-1` à la ligne 99 de la fonction `tour()` (conversion d'index)

### Phase 2: Corrections moyennes

- [ ] Supprimer `print()` de la ligne 117 de la fonction `tour()`
- [ ] Corriger la logique conditionnelle lignes 109-115 de la fonction `tour()`

### Tests

- [ ] Le programme démarre
- [ ] Possibilité de sélectionner un pion
- [ ] Affichage correct des destinations possibles
- [ ] Exécution des déplacements
- [ ] Le jeu progresse jusqu'à la fin

---

## 🔧 Méthode de Test Après Correction

### Cas de test 1: Fonctionnement de base
```
1. Exécuter le programme
2. Choisir "non" pour les paramètres par défaut
3. Sélectionner un pion (ex: colonne=3, ligne=3)
4. Vérifier l'affichage des directions possibles
5. Exécuter un mouvement
6. Confirmer l'absence d'erreur
```

### Cas de test 2: Capture
```
1. Placer son pion adjacent à un pion ennemi
2. Sélectionner ce pion
3. Vérifier affichage "une attaque est possible"
4. Exécuter la capture
5. Confirmer suppression du pion ennemi
```

### Cas de test 3: Fin de partie
```
1. Capturer tous les pions d'un joueur
2. Vérifier affichage "Les [couleur] ont gagné!"
3. Confirmer fin de la boucle de jeu
```

---

## 📚 Références

- `logic/System logic/analyse_logique_dame_ja.md` - Analyse initiale (14 bugs)
- `logic/System logic/analyse_logique_dame.md` - Version française de l'analyse
- `dame de main.py` - Code source actuel

---

**Auteur:** AI Assistant  
**Dernière mise à jour:** 2026-01-22  
**Prochaine vérification:** Après achèvement des corrections

