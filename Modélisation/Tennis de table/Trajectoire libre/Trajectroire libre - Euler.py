# -*- coding: utf-8 -*-
"""
Created on Sun Nov 21 16:18:54 2021

@author: bperr
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

# -- Forces du problème -- #

def fMagnus(alpha,omega,v): # réel, array, array
    return alpha*np.cross(omega,v)

def fFrot(h,v): # réel, array
    return -h*np.linalg.norm(v)*v

def fPoids(m,g): # réel, array
    return m*g

# -- Trajectoire -- #

def Euler(pas,acc,vit,pos): # réel, array, array, array
    pos2=np.array([0.,0.,0.])
    vit2=np.array([0.,0.,0.])
    for i in range (3):
        pos2[i]=pos[i]+vit[i]*pas
        vit2[i]=vit[i]+acc[i]*pas
    return vit2,pos2

def TrajectoireLibre(posIni,vitIni,omega,m,alpha,h,accPes,dimX,dimY,dt): # array, array, array, réels
    # Mémoire au cours de la trajectoire
    position=np.array([posIni])
    vitesse=np.array([vitIni])
    acceleration=np.array(np.empty((0,3)))
    
    # Tableaux pour les calculs
    g=np.array([0,0,-accPes])
    vit=np.array(vitIni)
    pos=np.array(posIni)
    while(pos[2]>0): # balle au dessus de la table
        # Calcul
        acc=(fMagnus(alpha,omega,vit)+fFrot(h, vit)+fPoids(m,g))/m
        vit,pos=Euler(dt,acc,vit,pos)
        # Stockage
        position = np.append(position,[pos],axis=0)
        vitesse = np.append(vitesse,[vit],axis=0)
        acceleration = np.append(acceleration,[acc],axis=0)
    
    if ((abs(pos[0])<dimX/2) and (abs(pos[1])<dimY/2)):
        print("Rebond sur la table")
    else:
        print("La balle est faute")
    
    acc=(fMagnus(alpha,omega,vit)+fFrot(h, vit)+fPoids(m,g))/m
    acceleration = np.append(acceleration,[acc],axis=0)
    
    return acceleration,vitesse,position



## -- Paramètres du calcul -- #

dt = 1e-3
masse = 2.7e-3
rayon = 20e-3
accPes = 9.81
alpha = 1.8e-5
Cx = 0.4
rho = 1.2
longueurTable = 274e-2
largeurTable = 152.5e-2

positionInitiale = np.array([-1.5,0,0.1])
vitesseInitiale = np.array([3,3,3])
vitesseRotation = np.array([0,0,0])

S = np.pi * rayon**2
h = 1/2*rho*Cx*S


## -- Calcul et tracé -- ##

acc,vit,pos= TrajectoireLibre(positionInitiale, vitesseInitiale, vitesseRotation, masse, alpha, h, accPes, longueurTable, largeurTable, dt)

pos2= np.swapaxes(pos,0,1)
x = pos2[0]
y = pos2[1]
z = pos2[2]
vit2= np.swapaxes(vit,0,1)
vx = vit2[0]
vy = vit2[1]
vz = vit2[2]
acc2= np.swapaxes(acc,0,1)
ax = acc2[0]
ay = acc2[1]
az = acc2[2]
tps = np.linspace(0,(len(x)-1)*dt,len(x))

def tracerTrajectoire(x,y,z,tps):
    fig = plt.figure('Trajectoire de la balle')
    axs=fig.add_subplot(2,2,1)
    axs.plot(tps,x)
    axs.set_title('x(t)')
    axs.grid()
    axs.set_xlabel('Temps en s')
    axs.set_ylabel('x en m')
    #axs.legend(["Sans effet","Top-spin","Back-spin","Side-Spin +","Side-Spin -"])

    axs=fig.add_subplot(2,2,2)
    axs.plot(tps,y)
    axs.set_title('y(t)')
    axs.grid()
    axs.set_xlabel('Temps en s')
    axs.set_ylabel('y en m')
    #axs.legend(["Sans effet","Top-spin","Back-spin","Side-Spin +","Side-Spin -"])
    
    axs=fig.add_subplot(2,2,3)
    axs.plot(tps,z)
    axs.set_title('z(t)')
    axs.grid()
    axs.set_xlabel('Temps en s')
    axs.set_ylabel('z en m')
    #axs.legend(["Sans effet","Top-spin","Back-spin","Side-Spin +","Side-Spin -"])
    
    axs=fig.add_subplot(2,2,4,projection='3d')
    axs.plot(x,y,z)
    axs.set_title('Trajectoire')
    axs.set_xlabel('x(t)')
    axs.set_ylabel('y(t)')
    axs.set_zlabel('z(t)')
    #axs.legend(["Sans effet","Top-spin","Back-spin","Side-Spin +","Side-Spin -"])
    plt.show()

tracerTrajectoire(x, y, z, tps)

def tracerVitesses(vx,vy,vz,tps):
    fig = plt.figure("Vitesse la balle") 
    
    axs=fig.add_subplot(2,2,1)
    v=np.sqrt(vx**2+vy**2+vz**2)
    axs.plot(tps,v)
    axs.set_title("Vitesse")
   # axs.legend(["Sans effet","Top-spin","Back-spin","Side-Spin +","Side-Spin -"])
    axs.grid()
    
    axs=fig.add_subplot(2,2,2)
    axs.plot(tps,vx)
    axs.set_title("Vx")
    #axs.legend(["Sans effet","Top-spin","Back-spin","Side-Spin +","Side-Spin -"])
    axs.grid()
    
    axs=fig.add_subplot(2,2,3)
    axs.plot(tps,vy)
    axs.set_title("Vy")
    #axs.legend(["Sans effet","Top-spin","Back-spin","Side-Spin +","Side-Spin -"])
    axs.grid()
    
    axs=fig.add_subplot(2,2,4)
    axs.plot(tps,vz)
    axs.set_title("Vz")
    #axs.legend(["Sans effet","Top-spin","Back-spin","Side-Spin +","Side-Spin -"])
    axs.grid()
    
    plt.show()

tracerVitesses(vx, vy, vz, tps)

def traceracc(ax,ay,az,tps):
    fig = plt.figure("Accélération la balle") 
    
    axs=fig.add_subplot(2,2,1)
    a=np.sqrt(ax**2+ay**2+az**2)
    axs.plot(tps,a)
    axs.set_title("Accélération")
   # axs.legend(["Sans effet","Top-spin","Back-spin","Side-Spin +","Side-Spin -"])
    axs.grid()
    
    axs=fig.add_subplot(2,2,2)
    axs.plot(tps,ax)
    axs.set_title("Ax")
    #axs.legend(["Sans effet","Top-spin","Back-spin","Side-Spin +","Side-Spin -"])
    axs.grid()
    
    axs=fig.add_subplot(2,2,3)
    axs.plot(tps,ay)
    axs.set_title("Ay")
    #axs.legend(["Sans effet","Top-spin","Back-spin","Side-Spin +","Side-Spin -"])
    axs.grid()
    
    axs=fig.add_subplot(2,2,4)
    axs.plot(tps,az)
    axs.set_title("Az")
    #axs.legend(["Sans effet","Top-spin","Back-spin","Side-Spin +","Side-Spin -"])
    axs.grid()
    
    plt.show()

traceracc(ax, ay, az, tps)