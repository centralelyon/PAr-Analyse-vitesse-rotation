# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 16:57:05 2022

@author: bperr

Script billard
"""


import ModuleTracking
import Reconstruction3D


import cv2
import numpy as np
import time as t
import screeninfo
import json







# # Script d'éxécution pour le billard  # #
# On place le billard par rapport au vidéoprojecteur (rectangle)
# On trouve l'homographie entre le plan de la caméra et les coordonées réelles
# On projete en temps réel la position de la bille et on laisse la possibilité de rejouer un coup


## Phase préparatoire du programme

# Récupération de tout les paramètres
with open("AllData.json") as file:
    allData = json.load(file) # allData est un dictionnnaire contenant tout les paramètres.


# Création de l'image de fond affichée par le vidéo projecteur
screen = screeninfo.get_monitors()[0]
height,width = screen.height,screen.width
coin1 = (int(allData["coefRectangleX1"]*width),int(allData["coefRectangleY1"]*height))
coin2 = (int(allData["coefRectangleX2"]*width),int(allData["coefRectangleY2"]*height))
fond = np.ones((height,width,3))
fond = cv2.rectangle(fond,coin1,coin2,(0,0,0),5)


# Full screen et affiché par dessus les autres fenêtres dès le début
window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
Reconstruction3D.positionnerTable(fond,window_name)


# Obtention de l'homographie entre la vision de la caméra et la vue de dessus du billard.
camera = cv2.VideoCapture(1)
upper=tuple(map(int,allData["upperBornRed"][1:-1].split(','))) # Borne supérieure de recherche de couleur dans l'espace HSV
lower=tuple(map(int,allData["lowerBornRed"][1:-1].split(','))) # Borne inférieure de recherche de couleur dans l'espace HSV
largeur = allData["largeurBillard"]
longueur = allData["longueurBillard"]
epaisseurBord = allData["epaisseurBordBillard"]
diametre = allData["diametreBille"]
isOK=False
while not isOK:
    answer = input("Voulez vous utiliser la matrice d'homographie sauvegardée ou alors la déterminer à nouveau ? [y/n] \t")
    if answer=="y":
        hg = np.array(allData["homography"])
        isOK = True
    elif answer=="n":
        hg = Reconstruction3D.getHomographyForBillard(camera,upper,lower,(largeur,longueur),epaisseurBord,diametre)
        allData["homography"] = hg
        isOK=True
        


#redéfinition car cv2.destroyAllWIndows() dans positionnerTable a supprimé les propriétés
window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
#cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

## Phase nominale du programme

# Variable du tracé de la trajectoire
listPosProj=[] # Liste des position de la bille à projeter
listTimeAdd=[] # Liste des instants d'ajouts des éléments à listPosProj
tempsTrace = allData["tpsTraceTrajectoire"] # Temps qu'un point de la trajectoire reste affiché

# Variables de l'enregistrement de la trajectoire
tempsAjoutTrajectoire=allData["tpsAjoutTrajectoire"] # Délai entre l'enregistrement de deux positions pour la trajectoire sauvegardée
derniereTrajectoire=[] # Liste des positions de la trajectoire en cours d'aquisition, un ajout est fait toute les tempsAjoutTrajectoire secondes.
trajectoiresSauvegardees=[] # Liste des trajectoires sauvegardées

# Variables pour la détection de l'arrêt de la bille
tempsDetectionArret=allData["tpsArret"] # Temps d'immobilité nécessaie pour que l'arrêt soit détecté
seuil = allData["seuilArret"] #Déplacement maximal pour que la bille soit définie comme à l'arrêt
arret=False # Booléen indiquant si la bille est à l'arrêt
positionArret=(0,0) # Position de la bille à l'arrêt
vitesseBille = (0,0) # Vitesse de la bille
prochainePosition = (0,0) # Position probable de la bille sur la prochaine frame
seuilRebond = allData["seuilRebond"] # Distance entre la position réelle et la position prévue pour que on détecte un rebond

instantDernierAjout=t.time()
mode = 0  # Mode de fonctionnement du programe

while True:
    key = cv2.waitKey(1) # Lecture d'interraction clavier par l'utilisateur
    fond2 = fond.copy() # Copie de l'image de fond générique, qui sera modifiée si l'on doit afficher de nouvelles choses
    
    
    if mode == 0:
        grabbed,frame = camera.read() # Lecture de l'image vue par la caméra
        
        center = ModuleTracking.trackingBillard(frame,upper,lower) # Détection de la position de la bille sur cette image
        
        if center !=None:
            # Obtention des coordonnées "réeles" grâce à l'homographie
            realCenter = Reconstruction3D.findRealCoordinatesBillard(center,hg,(largeur,longueur),epaisseurBord)
            
            # Ajout à la liste des positions de la trajectoire à tracer
            listPosProj.append(Reconstruction3D.getCoordProjection(realCenter,largeur,longueur,coin1,coin2))
            currentTime = t.time()
            listTimeAdd.append(currentTime)

            #traitement de la trajectoire à tracer : effacement après tempsTrace secondes 
            if (currentTime-listTimeAdd[0]>tempsTrace):
                listPosProj.pop(0)
                listTimeAdd.pop(0)
            # Affichage de la trajectoire sur l'image de fond   
            Reconstruction3D.affTraj(listPosProj,fond2,window_name)
            
            #traitement de la trajectoire à sauvegarder
            if (currentTime-instantDernierAjout>tempsAjoutTrajectoire): 
                instantDernierAjout=currentTime
                
                derniereTrajectoire.append(realCenter)
 
        
        #detection arret
        if arret:
            cv2.putText(fond2,"A l'arret",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 255), 2)
            # 250, 400 : déterminés pour le PC de la salle Amigo : à transformer en coef * screen.width ou screen.height
            if  not(Reconstruction3D.detectionArret(derniereTrajectoire[int(-tempsDetectionArret/tempsAjoutTrajectoire):] , seuil)): #si on se met à bouger, on commence une nouvelle trajectoire
                #réinitialiser et initialiser les liste de tracking
                derniereTrajectoire=[positionArret]
                arret=False
    
        else:
            cv2.putText(fond2,"En mouvement",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 200, 0), 2)
            # 250, 400 : déterminés pour le PC de la salle Amigo : à transformer en coef * screen.width ou screen.height
            #on n'autorise que des mouvements de + d'1 sec. (arbitraire)
            if  len(derniereTrajectoire)>=tempsDetectionArret/(2*tempsAjoutTrajectoire) and Reconstruction3D.detectionArret(derniereTrajectoire[int(-tempsDetectionArret/tempsAjoutTrajectoire):], seuil): #si on passe à l'arret, on sauvegarde la position d'arret
                positionArret=realCenter
                arret=True
        
        # Détection rebond
        if len(derniereTrajectoire)>1:
            print(prochainePosition)
            print(realCenter)
            print((prochainePosition[0]-realCenter[0])**2+(prochainePosition[1]-realCenter[1])**2)
            print('\n')
            if (prochainePosition[0]-realCenter[0])**2+(prochainePosition[1]-realCenter[1])**2 > seuilRebond**2:
                # On détecte un rebond
                 cv2.putText(fond2,"Rebond !",(int(allData["coeftextInfoX"]*width),3*int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 200, 0), 2)
            
        
        
        # Calcul et affichage vitesse
        if len(derniereTrajectoire)>1:
            vitesseBille=((derniereTrajectoire[-1][0]-derniereTrajectoire[-2][0])/tempsAjoutTrajectoire,(derniereTrajectoire[-1][1]-derniereTrajectoire[-2][1])/tempsAjoutTrajectoire)
            cv2.putText(fond2,"Vitesse : \n"+str(round(np.linalg.norm(vitesseBille),2))+" mm/s",(int(allData["coeftextInfoX"]*width),2*int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 200, 0), 2)
            prochainePosition= (derniereTrajectoire[-1][0]+vitesseBille[0]*tempsAjoutTrajectoire,derniereTrajectoire[-1][1]+vitesseBille[1]*tempsAjoutTrajectoire)
            
        
        
        
        #sauvegarde
        if key==ord("s") and arret:
            trajectoiresSauvegardees.append(derniereTrajectoire)
            
        #passage au mode 1
        if key==ord("r"):
            mode=1
            
        
        
        
    if mode == 1:
        cv2.putText(fond2,"Selection coup",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 255, 0), 2)
        # 250, 400 : déterminés pour le PC de la salle Amigo : à transformer en coef * screen.width ou screen.height
        #sélection rapide avec les numéros du clavier,
        #dans le futur: prévisualisation et sélection avec des flèches
    
    
    cv2.imshow(window_name,fond2)
    
    if key==ord('q'): # quitter avec 'q'
        cv2.destroyAllWindows()
        break


# Sauvegarde d'éventuelles modifications des paramètres de AllData
with open('AllData.json', 'w') as file:
	json.dump(allData, file)
    