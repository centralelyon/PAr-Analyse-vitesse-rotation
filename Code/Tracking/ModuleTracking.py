# -*- coding: utf-8 -*-
"""

Module tracking

@author Baptiste Perreyon, Guillaume Pacsek

"""

from collections import deque
import numpy as np
import cv2
import json
import SubImMoy


"""
## Fonction de tracking

@params camera : objet VideoCapture qui peut venir d'un fichier vidéo ou d'une caméra
        typeSoustraction : trois valeurs possibles : 0 - pas de soustraction
                                                     1 - soustraction d'une image fixe
                                                     2 - soustraction d'image moyenne
@return None
"""
def tracking(camera,typeSoustraction):
    # On récupère les paramètres pour le tracking dans le fichier json associé
    upper,lower,tailleIntervalle = getParameters(typeSoustraction)
    
    # On récupère le nombre d'image par seconde de la vidéo
    fps = camera.get(cv2.CAP_PROP_FPS)
    #initialisation de la liste des position
    
    liste_x_trackee=[]
    liste_y_trackee=[]
    liste_indice_trackee=[]
    indice_frame=0
    
    compteurDetection = 0
    compteurImage = 0
    
    if (typeSoustraction==1):
        (grabbed,frame)=camera.read()
        fondInitial=frame
        cv2.imshow("fond",frame)
    elif (typeSoustraction==2):
        frames = deque(maxlen=tailleIntervalle)
        for i in range(tailleIntervalle):   
            (grabbed,frame)=camera.read()
            frames.appendleft(frame)  # Ajoute une nouvelle image et en enlève une si besoin  
    
    print("Entrée dans la boucle")
    while True:
    
        (grabbed,frame)=camera.read()
        
        #start timer
        timer = cv2.getTickCount()
        
        if frame is None:
            break
        
        #pre-processing
        if (typeSoustraction==1):
            frame=cv2.subtract(frame,fondInitial)
        elif (typeSoustraction==2):
            frames.appendleft(frame)
            processedFrame = frames[tailleIntervalle//2]
            frame=SubImMoy.calcImageMoyenneArr(frames,tailleIntervalle//2)
        
        
        scale_percent = 100 # percent of original size !!! change le calibrage notamment sur la taille de la balle en pxl
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)
    
        frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        #frame= frame.resize(frame,width=1000)
        
        #floutage pour éliminer les effets des hautes fréquences
        blurred=cv2.GaussianBlur(frame,(5,5),0)
        #cv2.imshow("blurred",blurred)
        
        #convert to hsv
        hsv=cv2.cvtColor(blurred,cv2.COLOR_BGR2HSV)
        
        #construction du masque de couleur
        mask=cv2.inRange(hsv,lower,upper)
        
        #affinage du masque. 
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
            #print(radius)
            if M["m00"] and M["m00"]:
                center= ( int(M["m10"]/M["m00"]) , int(M["m01"]/M["m00"]))
            
            if radius < 10 and not (center is None): #j'ai enlevé la condition "radius >3". Changer ce critère
                cv2.circle(frame,(int(x),int(y)),int(radius), (0,255,255),2)
                cv2.circle(frame,center,5,(0,0,255),-1)
                compteurDetection+=1
                liste_x_trackee.append(center[0])
                liste_y_trackee.append(center[1])
                liste_indice_trackee.append(indice_frame)
    
        """    
        indice_frame+=1
        if indice_frame == 76:
            break
        """

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
    
    
"""
## Récupérer les paramètres de tracking dans un fichier JSON

@params typeSoustraction : indique le type de soustraction utilisée pour le tracking et donc le fichier à ouvrir
@return upper : borne supérieure dans l'espace de couleur HSV dans laquelle on va rechercher la balle
        lower : borne inférieure dans l'espace de couleur HSV dans laquelle on va rechercher la balle
        tailleIntervalle : dans le cas d'une soustraction de l'image moyenne (typeSoustraction=2), taille de l'intervalle de calcul de l'image moyenne
"""
def getParameters(typeSoustraction):
    name="Parameters"+str(typeSoustraction)+".json"
    
    with open(name) as json_data:
        data_dict=json.load(json_data)
    upper=tuple(map(int,data_dict["upperBorn"][1:-2].split(',')))
    lower=tuple(map(int,data_dict["lowerBorn"][1:-2].split(',')))
    if (typeSoustraction==2):
        tailleIntervalle=int(data_dict["tailleIntervalle"])
        return upper,lower,tailleIntervalle
    else:
        return upper,lower,0
    
    
    
    