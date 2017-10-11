########################################################
# matrix.py                                
# ------                             
#                                            
# Nicolas Méloni - meloni@univ-tln.fr        
# 26 Janvier 2015                              
########################################################

########################################################
#
# Programme d'inversion de matrices en Python
#
########################################################

def CreateUnity(n):
    "Returns the <n>x<n> unity matrix"
    I = [[0.0 for i in range(n)] for j in range(n)]
    for i in range(n):
        I[i][i] = 1.0
    return I

def RowMultiply(M,r,a):
    "Multiplies row <r> of matrix <M> by <a>"
    M[r] = [ a*e for e in M[r]]

def RowSwap(M, i, j):
    "Swaps Row <i> and <j> of matrix <M>"
    if i!=j:
        M[i],M[j] = M[j],M[i]

def AddMult(M, i, j, a):
    "adds a*M[j] to M[i]"
    M[i] = [ M[i][c] + a*M[j][c] for c in range(len(M[i]) )] 

def FindNonZero(M, c ):
    "returns the first row <r> >=c such that M[r][c] != 0, None otherwise" 
    for r in range(c,len(M)):
        if M[r][c] != 0:
            return r
    return None

def MatrixInverse(M):
    "returns the inverse of M!"
    n = len(M)
    I = CreateUnity(n)
    A = [ M[r]+I[r] for r in range(n) ]

    for c in range(n):
        r = FindNonZero(A,c)
        if r == None:
            return None
        RowSwap(A, c , r)
        RowMultiply(A, c, 1/A[c][c])
        for r in range(c+1, n):
            AddMult( A, r, c, -A[r][c] ) 
            
    for c in range(n-1,-1,-1):
        for r in range(c-1, -1, -1):
            AddMult( A, r, c, -A[r][c] )
            
    Inv = [ A[r][n:] for r in range(n) ]
   
    return Inv

