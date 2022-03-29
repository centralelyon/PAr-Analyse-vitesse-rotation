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
import timeit as ti
import os
import csv


def sauvTraj(trajs,coin1,coin2):
    os.chdir('Trajectoires_sauvegardees')
    nbTrajSauv = len(os.listdir())
    for t in trajs:
        nbTrajSauv+=1
        with open ('Trajectoire'+str(nbTrajSauv)+'.csv','a') as f:
            writer = csv.writer(f)
            writer.writerow(['Coin sup gauche',coin1,'Coin inf droit',coin2])
            writer.writerow(['x','y','t'])
            for p in t:
                writer.writerow(list(p))
    os.chdir('..')
        



def detectionRebond(lV,seuil1):
    rebond = False
    i=1
    #Signe global de la trajectoire
    vitX = np.mean([lV[i][0] for i in range(len(lV))])
    vitY = np.mean([lV[i][1] for i in range(len(lV))])
    signeX = vitX>=0
    signeY = vitY>=0
    
    while not(rebond) and i<len(lV):
        if (lV[i][0]>=0)!=signeX: # Changement de signe de Vx
            #print('Rebond X potentiel')
            if abs(lV[i-1][0]-lV[i][0])>seuil:
                #print('Rebond X confirme',lV[i-1][0],lV[i][0],lV[i-1][0]-lV[i][0])
                rebond=True
            else:
                #print('Rebond X infirme',lV[i-1][0],lV[i][0],lV[i-1][0]-lV[i][0])
                pass

        if (lV[i][1]>=0)!=signeY: # Changement de signe de Vx
            #print('Rebond Y potentiel')
            if abs(lV[i-1][1]-lV[i][1])>seuil:
                #print('Rebond Y confirme',lV[i-1][1],lV[i][1],lV[i-1][1]-lV[i][1])
                rebond=True
            else:
                #print('Rebond Y infirme',lV[i-1][1],lV[i][1],lV[i-1][1]-lV[i][1])
                pass
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



# Full screen et affiché par dessus les autres fenêtres dès le début
window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
resized = Reconstruction3D.positionnerTable(fond,window_name,coin1,coin2)

if resized : # On a redéfini les dimensions du rectangle
    allData["coefRectangeX1"] = round(coin1[0]/width,5)
    allData["coefRectangeY1"] = round(coin1[1]/height,5)
    allData["coefRectangeX2"] = round(coin2[0]/width,5)
    allData["coefRectangeY2"] = round(coin2[1]/height,5)
   
    
fond2 = fond.copy()
cv2.putText(fond2," Veuillez patienter, la caméra se connecte...",(coin1[0],int((coin1[1]+coin2[1])/2)),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
cv2.imshow(window_name,fond2)

# Obtention de l'homographie entre la vision de la caméra et la vue de dessus du billard.
camera = cv2.VideoCapture(1)
upper=tuple(map(int,allData["upperBornRed"][1:-1].split(','))) # Borne supérieure de recherche de couleur dans l'espace HSV
lower=tuple(map(int,allData["lowerBornRed"][1:-1].split(','))) # Borne inférieure de recherche de couleur dans l'espace HSV
largeur = allData["largeurBillard"]
longueur = allData["longueurBillard"]
epaisseurBord = allData["epaisseurBordBillard"]
diametre = allData["diametreBille"]
isOK=False

cv2.destroyAllWindows()
while not isOK:
    answer = input("Voulez vous utiliser la matrice d'homographie sauvegardée ou alors la déterminer à nouveau ? [y/n] \t")
    if answer=="y":
        hg = np.array(allData["homography"])
        isOK = True
    elif answer=="n":
        hg = Reconstruction3D.getHomographyForBillard(camera,upper,lower,(largeur,longueur),epaisseurBord,diametre)
        l4 = [list(e) for e in hg]
        l5=[]
        for i in range(len(l4)):
            ltemp=[]
            for j in range(len(l4[i])):
                ltemp.append(l4[i][j].item()) # conversion int32 to int
            l5.append(ltemp)
        allData["homography"] = l5
        isOK=True
        


#redéfinition car cv2.destroyAllWIndows() dans positionnerTable a supprimé les propriétés
window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
#cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

## Phase nominale du programme

# Variable du tracé de la trajectoire
listPosProj=[] # Liste des position de la bille à projeter et instant de détection
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
derniereVitesse = [] # Dernieres vitesses de la bille utilisées pour détecter le rebond
nbVitesse = 5 # Longueur de derniereVitesse
seuilRebond = allData["seuilRebond"] # Distance entre la position réelle et la position prévue pour que on détecte un rebond
tpsrebond=0
rebond=False

instantDernierAjout=t.time()
mode = 0  # Mode de fonctionnement du programe
fond2=fond.copy()
instantDebutTrajectoire=t.time()
arret=True


compteur = 1
start = t.time()
while True:
   
    
    key = cv2.waitKey(1) # Lecture d'interraction clavier par l'utilisateur
    #fond2 = fond.copy() # Copie de l'image de fond générique, qui sera modifiée si l'on doit afficher de nouvelles choses
    
    
    if mode == 0:
        grabbed,frame = camera.read() # Lecture de l'image vue par la caméra
        
        center = ModuleTracking.trackingBillard(frame,upper,lower) # Détection de la position de la bille sur cette image
        currentTime = t.time()
        if center !=None:
            # Obtention des coordonnées "réelles" grâce à l'homographie
            realCenter = Reconstruction3D.findRealCoordinatesBillard(center,hg,(largeur,longueur),epaisseurBord)
            
            # Ajout à la liste des positions de la trajectoire à tracer
            x3,y3 = Reconstruction3D.getCoordProjection(realCenter,largeur,longueur,coin1,coin2)
            listPosProj.append((x3,y3,currentTime))

            #traitement de la trajectoire à tracer : effacement après tempsTrace secondes 
            if (currentTime-listPosProj[0][2]>tempsTrace):
                listPosProj.pop(0)
		
            # Affichage de la trajectoire sur l'image de fond  
            Reconstruction3D.affTraj(listPosProj,fond2)
            
            #traitement de la trajectoire à sauvegarder
            if  (currentTime-instantDernierAjout>tempsAjoutTrajectoire): 
                instantDernierAjout=currentTime
                derniereTrajectoire.append(realCenter+tuple([currentTime-instantDebutTrajectoire]))
                
 
        
        #detection arret
        
        if arret and len(derniereTrajectoire)>=tempsDetectionArret/(2*tempsAjoutTrajectoire) and not(Reconstruction3D.detectionArret(derniereTrajectoire[int(-tempsDetectionArret/tempsAjoutTrajectoire):] , seuil)): #si on se met à bouger, on commence une nouvelle trajectoire
            #réinitialiser et initialiser les liste de tracking
            derniereTrajectoire=[positionArret+tuple([0])]
            instantDebutTrajectoire=currentTime
            arret=False
            #print('En mouvement')
            cv2.putText(fond2,"A l'arret",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 2)
            cv2.putText(fond2,"En mouvement",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 200, 0), 2)

        #on n'autorise que des mouvements de + d'1 sec. (arbitraire)
        if not arret and len(derniereTrajectoire)>=tempsDetectionArret/(2*tempsAjoutTrajectoire) and Reconstruction3D.detectionArret(derniereTrajectoire[int(-tempsDetectionArret/tempsAjoutTrajectoire):], seuil): 
            positionArret=realCenter #si on passe à l'arret, on sauvegarde la position d'arret
            arret=True
            #print('A l arret')
            cv2.putText(fond2,"En mouvement",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 2)
            cv2.putText(fond2,"A l'arret",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 255), 2)
     
        #Détection rebond
        if len(derniereVitesse)==nbVitesse:
            if detectionRebond(derniereVitesse,seuilRebond):
                #print("Rebond !")
                rebond=True
                tpsrebond=t.time()
            
        # Affichage temporaire
        if rebond: 
            #print(rebond)
            cv2.putText(fond2,"Rebond !",(int(allData["coeftextInfoX"]*width),3*int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 200, 0), 2)
            rebond = False
            
        if currentTime-tpsrebond>1.5:
            cv2.putText(fond2,"Rebond !",(int(allData["coeftextInfoX"]*width),3*int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 2)
            
            
        
        
        # Calcul et affichage vitesse
        if len(derniereTrajectoire)>1:
            cv2.putText(fond2,"Vitesse : "+str(round(np.linalg.norm(vitesseBille),2))+" mm/s",(int(allData["coeftextInfoX"]*width),2*int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
            vitesseBille=((derniereTrajectoire[-1][0]-derniereTrajectoire[-2][0])/tempsAjoutTrajectoire,(derniereTrajectoire[-1][1]-derniereTrajectoire[-2][1])/tempsAjoutTrajectoire)
            cv2.putText(fond2,"Vitesse : "+str(round(np.linalg.norm(vitesseBille),2))+" mm/s",(int(allData["coeftextInfoX"]*width),2*int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 200, 0), 2)
            derniereVitesse.append(vitesseBille)
            if len(derniereVitesse)>nbVitesse:
                derniereVitesse.pop(0)
        
        
        
        #sauvegarde
        if key==ord("s") and arret:
            dt = [Reconstruction3D.getCoordProjection(c, largeur,longueur,coin1,coin2)+tuple([c[2]]) for c in derniereTrajectoire]
            trajectoiresSauvegardees.append(dt)
            
        #passage au mode 1 uniquement si on a des trajectoires enregistrées
        if key==ord("r") and len(trajectoiresSauvegardees)>0:
            mode=1
            
        cv2.imshow(window_name,fond2)
            
        
        
        
    if mode == 1:
        fond2=fond.copy() #on efface l'ecran .
        
        #listeOrdChiffres=[ord(str(i+1)) for i in range(9)] #chiffres de 1 à 9
        # 1 <-> 49 / 2 <-> 50 / 9 <-> 57
        
        cv2.putText(fond2,"Selection coup",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 255, 0), 2)

        #affichage des boutons
        for i in range(len(trajectoiresSauvegardees)):
            #trouver coeff à la place de 200
            cv2.putText(fond2,str(i+1),(int(allData["coeftextInfoX"]*width + 50 * i ),int(allData["coeftextMoovY"]*height + 200 )),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 0, 0), 2)
        
        
        #sauvegarde du fond (modification si changement de traj à visualiser)
        fond3 = fond2.copy()
        
        #initialisation de la séléction
        indTrajSelectionnee=0   
        cv2.putText(fond2,"1",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height + 200 )),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 0, 255), 2)

        Reconstruction3D.affTrajTotal(trajectoiresSauvegardees[0],fond2)
        
        
        
        
        cv2.imshow(window_name,fond2)
            
        while True:
            key=cv2.waitKey(1)
            
            if key ==ord("\r"): #enter
                mode=2
                #supprimer background?
                break
            
            if key == 27: #echap
                fond2=fond.copy()    
                mode=0
                break
            
            if 49 <= key <= 49+len(trajectoiresSauvegardees)-1:
                #réinitialisation de l'image 
        
                fond2=fond3.copy()
                
                #actualisation de la selection
                indTrajSelectionnee = key - 48 - 1 #le chiffre appuyé est -48, l'indice de la liste est -49
                
                #tracer le chiffre selectionné en couleur, afficher la trajectoire
                cv2.putText(fond2,str(indTrajSelectionnee+1),(int(allData["coeftextInfoX"]*width + 50 * indTrajSelectionnee ),int(allData["coeftextMoovY"]*height + 200 )),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 0, 255), 2)
                Reconstruction3D.affTrajTotal(trajectoiresSauvegardees[indTrajSelectionnee],fond2)
                
                cv2.imshow(window_name,fond2)
        
    
        
    if mode==2:
        # On reprend le fond de base
        fond2=fond.copy()
        #fond: selection du mode.
        #effacer chiffres selection du mode 3
        cv2.putText(fond2,"Placez la bille",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 255, 0), 2)
        cv2.putText(fond2,"a l'endroit",(int(allData["coeftextInfoX"]*width),int(1.4*allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 255, 0), 2)
        cv2.putText(fond2,"indique",(int(allData["coeftextInfoX"]*width),int(1.8*allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 255, 0), 2)
        
        #afficher la position de la balle  en pointillés
        posIni = trajectoiresSauvegardees[indTrajSelectionnee][0][:2]
        cv2.circle(fond2,posIni,150,(0,0,255),6,cv2.LINE_AA)
        cv2.imshow(window_name,fond2)
        fond3 = fond2.copy()
        cv2.circle(fond3,posIni,200,(0,0,255),9,cv2.LINE_AA)
        #fond 3= fond
        #fond3 = fond2.copy()
        distanceMin=20
        posIniReel = Reconstruction3D.getInvCoordProjection(posIni,largeur,longueur,coin1,coin2)
        #print(posIniReel)
        #lancer le tracking: while key!=echap and balle pas au bon endroit et ca fait pas 3 sec
        balleNonPlace = True
        instantflag = t.time()
        while balleNonPlace or abs(t.time()-instantflag)<3:
            #getkey
            key = cv2.waitKey(1)
            
            grabbed,frame = camera.read() # Lecture de l'image vue par la caméra
            center = ModuleTracking.trackingBillard(frame,upper,lower) # Détection de la position de la bille sur cette image
            if center !=None:
                realCenter = Reconstruction3D.findRealCoordinatesBillard(center,hg,(largeur,longueur),epaisseurBord)

                #print(str((realCenter[0]-posIniReel[0])**2 + (realCenter[1]-posIniReel[1])**2))
                
                #si abs(centretrack - centrepos )<eps
                    #flag=1
                    #instantflag=t.time
                if (realCenter[0]-posIniReel[0])**2 + (realCenter[1]-posIniReel[1])**2 <= distanceMin**2:
                    if balleNonPlace:
                        instantflag = t.time()
                    balleNonPlace = False
                    
                    #si c'est dedans: on double le cercle
                    cv2.imshow(window_name, fond3)
                else:
                    balleNonPlace=True
                    cv2.imshow(window_name, fond2)
            
            #si echap:
            #mode 1, reset graphique
            if key == 27: # echap
                mode=1
                break
        
        #sinon:
        #mode 3, reset graphique
        if mode ==2:
            fond2=fond.copy()
            mode=3
        
        
            
    if mode==3:
        Reconstruction3D.affTrajPrevis(trajectoiresSauvegardees[indTrajSelectionnee],fond2)
        
        cv2.imshow(window_name,fond2)
    
    if key==ord('q'): # quitter avec 'q'
        cv2.destroyAllWindows()
        break


# Sauvegarde d'éventuelles modifications des paramètres de AllData
with open('AllData.json', 'w') as file:
	json.dump(allData, file)
    
# Sauvegarde des trajectoires
sauvTraj(trajectoiresSauvegardees, coin1, coin2)
    