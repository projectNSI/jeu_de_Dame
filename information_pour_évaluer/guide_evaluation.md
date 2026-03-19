# Guide d'Évaluation — Jeu de Dames

## Démarrage rapide

```bash
pip install customtkinter
python src/gui_system/dame_gui_ctk.py
```

Le jeu démarre par un **menu principal** où l'on choisit le mode (2 joueurs ou vs IA) et le thème visuel.

---

## Où regarder pour évaluer

| Ce que vous cherchez | Fichier / dossier |
|---------------------|-------------------|
| **Logique du jeu** (algorithmes, règles) | `src/damedemain.py` |
| **Interface graphique** (GUI jouable) | `src/gui_system/dame_gui_ctk.py` |
| **Contribution de chaque membre** | `information_pour_évaluer/travail_de_chaque_membre.md` |
| **Bugs trouvés et corrigés** (14 au total) | `information_pour_évaluer/corrections/` |
| **Analyse technique détaillée** | `information_pour_évaluer/analyse_technique/` |
| **Configuration du jeu** | `config/regle.json` |

---

## Fonctionnalités implémentées

### Logique (`damedemain.py`)

- Plateau configurable (dimensions, lignes de pions)
- Validation des mouvements diagonaux
- Détection et exécution de captures
- Support complet des dames (portée illimitée)
- Détection de fin de partie

### Interface graphique (`dame_gui_ctk.py`)

- Menu principal avec sélection du mode et du thème
- Plateau interactif avec hover et clic
- **IA à 3 niveaux** (aléatoire, glouton, Minimax + Alpha-Beta)
- **Capture en chaîne obligatoire** (rafle)
- **Capture obligatoire** (si capture possible, déplacement simple interdit)
- Système d'annulation (undo) avec Ctrl+Z
- Système d'indices (hint) avec Ctrl+H
- Sauvegarde/chargement de parties (JSON)
- Minuterie par tour et par partie
- 4 thèmes visuels
- Historique des coups avec coordonnées (A1-H8)
- Journal des appels de fonctions en temps réel
- Effets sonores différenciés (déplacement, capture, promotion, victoire)
- Export de l'historique en fichier texte

---

## Architecture du projet

```
jeu_de_Dame/
├── src/
│   ├── damedemain.py              ← Logique du jeu (Bartosz)
│   └── gui_system/
│       ├── dame_gui_ctk.py        ← GUI CustomTkinter (Fumimaro)
│       └── graphi_thema.py        ← GUI Pygame (version initiale)
│
├── config/
│   └── regle.json                 ← Paramètres configurables
│
├── information_pour_évaluer/
│   ├── travail_de_chaque_membre.md
│   ├── guide_evaluation.md        ← Ce fichier
│   ├── corrections/               ← Bugs corrigés
│   └── analyse_technique/         ← Documentation technique
│
├── requirements.txt
└── README.md
```

---

## Points forts du projet

1. **Séparation logique / GUI** : `damedemain.py` contient la logique pure, `dame_gui_ctk.py` l'interface. Les fonctions logiques sont appelées sans modification.

2. **14 bugs identifiés et corrigés** : chaque correction est documentée avec le code avant/après et l'impact sur le jeu.

3. **IA avec Minimax** : algorithme classique d'intelligence artificielle avec élagage Alpha-Beta et fonction d'évaluation à pondération positionnelle.

4. **Traçabilité complète** : le journal en temps réel affiche chaque appel à `is_friendly()`, `jeu_possible()`, `team_exist()` avec les paramètres et résultats.
