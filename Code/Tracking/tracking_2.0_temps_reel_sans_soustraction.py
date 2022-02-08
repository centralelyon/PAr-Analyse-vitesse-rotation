#vidéo filmée maison, balle orange, avec soustraction de fond
"""
Created on Tue Nov 16 12:28:54 2021

@author: Guillaume
from: https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
"""

from collections import deque
import numpy as np
import argparse
import cv2

#définition des fonctions de traitement de fond
def video2listImage(adresseVideo,saveFPS): # Renvoie une liste d'image sous forme d'array
    video = cv2.VideoCapture(adresseVideo)
    fps = video.get(cv2.CAP_PROP_FPS)
    
    imlist=[]
    continuer = True
    compteur=0
    while continuer:
        isRead , frame = video.read()  # A-t-on lu une image et si oui cette image
        if not isRead:
            continuer = False
        else:
            frameTimeCode = compteur/fps
            if frameTimeCode*fps%1==0: # Si le timeCode*le fps d'enregistrement est entier,
                                       # on sauvegarde l'image
                imlist.append(frame)
            compteur+=1
    return imlist

def subImageMoyArr(imListArr): # Renvoie un tableau OpenCV
    n=len(imListArr)
    imCentre=imListArr[n//2]
    imMoy=calcImageMoyenneArr(imListArr)
    
    # Conversion en tableau pour OpenCV
    #imCentreCV2 = imCentre[:,:,::-1].copy()
    #imMoyCV2 = imMoy[:,:,::-1].copy()
    imSub = cv2.subtract(imCentre,imMoy)
    return imSub

def calcImageMoyenneArr(imListArr): # Renvoie array
    w,h=len(imListArr[0]), len(imListArr[0][0])
    arr=np.zeros((h,w,4),np.float)
    images = np.array([image for image in imListArr])
    # Round values in array and cast as 8-bit integer
    arr=np.array(np.mean(images,axis=(0)),dtype=np.uint8)
    return arr

def listImage2Video(imList,writeFPS,nomFichier): #write une image
    height,width,layers=imList[0].shape
    # choose codec according to format needed
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video=cv2.VideoWriter(nomFichier, fourcc, writeFPS,(width,height))
    for img in imList:
        video.write(img)
    return video



#entrée de l'algorithme
namevideo = "Coup_Derriere.mov"

#CETTE LIGNE A CHANGER??
camera = cv2.VideoCapture(0)
fps = camera.get(cv2.CAP_PROP_FPS)


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# initialisation des bornes supérieures et inférieures pour la recherche de couleur. A initialiser avec attention


lower = (11, 89, 136) # orange sans soustraction
upper = (15, 201, 248)

lower = (11, 0, 208) # orange sans soustraction,angle différent
upper = (50, 255, 255)

lower = (11, 0, 208) # orange sans soustraction,angle différent
upper = (50, 255, 255)


#initialisation de la liste des position
pts = deque(maxlen=args["buffer"])


liste_x_trackee=[]
liste_y_trackee=[]
liste_indice_trackee=[]
indice_frame=0

compteurDetection = 0
compteurImage = 0


print("Entrée dans la boucle")
while True:

    (grabbed,frame)=camera.read()
    
    #start timer
    timer = cv2.getTickCount()
    
    if frame is None:
        break
    
    #pre-processing
    #frame=cv2.subtract(frame,imgMoy)
    
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
    #update de la liste des centroids (éventuellement None)
    pts.appendleft(center)
    
    
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


"""
#plotter les courbes
import matplotlib.pyplot as plt

#ouverture du fichier
f = open("Coup_Derriere.txt",'r',encoding="utf-8") 
stringFile = f.read()
f.close()

#conversion en tableau
listeFile = stringFile.split("\n")
for i in range(len(listeFile)):
    listeFile[i] =listeFile[i].split(" ")
    
#création des listes de coordonnées 
liste_x_pointee=[] #axe horizontal, de d à g
liste_y_pointee=[] #axe vertical, de h en b
#autrement dit, coordonnées matricielles

for elt in listeFile[2:-1]:
    liste_x_pointee.append(int(float(elt[1])))
    liste_y_pointee.append(int(float(elt[2])))
    
#mise à l'échelle des coordonnées pour le format de la vidéo
for i in range(len(liste_x_trackee)):
    liste_x_trackee[i] = int(liste_x_trackee[i] *100/scale_percent)
    liste_y_trackee[i] = int(liste_y_trackee[i] *100/scale_percent)
    
#pour plotter en coordonnées cartésiennes et non matricielles il faut inverser l'axe y
liste_y_pointee_plot=[]
liste_y_trackee_plot=[]

for i in range(len(liste_y_pointee)):
    liste_y_pointee_plot.append(2160-liste_y_pointee[i])

for i in range(len(liste_y_trackee)):
    liste_y_trackee_plot.append(2160-liste_y_trackee[i])
    

#Plot de la trajectoire théorique vs trackée
plt.plot(liste_x_pointee,liste_y_pointee_plot,c='green')
plt.scatter(liste_x_trackee,liste_y_trackee_plot,c='red',marker="x")

plt.axis('scaled')
plt.xlabel("x (px)")
plt.ylabel("y (px)")
plt.title("Comparaison des trajectoires pointées et trackées sans soustraction")
plt.legend(["Valeurs pointées","Valeurs trackées"])
plt.show()

#Plot de l'erreur de tracking en pixel, en fonction du temps
liste_temps=[]
for i in range(len(liste_indice_trackee)):
    liste_temps.append(liste_indice_trackee[i]/fps)

liste_erreurs=[]
for i in range(len(liste_indice_trackee)):
    liste_erreurs.append(abs(liste_x_pointee[liste_indice_trackee[i]]-liste_x_trackee[i])+abs(liste_y_pointee[liste_indice_trackee[i]]-liste_y_trackee[i]))
  
plt.figure()
plt.scatter(liste_temps,liste_erreurs,marker="x",color="orange")
plt.xlabel("Temps (s)")
plt.ylabel("Erreur de tracking (px)")
plt.title("Erreur de tracking sans soustraction")
plt.show()  

#calcul de l'erreur moyenne
liste_erreurs_coherentes=[elt for elt in liste_erreurs if elt<50]
print("Erreur de tracking pour les valeurs cohérentes : " ,  sum(liste_erreurs_coherentes)/len(liste_erreurs_coherentes))
print("Erreur de tracking pour toutes les valeurs : " , sum(liste_erreurs)/len(liste_erreurs) )
#calcul du nombre de frames trackées
print("Taux de détection : " , len(liste_erreurs_coherentes)/compteurImage*100, "%")

    
"""
    
    
