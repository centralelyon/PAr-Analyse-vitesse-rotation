# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 17:17:47 2021

@author: bperr
"""

import os, numpy
import cv2
import time
import matplotlib.pyplot as plt

def subImageMoy(imListPIL):
    n=len(imListPIL)
    imCentre=numpy.array(imListPIL[n//2],dtype=numpy.uint8)
    imMoy=calcImageMoyenne(imListPIL)
    
    # Conversion en tableau pour OpenCV
    imCentreCV2 = imCentre[:,:,::-1].copy()
    imMoyCV2 = imMoy[:,:,::-1].copy()
    imSub = cv2.subtract(imCentreCV2,imMoyCV2)
    return imSub

def calcImageMoyenne(imListPIL): # Renvoie array
    w,h=imListPIL[0].size
    arr=numpy.zeros((h,w,4),numpy.float)
    images = numpy.array([numpy.array(image) for image in imListPIL])
    # Round values in array and cast as 8-bit integer
    arr=numpy.array(numpy.mean(images,axis=(0)),dtype=numpy.uint8)
    return arr

def subarray(arr1,arr2):
    for i in range(len(arr1)):
        for j in range(len(arr1[i])):
            for k in range(3):
                arr1[i][j][k]=int(arr1[i][j][k])-int(arr2[i][j][k])
    arr1.dtype=numpy.uint8
    return arr1
    


 # --- Ouverture et chargement des images, plus tard remplacé par la caméra ---
"""
adresse=os.getcwd()+"\\ImTest2"
allfiles=os.listdir(adresse)
imlistString=[filename for filename in allfiles if  filename[-4:] in [".png",".PNG"]] #Juste des string des fichiers
# Plus tard, à remplacer par l'aquisition vidéo
print(imlistString)
imlistPIL= [Image.open(adresse+"\\"+im).convert('RGB') for im in imlistString]

 # --- Test sur une image --- 
imlistPIL[len(imlistPIL)//2].show()

imM = Image.fromarray(calcImageMoyenne(imlistPIL))
imM.show()

imSM = subImageMoy(imlistPIL)
cv2.imshow('Image Moyenne',imSM)
"""

 # --- Sur une suite d'image ---
"""
tailleMoy=9

adresse=os.getcwd()+"\\ImTest2"
allfiles=os.listdir(adresse)
imlistString=[filename for filename in allfiles if  filename[-4:] in [".png",".PNG"]] 
#Juste des string des fichiers
# Plus tard, à remplacer par l'aquisition vidéo
print(imlistString)
imlistPIL= [Image.open(adresse+"\\"+im).convert('RGB') for im in imlistString]

imlistMoy = [0]*tailleMoy
imlistSubMoy = [0]*(len(imlistPIL)-tailleMoy+1)
for i in range(tailleMoy//2,len(imlistPIL)-tailleMoy//2):
    # On selectionne les images autour de celle centrale
    for j in range(tailleMoy):
        imlistMoy[j]=imlistPIL[j+i-tailleMoy//2]
    imlistSubMoy[i-tailleMoy//2]=subImageMoy(imlistMoy)

# Affichage des images
for i in range(len(imlistSubMoy)):
    cv2.imshow("Image "+str(i),imlistSubMoy[i])
"""

 # --- Sur une vidéo ---
 
def video2listImage(adresseVideo): # Renvoie une liste d'image sous forme d'array
    video = cv2.VideoCapture(adresseVideo)
    videoFPS = video.get(cv2.CAP_PROP_FPS)
    compteur=0
    #On commence à enregistrer les images
    imlist=[]
    continuer = True
    while continuer:
        isRead , frame = video.read()  # A-t-on lu une image et si oui cette image
        if not isRead:
            continuer = False
        else:
            imlist.append(frame)
            compteur+=1
    duree=compteur/videoFPS
    return imlist,videoFPS,duree

def subImageMoyArr(imListArr,posIm): # Renvoie un tableau OpenCV
    imCentre=imListArr[posIm]
    imMoy=calcImageMoyenneArr(imListArr)
    
    # Conversion en tableau pour OpenCV
    #imCentreCV2 = imCentre[:,:,::-1].copy()
    #imMoyCV2 = imMoy[:,:,::-1].copy()
    imSub = cv2.subtract(imCentre,imMoy)
    return imSub

def calcImageMoyenneArr(imListArr): # Renvoie array
    w,h=len(imListArr[0]), len(imListArr[0][0])
    arr=numpy.zeros((h,w,4),numpy.float)
    images = numpy.array([image for image in imListArr])
    # Round values in array and cast as 8-bit integer
    arr=numpy.array(numpy.mean(images,axis=(0)),dtype=numpy.uint8)
    return arr


def SubImageMoySurListe(imList,tailleMoy,PosIm):
    imlistMoy = [0]*tailleMoy
    imlistSubMoy = [0]*(len(imList)-tailleMoy+1)
    for i in range(PosIm,len(imList)-(tailleMoy-PosIm)):
        # On selectionne les images autour de celle centrale
        for j in range(tailleMoy):
            imlistMoy[j]=imList[j+i-PosIm]
        imlistSubMoy[i-PosIm]=subImageMoyArr(imlistMoy,PosIm)
    return imlistSubMoy


def listImage2Video(imList,writeFPS,nomFichier):
    height,width,layers=imList[0].shape
    # choose codec according to format needed
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video=cv2.VideoWriter(nomFichier, fourcc, writeFPS,(width,height))
    for img in imList:
        video.write(img)
    return video

def readVideo(nomFichier):
    cap = cv2.VideoCapture(nomFichier)
    videoFPS = cap.get(cv2.CAP_PROP_FPS)
    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video  file")
    # Read until video is completed
    while(cap.isOpened()):
      # Capture frame-by-frame
      ret, frame = cap.read()
      if ret == True:
        # Display the resulting frame
        cv2.imshow('Frame', frame)
        time.sleep(1/videoFPS)
        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
          break
      # Break the loop
      else: 
        break
    # When everything done, release 
    # the video capture object
    cap.release()


videoReadFile="Vidéos/echanges_1(1).mov"
imList, FPS, duree  = video2listImage(videoReadFile) # Tableau d'array
#cv2.imshow('Frame 1',imList[4])
"""
frame = imList[40]
cv2.imshow('Image en cours de traitement',frame)
cv2.imshow('Image pré en cours de traitement',imList[39])
cv2.imshow('Image post en cours de traitement',imList[41])
frameMoy = calcImageMoyenneArr(imList[38:43])
cv2.imshow('Image Moyenne',frameMoy)
frameSub = subImageMoyArr(imList[38:43],3)
cv2.imshow('ImageSub',frameSub)
"""
#tailleMoy = 5
#posIm = 3
#imListSubMoy=SubImageMoySurListe(imList, tailleMoy,posIm) # Les mêmes images, auxquelles on a 
                                                    # enlevé les images moyennes
#cv2.imshow('Frame 1 Sub',imListSubMoy[3])

## Analyse
def variationListe(L):
    variation = numpy.zeros((len(L)-1,1))
    x,y,z=numpy.shape(L[0])
    for i in range(len(L)-1):
        cpt=0
        for j in range(x):
            for k in range(y):
                if (abs(L[i][j][k]-L[i+1][j][k])).any()!=0:
                    cpt+=1
        variation[i]=cpt/(x*y)*100
    return variation

def variationListeNorme(L):
    variation = numpy.zeros((len(L)-1,1))
    x,y,z=numpy.shape(L[0])
    for i in range(len(L)-1):
        for j in range(x):
            for k in range(y):
                variation[i]+=numpy.linalg.norm(L[i][j][k]-[255,255,255])
    return variation

def variationListeNorme2(L):
    variation = numpy.zeros((len(L)-1,1))
    x,y,z=numpy.shape(L[0])
    blanc=numpy.ones((x,y,z))*255
    for i in range(len(L)-1):
        variation[i]+=numpy.linalg.norm(L[i]-blanc)
    return variation
"""
n=len(imList)
nSub=len(imListSubMoy)

numFrame=numpy.arange(nSub//5-1)
print("débutSub")
variationPixelSub=variationListeNorme(imListSubMoy[nSub//5:2*(nSub//5)])
print("finSub")
print("débutOriginal")
variationPixel=variationListeNorme(imList[nSub//5+posIm:2*(nSub//5)+posIm])
print("finOriginal")

plt.figure()
plt.plot(numFrame,variationPixel)
plt.plot(numFrame,variationPixelSub)
plt.grid()
plt.xlabel("Numéro d'image")
plt.ylabel("Écart à un pixel blanc")
plt.title("Somme des normes de l'écart à un pixel blanc")
plt.legend(["Vidéo originale","Vidéo après soustraction"])
plt.show()
"""

plt.figure()
tailles=[3,5,7,9,11]
for t in tailles:
    print(t)
    p=1+t//2
    imListSub=SubImageMoySurListe(imList, t, p)
    nSub=len(imListSub)
    numFrame=numpy.arange(p,p+nSub//10-1)
    var=variationListeNorme(imListSub[nSub//10:2*(nSub//10)])
    plt.plot(numFrame,var)
    del imListSub
    del var
    del numFrame
plt.grid()
plt.xlabel("Numéro d'image")
plt.ylabel("Écart à un pixel blanc")
plt.title("Influence de la taille de l'intervalle de calcul de l'image moyenne")
legende=["TailleMoy = "+str(t) for t in tailles]
plt.legend(legende)
plt.show()

    
"""

def readAndWork(adresseVideo,saveFPS,tailleMoy,posIm):
    video = cv2.VideoCapture(adresseVideo)
    videoFPS = video.get(cv2.CAP_PROP_FPS)
    imlist=[]
    compteur=0
    while len(imlist)<tailleMoy:
        isRead , frame = video.read()  # A-t-on lu une image et si oui cette image
        if not isRead:
            print("Vidéo trop courte par rapport à l'intervalle choisi")
            return None
        else:
            frameTimeCode = compteur/videoFPS
            if frameTimeCode*fps%1==0: # Si le timeCode*le fps d'enregistrement est entier, on sauvegarde l'image
                imlist.append(frame)
            compteur+=1
    # Ici la liste est complète
    imgSub = subImageMoyArr(imlist, posIm)
    
    # # Détection de la balle # #
    
    
    imlist.pop(0)
    
    continuer = True
    while continuer:
        isRead , frame = video.read()  # A-t-on lu une image et si oui cette image
        if not isRead:
            continuer = False
        else:
            frameTimeCode = compteur/videoFPS
            if frameTimeCode*fps%1==0: # Si le timeCode*le fps d'enregistrement est entier,
                                       # on sauvegarde l'image
                imlist.append(frame)
            compteur+=1
        imgSub = subImageMoyArr(imlist, posIm)
        if compteur%10==0:
            cv2.imshow(str(compteur/10),imgSub)
        # # Détection de la balle # #
    
        imlist.pop(0) # On retire la première image, on va donc en rajouter dans la 
    
    
    return True



videoReadFile="Table Tennis in Slow Motion.mp4"
tailleIntervalle=5
position=2;
saveFPS=24

readAndWork(videoReadFile, saveFPS, tailleIntervalle, position)
"""