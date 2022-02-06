# PAr-Analyse-vitesse-rotation
Git pour le PAr 107 : Analyse vitesse / rotation de la balle en sport de table


## Présentation du projet
L'objectif de ce projet est de fournir un système de tracking vidéo fonctionnant pour deux sports de tables : le tennis de table et le billard. 
On utilise pour cela un algorithme recherchant la balle (ou les billes) dans l'image par sa (ou ses) couleur(s) dans l'espace HSV. Pour réduire le temps de recherche de la balle, on utilise une mdélisation du mouvement afin de prédire la position de la balle d'une image à la suivante et réduire ainsi le temps de calcul pour la détecter.
Le programme peut traiter des vidéos issues de caméras branchées sur le PC ou bien des fichiers pré-enregistrés.

## Etapes d'installation

