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
import time as t
import screeninfo

# Ext : 91.5 x 51
# Int : 80 x 39.5

def onClick(event,x,y,flags,params):
    if event==cv2.EVENT_LBUTTONDOWN:
        print(x,y)
        img=image.copy()
        cv2.circle(img,(x,y),2,(255,0,0),-1)
        cv2.putText(img,str(x)+"-"+str(y),(20,20),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,0,255),2)
        cv2.imshow(window_name,img)

def positionnerTable(dimInt,dimExt):
    img = np.zeros((1080,1920,3))
    color = (255,255,255)
    bordX=45
    bordY=10
    corner1 = (bordX,bordY)
    corner2 = (bordX+dimExt[0]*2,bordY+dimExt[1]*2)
    
    corner3= (bordX+(dimExt[0]-dimInt[0]),bordY+(dimExt[1]-dimInt[1]))
    corner4 = (corner3[0]+dimInt[0]*2,corner3[1]+dimInt[1]*2)
    
    # Extérieur
    cv2.rectangle(img,corner1,corner2,color,5)
    # Intérieur
    cv2.rectangle(img,corner3,corner4,color,5)
    cv2.imshow('rect',img)

def affTraj(listPos,imFond):
    imgFond=imFond.copy()
    color = (255,255,255)
    thickness = 5
    for i in range (len(listPos)-1):
        cv2.line(imgFond,listPos[i],listPos[i+1],color,thickness)
    #cv2.namedWindow("Projection", cv2.WND_PROP_FULLSCREEN)          
    #cv2.setWindowProperty("Projection", cv2.WND_PROP_FULLSCREEN, cv2.CV_WINDOW_FULLSCREEN)
    cv2.imshow('Projection',imgFond)
    
def getCoordProjection(coord):
    
    coordArray=np.array([coord[0],coord[1]])
    rotation = np.array([[0,1],[1,0]])
    scaling = np.array([[1080/505 , 0],[0 , 1920/910]])
    coordP = np.dot(np.dot(scaling,rotation),coordArray)
    
    coordRounded = (int(round(coordP[0])),int(round(coordP[1])))
    return coordRounded



# Script d'éxécution pour le billard : on trouve l'homographie et on affiche la camera avec les deux coordonées

camera = cv2.VideoCapture(0)
upper,lower,zero = ModuleTracking.getParameters(10) # 10  : billard sans soustraction
largeur = 395
longueur = 800
epaisseurBord = 55
diametre = 61.5

hg,imgFond = Reconstruction3D.getHomographyForBillard(camera,upper,lower,(largeur,longueur),epaisseurBord,diametre)
imgFondRotated = cv2.rotate(imgFond,cv2.ROTATE_90_CLOCKWISE)
imgFondResized = cv2.resize(imgFondRotated,(1080,1920),interpolation = cv2.INTER_NEAREST)


screen = screeninfo.get_monitors()[0]
height,width = np.shape(imgFondRotated)
image = imgFondRotated
#image = np.ones((height, width, 3), dtype=np.float32)
image[:10, :10] = 0  # black at top-left corner
image[height - 10:, :10] = [1, 0, 0]  # blue at bottom-left
image[:10, width - 10:] = [0, 1, 0]  # green at top-right
image[height - 10:, width - 10:] = [0, 0, 1] 

window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
cv2.setMouseCallback(window_name,onClick)
cv2.imshow(window_name, image)

while (True):
    k=cv2.waitKey(1)
    if k == ord('q'):
        break

"""




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
        
        c2 = (int(y),int(x))
        listPos.append(realCenter)
        listPosProj.append(getCoordProjection(c2))
        listTimeAdd.append(t.time())
        currentTime = t.time()
        if (currentTime-listTimeAdd[0]>tempsTrace):
            listPosProj.pop(0)
            listTimeAdd.pop(0)
        
        
        affTraj(np.array(listPosProj))
    
    if key==ord('q'): # quitter avec 'q'
        break


  """  