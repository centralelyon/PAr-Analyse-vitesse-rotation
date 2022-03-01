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
    print("Placer la bille dans le coin "+location+" puis validez avec la barre d'espace ou la touche entrée")
    while True:
        key = cv2.waitKey(1)
        (grabbed,frame)=camera.read()
        cv2.imshow('frame',frame)
        
        #floutage pour éliminer les effets des hautes fréquences
        blurred=cv2.GaussianBlur(frame,(5,5),0)
        #convert to hsv
        hsv=cv2.cvtColor(blurred,cv2.COLOR_BGR2HSV)
        #construction du masque de couleur
        mask=cv2.inRange(hsv,lower,upper)
        cv2.imshow("mask",mask)
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
       diametre : diametre de la bille en mm
@return homography : matrice d'homographie entre les deux plans
        newDim : dimensions de l'image de sortie (en pixels)
"""

def getHomographyForBillard(camera,upper,lower,dimensions,diametre):
    # Liste des positions sur l'image
    igc = addPoint(camera,upper,lower,"inférieur gauche")
    idc = addPoint(camera,upper,lower,"inférieur droit")
    sgc = addPoint(camera,upper,lower,"supérieur gauche")
    sdc = addPoint(camera,upper,lower,"supérieur droit")
    coordPixel=np.array([list(igc),list(idc),list(sgc),list(sdc)])
    
    # Liste des postions dans l'espace, le coin inférieur gauche est (0,0) mais on doit ajouter un décalage du à la taille de la bille
    dx = np.sqrt(2)/4*diametre
    coordReel=np.array([[dx,dx],[dimensions[0]-dx,dx],[dx,dimensions[1]-dx],[dimensions[0]-dx,dimensions[1]-dx]])
    
    # Calcul de l'homographie
    factor = 0.15
    translate = np.array([[1,0,factor*1000],[0,1,factor*500],[0,0,1]])
    h, status = cv2.findHomography(coordPixel,coordReel)
    homography = translate.dot(h)
    newDim = (int(factor*5000),int(factor*6500))
    
    # Juste pour vérification, à supprimer après
    grabbed,frame = camera.read()
    imReg = cv2.warpPerspective(frame,homography,newDim)
    cv2.imshow('rect',imReg)
    
    return homography,newDim
