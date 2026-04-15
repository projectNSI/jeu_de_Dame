# IA et fonctionnalités avancées

## 1. Intelligence artificielle (`SimpleAI`)

L'IA joue toujours les Blancs (joueur 2). Trois niveaux de difficulté :

| Niveau | Algorithme | Description |
|--------|-----------|-------------|
| Facile | Aléatoire | Choisit un coup au hasard parmi les coups légaux |
| Moyen | Glouton (greedy) | Évalue chaque coup et choisit celui qui donne le meilleur score immédiat |
| Difficile | Minimax + Alpha-Beta | Explore l'arbre de jeu sur 2 niveaux de profondeur |

### Fonction d'évaluation

```
score = Σ (valeur des pièces alliées) − Σ (valeur des pièces adverses)

valeur = 5.0 pour une dame, 1.0 pour un pion
bonus de position = distance vers la ligne de promotion × 0.15
```

### Minimax avec élagage Alpha-Beta

L'algorithme explore les coups possibles en alternant maximisation (tour de l'IA) et minimisation (tour du joueur). L'élagage Alpha-Beta coupe les branches inutiles :

- **Alpha** : meilleur score garanti pour le maximiseur
- **Beta** : meilleur score garanti pour le minimiseur
- Si `beta ≤ alpha`, la branche est coupée

### Optimisation : copie rapide du plateau

```python
def _copy_board(L):
    return [[[cell[0], cell[1], cell[2]] for cell in col] for col in L]
```

10 à 100× plus rapide que `copy.deepcopy()`. Essentiel car l'IA copie le plateau pour chaque nœud de l'arbre de recherche.

## 2. Effets sonores

Utilisation de `winsound.Beep(fréquence, durée)` dans un thread séparé pour ne pas bloquer l'interface.

| Événement | Fréquences (Hz) | Effet |
|-----------|-----------------|-------|
| Déplacement | 500 → 1000 | Montée d'une octave |
| Capture | 1400 → 350 | Chute de 2 octaves |
| Promotion | 440 → 660 → 880 → 1100 → 1400 | Gamme ascendante |
| Annulation | 900 → 300 | Descente |
| Victoire | Do → Mi → Sol → Do → Mi → Sol (octave+1) | Fanfare en accords |

## 3. Minuterie

Affichage en temps réel du temps écoulé par tour et du temps total de la partie. Mise à jour chaque seconde via `self.after(1000, self._tick_timer)`.

## 4. Thèmes visuels

4 palettes de couleurs pour le plateau, sélectionnables dans le menu principal ou en cours de partie :

- **Classique** : marron / beige
- **Émeraude** : vert foncé / vert clair
- **Océan** : bleu marine / bleu ciel
- **Crépuscule** : violet / rose

## 5. Système d'indices (hint)

Le bouton « 💡 Indice » utilise l'IA en mode glouton pour trouver le meilleur coup et l'affiche en surbrillance dorée pendant 3 secondes.

## 6. Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| Ctrl+Z | Annuler |
| Ctrl+N | Nouvelle partie |
| Ctrl+S | Sauvegarder |
| Ctrl+O | Charger |
| Ctrl+H | Indice |
