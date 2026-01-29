import json 
def creation_de_jeu(L,c,l,N)->list:
    '''c=nombre de colone,l=nombre de ligne ,N=nombre de ligne de pion
    creation du plateau de jeu'''
    T=input('voulez vous changer les parametres du jeu?oui/non')
    if T=='non':
        return L,c,l,N
    else:
        fc=int(input('nombre de colone,si tu notes rien on changera pas le nombre de colone'))
        if fc!=0 and fc:
            c=fc
        fl=int(input('nombre de ligne,si tu notes rien on changera pas le nombre de ligne'))
        if fl!=0 and fl:
            l=fl
        fn=int(input('nombre de ligne de pion,si tu notes rien on changera pas le nombre de ligne de pion'))
        if fn!=0 and fn:
            N=fn
        if c>N*2:
            L = [ [ [0,0,(1+h%2-g%2)%2] for g in range(l)] for h in range (c)]
            for i in range (c):
                for k in range (l):
                    if i<N:
                #je regarde les cases où des pion peuvent etre poser
                        if L[i][k][2]==1:
                    #je regarde les case noirs
                            L[i][k][0] = 1
                            #je place un pion noir
                            L[i][k][1] = 2
                            #je designe son type comme un pion
                    elif i>c-N:
                        if L[i][k][2]==1:
                            #je regarde les case noirs
                            L[i][k][0] = 2
                            #je place un pion blanc
                            L[i][k][1] = 2
                            #je designe son type comme un pion
        else:
            print('impossible de creer le plateau de jeu avec ces parametres')
    return L,c,l,N
def is_friendly(L:list,c:int,l:int,v:int):
    """test si le pion choisi est bien du joueur"""
    if v == 0:
        if L[c][l][0]==2:
            return True
        else:
            return False
    else:
        if L[c][l][0]==1:
            return True
        else:
            return False
def jeu_possible(L:list,c:int,l:int,diags:list,v:int,t:int)->list:
    """regarde si une mouvement est possible"""
    if L[c][l][1]==1:
        J=[]
        for i in range(len(diags)):
            try:
                if L[c+diags[i][0]][l+diags[i][1]][0] == (2-v) and L[c+2*diags[i][0]][l+2*diags[i][1]][0]==0:
                    J[i]=1
                elif 0 <= c+diags[i][0] < len(L) and 0 <= l+diags[i][1] < len(L[0]):
                    J[i]=0
                elif L[c+diags[i][0]][l+diags[i][1]][0] == 0:
                    J[i]=2
                else:
                    J[i]=0
            except IndexError:
                J[i]=0
    elif L[c][l][1]==2:
        for i in range(len(L)):
            for j in range(len(L[i])):
                try:   
                    if L[i][j][0]==(2-v)and ((c-diags[0][0]*(c-i)==i and l-diags[0][1]*(c-j)==j)or(c-diags[1][0]*(c-i)==i and l-diags[1][1]*(c-j)==j)or (c-diags[2][0]*(c-i)==i and l-diags[2][1]*(c-j)==j)or(c-diags[3][0]*(c-i)==i and l-diags[3][1]*(c-j)==j)) : 
                    #test diagonales:        
                        J[i][j]=1
                    elif L[i][j][0]==0:
                        J[i][j]=2
                    else:
                        J[i][j]=0
                except IndexError:
                    J[i][j]=0
                    
    return J
def team_exist(L:list,v:int)->bool:
    """regarde si une equipe a gagner"""
    for i in range(len(L)):
        for j in range(len(L[i])):
            if L[i][j][0]==v:
                return True
    return False
def tour(L:list,c:int,l:int,v:int):
    """le deroulement d'un tour"""
    M=[[],[],[]]
    q=''
    Y=True
    while Y:
        T=True
        while T:    
            ii=int(input(f'quelle colone?(1 à {c})'))
            h=int(input(f'quelle ligne?(1 à {l})'))
            diags=[[-1,1],[1,1],[-1,-1],[1,-1]]
            if is_friendly(L,ii,h,v)==True:
                T=False
            else:
                print('ce pion n est pas a vous')
        T=True
        J=jeu_possible(L,ii,h,diags,v)
        while T:
            if L[ii][h][1] == 1:
                for i in range(len(J)):
                    if J == [0] * len(diags):
                        print('une attaque est possible sur la',i+1,'eme diagonale')
                    elif J[i] ==2:
                        print('un deplacement est possible sur la',i+1,'eme diagonale')
                    else:
                        print('aucun deplacement n est possible avec ce pion')
                T=False
                d=int(input(print('quelle diagonale?(1 à 4)')))
                if d==1 or d==2:
                    if v==0:    
                        if J[d-1]==1:
                            L[ii+diags[d-1][0]][h+diags[d-1][1]][0]=0
                            L[ii+2*diags[d-1][0]][h+2*diags[d-1][1]][0]=L[ii][h][0]
                            L[ii][h][0]=0
                            Y=False
                        elif J[d-1]==0:
                            L[ii+diags[d-1][0]][h+diags[d-1][1]][0]=L[ii][h][0]
                            L[ii][h][0]=0
                            Y=False
                        else:
                            print('ce deplacement n est pas possible')
                    else:
                        pass
                elif d==3 or d==4:    
                    if v==1:
                        if J[d-1]==1:
                            L[ii+diags[d-1][0]][h+diags[d-1][1]][0]=0
                            L[ii+2*diags[d-1][0]][h+2*diags[d-1][1]][0]=L[ii][h][0]
                            L[ii][h][0]=0
                    
                        elif J[d-1]==2:
                            L[ii+diags[d-1][0]][h+diags[d-1][1]][0]=L[ii][h][0]
                            L[ii][h][0]=0
                    
                        else:
                            print('ce deplacement n est pas possible')
                    else:
                        pass
                else:
                    print('cette diagonale n existe pas')
            elif L[ii][h][1] == 2:
                for i in range (len(J)):
                    for j in range (len(J[i])):
                        if J[i][j]==1:
                            M[0].append(i,j)
                        elif J[i][j]==2:
                            M[1].append(i,j)
                        elif J[i][j]==0:
                            M[2].append(i,j)
                for i in range(len(M[0])):
                    print(M[0])



    v = (v + 1) % 2
    Y=team_exist(L,v)
    if v==0:
        print('c est au tour des noirs')
        q='noirs'
    else:
        print('c est au tour des blancs')
        q='blancs'
    return f'Les {q} ont gagné!' 


def main():
    return None
if __name__ == "__main__":
    assert main() is None
#lecture du fichier règle.json
with open('règle.json', 'r', encoding='utf-8') as f:
    LJ = json.load(f)[0]
    L = LJ['Liste']
    c = LJ['colonne']
    l = LJ['ligne']
    N = LJ['ligne_de_pion']
print(L,c,l,N)
L,c,l,N=creation_de_jeu(L,c,l,N)

J=[L,c,l,N]
v = 0

while team_exist(L, 1) and team_exist(L, 2):
    resultat = tour(L, c, l, v)
    v = (v + 1) % 2


