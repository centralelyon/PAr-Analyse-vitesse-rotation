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

