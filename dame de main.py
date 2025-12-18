def creation_de_jeu(L,c,l,N)->list:
    '''c=nombre de colone,l=nombre de ligne ,N=nombre de ligne de pion
    creation du plateau de jeu'''
    T=input('voulez vous changer les parametres du jeu?oui/non')
    if T=='non':
        return L,c,l,N
    else:
        fc=int(input('nombre de colone,si tu notes rien on changera pas le nombre de colone'))
        if fc!=0 or fc!=None:
            c=fc
        fl=int(input('nombre de ligne,si tu notes rien on changera pas le nombre de ligne'))
        if fl!=0 or fl!=None:
            l=fl
        fn=int(input('nombre de ligne de pion,si tu notes rien on changera pas le nombre de ligne de pion'))
        if fn!=0 or fn!=None:
            N=fn
        if c>N*2:
            L = [ [ [0,0,(1+h%2-g%2)%2] for g in range(l)] for h in range (c)]
            for i in range (c):
                for k in range (l):
                    if i<=N:
                #je regarde les cases où des pion peuvent etre poser
                        if L[i][k][2]==1:
                    #je regarde les case noirs
                            L[i][k][0] = 1
                    elif i>=c-N:
                        if L[i][k][2]==1:
                            L[i][k][0] = 2
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
    if t==1:
        for i in range(len(diags)):
            try:
                if L[c+diags[i][0]][l+diags[i][1]][0] == (2-v) and L[c+2*diags[i][0]][l+2*diags[i][1]][0]==0:
                    J[i]=1
                elif L[c+diags[i][0]][l+diags[i][1]][0] == 0:
                    J[i]=2
                else:
                    J[i]=0
            except IndexError:
                J[i]=0
    elif t==2:
        for i in range(len(L)):
            for j in range(len(L[i])):
                if L[i][j][0]==(2-v)and ((c-diags[0][0]*(c-i)==i and l-diags[0][1]*(c-j)==j)or(c-diags[1][0]*(c-i)==i and l-diags[1][1]*(c-j)==j)or (c-diags[2][0]*(c-i)==i and l-diags[2][1]*(c-j)==j)or(c-diags[3][0]*(c-i)==i and l-diags[3][1]*(c-j)==j))  #test diagonales:
                    J[i]=1
                elif L[i][j][0]==0:
                    J[i]=2
                else:
                    J[i]=0
                 except IndexError:
                J[i]=0
                    
    return J
def tour(L:list,c:int,l:int,v:int):
    """le deroulement d'un tour"""
    Y=True
    while Y:
        T=True
        while T:    
            i=int(input(print('quelle colone?'+'(1 à',c,')')))
            h=int(input(print('quelle ligne?'+'(1 à',l,')')))
            diags=[[-1,1],[1,1],[-1,-1],[1,-1]]
            if is_friendly(L,i,h,v)==True:
                T=False
            else:
                print('ce pion n est pas a vous')
        T=True
        while T:
            J=jeu_possible(L,i,h,diags,v,t)
            for i in range(len(J)):
                if J[i] ==1:
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
                    L[i+diags[d-1][0]][h+diags[d-1][1]][0]=0
                    L[i+2*diags[d-1][0]][h+2*diags[d-1][1]][0]=L[i][h][0]
                    L[i][h][0]=0
                    Y=False
                elif J[d-1]==0:
                    L[i+diags[d-1][0]][h+diags[d-1][1]][0]=L[i][h][0]
                    L[i][h][0]=0
                    Y=False
                else:
                    print('ce deplacement n est pas possible')
            else:
                pass
        elif d==3 or d==4:    
            if v==1:
                if J[d-1]==1:
                    L[i+diags[d-1][0]][h+diags[d-1][1]][0]=0
                    L[i+2*diags[d-1][0]][h+2*diags[d-1][1]][0]=L[i][h][0]
                    L[i][h][0]=0
                    Y=False
                elif J[d-1]==2:
                    L[i+diags[d-1][0]][h+diags[d-1][1]][0]=L[i][h][0]
                    L[i][h][0]=0
                    Y=False
                else:
                    print('ce deplacement n est pas possible')
            else:
                pass
        else:
            print('cette diagonale n existe pas')
    return i,h


def main():
    return None
if __name__ == "__main__":
    assert main() is None

J=[[],8,8,3]
L=J[0]
c=J[1]
l=J[2]
N=J[3]
L,c,l,N = creation_de_jeu(L,c,l,N)
print(L)
J=[L,c,l,N]
t,i=tour(L,c,l,0)
print(t)
print(i)


