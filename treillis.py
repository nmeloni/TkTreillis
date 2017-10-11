#!/usr/bin/python3

#########################################################
# treillis.py                                
# -----------                             
#                                            
# Nicolas Méloni - meloni@univ-tln.fr        
# 
#
# Version : 1.0
# MàJ     : 29 / 01 / 2016                             
#########################################################

#########################################################
#
#  Portage sous python3/tkinter du logiciel 
#  manipulation de treillis de Christian NGUYEN 
#  (http://www.univ-tln.fr/~nguyen)
#
#########################################################

#########################################################
#
# Copyright Nicolas Méloni, 2016
#
# This program is free software: you can redistribute it 
# and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, 
# either version 3 of the License, or (at your option) any
# later version.  
# 
# This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
# 
# You should have received a copy of the GNU General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
# 
#########################################################

#########################################################
#  Le canevas générale de l'application:
#
#       -------------------------------------------------
#       | Fichier |                                     |
#       -------------------------------------------------
#       |         |                          |          |
#       |         |                          | Bouttons |
#       |         |                          |          |
#       |  Info   |                          |  noeud   |
#       |         |       Dessin du          |          |
#       | objets  |                          |  barre   |
#       |         |                          |          |
#       |         |       Treillis           |    .     |
#       |         |                          |    .     |
#       |         |                          |    .     |
#       |         |                          |          |
#       |         |                          | résoudre |
#       -------------------------------------------------
#
#  Les frames d'info (Infobar), dessin (Canevas) et boutton 
#  (Toolbar) sont des classes contenu dans une classe plus 
#  générale: la classe Treilllis.
#
#
#
############################################################

 
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from math import cos, sin, pi, sqrt

import pickle

from matrix import MatrixInverse
from geom import *


# Les constantes globales du systèmes:
#
# Liste des différents états du 
CLIC_STATE_SELECT         = 0
CLIC_STATE_NOEUD          = 1
CLIC_STATE_EFFACER        = 2
CLIC_STATE_APPUI_FIXE     = 3
CLIC_STATE_APPUI_MOBILE   = 4
CLIC_STATE_BARRE          = 5
CLIC_STATE_BARRE_2        = 6

STR_STATE = ["Sélection","Noeud","Effacer",
             "Appui fixe","Appui mobile","Barre", "Barre"]

class Toolbar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.treillis = parent
        self.mode_str = tk.StringVar()
        
        # Les Labels du mode de clic
        self.llabels = [tk.Label(self, text="Mode",height=3),
                        tk.Label(self, textvariable=self.mode_str,
                             relief = tk.SUNKEN,width=10,height=3) ]
        
        # Les différents boutons de la barre d'outils
        self.lbuttons = [ tk.Button(self, text="Sélection",  
                             command=self.ButtonSelect,
                             width=10, height=3),
                          tk.Button(self, text="Noeud", 
                            command=self.ButtonNoeud,
                            width=10,height=3),
                          tk.Button(self, text="Barre", 
                             command=self.ButtonBarre,
                             width=10, height=3),
                          tk.Button(self, text="Appui mobile", 
                            command=self.ButtonAppuiM,
                            width=10,height=3),
                          tk.Button(self, text="Appui fixe", 
                             command=self.ButtonAppuiF,
                             width=10, height=3),
                          tk.Button(self, text="Effacer", 
                            command=self.ButtonEffacer,
                            width=10,height=3),
                          tk.Button(self, text="Résoudre", 
                            command=self.ButtonSolve,
                            width=10,height=3) ]
        
        self.PackButton()
        self.PackLabel()
        
    def PackButton(self):
        for button in self.lbuttons[::-1]:
            button.pack(side = "bottom", padx=5, pady=5)
        
    def PackLabel(self):
        for label in self.llabels:
            label.pack(side = "left", padx=5,pady=5)

    def ButtonClic(self, state):
        self.treillis.clic_state = state
        self.mode_str.set(STR_STATE[state])
        
    def ButtonSelect(self):
        self.ButtonClic(CLIC_STATE_SELECT)
        
    def ButtonNoeud(self):
        self.ButtonClic(CLIC_STATE_NOEUD)

    def ButtonBarre(self):
        self.ButtonClic(CLIC_STATE_BARRE)

    def ButtonAppuiM(self):
        self.ButtonClic(CLIC_STATE_APPUI_MOBILE)

    def ButtonAppuiF(self):
        self.ButtonClic(CLIC_STATE_APPUI_FIXE)

    def ButtonEffacer(self):
        self.ButtonClic(CLIC_STATE_EFFACER)

    def ButtonSolve(self):
        self.treillis.Resoudre()
        


class Infobar(tk.Frame): 
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.treillis = parent
        self.titre = tk.Label(self, text="Données",width=35)
        self.titre.pack(side = "top",  padx=5, pady=5)
        
    def nettoyer(self):
        for w in self.winfo_children():
            if w!= self.titre:
                w.pack_forget()
                
        
       
class Canevas(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.treillis = parent
        self.noeud1 = None
        self.noeud2 = None
        self.canevas = tk.Canvas(self, 
                                 width=self.treillis.canevas_x,
                                 height=self.treillis.canevas_y,
                                 bg='white')
        self.canevas.pack(fill="both",expand=True)
        
        self.canevas.bind("<Configure>", self.ChangeTaille)
        self.canevas.bind("<Button-1>",  self.Clic_1)
        self.canevas.bind("<B1-Motion>", self.Drag)

        self.current = None
        self.grille = []
        
    def ChangeTaille(self, event):
        self.treillis.canevas_x = event.width
        self.treillis.canevas_y = event.height
        if self.treillis.grille.get():
            self.treillis.grille.set(False)
            self.DessineGrille()
            self.treillis.grille.set(True)
            self.DessineGrille()

    def Clic_1(self,event):
        x,y = event.x, event.y
        self.current = self.ObjetClic(x,y)
        estNoeud = self.current in self.treillis.lnoeuds

        if self.current != None:
            self.current.affiche_info_frame()
        
        if self.treillis.grille.get():
            x = (x//self.treillis.grille_unit)*self.treillis.grille_unit
            y = (y//self.treillis.grille_unit)*self.treillis.grille_unit
            
        if (self.current == None) and (self.treillis.clic_state == CLIC_STATE_NOEUD):
            self.AjouteNoeud(x,y)
        elif (self.current != None) and (self.treillis.clic_state == CLIC_STATE_EFFACER):
            self.current.effacer()
        elif (self.current != None) and estNoeud:
            if not self.current.appui and (self.treillis.clic_state == CLIC_STATE_APPUI_FIXE):
                self.AjouteAppuiFixe(self.current)
            elif not self.current.appui and (self.treillis.clic_state == CLIC_STATE_APPUI_MOBILE):
                self.AjouteAppuiMobile(self.current)
            elif self.treillis.clic_state == CLIC_STATE_BARRE:
                self.noeud1 = self.current
                self.noeud2 = None
                self.treillis.toolbar.ButtonClic(CLIC_STATE_BARRE_2)
            elif self.treillis.clic_state == CLIC_STATE_BARRE_2:
               
                self.noeud2 = self.current
                if self.noeud1 == self.noeud2:
                    return
                for b in self.noeud1.lbar:
                    if b.noeud1 == self.noeud2 or b.noeud2 == self.noeud2:
                        return
                self.AjouteBarre(self.noeud1, self.noeud2)
                self.treillis.toolbar.ButtonClic(CLIC_STATE_BARRE)
                        
        

    def Drag(self, event):
        if (not self.current) or (self.treillis.clic_state != CLIC_STATE_SELECT):
            return
        if self.current in self.treillis.lnoeuds:
            if self.treillis.grille.get():
                unit = self.treillis.grille_unit
                self.current.deplacer((event.x//unit)*unit,
                                       (event.y//unit)*unit)
            else:
                self.current.deplacer(event.x,event.y)
            
            
    def ObjetClic(self,x,y):
        lobj = self.canevas.find_overlapping(x-2,y-2,x+2,y+2)
        if len(lobj) == 0:
            return None
        obj = lobj[-1]
        for num in self.treillis.lnum:
            if num.obj == obj:
                return num.noeud
        for n in self.treillis.lnoeuds:
            if n.obj == obj:
                return n
            if n.appui != None:
                if n.appuifixe == True:
                    if n.appui.obj == obj:
                        return n.appui
                else:
                    if obj in n.appui.obj:
                        return n.appui
            for b in n.lbar:
                if b.obj == obj:
                    return b

    def DessineNoeud(self,x,y,r, **kwargs):
        n = self.canevas.create_oval(x-r, y+r, x+r, y-r, **kwargs)
        self.AbaisseGrille()
        return n
        
    def DessineNum(self,x,y,**kwargs):
        n = self.canevas.create_text(x,y,**kwargs)
        self.AbaisseGrille()
        return n
        
    def DessineBarre(self,x1,y1,x2,y2,**kwargs):
        b = self.canevas.create_line(x1,y1,x2,y2,**kwargs)
        self.AbaisseGrille()
        return b
        
    def DessineAppuiFixe(self,x,y,r,**kwargs):
        rcos_a, rsin_a = r*cos(-pi/3), r*sin(-pi/3)
        points = [x, y, x + rcos_a, y - rsin_a, x - rcos_a, y - rsin_a]
        a = self.canevas.create_polygon(points,**kwargs)
        self.AbaisseGrille()
        return a
        
    def DessineAppuiMobile(self,x,y,r=RAYON_NOEUD,angle=pi/2,**kwargs):
        rcos_a, rsin_a = r*cos(-pi/3), r*sin(-pi/3)
        points = [x, y, x + rcos_a, y - rsin_a, x - rcos_a, y - rsin_a]
        triangle = self.canevas.create_polygon(points,**kwargs)
        rond1 = self.canevas.create_oval(points[2], points[3],
                                         points[2]-6, points[3]+6,
                                         **kwargs)
        rond2 = self.canevas.create_oval(points[4], points[5],
                                         points[4], points[5]+6,
                                         **kwargs)
        appui = [triangle, rond1, rond2]
        if angle != pi/2:
            alpha = angle-pi/2
            self.TournerAppui(appui,x,y-r,alpha)
        self.AbaisseGrille()
        return appui
    
    def TournerAppui(self,appui,x,y, angle):
        coord = self.canevas.coords(appui[0])
        x0,y0 = x,y
        cos_a, sin_a = cos(angle), sin(-angle)
        points = [ (coord[0]-x0)*cos_a + (coord[1]-y0)*sin_a+x0,
                   -(coord[0]-x0)*sin_a + (coord[1]-y0)*cos_a+y0,
                   (coord[2]-x0)*cos_a + (coord[3]-y0)*sin_a+x0,
                   -(coord[2]-x0)*sin_a + (coord[3]-y0)*cos_a+y0,
                   (coord[4]-x0)*cos_a + (coord[5]-y0)*sin_a+x0,
                   -(coord[4]-x0)*sin_a + (coord[5]-y0)*cos_a+y0]
        self.canevas.coords(appui[0], *points)
        coord = self.canevas.coords(appui[1])
        points = [ (coord[0]-x0+3)*cos_a + (coord[1]-y0+3)*sin_a+x0-3,
                   -(coord[0]-x0+3)*sin_a + (coord[1]-y0+3)*cos_a+y0-3,
                   (coord[0]-x0+3)*cos_a + (coord[1]-y0+3)*sin_a+x0+3,
                   -(coord[0]-x0+3)*sin_a + (coord[1]-y0+3)*cos_a+y0+3]
        self.canevas.coords(appui[1], *points)
        coord = self.canevas.coords(appui[2])
        points = [ (coord[0]-x0+3)*cos_a + (coord[1]-y0+3)*sin_a+x0-3,
                   -(coord[0]-x0+3)*sin_a + (coord[1]-y0+3)*cos_a+y0-3,
                   (coord[0]-x0+3)*cos_a + (coord[1]-y0+3)*sin_a+x0+3,
                   -(coord[0]-x0+3)*sin_a + (coord[1]-y0+3)*cos_a+y0+3]
        self.canevas.coords(appui[2], *points)
        
    
    def DessineGrille(self):
        if not self.treillis.grille.get():
            for l in self.grille[:]:
                self.canevas.delete(l)
                self.grille.remove(l)
        else:
            unit = self.treillis.grille_unit
            tx = self.treillis.canevas_x
            ty = self.treillis.canevas_y
            for i in range(1,tx//unit+1):
                lx=self.canevas.create_line(unit*i,0,unit*i,ty,fill = "light grey")
                self.grille.append(lx)
            for i in range(1,ty//unit+1):
                ly=self.canevas.create_line(0,unit*i,tx,unit*i,fill = "light grey")
                self.grille.append(ly)
        self.AbaisseGrille()
        
    def AbaisseGrille(self):
        for l in self.grille:
            self.canevas.tag_lower(l)
       
    def AjouteNoeud(self,x,y,num=None):
        return Noeud(self.canevas,self.treillis.infobar, x,y,num)

    def AjouteAppuiFixe(self, noeud):
        return AppuiFixe(noeud)
        
    def AjouteAppuiMobile(self, noeud, angle="270"):
        return AppuiMobile(noeud, angle)

    def AjouteBarre(self, noeud1, noeud2):
        return Barre(noeud1, noeud2)
        
class Treillis(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.app = parent
        
        # Les paramètres du treillis
        self.clic_state = CLIC_STATE_SELECT
        self.nbnoeuds = 0
        self.lnoeuds = []
        self.lnum = []
        self.lbar = []
        self.copie = []
        self.grille_unit = 20
        self.grille = tk.BooleanVar()
        self.grille.set(False)
       
        self.canevas_x = 600
        self.canevas_y = 600
        self.sol = {}
        self.top = None
        
        # Les différents éléments de la frame Treillis
        self.infobar = Infobar(self, width=250, height=600)
        self.toolbar = Toolbar(self, width=100)
        self.canevas = Canevas(self,
                               width=self.canevas_x,
                               height=self.canevas_y,
                               bg='light grey')
                
        self.infobar.pack(side="left",  padx=5, pady=5)
        self.toolbar.pack(side="right", padx=5, pady=5)
        self.canevas.pack(side="right", padx=5, pady=5, fill="both",expand=True)

        
        
    def NumeroNoeud(self):
        self.nbnoeuds += 1
        return self.nbnoeuds
     
    def ListeInconnues(self):
        lnoeuds_actifs = [ n for n in self.lnoeuds if (not n.appuifixe or n.appui == None)]
        linconnues=[]
        for n in lnoeuds_actifs:
            if n.appui != None:
                a = n.appui.angleVar.get()
                if a == "270" or a == "90":
                    linconnues.append("X"+str(n.num.val))
                else:
                    linconnues.append("Y"+str(n.num.val))
            else:
                linconnues.append("X"+str(n.num.val))
                linconnues.append("Y"+str(n.num.val))
        lbar = []
        for b in self.lbar:
            noeuds=[b.noeud1.num.val, b.noeud2.num.val]
            noeuds.sort()
            lbar.append("T"+str(noeuds[0])+str(noeuds[1]))
        lbar.sort()
        return linconnues+lbar
        
    def CreerMatrice(self):
        if not self.lnoeuds:
            return
            
        if self.top:
            self.FermetureMatrice()
        
        top = tk.Toplevel()
        top.title("Matrice du sytème")
                
        linco= self.ListeInconnues()
        self.linco = linco
        mat_len  = len(linco)

        for i in range(mat_len):
            tk.Label(top,text=linco[i],width=8, relief=tk.SUNKEN).grid(row=0,column=i,sticky=tk.W)
        
        tk.Label(top, text="S", width = 8, relief=tk.SUNKEN).grid(row=0, column=mat_len+1,sticky=tk.W)
        tk.Label(top, text="", width = 8).grid(row=0, column=mat_len+2,sticky=tk.W)
        tk.Label(top, text="V", width = 8, relief=tk.SUNKEN).grid(row=0, column=mat_len+3,sticky=tk.W)

        self.M = [ [ tk.StringVar() for i in linco] for j in linco]
        self.V = [ tk.StringVar() for i in linco]
        self.S = [ tk.StringVar() for i in linco]

        for i in range(mat_len):
            for r in range(mat_len):
                self.M[r][i].set(0.0)
                if r < len(self.lbar):
                    color = "LightCyan"
                else:
                    color = "LightGreen"
                entry=tk.Entry(top, textvariable=self.M[r][i], 
                               bg=color, width = 8)
                entry.grid(row=r+1, column=i,sticky=tk.W)
        for i in range(mat_len):    
            self.V[i].set(0.0)
            entry=tk.Entry(top, textvariable=self.V[i], width = 8)
            entry.grid(row=i+1, column=mat_len+3,sticky=tk.W)
            
            label = tk.Label(top, text=linco[i].lower(),width = 8,
                             padx=2, relief=tk.SUNKEN )
            label.grid(row=i+1, column=mat_len+1,sticky=tk.W)
            
        tk.Label(top, text="=").grid(row=mat_len//2, column=mat_len+2)
        tk.Label(top, text="x").grid(row=mat_len//2, column=mat_len)
        button = tk.Button(top, text="Résoudre", command=self.solve)
        button.grid(row=mat_len+1, columnspan=mat_len+1, sticky=tk.W)
        
    
    def Resoudre(self):
        self.CreerMatrice()

    def FermetureMatrice(self):
        for obj in self.copie:
            self.canevas.canevas.delete(obj)
        self.top.destroy()
        self.top = None
        
    def solve(self):
        if self.top:
            self.FermetureMatrice()
        for r in range(len(self.M)):
            for i in range(len(self.M)):
                try:
                    value = float(eval(self.M[r][i].get()))
                    self.M[r][i].set(round(value,4))
                except :
                    messagebox.showwarning("Erreur","Valeur incorrecte à \nla case ("\
                                           +str(r+1)+','+str(i+1)+') de la matrice')
                    return
                
        for r in range(len(self.M)):
            try:
                value = float(eval(self.V[r].get()))
                self.V[r].set(round(value,4))
            except :
                messagebox.showwarning("Erreur","Valeur incorrecte à \nla case "\
                                           +str(r+1)+' du vecteur')
                return
        mat = [ [float(e.get()) for e in r ] for r in self.M ]
        vec = [float(e.get()) for e in self.V ]
        inv = MatrixInverse(mat)
        if inv == None:
            messagebox.showwarning("Erreur","Matrice non inversible")
            return
        sol = [ round(sum( vec[i]*inv[r][i] for i in range(len(self.V)) ),2) for r in range(len(inv))]
        
        self.sol = {}
        noeuds_deplaces = [ n for n in self.lnoeuds if (not n.appuifixe or n.appui == None)]
        sol_index = 0
        for n in self.lnoeuds:
            if n in noeuds_deplaces:
                if n.appui != None:
                    if n.appui.angleVar.get() in ["270","90"]:
                        self.sol[n.num.val]=[sol[sol_index],0]
                    elif n.appui.angleVar.get() in ["225","45"]:
                        self.sol[n.num.val]=[-sol[sol_index],-sol[sol_index]]
                    elif n.appui.angleVar.get() in ["315","135"]:
                        self.sol[n.num.val]=[sol[sol_index],-sol[sol_index]]
                    else:
                        self.sol[n.num.val]=[0,-sol[sol_index]]
                    sol_index += 1
                else:
                    self.sol[n.num.val]=[sol[sol_index], -sol[sol_index+1]]
                    sol_index += 2
            else:
                self.sol[n.num.val]=[0,0]
                
        top = tk.Toplevel(self)
        self.top = top
        top.protocol("WM_DELETE_WINDOW", self.FermetureMatrice)
        top.grab_set()
        
        linco= self.linco
        mat_len  = len(linco)
        
        for i in range(mat_len):
            label = tk.Label(top, text=linco[i].lower(), width = 8,
                             padx=2, relief=tk.SUNKEN)    
            label.grid(row=i, column=0,sticky=tk.W)
            label = tk.Label(top, text=str(round(sol[i])), width = 8,
                             padx=2, relief=tk.SUNKEN)    
            label.grid(row=i, column=2,sticky=tk.W)
        
        tk.Label(top, text="=").grid(row=mat_len//2, column=1)
        self.CopieTreillis()
        
        
    def CopieTreillis(self):
        
        self.copie = []
        for b in self.lbar:
            x1 = b.noeud1.x + self.sol[b.noeud1.num.val][0]
            y1 = b.noeud1.y + self.sol[b.noeud1.num.val][1]
            x2 = b.noeud2.x + self.sol[b.noeud2.num.val][0]
            y2 = b.noeud2.y + self.sol[b.noeud2.num.val][1]
            
            obj = self.canevas.DessineBarre(x1,y1,x2,y2,
                                            fill="Orange",
                                            width = 5, smooth = 1)
            #self.canevas.tag_raise( obj )
            self.copie.append(obj)
        for n in self.lnoeuds:
            x = n.x + self.sol[n.num.val][0]
            y = n.y + self.sol[n.num.val][1]
            obj = self.canevas.DessineNoeud(x,y,RAYON_NOEUD,
                                            fill="Orange", 
                                            outline="Red")
            #self.canevas.tag_raise( obj )
            self.copie.append(obj)
            obj = self.canevas.DessineNum(x,y,text=str(n.num.val),
                                          fill="Red",
                                          font="Latin 16 bold")
            self.copie.append(obj)
       
    
            
class Menubar(tk.Menu):
    def __init__(self, parent, *args, **kwargs):
        tk.Menu.__init__(self, parent.root, *args, **kwargs)
        self.app = parent
        self.treillis = parent.treillis
        self.canevas = parent.treillis.canevas
        self.info = self.treillis.infobar
        
        self.menufichier = tk.Menu(self, tearoff=0)
        self.menufichier.add_command(label="Nouveau", 
                                     command=self.Nouveau)
        self.menufichier.add_command(label="Enregistrer", 
                                     command=self.Enregistrer)
        self.menufichier.add_command(label="Ouvrir", 
                                     command=self.Ouvrir)
        self.menufichier.add_separator()
        self.menufichier.add_command(label="Quitter", 
                                     command=self.Quitter)
        self.add_cascade(label="Fichier", menu=self.menufichier)

        self.menuoutils = tk.Menu(self, tearoff=0)
        self.menuoutils.add_checkbutton(label="grille",
                                      onvalue=True,
                                      offvalue=False,
                                      variable=self.treillis.grille,
                                      command=self.canevas.DessineGrille)
        self.add_cascade(label="Outils", menu=self.menuoutils)

        self.menuaide = tk.Menu(self, tearoff=0)
        self.menuaide.add_command(label="À propos", 
                                     command=self.APropos)
        self.add_cascade(label="Aide", menu=self.menuaide)
        
    def Nouveau(self):
        for w in self.info.winfo_children():
            if w!=self.info.titre:
                w.pack_forget()
                w.destroy()
        
        lnoeud =[ n for n in self.treillis.lnoeuds]
        for n in lnoeud:
            n.effacer()
        self.treillis.nbnoeuds = 0

    def Enregistrer(self):
        f = filedialog.asksaveasfile(mode='wb')
        if f == None:
            return
        lnoeuds = []
        for n in self.treillis.lnoeuds:
            x, y, num = n.x, n.y, n.num.val
            appui = False
            fixe = n.appuifixe
            angle = None
            if n.appui:
                appui = True
                if not fixe:
                    angle = n.appui.angleVar.get()
            lnoeuds.append((x,y,num,appui,fixe,angle))
        pickle.dump(lnoeuds, f)
        
        lbar =[]
        for b in self.treillis.lbar:
            numnoeuds =(b.noeud1.num.val,b.noeud2.num.val)
            r = b.rayon.get()
            y = b.young.get()
            lbar.append(numnoeuds+(r,y))
        pickle.dump(lbar, f)
        
        f.close()

    def Ouvrir(self):
        f = filedialog.askopenfile(mode='rb')
        if f == None:
            return
        self.Nouveau()
        lnoeuds = pickle.load(f)
        lbar = pickle.load(f)

        for n in lnoeuds:
            noeud=self.canevas.AjouteNoeud(n[0],n[1],n[2])
            if n[3]:
                if n[4]:
                    self.canevas.AjouteAppuiFixe(noeud)
                else:
                    self.canevas.AjouteAppuiMobile(noeud,n[5])
        for b in lbar:
            noeuds = []
            for n in self.treillis.lnoeuds:
                if b[0]==n.num.val or b[1]==n.num.val:
                    noeuds.append(n)
            barre = self.canevas.AjouteBarre(noeuds[0],noeuds[1])
            barre.rayon.set(b[2])
            barre.young.set(b[3])
            
        self.treillis.nbnoeuds = max([n.num.val for n in self.treillis.lnoeuds])
        f.close()

    def Quitter(self):
        self.app.root.destroy()

    def APropos(self):
        messagebox.showinfo("À propos de TkTreillis", 
                            "TkTreillis\n"\
                            "version: 1.0\n\n"\
                            "Programme pédagogique de manipulation de treillis"\
                            "prévu pour le cours de mécanique statique.\n\n"\
                            "Version disponible à l'adresse\n"\
                            "http://meloni.univ-tln.fr"    )

            
class MainApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.root.title("TkTreillis")
        
        self.treillis = Treillis(self)
        self.treillis.pack(side="right", fill="both", expand=True)
        
        self.menubar = Menubar(self)
        self.root.config(menu = self.menubar)
        
        

    def mainloop(self):
        self.root.mainloop()

if __name__=='__main__':
    App = MainApp(tk.Tk())
    App.pack(side="top", fill="both", expand=True)
    App.mainloop()
