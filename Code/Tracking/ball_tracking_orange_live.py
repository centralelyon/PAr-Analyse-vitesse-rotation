#vidéo filmée maison, balle orange, avec soustraction de fond
"""
Created on Tue Nov 16 12:28:54 2021

@author: Guillaume
from: https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
"""

from collections import deque
import numpy as np
import argparse
import imutils
import cv2


#intégrer la soustraction ici directement 
#et créer 2 programmes avec 2 soustractions de fond différentes.

#à rajouter:
#3 suppression de fond a tester : image à blanc, moyenne glissante,moyenne sur tout le match
#a améliorer:
#fouiller parmi les contour les candidats pour etre une balle (bonne taille de pixel)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# initialisation des bornes supérieures et inférieures pour la recherche de couleur. A initialiser avec attention


lower = (10, 100, 150) #orange: exemple téléchargé depuis internet pour une balle de TT
upper = (30, 255, 255)

lower = (10, 50, 50) #tout
upper = (30, 245, 245)

#initialisation de la liste des position
pts = deque(maxlen=args["buffer"])

namevideo = "SUB3_echanges_1.mp4"

camera = cv2.VideoCapture(namevideo)
print(camera.get(cv2.CAP_PROP_FPS))


while True:
    
    (grabbed,frame)=camera.read()
    
    #start timer
    timer = cv2.getTickCount()
    
    if frame is None:
        break
    
    #pre-processing
    
    
    #rognage 1280*720, on ne garde que le rectangle central d'une grille 3*3 en attendant la suppression de fond (426, 240, 426, 240)
    
    #x,y=height//4,width//4
    #w,h=x,y
    #crop=frame[y:y+h,x:x+w]
    
    #enregistrement et suppression de fond , solution provisoire en attendant baptiste. On fait la supression en RGB
    #if compteur==2907:
    #    cv2.imwrite('C:/Users/Guillaume/Desktop/PAr/Code/fond.png', crop)
    #sansFond=cv2.subtract(crop,fond)
    
    #resize si trop lent
    #frame= imutile.resize(frame,width=1000)
    
    #floutage pour éliminer les effets des hautes fréquences
    blurred=cv2.GaussianBlur(frame,(11,11),0)
    
    #convert to hsv
    hsv=cv2.cvtColor(blurred,cv2.COLOR_BGR2HSV)
    
    #construction du masque de couleur
    mask=cv2.inRange(hsv,lower,upper)
    #cv2.imshow("masdk",mask)
    
    #affinage du masque
    #mask=cv2.erode(mask,None,iterations=2) #enlever ces lignes pour vidéo baptiste
    #mask=cv2.dilate(mask,None,iterations=2)
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
        if M["m00"] and M["m00"]:
            center= ( int(M["m10"]/M["m00"]) , int(M["m01"]/M["m00"]))
        
        if  radius > 5 and not (center is None): #initialement radius > 10. tenter 5.5 7 pour la vidéo de baptiste
            cv2.circle(frame,(int(x),int(y)),int(radius), (0,255,255),2)
            cv2.circle(frame,center,5,(0,0,255),-1)
            #print(radius)
    #update de la liste des centroids (éventuellement None)
    pts.appendleft(center)
    
    #rajouter le script pour tracer la ligne
    
    #légende en haut à gauche: FPS, coordonnées de la balle
    cv2.putText(frame, "HSV Tracker", (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
    cv2.putText(frame, "FPS : " + str(int(fps)), (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)
    cv2.putText(frame, str(center), (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)
    cv2.imshow("FramePostPro", frame)
    
    key = cv2.waitKey(100) & 0xFF
    
    #pause si espace, quitter si q
    if key==ord(" "):
        cv2.waitKey(0)
        #print(compteur)
    if key== 27:
        break
    
camera.release()
cv2.destroyAllWindows()
    
    
    
    
