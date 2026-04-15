# Architecture du GUI — `dame_gui_ctk.py`

## 1. Architecture générale

```
DameGUI (CTk)
│
├── _show_menu()        → Menu principal
│   ├── Sélection du mode (2J / IA)
│   ├── Sélection du thème
│   ├── Commencer / Charger / Quitter
│   └── _menu_start() → _start_game()
│
└── _build_ui()         → Interface de jeu
    ├── Gauche : plateau + boutons
    └── Droite : historique + log
```

## 2. Structure de données

```python
L[col][ligne] = [couleur_pion, type_pion, couleur_case]
# couleur_pion : 0=vide, 1=noir, 2=blanc
# type_pion    : 0=vide, 1=pion, 2=dame
# couleur_case : 0=blanche, 1=noire
```

| GUI `current_player` | `damedemain` `v` | Couleur |
|---------------------|------------------|---------|
| 1 (premier) | 1 | Noir |
| 2 (second) | 0 | Blanc |

## 3. Système de hover

Le système de surbrillance permet au joueur de voir les mouvements possibles en survolant ses pièces.

**Flux d'événements :**

1. `<Enter>` sur un bouton → `_on_enter()` → calcule les mouvements → `_apply_hover()`
2. `<Leave>` du cadre → `_schedule_clear()` (60 ms de délai)
3. Si `<Enter>` sur un autre bouton avant 60 ms → `_cancel_clear()` (pas de clignotement)

**Optimisation :** `_apply_hover()` ne met à jour que les cellules dont la couleur a changé, pas les 64 cases.

## 4. Exécution des mouvements

`_execute_move()` est la méthode centrale, utilisée par le clic humain et l'IA :

1. Sauvegarde de l'état (pour undo)
2. Log des appels (`is_friendly`, `jeu_possible`)
3. `do_move()` déplace la pièce et retire la pièce capturée
4. Vérification de promotion (colonne adverse atteinte)
5. Vérification de capture en chaîne (rafle)
6. Si chaîne → `_chain_piece` est défini, le joueur doit continuer
7. Sinon → effet sonore + passage au tour suivant

## 5. Capture en chaîne (rafle)

Après une capture, si la même pièce peut capturer à nouveau :
- `_chain_piece` enregistre la position de la pièce
- Seules les captures sont affichées (pas de déplacement simple)
- Le hover sur d'autres pièces est bloqué
- Pour l'IA, `_ai_chain_step()` continue automatiquement avec un délai

## 6. Capture obligatoire

```python
if _any_capture_available(L, v, self.c, self.l):
    moves = [m for m in moves if m[2]]  # Seules les captures
```

Si un pion quelconque peut capturer, les déplacements simples sont interdits pour tous les pions.

## 7. Système d'annulation (undo)

Chaque mouvement sauvegarde : `(plateau, joueur, numéro de coup, score, dernier coup, texte historique)`.

L'annulation restaure l'état complet. Les chaînes de captures sont annulées en un seul undo (la sauvegarde n'a lieu qu'au début de la chaîne).

## 8. Sauvegarde/Chargement

Format JSON avec : plateau, joueur, score, dimensions, texte de l'historique. Le chargement est disponible depuis le menu principal et depuis le jeu (Ctrl+O).
