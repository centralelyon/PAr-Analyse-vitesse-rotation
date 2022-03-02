# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 15:12:01 2022

@author: bperr
"""

import numpy as np
import cv2

camera = cv2.VideoCapture(0)

grabbed, frame = camera.read()
h,  w = frame.shape[:2]

distorsionData = np.load("IntrisicParameters3.npz")
mtx=distorsionData['mtx']
dist = distorsionData['dist']
rvecs = distorsionData['r']
tvecs = distorsionData['t']

newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h)) # (w,h) : taille de l'image originale et nouvelle taille-->roi

a =7
b=7
objp = np.zeros((a*b,3), np.float32) # 8*8 = dimension de l'échiquier (grille)
objp[:,:2] = np.mgrid[0:a,0:b].T.reshape(-1,2)
objp=objp[:,0:2]
objp=objp*50 # Dimensions en mm
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

factor=0.5
translate = np.array([[1,0,factor*100],[0,1,factor*30],[0,0,1]])

while True:
    grabbed, frame = camera.read()
    cv2.imshow("Image sans traitement",frame)
    
    frameRect = cv2.undistort(frame,mtx,dist,None,newcameramtx)
    x, y, w, h = roi
    frameRect = frameRect[y:y+h, x:x+w]
    cv2.imshow("Image post traitement",frameRect)
    """
    ret, corners = cv2.findChessboardCorners(frame, (a,b), None) # (8,8) :grille
    #corners2 = cv2.cornerSubPix(frame,corners, (11,11), (-1,-1), criteria)
    corn = corners.reshape((49,2))
    
    h, status = cv2.findHomography(corn,objp)
    imReg = cv2.warpPerspective(frame, translate.dot(h),(frame.shape[1],frame.shape[0]))
    
    cv2.imshow('Image rectifiee',imReg)
    """
    key = cv2.waitKey(1)
    if key ==ord('q'):
        break

"""
frame = cv2.imread("Billard4.jpg")
cv2.imshow('Image originelle',frame)
w,h = frame.shape[:2]

diametre = 61.5
dx = np.sqrt(2)/4*diametre
coordPixel=np.array([[918,803],[1204,812],[918,174],[1204,172]])
coordReel=np.array([[dx, dx],[400-dx,dx],[dx,800-dx],[400-dx,800-dx]])

factor = 0.15
translate = np.array([[1,0,factor*1000],[0,1,factor*500],[0,0,1]])

he, status = cv2.findHomography(coordPixel,coordReel)
imReg = cv2.warpPerspective(frame,translate.dot(he),(int(factor*5000),int(factor*6500)))
#imReg = cv2.warpPerspective(frame,he,(frame.shape[1],frame.shape[0]))

cv2.imshow('Image rectifiee',imReg)
"""


def addPoint(camera,upper,lower,location):
    print("Placer la boule dans le coin "+location+" puis validez avec la barre d'espace ou la touche entrée")
    while True:
        key = cv2.waitKey(1)
        (grabbed,frame)=camera.read()
        cv2.imshow('frame',frame)
        #Resize
        scale_percent = 100 # percent of original size !!! change le calibrage notamment sur la taille de la balle en pxl
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)
        frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        
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
            #print(radius)
            if M["m00"] and M["m00"]:
                center= ( int(M["m10"]/M["m00"]) , int(M["m01"]/M["m00"]))
            
            if radius < 10 and not (center is None): #j'ai enlevé la condition "radius >3". Changer ce critère
                cv2.circle(frame,(int(x),int(y)),int(radius), (0,255,255),2)
                cv2.circle(frame,center,5,(0,0,255),-1)
        
        if key==ord(' ') or key==ord("\r"):
            break
    cv2.destroyAllWindows()
    return center

def getHomographyForBillard(camera,upper,lower,dimensions,diametre):
    igc = addPoint(camera,upper,lower,"inférieur gauche")
    idc = addPoint(camera,upper,lower,"inférieur droit")
    sgc = addPoint(camera,upper,lower,"supérieur gauche")
    sdc = addPoint(camera,upper,lower,"supérieur droit")
    coordPixel=np.array([list(igc),list(idc),list(sgc),list(sdc)])
    
    dx = np.sqrt(2)/4*diametre
    
    coordReel=np.array([[dx,dx],[dimensions[0]-dx,dx],[dx,dimensions[1]-dx],[dimensions[0]-dx,dimensions[1]-dx]])
    
    factor = 0.15
    translate = np.array([[1,0,factor*1000],[0,1,factor*500],[0,0,1]])
    h, status = cv2.findHomography(coordPixel,coordReel)
    homography = translate.dot(h)
    newDim = (int(factor*5000),int(factor*6500))
    
    grabbed,frame = camera.read()
    imReg = cv2.warpPerspective(frame,homography,newDim)
    cv2.imshow('rect',imReg)
    
    return homography,newDim

"""
camera = cv2.VideoCapture(0)
upper=(138,207,177)
lower=(91,73,19)
h,nd = getHomographyForBillard(camera, upper, lower,(400,800),65.5) """