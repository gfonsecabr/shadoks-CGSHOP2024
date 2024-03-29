import math
import random


def norm(v):
    return math.sqrt(v[0]*v[0]+v[1]*v[1])

def distance(a,b):
    AB=(b[0]-a[0],b[1]-a[1])
    return norm(AB)


def dotprod(u,v):
    return u[0]*v[0]+u[1]*v[1]

def angle(u,v):
    nu=norm(u)
    nv=norm(v)
    if nu==0 or nv==0:
        return 0
    d=dotprod(u,v)
    q=d/(nu*nv)
    if q<-1:
        return math.pi
    if q>1:
        return 0
    return math.acos(dotprod(u,v)/(norm(u)*norm(v)))
    

def angleTriangle(A,B,C):
    #angle entre les vecteurs AB et CB
    AB=[B[0]-A[0],B[1]-A[1]]
    CB=[B[0]-C[0],B[1]-C[1]]
    return angle(AB,CB)

def orientedAngle(A,B,C):
    AB=(B[0]-A[0], B[1]-A[1])
    BC=(C[0]-B[0], C[1]-B[1])
    if AB[0]*BC[1]-AB[1]*BC[0]>=0:
        return angle(AB,BC)
    else:
        return 2*math.pi-angle(AB,BC)
    
def orientedAnglePrime(A,B,C):
    AB=(B[0]-A[0], B[1]-A[1])
    BC=(C[0]-B[0], C[1]-B[1])
    d=AB[0]*BC[1]-AB[1]*BC[0]
    if d==0:
        if dotprod(AB,BC)>0:
            return math.pi
        else:
            return 0
    elif d>0:
        return math.pi+angle(AB,BC)
    else:
        return math.pi-angle(AB,BC)
    
    
def det(u,v):
    return u[0]*v[1]-u[1]*v[0]  


def area(A,B,C):
    AB=(B[0]-A[0],B[1]-A[1])
    AC=(C[0]-A[0],C[1]-A[1])
    return det(AB,AC)

def areaTriangle(A,B,C):
    AB=(B[0]-A[0],B[1]-A[1])
    BC=(C[0]-B[0],C[1]-B[1])
    return det(AB,BC)

def areaPolygon(vertices):
    n=len(vertices)
    area=0
    for i in range(n):
        j=(i+1)%n
        area=area-(vertices[j][0]-vertices[i][0])*(vertices[j][1]+vertices[i][1])
    return area      

def insegment(A,B,C): #cette fonction retourne 1 si C est dans le segment [AB] et 0 sinon...
    if C[0]==A[0] and C[1]==A[1]:
        return 1
    if C[0]==B[0] and C[1]==B[1]:
        return 1
    if area(A,B,C)!=0:
        #C n'est pas sur le segment [AB]
        return 0
    if angleTriangle(A,C,B)>0.999*math.pi:
        return 1
    return 0

# Variants of intersect are in crossing

def intersect(A,B,C,D):
    if area(A,B,C)*area(A,B,D)>0 or area(C,D,A)*area(C,D,B)>0: #un des deux segments est d'un côté de l'autre
        return 0
    if area(A,B,C)*area(A,B,D)<0 and area(C,D,A)*area(C,D,B)<0: #ce cas n'est pas dégénéré et c'est celui où les segments ne se coupent pas en un sommet
        return 1
    #Il y a un triplet de points alignés...au moins. Si on a une intersection, le point d'intersection est l'un des 4 points A,B,C,D.
    if insegment(A,B,C) or insegment(A,B,D): 
        return 1
    if insegment(C,D,A) or insegment(C,D,B): 
        return 1
    return 0

#We assume that the four points are distinct
# If AB intersects CD in the interior of the segment, it returns 1
# Otherwise, if C is on AB, we test the side of D



def inTriangle(A,B,C,P):
    if area(A,B,C)==0:#triangle dégénéré
        if insegment(A,B,P)==1:
            return 1
        if insegment(A,C,P)==1:
            return 1
        if insegment(B,C,P)==1:
            return 1
        return 0
    #On teste si P et C sont du même côté de (AB) (ont la même orientation)
    if area(A,B,C)*area(A,B,P)<0:
        return 0
    #On teste si P et B sont du même côté de (AC) (ont la même orientation)
    if area(A,C,B)*area(A,C,P)<0:
        return 0
    #On teste si P et A sont du même côté de (BC) (ont la même orientation)
    if area(B,C,A)*area(B,C,P)<0:
        return 0
    return 1    

###################################################################################################
# computes the directional Hull according to the directions

def dHull(directions,polygon):
    #We assume that minX and minY=0
    n=len(directions)
    mini=[min(dotprod(p,v) for p in polygon) for v in directions]
    maxi=[max(dotprod(p,v) for p in polygon) for v in directions]     
    return mini,maxi
    
        
#testDHull()

def inDHull(directions,mini,maxi,point):
    if len(directions) != len(mini):
        print("error in inDHull, use directions and mini of different lengths")
        return 1
    n=len(directions)
    for i in range(n):
        v=dotprod(directions[i],point)
        if v>maxi[i][0] or v<mini[i][0]:
            return 0
    return 1

def inDHullWithPosition(directions,mini,maxi,point,position):
    if len(directions) != len(mini):
        print("error in inDHull, use directions and mini of different lengths")
        return 1
    n=len(directions)
    for i in range(n):
        v=dotprod(directions[i],point)
        w=dotprod(directions[i],position)
        if v+w>maxi[i] or v+w<mini[i]:
            return 0
    return 1

###################################################################################################
# orientation
# if the orientation of the polygon is negative, we reverse it    
    
def orientation(points):
    lowest = min(points, key=lambda p: p[0]+0.00001*p[1])
    b=points.index(lowest)
    a=(b-1)%len(points)
    c=(b+1)%len(points)
    o=area(points[a],points[b],points[c])
    if o<0:
        points.reverse()
        print("reverse the orientation of polygon")
    if o==0:
        print("flat vertex in orientation... strange")
    
    
def testOrientation():
    points=[(0,0),(0,1),(1,1),(1,0)]
    orientation(points)
    print(points)
    
#testOrientation()



#######################################################################################
# test wether the polygon is convex
# We assume that the polygon is oriented positively

def isConvex(polygon):
    n=len(polygon)
    for i in range(n):
        A=polygon[i]
        B=polygon[(i+1)%n]
        C=polygon[(i+2)%n]
        if area(A,B,C)<0 :
            return 0 
    return 1

#######################################################################################
# we remove the vertices with too small edges

def simplify(poly):
    n=len(poly)
    newvertices=[]
    for i in range(n):
        A=poly[(i-1)%n]
        B=poly[i]
        C=poly[(i+1)%n]
        if angleTriangle(A,B,C)<0.9*math.pi:
            newvertices.append(B)
    return newvertices

#######################################################################################
# computes the convex hull with Graham scan algorithm

def convexHull(points):
    #etape 1
    #Pour le point le plus bas, on pourrait utiliser la fonction min, 
    # mais comme on veut le plus bas et à hauteur égale, le plus à droite, on va écrire la fonction
    #print(points)
    south=points[0]
    for p in points:
        if p[1]<south[1]:
            south=p
        elif p[1]==south[1] and p[0]>south[0]:
            south=p
            
    #etape 2
    hull=[(p[0],p[1]) for p in points]
    
    #etape 3
    # on peut se servir de la fonction angle(u,v) qui calcule l'angle non orienté entre deux vecteurs.
    # Attention au cas où l'un des deux vecteurs est nul. Ici, ce cas particulier sera bien traité 
    # et le point south devrait être le premier de la liste...
    I=(1,0)
    hull.sort(key=lambda p:angle(I,(p[0]-south[0],p[1]-south[1])))
    i=2
    pointsonfirstsegment=[hull[1]]
    while angleTriangle(south,hull[1],hull[i])==0 or angleTriangle(south,hull[1],hull[i])==math.pi:
         pointsonfirstsegment.append(hull[i])
         hull.pop(i)
    hull.pop(1)
    firstpoint=max(pointsonfirstsegment, key=lambda p:distance(south,p))
    hull.insert(1,firstpoint)
    #Same thing for the last segment
    if len(hull)>2:
        i=len(hull)-1
        pointsonlastsegment=[hull[i]]
        j=len(hull)-2
        while angleTriangle(south,hull[i],hull[j])==0 or angleTriangle(south,hull[i],hull[j])==math.pi:
            pointsonlastsegment.append(hull[j])
            hull.pop(j)
            j=j-1
            i=i-1
        hull.pop(i)
        lastpoint=max(pointsonlastsegment, key=lambda p:distance(south,p))
        hull.append(lastpoint)

    #etape 4
    j=1
    while j<len(hull):
        # i, j, k sont trois indices qui se suivent  0,1,2, puis 1,2,3, puis ... len-2,len-1,0
        #i l'indice du point avant j 
        i=(j-1)%len(hull)
        #k l'indice du point après j
        k=(j+1)%len(hull)
        if area(hull[i],hull[j],hull[k])<=0:
            #on supprime j 
            hull.pop(j)
            #et on revient d'un pas en arrière pour tester le point j-1
            j=(j-1)%len(hull)
        else:
            j=j+1
    return hull


def diameter(vertices):
    d=0 
    for i in range(len(vertices)-1):
        for j in range(i,len(vertices)):
            dist=distance(vertices[i],vertices[j])
            if dist>d:
                d=dist 
    return d

def centroid(vertices):
    x=0
    y=0
    n=len(vertices)
    for v in vertices:
        x=x+v[0]
        y=y+v[1]
    return (x//n , y//n)

def thickness(vertices):
    d=0 
    ii=0
    jj=0
    for i in range(len(vertices)-1):
        for j in range(i,len(vertices)):
            dist=distance(vertices[i],vertices[j])
            if dist>d:
                d=dist 
                ii=i
                jj=j
    vector=(vertices[jj][0]-vertices[ii][0],vertices[jj][1]-vertices[ii][1])
    n=norm(vector)
    vector=(-vector[1]/n,vector[0]/n)
    minv=min(vertices, key=lambda v:dotprod(vector,v))
    mini=dotprod(minv,vector)
    maxv=max(vertices, key=lambda v:dotprod(vector,v))
    maxi=dotprod(maxv,vector)
    return d/(maxi-mini)

################ normal function used to choose the direction to store... ###########

#optionfill=2

def normaltodiameter(vertices):
    d=0 
    ii=0
    jj=0
    for i in range(len(vertices)-1):
        for j in range(i,len(vertices)):
            dist=distance(vertices[i],vertices[j])
            if dist>d:
                d=dist 
                ii=i
                jj=j
    vector=(-vertices[jj][1]+vertices[ii][1],vertices[jj][0]-vertices[ii][0])
    if random.randint(0,1)==0:
        return (vector[0],vector[1])
    else:
        return (-vector[0],-vector[1])
    
#optionfill=3


def normaltodiameterforfactory(vertices):
    d=0 
    ii=0
    jj=0
    for i in range(len(vertices)-1):
        for j in range(i,len(vertices)):
            dist=distance(vertices[i],vertices[j])
            if dist>d:
                d=dist 
                ii=i
                jj=j
    vector0=(vertices[jj][1]-vertices[ii][1],-vertices[jj][0]+vertices[ii][0])
    n=norm(vector0)
    vector=(vector0[0]/n,vector0[1]/n)
    minv=min(vertices, key=lambda v:dotprod(vector,v))
    mini=dotprod(minv,vector)
    maxv=max(vertices, key=lambda v:dotprod(vector,v))
    maxi=dotprod(maxv,vector)
    
    if d>(maxi-mini)*2.3:
        #print(f"long with ratio {d/(maxi-mini)}")
        if vector0[0]<0:
            return vector[0]
        else:
            return -vector[0]
    #print(f"short with ratio {d/(maxi-mini)}")
    if vector0[0]>0:
        return 2+vector[0]
    else:
        return 2-vector[0]

def normaltodiameterleftright(vertices):
    d=0 
    ii=0
    jj=0
    for i in range(len(vertices)-1):
        for j in range(i,len(vertices)):
            dist=distance(vertices[i],vertices[j])
            if dist>d:
                d=dist 
                ii=i
                jj=j
    vector0=(vertices[jj][1]-vertices[ii][1],-vertices[jj][0]+vertices[ii][0])
    n=norm(vector0)
    vector=(vector0[0]/n,vector0[1]/n)
    minv=min(vertices, key=lambda v:dotprod(vector,v))
    mini=dotprod(minv,vector)
    maxv=max(vertices, key=lambda v:dotprod(vector,v))
    maxi=dotprod(maxv,vector)
    
    if d>(maxi-mini)*2.3:
        #print(f"long with ratio {d/(maxi-mini)}")
        if vector0[0]<0:
            return vector0
        else:
            return (-vector0[0],-vector0[1])
    #print(f"short with ratio {d/(maxi-mini)}")
    if vector0[0]>0:
        return vector0
    else:
        return (-vector0[0],-vector0[1])

#optionfill=4

def normaltodiameterrandom(vertices):
    d=0 
    ii=0
    jj=0
    for i in range(len(vertices)-1):
        for j in range(i,len(vertices)):
            dist=distance(vertices[i],vertices[j])
            if dist>d:
                d=dist 
                ii=i
                jj=j
    vector0=(vertices[jj][0]-vertices[ii][0],vertices[jj][1]-vertices[ii][1])
    n=norm(vector0)
    vector=(-vector0[1]/n,vector0[0]/n)
    minv=min(vertices, key=lambda v:dotprod(vector,v))
    mini=dotprod(minv,vector)
    maxv=max(vertices, key=lambda v:dotprod(vector,v))
    maxi=dotprod(maxv,vector)
    sd=0.2
    if d>(maxi-mini)*2.3:
        #print(f"long with ratio {d/(maxi-mini)}")
        if vector0[0]<0:
            return (-vector0[1],vector0[0])
        else:
            return (vector0[1],-vector0[0])
    
    #print(f"short with ratio {d/(maxi-mini)}")
    if vector0[1]>0:
        return (int(vector0[1]*random.gauss(1, sd)),-int(vector0[0]*random.gauss(1, sd)))
    else:
        return (int(-vector0[1]*random.gauss(1, sd)),int(-vector0[0]*random.gauss(1, sd)))
    

#optionfill=5

def normalmix(vertices):
    d=0 
    ii=0
    jj=0
    for i in range(len(vertices)-1):
        for j in range(i,len(vertices)):
            dist=distance(vertices[i],vertices[j])
            if dist>d:
                d=dist 
                ii=i
                jj=j
    vector0=(vertices[jj][0]-vertices[ii][0],vertices[jj][1]-vertices[ii][1])
    n=norm(vector0)
    vector=(-vector0[1]/n,vector0[0]/n)
    minv=min(vertices, key=lambda v:dotprod(vector,v))
    mini=dotprod(minv,vector)
    maxv=max(vertices, key=lambda v:dotprod(vector,v))
    maxi=dotprod(maxv,vector)
    sd=0.2
    if d>(maxi-mini)*2.3:
        #print(f"long with ratio {d/(maxi-mini)}")
        if vector0[1]>0:
            return (-vector0[1],vector0[0])
        else:
            return (vector0[1],-vector0[0])
    
    longestd=distance(vertices[0],vertices[1])
    ilongest=0
    n=len(vertices)
    for i in range(n):
        ii=(i+1)%n
        d=distance(vertices[i],vertices[ii])
        if d>longestd:
            longestd=d
            ilongest=i
    a=vertices[ilongest][1]-vertices[(ilongest+1)%n][1]
    if a>0:
        return (a,vertices[(ilongest+1)%n][0]-vertices[ilongest][0])
    else:
        return (-a,-vertices[(ilongest+1)%n][0]+vertices[ilongest][0])

#optionfill=6


def normlongestedge(vertices):
    longestd=distance(vertices[0],vertices[1])
    ilongest=0
    n=len(vertices)
    for i in range(n):
        ii=(i+1)%n
        d=distance(vertices[i],vertices[ii])
        if d>longestd:
            longestd=d
            ilongest=i
    a=vertices[(ilongest+1)%n][0]-vertices[ilongest][0]
    b=vertices[(ilongest+1)%n][1]-vertices[ilongest][1]
    n=math.sqrt(a*a+b*b)
    return n

def longestedgesatris(vertices):
    longestd=distance(vertices[0],vertices[1])
    ilongest=0
    n=len(vertices)
    verticalorhoritzontal=True
    for i in range(n):
        ii=(i+1)%n
        d=distance(vertices[i],vertices[ii])
        if d>longestd:
            #wec heck wether it is vertical or horizontal
            u=(vertices[ii][0]-vertices[i][0],vertices[ii][1]-vertices[i][1])
            v=(1,0)
            w=(0,1)
            #print(angle(u,v))
            if angle(u,v)>0.1 and angle(u,w)>0.1 and angle(u,v)<3.04 and angle(u,w)<3.04:
                longestd=d
                ilongest=i
                verticalorhoritzontal=False
    a=vertices[(ilongest+1)%n][0]-vertices[ilongest][0]
    b=vertices[(ilongest+1)%n][1]-vertices[ilongest][1]
    if verticalorhoritzontal==False:
        return angle((a,b),(1,0))
    else:
        return -5
        

def longestedgex(vertices):
    longestd=distance(vertices[0],vertices[1])
    ilongest=0
    n=len(vertices)
    for i in range(n):
        ii=(i+1)%n
        d=distance(vertices[i],vertices[ii])
        if d>longestd:
            longestd=d
            ilongest=i
    a=vertices[(ilongest+1)%n][0]-vertices[ilongest][0]
    b=vertices[(ilongest+1)%n][1]-vertices[ilongest][1]
    n=math.sqrt(a*a+b*b)
    a=a/n
    if b>0:
        return (a,1)
    return (-a,-1)



def normaltolongestedge(vertices):
    longestd=distance(vertices[0],vertices[1])
    ilongest=0
    n=len(vertices)
    for i in range(n):
        ii=(i+1)%n
        d=distance(vertices[i],vertices[ii])
        if d>longestd:
            longestd=d
            ilongest=i
    a=vertices[ilongest][1]-vertices[(ilongest+1)%n][1]
    #we randomly choose whether we send it on one side or the other
    if random.randint(0,1)==0:
        return (a,vertices[(ilongest+1)%n][0]-vertices[ilongest][0])
    else:
        return (-a,-vertices[(ilongest+1)%n][0]+vertices[ilongest][0])
    
#optionfill=7
    
def mix2(vertices):
    d=0 
    ii=0
    jj=0
    for i in range(len(vertices)-1):
        for j in range(i,len(vertices)):
            dist=distance(vertices[i],vertices[j])
            if dist>d:
                d=dist 
                ii=i
                jj=j
    vector0=(vertices[jj][1]-vertices[ii][1],-vertices[jj][0]+vertices[ii][0])
    n=norm(vector0)
    vector=(vector0[0]/n,vector0[1]/n)
    minv=min(vertices, key=lambda v:dotprod(vector,v))
    mini=dotprod(minv,vector)
    maxv=max(vertices, key=lambda v:dotprod(vector,v))
    maxi=dotprod(maxv,vector)
    
    if d>(maxi-mini)*2.3:
        #print(f"long with ratio {d/(maxi-mini)}")
        if vector0[0]<0:
            return vector0
        else:
            return (-vector0[0],-vector0[1])
    angle=random.uniform(-math.pi/2, +math.pi/2)
    vector=(int(100*math.cos(angle)), int(100*math.sin(angle)))
    return vector

#optionfill=8
    
def normalsatris(vertices):
    t=thickness(vertices)
    
    longestd=distance(vertices[0],vertices[1])
    ilongest=0
    n=len(vertices)
    for i in range(n):
        ii=(i+1)%n
        d=distance(vertices[i],vertices[ii])
        if d>longestd:
            longestd=d
            ilongest=i
    a=vertices[ilongest][0]-vertices[(ilongest+1)%n][0]
    b=vertices[ilongest][1]-vertices[(ilongest+1)%n][1]
    
    if t>3:
        if b>0:
            return (-b,a)
        else:
            return (b,-a)
    if b>0:
        return (b,-a)
    return (-b,a)

#optionfill=9 not yet ready
    
def normalatris(vertices):
    t=thickness(vertices)
    #we try to classify the shapes: 
    # long sent to the left
    return (1,0)
    
    

    





