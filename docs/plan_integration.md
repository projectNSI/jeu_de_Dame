# Plan d'Intégration GUI-Logic

## Objectif

Intégrer la logique du jeu (`damedemain.py`) avec l'interface graphique (`graphi_thema.py`) pour créer un jeu de dames complet et jouable.

## État Actuel

### damedemain.py (Logique)

**Points forts :**
- Validation des mouvements
- Détection de capture
- Alternance des joueurs
- Détection de victoire
- Support des dames

**Points faibles :**
- Interface en ligne de commande uniquement
- Structure de données complexe (3D)
- Entrée par `input()`

### graphi_thema.py (GUI)

**Points forts :**
- Rendu graphique avec Pygame
- Plateau 8x8 visuel
- Détection des clics souris
- Structure simple

**Points faibles :**
- Aucune logique de jeu
- Pas de validation des mouvements
- Pas de détection de victoire

## Différences Principales

| Aspect | damedemain.py | graphi_thema.py |
|--------|--------------|-----------------|
| Structure données | `L[col][ligne][3]` | `board[row][col]` |
| Indexation | colonne → ligne | ligne → colonne |
| Couleurs pions | 1=noir, 2=blanc | 1=rouge, 2=bleu |
| Entrée | `input()` texte | clics souris |
| Dame | oui | non |

## Stratégie d'Intégration : Méthode Wrapper

### Principe

Créer un nouveau fichier `dame_gui.py` qui :
1. Importe les fonctions de `damedemain.py`
2. Utilise Pygame pour l'affichage
3. Convertit les clics souris en coordonnées de jeu
4. Appelle les fonctions logiques existantes

### Architecture

```
dame_gui.py (nouveau)
│
├── Interface Pygame
│   ├── Affichage du plateau
│   ├── Dessin des pions
│   └── Gestion des événements
│
└── Import damedemain.py
    ├── Appels aux fonctions existantes
    └── Fonctions wrapper sans input()
```

## Unification des Structures de Données

### Problème

Les deux systèmes utilisent des structures différentes :

```python
# damedemain.py
L[col][ligne] = [couleur, type, couleur_case]

# graphi_thema.py
board[row][col] = couleur
```

### Solution : Adapter dans la Couche GUI

```python
# Dans dame_gui.py
class DameGUI:
    def __init__(self):
        # Utiliser la structure de damedemain.py
        self.L = logic.init_board_gui(8, 3)
    
    def convert_click_to_logic(self, screen_x, screen_y):
        """Convertit clic souris en coordonnées logique"""
        col = (screen_x - OFFSET_X) // SQUARE_SIZE
        ligne = (screen_y - OFFSET_Y) // SQUARE_SIZE
        return (col, ligne)
```

## Fonctions Wrapper Nécessaires

### Dans damedemain.py (à ajouter)

```python
def init_board_gui(size=8, num_rows=3):
    """Initialise le plateau sans input()"""
    L = [[[0, 0, (1+h%2-g%2)%2] for g in range(size)] 
         for h in range(size)]
    # Placement des pions...
    return L

def get_valid_moves_gui(L, col, ligne, player):
    """Retourne mouvements possibles sans input()"""
    v = 0 if player == 2 else 1
    if not is_friendly(L, col, ligne, v):
        return []
    diags = [[-1,1], [1,1], [-1,-1], [1,-1]]
    J = jeu_possible(L, col, ligne, diags, v, None)
    return convert_J_to_moves(J, col, ligne, diags)

def execute_move_gui(L, from_col, from_ligne, to_col, to_ligne, player):
    """Exécute mouvement sans input()"""
    # Valider et exécuter le mouvement
    # Retourner True si réussi
    return success

def check_winner_gui(L):
    """Vérifie victoire sans input()"""
    if not team_exist(L, 1):
        return 2  # Blancs gagnent
    if not team_exist(L, 2):
        return 1  # Noirs gagnent
    return 0  # Jeu continue
```

## Étapes d'Implémentation

### Phase 1 : Préparation (2h)

1. Ajouter fonctions wrapper dans `damedemain.py`
2. Tester les fonctions wrapper en console
3. Valider compatibilité

### Phase 2 : Interface de Base (3h)

4. Créer `dame_gui.py`
5. Importer `damedemain.py`
6. Initialiser plateau avec `init_board_gui()`
7. Afficher plateau et pions

### Phase 3 : Interaction (4h)

8. Détecter clic sur pion
9. Afficher mouvements possibles (cercles verts)
10. Exécuter mouvement au deuxième clic
11. Alterner les joueurs

### Phase 4 : Finition (3h)

12. Afficher joueur actuel
13. Détecter et afficher victoire
14. Ajouter bouton restart
15. Polir l'interface

## Exemple de Code : dame_gui.py

```python
import pygame
import damedemain as logic

class DameGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 600))
        self.L = logic.init_board_gui(8, 3)
        self.current_player = 1
        self.selected = None
        self.valid_moves = []
    
    def handle_click(self, pos):
        col, ligne = self.convert_position(pos)
        
        if self.selected is None:
            # Sélectionner pion
            if self.L[col][ligne][0] == self.current_player:
                self.selected = (col, ligne)
                self.valid_moves = logic.get_valid_moves_gui(
                    self.L, col, ligne, self.current_player
                )
        else:
            # Exécuter mouvement
            from_col, from_ligne = self.selected
            success = logic.execute_move_gui(
                self.L, from_col, from_ligne, 
                col, ligne, self.current_player
            )
            if success:
                self.current_player = 3 - self.current_player
                self.selected = None
                self.valid_moves = []
    
    def run(self):
        running = True
        while running:
            self.draw_board()
            self.draw_pieces()
            self.draw_valid_moves()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            pygame.display.flip()
```

## Visualisation des Mouvements

### Couleurs et Marqueurs

- **Pion sélectionné** : Bordure jaune épaisse
- **Mouvement simple** : Cercle vert transparent
- **Capture possible** : Cercle orange transparent
- **Joueur actuel** : Texte en haut de l'écran

### Feedback Visuel

```python
def draw_valid_moves(self):
    for col, ligne, move_type in self.valid_moves:
        x = OFFSET + col * SIZE + SIZE//2
        y = OFFSET + ligne * SIZE + SIZE//2
        
        if move_type == 'capture':
            color = (255, 165, 0)  # Orange
        else:
            color = (0, 255, 0)    # Vert
        
        pygame.draw.circle(self.screen, color, (x, y), 15)
```

## Tests et Validation

### Tests Unitaires

1. Conversion coordonnées écran ↔ logique
2. Sélection de pion
3. Affichage mouvements valides
4. Exécution de mouvement
5. Alternance joueurs
6. Détection victoire

### Tests d'Intégration

1. Partie complète humain vs humain
2. Capture de pions
3. Promotion en dame (futur)
4. Gestion erreurs (clics invalides)

## Conclusion

L'intégration suivra une approche progressive :
1. Fonctions wrapper sans modification du code existant
2. Interface graphique basée sur Pygame
3. Connexion via appels de fonctions
4. Tests et ajustements

Cette méthode préserve la logique existante tout en ajoutant une interface utilisateur moderne et intuitive.
