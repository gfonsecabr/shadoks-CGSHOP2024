import json
from structures import *

########################### Load instance ##################################

def load(instancefilename):  
    print(f"load {instancefilename}")
    # Opening JSON file
    f = open(instancefilename)
    data = json.load(f)
    #container
    c=data["container"]
    x_container = c.get('x')
    y_container =c.get('y')
    n=len(x_container )
    regionVertices=[(x_container[i], y_container[i]) for i in range(n)]

    #region
    region=polygon(1,-1,regionVertices,0,0,directions)
    #directions
    print(f"We have {len(directions)} directions")
    
    #polygons
    items=data["items"] #items is a list
    n=len(items)
    polygons=[]
    costs=[]
    quantities=[]
    for i in range(n):
        item=items[i]
        x=item.get('x')
        y=item.get('y')
        k=len(x)
        p=[(x[i], y[i]) for i in range(k)]
        poly=polygon(0,i,p,item.get('quantity'),item.get('value'),directions)
        polygons.append(poly)      
    f.close()
    return region,polygons,directions

def loadtranslations(instancefilename):
    #print(f"loadtranslations {instancefilename}")
    # Opening JSON file
    f = open(instancefilename)
    data = json.load(f)
    #container
    c=data["container"]
    x_container = c.get('x')
    y_container =c.get('y')
    n=len(x_container )
    regionVertices=[(x_container[i], y_container[i]) for i in range(n)]

    #region
    t0=findtranslations(regionVertices)
    
    #polygons
    items=data["items"] #items is a list
    n=len(items)
    translations=[]
    for i in range(n):
        item=items[i]
        x=item.get('x')
        y=item.get('y')
        k=len(x)
        p=[(x[i], y[i]) for i in range(k)]
        t=findtranslations(p)
        translations.append((i,t))     
    f.close()
    return t0,translations
    
########################### Write solution ##################################

def choosesolutionfilename(solutionsrepository,instancefilename,score):
    if '/' in instancefilename:
        shortname=instancefilename.split('/')[-1].split('.')[0]
    else:
        shortname=instancefilename.split('.')[0]
    solutionfilename=f"{solutionsrepository}/{shortname}-solution.{score}.json"
    return solutionfilename
    
    
   
def writesolution(solutionfilename,instancefilename,polygons,score,time,algoname):   
    # Data to be written
    t0,translations=loadtranslations(instancefilename)
    ipolygons=[]
    x=[]
    y=[]
    num_included_items=0
    for p in polygons:
        if p.positions!=None:
            for position in p.positions:
                num_included_items=num_included_items+1
    
    ipolygons=[0 for i in range(num_included_items)]
    x=[0 for i in range(num_included_items)]
    y=[0 for i in range(num_included_items)]
    i=0
    for p in polygons:
        if p.positions!=None:
            for position in p.positions:
                ipolygons[i]=p.id
                x[i]=position[0]-translations[p.id][1][0]#in case of error, might be due to t0 which is not used here
                y[i]=position[1]-translations[p.id][1][1]
                i=i+1
  
    dictionary ={
        "type": "cgshop2024_solution",
        "instance_name": f"{instancefilename}",
        "num_included_items": num_included_items,
        "meta": {"algorithm" : f"algoname" ,"time" : f"{time}s" },
        "item_indices": ipolygons,
        "x_translations": x,
        "y_translations": y
    }    
    with open(solutionfilename, "w") as outfile:
        json.dump(dictionary,  outfile, indent=4)
        
########################### read solution ##################################

def readsolution(instancefilename,solutionfilename):
    t0,translations=loadtranslations(instancefilename)
    region,polygons,directions=load(instancefilename)
    #reads solution
    f = open(solutionfilename)
    data = json.load(f)
    ipolygons= data.get('item_indices')
    x = data.get('x_translations')
    y = data.get('y_translations')
    for i in range(len(ipolygons)):
        ipolygon=ipolygons[i]
        xpolygon=x[i]+translations[ipolygon][1][0]
        ypolygon=y[i]+translations[ipolygon][1][1]
        p=(xpolygon,ypolygon)
        if polygons[ipolygon].positions==None:
            polygons[ipolygon].positions=[p]
        else:
            polygons[ipolygon].positions.append(p)
    f.close()
    cost,npacked,totalcost,totalquantities,areacovered=packingstatistics(polygons)    
    print(f"the cost of the packing is {round(100*cost/totalcost,2)}")
    #create SVG file
    xmax=max(vertex[0] for vertex in region.vertices)
    ymax=max(vertex[1] for vertex in region.vertices)
    grid=[20,150,50,20]
    scale=max(xmax/grid[1],ymax/grid[2])
    grid[1]=xmax/scale+100
    if '/' in instancefilename:
        shortname=instancefilename.split('/')[-1].split('.')[0]
    else:
        shortname=instancefilename.split('.')[0]
    namesvg=f"{shortname}.{cost}.svg"
    #print(namesvg)
    file=createSVG(namesvg)
    drawWindow(file, grid)
    drawPacking(file, grid, region, polygons, scale)
    closeSVG(file)        
    
   
#readsolution("instances/atris1240.cgshop2024_instance.json","solutions/atris1240.cgshop2024_solution.3614716974.json")
#fullname = os.path.dirname(os.path.abspath(sys.argv[0])) + f"/instances/{shortname}.cgshop2024_instance.json"

