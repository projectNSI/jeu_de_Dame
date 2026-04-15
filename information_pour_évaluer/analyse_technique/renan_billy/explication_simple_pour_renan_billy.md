# Explication du flux du code du jeu — Version simple
## Document d'explication pour Renan et Billy

---

## À propos de ce document

Ce document explique **comment le code du jeu fonctionne**, en **utilisant le moins de jargon technique possible**.

---

## Vue d'ensemble : Le flux du jeu

```
【Début du jeu】
    ↓
【Affichage】Dessine le plateau à l'écran
    ↓
【Interaction utilisateur】Souris se déplace, clique
    ↓
【Réaction】L'ordinateur détecte le mouvement et traite
    ↓
【Mise à jour】Le plateau change
    ↓
【Affichage】Écran se met à jour
    ↓
【IA】L'ordinateur joue
    ↓
【Affichage】Écran se met à jour
    ↓
... Boucle répétée ...
```

C'est simple. À chaque fois, on répète « réaction → traitement → affichage ».

---

## Partie 1 : Structure de l'écran (Qu'est-ce qu'on voit)

### Le plateau est fait de boutons

Le plateau de jeu de dames (8×8) est en réalité composé de **64 petits boutons**.

```
┌─────────────────────────────────┐
│  □  ■  □  ■  □  ■  □  ■  │  ← Boutons
│  ■  □  ■  □  ■  □  ■  □  │
│  □  ■  □  ■  □  ■  □  ■  │
│  ■  □  ■  □  ■  □  ■  □  │
│  □  ■  □  ■  □  ■  □  ■  │
│  ■  □  ■  □  ■  □  ■  □  │
│  □  ■  □  ■  □  ■  □  ■  │
│  ■  □  ■  □  ■  □  ■  □  │
└─────────────────────────────────┘
```

Chaque bouton :
- **Noir** = Ne peut pas se déplacer (apparence)
- **Blanc** = Peut se déplacer (apparence)
- Cliquer sur un bouton → Quelque chose se passe dans le jeu
- La souris entre sur un bouton → L'ordinateur « remarque » la présence

---

## Partie 2 : Réaction aux mouvements de souris (Fonction hover)

### Ce que fait l'utilisateur

```
1. Déplace la souris au-dessus d'une pièce
2. Le jeu affiche « vous pouvez vous déplacer d'ici » avec destinations en vert
3. Bouge la souris vers la destination
4. Les zones vertes restent visibles
5. Clique → Le coup s'exécute
```

### Comment le code réagit

Le comportement réel en termes de Tkinter (système de fenêtres) :

```
【Utilisateur : Souris entre sur Button A】
  ↓ Tkinter le détecte
Un événement « Enter event » se déclenche
  ↓
【Programme : Calcule où on peut se déplacer de ce bouton】
  ↓
【Affichage : Colore les destinations en vert】
  ↓
【Utilisateur : Bouge la souris de Button A vers Button B】
  ↓
L'événement « Leave event » se déclenche (quitte A)
L'événement « Enter event » se déclenche (entre B)
  ↓
【Ici c'est important】L'ordre des événements se mélange — Bug!
```

### Bug #1 : Qu'est-ce qui se passe

```
Prévu :   Leave(A) → Enter(B)
Réel :    Leave(A) → Leave(cadre parent【C'EST LE PROBLÈME!】) → Enter(B)

Le 【cadre parent】est comme l'« arrière-plan ».
Il réagit aussi et « efface les couleurs vertes » immédiatement!

Résultat :
L'utilisateur voit « le vert disparaît soudain »
```

### Comment on l'a corrigé

```
【L'idée de correction】
« Si on doit effacer le vert, attendre un peu »
C'est-à-dire : attendre 0.06 secondes avant d'effacer.
Si, entretemps, « on entre sur un nouveau bouton »,
on dit « Annule, pas besoin d'effacer »

【En code】
_schedule_clear() → Réserver « effacement après 0.06s »
_cancel_clear() → Annuler cette réservation
```

---

## Partie 3 : Les couleurs restent (Bug #2)

### Ce que fait l'utilisateur

```
1. Clique sur une pièce
2. Le coup s'exécute
3. Mais la destination est « encore verte »
4. Quelques secondes plus tard, revient à la bonne couleur
```

### Pourquoi ça arrive

```
【Avant le mouvement】
- self.hover_piece = (2, 3)           ← Pièce sélectionnée
- self.hover_moves = [(3,4), (4,5)]   ← Destinations

【On exécute le déplacement】
- (2,3) se déplace vers (3,4)

【Mise à jour l'écran : Peindre les nouvelles couleurs】
- De quelle couleur faire (2,3)?
  → On se demande : self.hover_piece == (2,3)?
  → OUI! On la repeint en vert!
  
- De quelle couleur faire (3,4)?
  → On se demande : (3,4) est dans self.hover_moves?
  → OUI! On la repeint en vert!
```

### Comment on l'a corrigé

```
【Correction : Faire oublier avant de bouger】
_apply_hover(None, [])
  ↓
self.hover_piece = None       ← « Il n'y a pas de pièce »
self.hover_moves = []         ← « Il n'y a pas de destinations »

【Ensuite on peint les couleurs】
- De quelle couleur faire (2,3)?
  → Pas de pièce en hover? NON! On peint la bonne couleur!
```

---

## Partie 4 : La promotion au mauvais endroit (Bug #3)

### Les règles de promotion au jeu de dames (version simple)

```
【Règles du jeu de dames international】
Une pièce se promeut quand elle atteint le bord adverse

Visuellement:

■ ■ ■ ■ ■ ■ ■ ●
Côté noir         Côté blanc

La pièce blanche qui atteint le côté noir (gauche) → se promeut
La pièce noire qui atteint le côté blanc (droite) → se promeut
```

### Bug : On testait haut/bas au lieu de gauche/droite

```
【Mauvais code】
if pièce est « tout en haut » or pièce est « tout en bas »:
    la promeut

【Du point de vue utilisateur】
On teste seulement la direction verticale (haut/bas)!
Mais on devrait tester horizontalement (gauche/droite) — le côté adverse!
```

### Comment on l'a corrigé

```
【Bon code】
if (pièce blanche) and (atteint le côté blanc):
    la promeut
elif (pièce noire) and (atteint le côté noir):
    la promeut
```

---

## Partie 5 : L'écran devient saccadé (Bug #4)

### Ce que fait l'utilisateur

```
1. Commence à jouer
2. Après 10~15 mouvements
3. La souris répond lentement (saccadé)
4. L'écran gèle momentanément
```

### Pourquoi ça arrive

```
【À chaque mouvement de souris】
L'ordinateur fait :

« Vérifier les 64 cases et repeindre toutes leurs couleurs »

Case 1 : De quelle couleur? → Vérifier → Peindre
Case 2 : De quelle couleur? → Vérifier → Peindre
Case 3 : De quelle couleur? → Vérifier → Peindre
...
Case 64 : De quelle couleur? → Vérifier → Peindre

Ça arrive « à chaque mouvement de souris »!

15 mouvements = 64 × 15 = 960 vérifications!
```

### Comment on l'a corrigé

```
【Correction : Repeindre seulement ce qui change】

【Avant】
La destination est seulement (3,4)
Mais on vérifie « les 64 cases »

【Après】
Seules les cases qui changent:
- (2,3) ← Vient de quitter (était verte)
- (3,4) ← Vient d'arriver
- Autres cases qui changent

C'est-à-dire : seulement 3~6 cases

Résultat : 64 cases → 6 cases = Environ 10 fois plus rapide!
```

---

## Partie 6 : Pas de son (Bug #5)

### Ce que fait l'utilisateur

```
1. Clique pour bouger une pièce → Silence
2. Capture une pièce adverse → Silence
3. Gagne la partie → Silence
```

### Quel est le problème

```
【Bruits nécessaires pour le jeu】
- Bouger normalement → « Bip » (son bas)
- Capturer une pièce → « Boom! » (son d'impact)
- Se promouvoir → « Fanfare! » (son victorieux)

【En réalité】
Tout est muet!
```

### Comment on l'a corrigé

```
【Correction : Ajouter les sons】
Utiliser système « winsound » de Windows
Spécifier la fréquence pour créer les sons

・Mouvement normal: 500Hz → 1000Hz (simple)
・Capture: 1400Hz → 350Hz (chute rapide)
・Promotion: 440Hz → 880Hz → Plus haut (montée)
・Victoire: Fanfare... (célébration musicale)
```

---

## Partie 7 : Les captures vers l'arrière impossible (Bug #6)

### Règles du jeu de dames (version simple)

```
【Pièce ordinaire】
- Direction avant: Seulement vers l'avant (direction de progression)
- Direction de capture: Toutes les directions (avant ET arrière)

【Dame (pièce promue)】
- Direction avant: Toutes les directions
- Direction de capture: Toutes les directions
```

### Bug : Les captures vers l'arrière ne marchaient pas

```
【Mauvais code】
if une pièce adverse existe:
    if« c'est vers l'avant»:       ← Vérification
        on peut capturer!
        
if« c'est vers l'arrière»:
    if« direction avant»:           ← Encore vérification « avant »!
        on peut capturer!
   else:
        on ne peut pas capturer!    ← BUG!
```

### Comment on l'a corrigé

```
【Bon code】
if「une pièce adverse existe」:
    on peut capturer! (peu importe la direction)
    
if「on veut se déplacer」:
    if「direction avant」:
        on peut se déplacer!
    else:
        on ne peut pas!

【Autrement dit】
« Capturer une pièce » et « se déplacer » = Règles différentes!
```

---

## Résumé : Ce qu'on a appris

| Bug # | Qu'est-ce qui s'est passé | Comment on l'a réparé |
|---|---|---|
| #1 (Renan) | Le vert disparaît | Attendre 0.06s avant d'effacer |
| #2 (Renan) | Les couleurs restent | Oublier avant de bouger |
| #3 (Renan) | Promotion au mauvais endroit | Tester gauche/droite, pas haut/bas |
| #4 (Billy) | L'écran saccade | Repeindre seulement ce qui change |
| #5 (Billy) | Pas de son | Ajouter le système de sons |
| #6 (Billy) | Captures arrière impossibles | Enlever le filtre pour les captures |

---

## Un peu plus difficile

### L'idée de « gestion d'état »

Un programme « gère l'état » :

```
【État du plateau】
self.L = [
  [noir, noir, blanc, noir, ...],
  [noir, noir, blanc, noir, ...],
  ...
]

【État du hover】
self.hover_piece = (2, 3)      ← Pièce sélectionnée maintenant
self.hover_moves = [(3,4), ...]  ← Liste de destinations

【Affichage à l'écran】
for chaque case in plateau:
    if cette case == hover_piece:
        couleur = vert
    elif cette case in hover_moves:
        couleur = vert
    else:
        couleur = normal
```

Un bug arrivent quand « l'état » et « l'affichage » se désynchronisent.

```
【Quand il y a un bug】
self.hover_piece = (2, 3)  ← State ancien
mais l'écran affiche
(3, 4) déjà nouvelle     ← Affichage nouveau

L'état et l'affichage ne coincident pas!

【Comment réparer】
Mettre à jour l'état:
self.hover_piece = None    ← « Il n'y a rien »
Mettre à jour l'état:
self.hover_moves = []      ← « Il n'y a rien »

Puis mettre l'écran à jour → État et affichage coincident!
```

---

## Pour finir

**Les principes fondamentaux de la programmation :**

1. **Gestion d'état** : Garder l'état actuel exact et à jour
2. **Traitement d'événements** : Quand quelque chose se passe, réagir
3. **Mise à jour d'affichage** : Afficher selon l'état
4. **Performance** : Éviter les travaux inutiles

Ces 6 bugs existaient parce qu'on n'a pas respecté ces principes.

---

*Ce document explique le code avec un minimum de jargon technique.*
