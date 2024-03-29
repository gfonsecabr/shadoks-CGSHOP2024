import statistics
from packingslates import *
from packing import *

wanttoaddoptimization=True
withdrawinginsvg=False
thinthreshold=6
strongcollapse=True


####################### Execution in console mode ######################

##### for computing NEW solutions ##########

# python3 factory.py solutionrepository instancefilename level  /  python3 factory.py solutions instance46.json 5
#  3 arguments (third -the level- is an integer => 0 or 1 to skip preprocessing of groups of at most "level" items)
#  => computes a solution (from scratch) and writes the solutions in "solutionrepository"
#     the computation uses slates preprocessing (groups of items with at most [level] items)
#     no timelimit is given as fourth argument... Then the algorithm will not terminate. It updates the solutions when better ones are found

# python3 factory.py solutionrepository instancefilename level timelimit  /  python3 factory.py solutions instance46.json 5 10000
#  4 arguments (third -the level- is an integer => 0 or 1 to skip preprocessing of groups of at most "level" items)
#  => computes a solution (from scratch) and writes the solutions in solutionrepository
#     the computation uses slates preprocessing (groups of items with at most [level] items)
#     timelimit (in seconds) is given as fourth argument... We don't stop everything when time is achieved, then the algorithm can use more time (but it breaks the main loops)

##### for optimizing a PREVIOUS solution ##########

# python3 factory.py solutionrepository solutionfilename instancefilename /  python3 factory.py solutions solution46toimprove.json instance46.json 
#  3 arguments (third is a .json filename)
#  => optimizes the solution "solutionfilename" and writes the solutions in "solutionrepository"
#     no timelimit is given as fourth argument... Then the algorithm will not terminate. It updates the solutions when better ones are found

# python3 factory.py solutionrepository solutionfilename instancefilename timelimit /  python3 factory.py solutions solution46toimprove.json instance46.json 10000
#  4 arguments (third is a .json filename)
#  => optimizes the solution "solutionfilename" and writes the solutions in "solutionrepository"
#     timelimit(in seconds) is given as fourth argument... We don't stop everything when time is achieved, then the algorithm can use more time (but it breaks the main loops)


############################# Plan #####################################

# 0  factory functions 
# 1  generation
# 2  graph of items adjacency
# 3  factory
# 4  packfactory = high level function with 
#                            1 slate generation
#                            2 packinbg the slates
#                            3 some optimizations
# 5  parameters choice before execution
# 6  main function = pack
# 7  execution in console mode




########################## 0 factory functions ########################

####################### How to build slates by combining polygons ############################

# how do we compute a score from an a combination

def geometricfeatureslatepluspolygon(polygons,inewpolygon,newpolygonposition,hull1):
    vertices=hull1.copy()
    test=True
    for v in polygons[inewpolygon].vertices:
        w=(v[0]+newpolygonposition[0],v[1]+newpolygonposition[1])
        if w not in vertices:
            vertices.append(w)
    hull2=convexHull(vertices)  
    areahull2=areaPolygon(hull2)
    d2=diameter(hull2)
    return areahull2,d2   

########################## functions to test packability ######################

# We test whether a slate can be packed... in the region 

def isaslatepackablehere(region,directions,polygons,sla,slaposition):
    for ii in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[ii]
        position=(slaposition[0]+sla.x[ii],slaposition[1]+sla.y[ii])
        if inConvexRegion(polygons[ipolygon],position,region,directions)!=1:
            return False
    return True 

def isaslatepackable(region,directions,polygons,sla,slapositions):
    for slaposition in slapositions:
        if isaslatepackablehere(region,directions,polygons,sla,slaposition)==1:
            return True
    return False
       
# We test if a slate plus a polygon can be packed in the region... for a given set of input positions 

def areslateandpolygonpackable(region,directions,polygons,sla,slapositions,inewpolygon,polygonpositioninslate):
    #print(directions) 
    stillNotPacked=True
    j=0
    while stillNotPacked and j<len(slapositions):
        slaposition=slapositions[j]
        positioniscorrect=True
        p0=(slaposition[0]+polygonpositioninslate[0],slaposition[1]+polygonpositioninslate[1])
        if inConvexRegion(polygons[inewpolygon],p0,region,directions)==False:
            #print("bad")
            positioniscorrect=False
        if positioniscorrect==True:
            #print("not bad")
            result=isaslatepackablehere(region,directions,polygons,sla,slaposition)
            if result==False:
                positioniscorrect=False
        if positioniscorrect==True:
            return True,position
        j=j+1
    return False,None

########################## drop and moving functions of a polygon in a slate ######################

def droppolygoninslate(directions,polygons,sla,inewpolygon,polygonpositioninslate):
    positioniscorrect=True
    for ii in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[ii]
        position=(sla.x[ii],sla.y[ii])
        if crossingPolygons(polygons[ipolygon],polygons[inewpolygon],position,polygonpositioninslate,directions)==1:
            return False
    return True

def movepolygoninslate(directions,polygons,sla,vector,inewpolygon,position0):
    print(f"\nmoves the polygon {inewpolygon} in the vector direction {vector} from position {position0}")
    if vector==(0,0):
        return position0
    loop=1 
    position=(position0[0],position0[1])
    newvector=vector
    count=0
    while loop and count<100:
        newposition=(position[0]+newvector[0],position[1]+newvector[1])
        if norm(newposition)>=norm(position):
            return position
        print(f"let us try this position: {newposition} with translation {newvector}")
        result=droppolygoninslate(directions,polygons,sla,inewpolygon,newposition)
        if result==True:
            print("find new position\n")
            position=newposition
            count=count+1
        else:
            print("try again")
            count=count+1 
            if newvector[0]%2==0 and newvector[1]%2==0:
                newvector=(int(newvector[0]/2),int(newvector[1]/2)) 
                if newvector==(0,0):
                    return position
            else:
                return position
    return position



def mergeslatepolygon(level,region,directions,polygons,sla,inewpolygon,parafactory,parascore):
    #hullcoeff=parafactory.hullcoeff
    #we compute the mean cost of the polygons of the slate
    if strongcollapse==True:
        relaxationfactor=1
        gridsize=50
    else:
        relaxationfactor=1
        gridsize=parafactory.mergegrid
    meancost=sla.cost/len(sla.ipolygons)   
    meanarea=sla.area/len(sla.ipolygons)         
    if meancost>4*relaxationfactor*polygons[inewpolygon].cost or 4*relaxationfactor*sla.cost<polygons[inewpolygon].cost or meanarea>5*relaxationfactor*polygons[inewpolygon].area or  4*relaxationfactor*sla.area<polygons[inewpolygon].area:
        #print(meancost)
        #print(2.5*polygons[inewpolygon].cost)
        #print(f"not interesting association for {inewpolygon} and {sla.ipolygons} with quantities {polygons[inewpolygon].quantity}")
        #wait=input("wait")
        return -15,(0,0)

    #We prepare the computations of the score by computings the vertices of the slate and some features:   
    x=0 
    y=0
    hull1= hullslate(polygons,sla)
    areahull1=areaPolygon(hull1)
    ratio1=areahull1/sla.area
    d1=diameter(hull1) 
    d2=diameter(polygons[inewpolygon].vertices)
    
    x0=min(p[0] for p in hull1)
    x1=max(p[0] for p in hull1)
    y0=min(p[1] for p in hull1)
    y1=max(p[1] for p in hull1)
    xmin=polygons[inewpolygon].min[0]
    ymin=polygons[inewpolygon].min[1]
    xmax=polygons[inewpolygon].max[0]
    ymax=polygons[inewpolygon].max[1]
    
    #the features that we try to minimize and store for comparisons
    min_centroiddistance=region.max[0]+region.max[1]
    min_hullarea=100000000*region.max[0]*region.max[1]
    position_hullarea=(0,0)
    positionfound=False
    count=0
    i=0
    i0=0
    j0=0
    
    #areabox [x0-xmax , x1+xmin ] x [y0-ymax, y1+ymin]
    if gridsize>0:
        a=(x1+xmin-x0+xmax)*(y1+ymin-y0+ymax)
        stepx=1+(x1+xmin-x0+xmax)//gridsize
        stepy=1+(y1-ymin-y0+ymax)//gridsize
        
        
        for x in range(x0-xmax,x1+xmin+stepx,stepx):
            j=0
            for y in range(y0-ymax,y1-ymin+stepy,stepy):
                count=count+1
                position=(x,y)
                result=droppolygoninslate(directions,polygons,sla,inewpolygon,position)
                if result==True:
                    positionfound=True
                    #Let's compute the score...
                    newareahull,newdiameter=geometricfeatureslatepluspolygon(polygons,inewpolygon,position,hull1)
                    pp=(position[0]+polygons[inewpolygon].centroid[0],position[1]+polygons[inewpolygon].centroid[1])
                    newdistancecentroid=norm(pp)
                    #print((newarea,newdiameter,newdistancecentroid))
                    if newdistancecentroid<min_centroiddistance:
                        min_centroiddistance=newdistancecentroid
                        position_centroiddistance=position
                        i0=i
                        j0=j
                        #print(f"{(i0,j0)} closer centroids")
                        hullarea_mincentroid=newareahull
                    elif newdistancecentroid<1.01*min_centroiddistance and newareahull<0.99*hullarea_mincentroid:
                        min_centroiddistance=newdistancecentroid
                        position_centroiddistance=position
                        i0=i
                        j0=j
                        #print(f"{(i0,j0)} relaxed closer centroid ")
                        hullarea_mincentroid=newareahull
                    if newareahull<min_hullarea:
                        min_hullarea=newareahull
                        position_hullarea=position
                        #print(f"{(i0,j0)} relaxed lower hull area")
                    elif newareahull<1.01*min_hullarea and newdistancecentroid<0.99*norm((position_hullarea[0]+polygons[inewpolygon].centroid[0],position_hullarea[1]+polygons[inewpolygon].centroid[1])):
                        min_hullarea=newareahull
                        position_hullarea=position
                        #print(f"{(i0,j0)} relaxed lower hull area")
                j=j+1
            i=i+1
    #We try now some specific positions:
    for ii in range(len(sla.ipolygons)):
        ipolygon=sla.ipolygons[ii]
        slapolygon=polygons[ipolygon]
        x=sla.x[ii]
        y=sla.y[ii]
        for v in slapolygon.vertices:
            vertex=(x+v[0],y+v[1])
            for newvertex in polygons[inewpolygon].vertices:
                #we choose the position putting the new vertex on the vertex
                #The position has to be 
                position=(vertex[0]-newvertex[0],vertex[1]-newvertex[1])
                #the we search whether it is better or not...
                result=droppolygoninslate(directions,polygons,sla,inewpolygon,position)
                if result==True:
                    positionfound=True
                    #Let's compute the score...
                    
                    #print("hull1 has length {len(hull1)}")
                    #print(hull1)
                    
                    
                    newareahull,newdiameter=geometricfeatureslatepluspolygon(polygons,inewpolygon,position,hull1)
                    pp=(position[0]+polygons[inewpolygon].centroid[0],position[1]+polygons[inewpolygon].centroid[1])
                    newdistancecentroid=norm(pp)
                    if newareahull<min_hullarea:
                        min_hullarea=newareahull
                        position_hullarea=position
                        #print(f"position={position} new min (relaxed) area {min_hullarea}") 
                    elif newareahull<1.01*min_hullarea and newdistancecentroid<0.99*norm((position_hullarea[0]+polygons[inewpolygon].centroid[0],position_hullarea[1]+polygons[inewpolygon].centroid[1])):
                        min_hullarea=newareahull
                        position_hullarea=position
                        #print(f"position={position} new min (relaxed) area {min_hullarea}") 
    
    area2=polygons[inewpolygon].area
    hull2=convexHull(polygons[inewpolygon].vertices)
    areahull2=areaPolygon(hull2)
    ratio2=areahull2/area2
    
    
    #test packability
    for v in polygons[inewpolygon].vertices:
        vv=(v[0]+position_hullarea[0],v[1]+position_hullarea[1])
        if vv not in hull1:
            hull1.append(vv)
    mini,maxi=dHull(directions,hull1)
    canbepacked=1 
    for i in range(len(directions)):
        if maxi[i]-mini[i]>region.max[i]-region.min[i]:
            #print("slate cannot be packed")
            canbepacked=0
    
    area2=polygons[inewpolygon].area
    newareahull,newdiameter=geometricfeatureslatepluspolygon(polygons,inewpolygon,position_hullarea,hull1)
    newratio=newareahull/(sla.area+area2)
    #print(f"ratio={newratio}  from   {newareahull} / {sla.area+area2}")

    if level==1:
        hullcoeff=parafactory.hullcoeffs[1]
    else:
        hullcoeff=parafactory.hullcoeffs[2]
        
    t=thickness(hull1)
    if t>thinthreshold:
        relaxationfactor=5
        
    if canbepacked==1 and newratio<hullcoeff*relaxationfactor*(ratio1+ratio2)/2 and newratio<relaxationfactor*parafactory.hullcoeffs[0]:
        #newareahull=areaPolygon(hull1) useless
        #for long polygons and long slates, we avoid them to be packed in the length
        if d1*d1/sla.area>3 and d2*d2/area2>3:
            if newdiameter>0.75*(d1+d2):
                relaxationfactor=1
                return -2,(0,0)
        
        
        newd=diameter(hull1)
        
        #print(position_hullarea)
        return scorefromfeatures(sla.cost+polygons[inewpolygon].cost,sla.area+area2,newareahull,newd,t,parascore),position_hullarea
    else:
        relaxationfactor=1
        return -5,(0,0)
    




########################################## 1 generation ###################################

class parametersfactory:
    def __init__(self,a,b,c,d,e,f,g):
        #option for building the graph
        self.optiongeneration=a
        self.optionpartitionsize=b
        self.coeffdistanceforedgesmerging=c
        #options for slate generation
        self.hullcoeffs=d
        self.mergegrid=e
        self.level=f
        self.nselection=g
    def __str__(self): 
        w=f"optiongeneration={self.optiongeneration} "
        w=w+f"optionpartitionsize={self.optionpartitionsize} "
        w=w+f"coeffdistanceforedgesmerging={self.coeffdistanceforedgesmerging} "
        w=w+f"hullcoeffs={self.hullcoeffs} "
        w=w+f"mergegrid={self.mergegrid} "
        w=w+f"level={self.level} "
        w=w+f"nselection={self.nselection} "
        return w
    
    
def checkcrossingsinslate(polygons,sla):
    for ii in range(len(sla.ipolygons)-1):
        ipolygon=sla.ipolygons[ii]
        positioni=(sla.x[ii],sla.y[ii])
        for jj in range(ii, len(sla.ipolygons)):
            if jj!=ii:
                jpolygon=sla.ipolygons[jj]
                positionj=(sla.x[jj],sla.y[jj])
                if crossingPolygons(polygons[ipolygon],polygons[jpolygon],positioni,positionj,directions)==1:
                    print("checkcrossings detects two crossing polygons")
                    print(f"indices are {ii} and {jj}")
                    print(f"quantities are {polygons[ipolygon].quantity} and {polygons[jpolygon].quantity}")
                    print(f"identities are {polygons[ipolygon].id} and {polygons[jpolygon].id}")
                    print(f"positions are {positioni} and {positionj}")
                    crossingPolygonsWithComments(polygons[ipolygon],polygons[jpolygon],positioni,positionj,directions)
                    return False
    return True

    
    

def initializeslates(polygons):
    slates=[]
    newidentity=0
    medianarea=statistics.median([p.area for p in polygons])
    mediandiameter=statistics.median([diameter(p.vertices) for p in polygons])
        #print(f"medianarea and diameter= {medianarea}  and {mediandiameter} ")
    
    count=0
    for i in range(len(polygons)):
            sla=slate(polygons,i,i)
            slates.append(sla)
            newidentity=newidentity+1
    #print(f"{count} small polygons ({int(100*count/len(polygons))}%) not added in factory")
    return slates


def slatesgeneration(pairs,region,directions,polygons,level,parafactory,parascore,startid,timelimit):
    print(f"slategeneration of level {level} with timelimit={timelimit}")
    #to choose the identity of the new slates
    slatesX=[]
    slatesX.append(initializeslates(polygons))         
    newidentity=startid
    n=1 
    nselection=parafactory.nselection
    
    while n<=level-1 and len(slatesX[n-1])>0 and len(pairs)>0 and time.time()-time0<=timelimit:
            print(f"generation {n+1}")
            #we use slategenerations[n-1] and the polygons to generate a new generation of slates...
            slates=[]
            bestslatesid=[]
            visitedindices=[]             
            for sla in slatesX[n-1]:
                    ipolygonstoconsider=[]
                    for islapolygon in sla.ipolygons:
                        for p in pairs:
                            if polygons[islapolygon].id==p[0]:
                                if ipolygonstoconsider not in ipolygonstoconsider:
                                    ipolygonstoconsider.append(p[1])
                            if polygons[islapolygon].id==p[1]:
                                if ipolygonstoconsider not in ipolygonstoconsider:
                                    ipolygonstoconsider.append(p[0])
  
                    for inewpolygon in ipolygonstoconsider:
                        #We test whether the new slate will have a higher cost to enter in the list.
                        count=0
                        for k in sla.ipolygons:
                            if k==inewpolygon:
                                count=count+1 
                        if count<polygons[inewpolygon].quantity:
                            #we test whether we did not already compute this combination
                            found=False
                            listipolygons=sla.ipolygons.copy()
                            listipolygons.append(inewpolygon)
                            listipolygons.sort()
                            if listipolygons in visitedindices:
                                    found=True
                                    #print(f"redondant slate {listipolygons}")
                            else:
                               visitedindices.append(listipolygons)
                               #print(f"first visisted {listipolygons}")
                            if found==False:
                                score,newp=mergeslatepolygon(n,region,directions,polygons,sla,inewpolygon,parafactory,parascore)
                                #print(score)
                                if len(slates)==nselection:
                                    if score<bestslatesid[nselection-1][1]:
                                        score=0
                                        #don't go further, the score is not better
                                if score>0:
                                    #we don't want twice the same polygon in a slate...
                                    #we search for the slates of the selection in conflict with the new slate
                                    concernedslates=[]
                                    for slap in slates:
                                        if inewpolygon in slap.ipolygons or sla.ipolygons[0] in slap.ipolygons:
                                            concernedslates.append(slap.identity)
                                    #print(f"concernedslates={concernedslates}")
                                    if len(concernedslates)>0:
                                        identitiestoremove=[]
                                        weaddit=True
                                        for b in bestslatesid:
                                            scoretocompare=b[1]
                                            if scoretocompare>score:
                                                if b[0] in concernedslates:
                                                    #the we do nothing. The new slate would destroy a better slate
                                                    weaddit=False
                                                    break
                                            else:
                                                break
                                        if weaddit==True:
                                            for b in bestslatesid:
                                                if b[0] in concernedslates:
                                                    #this slate has to be removed
                                                    identitiestoremove.append(b)
                                        if weaddit==True:   
                                            #we vreate the new slate and add it...
                                            newslate=makeacopy(polygons,sla,newidentity)
                                            addpolygoninslate(newslate,polygons,inewpolygon,newp)
                                            slates.append(newslate)
                                            #print(f"g={n+1}: new slate {newidentity}: {newslate.ipolygons} cost={newslate.cost}")
                                            bestslatesid.append((newidentity,score))
                                            newidentity=newidentity+1
                                            for b in identitiestoremove:   
                                                #print(f"remove {b}")
                                                for ii in range(len(slates)):
                                                    if slates[ii].identity==b[0]:
                                                        #we remove this slate from slates and replace it by the new slate
                                                        bestslatesid.remove(b)
                                                        #print(f"removes {slates[ii].ipolygons} to add {newslate.ipolygons}")
                                                        slates.pop(ii)
                                                        break  
                                            bestslatesid.sort(key=lambda pair:pair[1], reverse=True)                                            
                                    else: 
                                        if len(slates)<nselection:
                                            newslate=makeacopy(polygons,sla,newidentity)
                                            addpolygoninslate(newslate,polygons,inewpolygon,newp)
                                            #print(f"g={n+1}: new slate {newidentity}: {newslate.ipolygons} cost={newslate.cost}")                                        
                                            slates.append(newslate)
                                            bestslatesid.append((newidentity,score))
                                            bestslatesid.sort(key=lambda pair:pair[1], reverse=True)
                                            newidentity=newidentity+1  
                                        else:
                                            #we have to remove the last slate
                                            newslate=makeacopy(polygons,sla,newidentity)
                                            addpolygoninslate(newslate,polygons,inewpolygon,newp)
                                            #print(f"g={n+1}: new slate {newidentity}: {newslate.ipolygons} cost={newslate.cost}")
                                            newidentity=newidentity+1
                                            #we search the slate with the 
                                            identity=bestslatesid[nselection-1][0]
                                            for ii in range(nselection):
                                                if slates[ii].identity==identity:
                                                    #we remove this slate from slates and replace it by the new slate
                                                    slates[ii]=newslate
                                                    bestslatesid[nselection-1]=(newidentity-1,score)
                                                    bestslatesid.sort(key=lambda pair:pair[1], reverse=True)

            if len(slates)>0:
                slatesX.append(slates) 
            else:
                break
            n=n+1
    finalslates=[]
    for n in range(len(slatesX)):
        if slatesX[n]!=None and n>0:
            finalslates=finalslates+slatesX[n]
    return finalslates


#We want to generate more slates by avoidin the fact that 0,1 is deleted by 1,2 which is deleted by 2,3, which is deleted by 3,4...

def slatesgenerationprime(pairs,region,directions,polygons,level,parafactory,parascore,startid,timelimit):
    time0=time.time()
    print(f"slategeneration of level {level} with timelimit={timelimit}")
    slatesX=[initializeslates(polygons)]
    
    newidentity=startid
    n=1 
    nselection=parafactory.nselection
    if parafactory.optiongeneration==1:
        bestslateidscoreandslate=[(-1,0,None) for i in range(len(polygons))]
    while n<=level-1 and len(slatesX[n-1])>0 and time.time()-time0<=timelimit:
            print(f"generation {n+1}")
            #we use slategenerations[n-1] and the polygons to generate a new generation of slates...
            if parafactory.optiongeneration==2:
                bestslateidscoreandslate=[(-1,0,None) for i in range(len(polygons))]
            slates=[]
            bestslatesid=[]
            visitedindices=[]             
            for sla in slatesX[n-1]:
                    ipolygonstoconsider=[]
                    for islapolygon in sla.ipolygons:
                        for p in pairs:
                            if polygons[islapolygon].id==p[0]:
                                if ipolygonstoconsider not in ipolygonstoconsider:
                                    ipolygonstoconsider.append(p[1])
                            if polygons[islapolygon].id==p[1]:
                                if ipolygonstoconsider not in ipolygonstoconsider:
                                    ipolygonstoconsider.append(p[0])
  
                    for inewpolygon in ipolygonstoconsider:
                        
                        #We test whether the new slate will have a higher cost to enter in the list.
                        count=0
                        for k in sla.ipolygons:
                            if k==inewpolygon:
                                count=count+1 
                        if count<polygons[inewpolygon].quantity:
                            #we test whether we did not already compute this combination
                            found=False
                            listipolygons=sla.ipolygons.copy()
                            listipolygons.append(inewpolygon)
                            listipolygons.sort()
                            if listipolygons in visitedindices:
                                    found=True
                                    #print(f"redondant slate {listipolygons}")
                            else:
                               visitedindices.append(listipolygons)
                               #print(f"first visisted {listipolygons}")
                            if found==False:
                                #print(f"merge {sla.ipolygons} with {inewpolygon}")
                                score,newp=mergeslatepolygon(n,region,directions,polygons,sla,inewpolygon,parafactory,parascore)
                                #print(score)
                                wecontinue=0
                                for ii in sla.ipolygons:
                                    if score>bestslateidscoreandslate[ii][1]:
                                        wecontinue=True
                                        break
                                if wecontinue==False:
                                    score=0
                                    #don't go further, the score does not improve anything
                                if score>0:
                                    #we build the slate...
                                    newslate=makeacopy(polygons,sla,newidentity)
                                    addpolygoninslate(newslate,polygons,inewpolygon,newp)
                                    #print(f"g={n+1}: new slate {newidentity}: {newslate.ipolygons} cost={newslate.cost}") 
                                    checkcrossingsinslate(polygons,newslate)
                                    for ii in sla.ipolygons:
                                        if score>bestslateidscoreandslate[ii][1]:
                                            bestslateidscoreandslate[ii]=(newidentity,score,newslate)
                                    newidentity=newidentity+1
            alreadyaddedids=[]
            for ii in range(len(polygons)):
                 if bestslateidscoreandslate[ii][0]!=-1:
                     if parafactory.optiongeneration==2:
                         if bestslateidscoreandslate[ii][0] not in alreadyaddedids:
                             alreadyaddedids.append(bestslateidscoreandslate[ii][0])
                             slates.append(bestslateidscoreandslate[ii][2])
                     if parafactory.optiongeneration==1:
                         if len(bestslateidscoreandslate[ii][2].ipolygons)==n+1:
                             if bestslateidscoreandslate[ii][0] not in alreadyaddedids:
                                 alreadyaddedids.append(bestslateidscoreandslate[ii][0])
                                 slates.append(bestslateidscoreandslate[ii][2])
                     
            if len(slates)>0:
                slatesX.append(slates) 
            else:
                break
            n=n+1
    finalslates=[]
    for n in range(len(slatesX)):
        if slatesX[n]!=None and n>0:
            finalslates=finalslates+slatesX[n]
    return finalslates

####################################### 2 graph of adjacency #######################################


    
########### partition functions ###############
 
#part cuts the set of polygons in subsets of equal size (parafactory.optionpartitionsize)
    
def part(polygons,parafactory):
    #print("start buildgraph")
    polygons.sort(key=lambda p:p.id)
    partition=[]
    polygons.sort(key=lambda p:p.cost, reverse=True)
    #polygons.sort(key=lambda p:diameter(p.vertices), reverse=True)
    #polygons.sort(key=lambda p:normaltodiameterforfactory(p.vertices), reverse=True)
    
    newsetofindices=[]
    for i in range(len(polygons)):
            newsetofindices.append(polygons[i].id)
            if len(newsetofindices)%parafactory.optionpartitionsize==0 and len(newsetofindices)>0:
                partition.append(newsetofindices)
                newsetofindices=[]
                #just to test
    partition.append(newsetofindices)
    print(f"the partition has length {len(partition)}")
    return partition
   
def generalpartition(polygons,parafactory):
    #general
    partition=[]
    newsetofindices=[]
    for i in range(len(polygons)):
        newsetofindices.append(i)
        if i//parafactory.optionpartitionsize!=(i-1)//parafactory.optionpartitionsize and i>0:
            partition.append(newsetofindices)
            newsetofindices=[]
            #just to test
    partition.append(newsetofindices)
    #print(partition)
    return partition


#################### graphs ########################


def gluethinthin(polygons):
    polygons.sort(key=lambda p:p.id)
    thin=[]
    for p in polygons:
        if thickness(p.vertices)>thinthreshold:
            #we compute the direction of the longest edge...
            a,b=longestedgex(simplify(p.vertices))
            thin.append((a,b,p.id))
    thin.sort()
    #print(thin)
    pairs=[]
    n=len(thin) 
    for i in range(len(thin)):
        startfromi=False
        for p in polygons:
            if p.id==thin[i]:
                q=p.quantity
                if q>1:
                    startfromi=True
                break
        if startfromi==True:
            i0=i
        else:
            i0=i+1
        for j in range(i0,i+10):
            if thin[j%n][1]*thin[i][1]<0:#we want the edges to be in opposite directions
                pairs.append((polygons[thin[i][2]].id,polygons[thin[j%n][2]].id))
    print(f"graph of pairs of longlong polygons of size : {len(pairs)}")
    return pairs

def binary(corners,doublevector):
    left, right = 0, len(corners) - 1
    mid=0
    while left <= right:
        mid = left + (right - left) // 2

        if corners[mid][0] == doublevector:
            mid1=max(0,mid-10)
            mid2=min(len(corners)-1,mid1+11)
            return mid1,mid2
        elif corners[mid][0]< doublevector:
            left = mid + 1
        else:
            right = mid - 1
    mid1=max(0,mid-10)
    mid2=min(len(corners)-1,mid1+11)
    return mid1,mid2


def glueconcav(polygons):
    pairs=[]
    polygons.sort(key=lambda p:p.id)
    corners=[]
    for poly in polygons:
        #print(p.id)
        p=simplify(poly.vertices)
        n=len(p)
        
        for i in range(n):
            
            #edges adjacent to non convex vertices.... 
            i0=(i-1)%n
            i2=(i+1)%n
            #print(f"polygon identity = {poly.id} => vertex {i}  vectors {int((p[i][0]-p[i0][0])/10000)} , {int((p[i][1]-p[i0][1])/10000)} and {int((p[i2][0]-p[i][0])/10000)} , {int((p[i2][1]-p[i][1])/10000)}")
            if area(p[i0],p[i],p[i2])<0:
                #concave vertex
                
                if angleTriangle(p[i0],p[i],p[i2])<0.99*math.pi:
                    v=(p[i0][0]-p[i][0],p[i0][1]-p[i][1])
                    u=(p[i][0]-p[i2][0],p[i][1]-p[i2][1])
                    corners.append(((u,v),poly.id))
                    #print(f"corner for {poly.id} at vertex {i} with angle {int(180*angleTriangle(p[i0],p[i],p[i2])/math.pi)}")
    print(f"corners length= {len(corners)}")
    corners.sort()
    k=len(corners)
    for poly in polygons:
        p=simplify(poly.vertices)
        n=len(p)
        for i in range(n):
            i0=(i-1)%n
            i2=(i+1)%n
            u=(p[i][0]-p[i0][0],p[i][1]-p[i0][1])
            v=(p[i2][0]-p[i][0],p[i2][1]-p[i][1])
            index1,index2=binary(corners,(u,v))
            nou=norm(u)
            nov=norm(v)
            #print(f"{index1,index2}")
            for ii in range(index1,index2):               
                if distance(u,corners[ii][0][0])<0.1*nou:                    
                    if distance(v,corners[ii][0][1])<0.1*nov:
                        pair=(corners[ii][1],poly.id)
                        if pair not in pairs:
                            pairs.append(pair)
    corners.sort()
    print(f"cornergraph of length {len(pairs)}")
    return pairs

def gluefromlist(polygons,indiceslist,parafactory):
    print(f"glue from list of size {len(indiceslist)}")
    if len(indiceslist)>0: 
        
        polygons.sort(key=lambda p:p.id)
        chordsandindices=[]
        pairs=[]
        for k in indiceslist:
            points=simplify(polygons[k].vertices)
            diam=diameter(points)
            n=len(points)
            for i in range(n):
                ii=(i+1)%n
                chord=(points[ii][0]-points[i][0],points[ii][1]-points[i][1])
                r=norm(chord)
                wedecidetoconsiderthisedge=False
                if r>0.3*diam:#0.3
                    wedecidetoconsiderthisedge=True
                #edges adjacent to non convex vertices.... 
                iminus0=(i-1)%n
                i1=(i+1)%n
                i2=(i+2)%n
                if areaTriangle(points[iminus0],points[i],points[i1])<0 or area(points[i],points[i1],points[i2])<0:
                    wedecidetoconsiderthisedge=True  
                if wedecidetoconsiderthisedge==True:
                    #we search in chord the chords close to -chord
                    for c in chordsandindices:
                        if distance(chord,c[0])<r/parafactory.coeffdistanceforedgesmerging and (k,c[1]) not in pairs:
                            if k==c[1]:
                                if polygons[k].quantity>1:
                                    pairs.append((polygons[k].id,c[1]))
                            else:
                                pairs.append((polygons[k].id,c[1]))
                chordsandindices.append(((-chord[0],-chord[1]),k))
        print(f"gluefrom list provides a set of pairs of size {len(pairs)}")
        pairs.sort()
        return pairs
    else:
        return []      
    
#returns all the pairs...
    
def gluefrompartition(polygons,partition,parafactory):
    print("glue from partition")
    polygons.sort(key=lambda p:p.id)
    chordsandindices=[]
    pairs=[]
    for indiceslist in partition:
        print(f"In glue from partition, works with a list of indices of length {len(indiceslist)}")
        pairs.append(gluefromlist(polygons,indiceslist,parafactory))
    pairs.sort()
    return pairs
    
def connect(polygons,parafactory):
    print("start connect")
    graphs=[]
    graph0=glueconcav(polygons)
    graph1=gluethinthin(polygons)
    partition=part(polygons,parafactory)
    graph2=gluefrompartition(polygons,partition,parafactory)
    graph2.append(graph0)
    graph22=[]
    for graph in graph2:
        for pair in graph:
                if (pair[0],pair[1]) not in graph22 and (pair[1],pair[0]) not in graph22:
                    graph22.append(pair)     
    partition=generalpartition(polygons,parafactory)
    newgraph2=gluefrompartition(polygons,partition,parafactory)
    for graph in newgraph2:
        for pair in graph:
                if (pair[0],pair[1]) not in graph22 and (pair[1],pair[0]) not in graph22:
                    graph22.append(pair)   
    print(f"size of concav graph={len(graph0)}")
    print(f"size of thinthin graph={len(graph1)}")
    print(f"size of all together graph22 = {len(graph22)} ")
    return [graph0,graph1,graph22]

        
######################################## 3 factory ##################################

#function factory builds the slates (before packing them with fucntions of packingslates)

def factory(region,directions,polygons,level,parafactory,parascore,timelimit):
    print("start factory")
    time0=time.time()
    global strongcollapse
    strongcollapse=False
    slates=initializeslates(polygons)
    startid=slates[len(slates)-1].identity+1  
    k=len(slates)
    #print(f"startid={startid} and len(slates)={len(slates)}")
    #We analyze the pairs that can give new generations
    print(f"level in factory = {level}")
    if level>1:
        if len(polygons)<500:
            parafactory.optionpartitionsize=len(polygons)
        graphs=connect(polygons,parafactory)
        print(f"We have {len(graphs)} graphs for connecting the items")
        polygons.sort(key=lambda p:p.id)
        #print(mainpairs)
        for i in range(len(graphs)):
            graph=graphs[i]
            if i==0:
                strongcollapse=True
            if startid!=0:
                startid=slates[len(slates)-1].identity+1 
            if parafactory.optiongeneration==0: 
                newslates=slatesgeneration(graph,region,directions,polygons,level,parafactory,parascore,startid,timelimit+time0-time.time())
            else:
                newslates=slatesgenerationprime(graph,region,directions,polygons,level,parafactory,parascore,startid,timelimit+time0-time.time())
            slates=slates+newslates
            if time.time()-time0-timelimit>0:
                print("slate generation interrupted by timelimit")
                break
            
    #to keep only last generation (to look at the slates without any single item)
    justfortest=0
    if justfortest==1:
        for i in range(k):
            slates.pop(0)
    #to print all the slates        
    #for sla in slates:
    #    if len(sla.ipolygons)>1:
    #        print(f"slate {sla.ipolygons}")
    print("end factory")
    return slates


######################################## packfactory ###########################################

#It is the main function to use for computing packings with slates preprocessing...
           
def packfactory(solutionsrepository,instancefilename,parafactory,parapackingslates,parapackingpolygons,parascore,timelimit):
    print(f"start packfactory")
    time0=time.time()
    region,polygons,directions=load(instancefilename) 
    #start preprocessing: slates computations
    slatesX=factory(region,directions,polygons,parafactory.level,parafactory,parascore,time0+timelimit-time.time())
    time1=time.time()
    print(f"slates computation = {time1-time0} s\n")

    print(f"parapackingslates.estimationstyle={parapackingslates.estimationstyle}")
    packingslates(region,polygons,slatesX,directions,parapackingslates)
    correctcrossings(region,polygons,directions)
    time2=time.time()
    print(f"slates packing = {time2-time1} s")
    print(f"slates computation + packing = {time2-time0} s\n")
    
    #outputs
    cost,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons) 
    solutionfilename=choosesolutionfilename(solutionsrepository,instancefilename,cost)
    writesolution(solutionfilename,instancefilename,polygons,cost,time2-time0,"factory + packingslates")   
    print(f"the cost of the packing is {cost}\n") 
    
    if withdrawinginsvg==True:
        #create SVG file
        xmax=max(vertex[0] for vertex in region.vertices)
        ymax=max(vertex[1] for vertex in region.vertices)
        grid=[20,100,50,20]
        scale=max(xmax/grid[1],ymax/grid[2])
        grid[1]=xmax/scale
        namesvg=f"svg_score{cost}.svg"
        file=createSVG(namesvg)
        drawWindow(file, grid)
        drawPackingblack(file, grid, region, polygons, scale)
        closeSVG(file)
    
    #adds optimization... or not
    if wanttoaddoptimization:
        print("start opt")
        print(f"remaining time for opt is {int(timelimit+time0-time.time())}")
        cost,polygons=opt(solutionsrepository,solutionfilename,instancefilename,parapackingpolygons,timelimit+time0-time.time())
        print(f"end opt with cost={cost}")
        #draws an image of the packing ... or not
        if withdrawinginsvg==True:
            #create SVG file
            xmax=max(vertex[0] for vertex in region.vertices)
            ymax=max(vertex[1] for vertex in region.vertices)
            grid=[20,100,50,20]
            scale=max(xmax/grid[1],ymax/grid[2])
            grid[1]=xmax/scale
            namesvg=f"svg_score{cost}.svg"
            file=createSVG(namesvg)
            drawWindow(file, grid)
            drawPackingblack(file, grid, region, polygons, scale)
            closeSVG(file)
    else:
        print("No optimization after slates packing (if you want opt, change the value of wanttoaddoptimization (on top) to True")
    
    
    print("end packfactory")
    return cost

########################## 5 parameters ########################

estimationstylepacking=2
estimationstylescorefactory=9  #parameter to choose the order of the polygons
    #int from 0 to 8 (see scorefromfeatures)
    # 0 cost
    # 1 cost but 1 over 4 is randomly "downgraded"
    # 2 pow(cost,costexponent)/area polygon
    # 3 pow(cost,costexponent)*random.gauss(1, 0.05)/area polygon
    # 4 pow(cost,costexponent)*random.gauss(1, 0.05)/(area polygon+area convex hull)
    # 5 pow(cost,costexponent)/area convex hull
    # 6 pow(cost,costexponent)*random.gauss(1, 0.05)/area convex hull
    # 7 t=is the ratio diameter / thickness in the orthogonal direction of the diamater
    #    (1+coeffthickness*t)*pow(cost,costexponent)*random.gauss(1, 0.005)/a 
    # 8 t
    # 9 if thickness>4 returns pow(cost,costexponent)/(areahull+diameter²) otherwise as 5 (no diameter)
    # 10 no ordering but preprocessing...


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

costexponentpacking=1 #1.6
costexponentscorefactory=1.6 #1.6
npositions=1000 #500 or 1000 or more
npositionstodig=10#see update parameters
radiustopush=20#see update parameters
radiustodig=5#see update parameters

maxmovedigvertices=200
maxpositionsdigvertices=200
ndigbeforestopslates=50#digs holes and tries to pack in the holes... could be increase for optimizing small solutions...
ndigbeforestoppolygons=20
ratiodigvertexforpackingslates=0.15
ratiodigvertexforpackingpolygons=0.15
nxcage=20 #number of cells to minimize the number of crossing tests
nycage=20
ntries=10
ntriesdig=4
coeffthickness=1.2
    
#slates are built with parascore / packing with parapacking
parascore=parameterspacking2(estimationstylescorefactory,optionfill,costexponentscorefactory,0,0,0,0,0,0,0,0,0,0,0,0)
parapackingslates=parameterspacking2(estimationstylepacking,optionfill,costexponentpacking,npositions,npositionstodig,radiustopush,radiustodig,maxmovedigvertices,maxpositionsdigvertices,ndigbeforestopslates,ratiodigvertexforpackingslates,nxcage,nycage,ntries,coeffthickness)
parapackingpolygons=parameterspacking2(estimationstylepacking,optionfill,costexponentpacking,npositions,npositionstodig,radiustopush,radiustodig,maxmovedigvertices,maxpositionsdigvertices,ndigbeforestoppolygons,ratiodigvertexforpackingpolygons,nxcage,nycage,ntriesdig,coeffthickness)

mergegrid=0#grid size of a grid used for computing the slates. It can be chosen at 0. Incresae it slows the computation but might increase the slates quality
optiongeneration=2
    #0 generates slates so that at each goiuytreneration, we remove the slates when a better one is found for a polygon (at the end it can remain a unique slate)
    #1 we keep the best slate for each polygon 
    #2 we keep the best slate for each polygon of each generation
optionpartitionsize=100#reduce it if the time of computation of the slates is too high
coeffdistanceforedgesmerging=5#distance ratio for considering that two edges of two items are close
hullcoeffs=[1.3,1.25,1.2]#the first coeff is for the ratio and the authers for ratio versus ratio
level=0#the level is the maximum number of items that we combine in a slate.
nselection=10*optionpartitionsize #number of slates that we keep before starting the packing
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
parafactory=parametersfactory(optiongeneration,optionpartitionsize,coeffdistanceforedgesmerging,hullcoeffs,mergegrid,level,nselection)


########################## 6 main function : pack ########################

def pack(solutionsrepository,instancefilename,level,timelimit):
    print("\nstart pack")
    parafactory.level=level
    cost=packfactory(solutionsrepository,instancefilename,parafactory,parapackingslates,parapackingpolygons,parascore,timelimit)
    print("end pack")
    
 
    
# Examples for running directly pack (including preprocessing/greedy heuristic/optimization)
# "solutions" is the repository where the solutions are written
# "instances/atris1240.cgshop2024_instance.json" is the finename of the instance
# "5" is the maximum size of the groups of items computed in the preprocessing step (choose 0 or 1 to avoid this long preprocessing step)
# "1000" is the timelimit in seconds
#
#pack("solutions","jig29.json",5,1000)

# Example of running uniquely the greedy routine (without slate preprocessing and without optimization) for being fast
# "solutions" is the repository where the solutions are written
# "instances/atris1266.cgshop2024_instance.json" is the finename of the instance
# "parapackingpolygons" is the set of the parameters
#
#greedy("solutions","instances/atris1240.cgshop2024_instance.json",parapackingpolygons)

#Example of running uniquely the optimization routine on a previous solution
#"solutions" is the repository where the solutions are written
#"solutions/atris1266-solution.4963609036.json" is the filename of the solution to optimize
#"instances/atris1266.cgshop2024_instance.json" is the finename of the instance
#"parapackingpolygons" is the set of the parameters
#1000 is the timelimit in seconds
#
#opt("solutions","solutions/atris1240-solution.3128340626.json","instances/atris1240.cgshop2024_instance.json",parapackingpolygons,100)

########################### 7 execution in console mode ###################

if len(sys.argv) > 3:
    thirdargument=sys.argv[3]
    if thirdargument.endswith(".json"):
        fromscratch=False #the third argument is a solution to optimize
    else:
        fromscratch=True #the third argument is the level

    if fromscratch:
        if len(sys.argv) == 4:
            print("input check")
            solutionsrepository=sys.argv[1]
            print(f"argument1=solutionsrepository={solutionsrepository}")
            instancefilename=sys.argv[2]
            print(f"argument2=instancefilename={instancefilename}")
            level=int(sys.argv[3])
            if level <2:
                print(f"argument3=level={level}   (levels 0 or 1,as chosen here, do not use slates (otherwise, with level k, we build groups of items of sizes at most k items)")
            else:
                print(f"argument3=level={level}   (we build groups of items of sizes at most {level} items)")

            print("We proceed to pack\nAs no time limit is given... We fix a huge one so that the algorithm will not terminate (but updates of the solutionare done when better ones are found)")
            pack(solutionsrepository,instancefilename,level,10000000000000000)
        elif len(sys.argv) == 5:
            print("input check")
            solutionsrepository=sys.argv[1]
            print(f"argument1=solutionsrepository={solutionsrepository}")
            instancefilename=sys.argv[2]
            print(f"argument2=instancefilename={instancefilename}")
            level=int(sys.argv[3])
            if level <2:
                print(f"argument3=level={level}   (levels 0 or 1,as chosen here, do not use slates (otherwise, with level k, we build groups of items of sizes at most k items)")
            else:
                print(f"argument3=level={level}   (we build groups of items of sizes at most {level} items)")
            timelimit=int(sys.argv[4])
            print(f"argument4=timelimite={timelimit}")
            print(f"We proceed to pack with timelimit={timelimit} s")
            pack(solutionsrepository,instancefilename,level,timelimit)
        else:
            print("the number of parameters does not seem correct")
            print("examples of commands\n")
            print("python3 factory.py solutionrepository instancefilename level")
            print("3 arguments (third -the level- is an integer => 0 or 1 to skip preprocessing of groups of at most level items)")
            print("=> computes a solution (from scratch) and writes the solutions in solutionrepository")
            print("the computation uses slates preprocessing (groups of items with at most [level] items)")
            print("no timelimit is given as fourth argument... Then the algorithm will not terminate. It updates the solutions when better ones are found\n")

            print("python3 factory.py solutionrepository instancefilename level timelimit")
            print("4 arguments (third -the level- is an integer => 0 or 1 to skip preprocessing of groups of at most level items)")
            print("  => computes a solution (from scratch) and writes the solutions in solutionrepository")
            print("the computation uses slates preprocessing (groups of items with at most [level] items)")
            print("timelimit (in seconds) is given as fourth argument... We don't stop everything when time is achieved, then the algorithm can use more time (but it breaks the main loops)")

            print("      for optimizing a PREVIOUS solution   \n")

            print("python3 factory.py solutionrepository solutionfilename instancefilename")
            print("3 arguments (third is a .json filename)")
            print("  => optimizes the solution solutionfilename and writes the solutions in solutionrepository")
            print("no timelimit is given as fourth argument... Then the algorithm will not terminate. It updates the solutions when better ones are found")

            print("python3 factory.py solutionrepository solutionfilename instancefilename timelimit")
            print("4 arguments (third is a .json filename)")
            print("=> optimizes the solution solutionfilename and writes the solutions in solutionrepository")
            print("timelimit(in seconds) is given as fourth argument... We don't stop everything when time is achieved, then the algorithm can use more time (but it breaks the main loops)")

            
    else:
        if len(sys.argv) == 4:
            print("input check")
            solutionsrepository=sys.argv[1]
            print(f"argument1=solutionsrepository={solutionsrepository}")
            solutionfilename=sys.argv[2]
            print(f"argument2=solutionfilename={solutionfilename}")
            instancefilename=sys.argv[3]
            print(f"argument3=instancefilename={instancefilename}")
            print("We proceed to pack\nAs no time limit is given... We fix a huge one so that the algorithm will not terminate (but updates of the solutionare done when better ones are found)")
            #for packing a solution without timelimit (then it's likely that the program will not stop, but still try to improve the current solution)
            opt(solutionsrepository,solutionfilename,instancefilename,10000000000000000)
        elif len(sys.argv) == 5:
            print("input check")
            solutionsrepository=sys.argv[1]
            print(f"argument1=solutionsrepository={solutionsrepository}")
            solutionfilename=sys.argv[2]
            print(f"argument2=solutionfilename={solutionfilename}")
            instancefilename=sys.argv[3]
            print(f"argument3=instancefilename={instancefilename}")
            timelimit=int(sys.argv[4])
            print(f"argument4=timelimite={timelimit}")
            print(f"We proceed to opt with timelimit={timelimit} s")
            opt(solutionsrepository,solutionfilename,instancefilename,timelimit)
        else:
            print("the number of parameters does not seem correct")
            print("examples of commands\n")
            print("python3 factory.py solutionrepository instancefilename level")
            print("3 arguments (third -the level- is an integer => 0 or 1 to skip preprocessing of groups of at most level items)")
            print("=> computes a solution (from scratch) and writes the solutions in solutionrepository")
            print("the computation uses slates preprocessing (groups of items with at most [level] items)")
            print("no timelimit is given as fourth argument... Then the algorithm will not terminate. It updates the solutions when better ones are found\n")

            print("python3 factory.py solutionrepository instancefilename level timelimit")
            print("4 arguments (third -the level- is an integer => 0 or 1 to skip preprocessing of groups of at most level items)")
            print("  => computes a solution (from scratch) and writes the solutions in solutionrepository")
            print("the computation uses slates preprocessing (groups of items with at most [level] items)")
            print("timelimit (in seconds) is given as fourth argument... We don't stop everything when time is achieved, then the algorithm can use more time (but it breaks the main loops)")

            print("      for optimizing a PREVIOUS solution   \n")

            print("python3 factory.py solutionrepository solutionfilename instancefilename")
            print("3 arguments (third is a .json filename)")
            print("  => optimizes the solution solutionfilename and writes the solutions in solutionrepository")
            print("no timelimit is given as fourth argument... Then the algorithm will not terminate. It updates the solutions when better ones are found")

            print("python3 factory.py solutionrepository solutionfilename instancefilename timelimit")
            print("4 arguments (third is a .json filename)")
            print("=> optimizes the solution solutionfilename and writes the solutions in solutionrepository")
            print("timelimit(in seconds) is given as fourth argument... We don't stop everything when time is achieved, then the algorithm can use more time (but it breaks the main loops)")
else:
    print("the number of parameters does not seem correct")
    print("examples of commands\n")
    print("python3 factory.py solutionrepository instancefilename level")
    print("3 arguments (third -the level- is an integer => 0 or 1 to skip preprocessing of groups of at most level items)")
    print("=> computes a solution (from scratch) and writes the solutions in solutionrepository")
    print("the computation uses slates preprocessing (groups of items with at most [level] items)")
    print("no timelimit is given as fourth argument... Then the algorithm will not terminate. It updates the solutions when better ones are found\n")

    print("python3 factory.py solutionrepository instancefilename level timelimit")
    print("4 arguments (third -the level- is an integer => 0 or 1 to skip preprocessing of groups of at most level items)")
    print("  => computes a solution (from scratch) and writes the solutions in solutionrepository")
    print("the computation uses slates preprocessing (groups of items with at most [level] items)")
    print("timelimit (in seconds) is given as fourth argument... We don't stop everything when time is achieved, then the algorithm can use more time (but it breaks the main loops)")

    print("      for optimizing a PREVIOUS solution   \n")

    print("python3 factory.py solutionrepository solutionfilename instancefilename")
    print("3 arguments (third is a .json filename)")
    print("  => optimizes the solution solutionfilename and writes the solutions in solutionrepository")
    print("no timelimit is given as fourth argument... Then the algorithm will not terminate. It updates the solutions when better ones are found")

    print("python3 factory.py solutionrepository solutionfilename instancefilename timelimit")
    print("4 arguments (third is a .json filename)")
    print("=> optimizes the solution solutionfilename and writes the solutions in solutionrepository")
    print("timelimit(in seconds) is given as fourth argument... We don't stop everything when time is achieved, then the algorithm can use more time (but it breaks the main loops)")



