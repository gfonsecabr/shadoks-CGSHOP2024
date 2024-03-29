from daft import *

# extension of packing for working with slates (several items in relative fixed positions) 

############################# Plan #####################################

# 0  score function for slates
# 1  slates functions
# 2  drop
# 3  push and move 
# 4  fill
# 5  dig
# 6  packing slates
# 7  experiments (optimization of a solution or run from scratch)
# 8  check solution file


########################## 0 new score function ########################

#the function score calls scorefromfeatures in packing2

def score(polygons,sla,para):
    cost=sla.cost
    vertices=[]
    for ii in range(len(sla.ipolygons)):
        x=sla.x[ii]
        y=sla.y[ii]
        polygon=polygons[sla.ipolygons[ii]]
        for v in polygon.vertices:
            p=(v[0]+x,v[1]+y)
            if p not in vertices:
                vertices.append(p)
    areaslate=sla.area
    hull=convexHull(vertices)
    areahull=areaPolygon(hull)
    d=diameter(hull)
    t=thickness(hull)
    if para.estimationstyle>=10:
        para.estimationstyle=para.estimationstyle-10
        result=len(sla.ipolygons)*scorefromfeatures(cost,areaslate,areahull,d,t,para)
        para.estimationstyle=para.estimationstyle+10
        return result
    return sla.weight*scorefromfeatures(cost,areaslate,areahull,d,t,para)

########################## 1 slates functions ########################
            
def computeleft(polygons,sla):
    if sla.positions==None:
        mini=sla.quantity
    else:
        mini=sla.quantity-len(sla.positions)
    for ii in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[ii]
        if polygons[ipolygon].positions==None:
            if polygons[ipolygon].quantity<mini:
                mini=polygons[ipolygon].quantity
        elif polygons[ipolygon].quantity-len(polygons[ipolygon].positions)<mini:
            mini=polygons[ipolygon].quantity-len(polygons[ipolygon].positions)
    sla.left=mini
    return mini



# pack fills the cage, the positions of each polygon of the slate  and updates the left field of each slate...

def pack(c,polygons,slates,sla,position):
    print(f"            cost={sla.cost}, we pack {sla.ipolygons}")
    if sla.left==0:
        print("cannot pack the slate, no more left... pack returns 0")
        return 0
    sla.left=sla.left-1
    for ii in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[ii]
        #we update the positions of the polygons in the slate
        if polygons[ipolygon].positions==None:
            newposition=(position[0]+sla.x[ii],position[1]+sla.y[ii])
            #print(f"in pack, pack polygon {ipolygon} at {newposition}")
            polygons[ipolygon].positions=[newposition]
        else: 
            if  len(polygons[ipolygon].positions)<polygons[ipolygon].quantity:
                newposition=(position[0]+sla.x[ii],position[1]+sla.y[ii])
                polygons[ipolygon].positions.append(newposition)     
            else:
                print(f"polygon {ipolygon} is no more left for packing")
                return 0
        #We update the cage
        jposition=len(polygons[ipolygon].positions)-1
        x0=polygons[ipolygon].min[0]+newposition[0]
        x1=polygons[ipolygon].max[0]+newposition[0]
        y0=polygons[ipolygon].min[1]+newposition[1]
        y1=polygons[ipolygon].max[1]+newposition[1]                    
        for ii in range(int(x0//c.stepx),int(1+x1//c.stepx)):
            for jj in range(int(y0//c.stepy),int(1+y1//c.stepy)):
                insertpair(c.cells[ii][jj],(ipolygon,jposition))
        #We update the values of sla.left for the other slates containing the polygon...
        q=polygons[ipolygon].quantity-len(polygons[ipolygon].positions)
        for jj in polygons[ipolygon].inslates:
            slates[jj].left=min(slates[jj].left,q)
            #print(f"decreases .left in slates [{jj}]: {slates[jj].ipolygons}")
    
    if sla.positions==None:
        sla.positions=[position]
    else:
        sla.positions.append(position)
    return 1


#to do: take care about the cells... 
# for each packed polygon of the slate, take the last position and put it at the removed position
# change the cells of the cage accordingly

def unpackslate(c,polygons,slates,sla,jposition):
    position=sla.positions.pop(jposition)
    #update the positions in the polygon, in the cage and the slate
    for ii in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[ii]
        oldposition=(position[0]+sla.x[ii],position[1]+sla.y[ii])
        ipolygon=pair[0]
        jpositionpolygon=polygons[ipolygon].positions.index(oldposition)
        #removes the position
        oldposition=polygons[ipolygon].pop(jposition)
        #the cage
        x0=polygons[ipolygon].min[0]+oldposition[0]
        x1=polygons[ipolygon].max[0]+oldposition[0]
        y0=polygons[ipolygon].min[1]+oldposition[1]
        y1=polygon.max[1]+oldposition[1]                  
        for i in range( int(x0//c.stepx), min(c.nx,int(1+x1//c.stepx))):
            for j in range( int(y0//c.stepy), min(c.ny,int(1+y1//c.stepy)) ):
                removepair(c.cells[i][j],(ipolygon,jposition)) 
        #updates the left number of each slate
        k=polygons[ipolygon].quantity-len(polygons[ipolygon].positions) #it is the new number of this polygon availability, before it was k-1
        for jj in polygons[ipolygon].inslates:
            if k-1==slates[jj].left:
                #may be k was the responsible of this value. We recompute it
                computeleft(polygons,sla)  
    sla.pairs.pop(positionindex)
    sla.positions.pop(positionindex)
        


   
def changeslateposition(c,polygons, sla,jposition,pairsofposition,translation):
    if translation==(0,0):
        return

    for pair in pairsofposition:
        ipolygon2=pair[0]
        jposition2=pair[1]
        #updates the cage
        translateincage(c, polygons, ipolygon2, jposition2, translation)
        #updates the position
        polygons[ipolygon2].positions[jposition2]=(polygons[ipolygon2].positions[jposition2][0]+translation[0],polygons[ipolygon2].positions[jposition2][1]+translation[1])
    sla.positions[jposition]=(sla.positions[jposition][0]+translation[0],sla.positions[jposition][1]+translation[1])


def computespairsofposition(polygons,sla,jslaposition):
    #print("computes pairs of positions for slate")
    #print(f"j position=[{jslaposition}]")
    slaposition=sla.positions[jslaposition]
    pairs=[]
    for ii in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[ii]
        position=(slaposition[0]+sla.x[ii],slaposition[1]+sla.y[ii])
        #print(f"       search index of position={position} for polygon {ipolygon}")
        #print(f"the positions of the polygon are {polygons[ipolygon].positions}")
        #if position not in polygons[ipolygon].positions:
        #    print(f"slate {sla.ipolygons}")
        #    print(f"       search index of position={position} for polygon {ipolygon}")
        #    print(f"the positions of the polygon are {polygons[ipolygon].positions}")
        jposition=polygons[ipolygon].positions.index(position)
        pairs.append((ipolygon,jposition))
    #print(f"gets the pairs {pairs}")
    return pairs
       
########################## 2 drop ########################

# we use the variable newinpacking to avoid to test selfintersections when it is not for a new position of the slate
# newinpacking=1 for a new drop

def drop(c, region, polygons, directions, sla, slaposition, jslaposition, pairsofposition, ntries, step, newinpacking): 
    for ii in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[ii]
        position=(slaposition[0]+sla.x[ii],slaposition[1]+sla.y[ii])
        if inConvexRegion(polygons[ipolygon],position,region,directions)!=1:
            return 0,-1,None
    
    positionavailable=True
    obstructions=[]
    for ii in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[ii]
        polygon=polygons[ipolygon]
        position=(slaposition[0]+sla.x[ii],slaposition[1]+sla.y[ii])
        pairs=polygonsincage(c,polygon,position)
        if newinpacking!=1:
            for u in pairsofposition:
                removepair(pairs,u)
        for p in pairs:
            if crossingPolygons(polygon,polygons[p[0]],position,polygons[p[0]].positions[p[1]],directions)==1:
                #print(f"for pair {pair} position not available due to pair {p}")
                positionavailable=False
                obstructions.append(p)
                break
        if positionavailable==False:
            break
    #print("position not available")
    
    if positionavailable==True:
        return 1,-1,slaposition
    #We try now some other positions around the position
    for e in range(ntries):
        offsetx=random.randint(-step//2,step//2)
        offsety=random.randint(-step//2,step//2)
        newslaposition=(slaposition[0]+offsetx,slaposition[1]+offsety)
        #test in region
        positionavailable=True
        for ii in range(len(sla.ipolygons)):
            ipolygon=sla.ipolygons[ii]
            position=(newslaposition[0]+sla.x[ii],newslaposition[1]+sla.y[ii])
            if inConvexRegion(polygons[ipolygon],position,region,directions)!=1:
                positionavailable=False
                break
        
        if positionavailable==True:
            for ii in range(len(sla.ipolygons)):
                polygon=polygons[sla.ipolygons[ii]]
                position=(newslaposition[0]+sla.x[ii],newslaposition[1]+sla.y[ii])
                pairs=polygonsincage(c,polygon,position)
                if newinpacking!=1:
                    for u in pairsofposition:
                        removepair(pairs,u)             
                for p in obstructions: #obstructions is a list of pairs close to the region where we drop the current polygon
                    #print("try a crossing")
                    if crossingPolygons(polygon,polygons[p[0]],position,polygons[p[0]].positions[p[1]],directions):
                        positionavailable=False
                        break
                if positionavailable==True:
                    for p in pairs:
                        if binarypair(obstructions, p)==-1:#otherwise we already tested this pair 
                            if crossingPolygons(polygon,polygons[p[0]],position,polygons[p[0]].positions[p[1]],directions):
                                positionavailable=False
                                obstructions.append(p)
                                break
                if positionavailable==False:
                    break            
        if positionavailable==True:
            #print(f"try {e} with ")
            #rint("undirect drop")
            return 1,-1,newslaposition
    return -obstructions[0][0], obstructions[0][1],None

def dropconflict(c, region, polygons, directions, sla, slaposition): 
    for ii in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[ii]
        position=(slaposition[0]+sla.x[ii],slaposition[1]+sla.y[ii])
        if inConvexRegion(polygons[ipolygon],position,region,directions)!=1:
            return 0,None,None
    
    positionavailable=True
    conflict=[]
    costconflict=0
    countedpairs=[]

    for ii in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[ii]
        polygon=polygons[ipolygon]
        position=(slaposition[0]+sla.x[ii],slaposition[1]+sla.y[ii])
        pairs=polygonsincage(c,polygon,position)
        for p in pairs:
            if crossingPolygons(polygon,polygons[p[0]],position,polygons[p[0]].positions[p[1]],directions)==1:
                #print(f"for pair {pair} position not available due to pair {p}")
                positionavailable=False
                if p not in conflict:   
                    conflict.append(p)
                    costconflict=costconflict+polygons[p[0]].cost  
    if len(conflict)==0:
        return 1,None,None
    return 2,conflict,costconflict

def droparoundconflictslate(c, region, polygons, directions, sla, slaposition, ntries, step):
    for ii in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[ii]
        position=(slaposition[0]+sla.x[ii],slaposition[1]+sla.y[ii])
        if inConvexRegion(polygons[ipolygon],position,region,directions)!=1:
            return 0,None,None,None
        
    #We try now some  positions around the position
    offsetx=[0]
    offsety=[0]
    for e in range(ntries):
        offsetx.append(random.randint(-step//2,step//2))
        offsety.append(random.randint(-step//2,step//2))
        
    mincost=2*sla.cost
    bestnewposition=None
    bestconflictpairs=[]
    for i in range(len(offsetx)):
        positionavailable=True
        newslaposition=(slaposition[0]+offsetx[i],slaposition[1]+offsety[i])
        
        result,conflictpairs,cost=dropconflict(c, region, polygons, directions, sla, newslaposition)
        if result==1:
            return 1,[],newslaposition,0
        elif result==2:
            if cost<mincost and cost<sla.cost:
                bestnewposition=newslaposition
                bestconflictpairs=conflictpairs
                mincost=cost
    if mincost<sla.cost:
        return 2,bestconflictpairs,bestnewposition,sla.cost-mincost
    return 0,None,None,-10


###################### 3 move and push ######################
    
# moves a slate... same function if it packed or not packed...


def moveslate(c,region,polygons,directions,slates,isla,jposition,pairsofposition,vector,constrainedvector,newinpacking):
    #print(f"\nmoves the slate {isla} in the vector direction {vector} from position {slates[isla].positions[jposition]}")
    loop=1 
    sla=slates[isla]
    position0=sla.positions[jposition]
    position=(position0[0],position0[1])
    newvector=vector
    count=0
    exactdivision=0
    numberofdrops=0
    countnewposition=0
    while loop and count<100:
        newposition=(position[0]+newvector[0],position[1]+newvector[1])
        if exactdivision==1 and numberofdrops>0:
            result=(0,(0,0))
        else:   
            result=drop(c, region, polygons, directions, sla, newposition,jposition,pairsofposition,0, 0, newinpacking)
            numberofdrops+=1
        if result[0]==1:
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
                exactdivision=1 
            else:
                exactdivision=0
            if newvector==(0,0) or dotprod(constrainedvector,newvector)<=0:
                #if newinpacking=0 we pack
                if newinpacking==1:
                    #print(f"the slate {isla} is packed")
                    pack(c,polygons,slates,sla,position)
                    
                else:
                    #print(f"the slate {isla} is moved")
                    translation=(position[0]-position0[0],position[1]-position0[1])
                    changeslateposition(c,polygons,sla,jposition,pairsofposition,translation)
                return position
    return position

def pushslate(c,region,polygons,directions,slates,isla,jposition,pairsofposition,vector,step):
    #print(f"pushslate with vector {vector} and pairsofpositions={pairsofposition}")
    if vector==(0,0):
        return 1
    ratio=step/norm(vector)
    if ratio>1:
        ratio=int(ratio)
        v=(ratio*vector[0],ratio*vector[1])
    else:
        v=(vector[0],vector[1])
    #print(f"initial vector in pushslate={v}")
    moving=1
    count=0
    offsets=[1,2,4,8,16,32]
    while moving==1 and count<20:
        #print(pairsofposition)
        position0=(slates[isla].positions[jposition][0],slates[isla].positions[jposition][1])
        count=count+1
        
        moveslate(c,region,polygons,directions,slates,isla,jposition,pairsofposition,v,vector,0)#0 becaus eit is not a new slate in the packing... we just push it
        for i in offsets:
            v0=[-i*v[1]+v[0],i*v[0]+v[1]]
            if v0!=(0,0):
                moveslate(c,region,polygons,directions,slates,isla,jposition,pairsofposition,v0,vector,0)#0 becaus eit is not a new slate in the packing... we just push it
            
            v1=[i*v[1]+v[0],-i*v[0]+v[1]]
            if v1!=(0,0):
                moveslate(c,region,polygons,directions,slates,isla,jposition,pairsofposition,v1,vector,0)#0 becaus eit is not a new slate in the packing... we just push it

        if position0==slates[isla].positions[jposition]:
            moving=0 

def testpushslate():
    print("start testpushslate")
    directions=[(1,0),(0,1)]
    regionpoly=((0,0),(100,0),(100,100),(0,100))
    
    region=polygon(1,0,regionpoly,0,0,directions)
    xmax=max(vertex[0] for vertex in region.vertices)
    ymax=max(vertex[1] for vertex in region.vertices)
    polygons=[polygon(0,i,[(0,0),(1,0),(1,1),(0,1)],1,1,directions) for i in range(200)]
    
    nx=10
    ny=10
    c=buildcage(region, polygons, directions, nx, ny)
    
    #we build some basic slates...
    slates=[]
    for i in range(100):
        sla=slate(polygons,i,i)
        addpolygoninslate(sla,polygons,i+100,(0,1))
        slates.append(sla)

    for j in range(len(slates)):
        position=(10*(j//10) +5 , 10*(j%10)+5 )
        pack(c,polygons,slates,slates[j],position)
    step=10
    vector=(1,1)
    pairsofposition=[(10,0),(110,0)]
    pushslate(c,region,polygons,directions,slates,10,0,pairsofposition,vector,step)
    #for i in range(len(slates)):
        #pushslate(c,region,polygons,directions,slates,i,0,vector,step)
    grid=[20,150,50,20]
    scale=max(xmax/grid[1],ymax/grid[2])
    grid[1]=xmax/scale+100
    cost,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons)    
    print(f"the cost of the packing is {round(100*cost/totalcost,2)}")
    #create SVG file
    name=f"testpushslate.svg"
    print(name)
    file=createSVG(name)
    drawWindow(file, grid)
    
    drawPacking(file, grid, region, polygons, scale)
    closeSVG(file)
    print("end testpushslate")

#testpushslate()

    
###################### 4 fill ######################

def hullslate(polygons,sla):
    areaslate=0
    vertices=[]
    for ii in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[ii]
        position=(sla.x[ii],sla.y[ii])
        for v in polygons[ipolygon].vertices:
            w=(v[0]+position[0],v[1]+position[1])
            if w not in vertices:
                vertices.append(w)
    return convexHull(vertices)

def thicknessslate(polygons,sla):
    hull=hullslate(polygons,sla)
    return thickness(hull)

  

def fill(c,region,polygons,slates,directions,indicestopack,packedpairs,para):
    print(f"fill with {para.npositions} positions and {para.ntries} tries")
    positions,step=createPositions(region,para.npositions) 
    random.shuffle(positions)
    center=centroid(positions)
    ccc=(int(center[0]),int(center[1]))
    positions.insert(0,ccc)   
    a=0
    #we choose to push the tiles in the direction (2,1)
    vectortopush=(random.randint(-10,10),random.randint(-10,10))
    while vectortopush==(0,0):
        vectortopush=(random.randint(-10,10),random.randint(-10,10))
    #vectorlist=[vectortopush]
    #vectortopush=(-1,-2)

    
    while a<len(indicestopack):
        i=indicestopack[a]
        pairsofposition=[]
        #print(f"try to pack slate {i}")
        stillnotpacked=True
        j=0
        fullypacked=False
        while j<len(positions):
            position=positions[j]
            if slates[i].positions==None:
                jposition=0
            else:
                jposition=len(slates[i].positions)
            result= drop(c, region, polygons, directions, slates[i], position, jposition, pairsofposition, para.ntries, step, 1)
            if result[0]==1:
                stillnotpacked=False
                positionfound=result[2]   
                
                #We pack the polygon of index i at position  
                newposition=result[2]                    
                #print(f"                we pack {slates[i].ipolygons} at position {position}")
                canbepacked=pack(c,polygons,slates,slates[i],newposition)
                if canbepacked==0:
                    fullypacked=True
                else:
                    packedpairs.append((i,len(slates[i].positions)-1))
                    # we compute the pairs ipolygon/jposition of the new slate
                    pairsofposition=[]
                    listofipolygons=[]
                    count=[]
                    for iipolygon in slates[i].ipolygons:
                        if iipolygon in listofipolygons:
                            e=listofipolygons.index(iipolygon)
                            pairsofposition.append((iipolygon,len(polygons[iipolygon].positions)-1-count[e]))
                            count[e]+=1
                        else:
                            listofipolygons.append(iipolygon)
                            count.append(1)#the two lists count and listofipolygons are synchronized. Count tells how many times the polygon has been considered
                            pairsofposition.append((iipolygon,len(polygons[iipolygon].positions)-1))
                            
                    #According to optionfill, we compute the direction to push 
                    if para.optionfill==0:#in the random direction but all in the same direction
                        vectortopush=v0
                    elif para.optionfill==1:
                        vectortopush=(random.randint(-10,10),random.randint(-10,10))
                        while vectortopush==(0,0):
                            vectortopush=(random.randint(-10,10),random.randint(-10,10))
                    elif para.optionfill==2:#normal to the diameter on the left for the long items, and on the right for the short items...
                        vectortopush=normaltodiameter(hullslate(polygons,slates[i]))    
                    elif para.optionfill==3:#normal to the diameter 
                        vectortopush=normaltodiameterleftright(hullslate(polygons,slates[i]))
                    elif para.optionfill==4:#normal to the diameter 
                        vectortopush=normaltodiameterrandom(hullslate(polygons,slates[i]))
                    elif para.optionfill==5:#normal to the diameter 
                        vectortopush=normalmix(hullslate(polygons,slates[i]))
                    elif para.optionfill==6:#normal to the diameter 
                        vectortopush=normaltolongestedge(hullslate(polygons,slates[i]))
                    elif para.optionfill==7:#normal to the diameter 
                        vectortopush=mix2(hullslate(polygons,slates[i]))
                    elif para.optionfill==8:#designed for satris
                        vectortopush=normalsatris(hullslate(polygons,slates[i]))
                    elif para.optionfill==9:#designed for atris
                        vectortopush=normalatris(hullslate(polygons,slates[i]))
                    pushslate(c, region, polygons, directions, slates, i, len(slates[i].positions)-1, pairsofposition, vectortopush, step)
                    
                    if slates[i].left==0: #should be corrected when a slate contains multiple items
                        fullypacked=True
                    m=len(indicestopack)
                    for k in range(1,m+1):
                        kk=indicestopack[m-k]
                        if slates[kk].left==0 and kk!=i:
                            indicestopack.pop(m-k)   
                    break
            j=j+1
        if fullypacked==True:
            #print(f"{i} fully packed")
            a=indicestopack.index(i)
            indicestopack.remove(i)
            
            #a does not change
        if stillnotpacked==True:
            #print(f"not packed: polygon {slates[i].ipolygons[0]}")
            a=indicestopack.index(i)+1
    return step

def fillconflict(positions,c,region,polygons,slates,directions,indicestopack,para,step):
    print(f"fillconflict with {para.npositions} positions and {para.ntries} tries")
    random.shuffle(positions)
    center=centroid(positions)
    ccc=(int(center[0]),int(center[1]))
    positions.insert(0,ccc)   
    a=0
    while a<len(indicestopack):
        i=indicestopack[a]
        wecontinueafterapacking=False
        if i<len(indicestopack)-10:
            wecontinueafterpacking=True
            nextindices=[indicestopack[a+cc] for cc in range(10)]
            
        nextindices=[]
        #could recompute left
        if slates[i].left==0: 
            indicestopack.pop(a)
        else:
            print(f"try to pack slate {slates[i].ipolygons} (left={slates[i].left})")
            #print(indicestopack)
            j=0
            onepacked=False
            while j<len(positions):
                #print(f"at position of index {j} while positions of length {len(positions)}")
                position=positions[j]                                        
                result,conflictpairs,newposition,costimprovement=droparoundconflictslate(c, region, polygons, directions, slates[i], position, ntries, step)
                #result=0 nothing good
                #result=1 perfect, no conflict
                #result=2 conflicts but good...
                if result==1: 
                    canbepacked=pack(c,polygons,slates,slates[i],newposition)
                    if canbepacked==0:
                        onepacked=True
                    else:
                        # we compute the pairs ipolygon/jposition of the new slate
                        pairsofposition=[]
                        listofipolygons=[]
                        count=[]
                        for iipolygon in slates[i].ipolygons:
                            if iipolygon in listofipolygons:
                                e=listofipolygons.index(iipolygon)
                                pairsofposition.append((iipolygon,len(polygons[iipolygon].positions)-1-count[e]))
                                count[e]+=1
                            else:
                                listofipolygons.append(iipolygon)
                                count.append(1)#the two lists count and listofipolygons are synchronized. Count tells how many times the polygon has been considered
                                pairsofposition.append((iipolygon,len(polygons[iipolygon].positions)-1))
                                
                        #push
                        vectortopush=(random.randint(-10,10),random.randint(-10,10)) 
                        while vectortopush==(0,0):
                            vectortopush=(random.randint(-10,10),random.randint(-10,10))    
                        pushslate(c, region, polygons, directions, slates, i, len(slates[i].positions)-1, pairsofposition, vectortopush, step)
                        
                        remaining=computeleft(polygons,slates[i])
                        if remaining==0: #should be corrected when a slate contains multiple items
                            for k in slates[i].ipolygons:
                                if polygons[k].quantity-len(polygons[k].positions)==0:
                                    for u in range(len(slates)):
                                        if k in slates[u].ipolygons:
                                            slates[u].left=0 
                                            if u in indicestopack:
                                                indicestopack.remove(u) 
                        break
                    
                elif result==2:
                        onepacked=True
                        stillnotpacked=False
                        #we unpack 
                        conflictpairs.sort(reverse=True)
                        freeslates=[]
                        print(conflictpairs)
                        for pair in conflictpairs:
                            unpack(c,polygons,pair[0],pair[1])
                            print(f"we unpack {pair[0]}")
                            for e in range(len(slates)):
                                if pair[0] in slates[e].ipolygons:
                                    freeslates.append(e)
                        
                        for e in freeslates:
                            before=slates[e].left
                            remaining=computeleft(polygons,slates[e])
                            if before==0 and remaining>0:
                                #we put this slate in activity...
                                indicestopack.append(e)
                                
                        #now we pack... 
                        canbepacked=pack(c,polygons,slates,slates[i],newposition)
                        if canbepacked==0:
                            fullypacked=True
                        else:
                            # we compute the pairs ipolygon/jposition of the new slate
                            pairsofposition=[]
                            listofipolygons=[]
                            count=[]
                            for iipolygon in slates[i].ipolygons:
                                if iipolygon in listofipolygons:
                                    e=listofipolygons.index(iipolygon)
                                    pairsofposition.append((iipolygon,len(polygons[iipolygon].positions)-1-count[e]))
                                    count[e]+=1
                                else:
                                    listofipolygons.append(iipolygon)
                                    count.append(1)#the two lists count and listofipolygons are synchronized. Count tells how many times the polygon has been considered
                                    pairsofposition.append((iipolygon,len(polygons[iipolygon].positions)-1))
                                    
                            #push
                            vectortopush=(random.randint(-10,10),random.randint(-10,10)) 
                            while vectortopush==(0,0):
                                vectortopush=(random.randint(-10,10),random.randint(-10,10))    
                            pushslate(c, region, polygons, directions, slates, i, len(slates[i].positions)-1, pairsofposition, vectortopush, step)
                            
                            remaining=computeleft(polygons,slates[i])
                            if remaining==0: #should be corrected when a slate contains multiple items
                                fullypacked=True
                                concernedslates=[]
                                for k in slates[i].ipolygons:
                                    if polygons[k].quantity-len(polygons[k].positions)==0:
                                        for u in range(len(slates)):
                                            if k in slates[u].ipolygons:
                                                slates[u].left=0 
                                                if u in indicestopack:
                                                    indicestopack.remove(u)  
                            break
                j=j+1
            
            if onepacked==True:
                break
        a=a+1
        if onepacked==True:
            break
    return onepacked


#There is a parameter which is the ratio to the distance to here that we keep in the positions

def fillwithslateshere(c,region,polygons,slates,directions,npositions,indicestopack, ratio, ntries,here):   
    positions,step=createPositions(region,npositions)  
    maxd=max(distance(p,here) for p in positions)
    i=len(positions)-1
    while i>=0:
        if distance(positions[i],here )>ratio*maxd:
            positions.pop(i)
        i=i-1
    print(f"digs: {len(positions)} positions around")
    a=0
    wepackaslate=0
    while a<len(indicestopack):
        i=indicestopack[a]
        pairsofposition=[]
        #print(f"try to pack slate {i}")
        stillnotpacked=True
        j=0
        fullypacked=False
        if slates[i].left>0:
            while j<len(positions):
                position=positions[j]
                result= drop(c, region, polygons, directions, slates[i], position, 0, pairsofposition, ntries, step, 1)           
                if result[0]==1:
                    wepackaslate=1
                    stillnotpacked=False
                    positionfound=result[2]      
                    #We pack the polygon of index i at position                      
                    #print(f"                we pack slate {slates[i].ipolygons} at position {position} ")
                    pack(c,polygons,slates,slates[i],result[2])
                    pairsofposition=[]
                    listofipolygons=[]
                    count=[]
                    for iipolygon in slates[i].ipolygons:
                        if iipolygon in listofipolygons:
                            e=listofipolygons.index(iipolygon)
                            pairsofposition.append((iipolygon,len(polygons[iipolygon].positions)-1-count[e]))
                            count[e]+=1
                        else:
                            listofipolygons.append(iipolygon)
                            pairsofposition.append((iipolygon,len(polygons[iipolygon].positions)-1))
                            count.append(1)
                    #push
                    vectortopush=(positionfound[0]-here[0],positionfound[1]-here[0])
                    pushslate(c, region, polygons, directions, slates, i, len(slates[i].positions)-1, pairsofposition, vectortopush, step)

                    if slates[i].left==0:
                        fullypacked=True
                    m=len(indicestopack)
                    for k in range(1,m+1):
                        kk=indicestopack[m-k]
                        if slates[kk].left==0 and kk!=i:
                            indicestopack.pop(m-k) 
                    break
                j=j+1
            if fullypacked==True:
                a=indicestopack.index(i)
                indicestopack.remove(i)
                #a does not change
                
                
            if stillnotpacked==True:
                a=indicestopack.index(i)+1
        else:
            indicestopack.remove(i)
    return wepackaslate

def searchtopackslatewithconflict(positions,c,region,polygons,slates,directions,indicestopack, para,here,step,radiustodig):       
    poses=[]
    for p in positions:
        if distance(p,here)<radiustodig:
            poses.append(p)
    poses.sort(key=lambda p:distance(p,here))
    while len(poses)>para.maxpositionsdigvertices:
        poses.pop(para.maxpositionsdigvertices)
    dd=distance(poses[len(poses)-1],here)    
        

    print(f"digs: {len(poses)} positions around")

    onepacked=False
    for p in poses:
        a=0
        while a<len(indicestopack):
            i=indicestopack[a]           
            result,conflictpairs,newposition,costimprovement=droparoundconflictslate(c, region, polygons, directions, slates[i], p, ntries, step)
            
            if result==1:
                onepacked=True
                canbepacked=pack(c,polygons,slates,slates[i],newposition)
                if canbepacked==0:
                    onepacked=True
                else:
                    # we compute the pairs ipolygon/jposition of the new slate
                    pairsofposition=[]
                    listofipolygons=[]
                    count=[]
                    for iipolygon in slates[i].ipolygons:
                        if iipolygon in listofipolygons:
                            e=listofipolygons.index(iipolygon)
                            pairsofposition.append((iipolygon,len(polygons[iipolygon].positions)-1-count[e]))
                            count[e]+=1
                        else:
                            listofipolygons.append(iipolygon)
                            count.append(1)#the two lists count and listofipolygons are synchronized. Count tells how many times the polygon has been considered
                            pairsofposition.append((iipolygon,len(polygons[iipolygon].positions)-1))
                            
                    #push
                    vectortopush=(random.randint(-10,10),random.randint(-10,10)) 
                    while vectortopush==(0,0):
                        vectortopush=(random.randint(-10,10),random.randint(-10,10))    
                    pushslate(c, region, polygons, directions, slates, i, len(slates[i].positions)-1, pairsofposition, vectortopush, step)
                    
                    remaining=computeleft(polygons,slates[i])
                    if remaining==0: #should be corrected when a slate contains multiple items
                        concernedslates=[]
                        for k in slates[i].ipolygons:
                            if polygons[k].quantity-len(polygons[k].positions)==0:
                                for u in range(len(slates)):
                                    if k in slates[u].ipolygons:
                                        slates[u].left=0 
                                        if u in indicestopack:
                                            indicestopack.remove(u) 
                    break
                
            elif result==2:
                    onepacked=True
                    #we unpack 
                    
                    conflictpairs.sort(reverse=True)
                    freeslates=[]
                    for pair in conflictpairs:
                        print(f"we unpack {pair[0]}")
                        unpack(c,polygons,pair[0],pair[1])
                        for e in range(len(slates)):
                            if pair[0] in slates[e].ipolygons:
                                freeslates.append(e)
                    
                    for e in freeslates:
                        before=slates[e].left
                        remaining=computeleft(polygons,slates[e])
                        if before==0 and remaining>0:
                            #we put this slate in activity...
                            indicestopack.append(e)
                            
                    #now we pack... 
                    canbepacked=pack(c,polygons,slates,slates[i],newposition)
                    if canbepacked==0:
                        fullypacked=True
                    else:
                        # we compute the pairs ipolygon/jposition of the new slate
                        pairsofposition=[]
                        listofipolygons=[]
                        count=[]
                        for iipolygon in slates[i].ipolygons:
                            if iipolygon in listofipolygons:
                                e=listofipolygons.index(iipolygon)
                                pairsofposition.append((iipolygon,len(polygons[iipolygon].positions)-1-count[e]))
                                count[e]+=1
                            else:
                                listofipolygons.append(iipolygon)
                                count.append(1)#the two lists count and listofipolygons are synchronized. Count tells how many times the polygon has been considered
                                pairsofposition.append((iipolygon,len(polygons[iipolygon].positions)-1))
                                
                        #push
                        vectortopush=(random.randint(-10,10),random.randint(-10,10)) 
                        while vectortopush==(0,0):
                            vectortopush=(random.randint(-10,10),random.randint(-10,10))    
                        pushslate(c, region, polygons, directions, slates, i, len(slates[i].positions)-1, pairsofposition, vectortopush, step)
                        
                        remaining=computeleft(polygons,slates[i])
                        if remaining==0: #should be corrected when a slate contains multiple items
                            fullypacked=True
                            concernedslates=[]
                            for k in slates[i].ipolygons:
                                if polygons[k].quantity-len(polygons[k].positions)==0:
                                    for u in range(len(slates)):
                                        if k in slates[u].ipolygons:
                                            slates[u].left=0 
                                            if u in indicestopack:
                                                indicestopack.remove(u) 
                        break
            
            a=a+1 
            if onepacked:
                break
        if onepacked:
            break
    return onepacked
    
###################### 5 dig ######################

def digslateshere(c,region,polygons,slates,directions,step,here,packedpairs):
    #pairs=[]
    #for i in range(len(slates)):
    #    if slates[i].positions!=None:
    #        for j in range(len(slates[i].positions)):
    #            pairs.append((i,j)) 
    pairs=packedpairs.copy()
              
    pairs.sort(key=lambda pair:distance(here,(slates[pair[0]].positions[pair[1]][0],slates[pair[0]].positions[pair[1]][1])),reverse=True)
    count=0
    for pair in pairs:
        pairsofposition=computespairsofposition(polygons, slates[pair[0]], pair[1])
        count=count+1 
        v=(slates[pair[0]].positions[pair[1]][0]-here[0],slates[pair[0]].positions[pair[1]][1]-here[1])
        pushslate(c,region,polygons,directions,slates,pair[0],pair[1],pairsofposition,v,step)

        
def digslates(c,region,polygons,slates,directions,step,k,packedpairs):
    print("dig slates")
    pointlist=[]
    i=0
    here=(0,0)
    while i<k:
        here=(random.randint(0,region.max[0]),random.randint(0,region.max[1]))
        if pipregion(region,directions,here):
            digslateshere(c,region,polygons,slates,directions,step,here,packedpairs)
            i=i+1
    return here

def digandpackaroundvertex(c,region,polygons,slates,directions,step,indicestopack,packedpairs,ratio, npositions,ntries):
    #print("digandpackaroundvertex")
    n=len(region.vertices)
    k=random.randint(0,n-1)
    here=region.vertices[k]  
    digslateshere(c, region, polygons, slates, directions, step, here, packedpairs)
    digslateshere(c, region, polygons, slates, directions, step, here, packedpairs)
    wepackaslate=fillwithslateshere(c,region,polygons,slates,directions,npositions,indicestopack, ratio, ntries,here)
    return here,wepackaslate

def digandpacksomewhere(c,region,polygons,slates,directions,step,indicestopack,packedpairs,ratio, npositions,ntries):
    #print("digandpackaroundvertex")
    n=len(region.vertices)
    here=(random.randint(0,region.max[0]),random.randint(0,region.max[1]))
    while pipregion(region,directions,here)==0:
        here=(random.randint(0,region.max[0]),random.randint(0,region.max[1]))
    digslateshere(c, region, polygons, slates, directions, step, here, packedpairs)
    digslateshere(c, region, polygons, slates, directions, step, here, packedpairs)
    wepackaslate=fillwithslateshere(c,region,polygons,slates,directions,npositions,indicestopack, ratio, ntries,here)
    return here,wepackaslate


def digandpackaroundvertexslateconflict(positions,c,region,polygons,slates,directions,step,indicestopack,para,radiustodig):
    #print("digandpackaroundvertex")
    n=len(region.vertices)
    k=random.randint(0,n-1)
    here=region.vertices[k]  
    
    digHerewithradius(c,region,polygons,directions,step,here,para,False,radiustodig)
    digHerewithradius(c,region,polygons,directions,step,here,para,False,radiustodig)
    
    wepackaslate=searchtopackslatewithconflict(positions,c,region,polygons,slates,directions,indicestopack, para,here,step,radiustodig)
    return here,wepackaslate


def digandpacksomewhereslateconflict(positions,c,region,polygons,slates,directions,step,indicestopack,para,radiustodig):
    #print("digandpackaroundvertex")
    n=len(region.vertices)
    here=(random.randint(0,region.max[0]),random.randint(0,region.max[1]))
    while pipregion(region,directions,here)==0:
        here=(random.randint(0,region.max[0]),random.randint(0,region.max[1]))
        
    digHerewithradius(c,region,polygons,directions,step,here,para,True,radiustodig)
    digHerewithradius(c,region,polygons,directions,step,here,para,True,radiustodig)
    
    wepackaslate=searchtopackslatewithconflict(positions,c,region,polygons,slates,directions,indicestopack, para,here,step,radiustodig)
    return here,wepackaslate
                 

###################### 6 packing slates ######################

def packingslates(region,polygons,slates,directions,para):
    print("start packingslates")
    #preprocess inputPolygons by ordering them according a criterion
    for sla in slates:
        t=thicknessslate(polygons,sla)
        meanthickness=0
        for i in sla.ipolygons:
            meanthickness=meanthickness+thickness(polygons[i].vertices)
        meanthickness=meanthickness/len(sla.ipolygons)
        #if meanthickness>5:
        #    sla.weight=t*len(sla.ipolygons)
        #if len(sla.ipolygons)>1:
        #    sla.weight=sla.weight*math.sqrt(len(sla.ipolygons))
    
    if para.optionfill<10:
        slates.sort(key=lambda sla:score(polygons,sla,para),reverse=True)
    print(f"ordering {para.estimationstyle}")
    print(f"optonfill {para.optionfill}")
    
    fillinslates(polygons,slates)# don't change the order of the slates after this point... or make it carefully...
    nx=para.nxcage
    ny=para.nycage
    c=buildcage(region, polygons, directions, nx, ny)
           
    #start the packing
    packedpairs=[]
    indicestopack=[]
    for i in range(len(slates)):
        if slates[i].left>0:
            #we check the vale left...
            for iii in slates[i].ipolygons:
                if polygons[iii].positions==None:
                    if polygons[iii].quantity<slates[i].left:
                        slates[i].left=polygons[iii].quantity
                else:
                    if polygons[iii].quantity-len(polygons[iii].positions)<slates[i].left:
                        slates[i].left=polygons[iii].quantity-len(polygons[iii].positions)
                    
        if slates[i].left>0:        
            indicestopack.append(i)
        if slates[i].positions!=None:
            for j in range(len(slates[i].positions)):
                packedpairs.append((i,j))
            
    #main computation
    step=fill(c, region, polygons, slates, directions,  indicestopack, packedpairs, para)
    cost,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons) 
    print(f"current cost = {cost}\n")            
    #we remove the composed slates to keep only the polygons....
    k=len(slates)-1
    while k>0:
        if slates[k].positions==None:
            if len(slates[k].ipolygons)>1:
                slates.pop(k)
        else:
            if len(slates[k].positions)==0 and len(slates[k].ipolygons)>1:
                slates.pop(k)
        k=k-1
    #We recompute the packedpairs and indicestopack
    packedpairs=[]
    indicestopack=[]
    for i in range(len(slates)):
        if slates[i].left>0:
            indicestopack.append(i)
        if slates[i].positions!=None:
            for j in range(len(slates[i].positions)):
                packedpairs.append((i,j))
    fillinslates(polygons,slates)
    
    loop=0
    ndigbeforestop=para.ndigbeforestop
    ratio=para.ratiodigvertex
    ntries=para.ntries
    npositions=para.npositions
    print(f"round {loop+1}  with {npositions} positions")      
    #checkcrossings(polygons,directions)
    count=10000 
    while count<ndigbeforestop: 
        findone=False
        here1,wepackaslate=digandpackaroundvertex(c, region, polygons, slates, directions, step, indicestopack, packedpairs, ratio, npositions, ntries)
        if wepackaslate==1:
            cost,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons) 
            print(f"aroundvertex: current cost = {cost}")
            findone=True
        here2,wepackaslate=digandpacksomewhere(c,region,polygons,slates,directions,step,indicestopack,packedpairs,ratio, npositions,ntries)
        
        if wepackaslate==1:
            cost,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons) 
            print(f"anywhere: current cost = {cost}")
            findone=True
        if findone==True:
            count=0
        else:
            count=count+1
    print("end packingslates")


def runpackingslates(shortname,para):
    print("start testpackingslates")
    #name=f"examples/{shortname}.cgshop2024_instance.json"
    fullname=f"instances/{shortname}.cgshop2024_instance.json"
    region,polygons,directions=load(fullname)
    xmax=max(vertex[0] for vertex in region.vertices)
    ymax=max(vertex[1] for vertex in region.vertices)
    grid=[20,150,50,20]
    scale=max(xmax/grid[1],ymax/grid[2])
    grid[1]=xmax/scale+100
    #packing
    npositions=500
    slates=[]
    for i in range(len(polygons)):
        sla=slate(polygons,i,i)
        (x,y)=polygons[i].centroid
        sla.x[0]=-x
        sla.x[0]=-y
        slates.append(sla)
    #function 
    t0=time.time()
    packingslates(region,polygons,slates,directions,para)
    t1=time.time()
    #results
    cost,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons)    
    writeresults(shortname,region,polygons,t1-t0,para,"packingslates run")
    print("end testpackingslates")
    

def runexp():
    names,upperbounds=loadnamesandboudsofchallenge()
    
    estimationstyle=2  #parameter to choose the order of the polygons
    #int from 0 to 8 (see scorefromfeatures)
    # 0 cost
    # 1 cost but 1 over 4 is randomly "downgraded"
    # 2 pow(cost,costexponent)/area polygon
    # 3 pow(cost,costexponent)*random.gauss(1, 0.05)/area polygon
    # 4 pow(cost,costexponent)*random.gauss(1, 0.05)/(area polygon+area convex hull)
    # 5 pow(cost,costexponent)*random.gauss(1, 0.05)/area convex hull
    # 6 pow(cost,costexponent)*random.gauss(1, 0.05)/(area polygon + diamter²/5)
    # 7 t=is the ratio diameter / thickness in the orthogonal direction of the diamater
    #    (1+coeffthickness*t)*pow(cost,costexponent)*random.gauss(1, 0.005)/a 
    # 8 t

    coeffthickness=0.5

    optionfill=3 #int from 0 to 6 (see fill)
    #0: random
    #1: uniform push in a random unique direction
    #2: normal to diameter
    #3: normal to diameter: (left for thin polygons / right diameter) 
    #4: as 3 but with noise for the right side
    #5: normalmix (left diameter for thin polygons / right longest edge)
    #6: normal to the longest edge (randomly to the left or to the right)
    #7: diameter to the left/random to the right
    #8: designed for satris with longest edges, and according to thickness
    #9: designed for atris with longest edges, and according to thickness

    costexponent=1.5 #1.1 or 1.2 or may be more
    npositions=500 #500 or 1000 or more
    loopmax=2 #1: no optimization, 2 or more: a bit of optimization
    ndigbeforestop=5 #digs holes and tries to pack in the holes... could be increase for optimizing small solutions...
    ratiodigvertex=0.15
    nxcage=20 #number of cells to minimize the number of crossing tests
    nycage=20
    ntries=10
    
    threshold=0#if we want to reject thefill solutions which are too bad... fix the threshold

    
    para=parameterspacking2(estimationstyle,optionfill,costexponent,npositions,loopmax,ndigbeforestop,ratiodigvertex,nxcage,nycage,ntries,coeffthickness)
    

    startnumber=49
    for n in range(startnumber,180):
        for i in range(5):
            runpackingslates(names[n],para)
     
#runexp()


   
    


