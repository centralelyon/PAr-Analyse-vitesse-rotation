# -*- coding: utf-8 -*-
"""
Module reconstruction 3D
@author Baptiste Perreyon, Guillaume Paczek

"""

import numpy as np
import cv2

"""
## Récupération des données intrinsèques de la caméra, stockées dans un fichier à part

@return mtx : matrice intrinsèque de la caméra (focales et centre optiques)
        dist : coefficients de distorsion de la caméra
"""
def loadDistortionData():
    distorsionData = np.load("IntrisicParameters.npz")
    mtx=distorsionData['mtx']
    dist = distorsionData['dist']
    return mtx,dist


"""
## Dé-distord l'image en utilisant les paramètres de la caméra et la redimensionne

@param frame : image à traiter
       mtx : matrice intrinsèque de la caméra (focales et centre optiques)
       dist : coefficients de distorsion de la caméra
       newMtx : matrice de la caméra optimisée
       roi : region of interest, partie de l'image à garder, fournie par cv2.getOptimalNewCameraMatrix
@return frameRect : Image traitée pour effacer la distorstion
"""
def distCorrection(frame,mtx,dist,newMtx,roi):
    frameRect = cv2.undistort(frame,mtx,dist,None,newMtx)
    x, y, w, h = roi
    frameRect = frameRect[y:y+h, x:x+w]
    return frameRect


"""
## Renvoie - après validation par l'utilisateur - la position d'une bille placée dans un des coins de la table de billard par l'utilisateur.

@param camera : objet VideoCapture qui vient d'une caméra
       upper : borne supérieure dans l'espace de couleur HSV dans laquelle on va rechercher la balle
       lower : borne inférieure dans l'espace de couleur HSV dans laquelle on va rechercher la balle
       location : angle de la table où l'utilisateur doit placer la bille (chaine de caractères)
@return center : position (X,Y) de la bille sur l'image (en pixels)
"""
def addPoint(camera,upper,lower,location):
    print("Placer la bille rouge dans le coin "+location+" puis validez avec la barre d'espace ou la touche entrée")
    while True:
        key = cv2.waitKey(1)
        (grabbed,frame)=camera.read()
        
        #cv2.imshow('frame',frame)
        
        #floutage pour éliminer les effets des hautes fréquences
        blurred=cv2.GaussianBlur(frame,(5,5),0)
        #convert to hsv
        hsv=cv2.cvtColor(blurred,cv2.COLOR_BGR2HSV)
        #construction du masque de couleur
        mask=cv2.inRange(hsv,lower,upper)
        #cv2.imshow("mask",mask)
        #recherche de contour
        cnts = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
        
        #si on a trouvé des contours, on trouve le plus grand et on en déduit centroide+cercle ausculateur
        if len(cnts):
            imcont2=cv2.drawContours(frame, cnts, -1, (0,255,0), 1 )
            cv2.imshow("Contours sélectionnés",imcont2)
            
            c = max(cnts, key=cv2.contourArea)
            ((x,y),radius)= cv2.minEnclosingCircle(c)
            M=cv2.moments(c)
            if M["m00"] and M["m00"]:
                center= ( int(M["m10"]/M["m00"]) , int(M["m01"]/M["m00"]))
            
            if radius < 10 and not (center is None): #j'ai enlevé la condition "radius >3". Changer ce critère
                cv2.circle(frame,(int(x),int(y)),int(radius), (0,255,255),2)
                cv2.circle(frame,center,5,(0,0,255),-1)
        else:
            cv2.imshow("Contours sélectionnés",frame)
        
        if key==ord(' ') or key==ord("\r"): # Validation par l'utilisateur
            break
    cv2.destroyAllWindows()
    return center


"""
## Trouve une homographie entre le plan de l'image de la caméra et une vue de dessus de la table de billard

@param camera : objet VideoCapture qui vient d'une caméra
       upper : borne supérieure dans l'espace de couleur HSV dans laquelle on va rechercher la balle
       lower : borne inférieure dans l'espace de couleur HSV dans laquelle on va rechercher la balle
       dimensions : dimensions (largeur,longueur) de la table de billard en mm
       epaisseurBord : épaisseur du bord de la table en mm
       diametre : diametre de la bille en mm
       
@return homography : matrice d'homographie entre les deux plans
"""
def getHomographyForBillard(camera,upper,lower,dimensions,epaisseurBord,diametre):
    # Liste des positions sur l'image
    igc = addPoint(camera,upper,lower,"inférieur gauche")
    idc = addPoint(camera,upper,lower,"inférieur droit")
    sgc = addPoint(camera,upper,lower,"supérieur gauche")
    sdc = addPoint(camera,upper,lower,"supérieur droit")
    coordPixel=np.array([list(igc),list(idc),list(sgc),list(sdc)])
    
    # Liste des postions dans l'espace, le coin inférieur gauche est (0,0) mais on doit ajouter un décalage du à la taille de la bille
    dx = np.sqrt(2)/4*diametre
    coordReel=np.array([[2*epaisseurBord+dx,2*epaisseurBord+dx],[2*epaisseurBord+dimensions[0]-dx,2*epaisseurBord+dx],[2*epaisseurBord+dx,2*epaisseurBord+dimensions[1]-dx],[2*epaisseurBord+dimensions[0]-dx,2*epaisseurBord+dimensions[1]-dx]])
    
    # Calcul de l'homographie
    h, status = cv2.findHomography(coordPixel,coordReel)
    
    if status.all():
        translate = np.array([[1,0,-epaisseurBord],[0,1,-epaisseurBord],[0,0,1]])
        homography = translate.dot(h)
    else:
        print("Erreur, on recommence")
        homography = getHomographyForBillard(camera, upper, lower, dimensions, epaisseurBord, diametre)
        return homography
    
    # Vérification par l'utilisateur que tout a bien fonctionné
    print("Retirez la boule puis validez avec la barre d'espace ou la touche entrée")
    while True:
        key = cv2.waitKey(1)
        grabbed,frame = camera.read()
        cv2.imshow('frame',frame)
        if key==ord(' ') or key==ord("\r"): # Validation par l'utilisateur
            break
    cv2.destroyAllWindows()
    
    dim=(dimensions[0]+2*epaisseurBord,dimensions[1]+2*epaisseurBord)
    imReg = cv2.warpPerspective(frame,homography,dim)
    cv2.imshow('Image rectifiée',imReg)
    print("L'image est-elle correctement projetée ? [y/n]")
    isOK=True
    while True:
        k = cv2.waitKey(1)
        if k==ord('y'):
            cv2.destroyAllWindows()
            isOK=True
            break
        elif k==ord('n'):
            cv2.destroyAllWindows()
            isOK=False
            break
    
    if not isOK:
        homography = getHomographyForBillard(camera,upper,lower,dimensions,epaisseurBord,diametre)
        return homography
        
    return homography


"""
## Détermine les coordonées réelles d'un point à partir de l'homographie calculée

@param coord : coordonées de l'objet en pixel
       homography : matrice d'homographie entre le plan de la caméra et une vu de dessus de la table
       dimensions : dimensions (largeur,longueur) de la table de billard en mm
       epaisseurBord : épaisseur du bord de la table en mm
       
@return (x,y) : coordonées de la bille dans le repère centré sur le centre de la table
"""
def findRealCoordinatesBillard(coord,homography,dimensions,epaisseurBord):
    # Coordonées homogènes pour appliquer la transformation
    coordHomogenes = np.array(list(coord)+[1])
    # Application de l'homographie
    newCoordHomogenes = np.dot(homography,coordHomogenes)
    # Transformation en coordonées réelles
    x,y=newCoordHomogenes[0]/newCoordHomogenes[2],newCoordHomogenes[1]/newCoordHomogenes[2]
    # Placement dans le repère (centre de la table de billard)
    x = x-epaisseurBord-dimensions[0]/2
    y = y-epaisseurBord-dimensions[1]/2
    
    return (x,y)


"""
## Affiche l'image de fond (rectangle noir) pour que l'utilisateur positionne la table

@param img : image de fond
       fenetre : nom de la fenetre OpenCV
"""
def positionnerTable(img,fenetre):
    print("Veuillez positioner l'intérieur de la table dans le rectangle")
    cv2.imshow(fenetre,img)
    while True:
        k = cv2.waitKey(1)
        if k ==ord('q'):
            cv2.destroyAllWindows()
            break


"""
## Trace la trajectoire en reliant une liste de points

@param listPos : liste des positions de la bille à afficher
       imFond : image de fond sur laquelle on trace la trajectoire
       fenetre : nom de la fenetre OpenCV
"""
def affTraj(listPos,imFond,fenetre):
    color = (0,0,0)
    for i in range (len(listPos)-1):
        cv2.line(imFond,listPos[i],listPos[i+1],color,5)

    
"""
## Trace la trajectoire en pointillés

@param listPos : liste des positions de la bille à afficher
       imFond : image de fond sur laquelle on trace la trajectoire
       fenetre : nom de la fenetre OpenCV
"""
def affTrajPrevis(listPos,imFond,fenetre):
    color = (0,0,0)
    for i in range (len(listPos)):
        cv2.circle(imFond,(listPos[i]),15,color,-1)
    

"""
## Transforme les coordonnées réelles en coordonées sur l'image à afficher
@param coord : tuple des coordonnées réelles
       l : largeur de la table de billard
       L : longueur de la table de billard
       coin1 : position du coin supérieur gauche de la table sur l'image de fond
       coin2 : position du coin inférieur droit de la table sur l'image de fond
       
@return x4 : abscisse de la bille sur l'image projetée
        y4 : ordonnée de la bille sur l'image projetée
"""
def getCoordProjection(coord,l,L,coin1,coin2):   
    xreel,yreel = coord
    #Translation de l'origine du repere dans le coin
    x2 = xreel+l/2
    y2 = yreel+L/2
    # Rotation de l'image <=> inversion des coordonees
    x3,y3=y2,x2
    # mise a l'echelle
    coefX = (coin2[0]-coin1[0])/L
    coefY = (coin2[1]-coin1[1])/l
    x4=coin1[0]+int(round(x3*coefX))
    y4=coin1[1]+int(round(y3*coefY))
    #print(x4,y4)
    return (x4,y4)


"""
## Indique si la bille est en mouvement ou à l'arrêt

@param pos : liste de position de la balle
       seuil : distance maximale à la dernière position de la bille pour considérer que la bille est à l'arrêt

@return immobile : booléen indiquant si la bille est arrêtée ou non
"""
def detectionArret(pos,seuil): # Liste de position dont la taille a été réglée par l'ajout ponctuel de positions
    lastPos = pos[-1]
    nbpos = len(pos)
    immobile = True
    i=0
    while immobile and i<nbpos-1:
        if (pos[i][0]-lastPos[0])**2+(pos[i][1]-lastPos[1])**2>seuil**2:
            immobile = False
        i=i+1
    return immobile