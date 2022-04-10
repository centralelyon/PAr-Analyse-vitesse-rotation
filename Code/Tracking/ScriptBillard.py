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
        



def detectionRebond(lV,seuil):
    rebond = False
    i=1
    #Signe global de la trajectoire
    vitX = np.mean([lV[i][0] for i in range(len(lV))])
    vitY = np.mean([lV[i][1] for i in range(len(lV))])
    signeX = vitX>=0
    signeY = vitY>=0
    axis = -1
    
    
    if (lV[-1][0]>=0)!=signeX: # Changement de signe de Vx
        #print('Rebond X potentiel')
        if abs(lV[-2][0]-lV[-1][0])>seuil:
            print('Rebond X confirme',lV[i-1][0],lV[i][0],lV[i-1][0]-lV[i][0],i)
            rebond=True
            axis = 0
        else:
            #print('Rebond X infirme',lV[i-1][0],lV[i][0],lV[i-1][0]-lV[i][0])
            pass

    if (lV[-1][1]>=0)!=signeY: # Changement de signe de Vx
        #print('Rebond Y potentiel')
        if abs(lV[-2][1]-lV[-1][1])>seuil:
            print('Rebond Y confirme',lV[i-1][1],lV[i][1],lV[i-1][1]-lV[i][1],i)
            rebond=True
            axis = 1
        else:
            #print('Rebond Y infirme',lV[i-1][1],lV[i][1],lV[i-1][1]-lV[i][1])
            pass
    
    return rebond,axis

def affRebond(fond2,coord3,axis,coin1,coin2,radius):
    if axis==0: # rebond sur les bandes horizontales
        if coord3[1]>=(coin1[1]+coin2[1])/2:
            y=coin2[1]
        else:
            y=coin1[1]
        xmin = max(coin1[0],coord3[0]-radius)
        xmax = min(coin2[0],coord3[0]+radius)
        cv2.line(fond2,(xmin,y),(xmax,y),(0,0,255),5)
    
    else: # rebond sur les bandes verticales
        if coord3[0]>=(coin1[0]+coin2[0])/2:
            x=coin2[0]
        else:
            x=coin1[0]
        ymin = max(coin1[1],coord3[1]-radius)
        ymax = min(coin2[1],coord3[1]+radius)
        cv2.line(fond2,(x,ymin),(x,ymax),(0,0,255),5)

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
fond2 = fond.copy()
yZoneCommande = int(allData["coeftextCmdY"]*height)


# Full screen et affiché par dessus les autres fenêtres dès le début
window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
resized,newCoin1,newCoin2 = Reconstruction3D.positionnerTable(fond2,window_name,coin1,coin2,yZoneCommande)

if resized : # On a redéfini les dimensions du rectangle
    coin1 = newCoin1
    coin2 = newCoin2
    allData["coefRectangleX1"] = round(coin1[0]/width,5)
    allData["coefRectangleY1"] = round(coin1[1]/height,5)
    allData["coefRectangleX2"] = round(coin2[0]/width,5)
    allData["coefRectangleY2"] = round(coin2[1]/height,5)

fond = cv2.rectangle(fond,coin1,coin2,(0,0,0),5)

coin1Rebond = (int(coin1[0]+0.02*(coin2[0]-coin1[0])),int(coin1[1]+0.02*(coin2[0]-coin1[0])))
coin2Rebond = (int(coin2[0]-0.02*(coin2[0]-coin1[0])),int(coin2[1]-0.02*(coin2[0]-coin1[0])))

fond2 = fond.copy()
cv2.putText(fond2,"Veuillez patienter, la camera se connecte...",(int((8*coin1[0]+2*coin2[0])/10),int((coin1[1]+coin2[1])/2)),cv2.FONT_HERSHEY_SIMPLEX, 2.75, (0, 0, 0), 2)
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
nbRebond = 0

fond2 = fond.copy()
cv2.putText(fond2,"Voulez vous utiliser la matrice d'homographie sauvegardee",(int(1.5*coin1[0]),int((10*coin1[1]+8*coin2[1])/18)),cv2.FONT_HERSHEY_SIMPLEX, 2.75, (0, 0, 0), 2)
cv2.putText(fond2,"ou alors la determiner a nouveau ? [y/n]",(int(1.5*coin1[0]),int((8*coin1[1]+10*coin2[1])/18)),cv2.FONT_HERSHEY_SIMPLEX, 2.75, (0, 0, 0), 2)
cv2.imshow(window_name,fond2)
while True:
    key = cv2.waitKey()
    if key == ord('y'):
        hg = np.array(allData["homography"])
        break
    elif key == ord('n'):
        cv2.destroyAllWindows()
        hg = Reconstruction3D.getHomographyForBillard(camera,upper,lower,(largeur,longueur),epaisseurBord,diametre)
        l4 = [list(e) for e in hg]
        l5=[]
        for i in range(len(l4)):
            ltemp=[]
            for j in range(len(l4[i])):
                ltemp.append(l4[i][j].item()) # conversion int32 to int
            l5.append(ltemp)
        allData["homography"] = l5
        break


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
axis = -1

instantDernierAjout=t.time()
mode = 0  # Mode de fonctionnement du programe
fond2=fond.copy()
instantDebutTrajectoire=t.time()

# Commandes disponibles 
cv2.putText(fond2,"s : Sauvegarder une trajectoire",(coin1[0],yZoneCommande),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(fond2,"r : Selectionner une trajectoire pour la rejouer",(coin1[0],int(yZoneCommande*1.1)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(fond2,"p : Lancer une partie",(coin1[0],int(yZoneCommande*1.2)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(fond2,"q : Quitter",(coin1[0],int(yZoneCommande*1.3)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)



while True:
   
    
    key = cv2.waitKey(1) # Lecture d'interraction clavier par l'utilisateur
    #fond2 = fond.copy() # Copie de l'image de fond générique, qui sera modifiée si l'on doit afficher de nouvelles choses
    
    
    if mode == 0:
        grabbed,frame = camera.read() # Lecture de l'image vue par la caméra
        # 33.23 s
        
        center = ModuleTracking.trackingBillard(frame,upper,lower) # Détection de la position de la bille sur cette image
        # 0.954 s
        currentTime = t.time()
        if center !=None:
            # Obtention des coordonnées "réelles" grâce à l'homographie
            realCenter = Reconstruction3D.findRealCoordinatesBillard(center,hg,(largeur,longueur),epaisseurBord)
            # 0.0067 s
            # Ajout à la liste des positions de la trajectoire à tracer
            x3,y3 = Reconstruction3D.getCoordProjection(realCenter,largeur,longueur,coin1,coin2)
            # 0.0036 s
            listPosProj.append((x3,y3,currentTime))

            #traitement de la trajectoire à tracer : effacement après tempsTrace secondes 
            # Affichage de la trajectoire sur l'image de fond  
            Reconstruction3D.affTraj(listPosProj,fond2,currentTime,tempsTrace)
            # 0.0038 s
            
            #traitement de la trajectoire à sauvegarder
            if  (currentTime-instantDernierAjout>tempsAjoutTrajectoire): 
                instantDernierAjout=currentTime
                derniereTrajectoire.append(realCenter+tuple([currentTime-instantDebutTrajectoire]))
                
 
        
        #detection arret
        
        if arret and len(derniereTrajectoire)>=10 and not(Reconstruction3D.detectionArret(derniereTrajectoire[-10:] , seuil)): #si on se met à bouger, on commence une nouvelle trajectoire
            #réinitialiser et initialiser les liste de tracking
            derniereTrajectoire=[positionArret+tuple([0])]
            instantDebutTrajectoire=currentTime
            arret=False
            #print('En mouvement')
            cv2.putText(fond2,"A l'arret",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 2)
            cv2.putText(fond2,"En mouvement",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 200, 0), 2)
            # 0.14 s
            cv2.rectangle(fond2,coin1Rebond,coin2Rebond,(255,255,255),5)
            
        #on n'autorise que des mouvements de + d'1 sec. (arbitraire)
        if not arret and len(derniereTrajectoire)>=10 and Reconstruction3D.detectionArret(derniereTrajectoire[-10:], seuil): 
            positionArret=realCenter #si on passe à l'arret, on sauvegarde la position d'arret
            arret=True
            print(nbRebond)
            nbRebond=0
            #print('A l arret')
            cv2.putText(fond2,"En mouvement",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 2)
            cv2.putText(fond2,"A l'arret",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 255), 2)
            # 0.14 s
            
        #Détection rebond
        if len(derniereVitesse)==nbVitesse:
            if not rebond and not arret :
                rb,axis = detectionRebond(derniereVitesse,seuilRebond) # 0.03s
                if rb:
                    #print("Rebond !")
                    #cv2.circle(fond2,listPosProj[-3][:2],100,(0,0,0))
                    rebond=True
                    nbRebond+=1
                    tpsrebond=t.time()
                    affRebond(fond2, listPosProj[-3][:2], axis, coin1Rebond, coin2Rebond, 100)
                    
      
        if currentTime-tpsrebond>0.1:
            rebond = False
            axis = -1
    
        
        
        # Calcul et affichage vitesse
        if len(derniereTrajectoire)>1:                
            cv2.putText(fond2,"Vitesse : "+str(round(np.linalg.norm(vitesseBille),2))+" mm/s",(int(allData["coeftextInfoX"]*width),2*int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
            if arret:
                vitesseBille=(0,0)
            else:
                vitesseBille=((derniereTrajectoire[-1][0]-derniereTrajectoire[-2][0])/(derniereTrajectoire[-1][2]-derniereTrajectoire[-2][2]),(derniereTrajectoire[-1][1]-derniereTrajectoire[-2][1])/(derniereTrajectoire[-1][2]-derniereTrajectoire[-2][2]))
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
            
        #passage au mode 4 possible uniquement si on est à l'arrêt. 
        if key==ord("p") and arret:
            mode=4
            
        cv2.imshow(window_name,fond2)
            
        
        
        
    if mode == 1:
        fond2=fond.copy() #on efface l'ecran .
        cv2.putText(fond2,"1 a 9 : Selectionner une trajectoire",(coin1[0],yZoneCommande),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
        cv2.putText(fond2,"Entree : Valider le choix",(coin1[0],int(yZoneCommande*1.1)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
        cv2.putText(fond2,"echap : Retourner au mode de jeu classique",(coin1[0],int(yZoneCommande*1.2)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
        cv2.putText(fond2,"q : Quitter",(coin1[0],int(yZoneCommande*1.3)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

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
            
            elif key == 27: #echap
                fond2=fond.copy()    
                mode=0
                cv2.putText(fond2,"s : Sauvegarder une trajectoire",(coin1[0],yZoneCommande),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
                cv2.putText(fond2,"r : Selectionner une trajectoire pour la rejouer",(coin1[0],int(yZoneCommande*1.1)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
                cv2.putText(fond2,"p : Lancer une partie",(coin1[0],int(yZoneCommande*1.2)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
                cv2.putText(fond2,"q : Quitter",(coin1[0],int(yZoneCommande*1.3)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
                

                break
            
            elif 49 <= key <= 49+len(trajectoiresSauvegardees)-1:
                #réinitialisation de l'image 
        
                fond2=fond3.copy()
                
                #actualisation de la selection
                indTrajSelectionnee = key - 48 - 1 #le chiffre appuyé est -48, l'indice de la liste est -49
                
                #tracer le chiffre selectionné en couleur, afficher la trajectoire
                cv2.putText(fond2,str(indTrajSelectionnee+1),(int(allData["coeftextInfoX"]*width + 50 * indTrajSelectionnee ),int(allData["coeftextMoovY"]*height + 200 )),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 0, 255), 2)
                Reconstruction3D.affTrajTotal(trajectoiresSauvegardees[indTrajSelectionnee],fond2)
                
                cv2.imshow(window_name,fond2)
            
            elif key==ord('q'):
                break
    
        
    if mode==2:
        # On reprend le fond de base
        fond2=fond.copy()
        #fond: selection du mode.
        #effacer chiffres selection du mode 3
        cv2.putText(fond2,"Placez la bille",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 255, 0), 2)
        cv2.putText(fond2,"a l'endroit",(int(allData["coeftextInfoX"]*width),int(1.4*allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 255, 0), 2)
        cv2.putText(fond2,"indique",(int(allData["coeftextInfoX"]*width),int(1.8*allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5 , (0, 255, 0), 2)
        
        cv2.putText(fond2,"echap : Retour a la selection de la trajectoire",(coin1[0],yZoneCommande),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
        cv2.putText(fond2,"q : Quitter",(coin1[0],int(yZoneCommande*1.1)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

        
        #afficher la position de la balle  en pointillés
        posIni = trajectoiresSauvegardees[indTrajSelectionnee][0][:2]
        cv2.circle(fond2,posIni,150,(0,0,255),6,cv2.LINE_AA)
        cv2.imshow(window_name,fond2)
        fond3 = fond2.copy()
        cv2.circle(fond3,posIni,200,(0,0,255),9,cv2.LINE_AA)
        #fond 3= fond
        #fond3 = fond2.copy()
        distanceMin=5
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
            
            elif key==ord('q'):
                break
        
        #sinon:
        #mode 3, reset graphique et preset
        if mode ==2:
            fond2=fond.copy()
            Reconstruction3D.affTrajPrevis(trajectoiresSauvegardees[indTrajSelectionnee],fond2)
            #derniereTrajectoire=[ posIniReel+tuple([0]) ]
            derniereTrajectoire=[realCenter+tuple([0])]
            listPosProj= [posIni+tuple([0])]
            instantDebutTrajectoire=t.time()
            arret=True
            finCoup=False
            mode=3
        
        
            
    if mode==3:
        # L'affichage de la trajectoire sauvegardée se fait au moment de la transition, pour que l'on ne raffiche pas la trajectoire à chaque itération de la boucle while
        if not finCoup: # L'utilisateur n'a pas fini son coup
            grabbed,frame = camera.read()
            center = ModuleTracking.trackingBillard(frame,upper,lower) # Détection de la position de la bille sur cette image
            currentTime = t.time()
            if center !=None:
                # Obtention des coordonnées "réelles" grâce à l'homographie
                realCenter = Reconstruction3D.findRealCoordinatesBillard(center,hg,(largeur,longueur),epaisseurBord)
                # Ajout à la liste des positions de la trajectoire à tracer
                x3,y3 = Reconstruction3D.getCoordProjection(realCenter,largeur,longueur,coin1,coin2)
                listPosProj.append((x3,y3,currentTime))
		
                # Affichage de la trajectoire sur l'image de fond  
                Reconstruction3D.affTrajRejeu(listPosProj,fond2)
            
                #traitement de la trajectoire à sauvegarder
                if  (currentTime-instantDernierAjout>tempsAjoutTrajectoire): 
                    instantDernierAjout=currentTime
                    derniereTrajectoire.append(realCenter+tuple([currentTime-instantDebutTrajectoire]))
                    
            #detection debut trajectoire
            if arret and len(derniereTrajectoire)>=10 and not(Reconstruction3D.detectionArret(derniereTrajectoire[-10:] , seuil)): #si on se met à bouger, on commence une nouvelle trajectoire
                #réinitialiser et initialiser les liste de tracking
                derniereTrajectoire=[posIniReel+tuple([0])]
                instantDebutTrajectoire=currentTime
                arret=False
            
            #Lorsque la balle s'arrête, c'est la fin du coup rejoué
            if not arret and len(derniereTrajectoire)>=10 and Reconstruction3D.detectionArret(derniereTrajectoire[-10:], seuil): 
                arret=True
                finCoup=True
                positionArret=realCenter
                # Affichage des nouvelles commandes
                cv2.putText(fond2,"0 : Retour au mode de jeu classique",(coin1[0],yZoneCommande),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
                cv2.putText(fond2,"1 : Rejouer un autre coup",(coin1[0],int(yZoneCommande*1.1)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
                cv2.putText(fond2,"2 : Rejouer le meme coup",(coin1[0],int(yZoneCommande*1.2)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
                cv2.putText(fond2,"s : Sauvegarder la nouvelle trajectoire",(coin1[0],int(yZoneCommande*1.3)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
                cv2.putText(fond2,"Maj + s : Sauvegarder en ecrasant l'ancienne trajectoire",(coin1[0],int(yZoneCommande*1.4)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
                cv2.putText(fond2,"q : Quitter",(coin1[0],int(yZoneCommande*1.5)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

        
            cv2.imshow(window_name,fond2)
        
        else: # Interrcation avec l'utilisateur pour savoir quoi faire
            listPosProj=[]
            if key==48: # Retour au mode 0
                fond2=fond.copy()
                cv2.putText(fond2,"s : Sauvegarder une trajectoire",(coin1[0],yZoneCommande),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
                cv2.putText(fond2,"r : Selectionner une trajectoire pour la rejouer",(coin1[0],int(yZoneCommande*1.1)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
                cv2.putText(fond2,"p : Lancer une partie",(coin1[0],int(yZoneCommande*1.2)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

                cv2.putText(fond2,"q : Quitter",(coin1[0],int(yZoneCommande*1.3)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
                mode=0
            
            elif key==49: #_Retour au mode 1
                mode=1
            
            elif key==50: # Retour au mode 2
                mode=2
            
            elif key==ord('s'):
                dt = [Reconstruction3D.getCoordProjection(c, largeur,longueur,coin1,coin2)+tuple([c[2]]) for c in derniereTrajectoire]
                trajectoiresSauvegardees.append(dt)
            
            elif key==ord('S'):
                dt = [Reconstruction3D.getCoordProjection(c, largeur,longueur,coin1,coin2)+tuple([c[2]]) for c in derniereTrajectoire]
                trajectoiresSauvegardees[indTrajSelectionnee]=dt
                
    #C'est le mode de jeu inventé pour la soutenance.
    #Le code est le mode 0, adapté.            
    if mode == 4: 
        #afficher resultat
        
        #on affiche le cercle à chaque fois
        #cv2.circle(fond2
        
        grabbed,frame = camera.read() # Lecture de l'image vue par la caméra
        # 33.23 s
        
        center = ModuleTracking.trackingBillard(frame,upper,lower) # Détection de la position de la bille sur cette image
        # 0.954 s
        currentTime = t.time()
        
        if center !=None:
            # Obtention des coordonnées "réelles" grâce à l'homographie
            realCenter = Reconstruction3D.findRealCoordinatesBillard(center,hg,(largeur,longueur),epaisseurBord)
            # 0.0067 s
            # Ajout à la liste des positions de la trajectoire à tracer
            x3,y3 = Reconstruction3D.getCoordProjection(realCenter,largeur,longueur,coin1,coin2)
            # 0.0036 s
            listPosProj.append((x3,y3,currentTime))

            #traitement de la trajectoire à tracer : effacement après tempsTrace secondes 
            # Affichage de la trajectoire sur l'image de fond  
            Reconstruction3D.affTraj(listPosProj,fond2,currentTime,tempsTrace)
            # 0.0038 s
            
            #traitement de la trajectoire à sauvegarder
            if  (currentTime-instantDernierAjout>tempsAjoutTrajectoire): 
                instantDernierAjout=currentTime
                derniereTrajectoire.append(realCenter+tuple([currentTime-instantDebutTrajectoire]))
                
 
        
        #detection arret
        
        #si on se met à bouger, on commence une nouvelle trajectoire
        if arret and len(derniereTrajectoire)>=10 and not(Reconstruction3D.detectionArret(derniereTrajectoire[-10:] , seuil)): 
            #réinitialiser et initialiser les liste de tracking
            derniereTrajectoire=[positionArret+tuple([0])]
            instantDebutTrajectoire=currentTime
            arret=False
            #print('En mouvement')
            cv2.putText(fond2,"A l'arret",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 2)
            cv2.putText(fond2,"En mouvement",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 200, 0), 2)
            # 0.14 s
            cv2.rectangle(fond2,coin1Rebond,coin2Rebond,(255,255,255),5)
            
        #on n'autorise que des mouvements de + d'1 sec. (arbitraire)
        #si on passe à l'arret
        if not arret and len(derniereTrajectoire)>=10 and Reconstruction3D.detectionArret(derniereTrajectoire[-10:], seuil): 
            positionArret=realCenter 
            arret=True
            print(nbRebond)
            nbRebond=0
            #print('A l arret')
            cv2.putText(fond2,"En mouvement",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 2)
            cv2.putText(fond2,"A l'arret",(int(allData["coeftextInfoX"]*width),int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 255), 2)
            # 0.14 s
            
        #Détection rebond
        if len(derniereVitesse)==nbVitesse:
            if not rebond and not arret :
                rb,axis = detectionRebond(derniereVitesse,seuilRebond) # 0.03s
                if rb:
                    #print("Rebond !")
                    #cv2.circle(fond2,listPosProj[-3][:2],100,(0,0,0))
                    rebond=True
                    nbRebond+=1
                    tpsrebond=t.time()
                    affRebond(fond2, listPosProj[-3][:2], axis, coin1Rebond, coin2Rebond, 100)
                    
      
        if currentTime-tpsrebond>0.1:
            rebond = False
            axis = -1
    
        
        
        # Calcul et affichage vitesse
        if len(derniereTrajectoire)>1:                
            cv2.putText(fond2,"Vitesse : "+str(round(np.linalg.norm(vitesseBille),2))+" mm/s",(int(allData["coeftextInfoX"]*width),2*int(allData["coeftextMoovY"]*height)),cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
            if arret:
                vitesseBille=(0,0)
            else:
                vitesseBille=((derniereTrajectoire[-1][0]-derniereTrajectoire[-2][0])/(derniereTrajectoire[-1][2]-derniereTrajectoire[-2][2]),(derniereTrajectoire[-1][1]-derniereTrajectoire[-2][1])/(derniereTrajectoire[-1][2]-derniereTrajectoire[-2][2]))
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

        
        #initialisation du temps 
        
        #affichage trajectoire
        
            
    
    if key==ord('q'): # quitter avec 'q'
        cv2.destroyAllWindows()
        break


# Sauvegarde d'éventuelles modifications des paramètres de AllData
with open('AllData.json', 'w') as file:
	json.dump(allData, file)
    
# Sauvegarde des trajectoires
sauvTraj(trajectoiresSauvegardees, coin1, coin2)
    