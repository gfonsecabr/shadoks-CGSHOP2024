from load import *
            
def binary_search(chain,vsearch):
            # Binary search to find the rightmost left index of the target.
            left, right = 0, len(chain.vertices) - 1
            while left <= right:
                mid = left + (right - left) // 2
                if chain.vertices[mid]>= vsearch:
                    right = mid - 1
                else:
                    left = mid + 1

            if right<0:
                    right=0
            if right>len(chain.vertices)-2:
                    right=len(chain.vertices)-2
            return right



################ Variants for intersection of (directed from A to B and C to D) segments ###############

# If the points are in general position, this function returns the standard result
# Otherwise, we test whether the left sides of the segments cross.
# It is used for testing wether the interiors of two polygons cross
# We assume that the vertices are distinct and oriented according  to the positive direction

def intersect2(A,B,C,D):
    if A==C or A==D or B==C or B==D:
        return -1
    if area(A,B,C)*area(A,B,D)>0 or area(C,D,A)*area(C,D,B)>0: #un des deux segments est d'un côté de l'autre
        return 0
    if area(A,B,C)*area(A,B,D)<0 and area(C,D,A)*area(C,D,B)<0: #ce cas n'est pas dégénéré et c'est celui où les segments ne se coupent pas en un sommet
        #print(f"a intersect2 return 1 for {A,B,C,D}")    
        return 1
    #4 points alignés
    if area(A,B,C)==0 and area(A,B,D)==0:
        AB=(B[0]-A[0],B[1]-A[1])
        CD=(D[0]-C[0],D[1]-C[1])
        if dotprod(AB,CD)<0:
            return 0
        if insegment(A, B, C):
            return 1 
        if insegment(A, B, D):
            return 1 
        if insegment(C, D, A):
            return 1 
        if insegment(C, D, B):
            return 1 
        return 0
    #3 points alignés
    if area(A,B,C)==0:
        if insegment(A, B, C):
            if area(A,B,D)>0:
                return 1 
        return 0
    if area(A,B,D)==0:
        if insegment(A, B, D):
            if area(A,B,C)>0:
                return 1 
        return 0
    if area(C,D,A)==0:
        if insegment(C,D,A):
            if area(C,D,B)>0:
                return 1 
        return 0
    if area(C,D,B)==0:
        if insegment(C,D,B):
            if area(C,D,A)>0:
                return 1 
        return 0
    return 0


################ CrossingChains ##################

#For testing whether the interiors of two polygons cross...
# We return the result and the list of common vertices that have to be checked with the polygons

def crossingChains2(chain1,position1,chain2,position2):
    if (chain1.xmin[0]+position1[0],chain1.xmin[1]+position1[1])>(chain2.xmax[0]+position2[0],chain2.xmax[1]+position2[1]):
        return 0,None
    if (chain2.xmin[0]+position2[0],chain2.xmin[1]+position2[1])>(chain1.xmax[0]+position1[0],chain1.xmax[1]+position1[1]):
        return 0,None
    if chain1.ymin+position1[1]>chain2.ymax+position2[1]:
        return 0,None
    if chain2.ymin+position2[1]>chain1.ymax+position1[1]:
        return 0,None
    
    #print("crossing chains with")
    #print(chain1)
    #print(chain2)
    if (chain1.xmin[0]+position1[0],chain1.xmin[1]+position1[1])<=(chain2.xmin[0]+position2[0],chain2.xmin[1]+position2[1]):
        i1=binary_search(chain1,(chain2.xmin[0]+position2[0]-position1[0],chain2.xmin[1]+position2[1]-position1[1]))
        i2=0
    else:
        i2=binary_search(chain2,(chain1.xmin[0]+(position1[0]-position2[0]) , chain1.xmin[1]+(position1[1]-position2[1])))
        i1=0
    n1=len(chain1.vertices)
    n2=len(chain2.vertices)
    commonVertices=[]
    while i1<n1-1 and i2<n2-1:
        if chain1.direction=="right":
            A=(chain1.vertices[i1][0]+position1[0],chain1.vertices[i1][1]+position1[1])
            B=(chain1.vertices[i1+1][0]+position1[0],chain1.vertices[i1+1][1]+position1[1])
        else:
            B=(chain1.vertices[i1][0]+position1[0],chain1.vertices[i1][1]+position1[1])
            A=(chain1.vertices[i1+1][0]+position1[0],chain1.vertices[i1+1][1]+position1[1])
        if chain2.direction=="right":
            C=(chain2.vertices[i2][0]+position2[0],chain2.vertices[i2][1]+position2[1])
            D=(chain2.vertices[i2+1][0]+position2[0],chain2.vertices[i2+1][1]+position2[1])
        else:
            D=(chain2.vertices[i2][0]+position2[0],chain2.vertices[i2][1]+position2[1])
            C=(chain2.vertices[i2+1][0]+position2[0],chain2.vertices[i2+1][1]+position2[1])

        result=intersect2(A,B,C,D)
        if result==1:
            return 1,None
        #If result!=1, we continue...
        #but if result=-1, namely two vertices are in common and that should be checked with the whole polygons
        if result==-1:
            if A==C or A==D:
                if A not in commonVertices:
                    commonVertices.append(A)
            elif B==C or B==D:
                if B not in commonVertices:
                    commonVertices.append(B)
        if (chain1.vertices[i1+1][0]+position1[0],(chain1.vertices[i1+1][1]+position1[1]))<(chain2.vertices[i2+1][0]+position2[0],(chain2.vertices[i2+1][1]+position2[1])):
            i1=i1+1
        else:
            i2=i2+1
    return 0,commonVertices

        
################# point and polygon in polygon #################

# specially designed for pip in a region: for points in a convex region where the normals of the edges of the convex direction are in the directions

def pipregion(region,directions,point):
    for i in range(len(directions)):
        h=dotprod(point, directions[i])
        if h<region.min[i] or h>region.max[i]:
            return 0 
    return 1
        
# point in polygon : the boundary points are considered outside the polygon 

def pip2(polygon,point):
    #print("start pip2chain")
    num_intersections = 0
    
    for chain in polygon.chains:
        #print(f"point={point}")
        #print(chain)
        #print(f"{num_intersections} intersection with chains")
        if point>=chain.xmin and point<=chain.xmax: 
            i=binary_search(chain,point)
            #print(f"index={i}")
            if insegment(chain.vertices[i],chain.vertices[i+1],point):
                return 0 #on the boundary of the polygon
            if chain.vertices[i]<=point and point<=chain.vertices[i+1]:
                if area(chain.vertices[i],chain.vertices[i+1],point)>0:
                    num_intersections=num_intersections+1
    return 1 if num_intersections % 2 == 1 else 0


def pip3(polygon,point):
    #print("start pip2chain")
    num_intersections = 0
    for chain in polygon.chains:
        if point>=chain.xmin and point<=chain.xmax: 

            i=binary_search(chain,point)
            if insegment(chain.vertices[i],chain.vertices[i+1],point):
                return 1 #on the boundary of the polygon
            if chain.vertices[i]<=point and point<=chain.vertices[i+1]:
                if area(chain.vertices[i],chain.vertices[i+1],point)>0:
                    num_intersections=num_intersections+1
    return 1 if num_intersections % 2 == 1 else 0


################################## Crossing Polygons #########################################

def ai(u):
    nu=norm(u)
    if u[1]>=0:
        return math.acos(u[0]/nu)
    else:
        return -math.acos(u[0]/nu)
    
# This function returns 1 if the interior of the angles done by u1,u2,v1,v2 cross.


def wellOrdered2(u1,u2,v1,v2):
    if det(u1,v1)==0 and dotprod(u1,v1)==0:
        return 0
    if det(u2,v2)==0 and dotprod(u2,v2)==0:
        return 0
    u2=ai(u2)-ai(u1)
    if u2<0:
        u2=u2+2*math.pi
    v1=ai(v1)-ai(u1)
    if v1<0:
        v1=v1+2*math.pi
    v2=ai(v2)-ai(u1)
    if v2<0:
        v2=v2+2*math.pi  
    if v2<v1 and v1<=u2 and v2<=u2:
        #print("well ordered")
        return 1
    return 0


def crossingPolygons(polygon1,polygon2,position1,position2,directions):
    #First phase: check the directional hulls
    min1=polygon1.min
    min2=polygon2.min
    max1=polygon1.max 
    max2=polygon2.max        
    n=len(directions)
    n=min(8,len(directions))
    for i in range(n):
        h1=dotprod(position1,directions[i])
        h2=dotprod(position2,directions[i])
        if max1[i]+h1<=min2[i]+h2 or max2[i]+h2<=min1[i]+h1:
            return 0
    
    #Second phase: pip
    x1=polygon1.vertices[0][0]+position1[0]
    x2=polygon2.vertices[0][0]+position2[0]
    resultPip2polygon1=0
    resultPip2polygon2=0
    if x1<x2:
        A2=(polygon2.vertices[0][0]+position2[0]-position1[0],polygon2.vertices[0][1]+position2[1]-position1[1]) 
        resultPip2polygon1=pip2(polygon1,A2)
        if resultPip2polygon1==1:
            return 1
    if x2<x1:
        A1=(polygon1.vertices[0][0]+position1[0]-position2[0],polygon1.vertices[0][1]+position1[1]-position2[1])
        resultPip2polygon2=pip2(polygon2,A1)
        if resultPip2polygon2==1:
            return 1
    
    #Third phase
    #We use crossingChains2... and store the common vertices in common
    common=[]
    for chain1 in polygon1.chains:
        for chain2 in polygon2.chains:
            u,commonVertices=crossingChains2(chain1, position1, chain2, position2)
            if u==1:
                return 1
            if commonVertices!=None:
                for x in commonVertices:
                    if x not in common:
                        common.append(x)
    #Fourth phase
    #We check the common vertices of the two polygons.
    n1=len(polygon1.vertices)
    n2=len(polygon2.vertices)
    if common==None:
        return 0
    for commonVertex in common:
        vertexPolygon1=(commonVertex[0]-position1[0],commonVertex[1]-position1[1])
        i=polygon1.vertices.index(vertexPolygon1)  
        vertexPolygon2=(commonVertex[0]-position2[0],commonVertex[1]-position2[1])
        j=polygon2.vertices.index(vertexPolygon2) 
        A=(polygon1.vertices[(i-1)%n1][0],polygon1.vertices[(i-1)%n1][1])
        C=(polygon1.vertices[(i+1)%n1][0],polygon1.vertices[(i+1)%n1][1])
        u1=(A[0]-vertexPolygon1[0],A[1]-vertexPolygon1[1])
        u2=(C[0]-vertexPolygon1[0],C[1]-vertexPolygon1[1])
        D=(polygon2.vertices[(j-1)%n2][0],polygon2.vertices[(j-1)%n2][1])
        F=(polygon2.vertices[(j+1)%n2][0],polygon2.vertices[(j+1)%n2][1])
        v1=(D[0]-vertexPolygon2[0],D[1]-vertexPolygon2[1])
        v2=(F[0]-vertexPolygon2[0],F[1]-vertexPolygon2[1])
        if wellOrdered2(u1,u2,v1,v2)==0:
            return 1 
        #return 1
    #print("final result is 0")
    return 0

################################# polygon in convex region ######################################

# function to test whether a polygon at a given position is in the region (container)

def inConvexRegion(inPolygon,position,region,directions):
    #print(region)
    n=len(directions)
    mini=inPolygon.min
    maxi=inPolygon.max
    miniRegion=region.min
    maxiRegion=region.max
    for i in range(n):
        u=dotprod(position,directions[i])
        #print(f"u={u}")
        if mini[i]+u<miniRegion[i] or maxi[i]+u>maxiRegion[i]:
            return 0
    return 1

############################### check crossings in solutions #####################################

def checkcrossings(region,polygons,directions):
    print("start checkcrossings")
    i=0
    for i in range(len(polygons)):
        polygon1=polygons[i]
        if polygon1.positions!=None:
            for position1 in polygon1.positions:
                for j in range(len(polygons)):
                    polygon2=polygons[j]
                    if polygon2.positions!=None:
                        for position2 in polygon2.positions:
                            if polygon1!=polygon2 or position1!=position2:
                                result=crossingPolygons(polygon1,polygon2,position1,position2,directions)
                                if result==1: 
                                    print("checkcrossings detects two crossing polygons")
                                    print(f"indices are {i} and {j}")
                                    print(f"quantities are {polygon1.quantity} and {polygon2.quantity}")
                                    print(f"idetities are {polygon1.id} and {polygon2.id}")
                                    print(f"positions are {position1} and {position2}")
                                    return 0                                    
                    j=j+1
        i=i+1
    print("check OK")
    return 1


def correctcrossings(region,polygons,directions):
    i=0
    cross=False
    for i in range(len(polygons)):
        polygon1=polygons[i]
        if polygon1.positions!=None:
            for position1 in polygon1.positions:
                for j in range(len(polygons)):
                    polygon2=polygons[j]
                    if polygon2.positions!=None:
                        for position2 in polygon2.positions:
                            if polygon1!=polygon2 or position1!=position2:
                                result=crossingPolygons(polygon1,polygon2,position1,position2,directions)
                                if result==1: 
                                    cross=True
                                    print("correctcrossings detects two crossing polygons")
                                    print(f"indices are {i} and {j}")
                                    print(f"costs are {polygon1.cost} and {polygon2.cost}")
                                    print(f"identities are {polygon1.id} and {polygon2.id}")
                                    print(f"positions are {position1} and {position2}")
                                    if polygon1.cost>polygon2.cost:
                                        polygon2.positions.remove(position2)
                                        print(f"removes position from polygon2")
                                    else:
                                        polygon1.positions.remove(position1)
                                        print(f"removes position from polygon1")
                                    cost0,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons)
                                    print(f"new cost after correction is {cost0} and the new result is {result}")
                                                         
                    j=j+1
        i=i+1
    if cross==True:
        return correctcrossings(region,polygons,directions)
    return 1


def checksolution(instancefilename,solutionfilename):
    t0,translations=loadtranslations(instancefilename)
    region,polygons,directions=load(instancefilename)
    #reads solution
    print(f"loads solution {solutionfilename}")
    f = open(fullname)
    data = json.load(f)
    ipolygons= data.get('item_indices')
    x = data.get('x_translations')
    y = data.get('y_translations')
    f.close()
    #test integer value  
    for i in range(len(ipolygons)):
        ipolygon=ipolygons[i]
        xpolygon=x[i]+translations[ipolygon][1][0]
        ypolygon=y[i]+translations[ipolygon][1][1]
        if isinstance(xpolygon, int)==False or isinstance(ypolygon, int)==False:
            print(xpolygon)
            print(ypolygon)
            print("non integer positions")
            return 0
        p=(xpolygon,ypolygon)
        if polygons[ipolygon].positions==None:
            polygons[ipolygon].positions=[p]
        else:
            polygons[ipolygon].positions.append(p)
    #then we check the crossings
    print("checks crossings")
    return checkcrossings(polygons,directions)



