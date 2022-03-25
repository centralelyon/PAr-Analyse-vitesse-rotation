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
import copy

def drawRectangle(event,x,y,flags,params):
    if event==cv2.EVENT_LBUTTONDOWN:
        print(x,y)
        
        if params[2]==1:
            cv2.rectangle(params[3],params[0],params[1],(255,255,255),5)
            params[0]= (x,y)
            params[2]=2
            cv2.rectangle(params[3],params[0],params[1],(0,0,0),5)
            cv2.imshow(params[4],params[3])
        else:
            cv2.rectangle(params[3],params[0],params[1],(255,255,255),5)
            params[1] = (x,y)
            params[2]=3
            cv2.rectangle(params[3],params[0],params[1],(0,0,0),5)
            cv2.imshow(params[4],params[3])



def positionnerTable(img,fenetre,coin1,coin2):
    print("Veuillez positioner l'intérieur de la table dans le rectangle")
    img = cv2.rectangle(img,coin1,coin2,(0,0,0),5)
    cv2.imshow(fenetre,img)
    while True:
        k = cv2.waitKey(1)
        if k==ord('r'): # On veut changer les dimensions du rectangle
            
            params=[coin1,coin2,1,img,fenetre]
            cv2.setMouseCallback(fenetre,drawRectangle,params)
            while params[2]<3:
                c = cv2.waitKey(1)
            cv2.setMouseCallback(fenetre, lambda *args : None)
            coin1=params[0]
            coin2=params[1]
            img = params[3]
        if k ==ord('q'):
            cv2.destroyAllWindows()
            break
"""
# get the size of the screen
screen = screeninfo.get_monitors()[0] #remplacer 0 par le numéro de l'écran si plusieurs screens
width, height = screen.width, screen.height

camera = cv2.VideoCapture(0)
o,image = camera.read()


# create image
#image = np.ones((height, width, 3), dtype=np.float32)
image[:10, :10] = 0  # black at top-left corner
image[height - 10:, :10] = [1, 0, 0]  # blue at bottom-left
image[:10, width - 10:] = [0, 1, 0]  # green at top-right
image[height - 10:, width - 10:] = [0, 0, 1]  # red at bottom-right

#or read one (must be of the good size: width,height)
#image=cv2.imread("img.png")

window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
a = cv2.setMouseCallback(window_name,onClick)
cv2.imshow(window_name, image)

while (True):
    k=cv2.waitKey(1)
    if a!=None:
        print(a)
    if k == ord('q'):
        break
"""

screen = screeninfo.get_monitors()[0]
height,width = screen.height,screen.width
coin1 = (50,50)
coin2 = (200,200)
fond = np.ones((height,width,3))

window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
positionnerTable(fond,window_name,coin1,coin2)