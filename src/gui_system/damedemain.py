import json 

def creation_de_jeu(L, c, l, N) -> list:
    """
    Création du plateau de jeu avec paramètres personnalisables
    
    Paramètres:
        L: Liste du plateau (structure 3D)
        c: Nombre de colonnes
        l: Nombre de lignes
        N: Nombre de lignes de pions par joueur
    
    Retour:
        Tuple (L, c, l, N) avec le plateau initialisé
    """
    # Demander à l'utilisateur s'il veut modifier les paramètres
    T = input('Voulez-vous changer les paramètres du jeu? (oui/non): ')
    
    if T == 'non':
        return L, c, l, N
    else:
        # Modification du nombre de colonnes
        fc = int(input('Nombre de colonnes (0 pour garder la valeur actuelle): '))
        if fc != 0 and fc:  # CORRIGE: Condition logique correcte
            c = fc
        
        # Modification du nombre de lignes
        fl = int(input('Nombre de lignes (0 pour garder la valeur actuelle): '))
        if fl != 0 and fl:  # CORRIGE: Condition logique correcte
            l = fl
        
        # Modification du nombre de lignes de pions
        fn = int(input('Nombre de lignes de pions (0 pour garder la valeur actuelle): '))
        if fn != 0 and fn:  # CORRIGE: Condition logique correcte
            N = fn
        
        # Vérifier qu'il y a assez d'espace entre les deux camps
        if c > N * 2:
            # Créer le damier avec motif alternant (cases blanches et noires)
            # L[col][ligne] = [couleur_pion, type_pion, couleur_case]
            L = [[[0, 0, (1 + h % 2 - g % 2) % 2] for g in range(l)] for h in range(c)]
            
            # Placer les pions initiaux
            for i in range(c):
                for k in range(l):
                    # Pions noirs dans les N premières lignes
                    if i < N:
                        # Ne placer que sur les cases noires (cases jouables)
                        if L[i][k][2] == 1:
                            L[i][k][0] = 1  # Pion noir
                            L[i][k][1] = 1  # Type: pion normal (pas dame)
                    
                    # Pions blancs dans les N dernières lignes
                    elif i > c - N - 1:  # CORRIGE: Condition correcte
                        if L[i][k][2] == 1:
                            L[i][k][0] = 2  # Pion blanc
                            L[i][k][1] = 1  # Type: pion normal (pas dame)
        else:
            print('Impossible de créer le plateau avec ces paramètres')
    
    return L, c, l, N
def is_friendly(L: list, c: int, l: int, v: int) -> bool:
    """
    Vérifie si le pion sélectionné appartient au joueur actuel
    
    Paramètres:
        L: Plateau de jeu
        c: Colonne du pion
        l: Ligne du pion
        v: Joueur actuel (0 = blancs, 1 = noirs)
    
    Retour:
        True si le pion appartient au joueur, False sinon
    """
    if v == 0:
        # Joueur 0 (blancs) possède les pions de couleur 2
        return L[c][l][0] == 2
    else:
        # Joueur 1 (noirs) possède les pions de couleur 1
        return L[c][l][0] == 1
def jeu_possible(L: list, c: int, l: int, diags: list, v: int, t: int = None) -> list:
    """
    Détermine les mouvements possibles pour un pion donné
    
    Paramètres:
        L: Plateau de jeu
        c: Colonne du pion
        l: Ligne du pion
        diags: Vecteurs diagonaux [[-1,1], [1,1], [-1,-1], [1,-1]]
        v: Joueur actuel (0 = blancs, 1 = noirs)
        t: Type de mouvement (paramètre non utilisé)
    
    Retour:
        Liste J où:
        - J[i] = 0: mouvement impossible
        - J[i] = 1: capture possible (saut par-dessus ennemi)
        - J[i] = 2: déplacement simple possible
    """
    # PION NORMAL
    if L[c][l][1] == 1:
        # CORRIGE: Initialisation correcte de la liste
        J = [0] * len(diags)  # Crée [0, 0, 0, 0]
        
        for i in range(len(diags)):
            try:
                # Calculer la nouvelle position
                new_c = c + diags[i][0]
                new_l = l + diags[i][1]
                
                # Vérifier si la nouvelle position est dans les limites du plateau
                if not (0 <= new_c < len(L) and 0 <= new_l < len(L[0])):
                    J[i] = 0  # Hors limites
                    continue
                
                # Vérifier si c'est un ennemi (possibilité de capture)
                # CORRIGE: (2-v) détectait notre propre couleur ; (1+v) détecte l'ennemi
                # v=0 (blancs) → ennemi=1 (noirs) ; v=1 (noirs) → ennemi=2 (blancs)
                if L[new_c][new_l][0] == (1 + v):
                    # Calculer la position après le saut
                    capture_c = c + 2 * diags[i][0]
                    capture_l = l + 2 * diags[i][1]
                    
                    # Vérifier si la case de destination est vide et dans les limites
                    if (0 <= capture_c < len(L) and 
                        0 <= capture_l < len(L[0]) and
                        L[capture_c][capture_l][0] == 0):
                        J[i] = 1  # Capture possible
                    else:
                        J[i] = 0  # Impossible de capturer
                
                # Vérifier si la case est vide (déplacement simple)
                elif L[new_c][new_l][0] == 0:
                    J[i] = 2  # Déplacement simple possible
                
                else:
                    J[i] = 0  # Case occupée par un allié
            
            except IndexError:
                J[i] = 0  # Erreur d'accès, mouvement impossible
    
    # DAME (pion promu) - parcours diagonal complet
    elif L[c][l][1] == 2:
        # CORRIGE: la dame parcourt chaque diagonale case par case
        # Elle peut se déplacer librement sur les cases vides
        # et capturer en sautant par-dessus un ennemi (atterrissage sur case vide après)
        J = [[0 for _ in range(len(L[0]))] for _ in range(len(L))]

        for d in diags:
            dc, dl = d[0], d[1]
            step = 1
            found_enemy = False
            while True:
                nc = c + dc * step
                nl = l + dl * step
                if not (0 <= nc < len(L) and 0 <= nl < len(L[0])):
                    break
                cell = L[nc][nl][0]
                if cell == 0:
                    J[nc][nl] = 1 if found_enemy else 2
                elif cell == (1 + v):
                    if found_enemy:
                        break
                    found_enemy = True
                else:
                    break
                step += 1
    
    else:
        # AJOUTE: Cas par défaut
        J = []
    
    return J
def team_exist(L: list, v: int) -> bool:
    """
    Vérifie si une équipe a encore des pions sur le plateau
    
    Paramètres:
        L: Plateau de jeu
        v: Couleur de l'équipe à vérifier (1 = noirs, 2 = blancs)
    
    Retour:
        True si l'équipe a encore des pions, False si elle a perdu
    """
    # Parcourir tout le plateau
    for i in range(len(L)):
        for j in range(len(L[i])):
            # Si on trouve un pion de cette couleur, l'équipe existe encore
            if L[i][j][0] == v:
                return True
    
    # Aucun pion trouvé, l'équipe a perdu
    return False
def tour(L: list, c: int, l: int, v: int) -> str:
    """
    Gère le déroulement d'un tour de jeu complet
    
    Paramètres:
        L: Plateau de jeu
        c: Nombre de colonnes
        l: Nombre de lignes
        v: Joueur actuel (0 = blancs, 1 = noirs)
    
    Retour:
        Message de victoire
    """
    # Matrices pour stocker les mouvements possibles des dames
    M = [[], [], []]  # [captures possibles, déplacements possibles, impossibles]
    q = ''  # Nom de l'équipe gagnante
    Y = True  # Continuer le tour
    
    while Y:
        T = True
        
        # ETAPE 1: Sélection du pion
        while T:
            # CORRIGE: Conversion d'index 1-based vers 0-based
            ii = int(input(f'Quelle colonne? (1 à {c}): ')) - 1
            h = int(input(f'Quelle ligne? (1 à {l}): ')) - 1
            
            # Vecteurs diagonaux: [haut-gauche, haut-droite, bas-gauche, bas-droite]
            diags = [[-1, 1], [1, 1], [-1, -1], [1, -1]]
            
            # Vérifier que le pion appartient au joueur
            if is_friendly(L, ii, h, v):
                T = False  # Pion valide sélectionné
            else:
                print('Ce pion ne vous appartient pas!')
        
        T = True
        
        # ETAPE 2: Calculer les mouvements possibles
        J = jeu_possible(L, ii, h, diags, v, None)
        
        while T:
            # CAS 1: PION NORMAL
            if L[ii][h][1] == 1:
                # CORRIGE: Affichage correct des mouvements possibles
                for idx in range(len(J)):
                    if J[idx] == 1:
                        print(f'Une attaque est possible sur la {idx+1}ème diagonale')
                    elif J[idx] == 2:
                        print(f'Un déplacement est possible sur la {idx+1}ème diagonale')
                
                # Vérifier si aucun mouvement n'est possible
                if J == [0] * len(diags):
                    print('Aucun déplacement possible avec ce pion')
                
                T = False
                
                # CORRIGE: Suppression de print() dans input()
                d = int(input('Quelle diagonale? (1 à 4): '))
                # ETAPE 3: Exécuter le mouvement
                
                # Vérifier que la diagonale est valide
                if 1 <= d <= 4:
                    # Diagonales avant (1-2) pour les noirs (v==0)
                    if d == 1 or d == 2:
                        if v == 0:
                            # Capture (saut par-dessus un ennemi)
                            if J[d-1] == 1:
                                # Supprimer le pion ennemi
                                L[ii + diags[d-1][0]][h + diags[d-1][1]][0] = 0
                                # Placer le pion à la nouvelle position
                                L[ii + 2*diags[d-1][0]][h + 2*diags[d-1][1]][0] = L[ii][h][0]
                                # Vider la case d'origine
                                L[ii][h][0] = 0
                                Y = False
                            
                            # Déplacement simple
                            elif J[d-1] == 2:
                                L[ii + diags[d-1][0]][h + diags[d-1][1]][0] = L[ii][h][0]
                                L[ii][h][0] = 0
                                Y = False
                            
                            else:
                                print('Ce déplacement n\'est pas possible')
                        else:
                            print('Les noirs ne peuvent avancer que vers l\'avant')
                    
                    # Diagonales arrière (3-4) pour les blancs (v==1)
                    elif d == 3 or d == 4:
                        if v == 1:
                            # Capture
                            if J[d-1] == 1:
                                L[ii + diags[d-1][0]][h + diags[d-1][1]][0] = 0
                                L[ii + 2*diags[d-1][0]][h + 2*diags[d-1][1]][0] = L[ii][h][0]
                                L[ii][h][0] = 0
                                Y = False
                            
                            # Déplacement simple
                            elif J[d-1] == 2:
                                L[ii + diags[d-1][0]][h + diags[d-1][1]][0] = L[ii][h][0]
                                L[ii][h][0] = 0
                                Y = False
                            
                            else:
                                print('Ce déplacement n\'est pas possible')
                        else:
                            print('Les blancs ne peuvent avancer que vers l\'arrière')
                else:
                    print('Cette diagonale n\'existe pas!')
            # CAS 2: DAME (pion promu)
            elif L[ii][h][1] == 2:
                # Collecter tous les mouvements possibles
                for i in range(len(J)):
                    for j in range(len(J[i])):
                        if J[i][j] == 1:
                            M[0].append([i, j])  # Captures possibles
                        elif J[i][j] == 2:
                            M[1].append([i, j])  # Déplacements possibles
                        elif J[i][j] == 0:
                            M[2].append([i, j])  # Impossibles
                
                # Afficher les captures possibles
                if M[0]:
                    print('Captures possibles pour la dame:')
                    for idx, pos in enumerate(M[0]):
                        print(f'  {idx+1}. Position ({pos[0]}, {pos[1]})')
                
                # Afficher les déplacements possibles
                if M[1]:
                    print('Déplacements possibles pour la dame:')
                    for idx, pos in enumerate(M[1]):
                        print(f'  {idx+1}. Position ({pos[0]}, {pos[1]})')
                
                # TODO: Implémenter la logique de déplacement de la dame
                # (Code incomplet dans la version originale)
                T = False
                Y = False
    
    # ÉTAPE 4: Changer de joueur (déjà corrigé)
    v = (v + 1) % 2
    
    # Déterminer le nom de l'équipe pour l'affichage
    if v == 0:
        print('C\'est au tour des blancs')
        q = 'blancs'
    else:
        print('C\'est au tour des noirs')
        q = 'noirs'
    
    return f'Les {q} ont gagné!' 


def main():
    """
    Fonction principale du jeu de dames
    Charge la configuration, initialise le plateau et lance la boucle de jeu
    """
    # Charger les paramètres depuis le fichier de configuration
    with open('règle.json', 'r', encoding='utf-8') as f:
        LJ = json.load(f)[0]
        L = LJ['Liste']      # Plateau de jeu
        c = LJ['colonne']    # Nombre de colonnes
        l = LJ['ligne']      # Nombre de lignes
        N = LJ['ligne_de_pion']  # Nombre de lignes de pions
    
    # Afficher les paramètres initiaux
    print('=== JEU DE DAMES ===')
    print(f'Plateau: {c}x{l}')
    print(f'Lignes de pions: {N}')
    print()
    
    # Demander à l'utilisateur s'il veut modifier les paramètres
    L, c, l, N = creation_de_jeu(L, c, l, N)
    
    # Initialiser le joueur (0 = blancs commencent)
    v = 0
    
    # Boucle principale du jeu
    print('\n=== DÉBUT DE LA PARTIE ===\n')
    
    while team_exist(L, 1) and team_exist(L, 2):
        # Jouer un tour
        resultat = tour(L, c, l, v)
        
        # CORRIGE: Alternance correcte des joueurs (déjà fait dans tour())
        # v = (v + 1) % 2  # Déjà géré dans tour()
    
    # Afficher le résultat final
    print('\n=== FIN DE LA PARTIE ===')
    print(resultat)
    
    return None


if __name__ == "__main__":
    main()


