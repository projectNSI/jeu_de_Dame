# Analyse Détaillée des Bugs Détectés par Renan et Billy
## Rapport de Test - Explication du Code Avant/Après

---

## Vue d'ensemble

Ce document détaille les 6 bugs découverts par Renan (testeur GUI) et Billy (testeur utilisateur) lors de la phase de test.

| Testeur | Nombre de bugs | Catégorie |
|---|---|---|
| RENAN (Interface graphique) | 3 | Événements souris / Logique affichage |
| BILLY (Utilisation du jeu) | 3 | Performance / Logique jeu |
| TOTAL | 6 | — |

---

## BUGS DÉTECTÉS PAR RENAN

### RENAN — Bug #1: Le hover disparaît lors du déplacement entre pièces

#### Symptôme observé pendant les tests
En survolant une pièce puis en glissant la souris vers une case destination en vert, la surbrillance verte s'efface soudainement. L'utilisateur ne voit plus où il peut cliquer.

#### Role du code (fonctionnement normal attendu)
Le plateau est composé de 64 petits boutons Tkinter arrangés en grille:
- Chaque bouton représente une case
- Quand la souris entre sur une case, un événement `<Enter>` se déclenche
- Le code doit afficher les mouvements possibles en vert
- Quand la souris sort, les surbrillances doivent disparaître

#### Quelle était la défaillance du code original
L'ordre d'exécution réel des événements Tkinter crée un conflictflict:

```
Architecture:
_board_frame (cadre parent)
|-- Button(0,0)
|-- Button(0,1)
|-- ...
|-- Button(7,7)

Quand la souris va de Button_A vers Button_B:

1. Button_A.leave()          Événement: quitter Button_A
2. _board_frame.leave()      PROBLÈME: événement du PARENT se déclenche
   └─ EFFACE les surbrillages vert immédiatement!
3. Button_B.enter()          Trop tard! Les couleurs sont déjà effacées
   └─ Essaie d'afficher les nouveaux surbrillages
   └─ Mais l'utilisateur ne les voit pas!
```

Le bug: Tkinter exécute l'événement `<Leave>` du parent AVANT le `<Enter>` du nouvel enfant.

#### Comment on a changé le code pour corriger
Utiliser une ` temporisation` au lieu d'effacer immédiatement:

```python
# Fichier: dame_gui_ctk.py, lignes 664-672

# Nouveau système de gestion du hover
def _schedule_clear(self):
    """Planifier l'effacement dans 60 millisecondes (pas tout de suite!)"""
    if self._clear_timer:
        self.after_cancel(self._clear_timer)  # Annuler ancien timer s'il existe
    
    # Dire à Tkinter: "Efface dans 60ms"
    # 60ms = assez de temps pour que le nouvel événement <Enter> se déclenche
    self._clear_timer = self.after(60, self._do_scheduled_clear)

def _do_scheduled_clear(self):
    """Effectuer l'effacement après le délai (si rien ne l'a arrêté)"""
    self._clear_timer = None
    if not self._chain_piece:  # Exception: ne pas effacer si capture obligatoire
        self._clear_hover()

def _cancel_clear(self):
    """Annuler le timer si détecte nouvelle entrée"""
    if self._clear_timer:
        self.after_cancel(self._clear_timer)  # Arrêter le timer!
        self._clear_timer = None

def _on_enter(self, col, ligne):
    # CLÉE: Annuler immédiatement si on revient sur une case
    self._cancel_clear()  # <- Nouvelle ligne critique
    
    # Puis afficher les mouvements
    if self._game_over or self._is_ai_turn():
        return
    # ... reste du code de recherche de coups ...
```

Timeline corrigée:
```
Quand souris quitte le plateau:
├─ <Leave> _board_frame
└─ _schedule_clear()
   └─ Timer: "Efface les couleurs dans 60ms"

Quand souris entre sur nouvelle case immédiatement:
├─ <Enter> Button_B
└─ _cancel_clear()
   └─ "Non! N'efface pas, on continue!"
   └─ Arrête le timer maintenant

Résultat:
├─ Les 60ms passent
├─ Le timer était annulé
└─ Les surbrillances restent visibles!
```

#### Résultat après correction
- Les surbrillages verts restent visibles quand on glisse entre pièces
- L'utilisateur peut voir les destinations et cliquer sans problème


---

### RENAN — Bug #2: Les surbrillances vertes restent après un déplacement

#### Symptôme observé pendant les tests
Après avoir cliqué pour déplacer une pièce, les cases qui étaient surlignées en vert restent vertes. Il faut attendre quelques secondes pour les voir redevenir normales.

#### Role du code (fonctionnement normal attendu)
Chaque action doit respecter cet ordre:
1. Utilisateur clique pour exécuter un coup
2. Le système efface les anciennes surbrillances vertes
3. Met à jour l'état du plateau interne
4. Redessine les cases affectées avec leurs vraies couleurs

#### Quelle était la défaillance du code original
L'ordre d'exécution était INCORRECT:

```python
# CODE ORIGINAL (BUGUÉ):
def _execute_move(self, fc, fl, tc, tl, is_cap):
    # ÉTAPE 1: Exécuter le coup
    if is_cap:
        captured = ffdje.apply_capture_no_promote(...)
    else:
        ffdje.apply_quiet_move(...)
    
    # ÉTAPE 2: Redessiner
    self._draw_cell(fc, fl)  # Ancien emplacement
    self._draw_cell(tc, tl)  # Nouvel emplacement
    
    # PROBLÈME:
    # Les variables self.hover_piece et self.hover_moves contiennent
    # TOUJOURS l'ancienne valeur!
```

Le problème détaillé:

```python
# Ces variables stockent les surbrillages actuels
self.hover_piece = (2, 3)     # L'ancienne pièce sélectionnée
self.hover_moves = [(3,4), (4,5)]  # Les anciennes destinations

# Quand _draw_cell() redessine, elle CHECK ces variables:
def _draw_cell(self, col, ligne):
    self._set_bg(col, ligne)  # Appelle _set_bg

def _set_bg(self, col, ligne, bg=None):
    if bg is None:
        # Regarder si cette case doit rester surlignée
        if (col, ligne) == self.hover_piece:
            # self.hover_piece contient TOUJOURS (2,3)!
            # Donc (2,3) redevient verte même après le coup!
            use_hl_color = True
        elif (col, ligne) in self.hover_moves:
            # self.hover_moves contient TOUJOURS [(3,4), (4,5)]!
            use_hl_color = True
    # ...
```

Résultat: Les cases (2,3), (3,4), (4,5) restent VERTES car les variables n'ont jamais été vidées!

#### Comment on a changé le code pour corriger
Ajouter UNE SEULE LIGNE qui nettoie AVANT de redessiner:

```python
# CODE CORRIGÉ:
def _execute_move(self, fc, fl, tc, tl, is_cap, save=True):
    if save and not self._chain_piece:
        self._save_state()
    
    # ... validations ...
    
    # NOUVELLE LIGNE CLÉE:
    self._apply_hover(None, [])  # Vider les surbrillages!
    
    # Maintenant self.hover_piece = None et self.hover_moves = []
    
    # ÉTAPE 2: Exécuter le coup
    p_before = self.L[fc][fl][1]
    captured = None
    if is_cap:
        captured = ffdje.apply_capture_no_promote(self.L, fc, fl, tc, tl)
    else:
        ffdje.apply_quiet_move(self.L, fc, fl, tc, tl, self.c)
    
    # ÉTAPE 3: Redessiner (maintenant sans les "fantômes" verts!)
    cells_to_redraw = {(fc, fl), (tc, tl)}
    if captured:
        cells_to_redraw.add(captured)
    
    for cr, lr in cells_to_redraw:
        self._draw_cell(cr, lr)  # Redessine avec couleurs correctes
```

Comment fonctionne `_apply_hover(None, [])`:

```python
def _apply_hover(self, piece, moves):
    # Déterminer anciennes surbrillances
    old = set()
    if self.hover_piece:
        old.add(self.hover_piece)     # Pouvait être (2,3)
    for m in self.hover_moves:
        old.add((m[0], m[1]))         # Pouvait être [(3,4), (4,5)]
    
    # Déterminer nouvelles surbrillances (vides dans ce cas)
    new_map = {}
    if piece:           # piece = None, on n'entre pas
        new_map[piece] = ...
    for m in moves:     # moves = [], on n'entre pas
        new_map[...] = ...
    
    # Mettre à jour les variables
    self.hover_piece = piece   # Maintenant None
    self.hover_moves = moves   # Maintenant []
    
    # CLÉE: Effacer les anciennes cases qui ne sont plus surlignées
    for cell in old:
        if cell not in new_map:  # Cette case n'est plus surbrillée
            self._set_bg(cell[0], cell[1])  # Remet couleur normale
    
    # Appliquer les nouvelles (il n'y en a pas ici)
    for cell, color in new_map.items():
        self._set_bg(cell[0], cell[1], color)
```

#### Résultat après correction
- Les surbrillages vertes disparaissent correctement après un coup
- Le plateau affiche l'état correct immédiatement

---

### RENAN — Bug #3: La promotion se fait au mauvais endroit du plateau

#### Symptôme observé pendant les tests
Un pion noir arrivant au bord HAUT du plateau se transforme en dame. Un pion blanc arrivant au bord BAS se transforme. C'est superficiellement normal, mais ce ne sont PAS les vraie règles du jeu!

#### Les vraies règles du jeu de dames
En jeu de dames international:
```
Promotion au CÔTÉ ADVERSE horizontal:
- Pion noir: se promeut quand il atteint COLONNE 7 (côté blanc)
- Pion blanc: se promeut quand il atteint COLONNE 0 (côté noir)

PAS au bord vertical!
```

Visualisation:
```
Colonne:  0   1   2   3   4   5   6   7
(blanc)                             (noir)

●→→→→→→→★        Pion blanc: arrivé colonne 7 = PROMEUT
(start)         (promotion)

★←←←←←←←●        Pion noir: arrivé colonne 0 = PROMEUT
(promotion)     (start)
```

#### Quelle était la défaillance du code original
Le code testait l'axe VERTICAL (ligne) au lieu de l'axe HORIZONTAL (colonne):

```python
# CODE BUGUÉ:
if to_ligne == 0 or to_ligne == self.l - 1:
    # PROBLÈME: teste le Y (haut/bas) au lieu du X (gauche/droite)
    piece.type = DAME
```

Confusion des axes:
```
Plateau 8x8:

Axe LIGNE (vertical):       Axe COLONNE (horizontal):
l=0 (bas)                   c=0 (gauche/blanc)
l=1                         c=1
l=2                         c=2
...                         ...
l=7 (haut)                  c=7 (droite/noir)

Code regardait: if to_ligne == 0 or to_ligne == 7
DEVRAIT regarder: if to_colonne == 0 or to_colonne == 7
```

Exemple du bug:
```
Pion noir à (1, 0) se déplaçant à (2, 0):
- ancien code: to_ligne=0, donc PROMEUT
- FAUX! Colonne 2 n'est pas le côté adverse

Pion noir à (6, 5) se déplaçant à (7, 5):
- ancien code: to_ligne=5, donc N'EFFACE PAS
- FAUX! Colonne 7 est le côté blanc, DEVRAIT PROMOUVOIR
```

#### Comment on a changé le code pour corriger
Vérifier la COLONNE au lieu de la LIGNE:

```python
# CODE CORRIGÉ:
# Fichier: ffdje.py, fonction apply_quiet_move()

def apply_quiet_move(L, fc, fl, tc, tl, c_max):
    """Exécute un déplacement simple + promotion si applicable"""
    do_move(L, fc, fl, tc, tl, False)
    
    # Vérifier si la pièce doit être promue
    if L[tc][tl][1] == 1:  # Si c'est un pion (pas déjà dame)
        color = L[tc][tl][0]
        
        # CORRECTION: Vérifier la COLONNE (axe territorial)
        if (color == 1 and tc == c_max - 1) or \
           (color == 2 and tc == 0):
            L[tc][tl][1] = 2  # Transforme en dame
```

Même logique pour les raflès:

```python
# Fichier: ffdje.py, fonction maybe_promote_end_of_turn()

def maybe_promote_end_of_turn(L, tc, tl, c_max):
    """Couronne un pion après une rafle si applicable"""
    if L[tc][tl][1] == 1:
        color = L[tc][tl][0]
        # Même vérification sur les colonnes
        if (color == 1 and tc == c_max - 1) or (color == 2 and tc == 0):
            L[tc][tl][1] = 2
```

#### Résultat après correction
- Les promotions ne se font aux bons endroits
- Respect des vraies règles du jeu de dames
- Conformité internationale

---

## BUGS DÉTECTÉS PAR BILLY

### BILLY — Bug #4: Le jeu ralentit après plusieurs coups

#### Symptôme observé pendant les tests
En jouant plusieurs parties d'affilée, après environ 10-15 mouvements, le GUI devient visiblement lent. Les mouvements de souris gèlent temporairement et il y a une latence avant que les surbrillages verts apparaissent.

#### Role du code (fonctionnement normal attendu)
À chaque mouvement de souris, le code doit:
1. Calculer les coups possibles depuis la case survolée
2. Afficher les destinations en vert
3. Redessiner le plateau

#### Quelle était la défaillance du code original
L'ancien code redessainait TOUTES les 64 cases du plateau, même si seules 2-4 cases changeaient:

```python
# CODE ORIGINAL (TRÈS INEFFICACE):
def _on_enter(self, col, ligne):
    # Calcul des coups possibles
    J = jeu_possible(self.L, col, ligne, DIAGS, v, None)
    
    # PROBLÈME ÉNORME: Boucle sur TOUTES les cases
    for col_redraw in range(self.c):           # 0 à 7
        for row_redraw in range(self.l):       # 0 à 7
            # 64 itérations CHAQUE FOIS!
            
            if (col_redraw, row_redraw) == (col, ligne):
                self.squares[row_redraw][col_redraw].configure(fg_color=GREEN)
            elif est_destination(col_redraw, row_redraw, J):
                self.squares[row_redraw][col_redraw].configure(fg_color=GREEN)
            else:
                self.squares[row_redraw][col_redraw].configure(fg_color=BASE)
            # Chaque .configure() demande du travail à Tkinter!
```

Impact graphique:
```
Chaque ".configure()" est une opération COÛTEUSE:
- Accès au GPU
- Redessinage d'une case
- Synchronisation avec l'écran

1 mouvement de souris = 64 appels .configure()
10 mouvements = 640 appels
20 mouvements = 1280 appels (saturation commence!)
50 mouvements = 3200 appels (GUI gèle!)
```

#### Comment on a changé le code pour corriger
Utiliser la MISE À JOUR DIFFÉRENTIELLE: ne toucher que ce qui change:

```python
# CODE CORRIGÉ (OPTIMISÉ):
# Fichier: dame_gui_ctk.py, lignes 640-654

def _apply_hover(self, piece, moves):
    """Mise à jour intelligente: seulement les cases qui changent"""
    
    # ÉTAPE 1: Identifier les ANCIENNES surbrillances
    old = set()
    if self.hover_piece:
        old.add(self.hover_piece)
    for m in self.hover_moves:
        old.add((m[0], m[1]))
    
    # ÉTAPE 2: Identifier les NOUVELLES surbrillances
    new_map = {}
    if piece:
        new_map[piece] = HL_PIECE
    for m in moves:
        dest_color = m[3] if len(m) > 3 else HL_MOVE
        new_map[(m[0], m[1])] = dest_color
    
    # Mettre à jour les variables
    self.hover_piece = piece
    self.hover_moves = moves
    
    # CLÉE ALGORITHME: Différence ensembliste
    for cell in old:
        if cell not in new_map:
            # Cette case PASSE de normal à surbrillée: ne pas toucher
            # Cette case PASSE de surbrillée à normal: redessiner!
            self._set_bg(cell[0], cell[1])  # 1 appel .configure()
    
    for cell, color in new_map.items():
        # Ces cases doivent être surlignées
        self._set_bg(cell[0], cell[1], color)  # 1 appel .configure()
```

Comparaison d'efficacité:
```
ANCIEN SYSTÈME:
Survol de (2,3) avec destinations (3,4), (4,5):
├─ Mise à jour case (2,3)      → 1 appel
├─ Mise à jour case (3,4)      → 1 appel
├─ Mise à jour case (4,5)      → 1 appel
└─ Mise à jour cases restantes → 61 appels inutiles
Total: 64 appels

Ensuite survol de (3,2) avec destinations (3,3), (4,1):
└─ Recommence: 64 appels
Total après 2 survols: 128 appels!

NOUVEAU SYSTÈME (DIFFÉRENTIEL):
Survol de (2,3) avec destinations (3,4), (4,5):
├─ Mettre à jour (2,3)  → 1 appel
├─ Mettre à jour (3,4)  → 1 appel
└─ Mettre à jour (4,5)  → 1 appel
Total: 3 appels

Ensuite survol de (3,2) avec destinations (3,3), (4,1):
├─ old = {(2,3), (3,4), (4,5)}
├─ new = {(3,2), (3,3), (4,1)}
├─ À nettoyer: (2,3), (4,5)
├─ À colorer: (3,2), (4,1)
└─ Total: 4 appels
Cumul après 2 survols: 7 appels!

AMÉLIORATION: 128 / 7 ≈ 18 fois plus rapide!
```

#### Résultat après correction
- Pas d'accumulation de "dettes" graphiques
- GUI fluide même après 50+ coups
- Expérience de jeu nettement améliorée

---

### BILLY — Bug #5: Absence de feedback sonore

#### Symptôme observé pendant les tests
En jouant, surtout en mode contre l'IA, il manque un retour sensoriel. L'utilisateur ne sait pas si son clic a été enregistré ou si c'est au tour de l'IA.

#### Role du code (fonctionnement attendu)
Chaque action importante devrait produire un son unique pour confirmer:
- Déplacement simple → son neutre
- Capture → son d'impact
- Promotion → son victorieux
- Victoire → fanfare

#### Quelle était la défaillance
Le système de son n'existait PAS du tout dans la version originale.

#### Comment on a ajouté la correction
Fumimaro a implémenté un système de beeps multicanal:

```python
# CODE CORRIGÉ (NOUVEAU):
# Fichier: dame_gui_ctk.py

# Importer le module son Windows
try:
    import winsound
    _HAS_WINSOUND = True
except ImportError:
    _HAS_WINSOUND = False

# Fonction générique pour jouer des beeps
def _beep_seq(notes):
    """Joue une séquence de bips (fréquence Hz, durée ms)"""
    if not _HAS_WINSOUND:
        return
    
    def _play():
        for freq, dur in notes:
            winsound.Beep(freq, dur)
    
    # Exécuter en thread séparé pour ne pas bloquer l'interface
    threading.Thread(target=_play, daemon=True).start()

# Sons différents pour chaque type d'action
def _play_sound(self, is_capture=False, is_promotion=False):
    """Joue le bon son selon le type d'action"""
    if is_promotion:
        # Ton montant (celebration musicale)
        _beep_seq([
            (440, 120),    # Do
            (660, 120),    # Mi
            (880, 120),    # Sol
            (1100, 120),   # Do aigü
            (1400, 200),   # Très aigü (climax)
        ])
    elif is_capture:
        # Saut grave-air (impact de capture)
        _beep_seq([
            (1400, 120),   # Très aigü
            (350, 250)     # Très grave
        ])
    else:
        # Bip neutre (déplacement simple)
        _beep_seq([
            (500, 150),
            (1000, 150)
        ])

def _play_undo_sound(self):
    """Son pour l'annulation"""
    _beep_seq([
        (900, 100),
        (300, 200)
    ])

def _play_victory_sound(self):
    """Fanfare de victoire"""
    _beep_seq([
        (523, 150),
        (659, 150),
        (784, 150),
        (1047, 150),
        (1319, 150),
        (1568, 300)
    ])
```

Intégration dans les mouvements:

```python
# Fichier: dame_gui_ctk.py - fonction _execute_move()

def _execute_move(self, fc, fl, tc, tl, is_cap):
    # ... exécution du coup ...
    
    # Jouer le son approprié
    if promoted:
        self._play_sound(is_capture=False, is_promotion=True)
    elif is_cap:
        self._play_sound(is_capture=True, is_promotion=False)
    else:
        self._play_sound(is_capture=False, is_promotion=False)
```

#### Résultat après correction
- Feedback confirmant chaque action
- Amélioration significative de l'UX
- Le jeu devient plus engageant

---

### BILLY — Bug #6: Les captures vers l'arrière étaient impossibles

#### Symptôme observé pendant les tests
Un pion noir avec un ennemi blanc adjacent en diagonale "arrière" ne peut pas le capturer, même si la case derrière est libre.

#### Les vraies règles du jeu de dames
```
CAPTURE: obligatoire et possible dans TOUTES les directions
         (avant et arrière pour les pions)

DÉPLACEMENT SIMPLE: restreint à la direction "avant" pour les pions

DAME: liberté totale dans les deux sens
```

#### Quelle était la défaillance du code original
Le code filtrait les captures de la même façon que les mouvements simples:

```python
# CODE BUGUÉ:
# Fichier: ffdje.py, fonction get_moves()

def get_moves(L, col, ligne, J, v):
    moves = []
    
    forward = [0, 2] if v == 0 else [1, 3]  # Directions "avant"
    
    for i in range(4):
        if J[i] == 1:  # Capture possible
            if i in forward:  # ERREUR! Applique le filtre aux captures!
                moves.append((col + 2*DIAGS[i][0], 
                              ligne + 2*DIAGS[i][1], True))
        
        elif J[i] == 2:  # Déplacement simple
            if i in forward:  # Correct pour les déplacements
                moves.append((col + DIAGS[i][0], 
                              ligne + DIAGS[i][1], False))
```

Exemple concret:
```
Pion noir (v=1) à (2, 2) avec ennemi blanc en direction [2] (haut-gauche):

forward = [1, 3] pour noirs (bas-gauche, bas-droit)
DIAGS[2] = [-1, -1] (haut-gauche) - pas dans forward!

Résultat:
├─ Ennemi trouvé: J[2] = 1 (capture possible)
├─ i=2, forward=[1,3]
├─ 2 NOT in forward
└─ Capture REFUSÉE (BUG!)
```

#### Comment on a changé le code pour corriger
Retirer le filtre `forward` pour les captures SEULEMENT:

```python
# CODE CORRIGÉ:
# Fichier: ffdje.py

def get_moves(L, col, ligne, J, v):
    """Les captures sont libres, les déplacements sont limités"""
    moves = []
    
    forward = [0, 2] if v == 0 else [1, 3]  # Seulement pour mouvements
    
    for i in range(4):
        if J[i] == 1:  # Capture possible
            # CORRECTION: PAS DE FILTRE forward pour les captures!
            moves.append((col + 2*DIAGS[i][0],
                          ligne + 2*DIAGS[i][1], True))
            # Captures autorisées dans TOUTES les directions
        
        elif J[i] == 2:  # Déplacement simple
            if i in forward:  # Filtre UNIQUEMENT pour déplacements
                moves.append((col + DIAGS[i][0],
                              ligne + DIAGS[i][1], False))
```

Différence clé:
```
AVANT: Capture ET déplacement → filtres forward
APRÈS: Capture libre (4 directions)
       Déplacement → filtré (2 directions avant)
```

#### Résultat après correction
- Captures possibles dans toutes les directions
- Respect des vraies règles du jeu

---

## RÉSUMÉ DE TOUS LES BUGS

| Testeur | Bug | Cause | Correction |
|---|---|---|---|
| RENAN | Hover disparaît | Événement parent trop tôt | Timer 60ms avec annulation |
| RENAN | Couleurs résiduelles | Variables hover non vidées | `_apply_hover(None, [])` préalable |
| RENAN | Promotion mauvais axe | Teste ligne au lieu de colonne | Vérifier colonne =c_max |
| BILLY | GUI ralentit | 64 updates à chaque survol | Mise à jour différentielle |
| BILLY | Pas de son | Fonctionnalité absente | Système de beeps |
| BILLY | Captures arrière impossibles | Filtre forward appliqué aux captures | Retirer filtre pour captures |

---

*Rapport de test par Renan et Billy*
