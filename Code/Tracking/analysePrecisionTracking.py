# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 14:02:47 2022

@author: Guillaume
"""
import matplotlib.pyplot as plt
import cv2
import ModuleTracking
import numpy as np
import scipy.stats as ss

def compErrVit(file):
    
    #initialisation listes tracking
    liste_x_trackee = []
    liste_y_trackee = []
    
    #ouverture de la vidéo
    video = cv2.VideoCapture(file+".mp4")
    
    lower = (0, 166, 0)
    upper = (9, 255, 255)
    
    fps = 30
    
    nFrame = 0
    listeDetection = []
    while True:
        grabbed , frame = video.read()
        if frame is None: 
            break
        
        center = ModuleTracking.trackingBillard(frame,upper,lower)
        if not(center is None):
            liste_x_trackee.append(center[0])
            liste_y_trackee.append(center[1])
            listeDetection.append(nFrame) #permet de calculer les erreurs , si détection
        else:
            print(nFrame)
            cv2.imshow("Frame manquee",frame)
            cv2.waitKey(1000)
        
        nFrame+=1
            
        
        cv2.waitKey(1)

    #ouverture du fichier texte
    f = open(file+".txt",'r',encoding="utf-8") 
    stringFile = f.read()
    f.close()
    
    #conversion en tableau
    listeFile = stringFile.split("\n")
    for i in range(len(listeFile)):
        listeFile[i] =listeFile[i].split(";")
        
    #création des listes de coordonnées 
    liste_x_pointee=[]
    liste_y_pointee=[]
    for elt in listeFile[2:-1]: #on supprime les 2 premières lignes: texte
        liste_x_pointee.append(float(elt[1]))
        liste_y_pointee.append(float(elt[2]))
    vitesse=[]
    for i in range(len(liste_x_pointee)-1):
        vitesse.append(np.sqrt((liste_x_pointee[i+1]-liste_x_pointee[i])**2+(liste_y_pointee[i+1]-liste_y_pointee[i])**2))

#conversion coordonnees cart

# hauteurVideo = 1980 #frame.shape[0]#frame non none

# liste_y_pointee_plot=[]
# liste_y_trackee_plot=[]
# for i in range(len(liste_y_pointee)):
#     liste_y_pointee_plot.append(hauteurVideo-liste_y_pointee[i])
# for i in range(len(liste_y_trackee)):
#     liste_y_trackee_plot.append(hauteurVideo-liste_y_trackee[i])



# #Plot de la trajectoire théorique vs trackée
# plt.plot(liste_x_pointee,liste_y_pointee_plot,c='green')
# plt.scatter(liste_x_trackee,liste_y_trackee_plot,c='red',marker="x")




# #plt.axis('scaled')
# plt.xlim(713,1326)
# plt.ylim(1530,1785)
# plt.xlabel("x (px)")
# plt.ylabel("y (px)")
# plt.title("Comparaison des trajectoires pointées et trackées")
# plt.legend(["Valeurs pointées","Valeurs trackées"])
# plt.show()

#Plot de l'erreur de tracking en pixel, en fonction du temps
    liste_temps=[]
    for i in range(len(listeDetection)):
        liste_temps.append(listeDetection[i]/fps)
    
    liste_erreurs=[]
    for i in range(len(listeDetection)):
        liste_erreurs.append(np.sqrt((liste_x_pointee[listeDetection[i]]-liste_x_trackee[i])**2+(liste_y_pointee[listeDetection[i]]-liste_y_trackee[i])**2))

# #Plot de lignes de référence
# objectif = 7.7
# yobj = objectif * np.ones(len(listeDetection))    

# moyenne = sum(liste_erreurs)/len(liste_erreurs)
# ymoy = moyenne * np.ones(len(listeDetection))   

    
# plt.figure()
# plt.scatter(liste_temps,liste_erreurs,marker="x",color="orange")
# plt.plot(liste_temps,yobj,color="red",linestyle='--')
# plt.plot(liste_temps,ymoy,color="green")
# plt.grid()
# plt.legend(["Erreur réelle","Critère de précision","Erreur moyenne"])
# plt.xlabel("Temps (s)")
# plt.ylabel("Erreur de tracking (px)")
# plt.title("Erreur de tracking en fonction du temps")
# plt.ylim(0,20)
# plt.show()  


# #calcul de l'erreur moyenne
# print("Erreur de tracking moyenne : " ,  sum(liste_erreurs)/len(liste_erreurs))
# #calcul du nombre de frames trackées
# print("Taux de détection : " , len(listeDetection)/len(liste_x_pointee)*100, "%")
    return vitesse,liste_erreurs[:-1]

allSpeed=[]
allError=[]
files = list(range(1,13))
files.pop(9)
for num in files:
    vit, err = compErrVit("coup_"+str(num)+"_trimmed")
    allSpeed+=vit
    allError+=err


plt.figure("Erreur en fonction de la vitesse")
plt.plot(allSpeed,allError,"x",color="orange")


lr = ss.linregress(allSpeed,allError)
pente = lr.slope
ordoneeOrigine = lr.intercept
R2 = lr.rvalue

x = list(range(int(min(allSpeed)),int(max(allSpeed)),1))
y = [pente*abscisse+ordoneeOrigine for abscisse in x]
plt.plot(x,y,'blue')

objectif = 7.7
yobj = objectif * np.ones((50,1))
plt.plot(np.ones((50,1)),yobj,color="red",linestyle='--')

plt.title("err = "+str(round(pente,2))+"*vit + "+str(round(ordoneeOrigine,2))+" ; R^2 ="+str(round(R2,4)))
plt.xlabel("Vitesse (px/s)")
plt.ylabel("Erreur de tracking (px)")
plt.grid(True)


