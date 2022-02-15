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

distorsionData = np.load("IntrisicParameters.npz")
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
    
    ret, corners = cv2.findChessboardCorners(frame, (a,b), None) # (8,8) :grille
    #corners2 = cv2.cornerSubPix(frame,corners, (11,11), (-1,-1), criteria)
    corn = corners.reshape((49,2))
    
    h, status = cv2.findHomography(corn,objp)
    imReg = cv2.warpPerspective(frame, translate.dot(h),(frame.shape[1],frame.shape[0]))
    
    cv2.imshow('Image rectifiee',imReg)
    
    key = cv2.waitKey(100)
    if key ==27:
        break
