# -*- coding: utf-8 -*-
"""
Module soustraction de l'image moyenne

@author Baptiste Perreyon, Guillaume Paczek
"""
import cv2
import numpy as np


""" 
## Lecture d'un fichier vidéo enregistré sur l'ordinateur

@params adresseVideo : adresse du fichier vidéo à ouvrir
@return imlist : liste d'images représentées par des array de openCV
        fps : nombre d'image par seconde de la vidéo
"""
def video2listImage(adresseVideo):
    video = cv2.VideoCapture(adresseVideo) # Ouverture du fichier dans une variable
    fps = video.get(cv2.CAP_PROP_FPS) # On récupère le nombre d'images par seconde
    imlist=[] # Liste qui stocke les images de la vidéo
    continuer = True
    while continuer:
        isRead , frame = video.read()  # A-t-on lu une image et si oui cette image (si non c'est qu'on a atteint la fin de la vidéo)
        if not isRead:
            continuer = False
        else:
                imlist.append(frame)
    return imlist,fps


"""
## Ecriture d'un fichier vidéo sur l'ordinateur. Utilisée pour sauvegarder en tant que vidéo une liste d'images post-traitement

@params imList : Liste d'images à transformer en vidéo
        writeFPS : Nombre d'images par seconde dans la vidéo à enregister
        nomFichier : adresse où sauvegarder le fichier
@return video : variable permettant de créer un fichier vidéo
"""
def listImage2Video(imList,writeFPS,nomFichier):
    height,width,layers=imList[0].shape # Paramètres de taille de l'image
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # choose codec according to format needed
    video=cv2.VideoWriter(nomFichier, fourcc, writeFPS,(width,height)) # Création d'un objet vidéo qui sera enregistré sur le PC
    for img in imList:
        video.write(img) # On ajoute les images à la vidéo
    return video


"""
## Soustraction de l'image moyenne sur une image d'un intervalle passé en parametre

@params imListArr : liste d'images (arrays openCV) utiles pour le calcule de soustraction d'image moyenne
        PosIm : indice dans la liste de l'image qui subit la soustraction
@return imSub : image après soustraction sous forme de tableau openCV
"""
def subImageMoyArr(imListArr,PosIm):
    n=len(imListArr)
    imCentre=imListArr[PosIm] # Image qui va subir la soustraction
    imMoy=np.array(np.mean(imListArr,axis=(0)),dtype=np.uint8) # Calcule l'image moyenne en arrondissant les valeurs en int sur 8bits (0 à 255)
    imSub = cv2.subtract(imCentre,imMoy) # Soustraction
    return imSub


"""
## Application de la soustraction sur une liste d'images consécutives. Utile pour traiter une vidéo enregistrée.

@params imList : liste d'images sur lesquelles on doit appliquer l'algorithme de soustraction
        tailleMoy : nombre d'images utilisées pour le calcul de soustraction
        PosIm : position de l'image dans l'intervalle des images utilisées pour l'algoritme de soustraction
@return imlistSubMoy : liste d'images post-traitement modélisées par des arrays
"""
def SubImageMoySurListe(imList,tailleMoy,PosIm): # Renvoie une liste des images soustraites
    imlistMoy = [0]*tailleMoy
    imlistSubMoy = [0]*(len(imList)-tailleMoy+1)
    for i in range(PosIm,len(imList)-(tailleMoy-PosIm)):
        # On selectionne les images autour de celle traitée
        for j in range(tailleMoy):
            imlistMoy[j]=imList[j+i-PosIm]
        imlistSubMoy[i-PosIm]=subImageMoyArr(imlistMoy,PosIm)
    return imlistSubMoy

