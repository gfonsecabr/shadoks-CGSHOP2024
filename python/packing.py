from daft import *
import time
import random
import heapq
import sys
import os


############################# Plan #####################################

# 1  optimization routine: dig
# 2  greedy (computes an initial solution and finishes with 1 run of dig)
# 3  optimization opt (several routines of dig with several parameters)

# For using slate preprocessing, use factory.py ... which imports packing.py and packingslates.py

######################### 1 dig ###############################

  
def dig(solutionsrepository,instancefilename,region,polygons,directions,para,timelimit):
    print("start dig")
    time0=time.time()
    polygons.sort(key=lambda polygon:score(polygon,para),reverse=True)
    #builds the cage
    n=0
    for p in polygons:
        if p.positions!=None:
            n=n+len(p.positions)
    ncage=max(para.nxcage, int(5*math.sqrt(n)))
    c=buildcage(region, polygons, directions, ncage, ncage)

    #preprocess the packing   
    unpackedindices=[]
    for i in range(len(polygons)):
        if polygons[i].positions!=None:
            if len(polygons[i].positions)<polygons[i].quantity:
                unpackedindices.append(i)
        else:
            unpackedindices.append(i)
       
    cost,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons) 
    solutionfilename=choosesolutionfilename(solutionsrepository,instancefilename,cost)
    writesolution(solutionfilename,instancefilename,polygons,cost,0,"start dig")
    time0=time.time()
    
    print(f"current cost={cost}")
    computedigfeatures(region,polygons,para)
    print(f"number of positions to dig={para.npositionstodig}")
    positions,step=createPositions(region,para.npositionstodig)  
    
    count=0
    while count<para.ndigbeforestop and time.time()-time0<timelimit: 
        u=random.randint(0,99)
        if u<20:
            onepacked=digandpackaroundvertex(positions,c,region,polygons,directions,step,unpackedindices,para)
            if onepacked==1:
                newcost,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons) 
                #print(f"aroundvertex: current cost = {newcost} and previous cost={cost}")
                
                if newcost>cost:
                    count=0
                    newsolutionfilename=choosesolutionfilename(solutionsrepository,instancefilename,newcost)
                    time1=time.time()
                    writesolution(newsolutionfilename,instancefilename,polygons,newcost,time1-time0,"greedy opt")
                    os.remove(solutionfilename)
                    solutionfilename=newsolutionfilename
                    cost=newcost   
                else:
                    count=count+1
            else:
                count=count+1
        elif u<95:
            onepacked=digandpackintheinterior(positions,c,region,polygons,directions,step,unpackedindices,para)
            if onepacked==1:
                newcost,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons) 
                #print(f"dig inside: current cost = {newcost} and previous cost={cost}")
                if newcost>cost:
                    count=0
                    newsolutionfilename=choosesolutionfilename(solutionsrepository,instancefilename,newcost)
                    time1=time.time()
                    writesolution(newsolutionfilename,instancefilename,polygons,newcost,time1-time0,"greedy opt")
                    os.remove(solutionfilename)
                    solutionfilename=newsolutionfilename
                    cost=newcost
                else:
                    count=count+1
            else:
                count=count+1    
        else:
            onepacked=fillconflict(c, region, polygons, directions, unpackedindices,para)
            if onepacked==1:
                newcost,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons) 
                #print(f"fillconflict: current cost = {newcost} and previous cost={cost}")
                if newcost>cost:
                    count=0
                    newsolutionfilename=choosesolutionfilename(solutionsrepository,instancefilename,newcost)
                    time1=time.time()
                    writesolution(newsolutionfilename,instancefilename,polygons,newcost,time1-time0,"greedy opt")
                    os.remove(solutionfilename)
                    solutionfilename=newsolutionfilename
                    cost=newcost 
                else:
                    count=count+1
            else:
                count=count+1
    print("end dig")
    return cost

############################# 2 Greedy #####################################

def greedy(solutionsrepository,instancefilename,para):
    print("start greedy")   
    
    #load data
    region,polygons,directions=load(instancefilename)
    xmax=max(vertex[0] for vertex in region.vertices)
    ymax=max(vertex[1] for vertex in region.vertices)
    
    #preprocess inputPolygons by ordering them according a criterion
    polygons.sort(key=lambda polygon:score(polygon,para),reverse=True)
    #builds the cage
    n=0
    for p in polygons:
        if p.positions!=None:
            n=n+len(p.positions)
    ncage=max(para.nxcage, int(5*math.sqrt(n)))
    c=buildcage(region, polygons, directions, ncage, ncage)
       
    #prepare the packing   .
    unpackedindices=[]
    for i in range(len(polygons)):
        if polygons[i].positions!=None:
            if len(polygons[i].positions)<polygons[i].quantity:
                unpackedindices.append(i)
        else:
            unpackedindices.append(i)
            
    time0=time.time()
    fillconflict(c, region, polygons, directions, unpackedindices,para)    
    time1=time.time()
    cost,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons) 
    
    solutionfilename=choosesolutionfilename(solutionsrepository,instancefilename,cost)
    writesolution(solutionfilename,instancefilename,polygons,cost,time1-time0,"greedy fill")
    print(f"cost after greedy fill={cost}")
    
    #dig(solutionsrepository,instancefilename,region,polygons,directions,para,1000)
    
    
    #We check that the packed polygons have no crossing
    if checkcrossings(region,polygons,directions)==0:
        print("non valid solution")
    print("end greedy")
    

############################# 3 Optimization #####################################
    
    
def opt(solutionsrepository,solutionfilename,instancefilename,para,timelimit):
    time0=time.time()
    t0,translations=loadtranslations(instancefilename)
    region,polygons,directions=load(instancefilename)
    #reads solution
    print(f"loads solution {solutionfilename}")
    f = open(solutionfilename)
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

    #then we check the crossings and correct it if necessary
    result=checkcrossings(region,polygons,directions)
    if result==0:
        print("we correct the crossing")
        correctcrossings(region,polygons,directions)
        result=checkcrossings(region,polygons,directions)
        cost0,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons)
        print(f"new cost after correction is {cost0} and the new result is {result}")
        if result==0:
            exit()
    
    cost0,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons)
    cost=cost0
    t0=time.time()
    #100 runs of optimization
    countnullround=0
    while countnullround<100 and time.time()-time0<timelimit:
        time1=time.time()-time0
        print(f"remaining time = {int(timelimit+time0-time.time())} seconds")
        cost=dig(solutionsrepository,instancefilename,region,polygons,directions,para,timelimit-time1)
        if cost==cost0:
            countnullround=countnullround+1
            if para.npositions<30000:
                para.npositions=int(1.5*para.npositions)               
            para.maxmovedigvertices=int(1.5*para.maxmovedigvertices)
            para.maxpositionsdigvertices=int(1.5*para.maxpositionsdigvertices)
            para.ratiodigvertex=1.5*para.ratiodigvertex
            para.ndigbeforestop=int(para.ndigbeforestop*1.5)
            if para.ntries<10:
                para.ntries=int(para.ntries*1.5)
        else:
            cost0=cost
            countnullround=0  
    return cost,polygons
            

############################# 8 experiments ############################

estimationstyle=2  #parameter to choose the order of the polygons
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
npositions=1000 #500 or 1000 or more
npositionstodig=10#see update parameters
radiustopush=20#see update parameters
radiustodig=5#see update parameterse 
maxmovedigvertices=200
maxpositionsdigvertices=200#400
ndigbeforestoppolygons=50
ratiodigvertex=0.15
nxcage=20 #number of cells to minimize the number of crossing tests
nycage=20
ntries=3
coeffthickness=1.2
para=parameterspacking2(estimationstyle,optionfill,costexponent,npositions,npositionstodig,radiustopush,radiustodig,maxmovedigvertices,maxpositionsdigvertices,ndigbeforestoppolygons,ratiodigvertex,nxcage,nycage,ntries,coeffthickness)

#examples
#greedy("solutions","instances/atris1266.cgshop2024_instance.json",para)
#opt("solutions","solutions/atris1266-solution.4963609036.json","instances/atris1266.cgshop2024_instance.json",para)



