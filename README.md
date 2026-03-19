# Jeu de Dames - Projet NSI

**Projet:** Implémentation d'un jeu de dames en Python avec interface graphique  
**Classe:** Terminale NSI  
**Date:** Mars 2026

## Guide d'Évaluation

Cette section aide l'enseignant à évaluer le projet efficacement.

### Comment Naviguer dans le Projet

Le projet est organisé de manière claire pour faciliter l'évaluation :

#### 1. Code Source (`src/`)

- **`src/damedemain.py`** - Logique principale du jeu
  - Algorithmes de validation des mouvements
  - Gestion des règles du jeu de dames
  - Détection de capture et de victoire
  - Interface en ligne de commande

- **`src/gui_system/graphi_thema.py`** - Interface graphique (Pygame, legacy)
- **`src/gui_system/dame_gui_ctk.py`** - Interface graphique jouable (CustomTkinter)
  - Utilise les fonctions de `damedemain.py` sans les modifier
  - Plateau cliquable + zone de log des appels de fonctions
  - Affichage des mouvements possibles (vert = déplacement, orange = capture)

#### 2. Documentation (`docs/`)

- **`analyse_logique.md`** - Analyse détaillée de la logique du jeu
- **`plan_integration.md`** - Plan d'intégration GUI/Logic
- **`corrections.md`** - Liste des bugs corrigés et améliorations

#### 3. Configuration (`config/`)

- **`règle.json`** - Fichier de configuration des paramètres du jeu
  - Dimensions du plateau
  - Nombre de lignes de pions
  - Paramètres personnalisables

### Critères d'Évaluation Suggérés

#### 1. Logique du Jeu (50%)

- **Validation des mouvements**
  - Vérification des mouvements légaux (diagonales uniquement)
  - Respect des directions (blancs vs noirs)
  - Gestion des limites du plateau

- **Détection de capture**
  - Identification des prises possibles
  - Suppression correcte des pions capturés
  - Calcul des sauts multiples (partiellement implémenté)

- **Alternance des joueurs**
  - Changement correct de joueur après chaque tour
  - Vérification de propriété des pions

- **Détection de fin de partie**
  - Vérification de l'existence de pions pour chaque équipe
  - Annonce du vainqueur

#### 2. Interface Graphique (30%)

- **Affichage du plateau**
  - Damier 8x8 avec motif alternant
  - Pions colorés (rouge/bleu)
  - Étiquettes de coordonnées

- **Interaction utilisateur**
  - Détection des clics souris
  - Feedback visuel

- **Qualité du rendu**
  - Code propre et organisé
  - Utilisation appropriée de Pygame

#### 3. Documentation et Code (20%)

- **Clarté du code**
  - Noms de variables explicites
  - Structure logique
  - Fonctions bien définies

- **Commentaires en français**
  - Documentation des fonctions (docstrings)
  - Commentaires explicatifs
  - Code compréhensible

- **Documentation technique**
  - README complet
  - Documentation de la logique
  - Plan d'intégration

## Installation et Exécution

### Prérequis

- Python 3.x
- Pygame 2.x

### Installation des Dépendances

```bash
pip install pygame customtkinter
```

### Exécuter le Jeu

#### Interface CustomTkinter (recommandée, jouable)

```bash
python src/gui_system/dame_gui_ctk.py
```

L'interface CustomTkinter offre :
- Un plateau 8x8 cliquable avec damier
- Pions noirs (●) et blancs (○), dames (♔/♕)
- Mouvements possibles en vert (déplacement) et orange (capture)
- Zone de log affichant tous les appels aux fonctions de `damedemain.py`
- Promotion automatique en dame

#### Interface Pygame (legacy)

```bash
python src/gui_system/graphi_thema.py
```

L'interface Pygame affiche :
- Un plateau 8x8 avec damier
- Pions rouges (en haut) et bleus (en bas)
- Détection des clics (position affichée dans la console)

#### Mode Console (Logique Pure)

```bash
python src/damedemain.py
```

Le mode console permet de :
- Configurer les paramètres du jeu
- Jouer tour par tour en entrant les coordonnées
- Tester la logique sans interface graphique

## Fonctionnalités Implémentées

### Complètes

- [x] Plateau 8x8 avec damier
- [x] Initialisation des pions (3 lignes par joueur)
- [x] Pions avec couleurs distinctes
- [x] Validation des mouvements diagonaux
- [x] Détection de capture (saut par-dessus ennemi)
- [x] Alternance correcte des joueurs
- [x] Détection de victoire (élimination totale)
- [x] Interface graphique avec Pygame
- [x] Configuration personnalisable (JSON)
- [x] Commentaires en français

### En Cours / Futures Améliorations

- [x] Promotion en dame (interface CustomTkinter)
- [ ] Captures multiples en un seul tour
- [x] Intégration complète GUI + Logique (CustomTkinter)
- [ ] Animation des mouvements
- [ ] Sauvegarde/Chargement de partie

## Structure du Code

### `src/damedemain.py`

**Fonctions principales :**

```python
def creation_de_jeu(L, c, l, N) -> list:
    """Initialisation du plateau avec paramètres personnalisables"""
    
def is_friendly(L: list, c: int, l: int, v: int) -> bool:
    """Vérifie si le pion appartient au joueur actuel"""
    
def jeu_possible(L: list, c: int, l: int, diags: list, v: int) -> list:
    """Détermine les mouvements possibles pour un pion"""
    
def tour(L: list, c: int, l: int, v: int) -> str:
    """Gère le déroulement d'un tour complet"""
    
def team_exist(L: list, v: int) -> bool:
    """Vérifie si une équipe a encore des pions"""
```

**Structure de données :**

Le plateau est représenté par une liste 3D :
```python
L[colonne][ligne] = [couleur_pion, type_pion, couleur_case]
```

- `couleur_pion` : 0 (vide), 1 (noir), 2 (blanc)
- `type_pion` : 1 (normal), 2 (dame)
- `couleur_case` : 0 (blanche), 1 (noire)

### `src/gui_system/graphi_thema.py`

**Fonctionnalités :**

- Initialisation de Pygame
- Création du plateau graphique 8x8
- Dessin des pions avec `pygame.draw.circle()`
- Gestion des événements (clics, fermeture)
- Boucle de jeu principale avec `pygame.display.update()`

**Constantes :**

```python
SCREEN_SIZE = (600, 500)      # Taille de la fenêtre
BOARD_SIZE = 8                 # Plateau 8x8
SQUARE_SIZE = 50               # Taille d'une case
COLOR_BLACK = (0, 0, 0)        # Couleur noire
COLOR_WHITE = (255, 255, 255)  # Couleur blanche
COLOR_RED = (255, 0, 0)        # Pions rouges
COLOR_BLUE = (0, 0, 255)       # Pions bleus
```

## Améliorations et Corrections

Consultez [`docs/corrections.md`](docs/corrections.md) pour la liste complète des bugs corrigés.

### Corrections Majeures Effectuées

1. **Initialisation correcte des listes**
   - Correction : `J = [0] * len(diags)` au lieu de `J = []`
   - Impact : Évite les erreurs IndexError

2. **Conversion d'index (1-based vers 0-based)**
   - Correction : Ajout de `-1` lors de la saisie utilisateur
   - Impact : Correspondance correcte entre entrée utilisateur et indices du tableau

3. **Conditions logiques**
   - Correction : `if fc != 0 and fc:` au lieu de `if fc != 0 or fc != None:`
   - Impact : Logique de vérification correcte

4. **Boucle de jeu principale**
   - Ajout : `while team_exist(L, 1) and team_exist(L, 2):`
   - Impact : Le jeu continue jusqu'à ce qu'une équipe gagne

5. **Alternance des joueurs**
   - Correction : `v = (v + 1) % 2` au lieu de `v += 1 % 2`
   - Impact : Alternance correcte entre joueur 0 et 1

## Architecture du Projet

```
jeu_de_Dame/
├── src/                      # Code source
│   ├── damedemain.py        # Logique du jeu (390 lignes)
│   └── gui_system/
│       └── graphi_thema.py  # Interface Pygame (100 lignes)
│
├── docs/                     # Documentation
│   ├── analyse_logique.md   # Analyse détaillée de la logique
│   ├── plan_integration.md  # Plan d'intégration GUI/Logic
│   └── corrections.md       # Liste des corrections
│
├── config/                   # Configuration
│   └── règle.json           # Paramètres du jeu
│
├── .gitignore               # Fichiers à ignorer par Git
└── README.md                # Ce fichier
```

## Dépendances Externes

- **Pygame** : Bibliothèque pour l'interface graphique
  - Version recommandée : 2.x
  - Installation : `pip install pygame`

## Tests et Validation

### Test du Mode Console

1. Lancer `python src/damedemain.py`
2. Choisir "non" pour garder les paramètres par défaut
3. Entrer les coordonnées d'un pion noir (ex: colonne 3, ligne 3)
4. Vérifier l'affichage des mouvements possibles
5. Exécuter un mouvement
6. Vérifier l'alternance du joueur

### Test de l'Interface Graphique

1. Lancer `python src/gui_system/graphi_thema.py`
2. Vérifier l'affichage du plateau 8x8
3. Vérifier la présence des pions rouges (haut) et bleus (bas)
4. Cliquer sur différentes cases
5. Vérifier l'affichage des coordonnées dans la console

## Difficultés Rencontrées et Solutions

### 1. Bugs dans la Logique Initiale

**Problème :** Le code initial contenait 14 bugs qui empêchaient l'exécution.

**Solution :** Analyse systématique et correction de chaque bug avec documentation détaillée.

### 2. Structure de Données Complexe

**Problème :** Liste 3D difficile à comprendre et manipuler.

**Solution :** Documentation claire avec commentaires et schémas explicatifs.

### 3. Intégration GUI/Logic

**Problème :** Deux systèmes distincts (GUI et logique) à intégrer.

**Solution :** Plan d'intégration détaillé avec méthode wrapper (en cours).

## Perspectives d'Amélioration

### Court Terme

- Implémenter la promotion en dame
- Intégrer complètement GUI et logique
- Ajouter animations de mouvement

### Moyen Terme

- Captures multiples obligatoires
- Mode deux joueurs en réseau
- Intelligence artificielle (IA)

### Long Terme

- Variantes du jeu (dames internationales, etc.)
- Système de classement
- Tutoriel interactif

## Ressources et Références

- **Documentation Pygame** : https://www.pygame.org/docs/
- **Règles des dames** : https://fr.wikipedia.org/wiki/Dames
- **Python Official Docs** : https://docs.python.org/3/

## Licence et Crédits

**Projet éducatif** - NSI (Numérique et Sciences Informatiques)  
**Établissement:** [Nom du lycée]  
**Année scolaire:** 2025-2026

Ce projet est réalisé dans le cadre du programme NSI de Terminale.

---

## Contact

Pour toute question sur ce projet, veuillez contacter :
- [Nom des élèves]
- [Email de contact]

---

*Dernière mise à jour : Mars 2026*
