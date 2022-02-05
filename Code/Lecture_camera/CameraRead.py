# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 13:24:22 2022

@author: bperr

Objectif :  1.recevoir la vidéo depuis la caméra et l'afficher sur l'écran
            2. appliquer un traitement de soustraction de fond avant d'affficher
"""


import cv2

 # Une caméra

camera=cv2.VideoCapture(1)
if not (camera.isOpened()):
    camera= cv2.VideoCapture(0)
    
ok,frame=camera.read()
cv2.imshow('frame',frame)

"""
 # Deux caméras
camera2=cv2.VideoCapture(2)
if not (camera2.isOpened()):
    camera2=cv2.VideoCapture(1)
    camera1=cv2.VideoCapture(0)
else:
    camera1=cv2.VideoCapture(1)
"""


    



