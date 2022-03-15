# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 16:57:05 2022

@author: bperr

Script billard
"""


"""
screen : 3840 2160
    ig 0 0  --> 0 0
    id 126 1553 --> 0.0052 0.7366
    sg 2987 104 --> 0.8146 0
    sd 2973 1548 --> 0.7953 0.7542
    
    en ccl 0.77604 0.71782
"""

import ModuleTracking
import Reconstruction3D
import SubImMoy

import cv2
import numpy as np
import time as t
import screeninfo




def positionnerTable(w,h,fenetre):
    print("Veuillez positioner l'intérieur de la table dans le rectangle")
    img = np.ones((h,w,3))
    color = (0,0,0)
    cv2.rectangle(img,(150,150),(int(0.77604*w),int(0.71782*h)),color,5)
    cv2.imshow(fenetre,img)
    while True:
        k = cv2.waitKey(1)
        if k ==ord('q'):
            cv2.destroyAllWindows()
            break

def affTraj(listPos,imFond,fenetre):
    color = (0,0,0)
    for i in range (len(listPos)):
        cv2.circle(imFond,(listPos[i]),3,color,-1)
    h,w = np.shape(imFond)[:2]
    cv2.rectangle(imFond,(150,150),(int(0.77604*w),int(0.71782*h)),color,10)
    
def getCoordProjection(coord,l,L,w,h):   
    xreel,yreel = coord
    #Translation de l'origine du repere dans le coin
    x2 = xreel+l/2
    y2 = yreel+L/2
    # Rotation de l'image <=> inversion des coordonees
    x3,y3=y2,x2
    # mise a l'echelle
    coefX = (w*0.77604-150)/L
    coefY = (h*0.71782-150)/l
    x4=150+int(round(x3*coefX))
    y4=150+int(round(y3*coefY))
    print(x4,y4)
    return (x4,y4)

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



# Script d'éxécution pour le billard : on trouve l'homographie et on affiche la camera avec les deux coordonées

screen = screeninfo.get_monitors()[0]
height,width = screen.height,screen.width
fond = np.ones((height,width,3))
window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
positionnerTable(width, height,window_name)


camera = cv2.VideoCapture(1)
upper,lower,zero = ModuleTracking.getParameters(10) # 10  : billard sans soustraction
largeur = 395
longueur = 800
epaisseurBord = 55
diametre = 61.5

hg = Reconstruction3D.getHomographyForBillard(camera,upper,lower,(largeur,longueur),epaisseurBord,diametre)


#redéfinition car cv2.destroyAllWIndows dans positionnerTable a supprimé les propriétés
window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)



listPos=[]
listPosProj=[]
listTimeAdd=[]
tempsTrace = 3

tempsAjoutTrajectoire=0.2 #pour la sauvegarde de trajectoire et la détection d'arret, on regarde toutes les 0.2 sec
tempsDetectionArret=2 #critère d'arret: 2 sec immobile
seuil = 10 #critère d'arret: pas de variation de + de 10 mm


instantDernierAjout=t.time()
derniereTrajectoire=[] #enregistre complètement la dernière trajectoire, chaque tempsAjoutTrajectoire
finTrajectoire=[] #enregistre les dernières positions de la trajectoire, chaque tempsAjoutTrajectoire
trajectoiresSauvegardees=[]
arret=False

mode = 0


while True:
    key = cv2.waitKey(1)
    fond2 = fond.copy()
    
    
    if mode == 0:
        grabbed,frame = camera.read()
        
        center = ModuleTracking.trackingBillard(frame,upper,lower)
        
        if center !=None:
            #Caméra
            realCenter = Reconstruction3D.findRealCoordinatesBillard(center,hg,(largeur,longueur),epaisseurBord)
                    
            listPosProj.append(getCoordProjection(realCenter,largeur,longueur,width,height))
            listTimeAdd.append(t.time())
            currentTime = t.time()
            
            #traitement de la trajectoire à tracer: 
            if (currentTime-listTimeAdd[0]>tempsTrace):
                listPosProj.pop(0)
                listTimeAdd.pop(0)
            
            affTraj(np.array(listPosProj),fond,window_name)
            
            #traitement de la trajectoire à sauvegarder, détection de l'arret
            if (currentTime-instantDernierAjout>tempsAjoutTrajectoire): 
                instantDernierAjout=t.time()
                
                derniereTrajectoire.append(realCenter)
                finTrajectoire.append(realCenter) 
                
                if len(finTrajectoire)>=tempsDetectionArret/tempsAjoutTrajectoire: #la détection de l'arret ne se fait que sur la fin de la trajectoire
                    finTrajectoire.pop(0)
                    
        
        #detection arret
        if arret:
            cv2.putText(fond2,"A l'arret",(150 + width/0.77604 +200,50),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
            if  not(detectionArret(finTrajectoire, seuil)): #si on se met à bouger, on commence une nouvelle trajectoire
                #réinitialiser et initialiser les liste de tracking
                finTrajectoire=[positionArret]
                derniereTrajectoire=[positionArret]
                arret=False
    
        else:
            cv2.putText(fond2,"En mouvement",(150 + width/0.77604 +200,50),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
            if detectionArret(finTrajectoire, seuil): #si on passe à l'arret, on sauvegarde la position d'arret
                positionArret=realCenter
                arret=True
        
        
        # if  not(detectionArret(finTrajectoire, seuil)) and arret: #si on se met à bouger, on commence une nouvelle trajectoire
        #     #réinitialiser et initialiser les liste de tracking
        #     finTrajectoire=[positionArret]
        #     derniereTrajectoire=[positionArret]
        #     arret=False
        #     cv2.putText(imFond2,"En mouvement",(150 + width/0.77604 +200,20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
            
        # if detectionArret(finTrajectoire, seuil) and not arret: #si on passe à l'arret, on sauvegarde la position d'arret
        #     positionArret=realCenter
        #     arret=True
        #     cv2.putText(imFond2,"A l'arret",(150 + width/0.77604 +200,20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        
        
        #sauvegarde
        if key==ord("s") and arret:
            trajectoiresSauvegardees.append(derniereTrajectoire)
            
        #passage au mode 1
        if key==ord("r"):
            mode=1
            
        
        
        
    if mode == 1:
        cv2.putText(fond2,"Selection coup",(150 + width/0.77604 + 200,20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        #sélection rapide avec les numéros du clavier,
        #dans le futur: prévisualisation et sélection avec des flèches
    
    
    cv2.imshow(window_name,fond2)
    
    if key==ord('q'): # quitter avec 'q'
        cv2.destroyAllWindows()
        break

