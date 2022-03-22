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


def detectionRebond(lV,seuil):
    rebond = False
    i=1
    signeX = (lV[0][0]>0)
    signeY = (lV[0][1]>0)
    while not(rebond) and i<len(lV):
        if (lV[i][0]>0)!=signeX: # Changement de signe de Vx
            print('Rebond X potentiel')
            if abs(lV[i-1][0]-lV[i][0])>seuil:
                print('Rebond X confirme')
                rebond=True
            else:
                print("Rebond X infirme")

        if (lV[i][1]>0)!=signeY: # Changement de signe de Vx
            print('Rebond Y potentiel')
            if abs(lV[i-1][1]-lV[i][1])>seuil:
                print('Rebond Y confirme')
                rebond=True
            else:
                print("Rebond Y infirme")
        
        i+=1
    return rebond


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
derniereVitesse = [] # Position probable de la bille sur la prochaine frame
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
            Reconstruction3D.affTraj(listPosProj,fond2)
            
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
            if (prochainePosition[0]-realCenter[0])**2+(prochainePosition[1]-realCenter[1])**2 > seuilRebond**2:
                # On détecte un rebond
                print("Rebond")
                cv2.putText(fond2,"Rebond !",(int(allData["coeftextInfoX"]*width),3*int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 200, 0), 2)
            
        
        
        # Calcul et affichage vitesse
        if len(derniereTrajectoire)>1:
            vitesseBille=((derniereTrajectoire[-1][0]-derniereTrajectoire[-2][0])/tempsAjoutTrajectoire,(derniereTrajectoire[-1][1]-derniereTrajectoire[-2][1])/tempsAjoutTrajectoire)
            cv2.putText(fond2,"Vitesse : \n"+str(round(np.linalg.norm(vitesseBille),2))+" mm/s",(int(allData["coeftextInfoX"]*width),2*int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 200, 0), 2)
            derniereVitesse.append(vitesseBille)
            if len(derniereVitesse)>5:
                derniereVitesse.pop(0)
        
        
        
        #sauvegarde
        if key==ord("s") and arret:
            trajectoiresSauvegardees.append(derniereTrajectoire)
            
        #passage au mode 1 uniquement si on a des trajectoires enregistrées
        if key==ord("r") and len(trajectoiresSauvegardees):
            mode=1
            
        cv2.imshow(window_name,fond2)
            
        
        
        
    if mode == 1:   
        
        #listeOrdChiffres=[ord(str(i+1)) for i in range(9)] #chiffres de 1 à 9
        # 1 <-> 49 / 2 <-> 50 / 9 <-> 57
        
        cv2.putText(fond2,"Selection coup",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 255, 0), 2)

        #affichage des boutons
        for i in range(len(trajectoiresSauvegardees)):
            #trouver coeff à la place de 200
            cv2.putText(fond2,str(i+1),(int(allData["coeftextInfoX"]*width + 50 * i ),int(allData["coeftextMoovY"]*height + 200 )),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (100, 100, 100), 2)
        
        
        #sauvegarde du fond (modification si changement de traj à visualiser)
        fond3 = fond2.copy()
        
        #initialisation de la séléction
        indTrajSelectionnee=0   
        cv2.putText(fond2,"1",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height + 200 )),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 0, 255), 2)
        Reconstruction3D.affTraj(trajectoiresSauvegardees[0],fond2,window_name)
        
        
        
        
        cv2.imshow(window_name,fond3)
            
        while True:
            key=cv2.waitKey(1)
            
            if key ==ord("\n"): #enter
                mode=2
                #supprimer background?
                break
            
            if key == 27: #echap
                mode=0
                break
            
            if 49 <= key <= 49+len(trajectoiresSauvegardees)-1:
                #réinitialisation de l'image 
                fond2=fond3.copy()
                
                #actualisation de la selection
                indTrajSelectionnee = key - 48 - 1 #le chiffre appuyé est -48, l'indice de la liste est -49
                
                #tracer le chiffre selectionné en couleur, afficher la trajectoire
                cv2.putText(fond2,str(indTrajSelectionnee+1),(int(allData["coeftextInfoX"]*width + 50 * indTrajSelectionnee ),int(allData["coeftextMoovY"]*height + 200 )),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 0, 255), 2)
                Reconstruction3D.affTraj(trajectoiresSauvegardees[0])
                
                cv2.imshow(window_name,fond2)
        
    
        
    if mode==2:
        #fond: selection du mode.
        #effacer chiffres selection du mode 3
        
        #afficher la position de la balle  en pointillés
        
        #fond 3= fond
        
        
        
        #lancer le tracking: while key!=echap and balle pas au bon endroit et ca fait pas 3 sec
            #getkey
            
            #si abs(centretrack - centrepos )<eps
                #flag=1
                #instantflag=t.time
                
            #si c'est dedans: on épaissit le trait
            
        #si echap:
            #mode 1, reset graphique
            
        #sinon:
            #mode 3, reset graphique
        
            
        pass
    
            
    
    if key==ord('q'): # quitter avec 'q'
        cv2.destroyAllWindows()
        break


# Sauvegarde d'éventuelles modifications des paramètres de AllData
with open('AllData.json', 'w') as file:
	json.dump(allData, file)
    