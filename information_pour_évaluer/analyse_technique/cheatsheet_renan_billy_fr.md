# 📋 Mémo de Test - Erreurs Détectées
## Renan & Billy — Rapport Informel pour Présentation

---

## COMMENT LE JEU FONCTIONNE (Vue d'ensemble)

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUX DU JEU DE DAMES                     │
└─────────────────────────────────────────────────────────────┘

1️⃣  Joueur 1 déplace sa souris sur le plateau
     ↓
2️⃣  Événement <Enter> se déclenche (la souris ENTRE sur une case)
     ↓
3️⃣  Fonction _on_enter() s'exécute
     ├─ Calcule les coups possibles
     ├─ Surligne en VERT les destinations
     └─ Stocke l'état dans hover_piece et hover_moves
     ↓
4️⃣  Joueur clique sur une destination en vert
     ↓
5️⃣  Fonction _execute_move() valide et exécute le coup
     ├─ Met à jour le plateau interne
     └─ Redessine les cases touchées
     ↓
6️⃣  Événement <Leave> se déclenche (la souris SORT de la case)
     ↓
7️⃣  Les surbrillances VERT doivent disparaître
```

**Les bugs se sont produits AUX ÉTAPES 2-3 et 7 → défaut dans la GESTION des ÉVÉNEMENTS SOURIS**

---

## ERREUR #1: Le hover disparaît en bougeant la souris
### (Détecté par RENAN)

#### **Qu'est-ce qu'on a observé:**
- On position la souris sur une pièce noire → elle devient verte ✓
- On déplace vers une destination (case verte en bas) → la destination redevient marron ✗
- Impossible de cliquer car on ne voit pas où cliquer!

#### **Pourquoi ça arrive (cause racine):**

Dans `dame_gui_ctk.py`, les cases du plateau sont en grille comme ça:

```
┌──────────────────────────┐
│ [Board Frame parent]     │  ← Élément Tkinter parent
│ ┌─────────────────────┐  │
│ │ Button 1 │ Button 2│  │  ← 64 petits buttons enfants
│ │ Button 3 │ Button 4│  │
│ └─────────────────────┘  │
└──────────────────────────┘
```

Quand la souris bouge d'une case à l'autre:

```
Timeline du problème:
─────────────────────

Souris de Button_A vers Button_B:

├─ 1️⃣  <Leave> du parent se déclenche
│     └─ EFFACE les surbrillages vert ❌
│
├─ 2️⃣  <Leave> de Button_A 
│
├─ 3️⃣  <Enter> de Button_B
│
└─ 🎉 Trop tard! Les surbrillages ont déjà disparu!
```

Tkinter détecte d'abord que la souris quitte le cadre PARENT avant de voir qu'elle entre dans un child button!

#### **La solution (ce qu'on a trouvé):**

Ajouter une **temporisation** au lieu d'effacer immédiatement:

```python
# Étape 6: Au lieu d'effacer tout de suite...
def _schedule_clear():
    """Planifier l'effacement dans 60 millisecondes"""
    self._clear_timer = self.after(60, self._do_scheduled_clear)

# Étape 2 nouveau: Quand on entre sur une case...
def _on_enter(self, col, ligne):
    self._cancel_clear()  # ← ANNULER le timer!
```

```
Timeline corrigée:
──────────────────

Souris de A vers B:

├─ <Leave> parent    → _schedule_clear() 
│                     └─ "J'vais effacer dans 60ms"
│
├─ <Enter> Button_B  → _cancel_clear()  
│                     └─ "Non, attends! Nouveau survol détecté"
│
└─ 60ms passe
    └─ Mais le timer a été ANNULÉ → Les surbrillages restent! ✓
```

**Fichier:** `dame_gui_ctk.py` ligne 664-672  
**Cause du code:** Pas de gestion des priorités d'événements parent-enfant

---

## ERREUR #2: Les surlignages restent après avoir cliqué
### (Détecté par RENAN)

#### **Qu'est-ce qu'on a observé:**
- On clique pour déplacer une pièce
- Le coup s'exécute ✓
- Mais les cases vert (les anciennes destinations) restent vertes ✗
- On doit attendre quelques secondes pour que ça se réinitialise

#### **Pourquoi ça arrive:**

Après chaque mouvement, le programme doit:
1. **Effacer** les anciennes surbrillances
2. Mettre à jour le plateau visuel
3. Afficher le nouveau plateau

Mais l'ordre était mauvais:

```python
# Code AVANT (mauvais ordre):
def _execute_move(self, fc, fl, tc, tl, is_cap):
    # ... valider le coup ...
    
    # Exécuter le mouvement
    L[fc][fl] = 0  # Ancien emplacement vide
    L[tc][tl] = pion  # Nouvelle position
    
    # ERREUR: on redessine les cases SANS EFFACER le hover d'abord!
    self._draw_cell(fc, fl)
    self._draw_cell(tc, tl)
```

Les variables `hover_piece` et `hover_moves` **gardaient les anciennes valeurs**:
- `hover_piece = (2, 3)` ← l'ancienne position
- `hover_moves = [(3,4), (4,5)]` ← les anciennes destinations

Donc quand on redessine, le système voit ces variables et **remaintient les couleurs vertes**!

#### **La solution:**

Ajouter UNE LIGNE avant d'exécuter le mouvement pour tout nettoyer:

```python
def _execute_move(self, fc, fl, tc, tl, is_cap):
    # ... validations ...
    
    # ← NOUVELLE LIGNE CLÉE
    self._apply_hover(None, [])  # "Efface tous les surlignages"
    
    # Maintenant, les anciennes variables hover_piece et hover_moves
    # sont définies à (None, [])
    
    # Exécuter le mouvement
    L[fc][fl] = 0
    L[tc][tl] = pion
    
    # Redessiner sans les "ghosts" verts
    self._draw_cell(fc, fl)
    self._draw_cell(tc, tl)
```

Comment ça marche:
```python
def _apply_hover(piece, moves):
    # Trouver les ANCIENNES cases à nettoyer
    old_cases = {hover_piece} ∪ {toutes les moves}
    # Trouver les NOUVELLES cases à colorer  
    new_cases = {piece} ∪ {moves}
    
    # Nettoyer ce qui n'est plus dans 'new_cases'
    for case in old_cases - new_cases:
        restore_to_original_color(case)
    
    # Colorer ce qui est dans 'new_cases'
    for case in new_cases:
        color_case(case, color)
```

**Fichier:** `dame_gui_ctk.py` ligne 725 (appel à `_apply_hover(None, [])`)  
**Cause du code:** Oubli de l'ordre d'exécution des opérations visuelles

---

## ERREUR #3: La promotion se fait au mauvais endroit
### (Détecté par RENAN)

#### **Qu'est-ce qu'on a observé:**
- Un pion noir arrivant en haut du plateau se transforme en dame ✗
- Un pion blanc arrivant en bas se transforme en dame ✗
- C'est NORMAL en apparence → Mais ce n'est pas les règles du jeu de dames!

#### **Les VRAIES règles:**
```
   Colonne 0    Colonne 7
   (blanc)      (noir)
       ↓            ↓

●→→→→→→→★  
Pion blanc arrive au bout NOIR 
→ se transforme en dame ✓

★←←←←←←←●
Dame blanche  Pion noir arrive au bout BLANC
                → se transforme en dame ✓
```

**C'EST L'AXE HORIZONTAL (colonne)**, pas vertical (ligne)!

#### **Pourquoi le code était faux:**

```python
# Code AVANT (incorrect):
if to_ligne == 0 or to_ligne == self.l - 1:
    # Améliore promis!
    piece.type = DAME
```

Le problème: `ligne` = axe VERTICAL (haut/bas)
- Mais en dames, on se promeut en atteignant l'axe HORIZONTAL (gauche=blanc, droite=noir)

Exemple:
```
Pion noir partant de [1, 0]:
├─ Ligne = 0 (en bas) AUCUNE promotion
├─ Mais il peut monter jusqu'à [7, 0] (autre coté) → PROMOTION!

Pion blanc partant de [7, 7]:
├─ Ligne = 7 (en haut) AUCUNE promotion  
├─ Mais il peut descendre jusqu'à [0, 7] (autre coté) → PROMOTION!
```

Les pions bougeaient verticalement mais devaient se promouvoir **horizontalement**!

#### **La solution:**

```python
# Code APRÈS (correct):
if (color == 1 and tc == c_max - 1) or (color == 2 and tc == 0):
    piece.type = DAME

# En clair:
# - Pion noir (color=1) → promotion quand colonne = 7 (max)
# - Pion blanc (color=2) → promotion quand colonne = 0 (min)
```

Visualisation du système de coordonnées:

```
Plateau 8×8:

Axe VERTICAL (ligne):  Axe HORIZONTAL (colonne):
      l                        c
      ↑                        
 7    ●                   0   ●
 6                        1
 5                        2   ★ (promotion)
 4                        ...
 3                        7   ●
 2
 1
 0    ■
      →
```

**Fichier:** `ffdje.py` ligne 84-99 (fonction `apply_quiet_move`)  
**Cause du code:** Confusion entre axes vertical et territorial du plateau

---

## ERREUR #4: Le jeu devient de plus en plus lent
### (Détecté par BILLY)

#### **Qu'est-ce qu'on a observé:**
- Au début: le jeu est fluide ✓
- Après 10 mouvements: léger ralentissement
- Après 20 coups: vraiment lent! ✗
- Les mouvements de souris gèlent le GUI temporairement

#### **Pourquoi ça arrive (cause = inefficacité, pas erreur):**

À chaque mouvement de souris qui rentre sur une case, le code redessine TOUTES les 64 cases du plateau:

```python
# Code AVANT (très inefficace):
def _on_enter(self, col, ligne):
    J = jeu_possible(...)  # Calcule les coups depuis cette case
    
    for col_redraw in range(8):  # Boucle sur TOUTES les colonnes
        for row_redraw in range(8):  # Boucle sur TOUTES les lignes
            if (col_redraw, row_redraw) == (col, ligne):
                self.squares[row_redraw][col_redraw].configure(fg_color=GREEN)
            elif destination_possible(col_redraw, row_redraw, J):
                self.squares[row_redraw][col_redraw].configure(fg_color=GREEN)
            else:
                self.squares[row_redraw][col_redraw].configure(fg_color=ORIGINAL)
```

Chaque appel `.configure()` est COÛTEUX en CPU!

```
1 mouvement de souris = 64 appels .configure()
2 mouvements = 128 appels
10 mouvements = 640 appels
50 mouvements = 3200 appels ← Le GUI devient UNE TORTUE
```

#### **La solution:**

Seulement redessiner les cases qui CHANGENT:

```python
# Code APRÈS (optimisé):
def _apply_hover(self, piece, moves):
    # Anciennes surbrillances
    old = {piece_ancienne} ∪ {anciennes_destinations}
    # Nouvelles surbrillances  
    new = {piece_nouvelle} ∪ {nouvelles_destinations}
    
    # Nettoyer seulement ce qui a changé
    for case in old - new:  # Cases qui n'ont plus de surbrillance
        self._set_bg(case)  # 1 appel .configure()
    
    # Colorer seulement ce qui est nouveau
    for case in new - old:  # Nouvelles surbrillances
        self._set_bg(case, color)  # 1 appel .configure()
```

Au lieu de 64 appels → seulement 4-6 appels! 🚀

```
Changement entre deux survols:

AVANT (64 updates):
Move A→B,C,D  →  ████████  ████████  ████████  ████████
Move D→E,F,G  →  ████████  ████████  ████████  ████████
Résultat: 128 updates pour un simple glissement

APRÈS (6 updates):
Move A→B,C,D  →  3 updates (afficher B, C, D)
Move D→E,F,G  →  3 updates (effacer A, afficher E, F, G)
Résultat: 6 updates seulement!

Amélioration = 128/6 ≈ ×21 fois plus rapide!
```

**Fichier:** `dame_gui_ctk.py` lignes 640-654 (fonction `_apply_hover`)  
**Cause du code:** Algorithme O(n²) au lieu d'algorithme différentiel O(Δn)

---

## ERREUR #5 (BONUS): Les sons feedback manquaient
### (Suggéré par BILLY)

#### **Qu'est-ce qu'on a observé:**
- On clique → rien ne se passe visuellement pendant une microseconde
- On ne sait pas si notre action a été enregistrée
- Surtout en mode IA, c'est confus!

#### **La solution (ajoutée par Fumimaro):**

```python
def _play_sound(self, is_capture=False, is_promotion=False):
    if is_promotion:
        beep(440), beep(660), beep(880), beep(1100), beep(1400)
        # Ton montant = victoire musicale ✓
    elif is_capture:
        beep(1400), beep(350)  # Grave→Air = prise d'une pièce!
    else:
        beep(500), beep(1000)  # Bip neutre = déplacement simple
```

Chaque action produit maintenant un RETOUR AUDITIF différent!

**Fichier:** `dame_gui_ctk.py` lignes 1201-1213

---

## ERREUR #6: Les captures arrière étaient impossibles
### (Constaté par BILLY en jouant)

#### **Qu'est-ce qu'on a observé:**
- Un pion noir avec un ennemi blanc en bas-gauche (direction "arrière")
- La case derrière l'ennemi est libre
- On devrait pouvoir capturer... Mais non! ✗

#### **Règles du jeu de dames:**
> Les **captures sont obligatoires et possibles dans TOUTES les directions**, y compris arrière pour les pions.  
> Seuls les **déplacements simples** sont restreints vers l'avant.

#### **Le code était trop restrictif:**

```python
# Code AVANT (sévère):
def get_moves(L, col, ligne, J, v):
    forward = [0, 2] if v == 0 else [1, 3]
    
    for i in range(4):
        if J[i] == 1:  # Capture détectée
            if i in forward:  # ← ERREUR! Filtre même les captures!
                moves.append((capture_pos, True))
                
        if J[i] == 2:  # Déplacement simple
            if i in forward:  # Correct: restreint à l'avant
                moves.append((move_pos, False))
```

Les captures étaient restreintes comme les déplacements simples!

#### **La solution:**

```python
# Code APRÈS (correct):
def get_moves(L, col, ligne, J, v):
    forward = [0, 2] if v == 0 else [1, 3]
    
    for i in range(4):
        if J[i] == 1:  # Capture détectée
            moves.append((capture_pos, True))  # ← Pas de filtre!
            # Les captures vont dans TOUTES les directions
                
        if J[i] == 2:  # Déplacement simple  
            if i in forward:  # Restriction OK pour les mouvements simples
                moves.append((move_pos, False))
```

**Fichier:** `ffdje.py` fonction `get_moves()`  
**Cause du code:** Confusion entre règles de capture et règles de déplacement

---

## 📊 TABLEAU RÉCAPITULATIF POUR LA PRÉSENTATION

| # | Type | Observé | Cause | Correction | Fichier |
|---|------|---------|-------|-----------|---------|
| 1 | GUI | Hover vert disparaît | Événement parent déclenché avant événement enfant | Timer 60ms avec annulation | dame_gui_ctk.py:664 |
| 2 | GUI | Couleurs restent après coup | Variables hover_piece/moves pas vidées | `_apply_hover(None, [])` avant exécution | dame_gui_ctk.py:725 |
| 3 | Logique | Promotion au mauvais endroit | Test sur `ligne` au lieu de `colonne` | Vérifier `tc == 0` ou `tc == max` | ffdje.py:84-99 |
| 4 | Perfs | GUI ralentit au fil du temps | 64 updates à chaque mouche souris | Mise à jour différentielle | dame_gui_ctk.py:640-654 |
| 5 | UX | Pas de feedback sonore | Fonctionnalité manquante | Système multicanal de beeps | dame_gui_ctk.py:124-1213 |
| 6 | Logique | Captures arrière impossibles | Filtre `forward` appliqué aux captures | Retirer filtre pour captures seulement | ffdje.py:get_moves() |

---

## 🎓 COMMENT PRÉSENTER CELA AU PROF

**"Nous avons trouvé 6 problèmes lors du test:**

1. **Erreurs d'événements souris (Renan):** Le hover disparaissait et les couleurs restaient → solution: temporisation intelligente + nettoyage explicite
   
2. **Erreur de logique de promotion (Renan):** Les pions se promouvaient sur le mauvais axe → solution: vérifier la colonne, pas la ligne

3. **Erreur de performance (Billy):** Le GUI ralentissait car on redessainait tout à chaque fois → solution: mise à jour différentielle (seulement les cases qui changent)

4. **Erreur de règles de jeu (Billy):** Les captures arrière étaient bloquées → solution: retirer la restriction sur les captures

5. **Feedback utilisateur (Billy):** Pas de sons pour confirmer les actions → solution: système de beeps multicanal

Ces erreurs venaient d'une compréhension incomplète de:
- L'ordre d'exécution des événements Tkinter
- Les axes du plateau (vertical vs horizontal)
- L'optimisation des algorithmes graphiques
- Les règles précises du jeu de dames"**

---

*— Renan & Billy, testeurs du Jeu de Dames*
