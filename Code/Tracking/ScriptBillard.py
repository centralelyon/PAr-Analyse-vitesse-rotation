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
    imFond2=imFond.copy()
    color = (0,0,0)
    thickness = 5
    for i in range (len(listPos)-1):
        cv2.line(imFond2,listPos[i],listPos[i+1],color,thickness)
    h,w = np.shape(imFond2)[:2]
    cv2.rectangle(imFond2,(150,150),(int(0.77604*w),int(0.71782*h)),color,10)
    cv2.imshow(fenetre,imFond2)
    
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

hg,imgFond = Reconstruction3D.getHomographyForBillard(camera,upper,lower,(largeur,longueur),epaisseurBord,diametre)


window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)



listPos=[]
listPosProj=[]
listTimeAdd=[]
tempsTrace = 3

while True:
    key = cv2.waitKey(1)
    grabbed,frame = camera.read()
    
    center = ModuleTracking.trackingBillard(frame,upper,lower)
    
    if center !=None:
        #Caméra
        realCenter = Reconstruction3D.findRealCoordinatesBillard(center,hg,(largeur,longueur),epaisseurBord)
        realCenterRound=(round(realCenter[0],1),round(realCenter[1],1))
        cv2.circle(frame,center,5,(0,0,255),-1)
        cv2.putText(frame,"Coordonees pixels : "+str(center),(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,0,255),2)
        cv2.putText(frame,"Coordonees reeles : "+str(realCenterRound),(50,80),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,0,255),2)
        
        #cv2.imshow('Image camera',frame)
        
        # Projection
        # x = realCenter[0]+epaisseurBord+largeur/2
        # y = realCenter[1]+epaisseurBord+longueur/2
        # xR = round(x,1)
        # yR = round(y,1)
        # c = (int(x),int(y))        
        #cv2.circle(imf,c,20,(0,0,255),-1)
        #cv2.putText(imf,"Coordonees : "+str(realCenterRound),(20,35),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,0,255),2)
        #cv2.imshow('Image projetee',imf)
        
        listPos.append(realCenter)
        listPosProj.append(getCoordProjection(realCenter,largeur,longueur,width,height))
        listTimeAdd.append(t.time())
        currentTime = t.time()
        if (currentTime-listTimeAdd[0]>tempsTrace):
            listPosProj.pop(0)
            listTimeAdd.pop(0)
        
        
        affTraj(np.array(listPosProj),fond,window_name)
    
    if key==ord('q'): # quitter avec 'q'
        cv2.destroyAllWindows()
        break

