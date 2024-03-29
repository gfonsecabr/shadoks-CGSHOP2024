from svg import *


directions=[(1,0),(0,1),(1,1),(1,-1),(2,1),(-1,2),(1,2),(-2,1)]

##############################################################################
############################## Chains ########################################
##############################################################################

# chains are polygonal lines with vertices having growing x coordinates (exactly x+0.000001 y is growing)

class chain:
    def __init__(self,vertices,position):
        #print(f"the length of the chain is {len(vertices)}")
        #if vertices[0][0]+verysmall*vertices[0][1]<vertices[1][0]+verysmall*vertices[1][1]:
        #    right=True
        #else:
        #    right=False
        #n=len(vertices)
        #for i in range(n-1):
        #    if right==True:
        #        if vertices[0][0]+verysmall*vertices[0][1]>=vertices[1][0]+verysmall*vertices[1][1]:
        #            print("problem with a right chain")
        #    else:
        #        if vertices[0][0]+verysmall*vertices[0][1]<=vertices[1][0]+verysmall*vertices[1][1]:
        #            print("problem with a left chain")
        
        
        if position!=None:
            self.position=position
        else:
            self.position=None
        self.xmin=min(v for v in vertices)
        self.xmax=max(v for v in vertices)
        self.ymin=min(v[1] for v in vertices)
        self.ymax=max(v[1] for v in vertices)
        if vertices[0]>vertices[1]:
            self.direction="left"
            vertices.reverse()
            self.vertices = vertices
        else:
            self.direction="right"
            self.vertices = vertices
        
            
    def __str__(self):      
        if self.position==None:
            w="\nChain\nNo position"
        else:
            w=f"Chain\nPosition={self.position}"
        w=w+f"\ndirection={self.direction}"
        w=w+f"\nchain vertices = {self.vertices}"
        w=w+f"\nxmin = {self.xmin}"
        w=w+f"\nxmax = {self.xmax}"
        w=w+f"\nymin = {self.ymin}"
        w=w+f"\nymax = {self.ymax}"
        return w
        
    
########################## decomposition of a polygon in chains #############################
    
def computeChains(vertices):
    n=len(vertices)
    mini=min(vertices)
    #print(mini)
    if vertices[0]!=mini:
        print("In computeChains, the first vertex is not the leftmost")
        print(a)
    chains=[]
    n=len(vertices)
    newchain=[vertices[0],vertices[1]]
    right=True
    i=1
    while i<n:
        if right==True:
            if vertices[(i+1)%n]>vertices[i]:
                newchain.append(vertices[(i+1)%n])
            else:
                c=chain(newchain,None)
                chains.append(c)
                #we build a new chain
                newchain=[vertices[i],vertices[(i+1)%n]]
                right=False
        else:
            if vertices[(i+1)%n]<vertices[i]:
                newchain.append(vertices[(i+1)%n])
            else:
                c=chain(newchain,None)
                chains.append(c)
                #we build a new chain
                newchain=[vertices[i],vertices[(i+1)%n]]
                right=True                
        i=i+1
    c=chain(newchain,None)
    chains.append(c)
    return chains


##############################################################################
############################## Polygons ######################################
##############################################################################

    
def fixRegion(points):
    n=len(points)
    mini=min(points)
    indexmin=points.index(mini)
    min_x = mini[0]
    min_y = min(points, key=lambda p: p[1])[1]
    #print(f"in region translation {min_x,min_y}")
    translated_points = [(0,0) for i in range(len(points))]
    i=0
    for p in points:
        newpoint=(p[0] - min_x, p[1] - min_y)
        translated_points[(i-indexmin)%n]=newpoint
        i=i+1
    return translated_points

def fix(points):
    n=len(points)
    mini=min(points)
    indexmin=points.index(mini)
    x0=mini[0]
    y0=mini[1]
    translated_points = [(0,0) for i in range(len(points))]
    i=0
    #print(f"translation {x0,y0}")
    for p in points:
        newpoint=(p[0] - x0, p[1] - y0)
        translated_points[(i-indexmin)%n]=newpoint
        i=i+1
    return translated_points

def findtranslations(points):
    n=len(points)
    mini=min(points)
    indexmin=points.index(mini)
    x0=mini[0]
    y0=mini[1]
    return x0,y0

#############################################################################

def regionDirections(region):
    hull=convexHull(region)
    n=len(hull)
    direct=[]
    for i in range(n):
        x=int(hull[(i+1)%n][0]-hull[i][0])
        y=int(hull[(i+1)%n][1]-hull[i][1])
        w=math.gcd(x,y)
        x=x/w
        y=y/w
        #direct.append((x,y))
        direct.append((-y,x))
    return direct

class polygon:
    def __init__(self,isRegion,index,p,quantity,cost,directions):
        orientation(p)
        if isRegion:
            f=fixRegion(p)
        else:
            f=fix(p)
        self.id=index
        self.vertices = f
        self.chains= computeChains(f)
        if isRegion:
            u=regionDirections(f)
            for d in u:
                dd=(-d[0],-d[1])
                if d not in directions and dd not in directions:
                    directions.append(d)
            for c in self.chains:
                c.position=(0,0)
        self.min,self.max = dHull(directions,f) 
        #ff = [i for i in range(len(f))]
        #ff.sort(key=lambda i:p[i][0]+verysmall*p[i][1])
        #self.xIndices = ff   
        c=centroid(f)
        self.centroid=(int(c[0]),int(c[1]))
        #print(f"when we build the polygon, the centroid is {centroid}")
        self.cost=cost
        self.quantity=quantity
        self.area=areaPolygon(f)
        self.convexarea=areaPolygon(convexHull(f))
        self.positions=None #positions is a list of points in the case where the quantity is >1
        self.inslates=[]
        self.weight=1
            
    def __str__(self): 
        w=f"polygon vertices = {self.vertices}"
        i=0
        for c in self.chains:
            #w=w+f"\nchain[{i}]:{c}"
            i=i+1
        w=w+f"\nmin = {self.min}"
        w=w+f"\nmax = {self.max}"
        #w=w+f"\nx ordered vertices = {self.xIndices}"
        w=w+f"\ncost = {self.cost}"
        w=w+f"\nquantity = {self.quantity}"
        w=w+f"\narea = {self.area}"
        w=w+f"\nweight = {self.weight}"
        w=w+f"\ncentroid={self.centroid}"
        if self.positions==None:
            w=w+"\nposition = Not packed"
        else: 
            w=w+f"\n{len(self.positions)} packed"
            w=w+f"\npositions = {self.positions}"
        return w
        
    def pack(self,p):
        if self.positions==None:
            self.positions=[p]
        else:
            if self.quantity>len(self.positions):
                self.positions.append(p)
            else:
                print("\ncannot pack the polygon since no more left")
              


def packingstatistics(polygons):
    cost=0 
    count=0
    totalquantities=0
    totalcost=0
    areacovered=0
    for polygon in polygons:
        totalquantities=totalquantities+polygon.quantity
        totalcost=totalcost+polygon.quantity*polygon.cost
        if polygon.positions!=None:
            cost=cost+polygon.cost*len(polygon.positions)
            count=count+len(polygon.positions)
            areacovered=areacovered+polygon.area*len(polygon.positions)
    return cost,count,totalcost,totalquantities,areacovered


##############################################################################
################################# Slates #####################################
##############################################################################

class slate:
    def __init__(self,polygons,i,identity):
        polygon=polygons[i]
        polygon.inslates.append(identity)
        self.identity=identity
        self.quantity=polygon.quantity
        self.cost=polygon.cost
        self.left=polygon.quantity #the remaining quantity of this slate
        self.positions=None
        self.area=polygons[i].area
        #and the same characteritics than a brick
        
        #self.jpositions=[] #Contains the list (for each position of the slate) of the pairs (polygonindex,position index in the positions of the polygon), [] because not yet packed
        self.ipolygons=[i]
        
        self.x=[-polygon.centroid[0]] #x coordinate of tne relative position for each polygon of the brick (this is usually fixed before the packing)
        self.y=[-polygon.centroid[1]] #x coordinate of tne relative position for each polygon of the brick (this is usually fixed before the packing)
        self.weight=1
        
    def __str__(self):
        w=f"\nslate:  positions={self.positions}"
        w=w+f"\n    pairs={self.ipolygons}"
        w=w+f"\n    left={self.left}"
        return w
    
    
# a function to translate the slate (not yet packed, otherwise take care of the positions of the polygons) 
# so that the centroid (of the centroids of each polygon weighted by its area) could be close to (0,0)

def makeacopy(polygons,sla,identity):
    newslate=slate(polygons,sla.ipolygons[0],identity)
    newslate.quantity=sla.quantity
    newslate.cost=sla.cost
    newslate.left=sla.left
    newslate.area=sla.area
    if sla.positions!=None:
        #newslate.positions=sla.positions.copy()
        newslate.positions=None
    else:
        newslate.positions=[]
    newslate.ipolygons=sla.ipolygons.copy()
    newslate.x=sla.x.copy()
    newslate.y=sla.y.copy()
    return newslate
    

def slacentroid(sla,polygons):
    center=[0,0]
    totalarea=0
    for i in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[i]
        x=sla.x[i]
        y=sla.y[i]
        center[0]=center[0]+(polygons[ipolygon].centroid[0]+x)*polygons[ipolygon].area
        center[1]=center[1]+(polygons[ipolygon].centroid[1]+y)*polygons[ipolygon].area
        totalarea=totalarea+polygons[ipolygon].area
    center[0]=int(center[0]/totalarea)
    center[1]=int(center[1]/totalarea)
    return center

def centerslate(sla,polygons):
    #compute the centroid
    center=slacentroid(sla,polygons)
    #print(f"before centering, the centroid of the slate is {center}")
    #now we recenter all the polygons of the slate
    for i in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[i]
        sla.x[i]=sla.x[i]-center[0]
        sla.y[i]=sla.y[i]-center[1]
    center=slacentroid(sla,polygons)
    #print(f"after centering, the centroid of the slate is {center}")
    



#we add a polygon in a slate which is not yet packed
    
def addpolygoninslate(sla,polygons,ipolygon,position):
    #print(f"add polygon {ipolygon} in slate")
    newpolygon=polygons[ipolygon]
    #we count how many times the new polygon is in the slate:
    count=0 
    for i in sla.ipolygons:
        if i==ipolygon:
            cout=count+1
    if newpolygon.positions==None:
        q=newpolygon.quantity//(count+1)
    else:
        q=newpolygon.quantity//(count+1)-len(newpolygon.positions)
    if q<sla.left:
        sla.left=q
    c=sla.cost
    sla.cost=sla.cost+polygons[ipolygon].cost
    #print(f"adds slates costs: {c} + {polygons[ipolygon].cost} = {sla.cost}")
    sla.area=sla.area+polygons[ipolygon].area
    sla.ipolygons.append(ipolygon)
    sla.x.append(position[0])
    sla.y.append(position[1])
    #we translate the set to have the centroid of its centroids at (0,0)
    centerslate(sla,polygons)
    
    
#to coordinate the inslate tab if the slates are reordered...

def fillinslates(polygons,slates):
    for p in polygons:
        p.inslates=[]
    for i in range(len(slates)):
        for ipolygon in slates[i].ipolygons:
            polygons[ipolygon].inslates.append(i)
        



##############################################################################
############################## Cage ########################################
##############################################################################

# The cage is a decomposition of the region in rectangular cells aned we store in each cell the polygons whose
# box crosses the cell

class cage:
    def __init__(self,nx,ny,stepx,stepy):
        self.nx=nx
        self.ny=ny 
        self.stepx=stepx
        self.stepy=stepy
        self.cells=[[   [] for j in range(ny)] for i in range(nx)] 
        
    def __str__(self):
        w=f"cage size is = {self.nx},{self.ny}"
        for i in range(len(self.cells)):
            for j in range(len(self.cells[i])):
                w=w+f"\n cell[{i}][{j}] is {self.cells[i][j]}"
        return w
    
def testCage():
    c=cage(5,3)
    c.cells[1][2].append(5)
    print(c)
    
#testCage()



