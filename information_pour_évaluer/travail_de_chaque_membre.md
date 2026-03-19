# Contribution de chaque membre de l'équipe

---

## Bartosz — Développement du cœur logique du jeu

Bartosz a pris en charge le développement du fichier principal `damedemain.py`, qui contient toute la logique fondamentale du jeu de dames. Son travail comprend :

- **Conception de la structure de données du plateau** : il a conçu la représentation tridimensionnelle `L[colonne][ligne] = [couleur_pion, type_pion, couleur_case]`, permettant de stocker à la fois l'état des pièces et la couleur des cases dans une seule structure. Cette approche facilite le calcul des mouvements et la vérification des règles.

- **Implémentation de la fonction `creation_de_jeu()`** : cette fonction initialise le plateau en plaçant automatiquement les pions sur les cases noires, en respectant le nombre configurable de lignes de pions (`N`). Elle prend en charge les paramètres personnalisables via le fichier `regle.json`.

- **Développement de `jeu_possible()`** : c'est la fonction centrale du jeu. Elle calcule, pour un pion donné, toutes les directions de déplacement possibles (simples et captures) en utilisant les vecteurs diagonaux. Bartosz a implémenté la logique pour les pions normaux (4 directions avec distinction avant/arrière) ainsi que pour les dames (parcours diagonal complet avec détection d'ennemis).

- **Implémentation de `is_friendly()` et `team_exist()`** : ces fonctions vérifient respectivement si un pion appartient au joueur actuel et si une équipe possède encore des pions sur le plateau. Elles sont utilisées à chaque tour pour valider les actions et détecter la fin de partie.

- **Gestion du déroulement d'un tour (`tour()`)** : cette fonction orchestre la sélection d'un pion, l'affichage des mouvements possibles, et l'exécution du déplacement ou de la capture choisi par le joueur.

- **Lecture de la configuration JSON** : intégration du chargement des paramètres depuis `regle.json` pour rendre le jeu configurable (taille du plateau, nombre de lignes de pions).

---

## Fumimaro — Conception du système GUI, validation logique et gestion GitHub

Fumimaro a joué un rôle transversal en assurant la liaison entre la logique métier et l'interface utilisateur, tout en gérant l'infrastructure du projet. Son travail comprend :

- **Conception et développement du système GUI CustomTkinter** (`dame_gui_ctk.py`) : il a conçu l'architecture complète de l'interface graphique, incluant le menu principal avec sélection du mode de jeu et du thème, le plateau interactif avec système de hover et de clic, le panneau d'historique des coups avec coordonnées (A1-H8), le journal des appels de fonctions en temps réel, et l'intégration de l'IA à trois niveaux de difficulté (algorithme Minimax avec élagage Alpha-Beta).

- **Validation et correction du fichier logique** (`damedemain.py`) : Fumimaro a effectué une revue approfondie du code logique de Bartosz. Il a identifié et corrigé plusieurs bugs critiques, notamment la formule de détection d'ennemis `(2-v)` → `(1+v)`, la logique de déplacement des dames qui ne parcourait pas correctement les diagonales, et les problèmes d'initialisation des listes. Au total, 14 corrections ont été documentées dans `docs/corrections.md`.

- **Implémentation des fonctionnalités avancées** : système d'annulation (undo) avec pile d'états, capture en chaîne obligatoire (rafle), sauvegarde/chargement de parties en JSON, minuterie de jeu, système de thèmes visuels, export de l'historique, raccourcis clavier, système d'indices (hint), et effets sonores différenciés.

- **Gestion du dépôt GitHub** : configuration du repository, gestion des branches, organisation de la structure du projet (`src/`, `docs/`, `config/`, `information_pour_évaluer/`), et rédaction de la documentation technique.

---

## Renan — Tests fonctionnels et détection de bugs GUI

Renan a contribué au projet en se concentrant sur les tests manuels de l'interface graphique et la détection de problèmes d'expérience utilisateur. Son travail comprend :

- **Détection du bug de disparition du hover** : en testant le jeu, Renan a remarqué que lorsqu'on déplaçait le curseur d'une pièce vers une case de destination, la surbrillance verte disparaissait instantanément, rendant impossible la sélection de la case. Ce bug était causé par l'événement `<Leave>` du cadre parent qui se déclenchait avant l'événement `<Enter>` du bouton enfant. Son signalement a conduit à l'implémentation du système de « scheduled clear » avec temporisation de 60 ms.

- **Détection du bug de persistance des couleurs après déplacement** : Renan a observé qu'après avoir déplacé une pièce, les cases précédemment surlignées en vert restaient colorées au lieu de revenir à leur couleur d'origine. Ce problème a été corrigé en ajoutant un appel explicite à `_apply_hover(None, [])` avant l'exécution du mouvement.

- **Tests de la promotion en dame** : il a testé la fonctionnalité de promotion et a signalé que les pièces devenaient des dames en touchant le bord haut ou bas du plateau, alors que dans les règles du jeu de dames, la promotion ne devrait se produire qu'en atteignant le côté opposé de l'adversaire. Ce signalement a permis de corriger la logique de promotion de « basée sur les lignes » à « basée sur les colonnes ».

- **Tests du compteur de points** : participation à la mise en place et à la vérification du système de comptage des captures, en s'assurant que le score s'incrémentait correctement pour chaque prise.

---

## Billy — Tests utilisateur et retours sur l'ergonomie

Billy a contribué au projet par des tests approfondis du point de vue utilisateur, en jouant des parties complètes et en identifiant des problèmes d'ergonomie. Son travail comprend :

- **Détection du problème de performance (lag du GUI)** : en jouant plusieurs parties d'affilée, Billy a constaté que l'interface devenait de plus en plus lente au fur et à mesure des mouvements de souris. Ce retour a permis d'identifier que chaque événement `<Enter>` déclenchait un recalcul complet et un redessin des 64 cases. La correction a consisté à implémenter un système de mise à jour différentielle (`_apply_hover`) qui ne modifie que les cellules changées.

- **Signalement de l'absence de feedback sonore** : Billy a fait remarquer que le jeu manquait de retour sensoriel lors des déplacements. L'utilisateur ne savait pas si son action avait été prise en compte. Suite à cette observation, un système de sons électroniques a été implémenté avec des tonalités différentes pour les déplacements, captures, promotions et la victoire.

- **Tests de la capture pour les pions normaux** : en essayant de capturer des pièces adverses, Billy a remarqué que certaines captures étaient impossibles malgré la présence d'un ennemi adjacent avec une case vide derrière. Ce signalement a conduit à la découverte du bug critique de la formule `(2-v)` dans `jeu_possible()`.

- **Tests du compteur de points** : Billy a participé à la vérification du compteur de points en jouant des parties complètes et en comparant le nombre de pièces capturées avec le score affiché, confirmant le bon fonctionnement du système.
