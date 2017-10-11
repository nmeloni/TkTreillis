#########################################################
# geom.py                                
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
#  Module de gestion des objets geometrique Tkinter
#  pour le programme treillis.py
#
#########################################################

import tkinter as tk 
from math import cos, sin, pi, sqrt

# Constantes géométriques
RAYON_NOEUD = 15
ORIGINE = (0,600)

class Noeud:
    def __init__(self,canevas,info,x,y,num=None):
        """ 
        Crée un objet noeud centré en (x,y) avec self.obj
        comme référence (renvoyé par la méthode .create_oval() )
        """
        self.x, self.y = x, y
        self.X, self.Y = tk.StringVar(), tk.StringVar()
        self.treillis = canevas.master.treillis
        self.canevas = canevas
        self.info = info
        self.obj = self.dessiner()
        if num:
            self.num = Numero(self, num)
        else:
            self.num = Numero(self, self.treillis.NumeroNoeud())
        self.appui = None
        self.appuifixe = True
        self.lbar = []
        self.data_frame = None
        self.cree_info_frame()
        self.treillis.lnoeuds.append(self)
        self.treillis.lnum.append(self.num)
        
        
    def dessiner(self):
        x,y=self.x, self.y
        return self.treillis.canevas.DessineNoeud(x,y,RAYON_NOEUD,
                                                  fill="PaleGreen", 
                                                  outline="MediumSeaGreen",
                                                  activefill="SeaGreen")

    def deplacer(self,x,y):
        """ Déplace le noeud aux nouvelles coordonnées (x,y) """
        dx, dy = x-self.x, y-self.y
        #if self.appui != None:
        #    self.appui.move( dx, dy )
        self.canevas.move(self.obj, dx, dy)
        self.canevas.move(self.num.obj, dx,dy)
        if self.appui:
            self.appui.deplacer(dx,dy)
        self.x, self.y = x, y
        self.X.set(str(self.x))
        self.Y.set(str(ORIGINE[1]-self.y))
        for b in self.lbar:
            b.deplacer(self)
        self.affiche_info_frame()
            
    def effacer(self):
        self.canevas.delete(self.obj)
        self.canevas.delete(self.num.obj)
        
        self.treillis.lnoeuds.remove(self)
        self.treillis.lnum.remove(self.num)
        
        if self.appui != None:
            self.appui.effacer()
            self.appui = None
        
        for b in self.lbar[:]: 
            b.effacer()
        
        self.data_frame.pack_forget()
        self.data_frame.destroy()
            
    def cree_info_frame(self):
        
        frm = tk.Frame(self.info)
        self.data_frame = frm
        
        label = tk.Label(frm, text="Noeud " + str(self.num.val))
        label.pack(side = "top", padx=5, pady=5)
        
        frm2 = tk.Frame(frm)
        frm2.pack(side ="top")
        
        label2 = tk.Label(frm2, text="Coord. X =")
        label2.pack(side ="left")
        self.X.set(str(self.x))
        chmp1 = tk.Entry(frm2, textvariable= self.X, validate="focus", vcmd=self.validateX, width = 4)
        chmp1.pack(side ="left")
        
        label3 = tk.Label(frm2, text="Y =")
        label3.pack(side ="left")
        self.Y.set(str(ORIGINE[1]-self.y))
        chmp2 = tk.Entry(frm2, textvariable= self.Y, validate="focus", vcmd=self.validateY, width = 4)
        chmp2.pack(side ="left")

        self.affiche_info_frame()
        
        
    def affiche_info_frame(self):
        self.info.nettoyer()
        self.data_frame.pack(side = "top", padx=5, pady=5)
        for b in self.lbar:
            b.data_frame.pack(side = "top", padx=5, pady=5)
        if (self.appui != None) and (self.appuifixe == False):
            self.appui.data_frame.pack(side = "top", padx=5, pady=5)
    
    def validateX(self):
        value = self.X.get()
        try:
            if value:
                x = int(value)
                self.deplacer(x,self.y)
            return True
        except ValueError:
            return None

    def validateY(self):
        value = self.Y.get()
        try:
            if value:
                y = ORIGINE[1]-int(value)
                self.deplacer(self.x,y)
            return True
        except ValueError:
            return None
    
class Numero:
    def __init__(self, noeud, num):
        self.val = num
        self.noeud = noeud
        self.obj = self.dessiner()
        
        
    def dessiner(self):
        return self.noeud.treillis.canevas.DessineNum(self.noeud.x, self.noeud.y,
                                                      text=str(self.val),
                                                      fill="orange",
                                                      font="Latin 16 bold")

class AppuiFixe:
    def __init__(self, noeud):
        self.noeud = noeud
        self.treillis = noeud.treillis
        self.canevas = noeud.canevas
        self.obj = self.dessiner()
        self.noeud.appui = self
        self.noeud.appuifixe = True
    
    def dessiner(self):
        if self.noeud.appui:
            return 
        x, y = self.noeud.x, self.noeud.y + RAYON_NOEUD
        return self.treillis.canevas.DessineAppuiFixe(x,y,RAYON_NOEUD,
                                                      fill="OrangeRed",
                                                      outline="red",
                                                      activefill="orange")
        
    def effacer(self):
        self.canevas.delete(self.obj)
        self.noeud.appui = None
        
    def deplacer(self, dx, dy):
        self.canevas.move(self.obj, dx, dy)

    def cree_info_frame(self):
        return

    def affiche_info_frame(self):
        self.noeud.info.nettoyer()
    
class AppuiMobile:
    def __init__(self, noeud, angle="270"):
        self.noeud = noeud
        self.treillis = noeud.treillis
        self.canevas = noeud.canevas
        self.angleVar = tk.StringVar()
        self.angleVar.set(angle) 
        self.angle = ((360-int(angle))//45)*(pi/4)
        self.obj = self.dessiner()
        self.noeud.appui = self
        self.noeud.appuifixe = False
        self.cree_info_frame()
        
        
    def dessiner(self):
        if self.noeud.appui:
            return 
        x, y = self.noeud.x, self.noeud.y + RAYON_NOEUD
        return self.treillis.canevas.DessineAppuiMobile(x,y,RAYON_NOEUD,self.angle,
                                                        fill="OrangeRed",
                                                        outline="red",
                                                        activefill="orange")
        
        
    def effacer(self):
        for o in self.obj:
            self.canevas.delete(o)
        self.noeud.appui = None
        self.data_frame.pack_forget()
        self.data_frame.destroy()
        
    def deplacer(self, dx, dy):
        for o in self.obj:
            self.canevas.move(o, dx, dy)
    
    def tourner(self, alpha):
        new_angle = ((360-int(alpha))//45)*(pi/4)
        angle = new_angle - self.angle
        self.angle = new_angle
        self.treillis.canevas.TournerAppui(self.obj, self.noeud.x,self.noeud.y, angle)

    def cree_info_frame(self):
        frm = tk.Frame(self.noeud.info)
        self.data_frame = frm
        label = tk.Label(frm, text="Angle Appuie")
        label.pack(side = "top", padx=5, pady=5)
        chmp = tk.Scale(frm, from_= 0, to=360, resolution=45,orient=tk.HORIZONTAL, 
                        variable=self.angleVar, command=self.tourner)
        chmp.pack(side = "left")
        self.affiche_info_frame()
        
    def affiche_info_frame(self):
        self.noeud.info.nettoyer()
        self.data_frame.pack(side = "top", padx=5, pady=5)


class Barre:
    def __init__(self, noeud1, noeud2):
        self.noeud1 = noeud1
        self.noeud2 = noeud2
        self.treillis = noeud1.treillis
        self.canevas = self.noeud1.canevas
        self.info = self.noeud1.info
        self.length = tk.StringVar()
        self.rayon = tk.StringVar()
        self.young = tk.StringVar()
        self.coef = tk.StringVar()
        self.length.set(self.get_length())
        self.rayon.set(1)
        self.young.set(1)
        self.coef.set(self.get_coef())
        self.obj = self.dessiner()
        self.noeud1.lbar.append(self)
        self.noeud2.lbar.append(self)
        self.noeud1.treillis.lbar.append(self)
        self.cree_info_frame()
        
    def dessiner(self):
        barre = self.treillis.canevas.DessineBarre( self.noeud1.x, self.noeud1.y,
                                                    self.noeud2.x, self.noeud2.y,
                                                    fill = "PaleTurquoise",
                                                    activefill = "SteelBlue",
                                                    width = 5, smooth = 1)
        self.canevas.tag_lower( barre )
        return barre

    def effacer(self):
        self.noeud1.lbar.remove(self)
        self.noeud2.lbar.remove(self)
        self.noeud1.treillis.lbar.remove(self)
        self.canevas.delete(self.obj)
        self.data_frame.pack_forget()
        self.data_frame.destroy()
        
    def deplacer(self,noeud):
        coord = self.canevas.coords(self.obj)
        if noeud == self.noeud1:
            newcoord = [noeud.x, noeud.y]+coord[2:]
        else:
            newcoord = coord[:2]+[noeud.x, noeud.y]
        self.canevas.coords(self.obj, *newcoord)
        self.length.set( self.get_length() )
        self.coef.set( self.get_coef() )

        
    def get_length(self):
        return round(sqrt( (self.noeud1.x-self.noeud2.x)**2 + (self.noeud1.y-self.noeud2.y)**2),2)
            
    def get_coef(self):
        d = float(self.young.get())*pi*float(self.rayon.get())**2
        n =  float(self.length.get())
        return round(n/d,4)
        
    def cree_info_frame(self):
        frm = tk.Frame(self.info)
        self.data_frame = frm
        self.data_frame.pack(side = 'top', padx=5,pady=5)
        
        valider = frm.register(self.valider)
        
        noeuds = [self.noeud1.num.val, self.noeud2.num.val]
        noeuds.sort()
        
        numbar = str(noeuds[0])+"_"+str(noeuds[1])
        lbl=tk.Label(frm, justify='left', text="Barre "+numbar)
        lbl.pack(side="top", padx=5, pady=5)
        
        frm1 = tk.Frame(frm)
        tk.Label(frm1, text = "L"+numbar+"=").pack(side="left", padx=5, pady=5)
        tk.Entry(frm1, textvariable= self.length, state=tk.DISABLED, width = 6).pack(side='left')
        tk.Label(frm1, text = "cm").pack(side="left")
        tk.Label(frm1, text = "C"+numbar+"=").pack(side="left", padx=5, pady=5)
        tk.Entry(frm1, textvariable= self.coef, state=tk.DISABLED, width = 9).pack(side='left')
        frm1.pack(side='top')
        
        frm2 = tk.Frame(frm)
        tk.Label(frm2, text = "R"+numbar+"=").pack(side="left", padx=5, pady=5)
        tk.Entry(frm2, textvariable=self.rayon, 
                 validate="all", 
                 vcmd=(valider,'%P'), width = 6).pack(side = 'left')
        tk.Label(frm2, text = "cm").pack(side="left")
        tk.Label(frm2, text = "E"+numbar+"=").pack(side="left", padx=5, pady=5)
        tk.Entry(frm2, textvariable=self.young, 
                 validate="all", 
                 vcmd=(valider,'%P'), width = 6).pack(side = 'left')
        tk.Label(frm2, text = "MPa").pack(side="left")
        frm2.pack(side='top')
        
        self.data_frame = frm
        self.affiche_info_frame()
        

    def affiche_info_frame(self):
        self.info.nettoyer()
        self.length.set(self.get_length())
        self.coef.set(self.get_coef())
        self.data_frame.pack(side = 'top', padx=5,pady=5)
        
    def valider(self, v):
        v1 = self.rayon.get()
        v2 = self.young.get() 
        try:
            float(v)
            if v1 and v2:
                R = float(v1)
                E = float(v2)
                self.coef.set( self.get_coef() )
            return True
        except:
            return False

    
