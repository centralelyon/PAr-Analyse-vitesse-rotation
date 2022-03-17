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


import cv2
import numpy as np
import time as t
import screeninfo
import json


def positionnerTable(img,fenetre):
    print("Veuillez positioner l'intérieur de la table dans le rectangle")
    cv2.imshow(fenetre,img)
    while True:
        k = cv2.waitKey(1)
        if k ==ord('q'):
            cv2.destroyAllWindows()
            break

def affTraj(listPos,imFond,fenetre):
    color = (0,0,0)
    for i in range (len(listPos)-1):
        cv2.line(imFond,listPos[i],listPos[i+1],color,5)
        
def affTrajPrevis(listPos,imFond,fenetre):
    color = (0,0,0)
    for i in range (len(listPos)):
        cv2.circle(imFond,(listPos[i]),15,color,-1)
    
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



# # Script d'éxécution pour le billard  # #
# On place le billard par rapport au vidéoprojecteur (rectangle)
# On trouve l'homographie entre le plan de la caméra et les coordonées réelles
# On projete en temps réel la position de la balle et on laisse la possibilité de rejouer un coup


# Récupération de tout les paramètres

with open('AllData.json') as file:
    allData = json.load(file) # allData est un dictionnnaire contenant tout les paramètres.



screen = screeninfo.get_monitors()[0]
height,width = screen.height,screen.width
coin1 = (150,150)
coin2 = (int(allData["coefRectangleX2"]*width),int(allData["coefRectangleY2"]*height))
fond = np.ones((height,width,3))
fond = cv2.rectangle(fond,coin1,coin2,(0,0,0),5)


# Full screen et affiché par dessus les autres fenêtres dès le début
window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
positionnerTable(fond,window_name)


camera = cv2.VideoCapture(1)
upper,lower = allData["upperBornRed"], allData["lowerBornRed"]
largeur = allData["largeurBillard"]
longueur = allData["longueurBillard"]
epaisseurBord = allData["epaisseurBordBillard"]
diametre = allData["diametreBille"]

isOK=False

while not isOK:
    answer = input("Voulez vous utiliser la matrice d'homographie sauvegardée ou alors la déterminer à nouveau ? [y/n]")
    if answer=="y":
        hg = np.array(allData["homography"])
        isOk = True
    elif answer=="n":
        hg = Reconstruction3D.getHomographyForBillard(camera,upper,lower,(largeur,longueur),epaisseurBord,diametre)
        allData["homography"] = hg
        isOk=True
        


#redéfinition car cv2.destroyAllWIndows dans positionnerTable a supprimé les propriétés
window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
#cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)



listPos=[]
listPosProj=[]
listTimeAdd=[]
tempsTrace = allData["tpsTraceTrajectoire"]

tempsAjoutTrajectoire=allData["tpsAjoutTrajectoire"] #pour la sauvegarde de trajectoire et la détection d'arret, on regarde toutes les 0.2 sec
tempsDetectionArret=allData["tpsArret"] #critère d'arret: 2 sec immobile
seuil = allData["seuilArret"] #critère d'arret: pas de variation de + de 10 mm


instantDernierAjout=t.time()
derniereTrajectoire=[] #enregistre complètement la dernière trajectoire, chaque tempsAjoutTrajectoire
finTrajectoire=[] #enregistre les dernières positions de la trajectoire, chaque tempsAjoutTrajectoire
trajectoiresSauvegardees=[]
arret=False
positionArret=(0,0)

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
            currentTime = t.time()
            listTimeAdd.append(currentTime)

            #traitement de la trajectoire à tracer: 
            if (currentTime-listTimeAdd[0]>tempsTrace):
                listPosProj.pop(0)
                listTimeAdd.pop(0)
                
            affTraj(np.array(listPosProj),fond2,window_name)
            
            #traitement de la trajectoire à sauvegarder
            if (currentTime-instantDernierAjout>tempsAjoutTrajectoire): 
                instantDernierAjout=t.time()
                
                derniereTrajectoire.append(realCenter)
                finTrajectoire.append(realCenter) 
                
                if len(finTrajectoire)>=tempsDetectionArret/tempsAjoutTrajectoire: #la détection de l'arret ne se fait que sur la fin de la trajectoire
                    finTrajectoire.pop(0)
                    
        
        #detection arret
        if arret:
            cv2.putText(fond2,"A l'arret",( coin2[0] +250,400),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 255), 2)
            # 250, 400 : déterminés pour le PC de la salle Amigo : à transformer en coef * screen.width ou screen.height
            if  not(detectionArret(finTrajectoire, seuil)): #si on se met à bouger, on commence une nouvelle trajectoire
                #réinitialiser et initialiser les liste de tracking
                finTrajectoire=[positionArret]
                derniereTrajectoire=[positionArret]
                arret=False
    
        else:
            cv2.putText(fond2,"En mouvement",( coin2[0] +250 ,400),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 200, 0), 2)
            # 250, 400 : déterminés pour le PC de la salle Amigo : à transformer en coef * screen.width ou screen.height
            #on n'autorise que des mouvements de + d'1 sec. (arbitraire)
            if  len(finTrajectoire)>=tempsDetectionArret/(2*tempsAjoutTrajectoire) and detectionArret(finTrajectoire, seuil): #si on passe à l'arret, on sauvegarde la position d'arret
                positionArret=realCenter
                arret=True
        
        #sauvegarde
        if key==ord("s") and arret:
            trajectoiresSauvegardees.append(derniereTrajectoire)
            
        #passage au mode 1
        if key==ord("r"):
            mode=1
            
        
        
        
    if mode == 1:
        cv2.putText(fond2,"Selection coup",( coin2[0]+250 ,400),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 255, 0), 2)
        # 250, 400 : déterminés pour le PC de la salle Amigo : à transformer en coef * screen.width ou screen.height
        #sélection rapide avec les numéros du clavier,
        #dans le futur: prévisualisation et sélection avec des flèches
    
    
    cv2.imshow(window_name,fond2)
    
    if key==ord('q'): # quitter avec 'q'
        cv2.destroyAllWindows()
        break


# Sauvegarde d'éventuelles modifications des paramètres de AllData
with open('AllData.json', 'w') as file:
	json.dump(allData, file)
    