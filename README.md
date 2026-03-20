# Jeu de Dames — Projet NSI

**Équipe :** Bartosz, Fumimaro, Renan, Billy  
**Année scolaire :** 2025–2026

---

## Lancer le jeu

### Interface CustomTkinter (bureau)

```bash
pip install customtkinter
python src/gui_system/dame_gui_ctk.py
```

### Interface Pygame (bureau + compatible web)

```bash
pip install pygame
python src/gui_system/dame_gui_pygame.py
```

Le menu principal apparaît. Choisissez le mode de jeu et le thème, puis cliquez **Commencer**.

### Affichage plein écran (Pygame)

- Le jeu Pygame démarre en plein écran.
- `F11` permet de basculer entre plein écran et fenêtre.

---

## Structure du projet

```
jeu_de_Dame/
│
├── src/                                ← Code source
│   ├── damedemain.py                   ← Logique du jeu (Bartosz)
│   └── gui_system/
│       ├── dame_gui_ctk.py             ← Interface CustomTkinter (Fumimaro)
│       ├── dame_gui_pygame.py          ← Interface Pygame (compatible web)
│       └── graphi_thema.py             ← Interface Pygame (version initiale)
│
├── config/
│   └── regle.json                      ← Paramètres du plateau
│
├── information_pour_évaluer/           ← Documentation pour l'enseignant
│   ├── guide_evaluation.md             ← Guide rapide d'évaluation
│   ├── travail_de_chaque_membre.md     ← Contributions de chaque membre
│   ├── corrections/                    ← 14 bugs corrigés (FR + JP)
│   │   ├── liste_corrections.md
│   │   └── エラー一覧と修正記録.md
│   └── analyse_technique/              ← Documentation technique (FR + JP)
│       ├── analyse_logique.md
│       ├── architecture_gui.md
│       ├── GUIコアロジック解説.md
│       ├── ia_et_fonctionnalites.md
│       ├── AI・追加機能解説.md
│       └── plan_integration.md
│
├── requirements.txt
└── README.md                           ← Ce fichier
```

---

## Pour l'enseignant

> **Commencez par** `information_pour_évaluer/guide_evaluation.md`  
> Ce fichier donne un parcours d'évaluation rapide avec les liens vers chaque partie du projet.

| Document | Contenu |
|----------|---------|
| `guide_evaluation.md` | Parcours d'évaluation, architecture, fonctionnalités |
| `travail_de_chaque_membre.md` | Rôle et contributions détaillées de chaque élève |
| `corrections/liste_corrections.md` | 14 bugs identifiés et corrigés avec code avant/après |
| `analyse_technique/analyse_logique.md` | Analyse de `damedemain.py` (structure de données, algorithmes) |
| `analyse_technique/architecture_gui.md` | Architecture du GUI, hover, undo, sauvegarde |
| `analyse_technique/ia_et_fonctionnalites.md` | IA Minimax, effets sonores, thèmes |
| `analyse_technique/plan_integration.md` | Stratégie d'intégration logique ↔ GUI |

---

## Fonctionnalités

### Logique du jeu (`damedemain.py`)

- Plateau 8×8 configurable via JSON
- Mouvements diagonaux avec validation des limites
- Captures par saut (pions et dames)
- Dames avec portée illimitée sur les diagonales
- Détection de fin de partie

### Interface graphique (`dame_gui_ctk.py`)

- Menu principal (mode de jeu, thème, chargement)
- Plateau interactif avec hover en temps réel
- **IA à 3 niveaux** : aléatoire, glouton, Minimax + Alpha-Beta
- **Capture en chaîne** (rafle) obligatoire
- **Capture obligatoire** (prise forcée)
- Annulation de coup (Ctrl+Z)
- Système d'indices (Ctrl+H)
- Sauvegarde / chargement de parties (JSON)
- Minuterie (tour + total)
- 4 thèmes visuels
- Historique des coups avec coordonnées
- Journal des appels de fonctions
- Effets sonores
- Export de l'historique en fichier texte

### Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| Ctrl+Z | Annuler le dernier coup |
| Ctrl+N | Nouvelle partie |
| Ctrl+S | Sauvegarder |
| Ctrl+O | Charger une partie |
| Ctrl+E | Exporter l'historique |
| Ctrl+H | Afficher un indice |

---
###### **Indice (easter egg) :** en partie *contre l’IA*, si la fenêtre a le focus clavier, on murmure qu’un **mot synonyme d’« ultime »** — en français comme en anglais, tapé lettre par lettre — pourrait réveiller un adversaire plus tenace. Le journal de partie trahit parfois le secret…
---

## Prérequis

- **Python 3.9+** recommandé (le code du dépôt reste compatible **3.8** en pratique ; **3.8** n’est plus maintenu par python.org — viser **3.10** à **3.13** en classe ou sur votre machine)
- `customtkinter` (pour la version bureau) : `pip install customtkinter`
- `pygame` (pour la version Pygame / web) : `pip install pygame`
