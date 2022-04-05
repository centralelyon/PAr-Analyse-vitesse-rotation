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



#initialisation listes tracking
liste_x_trackee = []
liste_y_trackee = []

#ouverture de la vidéo
video = cv2.VideoCapture("coup_5_trimmed.mp4")

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
     
    #visualisation de la frame, et mise en pause    
    #cv2.imshow("Frame",frame)
    if cv2.waitKey(100)==ord(" "):
        cv2.waitKey(0)
        
    
    
    nFrame+=1

#ouverture du fichier texte
f = open("coup_5_trimmed.txt",'r',encoding="utf-8") 
stringFile = f.read()
f.close()

#conversion en tableau
listeFile = stringFile.split("\n")
for i in range(len(listeFile)):
    listeFile[i] =listeFile[i].split(";")


#plt.figure()
#plt.scatter(liste_temps,liste_erreurs,marker="x",color="orange")
#plt.plot(liste_temps,yobj,color="red",linestyle='--')
#plt.plot(liste_temps,ymoy,color="green")
#plt.grid()
#plt.legend(["Erreur réelle","Critère de précision du cahier des charges","Erreur moyenne mesurée"])
#plt.xlabel("Temps (s)")
#plt.ylabel("Erreur de tracking (px)")
#plt.title("Erreur de tracking en fonction du temps")
#plt.ylim(0,20)
#plt.show()  


liste_y_pointee_plot=[]
liste_y_trackee_plot=[]
for i in range(len(liste_y_pointee)):
    liste_y_pointee_plot.append(hauteurVideo-liste_y_pointee[i])
for i in range(len(liste_y_trackee)):
    liste_y_trackee_plot.append(hauteurVideo-liste_y_trackee[i])

#Plot de la trajectoire théorique vs trackée
plt.plot(liste_x_pointee,liste_y_pointee_plot,c='green')
plt.scatter(liste_x_trackee,liste_y_trackee_plot,c='red',marker="x")

#plt.axis('scaled')
plt.xlim(713,1326)
plt.ylim(1530,1792)
plt.xlabel("x (px)")
plt.ylabel("y (px)")
plt.title("Comparaison des trajectoires pointées et trackées")
plt.legend(["Valeurs pointées","Valeurs trackées"])
plt.show()

#Plot de l'erreur de tracking en pixel, en fonction du temps
liste_temps=[]
for i in range(len(listeDetection)):
    liste_temps.append(listeDetection[i]/fps)

liste_erreurs=[]
for i in range(len(listeDetection)):
    liste_erreurs.append(np.sqrt((liste_x_pointee[listeDetection[i]]-liste_x_trackee[i])**2+(liste_y_pointee[listeDetection[i]]-liste_y_trackee[i])**2))

#Plot de lignes de référence
    
plt.figure()
plt.scatter(liste_temps,liste_erreurs,marker="x",color="orange")
plt.plot(liste_temps,yobj,color="red",linestyle='--')
plt.plot(liste_temps,ymoy,color="green")
plt.grid()
plt.legend(["Erreur réelle","Critère de précision du cahier des charges","Erreur moyenne mesurée"])
plt.xlabel("Temps (s)")
plt.ylabel("Erreur de tracking (px)")


