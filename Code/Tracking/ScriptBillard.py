# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 16:57:05 2022

@author: bperr

Script billard
"""

import ModuleTracking
import Reconstruction3D
import SubImMoy

import cv2
import numpy as np

# Script d'éxécution pour le billard : on trouve l'homographie et on affiche la camera avec les deux coordonées

camera = cv2.VideoCapture(0)
upper,lower,zero = ModuleTracking.getParameters(10) # 10  : billard sans soustraction
largeur = 395
longueur = 800
epaisseurBord = 55
diametre = 61.5

hg,imgFond = Reconstruction3D.getHomographyForBillard(camera,upper,lower,(largeur,longueur),epaisseurBord,diametre)


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
        
        cv2.imshow('Image camera',frame)
        
        # Projection
        imf = imgFond.copy()
        x = realCenter[0]+epaisseurBord+largeur/2
        y = realCenter[1]+epaisseurBord+longueur/2
        xR = round(x,1)
        yR = round(y,1)
        c = (int(x),int(y))
        
       
        cv2.circle(imf,c,20,(0,0,255),-1)
        cv2.putText(imf,"Coordonees : "+str(realCenterRound),(20,35),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,0,255),2)
        cv2.imshow('Image projetee',imf)
    
    if key==ord('q'): # quitter avec 'q'
        break
