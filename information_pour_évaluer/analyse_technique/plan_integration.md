# Plan d'Intégration GUI-Logic

## Objectif

Intégrer la logique du jeu (`damedemain.py`) avec une interface graphique pour créer un jeu de dames jouable.

## Approche retenue : méthode wrapper

Au lieu de modifier `damedemain.py`, un fichier GUI séparé (`dame_gui_ctk.py`) importe et appelle ses fonctions directement.

```
dame_gui_ctk.py (GUI)
│
├── Appels directs à damedemain.py :
│   ├── is_friendly(L, c, l, v)     → validation de la sélection
│   ├── jeu_possible(L, c, l, d, v) → calcul des mouvements
│   └── team_exist(L, v)            → détection de fin de partie
│
├── Fonctions GUI propres :
│   ├── create_board()     → initialisation (wrapper de creation_de_jeu)
│   ├── get_moves()        → conversion du résultat de jeu_possible
│   ├── do_move()          → exécution du mouvement sur le plateau
│   └── _execute_move()    → orchestration complète (hover, son, score)
│
└── Journal en temps réel :
    └── Chaque appel à damedemain.py est tracé dans le log
```

## Différences de structure de données

| Aspect | `damedemain.py` | `dame_gui_ctk.py` |
|--------|------------------|--------------------|
| Structure | `L[col][ligne][3]` | Même (réutilisée) |
| Joueur | `v` (0=blancs, 1=noirs) | `current_player` (1=noirs, 2=blancs) |
| Entrée | `input()` texte | Clics souris / hover |

## Résultat

L'intégration a été réalisée avec succès via CustomTkinter. La logique de `damedemain.py` est appelée sans modification (sauf les corrections de bugs documentées). Toutes les fonctionnalités avancées (IA, rafle, undo, sauvegarde) sont implémentées dans la couche GUI.
