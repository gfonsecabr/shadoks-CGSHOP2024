from geometry import *

###################################################################################################
###################################### svg ###################################################
###################################################################################################

# Ce fichier contient un certain nombre de fonctions en python 
# dont le but est de créer facilement une image en format vectoriel svg.
# Ces images s'ouvrent très facilement avec un navigateur web.
# Ce fichier contient les fonctions de la librairie et pour la plupart 
# d'entre elles une petite fonction de test qui permet de vérifier sa syntaxe 
# et ce qu'elle produit
#
#********************* Grid ********************
# La librairie de tracé fonctionne avec une structure de grille sous-jacente.
# Il faut choisir au départ la taille de la grille que l'on va utiliser, 
# en mettant ces grandeurs dans une liste le plus souvent nommée grid.
# grid[0] est le nombre de pixel sur le bord de l'image autour de la grille
# grid[1] est le nombre de colonnes de la grille
# grid[2] est le nombre de bandes horizontales de la grille
# grid[3] est la taille des carrés de la grille, 
# Tout ce qui sera dessiné dans l'image le sera en utilisant les coordonnées dans la grille 
# Le point de coordonnées (0,0) est en bas à gauche (à la limite de la marge) 
# Le point de coordonnées (grid[1],0) et en bas à droite
# Le point de coordonnées (grid[1],grid[2]) et en haut à droite
# Et le point de coordonnées (0,grid[2]) et en haut à gauche
# Exemple grid=[15,50,30,20] signifie que l'on va faire une grille avec une bordure autour de 15 pixels.
# La grille aura 50 colonnes, 30 bandes horizontales et 
# chaque carré de la grille aura comme taille 20 pixels de côté.
#
#*******************Comment créer une image ?**********************
# Pour créer une image la procédure est toujours la même:
# On choisit les dimensions de la grille, avec par exemple l'instruction: grid=[15,50,30,20]
# On appelle successivement les fonctions createSVG(nomDuFichierImage) qui retourne un file, 
# puis drawWindow(file, grid)...
# Ensuite on peut faire appel à toutes les fonctions de tracés mises à disposition...
# Puis on ferme en appelant la fonction closeSCG(file)
# Et c'est fini!!!!!
# Il ne reste plus qu'à visualiser le résultat obtenu dans un navigateur (les fichiers produits sont des .xml)

# A suivre deux grandes parties:
    # La partie cuisine (Les fonctions support) qu'à-priori, vous n'avez pas besoin de regarder trop en détail
    # La partie utile qui contient toutes les fonctions de tracé, et une invitation pour les tester.
# Vous pouvez sauter la partie cuisine et aller directement à la partie utile... 

##########################################################################################
########################## Liste des fonctions disponibles ###############################
##########################################################################################

# Au début...
# createSVG(fileName)                   => création de l'image
# drawWindow(file, grid)                => création de la fenêtre où tracer

# Dans le corps du tracé
# colorRGB(r,g,b)                                               => choix d'une couleur selon son code RGB
# randomColorRgb()                                              => choix d'une couleur aléatoire
# randomColor()                                                 => choix d'une couleur aléatoire
# randomSetOfPoints(grid,n)                                     => génération d'une liste de points du plan aléatoire dans la grille
# randomOrientedPolygon(grid)                                   => génération d'un polygone aléatoire à partir d'un chemin aléatoire
# randomSetOfPointsWithSeeds(grid,n,s)                          => génération d'un ensemble de points aléatoire à partir de s graines
# drawGrid(file, grid, color)                                   => tracé de la grille
# drawPoint(file, grid, point, color)                           => tracé d'un point
# drawBigPoint(file, grid, point, color)                        => tracé d'un point (plus gros) 
# drawSegment(file, grid, vertex1, vertex2, color)              => tracé d'un segment
# segmentWithoutVertices(file, grid, vertex1, vertex2, color)   => tracé d'un segment sans tracer les extrémités
# drawPolyline(file, grid, polygon, color)                      => tracé d'une ligne polygonale
# drawPolygon(file, grid, polygon, color)                       => tracé d'un polygone
# drawPolygonOpacity(file, grid, polygon, color, opacity)       => tracé d'un polygone en réglant l'opacité intérieure
# colorPixel(file, grid, pixel, color)                          => coloriage d'un pixel de la grille
# drawCircle(file, grid, center, radius, color)                 => tracé d'un cercle
# drawDisk(file, grid, center, radius, color)                   => tracé d'un disque
# backgroundColor(file, grid, color)                            => choix de la couleur en arrière plan de l'image
# drawLine(file, grid, line, color)                             => tracé d'une droite d'équation ax+by=c où line=(a,b,c)
# drawRay(file, grid, ray, color)                               => tracé d'une demi-droite ray donnée par l'origine et la direction
# writeText(file, grid, text, size, position, color)            => écriture d'un texte à l'emplacement position
 

# A la fin
# closeSVG(file)                        => fermeture du fichier


##########################################################################################  
############### Partie cuisine / Fonctions support (inutile pour l'usager) ###############
##########################################################################################

# Cette partie cuisine contient 
    # des fonctions essentielles de gestio du fichier image (création, ouverture, fermeture, repérage)
    # des fonctions de tirage aléatoire d'une couleur. Très pratique
    # des fonctions de génération aléatoire d'un ensemble de point ou d'un polygone.

######## Creation/Ouverture/Fermeture du fichier image #######
    
def createSVG(fileName):
    #print("createSVG")
    file=open(fileName, "w")
    file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
    file.write("<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\"")
    return file

def drawWindow(file, grid):
    #print("drawWindow")
    file.write(" width=\"%d\" height=\"%d\">\n" % ((grid[1]+1)*grid[3]+2*grid[0], (grid[2]+1)*grid[3]+2*grid[0]))

def closeSVG(file):
    #print("closeSVG")
    file.write("</svg>")
    file.close()

# Sauf pour développer de nouvelles fonctions de tracé, cette fonction n'a pas besoin d'être inspectée...
# xyInSVG est une fonction de conversion de coordonnées: 
# On lui donne les coordonnées dans la grille (ce sont les coordonnées de point) et elle retourne les coordonnées
# dans l'image.
# A priori, pas besoin de vous en servir, sauf si vous voulez ajouter de nouvelles fonctions de tracé. 

def xyInSVG(grid,point):
    x=grid[0]+point[0]*grid[3]+grid[3]/2
    y=grid[0]+(grid[2]-point[1])*grid[3]+grid[3]/2
    return x,y

# Fonction utilisée pour tracer la grille
def segmentWV(file, grid, vertex1, vertex2, color):
    x1,y1=xyInSVG(grid, vertex1)
    x2,y2=xyInSVG(grid, vertex2)
    stroke=0.2
    file.write(f"<line x1=\"{x1}\" y1=\"{y1}\" x2=\"{x2}\" y2=\"{y2}\" stroke=\"{color}\" stroke-width=\"{stroke}\" />\n")

######## Les fonctions de couleurs aléatoires ##########
# Une fonction pour choisir une couleur au hasard en tirant aléatoirement ses coefficients RGB

def colorRGB(r,g,b):
    return f"rgb({r},{g},{b})"
    
def randomColorRgb():
    i=random.randint(0,7)
    if i==0:
        return f"rgb({random.randint(150,255)},{random.randint(0,100)},{random.randint(0,100)})"
    if i==1:
        return f"rgb({random.randint(0,100)},{random.randint(150,255)},{random.randint(0,100)})"
    if i==2:
        return f"rgb({random.randint(0,100)},{random.randint(0,100)},{random.randint(150,255)})"
    if i==3:
        return f"rgb({random.randint(0,100)},{random.randint(150,255)},{random.randint(150,255)})"
    if i==4:
        return f"rgb({random.randint(150,255)},{random.randint(150,255)},{random.randint(0,100)})"
    if i==5:
        return f"rgb({random.randint(150,255)},{random.randint(0,100)},{random.randint(150,255)})"
    return f"rgb({random.randint(150,255)},{random.randint(150,255)},{random.randint(150,255)})"
    return f"rgb({random.randint(0,50)},{random.randint(0,50)},{random.randint(0,50)})"

#♥Une autre fonction pour choisir aléatoirement une couleur dans une liste préfixée...

def randomColor():
    i=random.randint(0,70)
    if i==1:
        return "burlywood"
    if i==2:
        return "coral"
    if i==3:
        return "cyan"
    if i==4:
        return "darkgray"
    if i==5:
        return "deeppink"
    if i==6:
        return "dodgerblue"
    if i==7:
        return "fuchsia"
    if i==8:
        return "lightgreen"
    if i==9:
        return "lightseagreen"
    if i==10:
        return "mediumblue"
    if i==11:
        return "rosybrown"
    if i==12:
        return "turquoise"
    if i==13:
        return "blue"
    if i==14:
        return "darksalmon"
    if i==15:
        return "firebrick"
    if i==16:
        return "lawngreen"
    if i==17:
        return "silver"
    if i==18:
        return "rosybrown"
    if i==19:
        return "magenta"
    if i==20:
        return "red"
    if i==21:
        return "tomato"
    if i==22:
        return "palevioletred"
    if i==23:
        return "darkviolet"
    if i==24:
        return "fuchsia"
    if i==25:
        return "lightgreen"
    if i==26:
        return "lightseagreen"
    if i==27:
        return "mediumblue"
    if i==28:
        return "rosybrown"
    if i==29:
        return "turquoise"
    if i==30:
        return "blue"
    if i==31:
        return "darksalmon"
    if i==32:
        return "limegreen"
    if i==33:
        return "lightsalmon"
    if i==34:
        return "gold"
    if i==35:
        return "crimson"
    if i==36:
        return "steelblue"
    if i==37:
        return "brown"
    if i==38:
        return "aquamarine"
    if i==39:
        return "aqua"
    if i==40:
        return "hotpink"
    if i==41:
        return "lightpink"
    if i==42:
        return "mediumpurple"
    if i==43:
        return "orangered"
    if i==44:
        return "saddlebrown"
    if i==45:
        return "yellow"
    if i==46:
        return "violet"
    if i==47:
        return "saddlebrown"
    if i==48:
        return "orange"
    if i==49:
        return "thistle"
    if i==50:
        return "slateblue"
    if i==51:
        return "paleturquoise"
    if i==52:
        return "gainsboro"
    if i==53:
        return "wheat"
    if i==54:
        return "maroon"
    return randomColorRgb()

########### Les générateurs aléatoires utilisés (ou pas) dans les tests ###########

# un generateur d'un ensemble de points (qui peut être pris comme un ensemble de sommets d'un polygone)
# (utilisé pour les tests).

def randomSetOfPoints(grid,n):
    polygon=[]
    for i in range(n):
        p=[random.randint(0,grid[1]),random.randint(0,grid[2])]
        polygon.append(p)
    return polygon
    
# un generateur de polygone aléatoire (utilisé pour les tests): cette fonction ne sert pas à tracer 
# mais à générer la liste des points du polygone dans une grille grid
    
def randomOrientedPolygon(grid):
    #print("start randomPolygonGenerator")
    X=grid[1]
    Y=grid[2]
    polygon=[]
    start=[int(X/2),int(Y/2)]
    polygon.append(start)
    #On tire au hasard une direction dans (1,0), (1,1), (0,1), (-1, 1), (-1,0), (-1;-1), (0,-1), (1,-1)
    rr=random.randint(0,7)
    notArrived=1
    while notArrived==1:
        #We move from 1 step according to the random value of rr
        if rr==0:
            step=(1,0)
        if rr==1:
            step=(1,1)
        if rr==2:
            step=(0,1)
        if rr==3:
            step=(-1,1)
        if rr==4:
            step=(-1,0)
        if rr==5:
            step=(-1,-1)
        if rr==6:
            step=(0,-1)
        if rr==7:
            step=(1,-1)
        x=polygon[len(polygon)-1][0]+step[0]
        y=polygon[len(polygon)-1][1]+step[1]
        if x>0 and x<X and y>0 and y<Y: 
            newPoint=[x,y]
            polygon.append(newPoint)
            rr=(rr+random.randint(-1,1))%8
        else:
            #We go outside... we should not add this point
            rr=(rr+1)%8
        #We stop when coming back to the center
        if polygon[len(polygon)-1][0]==polygon[0][0] and polygon[len(polygon)-1][1]==polygon[0][1]:
            notArrived=0
    #print("end randomPolygonGenerator")
    return polygon

# Un générateur d'ensemble de points à partir de graines tirées aussi aléatoirement. 
# n est le nombre de points de l'ensemble demandé
# s est le nombre de seeds (graines autour desquelles les points sont plus ou moins regroupés).

def randomSetOfPointsWithSeeds(grid,n,s):
    X=grid[1]
    Y=grid[2]
    point=[]
    #We choose the cardinalities around each seed
    card=[]
    if s<=0:
        s=1
    if s==1:
        card.append(n)
    else:
        somme=0
        for i in range(s):
            k=random.randint(0,1000)
            somme=somme+k
            card.append(k)
        partialSomme=0
        for i in range(s-1):
            #We normalize the cardinalities
            card[i]=int(n*card[i]/somme)
            partialSomme=partialSomme+card[i]
        card[s-1]=n-partialSomme
    #We build the set with card[i] points around each seed
    for i in range(s):
        seed=[random.randint(0,X),random.randint(0,Y)]
        #We choose a radius...
        r=int(min(2*seed[0],2*(X-seed[0]),2*seed[1],2*(Y-seed[1]),X/10,Y/10))
        for k in range(card[i]):
            x=-1
            while x<0 or x>X: 
                #x=seed[0]+random.randint(-r,r)
                x=random.gauss(seed[0],r)
            y=-1
            while y<0 or y>Y: 
                #y=seed[1]+random.randint(-r,r)
                y=random.gauss(seed[1],r)
            newPoint=[x,y]
            point.append(newPoint)
    return point




##########################################################################################  
################## La partie utile / les fonctions de tracé dans la fenêtre de l'image #########################
##########################################################################################
    
# C'est là que les choses utiles commencent!

############################## Création d'une première image (vide)  ########################################

# 1) Executez  testCreation() 
# On aura alors une fenêtre avec un bord de 15 pixels, des cases de taille 20x20 
# avec 50 cases sur chaque horizontale et 30 cases sur chaque verticale
# autrement dit (50x30 cases de taille 20x20 pixels et un bord tout autour de taille 15 pixels)
# Ouvrez le fichier créé "testCreation.xml" avec un navigateur web
# pour voir à quoi il ressemble... Une fenêtre toute blanche, il ne reste plus 
# qu'à dessiner de choses dedans.
# Ouvrez le en mode texte pour voir ce qui écrit dans le fichier 
# (par exemple en tapant CTRL U dans votre navigateur)!
# Les fonctions de tracé ne font rien d'autre que d'écrire le morceau de texte 
# qui correspond à ce que vous demandez de tracer.

def testCreation():
    print("testCreation")
    grid=[15,50,30,20]
    fileName="testCreation.xml"
    file=createSVG(fileName)
    drawWindow(file, grid)
    closeSVG(file)
    
#testCreation()

############################## Tracé de la grille ########################################
# Une fonction pour tracer la grille qui a servi pour construire l'image: drawGrid
# Elle est utile pour se repérer dans l'image.    

def drawGrid(file, grid, color):
    #print("drawGrid")
    ncolumns=grid[1]
    nrows=grid[2]
    gridPrime=grid.copy()
    for x in range(int(ncolumns)+1):
        segmentWV(file,gridPrime,(x,0),(x,nrows),"black")
    for x in range(int(nrows)+1):
        segmentWV(file,gridPrime,(0,x),(ncolumns,x),"black")



# 2) Executez  testDrawGrid() en le décommentant
# On aura alors une fenêtre qui n'est plus toute blanche:
# Elle contient maintenant une grille de 50x30 cases de taille 20x20 pixels et un bord tout autour de taille 15 pixels.
# Ouvrez le fichier créé "testDrawGrid.xml" avec un navigateur web.
# Ouvrez le en mode texte pour voir son contenu en texte!
# Modifier la couleur de la grille, en remplaçant par exemple "black" par "blue"

def testDrawGrid():
    print("testDrawGrid")
    #Begin SVG file
    grid=[15,50,30,20]

    #create SVG file
    file=createSVG("testDrawGrid.xml")
    drawWindow(file,grid)
    #add elements inside
    drawGrid(file,grid,"black")
    #Close SVG file
    closeSVG(file)
    
#testDrawGrid()

#################################### Tracé d'un point ############################################ 
# La fonction drawPoint affiche un point sous la forme d'un petit disque...

def drawPoint(file, grid, point, color):
    #print("drawPoint")
    x,y=xyInSVG(grid, point)
    file.write(f"<circle cx=\"{x}\" cy=\"{y}\" r=\"3.5\" fill=\"{color}\" />\n")
    
# La fonction drawBigPoint affiche un point sous la forme d'un disque un peu plus gros...
    
def drawBigPoint(file, grid, point, color):
    #print("drawPoint")
    x,y=xyInSVG(grid, point)
    file.write(f"<circle cx=\"{x}\" cy=\"{y}\" r=\"5\" fill=\"{color}\" />\n")
    
    
# 3) Executez  testDrawPoint()
# On affiche des points de différentes couleurs...
# Ouvrez le fichier "testDrawPoint.xml" avec un navigateur
# Modifier les coordonnées des points, essayez d'autres couleurs
# (couleurs possibles: burlywood - coral - cyan - darkgray - darlmagenta - deeppink -
# dodgerblue - mediumblue - turquoise - firebrick - gray - orchid - orange - violet
# yellow - aqua - blueviolet - chartreuse - darkcyan - lime - mediumpruple - orangered
# springgreen - brown - chocolate - crimson - gold - lightsalmon - sienna - tomato
# white )

def testDrawPoint():
    print("testDrawPoint")
    #Begin SVG file
    grid=[15,50,30,20]
    #create SVG file
    file=createSVG("testDrawPoint.xml")
    drawWindow(file, grid)
    #add elements inside
    drawGrid(file,grid,"black")
    point0=[0,0]
    point1=[24,7]
    point2=[38,27]
    point3=[2,17]
    A=[19,26]
    drawPoint(file, grid, point0, "blue")
    drawPoint(file, grid, point1, "red")
    drawPoint(file, grid, point2, "grey")
    drawPoint(file, grid, point3, "chocolat")
    drawBigPoint(file, grid, A, randomColor())#Pour le point A, on va le tracer en gros, avec une couleur aléatoire
    #Close SVG file
    closeSVG(file)
    
#testDrawPoint()

# 4) Executez  testDrawPointRandom()
# Cette fois, on va tirer aléatoirement un ensemble de 1000 points que l'on va tracer avec des couleurs elles aussi aléatoires.
# Changer la valeur de 1000 et génrerez quelques images...

def testDrawPointRandom():
    print("testDrawPointRandom")
    #Begin SVG file
    grid=[15,50,30,20]
    #create SVG file
    file=createSVG("testDrawPointRandom.xml")
    drawWindow(file, grid)
    #add elements inside
    drawGrid(file,grid,"black")
    for i in range(1000):
        A=(random.randint(0,grid[1]),random.randint(0,grid[2]))
        drawBigPoint(file, grid, A, randomColor())#Pour le point A, on va le tracer en gros, avec une couleur aléatoire
    #Close SVG file
    closeSVG(file)

#testDrawPointRandom()

################################# tracé d'un segment ############################################ 

# La fonction de tracé d'un segment est drawSegment.
# Les extrémités du segment tracé sont des petits disques.
# Si vous souhaitez supprimer les extrémités, utilisez de préférence la fonction segmentWithoutVertices
# Si vous souhaitez des segments plus épais, il faut augmenter la valeur de stroke en la multipliant par une constante...

def drawSegment(file, grid, vertex1, vertex2, color):
    x1,y1=xyInSVG(grid, vertex1)
    x2,y2=xyInSVG(grid, vertex2)
    stroke=(1.1+grid[3]/10)
    file.write(f"<line x1=\"{x1}\" y1=\"{y1}\" x2=\"{x2}\" y2=\"{y2}\" stroke=\"{color}\" stroke-width=\"{stroke}\" />\n")
    drawPoint(file,grid,vertex1,color)
    drawPoint(file,grid,vertex2,color)
    
# La fonction de tracé d'un segment sans représenter les extrémités par un disque.
def segmentWithoutVertices(file, grid, vertex1, vertex2, color):
    x1,y1=xyInSVG(grid, vertex1)
    x2,y2=xyInSVG(grid, vertex2)
    stroke=0.2
    file.write(f"<line x1=\"{x1}\" y1=\"{y1}\" x2=\"{x2}\" y2=\"{y2}\" stroke=\"{color}\" stroke-width=\"{stroke}\" />\n")

# 5) Executez  testDrawSegment()  
# On affiche des segments de différentes couleurs...
# Ouvrez le fichier "testDrawSegment.xml" avec un navigateur
# Modifier les coordonnées des points...

def testDrawSegment():
    print("testDrawSegment")
    #Begin SVG file
    grid=[15,50,30,20]
    
    #create SVG file
    file=createSVG("testDrawSegment.xml")
    drawWindow(file, grid)
    #add elements inside
    drawGrid(file, grid,"black")
    A=[45,23]
    B=[12,27]
    C=[38,14]
    U=[8,13]
    V=[34,25]
    drawSegment(file, grid, A, B, "blue")
    drawSegment(file, grid, B, C, "orchid")
    segmentWithoutVertices(file, grid, U,V, randomColor())
    #Close SVG file
    closeSVG(file)
    
#testDrawSegment()

# 6) Executez  testDrawSegmentRandom() où l'on choisit les sommets de 500 segments de façon aléatoire

def testDrawSegmentRandom():
    print("testDrawSegmentRandom")
    #Begin SVG file
    grid=[15,50,30,20]
    #create SVG file
    file=createSVG("testDrawSegmentRandom.xml")
    drawWindow(file, grid)
    #add elements inside
    drawGrid(file, grid,"black")
    for i in range(500):
        A=(random.randint(0,grid[1]),random.randint(0,grid[2]))
        B=(random.randint(0,grid[1]),random.randint(0,grid[2]))
        drawSegment(file, grid, A, B, randomColor())
    #Close SVG file
    closeSVG(file)

#testDrawSegmentRandom()

########################### tracé d'une ligne polygonale ############################################ 

# Polygon est une liste de points, par exemple polygon=[[1,2],[9,5],[3,0]]
# La fonction drawPolyline trace la ligne polygonale rejoignant les sommets successifs de la liste de point polygon
# La ligne polygonale n'est pas fermée... quand l'objet est fermé, c'est un polygone et c'est la fonction suivante...

def drawPolyline(file, grid, polygon, color):
    #print("drawPolygon")
    file.write("<polyline points=\"")
    x,y=xyInSVG(grid, polygon[0])
    file.write(f"{x},{y}")
    #drawPoint(file,grid,polygon[i],color)
    for i in range(len(polygon)):
        x,y=xyInSVG(grid, polygon[i])
        file.write(f" {x},{y}")
    x,y=xyInSVG(grid, polygon[0])
    #file.write(f" {x},{y}")
    stroke=(1.1+grid[3]/10)    
    file.write(f"\" fill=\"none\" fill-opacity=\"0.5\" stroke=\"{color}\" stroke-width=\"{stroke}\" />\n")
    #file.write(f"\" fill=\"{color}\" fill-opacity=\"0.5\" stroke=\"{color}\" stroke-width=\"{stroke}\" />\n") #Ligne à commenter/ décommenter
    
# 7) Executez  testDrawPolyline()  
# On affiche des lignes polygonales...
# Ouvrez le fichier "testDrawPolyline.xml" avec un navigateur
# Modifiez quelques paramètres, coordonnées, couleurs....

def testDrawPolyline():
    print("testDrawPolyline")
    #Begin SVG file
    grid=[15,50,30,20]
    #create SVG file
    file=createSVG("svg-testDrawPolyline.xml")
    drawWindow(file, grid)
    #add elements inside
    drawGrid(file,grid,"black")
    #draw a polyline
    A=[45,23]
    B=[12,27]
    C=[38,14]
    D=[12,4]
    E=[17,8]
    polyline=[A,B,C,D,E]
    drawPolyline(file,grid,polyline,"green");
    #Close SVG file
    closeSVG(file)
    
#testDrawPolyline()


####################### tracé d'un polygone (fermé) ############################################ 

# La fonction de tracé d'un polygone fermé (l'intérieur du polygone est coloré) est drawPolygon
def drawPolygon(file, grid, polygon, color):
    #print("drawPolygon")
    file.write("<polyline points=\"")
    x,y=xyInSVG(grid, polygon[0])
    file.write(f"{x},{y}")
    #drawPoint(file,grid,polygon[i],color)
    for i in range(len(polygon)):
        x,y=xyInSVG(grid, polygon[i])
        file.write(f" {x},{y}")
    x,y=xyInSVG(grid, polygon[0])
    file.write(f" {x},{y}")
    stroke=(1.1+grid[3]/10)
    file.write(f"\" fill=\"{color}\" fill-opacity=\"0.5\" stroke=\"{color}\" stroke-width=\"{stroke}\" />\n")

#Si on ne veut un tracé où on choisit l'opacité du polygone. Choisir opacity=1 pour un tracé totalement opaque

def drawPolygonOpacity(file, grid, polygon, color, opacity):
    #print("drawPolygon")
    file.write("<polyline points=\"")
    x,y=xyInSVG(grid, polygon[0])
    file.write(f"{x},{y}")
    #drawPoint(file,grid,polygon[i],color)
    for i in range(len(polygon)):
        x,y=xyInSVG(grid, polygon[i])
        file.write(f" {x},{y}")
    x,y=xyInSVG(grid, polygon[0])
    file.write(f" {x},{y}")
    stroke=(1.1+grid[3]/10)
    file.write(f"\" fill=\"{color}\" fill-opacity=\"{opacity}\" stroke=\"{color}\" stroke-width=\"{stroke}\" />\n")
    
def drawPolygonwithoutstroke(file, grid, polygon, color):
    #print("drawPolygon")
    file.write("<polyline points=\"")
    x,y=xyInSVG(grid, polygon[0])
    file.write(f"{x},{y}")
    #drawPoint(file,grid,polygon[i],color)
    for i in range(len(polygon)):
        x,y=xyInSVG(grid, polygon[i])
        file.write(f" {x},{y}")
    x,y=xyInSVG(grid, polygon[0])
    file.write(f" {x},{y}")
    stroke=0
    opacity=1
    file.write(f"\" fill=\"{color}\" fill-opacity=\"{opacity}\" stroke=\"{color}\" stroke-width=\"{stroke}\" />\n")

# 8) Executez  testDrawPolygon()  
# On affiche cette fois un polygone... euf, en fait deux: un polygone ABCDEF 
# et un polygone généré aléatoirement par la fonction randomPolygonGenerator(grid)
# Ouvrez le fichier "testDrawPolygon.xml" avec un navigateur
# Modifiez quelques paramètres, coordonnées, couleurs....

def testDrawPolygon():
    print("testDrawPolygon")
    #Begin SVG file
    grid=[15,50,30,20]
    #create SVG file
    file=createSVG("testDrawPolygon.xml")
    drawWindow(file, grid)
    #add elements inside
    drawGrid(file,grid,"black")
    #Draw a polygon
    A=[10,10]
    B=[20,10]
    C=[30,20]
    D=[48,2]
    E=[40,25]
    F=[10,27]
    polygon=[A,B,C,D,E,F] 
    drawPolygon(file,grid,polygon,"red");
    randomPolygon=randomOrientedPolygon(grid)
    drawPolygon(file,grid,randomPolygon,"blue");
    #Close SVG file
    closeSVG(file)

#testDrawPolygon()

###################### coloriage d'un pixel (un petit carré de la grille) ############################################ 

# La fonction colorPixel colorie le pixel "pixel" qui se compose de deux coordonnées entières, par exemple pixel=[15,28] 
# Pour [15,28], on va par exemple colorier les petit carré avec des x allant d e15 à 16 et des y allant de 28 à 29.

def colorPixel(file, grid, pixel, color):
    #print("drawPixel")
    p=[int(pixel[0]),int(pixel[1])]
    A=[p[0],p[1]]
    B=[p[0],p[1]+1]
    C=[p[0]+1,p[1]+1]
    D=[p[0]+1,p[1]]
    file.write("<polyline points=\"")
    x,y=xyInSVG(grid, A)
    file.write(f"{x},{y}")
    x,y=xyInSVG(grid, B)
    file.write(f" {x},{y}")
    x,y=xyInSVG(grid, C)
    file.write(f" {x},{y}")
    x,y=xyInSVG(grid, D)
    file.write(f" {x},{y}")
    x,y=xyInSVG(grid, A)
    file.write(f" {x},{y}")
    stroke=0
    file.write(f"\" fill=\"{color}\" fill-opacity=\"0.8\" stroke=\"{color}\" stroke-width=\"{stroke}\" />\n")
    
# 9) Executez  testColorPixel()  
# Ouvrez le fichier "testColorPixel.xml" avec un navigateur

def testColorPixel():
    print("testColorPixel")
    #Begin SVG file
    grid=[15,50,30,20]
    #create SVG file
    file=createSVG("testColorPixel.xml")
    drawWindow(file, grid)
    #add elements inside
    drawGrid(file,grid,"black")
    #Color some pixels
    A=[10,10]
    B=[20,10]
    C=[30,20]
    D=[40,25]
    E=[10,27]
    drawGrid(file,grid,"black")
    colorPixel(file,grid,A,"purple")
    colorPixel(file,grid,B,"magenta")
    colorPixel(file,grid,C,"orange")
    colorPixel(file,grid,D,randomColor())
    colorPixel(file,grid,E,randomColorRgb())
    closeSVG(file)
    
#testColorPixel()

# 10) Executez  mosaic()  
# Ouvrez le fichier "testColorPixelRandom.xml" avec un navigateur
# Modifiez la fonction pour que 1 pixel sur deux soit noir (en damier...)

def mosaic():
    print("mosaic")
    #Begin SVG file
    grid=[15,100,100,20]
    #create SVG file
    file=createSVG("mosaic.xml")
    drawWindow(file, grid)
    #add elements inside
    drawGrid(file,grid,"black")
    for i in range(grid[1]):
         for j in range(grid[2]):
             pixel=[i,j]
             colorPixel(file,grid,pixel,randomColor())    
    closeSVG(file)
    
#mosaic()

#################################### tracé d'un cercle ############################################ 

# La fonction de tracé d'un cercle vide est drawCircle

def drawCircle(file, grid, center, radius, color):
    x,y=xyInSVG(grid, center)
    file.write(f"<circle cx=\"{x}\" cy=\"{y}\" r=\"{radius*grid[3]}\" stroke=\"{color}\" stroke-width=\"{0.1+grid[3]/10}\" fill=\"none\" />\n")
    drawPoint(file,grid,center,color)
    
# La fonction de tracé d'un disque est drawDisk

def drawDisk(file, grid, center, radius, color):
    x,y=xyInSVG(grid, center)
    file.write(f"<circle cx=\"{x}\" cy=\"{y}\" r=\"{radius*grid[3]}\" stroke=\"{color}\" stroke-width=\"{0.1+grid[3]/10}\" fill=\"{color}\" />\n")


# 11) Executez  testDrawCirclesAndDisks()  
# On affiche des cercles et des disques de différents rayon...
# Ouvrez le fichier "testDrawCircle.xml" avec un navigateur
# Modifiez quelques éléments....

def testDrawCirclesAndDisks():
    print("testDrawCirclesAndDisks")
    #Begin SVG file
    grid=[15,100,70,20]
    #create SVG file
    file=createSVG("testDrawCirclesAndDisks.xml")
    drawWindow(file, grid)
    #add elements inside
    #draws circles
    for i in range(1000):
        center=(random.randint(0,grid[1]),random.randint(0,grid[2]))
        r=random.randint(1,10)
        drawCircle(file,grid,center,r,randomColor())    
        center=(random.randint(0,grid[1]),random.randint(0,grid[2]))
        r=random.randint(1,4)
        drawDisk(file,grid,center,r,randomColor())
    closeSVG(file)
    
#testDrawCirclesAndDisks()

############################## Changer la couleur du fond  ########################################

def backgroundColor(file, grid, color):
    A=(-100,-100)
    B=(grid[1]+100,-100)
    C=(-100,grid[2]+100)
    D=(grid[1]+100,grid[2]+100)
    back=(A,B,D,C)
    drawPolygonOpacity(file,grid,back,color,1)
  

# 12) Executez  testBackGroundColor() 
# Un fond noir, ça peut être plus artistique...

def testBackgroundColor():
    print("testBackgroundColor")
    #Begin SVG file
    grid=[15,200,140,20]
    #create SVG file
    file=createSVG("testBackgroundColor.xml")
    drawWindow(file, grid)
    backgroundColor(file, grid, "black")
    S=randomSetOfPointsWithSeeds(grid,1000,10)
    for i in range(len(S)):   
        r=random.randint(1,6)
        drawDisk(file,grid,S[i],r,randomColor())
    closeSVG(file)
    
#testBackgroundColor()



############################### tracé d'une droite d'équation donnée ################################################

# la fonction de tracé d'une droite prend en entrée une équation de la droite donnée sous la forme
# d'une liste de trois coefficients [a,b,c] pour représenter la droite d'équation ax+by=c
# Si on veut tracer la droite d'équation 2x+y=5, il faut prendre line=[2,3,5]

def drawLine(file, grid, line, color):
    #print(line)
    a=line[0]
    b=line[1]
    c=line[2]
    if a==0 and b==0:
        #Ce n'est pas une equation de droite
        return
    #On calcule les 4 points d'intersection de la droite avec les droites x=0, x=grid[1], y=0, y=grid[1]
    #Si la droite est horizontale
    if a==0:
        if b*c>=0 and c<=b*grid[1]:
            y=c/b
            A=(0,y)
            B=(grid[1],y)
            drawSegment(file, grid, A,B, color)
        return
    #Si la droite est horizontale
    if b==0:
        if a*c>=0 and c<=a*grid[2]:
            x=c/a
            A=(x,-10)
            B=(x,grid[2]+10)
            drawSegment(file, grid, A,B, color)
        return
    y=(c-a*(-10))/b
    A=(-10,y)
    y=(c-a*(grid[1]+10))/b
    B=(grid[1]+10,y)
    drawSegment(file, grid, A,B, color)
    
# 13) Executez  testDrawLine()  
# On affiche des droites...
# Ouvrez le fichier "testDrawLine.xml" avec un navigateur
# Modifiez quelques éléments.... en décommantant par exemple la ligne u=random... 
# en passant le nombre de droites de 100 à 1000...

def testDrawLine():
    print("testDrawLine")
    #Begin SVG file
    grid=[15,100,70,20,1]
    #create SVG file
    file=createSVG("testDrawLine.xml")
    drawWindow(file, grid)
    #add elements inside
    backgroundColor(file, grid, "black")
    #drawGrid(file,grid,"black")
    #draws lines
    line1=[1,-1,0]
    drawLine(file,grid,line1,"red")
    line2=[1,1,grid[2]]
    drawLine(file,grid,line2,"blue")
    n=100
    cx=grid[1]/2
    cy=grid[2]/2
    for i in range(2*n):
        u=i
        #u=random.randint(0,2*n)
        a=math.cos(u*math.pi/n)
        b=math.sin(u*math.pi/n)
        line=(a,b,a*cx+b*cy+5)
        drawLine(file,grid,line,randomColor())
    closeSVG(file)
    
#testDrawLine()



############################### tracé d'une demi-droite donnée ################################################

# la fonction de tracé d'une demi-droite prend en entrée ray, sous la forme d'une liste
# avec ray[0] le point origine, et ray[1] la direction de la demi-droite...


def drawRay(file, grid, ray, color):
    x1,y1=xyInSVG(grid, ray[0])
    farPoint=[ray[0][0]+10000*ray[1][0],ray[0][1]+10000*ray[1][1]]
    x2,y2=xyInSVG(grid, farPoint)
    stroke=(1.1+grid[3]/10)
    file.write(f"<line x1=\"{x1}\" y1=\"{y1}\" x2=\"{x2}\" y2=\"{y2}\" stroke=\"{color}\" stroke-width=\"{stroke}\" />\n")
    drawPoint(file,grid,ray[0],color)

    
# 14) Executez  testDrawRay()  
# On affiche des demi-droites...
# Ouvrez le fichier "testDrawRay.xml" avec un navigateur
# Modifiez quelques éléments.... en décommantant par exemple la ligne u=random... 
# en passant le nombre de droites de 100 à 1000...

def testDrawRay():
    print("testDrawRay")
    #Begin SVG file
    grid=[15,100,70,20,1]
    #create SVG file
    file=createSVG("testDrawRay.xml")
    drawWindow(file, grid)
    #add elements inside
    backgroundColor(file, grid, "black")
    #drawGrid(file,grid,"black")
    #draws half-lines
    n=100
    cx=grid[1]/2
    cy=grid[2]/2
    for u in range(2*n):
        a=cx+7*math.cos(u*math.pi/n)
        b=cy+7*math.sin(u*math.pi/n)
        c=-math.cos((u+n/2)*math.pi/n)
        d=-math.sin((u+n/2)*math.pi/n)
        ray=((a,b),(c,d))
        drawRay(file,grid,ray,randomColor())
    for u in range(2*n):
        a=cx+25*math.cos(u*math.pi/n)
        b=cy+25*math.sin(u*math.pi/n)
        c=-math.cos((u-n/2)*math.pi/n)
        d=-math.sin((u-n/2)*math.pi/n)
        ray=((a,b),(c,d))
        drawRay(file,grid,ray,randomColor())
    closeSVG(file)
    
#testDrawRay()



############################### écriture de texte ################################################

def writeText(file, grid, text, size, position, color):
    x,y=xyInSVG(grid, position)
    file.write(f"<text x=\"{x}\" y=\"{y}\" font-size=\"{size}\" style=\"fill : {color} ;\" >{text} </text>\n")

# 1) Executez  testWriteText()  
# On affiche "the good", "the bad", "the ugly" sur un fond noir... à des positions aléatoires
# Puis ... par dessus "c'est facile à utiliser"...
# Modifier la position des textes affichés et la atille des polices.

def testWriteText():
    print("testWriteText")
    #Begin SVG file
    grid=[15,100,70,20,1]
    #create SVG file
    file=createSVG("testWriteText.xml")
    drawWindow(file, grid)
    #add elements inside
    backgroundColor(file, grid, "black")
    drawGrid(file,grid,"grey")
    #draws texts
    n=1000
    S=randomSetOfPoints(grid, n)
    for i in range(len(S)):
        if i%3==0:
            text="the good"
        if i%3==1:
            text="the bad"
        if i%3==2:
            text="the ugly"
        size=random.randint(25,60)
        writeText(file, grid, text, size, S[i], "grey")
    writeText(file, grid, "C'est facile a utiliser", 200, (10,40), "red")
    writeText(file, grid, "(mais sans accents)", 150, (25,25), "yellow")
    closeSVG(file)
    
#testWriteText()

################################### Just for packing ##########################################

def xyInSVGScale(grid,point,scale):
    x=grid[0]+point[0]*grid[3]/scale+grid[3]/2
    y=grid[0]+(grid[2]-point[1]/scale)*grid[3]+grid[3]/2
    return x,y

def drawPolygonScale(file, grid, polygon, scale, opacity, color):
    #print("drawPolygon")
    file.write("<polyline points=\"")
    x,y=xyInSVGScale(grid, polygon[0],scale)
    file.write(f"{x},{y}")
    #drawPoint(file,grid,polygon[i],color)
    for i in range(len(polygon)):
        x,y=xyInSVGScale(grid, polygon[i],scale)
        file.write(f" {x},{y}")
    x,y=xyInSVGScale(grid, polygon[0],scale)
    file.write(f" {x},{y}")
    stroke=(1.1+grid[3]/10)
    file.write(f"\" fill=\"{color}\" fill-opacity=\"{opacity}\" stroke=\"{color}\" stroke-width=\"{stroke}\" />\n")


def drawPolygonPosition(file, grid, polygon, position, color, opacity):
    #print("drawPolygon")
    file.write("<polyline points=\"")
    translatedVertex=(polygon[0][0]+position[0],polygon[0][1]+position[1])
    x,y=xyInSVG(grid, translatedVertex)
    file.write(f"{x},{y}")
    #drawPoint(file,grid,polygon[i],color)
    for i in range(len(polygon)):
        translatedVertex=(polygon[i][0]+position[0],polygon[i][1]+position[1])
        x,y=xyInSVG(grid, translatedVertex)
        file.write(f" {x},{y}")
    translatedVertex=(polygon[0][0]+position[0],polygon[0][1]+position[1])
    x,y=xyInSVG(grid, translatedVertex)
    file.write(f" {x},{y}")
    stroke=(1.1+grid[3]/10)
    file.write(f"\" fill=\"{color}\" fill-opacity=\"{opacity}\" stroke=\"{color}\" stroke-width=\"{stroke}\" />\n")
    
def drawPolygonPositionScale(file, grid, polygon, position, scale, color, opacity):
    #print("drawPolygon")
    file.write("<polyline points=\"")
    translatedVertex=(polygon[0][0]+position[0],polygon[0][1]+position[1])
    x,y=xyInSVGScale(grid, translatedVertex,scale)
    file.write(f"{x},{y}")
    #drawPoint(file,grid,polygon[i],color)
    for i in range(len(polygon)):
        translatedVertex=(polygon[i][0]+position[0],polygon[i][1]+position[1])
        x,y=xyInSVGScale(grid, translatedVertex,scale)
        file.write(f" {x},{y}")
    translatedVertex=(polygon[0][0]+position[0],polygon[0][1]+position[1])
    x,y=xyInSVGScale(grid, translatedVertex,scale)
    file.write(f" {x},{y}")
    stroke=(1.1+grid[3]/10)
    stroke=0
    file.write(f"\" fill=\"{color}\" fill-opacity=\"{opacity}\" stroke=\"{color}\" stroke-width=\"{stroke}\" />\n")

def drawPolygonPositionScaleInformation(file, grid, polygon, identity, position, quantity, cost, area, scale, color, opacity):
    #print("drawPolygon")
    file.write("<polyline points=\"")
    translatedVertex=(polygon[0][0]+position[0],polygon[0][1]+position[1])
    x,y=xyInSVGScale(grid, translatedVertex,scale)
    file.write(f"{x},{y}")
    #drawPoint(file,grid,polygon[i],color)
    for i in range(len(polygon)):
        translatedVertex=(polygon[i][0]+position[0],polygon[i][1]+position[1])
        x,y=xyInSVGScale(grid, translatedVertex,scale)
        file.write(f" {x},{y}")
    translatedVertex=(polygon[0][0]+position[0],polygon[0][1]+position[1])
    x,y=xyInSVGScale(grid, translatedVertex,scale)
    file.write(f" {x},{y}")
    stroke=(1.1+grid[3]/100)#should be 10
    file.write(f"\" fill=\"{color}\" fill-opacity=\"{opacity}\" stroke=\"white\" stroke-width=\"{stroke}\" >\n")
    file.write(f"<title>i={identity} at ({int(position[0])},{int(position[1])})\nq={quantity} cost={cost}\ncost/area={round(10000000000000000*cost/area,2)}</title></polyline>\n")

def drawArray(file, grid, a, step, scale, opacity):
    #drawPoint(file,grid,polygon[i],color)
    size=np.shape(a)
    largeur=size[0]
    hauteur=size[1]
    maxi=a.max()
    mini=a.min()
    
    for i in range(largeur):
        for j in range(hauteur):
            h=step/2
            square=[(i*step-h,j*step-h),(i*step+h,j*step-h),(i*step+h,j*step+h),(i*step-h,j*step+h)]
            value=a[i][j]
            if value>0:
                u=255*value/maxi
                color=colorRGB(255,255-u,255-u)
                drawPolygonScale(file, grid, square, scale, 0.7, color)
            if value<0:
                u=int(255*value/mini)
                color=colorRGB(255-u,255,255-u)
                drawPolygonScale(file, grid, square, scale, 0.7, color)
                
def drawPacking(file, grid, region, polygons, scale):
    def det(u,v):
        return u[0]*v[1]-u[1]*v[0]  
    def area(A,B,C):
        AB=(B[0]-A[0],B[1]-A[1])
        AC=(C[0]-A[0],C[1]-A[1])
        return det(AB,AC)
    def areaPolygon(vertices):
        n=len(vertices)
        area=0
        for i in range(n):
            j=(i+1)%n
            area=area-(vertices[j][0]-vertices[i][0])*(vertices[j][1]+vertices[i][1])
        return area   
    def finalResults(polygons):
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
    
    xmax=max(vertex[0] for vertex in region.vertices)
    ymax=max(vertex[1] for vertex in region.vertices)
    backgroundColor(file, grid, "grey")
    drawPolygonScale(file, grid, region.vertices, scale, 1, "white")
    for p in polygons:
        #print(p)
        if p.positions !=None:
            for position in p.positions:
                color=randomColor()
                drawPolygonPositionScaleInformation(file, grid, p.vertices, p.id, position, p.quantity, p.cost, p.area, scale, color, 0.7)
                #c=((p.centroid[0]+position[0])/scale,(p.centroid[1]+position[1])/scale)
                #drawPoint(file,grid,c,color)
        else:
            position=(scale*random.randint(int(xmax/scale)+20,int(xmax/scale)+70),scale*random.randint(0,grid[2]-10))
            drawPolygonPositionScaleInformation(file, grid, p.vertices, polygons.index(p), position, p.quantity, p.cost, p.area, scale, randomColor(), 0.3)

    cost,npacked,totalcost,totalquantities,areacovered=finalResults(polygons)
    v="{:.1f}".format(100*cost/totalcost)
    text1=f"cost={cost} / {totalcost}"
    size=60
    writeText(file, grid, text1, size,(xmax/scale+8,35), "white")
    writeText(file, grid, f"{v}%", size,(xmax/scale+18,30), "white")
    text2=f"{npacked} polygons packed / {totalquantities}"
    writeText(file, grid, text2, size,(xmax/scale+8,25), "white")
    w="{:.1f}".format(100*npacked/totalquantities)
    writeText(file, grid, f"{w}%", size,(xmax/scale+18,20), "white")
    w="{:.1f}".format(100*npacked/totalquantities)
    writeText(file, grid, f"covered area={areacovered}", size,(xmax/scale+8,15), "white")
    a=areaPolygon(region.vertices)
    w="{:.1f}".format(100*areacovered/a)
    writeText(file, grid, f"{w}%", size,(xmax/scale+18,10), "white")
    p=polygons[1]
    #drawPolygonPositionScaleInformation(file, grid, p.vertices, p.id,  (0,0), 1, p.cost, p.area, scale, "red", 0.2)


def drawPackingSlates(file, grid, region, polygons, scale, tog):
    def det(u,v):
        return u[0]*v[1]-u[1]*v[0]  
    def area(A,B,C):
        AB=(B[0]-A[0],B[1]-A[1])
        AC=(C[0]-A[0],C[1]-A[1])
        return det(AB,AC)
    def areaPolygon(vertices):
        n=len(vertices)
        area=0
        for i in range(n):
            j=(i+1)%n
            area=area-(vertices[j][0]-vertices[i][0])*(vertices[j][1]+vertices[i][1])
        return area   
    def finalResults(polygons):
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
    
    xmax=max(vertex[0] for vertex in region.vertices)
    ymax=max(vertex[1] for vertex in region.vertices)
    backgroundColor(file, grid, "white")
    drawPolygonScale(file, grid, region.vertices, scale, 1, "black")
    
    for indicesandcoordinates in tog:
        color=randomColor()
        for abc in indicesandcoordinates:
            i=abc[0]
            position=(abc[1],abc[2])
            drawPolygonPositionScaleInformation(file, grid, polygons[i].vertices, polygons[i].id, position, polygons[i].quantity, polygons[i].cost, polygons[i].area, scale, color, 1)
            #c=((p.centroid[0]+position[0])/scale,(p.centroid[1]+position[1])/scale)
            #drawPoint(file,grid,c,color)
    
def drawPackingblack(file, grid, region, polygons, scale):
    def det(u,v):
        return u[0]*v[1]-u[1]*v[0]  
    def area(A,B,C):
        AB=(B[0]-A[0],B[1]-A[1])
        AC=(C[0]-A[0],C[1]-A[1])
        return det(AB,AC)
    def areaPolygon(vertices):
        n=len(vertices)
        area=0
        for i in range(n):
            j=(i+1)%n
            area=area-(vertices[j][0]-vertices[i][0])*(vertices[j][1]+vertices[i][1])
        return area   
    def finalResults(polygons):
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
    
    xmax=max(vertex[0] for vertex in region.vertices)
    ymax=max(vertex[1] for vertex in region.vertices)
    backgroundColor(file, grid, "white")
    drawPolygonScale(file, grid, region.vertices, scale, 1, "black")

    for p in polygons:
         #print(p)
         if p.positions !=None:
             for position in p.positions:
                 color=randomColor()
                 drawPolygonPositionScale(file, grid, p.vertices, position, scale, color, 1)
                 
def drawPackingblackslates(file, grid, region, polygons, scale,tog):
    def det(u,v):
        return u[0]*v[1]-u[1]*v[0]  
    def area(A,B,C):
        AB=(B[0]-A[0],B[1]-A[1])
        AC=(C[0]-A[0],C[1]-A[1])
        return det(AB,AC)
    def areaPolygon(vertices):
        n=len(vertices)
        area=0
        for i in range(n):
            j=(i+1)%n
            area=area-(vertices[j][0]-vertices[i][0])*(vertices[j][1]+vertices[i][1])
        return area   
    def finalResults(polygons):
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
    
    xmax=max(vertex[0] for vertex in region.vertices)
    ymax=max(vertex[1] for vertex in region.vertices)
    backgroundColor(file, grid, "white")
    drawPolygonScale(file, grid, region.vertices, scale, 1, "black")

    for p in polygons:
         #print(p)
         if p.positions !=None:
             for position in p.positions:
                 color=randomColor()
                 drawPolygonPositionScale(file, grid, p.vertices, position, scale, color, 1)
                 
    for indicesandcoordinates in tog:
        color=randomColor()
        for abc in indicesandcoordinates:
            i=abc[0]
            position=(abc[1],abc[2])
            drawPolygonPositionScale(file, grid, polygons[i].vertices, position, scale, color, 1)


    

