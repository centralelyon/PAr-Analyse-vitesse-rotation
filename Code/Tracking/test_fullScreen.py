# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 15:04:32 2022

@author: Guillaume
"""
#source https://gist.github.com/ronekko/dc3747211543165108b11073f929b85e
#prend une image en paramètre: "img.png", et l'affiche en plein écran
#il faut que la taille de l'image soit de la taille de l'écran
import cv2
import numpy as np
import screeninfo


# get the size of the screen
screen = screeninfo.get_monitors()[0] #remplacer 0 par le numéro de l'écran si plusieurs screens
width, height = screen.width, screen.height


# create image
image = np.ones((height, width, 3), dtype=np.float32)
image[:10, :10] = 0  # black at top-left corner
image[height - 10:, :10] = [1, 0, 0]  # blue at bottom-left
image[:10, width - 10:] = [0, 1, 0]  # green at top-right
image[height - 10:, width - 10:] = [0, 0, 1]  # red at bottom-right

#or read one (must be of the good size: width,height)
#image=cv2.imread("img.png")

window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cv2.imshow(window_name, image)