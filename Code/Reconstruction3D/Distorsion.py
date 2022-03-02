# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 22:02:17 2022

@author: bperr
"""

import numpy as np
import cv2 as cv
import glob
import time
import sys

""" Calibration """

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0) # Coordonées réelles de tt les points
a =7
b=7
objp = np.zeros((a*b,3), np.float32) # 8*8 = dimension de l'échiquier (grille)
objp[:,:2] = np.mgrid[0:a,0:b].T.reshape(-1,2)

objp=objp*50 # Dimensions en mm


# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
i=0
images = glob.glob('Images_echiquier3/*.jpg')
for fname in images:
    
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (a,b), None) # (8,8) :grille
    if ret==True:
        i+=1
    print(ret,fname)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (a,b), corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(500)
#cv.destroyAllWindows()

print(i)

"""
# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0) # Coordonées réelles de tt les points
objp = np.zeros((6*6,3), np.float32) # 8*8 = dimension de l'échiquier (grille)
objp[:,:2] = np.mgrid[0:6,0:6].T.reshape(-1,2)
objp=objp*50 # Dimensions en mm

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

cam = cv.VideoCapture(0)
 
while (len(imgpoints)<14):
    time.sleep(5)
    worked, img = cam.read()
    print("Read")
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (6,6), None) # (8,8) :grille
    # If found, add object points, image points (after refining them)
    if ret == True:
        cv.imwrite('ChessBoard'+str(len(imgpoints)+1)+'.jpg',img)
        print(ret)
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (6,6), corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(500)
#cv.destroyAllWindows()

print("On a toute les images")
"""

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

""" Dé-distorsion """

img = cv.imread('test2.jpg')
h,  w = img.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h)) # (w,h) : taille de l'image originale et nouvelle taille-->roi

# undistort
dst = cv.undistort(img, mtx, dist, None, newcameramtx)
# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite('calibresult.png', dst)

""" Sauvegarde des paramètres dans un fichier annexe """

np.savez("IntrisicParameters3.npz",mtx=mtx,dist=dist,r=rvecs,t=tvecs)

