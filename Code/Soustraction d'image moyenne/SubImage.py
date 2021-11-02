# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 17:17:47 2021

@author: bperr
"""

import os, numpy, PIL
from PIL import Image
import cv2
import time



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
 
def video2listImage(adresseVideo,saveFPS): # Renvoie une liste d'image sous forme d'array
    video = cv2.VideoCapture(adresseVideo)
    videoFPS = video.get(cv2.CAP_PROP_FPS)
    fps = min(saveFPS,videoFPS) # On peut enregistrer moins d'images en mettant un saveFPS 
                                # inférieur mais pas l'inverse
    fps=videoFPS
    imlist=[]
    continuer = True
    compteur=0
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
    arr=numpy.zeros((h,w,4),numpy.float)
    images = numpy.array([image for image in imListArr])
    # Round values in array and cast as 8-bit integer
    arr=numpy.array(numpy.mean(images,axis=(0)),dtype=numpy.uint8)
    return arr

def SubImageMoySurListe(imList,tailleMoy):
    imlistMoy = [0]*tailleMoy
    imlistSubMoy = [0]*(len(imList)-tailleMoy+1)
    for i in range(tailleMoy//2,len(imList)-tailleMoy//2):
        # On selectionne les images autour de celle centrale
        for j in range(tailleMoy):
            imlistMoy[j]=imList[j+i-tailleMoy//2]
        imlistSubMoy[i-tailleMoy//2]=subImageMoyArr(imlistMoy)
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


videoReadFile="TT Real Speed.mp4"
imList = video2listImage(videoReadFile,24) # Tableau d'array
cv2.imshow('Frame 1',imList[0])

tailleMoy = 3
imListSubMoy=SubImageMoySurListe(imList, tailleMoy) # Les mêmes images, auquelles on a 
                                                    # enlevé les images moyennes
cv2.imshow('Frame 1 Sub',imListSubMoy[0])

videoWriteFile="SUB TT Real Speed.mp4"
videoSub = listImage2Video(imListSubMoy, 24, videoWriteFile)
videoSub.release()

readVideo(videoWriteFile)

