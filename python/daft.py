from crossing import *
import time
import random
import heapq
import sys
import os


############################# Plan #####################################

# 0  list manipulation
# 1  cage functions (build, insertion, remove, merge)
# 2  drop
# 3  push and move 
# 4  fill
# 5  dig
# 6  packing 
# 7  experiments (optimization of a solution or run from scratch)
# 8  check solution file


########################## 0 list manipulation ########################

# With the cage, we work with lists of pairs of indices

def myorder(pair1,pair2):
    if pair1[0]<pair2[0]:
        return 1
    if pair1[0]==pair2[0] and pair1[1]<pair2[1]:
        return 1 
    return 0

# search for a pair in the ordered list of pairs

def binarypair(myorderedlist, pair):
    left, right = 0, len(myorderedlist) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if myorderedlist[mid] == pair:
            return mid
        elif myorder(myorderedlist[mid], pair):
            left = mid + 1
        else:
            right = mid - 1
    return -1


def insertpair(myorderedlist, pair):
    left, right = 0, len(myorderedlist) - 1
    while left <= right:
        mid = left + (right - left) // 2

        if myorderedlist[mid] == pair:
            return
        elif myorder(myorderedlist[mid], pair):
            left = mid + 1
        else:
            right = mid - 1
    # L'élément n'est pas dans la liste, donc on l'insère à la position 'left'
    myorderedlist.insert(left, pair)
    
def removepair(myorderedlist, pair):
    left, right = 0, len(myorderedlist) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if myorderedlist[mid] == pair:
            # L'élément est trouvé, le supprimer
            del myorderedlist[mid]
            return
        elif myorder(myorderedlist[mid] , pair):
            left = mid + 1
        else:
            right = mid - 1
            
def testpairs():
    mylist = [(1,0),(1,4),(2,3),(2,5),(2,6),(3,0),(4,5)]
    insertpair(mylist,(2,4))
    removepair(mylist,(4,5))
    print(mylist)
    
    
#testpairs()
def mergelists(lists):
    if not lists:
        return []

    min_heap = [(lst[0], i, 1) for i, lst in enumerate(lists) if lst]

    heapq.heapify(min_heap)

    merged_list = []

    prev_pair = None  # Pour suivre la paire précédente

    while min_heap:
        pair, i, idx = heapq.heappop(min_heap)

        # Vérifier si la paire est différente de la précédente
        if pair != prev_pair:
            merged_list.append(pair)
            prev_pair = pair

        if idx < len(lists[i]):
            next_pair = lists[i][idx]
            idx += 1
            heapq.heappush(min_heap, (next_pair, i, idx))
    return merged_list


######################### 1 cage functions #########################################

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

def buildcage(region,polygons,directions,nx,ny):
    xmax=region.max[0]
    ymax=region.max[1]
    if nx==1:
        stepx=xmax+1
    else:
        stepx=xmax//(nx-1)
    if ny==1:
        stepy=ymax+1 
    else:
        stepy=ymax//(ny-1)
    c=cage(nx,ny,stepx,stepy)
    
    for i in range(len(polygons)):
        polygon=polygons[i]
        if polygon.positions!=None:
            for j in range(len(polygon.positions)):
                #we test the position
                x0=polygon.min[0]+polygon.positions[j][0]
                x1=polygon.max[0]+polygon.positions[j][0]
                y0=polygon.min[1]+polygon.positions[j][1]
                y1=polygon.max[1]+polygon.positions[j][1]                    
                for ii in range(x0//stepx,1+x1//stepx):
                    for jj in range(y0//stepy,1+y1//stepy):
                        insertpair(c.cells[ii][jj],(i,j))
    return c
                        
def addInCage(c,polygons,ipolygon,jposition,newposition):
    polygon=polygons[ipolygon]
    x0=polygon.min[0]+newposition[0]
    x1=polygon.max[0]+newposition[0]
    y0=polygon.min[1]+newposition[1]
    y1=polygon.max[1]+newposition[1]                    
    for ii in range(int(x0//c.stepx),int(1+x1//c.stepx)):
        for jj in range(int(y0//c.stepy),int(1+y1//c.stepy)):
            insertpair(c.cells[ii][jj],(ipolygon,jposition))
            
           
def removefromcage(c,polygons,ipolygon,jposition):
    polygon=polygons[ipolygon]
    oldposition=polygon.positions[jposition]
    x0=polygon.min[0]+oldposition[0]
    x1=polygon.max[0]+oldposition[0]
    y0=polygon.min[1]+oldposition[1]
    y1=polygon.max[1]+oldposition[1]                   
    for i in range( int(x0//c.stepx), min(c.nx,int(1+x1//c.stepx))):
        for j in range( int(y0//c.stepy), min(c.ny,int(1+y1//c.stepy)) ):
            removepair(c.cells[i][j],(ipolygon,jposition))

                    
def translateincage(c,polygons,ipolygon,jposition,translation):
    if translation==(0,0):
        return
    polygon=polygons[ipolygon]
    oldx0=int((polygon.min[0]+polygon.positions[jposition][0])//c.stepx)
    oldx1=min(int((polygon.max[0]+polygon.positions[jposition][0])//c.stepx),c.nx-1)
    oldy0=int((polygon.min[1]+polygon.positions[jposition][1])//c.stepy)
    oldy1=min(int((polygon.max[1]+polygon.positions[jposition][1])//c.stepy),c.ny-1)
    
    newx0=int((polygon.min[0]+polygon.positions[jposition][0]+translation[0])//c.stepx)
    newx1=min(int((polygon.max[0]+polygon.positions[jposition][0]+translation[0])//c.stepx),c.nx-1)
    newy0=int((polygon.min[1]+polygon.positions[jposition][1]+translation[1])//c.stepy)
    newy1=min(int((polygon.max[1]+polygon.positions[jposition][1]+translation[1])//c.stepy),c.ny-1)
    
    if newx1==oldx1 and newx0==oldx0 and newy0==oldy0 and newy1==oldy1:
        return
    
    if newx0>oldx1 or newx1<oldx0 or newy0>oldy1 or newy1<oldy0:
        for i in range(newx0,newx1+1):
            for j in range(newy0,newy1+1):
                insertpair(c.cells[i][j],(ipolygon,jposition))
        for i in range(oldx0,oldx1+1):
            for j in range(oldy0,oldy1+1):
                removepair(c.cells[i][j],(ipolygon,jposition))
        #print("no common cells")
        return
                
    #The new cells
    if newx1>=oldx1:
        if newx1>oldx1 and newy1+1>newy0:
            for i in range(oldx1+1,min(c.nx,newx1+1)):
                for j in range(newy0,min(c.ny,newy1+1)):
                    insertpair(c.cells[i][j],(ipolygon,jposition))
        if newy1>oldy1 and oldx1+1>newx0:
            for i in range(newx0,min(c.nx,oldx1+1)):
                for j in range(oldy1+1,min(c.ny,newy1+1)):
                    insertpair(c.cells[i][j],(ipolygon,jposition))
        if newy0<oldy0 and newx0<oldx1+1:
            for i in range(newx0,min(c.nx,oldx1+1)):
                for j in range(newy0,oldy0):
                    insertpair(c.cells[i][j],(ipolygon,jposition))
    if newx0<=oldx0:
        if newy1+1>newy0:
            for i in range(newx0,min(oldx0,newx1+1,c.nx)):
                for j in range(newy0,min(c.ny,newy1+1)):
                    insertpair(c.cells[i][j],(ipolygon,jposition))
        if newy1>oldy1 and newx1+1>oldx0:
            for i in range(oldx0,min(c.nx,newx1+1)):
                for j in range(oldy1+1,min(c.ny,newy1+1)):
                    insertpair(c.cells[i][j],(ipolygon,jposition))
        if newy0<oldy0 and newx1+1>oldx0:
            for i in range(oldx0,min(c.nx,newx1+1)):
                for j in range(newy0,min(c.ny,oldy0)):
                    insertpair(c.cells[i][j],(ipolygon,jposition))
    #the old cells
    if oldx0<=newx0:
        if newx0>oldx0:
            for i in range(oldx0,newx0):
                for j in range(oldy0,oldy1+1):
                    removepair(c.cells[i][j],(ipolygon,jposition))
        if newy0>oldy0 and oldx1+1>oldx0:
            for i in range(oldx0,oldx1+1):
                for j in range(oldy0,newy0):
                    removepair(c.cells[i][j],(ipolygon,jposition))
        if newy1<oldy1 and oldx1+1>newx0:
            for i in range(newx0,oldx1+1):
                for j in range(newy1+1,oldy1+1):
                    removepair(c.cells[i][j],(ipolygon,jposition)) 
    if newx1<=oldx1:
        if oldy1+1>oldy0:
            for i in range(newx1+1,oldx1+1):
                for j in range(oldy0,oldy1+1):
                    removepair(c.cells[i][j],(ipolygon,jposition))
                
        if oldy0<newy0 and newx1+1>oldx0:
            for i in range(oldx0,newx1+1):
                for j in range(oldy0,newy0):
                    removepair(c.cells[i][j],(ipolygon,jposition))
        if  oldy1>newy1 and oldx0<newx1+1:
            for i in range(oldx0,newx1+1):
                for j in range(newy1+1, oldy1+1):
                    removepair(c.cells[i][j],(ipolygon,jposition))

    
# this function returns the indices of the polygons and positions that could cross the polygon at a given position

def polygonsincage(c,polygon,newposition):
    x0=polygon.min[0]+newposition[0]
    x1=polygon.max[0]+newposition[0]
    y0=polygon.min[1]+newposition[1]
    y1=polygon.max[1]+newposition[1]    
    cellsconcerned=[]                
    for ii in range( int(x0//c.stepx), int(1+x1//c.stepx)):
        for jj in range( int(y0//c.stepy), int(1+y1//c.stepy) ):
            cellsconcerned.append(c.cells[ii][jj])  
    pairs=mergelists(cellsconcerned)
    return pairs

#not yet tested

def unpack(c,polygons,ipolygon,jpositiontoremove):
    removefromcage(c,polygons,ipolygon,jpositiontoremove)
    polygon=polygons[ipolygon]
    polygon.positions.pop(jpositiontoremove)    
    if jpositiontoremove<len(polygons[ipolygon].positions):
        #we need to update the pairs of the cage for the indices j from jpositiontoremove+1 to len(polygons[ipolygon].positions)-1
        for j in range(jpositiontoremove,len(polygons[ipolygon].positions)):
            position=polygon.positions[j]
            x0=polygon.min[0]+position[0]
            x1=polygon.max[0]+position[0]
            y0=polygon.min[1]+position[1]
            y1=polygon.max[1]+position[1]                   
            for ii in range( int(x0//c.stepx), min(c.nx,int(1+x1//c.stepx))):
                for jj in range( int(y0//c.stepy), min(c.ny,int(1+y1//c.stepy)) ):
                    removepair(c.cells[ii][jj],(ipolygon,j+1))
                    insertpair(c.cells[ii][jj],(ipolygon,j))
  
    if len(polygon.positions)==0:
        polygon.positions=None


#########################  2 drop ##############################

#for optimization when we accept to remove polygons...

def conflict(c, region, polygons, directions, polygon, position):
    if inConvexRegion(polygon,position,region,directions)!=1:
        return 0,None
    pairs=polygonsincage(c,polygon,position)
    conflict=[]
    costconflict=0
    for p in pairs:
        if crossingPolygons(polygon,polygons[p[0]],position,polygons[p[0]].positions[p[1]],directions):
            costconflict=costconflict+polygons[p[0]].cost
            conflict.append(p)
        if costconflict>polygon.cost:
            return 0,None
    if len(conflict)==0:
        return 1,None
    return 2,conflict
    

def droparoundPolygon(c, region, polygons, directions, polygon, position, ntries, step):
    if inConvexRegion(polygon,position,region,directions)!=1:
        return 0,-1,None
    pairs=polygonsincage(c,polygon,position)
    positionavailable=True
    obstructions=[]
    for p in pairs:
        if crossingPolygons(polygon,polygons[p[0]],position,polygons[p[0]].positions[p[1]],directions):
            positionavailable=False
            obstructions.append(p)
            break
        
    if positionavailable==True:
        return 1,position
    #We try now some other positions around the position
    for e in range(ntries):
        offsetx=random.randint(-step//2,step//2)
        offsety=random.randint(-step//2,step//2)
        positionavailable=True
        newposition=(position[0]+offsetx,position[1]+offsety)
        
        if inConvexRegion(polygon,newposition,region,directions)==1:
            for p in obstructions: #obstructions is a list of pairs close to the region where we drop the current polygon
                if crossingPolygons(polygon,polygons[p[0]],newposition,polygons[p[0]].positions[p[1]],directions):
                    positionavailable=False
                    break
            if positionavailable==True:
                pairs=polygonsincage(c,polygon,newposition)
                for p in pairs:
                    if binarypair(obstructions, p)==-1:#otherwise we already tested this pair 
                        if crossingPolygons(polygon,polygons[p[0]],newposition,polygons[p[0]].positions[p[1]],directions):
                            positionavailable=False
                            obstructions.append(p)
                            break
        else:
            positionavailable=False
            
        if positionavailable==True:
            return 1,newposition
    return 0,None


def droparoundPolygonconflict(c, region, polygons, directions, polygon, position, ntries, step):
    if inConvexRegion(polygon,position,region,directions)!=1:
        return 0,-1,None
    pairs=polygonsincage(c,polygon,position)
    positionavailable=True
    obstructions=[]
    conflict=[]
    costobstruction=0
    for p in pairs:
        if crossingPolygons(polygon,polygons[p[0]],position,polygons[p[0]].positions[p[1]],directions):
            positionavailable=False
            costobstruction=costobstruction+polygons[p[0]].cost
            obstructions.append(p)
            if costobstruction>polygon.cost:
                break
        
    if positionavailable==True:
        return 1,position,None
    if costobstruction<polygon.cost:
        return 2,position,obstructions
    if costobstruction==polygon.cost:
        #if the area is reduced, we accept to change...
        a=0 
        for p in obstructions:
            a=a+polygons[p[0]].area
        if a>polygon.area:
            #print(f"area decreases from {a-polygon.area}")
            return 2,position,obstructions
        
    #We try now some other positions around the position
    for e in range(ntries):
        offsetx=random.randint(-step//2,step//2)
        offsety=random.randint(-step//2,step//2)
        positionavailable=True
        newposition=(position[0]+offsetx,position[1]+offsety)
        inconvex=False
        if inConvexRegion(polygon,newposition,region,directions)==1:
            #print(f"obstructions={obstructions}")
            newobstructions=[]
            newobstructionscost=0

            pairs=polygonsincage(c,polygon,newposition)
            for p in pairs:
                    if crossingPolygons(polygon,polygons[p[0]],newposition,polygons[p[0]].positions[p[1]],directions):
                        positionavailable=False
                        #print(f"new intersection {p}")
                        newobstructionscost=newobstructionscost+polygons[p[0]].cost
                        newobstructions.append(p)
                        if newobstructionscost>polygon.cost:
                            #print("break")
                            break
            if len(newobstructions)==0:
                return 1,newposition,None
            
            if newobstructionscost<polygon.cost:
                return 2,newposition,newobstructions
            
            
            if newobstructionscost==polygon.cost:
                #if the area is reduced, we accept to change...
                a=0 
                for p in newobstructions:
                    a=a+polygons[p[0]].area
                if a>polygon.area:
                    #print(f"area decreases from {a-polygon.area}")
                    return 2,newposition,newobstructions
    return 0,None


#Secondly, in Packing to say that the polygon is already packed. In this case, we don't take into account its self intersections
  
def dropPolygonInPacking(c,region, polygons, directions, ipolygon, jposition, position):
    if inConvexRegion(polygons[ipolygon],position,region,directions)!=1:
        return 0,None
    pairs=polygonsincage(c,polygons[ipolygon],position)  
    for p in pairs:
        if ipolygon!=p[0] or jposition!=p[1]:
            if crossingPolygons(polygons[ipolygon],polygons[p[0]],position,polygons[p[0]].positions[p[1]],directions)==1:
                #print("cannot drop")
                return 0
    return 1

 
############################## 3 push and move #################################

def move(c,region,polygons,directions,ipolygon,jposition,vector,constrainedvector):
    loop=1 
    polygon=polygons[ipolygon]
    position0=polygon.positions[jposition]
    validposition=(position0[0],position0[1])
    position=(position0[0],position0[1])
    newvector=vector
    count=0
    exactdivision=0
    numberofdrops=0
    countnewposition=0
    while loop and count<50:
        newposition=(position[0]+newvector[0],position[1]+newvector[1])
        if exactdivision==1 and numberofdrops>0:
            result=0
        else:   
            result=dropPolygonInPacking(c,region, polygons, directions, ipolygon, jposition, newposition)
            numberofdrops+=1
        if result==1:
            validposition=(newposition[0],newposition[1])
            position=newposition
            count=count+1 
            countnewposition=countnewposition+1
            if countnewposition==2:
                countnewposition=0
                newvector=(3*newvector[0],3*newvector[1]) 
        else:
            countnewposition=0
            numberofdrops=0
            count=count+1 
            newvector0=(newvector[0],newvector[1])
            newvector=(int(newvector[0]/2),int(newvector[1]/2)) 
            if 2*newvector[0]==newvector0[0] and 2*newvector[1]==newvector0[1]:
                #exact division
                exactdivision=1 
            else:
                exactdivision=0
            if newvector==(0,0) or dotprod(newvector,constrainedvector)<=0:
                translation=(validposition[0]-position0[0],validposition[1]-position0[1])
                translateincage(c, polygons, ipolygon, jposition, translation)
                polygon.positions[jposition]=validposition
                return position  
    translation=(validposition[0]-position0[0],validposition[1]-position0[1])
    translateincage(c, polygons, ipolygon, jposition, translation)
    polygon.positions[jposition]=validposition
    return position
            

def push(c,region,polygons,directions,ipolygon,jposition,vector,step):
    if vector==(0,0):
        return 1
    ratio=step/norm(vector)
    if ratio>1:
        ratio=int(ratio)
        v=(ratio*vector[0],ratio*vector[1])
    else:
        v=(vector[0],vector[1])
    moving=1
    count=0
    while moving==1 and count<20:
        position0=(polygons[ipolygon].positions[jposition][0],polygons[ipolygon].positions[jposition][1])
        count=count+1
        move(c,region,polygons,directions,ipolygon,jposition,v,vector)
        offsets=[1,2,4,8,16,32]
        for i in offsets:
            v0=[-i*v[1]+v[0],i*v[0]+v[1]]
            move(c,region,polygons,directions,ipolygon,jposition,v0,vector)
            v1=[i*v[1]+v[0],-i*v[0]+v[1]]
            move(c,region,polygons,directions,ipolygon,jposition,v1,vector)
        if position0==(polygons[ipolygon].positions[jposition][0],polygons[ipolygon].positions[jposition][1]):
            moving=0 
            
############################# 4 fill ############################

def createPositions(region,maxNumberOfPositions):
    direct=((1,0),(0,1))
    mini,maxi=dHull(direct,region.vertices)
    
    def countPositions(mini,maxi,step):
        c=0
        for x in range(int(mini[0]/step),int(maxi[0]/step)+1):
            for y in range(int(mini[1]/step),int(maxi[1]/step)+1):
                point=(x*step,y*step)
                if pip3(region,point):
                    c=c+1
        return c
    
    ratio=1.1
    xmax=max(vertex[0] for vertex in region.vertices) 
    if xmax<501:
        step=1
    else:
        step=max(vertex[0]/10 for vertex in region.vertices) 
    #print("first step is",step)
    n1=countPositions(mini,maxi,step)
    sens=0
    if n1<maxNumberOfPositions:
        step=step/ratio
        sens=+1
        loop=True
    elif n1>maxNumberOfPositions:
        step=step*ratio
        sens=-1
        loop=True
    else:
        loop=False
        sens=0
        n2=n1
    while loop:
        n2=countPositions(mini,maxi,step)
        if n2<maxNumberOfPositions and sens==+1:
            step=step/ratio
        elif n2<maxNumberOfPositions and sens==-1:
            loop=False
        elif n2>maxNumberOfPositions and sens==-1:
            step=ratio*step
        elif n2>maxNumberOfPositions and sens==+1:
            loop=False
            step=step*ratio
        else:
            loop=False
    step=int(step)
    if step==0:
        step=1
    
    positions=[]
    for x in range(int(mini[0]/step),int(maxi[0]/step)+1):
        for y in range(int(mini[1]/step),int(maxi[1]/step)+1):
            point=(int(x*step),int(y*step))
            if pip3(region,point):
                #print(point)
                positions.append(point)  
    #print("step positions= ",step)
    #We add a position in the center as first position...
    random.shuffle(positions)
    positions.insert(0,centroid(positions))
    return positions,step


def fillconflict(c,region,polygons,directions,unpackedindices,para):
    #print(f"fill around with {para.npositions} positions and {para.ntries} tries")
    #print(directions)
    positions,step=createPositions(region,para.npositions)  
    v0=(random.randint(-10,10),random.randint(-10,10))
    onepacked=False
    while v0==(0,0):
        v0=(random.randint(-10,10),random.randint(-10,10))
    a=0
    while a<len(unpackedindices):
        i=unpackedindices[a]
        #print(f"try to pack polygon {i}")
        polygonfullypacked=False
        stillNotPacked=True
        j=0
        while j<len(positions):
            position=(positions[j][0]-polygons[i].centroid[0],positions[j][1]-polygons[i].centroid[1])
            result= droparoundPolygonconflict(c, region, polygons, directions, polygons[i], position, para.ntries, step)
            if result[0]==1: 
                stillNotPacked=False
                positionfound=result[1]      
                #We pack the polygon of index i at position                      
                print(f"         cost {polygons[i].cost}, we pack polygon {i}")
                polygons[i].pack(positionfound) 
                addInCage(c, polygons, i, len(polygons[i].positions)-1, positionfound)
                
                #According to optionfill, we compute the direction to push 
                if para.optionfill==0:#in the random direction but all in the same direction
                    vectortopush=v0
                elif para.optionfill==1:
                    vectortopush=(random.randint(-10,10),random.randint(-10,10))
                    while vectortopush==(0,0):
                        vectortopush=(random.randint(-10,10),random.randint(-10,10))
                elif para.optionfill==2:#normal to the diameter on the left for the long items, and on the right for the short items...
                    vectortopush=normaltodiameter(polygons[i].vertices)    
                elif para.optionfill==3:#normal to the diameter 
                    vectortopush=normaltodiameterleftright(polygons[i].vertices)
                elif para.optionfill==4:#normal to the diameter 
                    vectortopush=normaltodiameterrandom(polygons[i].vertices)
                elif para.optionfill==5:#normal to the diameter 
                    vectortopush=normalmix(polygons[i].vertices)
                elif para.optionfill==6:#normal to the diameter 
                    vectortopush=normaltolongestedge(polygons[i].vertices)
                elif para.optionfill==7:#normal to the diameter 
                    vectortopush=mix2(polygons[i].vertices)
                elif para.optionfill==8:#designed for satris
                    vectortopush=normalsatris(polygons[i].vertices)
                elif para.optionfill==9:#designed for atris
                    vectortopush=normalatris(polygons[i].vertices)
                    
                #Then we push it
                push(c, region, polygons, directions, i, len(polygons[i].positions)-1, vectortopush, step)
                
                if len(polygons[i].positions)==polygons[i].quantity:
                    unpackedindices.remove(i)
                    polygonfullypacked=True
                    #in this case the value of a does not change 
                onepacked=True
                break
            if result[0]==2: 
                stillNotPacked=False
                positionfound=result[1]   
                cost=0
                
                #checks conflict pairs
                #pairs=polygonsincage(c,polygons[i],positionfound)
                #obs=[]
                #for p in pairs:
                #    if crossingPolygons(polygons[i],polygons[p[0]],positionfound,polygons[p[0]].positions[p[1]],directions):
                #        obs.append(p)
                #print(f"before unpacking obs is {obs}")
                result[2].sort(reverse=True)
                for pair in result[2]:
                    unpack(c,polygons,pair[0],pair[1])
                    if pair[0] not in unpackedindices:
                        unpackedindices.append(pair[0])
                    cost=cost+polygons[pair[0]].cost
                    
                #We pack the polygon of index i at position                      
                print(f"unpack {result[2]} to pack {i} : cost increases from {polygons[i].cost-cost}")    
                    
                #checks conflict pairs
                #pairs=polygonsincage(c,polygons[i],positionfound)
                #obs=[]
                #for p in pairs:
                #    if crossingPolygons(polygons[i],polygons[p[0]],positionfound,polygons[p[0]].positions[p[1]],directions):
                #        obs.append(p)
                #if len(obs)>0:
                #    #print(f"new position in fill={positionfound}")
                #    wait=input("wait!")
                        
                
                polygons[i].pack(positionfound) 
                addInCage(c, polygons, i, len(polygons[i].positions)-1, positionfound)
                
                #According to optionfill, we compute the direction to push 
                if para.optionfill==0:#in the random direction but all in the same direction
                    vectortopush=v0
                elif para.optionfill==1:
                    vectortopush=(random.randint(-10,10),random.randint(-10,10))
                    while vectortopush==(0,0):
                        vectortopush=(random.randint(-10,10),random.randint(-10,10))
                elif para.optionfill==2:#normal to the diameter on the left for the long items, and on the right for the short items...
                    vectortopush=normaltodiameter(polygons[i].vertices)    
                elif para.optionfill==3:#normal to the diameter 
                    vectortopush=normaltodiameterleftright(polygons[i].vertices)
                elif para.optionfill==4:#normal to the diameter 
                    vectortopush=normaltodiameterrandom(polygons[i].vertices)
                elif para.optionfill==5:#normal to the diameter 
                    vectortopush=normalmix(polygons[i].vertices)
                elif para.optionfill==6:#normal to the diameter 
                    vectortopush=normaltolongestedge(polygons[i].vertices)
                elif para.optionfill==7:#normal to the diameter 
                    vectortopush=mix2(polygons[i].vertices)
                elif para.optionfill==8:#designed for satris
                    vectortopush=normalsatris(polygons[i].vertices)
                elif para.optionfill==9:#designed for atris
                    vectortopush=normalatris(polygons[i].vertices)
                    
                #Then we push it
                push(c, region, polygons, directions, i, len(polygons[i].positions)-1, vectortopush, step)
                
                if len(polygons[i].positions)==polygons[i].quantity:
                    unpackedindices.remove(i)
                    polygonfullypacked=True
                    #in this case the value of a does not change   
                onepacked=True
                break
            j=j+1
        if stillNotPacked==True:
            a=a+1
        
    return onepacked



def computedigfeatures(region,polygons,para):
    maxdiameterofapolygon=max(diameter(polygon.vertices) for polygon in polygons)
    numberofpolygonpacked=0 
    for polygon in polygons:
        if polygon.positions!=None:
            numberofpolygonpacked=numberofpolygonpacked+len(polygon.positions)
    para.radiustodig=maxdiameterofapolygon*para.coeffradiustodig
    para.radiustopush=maxdiameterofapolygon*para.coeffradiustopush
    para.npositionstodig=min(10000,max(para.npositions,numberofpolygonpacked*para.coeffnpositionstodig))


def searchtopackhereconflict(positions,step,c,region,polygons,directions,unpackedindices,here,para):
    #print(directions) 
    #we keep only a ratio of the position according to their distance to here
    #print(f"searchtopackhere at {here}")
    #print(f"radiustodig={para.radiustodig}")
    #print(f"len of positions={len(positions)}")
    poses=[]
    for p in positions:
        if distance(p,here)<100*para.radiustodig:
            poses.append(p)
    poses.sort(key=lambda p:distance(p,here))
    while len(poses)>para.maxpositionsdigvertices:
        poses.pop(para.maxpositionsdigvertices)
    dd=distance(poses[len(poses)-1],here)
    #print(f"digs: {len(poses)} positions around")

    onepacked=False
    random.shuffle(unpackedindices)
    for p in poses:
        a=0
        while a<len(unpackedindices):
            i=unpackedindices[a]
            #print(f"try to pack polygon {i}")
            polygonfullypacked=False
            stillNotPacked=True
            position=(p[0]-polygons[i].centroid[0],p[1]-polygons[i].centroid[1])
            result= conflict(c, region, polygons, directions, polygons[i], position)
            #droparoundPolygonconflict(c, region, polygons, directions, polygon, position, ntries, step)
            if result[0]==1: 
                onepacked=True
                stillNotPacked=False  
                #We pack the polygon of index i at position                      
                print(f"         cost {polygons[i].cost}, we pack polygon {i}")              
                polygons[i].pack(position) 
                addInCage(c, polygons, i, len(polygons[i].positions)-1, position)
                vectortopush=(position[0]-here[0],position[1]-here[0])
                #Then we push it
                push(c, region, polygons, directions, i, len(polygons[i].positions)-1, vectortopush, step)

                if len(polygons[i].positions)==polygons[i].quantity:
                    unpackedindices.remove(i)
                    #in this case the value of a does not change   
                onepacked=True
                break
            elif result[0]==2:
                #let's analyze the conflicts...
                cost=0
                for pair in result[1]:
                    cost=cost+polygons[pair[0]].cost
                    
                weunpack=False
                if cost<=polygons[i].cost:
                    weunpack=True
                elif cost==polygons[i].cost:
                    areasum=0 
                    for pair in result[1]:
                        areasum=area+polygons[pair[0]].area
                    if areasum>polygons[i].area:
                        #print(f"area decreases")
                        weunpack=True
    
                if weunpack==True:
                    #we unpack 
                    result[1].sort(reverse=True)
                    for pair in result[1]:
                        unpack(c,polygons,pair[0],pair[1])
                        if pair[0] not in unpackedindices:
                            #unpackedindices.append(pair[0])
                            unpackedindices.insert(0,pair[0])
                            a=a+1
                    #we pack
                    polygons[i].pack(position) 
                    addInCage(c, polygons, i, len(polygons[i].positions)-1, position)
                    onepacked=True
                    #print(f"unpack {result[1]} to pack {i} : cost increases from {polygons[i].cost-cost}")
                    #Then we push it
                    vectortopush=(position[0]-here[0],position[1]-here[0])
                    push(c, region, polygons, directions, i, len(polygons[i].positions)-1, vectortopush, step)
                    #to remove...
                    #c=buildcage(region, polygons, directions, para.nxcage, para.nycage)

                    if len(polygons[i].positions)==polygons[i].quantity:
                        unpackedindices.remove(i)                   
                #to add in the case where we have small polygons, we can try to replace them...
            a=a+1       
    return onepacked


############################# 5 dig ############################

#for aroundvertex, we push all the polygons, for interior points, we push a bounded number at a bounded distance

def digHere(c,region,polygons,directions,step,here,para,aroundvertex):
    orderedlist=[]
    for i in range(len(polygons)): 
        if polygons[i].positions!=None:
            for j in range(len(polygons[i].positions)):
                if aroundvertex==False:
                    if distance(here,(polygons[i].centroid[0]+polygons[i].positions[j][0],polygons[i].centroid[1]+polygons[i].positions[j][1]))<para.radiustopush:
                        orderedlist.append((i,j))
                else:
                    orderedlist.append((i,j))
    orderedlist.sort(key=lambda indicespair:distance(here,(polygons[indicespair[0]].centroid[0]+polygons[indicespair[0]].positions[indicespair[1]][0],polygons[indicespair[0]].centroid[1]+polygons[indicespair[0]].positions[indicespair[1]][1])), reverse=True)
    if aroundvertex==False:                
        while len(orderedlist)>para.maxmovedigvertices:
            orderedlist.pop(0)
    else:
        while len(orderedlist)>3*para.maxmovedigvertices:
            orderedlist.pop(0)
    #print(f"moves: {len(orderedlist)} polygons")
    for indicespair in orderedlist:
        a=polygons[indicespair[0]].centroid[0]+polygons[indicespair[0]].positions[indicespair[1]][0]
        b=polygons[indicespair[0]].centroid[1]+polygons[indicespair[0]].positions[indicespair[1]][1]
        v=(a-here[0],b-here[1])
        push(c,region, polygons, directions, indicespair[0],indicespair[1], v, step)
        
def digHerewithradius(c,region,polygons,directions,step,here,para,aroundvertex,r):
    orderedlist=[]
    for i in range(len(polygons)): 
        if polygons[i].positions!=None:
            for j in range(len(polygons[i].positions)):
                if aroundvertex==False:
                    if distance(here,(polygons[i].centroid[0]+polygons[i].positions[j][0],polygons[i].centroid[1]+polygons[i].positions[j][1]))<r:
                        orderedlist.append((i,j))
                else:
                    orderedlist.append((i,j))
    orderedlist.sort(key=lambda indicespair:distance(here,(polygons[indicespair[0]].centroid[0]+polygons[indicespair[0]].positions[indicespair[1]][0],polygons[indicespair[0]].centroid[1]+polygons[indicespair[0]].positions[indicespair[1]][1])), reverse=True)
    if aroundvertex==False:                
        while len(orderedlist)>para.maxmovedigvertices:
            orderedlist.pop(0)
    else:
        while len(orderedlist)>3*para.maxmovedigvertices:
            orderedlist.pop(0)
    #print(f"moves: {len(orderedlist)} polygons")
    for indicespair in orderedlist:
        a=polygons[indicespair[0]].centroid[0]+polygons[indicespair[0]].positions[indicespair[1]][0]
        b=polygons[indicespair[0]].centroid[1]+polygons[indicespair[0]].positions[indicespair[1]][1]
        v=(a-here[0],b-here[1])
        push(c,region, polygons, directions, indicespair[0],indicespair[1], v, step)
        

def digandpackaroundvertex(positions,c,region,polygons,directions,step,unpackedindices,para):
    n=len(region.vertices)
    k=random.randint(0,n-1)
    here=region.vertices[k]
    digHere(c,region,polygons,directions,step,here,para,True)
    onepacked=searchtopackhereconflict(positions,step,c,region,polygons,directions,unpackedindices,here,para)
    return onepacked

def digandpackintheinterior(positions,c,region,polygons,directions,step,unpackedindices,para):
    here=(random.randint(0,region.max[0]),random.randint(0,region.max[1]))
    while pipregion(region,directions,here)==0:
        here=(random.randint(0,region.max[0]),random.randint(0,region.max[1]))
    digHere(c,region,polygons,directions,step,here,para,False)
    onepacked=searchtopackhereconflict(positions,step,c,region,polygons,directions,unpackedindices,here,para)
    return onepacked
    

############################# 6 packing ############################

class parameterspacking2:
    def __init__(self,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o):
        self.estimationstyle=a
        self.optionfill=b
        self.costexponent=c
        self.npositions=d
        self.coeffnpositionstodig=e
        self.coeffradiustopush=f
        self.coeffradiustodig=g
        self.npositionstodig=0
        self.radiustopush=0
        self.radiustodig=0
        self.maxmovedigvertices=h
        self.maxpositionsdigvertices=i
        self.ndigbeforestop=j
        self.ratiodigvertex=k
        self.nxcage=l
        self.nycage=m
        self.ntries=n
        self.coeffthickness=o
    def __str__(self): 
        w=f"estimationstyle={self.estimationstyle} -"
        w=w+f"optionfill={self.optionfill} - "
        w=w+f"costexponent={self.costexponent} - "        
        w=w+f"npositions = {self.npositions} - "
        w=w+f"npositionstodig={self.npositionstodig} - "
        w=w+f"diametertodig={self.radiustodig} - "
        w=w+f"ndigbeforestop={self.ndigbeforestop} - "
        w=w+f"ratiodigvertex={self.ratiodigvertex} - "
        w=w+f"ntries={self.ntries} "
        w=w+f"coeffthickness={self.coeffthickness}"
        return w
    
def scorefromfeatures(cost,areaslate,areahull,d,t,para):
    costexponent=para.costexponent
    if para.estimationstyle==0: 
        return cost
    elif para.estimationstyle==1:
        if random.randint(0,100)<50:
            return pow(cost,costexponent)*random.gauss(1, 0.15)/areaslate
        else: 
            return pow(cost,costexponent)*random.gauss(1, 0.15)/(10*areaslate)
    elif para.estimationstyle==2:
        a=areaslate
        return pow(cost,costexponent)/a
    elif para.estimationstyle==3:
        a=areaslate
        return pow(cost,costexponent)*random.gauss(1, 0.05)/a
    elif para.estimationstyle==4:
        a=0.5*areahull+0.5*areaslate
        return pow(cost,costexponent)*random.gauss(1, 0.05)/a
    elif para.estimationstyle==5:
        a=areahull
        return pow(cost,costexponent)/a
    elif para.estimationstyle==6:
        a=areahull
        return pow(cost,costexponent)*random.gauss(1, 0.05)/a
    elif para.estimationstyle==7:
        a=areaslate
        return (1+para.coeffthickness*t)*pow(cost,costexponent)*random.gauss(1, 0.005)/a 
    elif para.estimationstyle==8:
        return t   
    elif para.estimationstyle==9:
        a=areahull
        if t>4:#○we penalize if it long to avoid junctions in the length of jigsaw very thin polygons
            return pow(cost,costexponent)/(a+d*d)
        return pow(cost,costexponent)/a
    elif para.estimationstyle==10:
        return -areahull  
    return 0

def score(polygon,para):
    cost=polygon.cost
    area=polygon.area
    hull=convexHull(polygon.vertices)
    areahull=areaPolygon(hull)
    d=diameter(hull)
    t=thickness(hull)
    return polygon.weight*scorefromfeatures(cost,area,areahull,d,t,para)

