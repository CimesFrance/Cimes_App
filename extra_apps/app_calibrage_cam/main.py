import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter import PhotoImage
import numpy as np
from extra_apps.app_calibrage_cam.utils.import_manager import importer_image_tk
from extra_apps.app_calibrage_cam.utils.point_manager import bool_pt_appuye

import json

class JSONVar(tk.StringVar):
  """A Tk variable that can hold dicts and lists"""

  def __init__(self, *args, **kwargs):
    kwargs['value'] = json.dumps(kwargs.get('value'))
    super().__init__(*args, **kwargs)

  def set(self, value, *args, **kwargs):
    string = json.dumps(value)
    super().set(string, *args, **kwargs)

  def get(self, *args, **kwargs):
    """Get the list or dict value"""
    string = super().get(*args, **kwargs)
    return json.loads(string)


class image_frame(tk.Frame):
   def __init__(self,parent,app,fi,*args,**kwargs):
      super().__init__(parent,*args,**kwargs)
      self.app = app
      self.fi = fi
      self.tk_charger_logo = importer_image_tk("logodownload.png")
      self._image_frame_GUI()
   
   def _image_frame_GUI(self):
      title = tk.Label(self,text="Image",font=("Arial", 14, "bold"))
      separator = tk.Frame(self, bg="black", height=2)
      label_btn_import_img = tk.Label(self,text='Importer image')
      btn_import_img = ttk.Button(self,image=self.tk_charger_logo,command=lambda : self._import_tk_img())

      title.grid(row=0,column=0,columnspan=2,sticky='we',padx=(2,2),pady=(2,2))
      separator.grid(row=1,column=0,columnspan=2,sticky='we',padx=(2,2),pady=(2,2))
      label_btn_import_img.grid(row=2,column=0,sticky='w',padx=(2,2),pady=(2,2))
      btn_import_img.grid(row=2,column=1,sticky='e',padx=(2,2),pady=(2,2))

      for i in range(2):
         self.columnconfigure(i,weight=1)
   
   def _import_tk_img(self):
      path = filedialog.askopenfilename(title='veilleur selectionner une image',filetypes=[("Image PNG", "*.png")])
      if not path:
         print("Erreur : Aucune fichier n'a été selectionné")
      else :
         self.app.img.reboot()
         self.app.zoom_factor.set(1)
         self.app.img.img_path.set(path)
         self.maj_affichage_aprs_import()
   
   def maj_affichage_aprs_import(self):
      self.app.flag_mesures_supp_affiche.set(True)
      self.app.flage_changer_echelle_affiche.set(True)
      self.app.flag_echelle_frame.set(True)
      self.app.flag_save_btn_affiche.set(True)


       
class Echelle_frame(tk.Frame):
   def __init__(self,parent,app,*args,**kwargs):
      super().__init__(parent,*args,**kwargs)
      self.app = app
      
      self.app.mesure_echelle.mesure_frame = tk.Frame(self)
      self.app.mesure_echelle.created = True
      self.changer_echelle =  changer_echelle(self,self.app)

      self.app.flag_echelle_frame.trace_add("write",self.display_state)
      self._Echelle_frame_GUI()

   def _Echelle_frame_GUI(self):
      title = tk.Label(self,text="Echelle",font=("Arial", 14, "bold"))
      separator = tk.Frame(self, bg="black", height=2)
      self.app.mesure_echelle.mesure_GUI()
      self.changer_echelle.changer_echelle_GUI()

      title.grid(row=0,column=0,sticky="we",padx=(2,2),pady=(2,2))
      separator.grid(row=1,column=0,sticky='nsew',padx=(2,2),pady=(2,2))
      self.app.mesure_echelle.mesure_frame.grid(row=2,column=0,sticky="nsew",padx=(2,2),pady=(2,2))
      self.changer_echelle.changer_echelle_frame.grid(row=3,column=0,sticky="nsew",padx=(2,2),pady=(2,2))

      self.columnconfigure(0,weight=1)

      return None
   def display_state(self,*args):
      self.app.mesure_echelle.flag_affiche_frame.set(self.app.flag_echelle_frame.get())
      self.changer_echelle.flag_affiche.set(self.app.flag_echelle_frame.get())


class changer_echelle:
   def __init__(self,parent_frame,app):
         self.app = app
         self.changer_echelle_frame = tk.Frame(parent_frame)
         self.flag_affiche = tk.BooleanVar(value=False)
         self.flag_affiche.trace_add("write",self.display_state)
         self.changer_echelle_GUI()

   def changer_echelle_GUI(self):
         self.label_mesure_reelle = tk.Label(self.changer_echelle_frame,text="Mesure Réelle",state='disabled')
         self.mesure_reelle_entry = tk.Entry(self.changer_echelle_frame,textvariable=self.app.distance_saisie,state='disabled')
         self.valider_btn = ttk.Button(self.changer_echelle_frame,text="Valider",state='disabled',command=self.changer_echelle)

         self.label_mesure_reelle.grid(row=0,column=0,sticky='w',padx=(2,2),pady=(2,2))
         self.mesure_reelle_entry.grid(row=0,column=1,sticky='w',padx=(2,2),pady=(2,2))
         self.valider_btn.grid(row=1,column=0,columnspan=2,sticky='we',padx=(2,2),pady=(2,2))

         self.changer_echelle_frame.columnconfigure(0,weight=1)
         self.changer_echelle_frame.columnconfigure(1,weight=1)
   
   def display_state(self,*args):
      etat = {"True" : "normal" , "False" : "disabled"}
      self.label_mesure_reelle.config(state=etat[str(self.flag_affiche.get())])
      self.mesure_reelle_entry.config(state=etat[str(self.flag_affiche.get())])
      self.valider_btn.config(state=etat[str(self.flag_affiche.get())])
   
   def changer_echelle(self):
      dist_entree = float(self.app.distance_saisie.get())
      if self.app.mesure_echelle.pts["pt1"].created == True and self.app.mesure_echelle.pts["pt2"].created == True:
         distance_pixel = self.app.mesure_echelle.calcul_distance() / self.app.facteur_conversion.get()
         self.app.facteur_conversion.set(dist_entree / distance_pixel)
         for mesure in self.app.list_mesures:
            if mesure.pts["pt1"].created and mesure.pts["pt2"].created:
               mesure.longueur.set(str(mesure.calcul_distance()))





class mesures_supp():
   def __init__(self,app):
      self.app = app
      self.mesures_supp_frame = None

      self.mes_mesures_supp = {
         "Mesure_supp_1" : une_mesure("Mesure N°1",'green',1,self.app),
         "Mesure_supp_2" : une_mesure("Mesure N°2",'blue',2,self.app),
         "Mesure_supp_3" : une_mesure("Mesure N°3",'yellow',3,self.app)
      }

      self.app.flag_mesures_supp_affiche.trace_add("write",self.display_state)
      # self.app.add_pt_flag.trac_add("write",self.add_pt_mesure)

      
      
   def mesures_supp_GUI(self):
      if self.mesures_supp_frame != None:
         title = tk.Label(self.mesures_supp_frame,text="Mesures",font=("Arial", 14, "bold"))
         separator = tk.Frame(self.mesures_supp_frame, bg="black", height=2)
         self.btn_ajouter = ttk.Button(self.mesures_supp_frame,text='Ajouter',state='disabled',command=self._ajouter_mesure)
         self.btn_supprimer = ttk.Button(self.mesures_supp_frame,text='Supprimer',state='disabled',command=self._supprimer_mesure)
         for cle in self.mes_mesures_supp.keys():
            self.mes_mesures_supp[cle].mesure_GUI()

         title.grid(row=0,column=0,columnspan=2,sticky="we",padx=(2,2),pady=(2,2))
         separator.grid(row=1,column=0,columnspan=2,sticky="we",padx=(2,2),pady=(2,2))
         self.btn_ajouter.grid(row=2,column=0,sticky="we",padx=(2,2),pady=(2,2))
         self.btn_supprimer.grid(row=2,column=1,sticky="we",padx=(2,2),pady=(2,2))
         i=3
         for cle in self.mes_mesures_supp.keys():
            self.mes_mesures_supp[cle].mesure_frame.grid(row=i,column=0,columnspan=2,sticky="nsew",padx=(2,2),pady=(2,2))
            i += 1

         self.mesures_supp_frame.columnconfigure(0,weight=1)
         self.mesures_supp_frame.columnconfigure(1,weight=1)
      else:
         print("self.mesures_supp_frame == None")
   
   def display_state(self,*args):
      etat = {"True" : "normal" , "False" : "disabled"}
      self.btn_ajouter.config(state=etat[str(self.app.flag_mesures_supp_affiche.get())])
      self.btn_supprimer.config(state=etat[str(self.app.flag_mesures_supp_affiche.get())])
      # for cle in self.mes_mesures_supp.keys():
      #    self.mes_mesures_supp[cle].flag_affiche.set(self.app.flag_mesures_supp_affiche.get())

   def _ajouter_mesure(self):
      num_mesure = self.app.choix_mesure.get()
      key_dict = "Mesure_supp_"+str(num_mesure) #On construit la clé de la mesure correspondante à la selection
      if num_mesure > 0 :
         self.mes_mesures_supp[key_dict].flag_affiche_frame.set(1)
         self.mes_mesures_supp[key_dict].created = True
   
   def _supprimer_mesure(self):
      num_mesure = self.app.choix_mesure.get()
      key_dict = "Mesure_supp_"+str(num_mesure) #On construit la clé de la mesure correspondante à la selection
      if num_mesure > 0 :
         self.mes_mesures_supp[key_dict].flag_affiche_frame.set(0)
         self.mes_mesures_supp[key_dict].created = False
         self.mes_mesures_supp[key_dict].supprimer_pts()
         self.mes_mesures_supp[key_dict].longueur.set("0.00")
         self.app.modif_canvas.set(True)


class une_mesure():
   def __init__(self,title,color,num,app):
      self.title = title
      self.color = color
      self.flag_affiche_ptLigne = tk.BooleanVar(value=True)
      self.flag_affiche_frame = tk.BooleanVar(value=False)
      self.num = num
      self.longueur = tk.StringVar(value='0.00')
      self.mesure_frame = None
      self.app = app
      self.pts = {"pt1" : point(color) , "pt2" : point(color)}
      self.created = False

      self.flag_affiche_frame.trace_add("write",self.display_state)
   
   def mesure_GUI(self):
      if self.mesure_frame != None:
         self.title_label = tk.Label(self.mesure_frame,text=self.title,font=("Arial", 10, "bold"),state="disabled")
         color_square = tk.Label(self.mesure_frame,bg=self.color, width=2, height=1, relief="raised",state='disabled')
         self.chek_affichage = tk.Checkbutton(self.mesure_frame,text='Afficher',variable=self.flag_affiche_ptLigne
                                          ,command=self._affiche_mesure,onvalue=1, offvalue=0,compound='top',state='disabled')
         select_mesure = tk.Radiobutton(self.mesure_frame,text='Selectionner',value=self.num,variable=self.app.choix_mesure)
         self.label_afficheur_longueure = tk.Label(self.mesure_frame,text="Longueur mesurée  ",state="disabled")
         self.afficheur_longueure = tk.Label(self.mesure_frame,textvariable=self.longueur,state="disabled")

         self.title_label.grid(row=0,column=0,columnspan=2,sticky='w',padx=(2,2),pady=(2,2))
         color_square.grid(row=0,column=1,sticky='e',padx=(2,2),pady=(2,2))
         self.chek_affichage.grid(row=1,column=0,sticky='w')
         select_mesure.grid(row=1,column=1,sticky="e")
         self.label_afficheur_longueure.grid(row=2,column=0,sticky="w",padx=(2,2),pady=(2,2))
         self.afficheur_longueure.grid(row=2,column=1,sticky='w',padx=(2,2),pady=(2,2))

         #Organisation de la fenêtre#
         self.mesure_frame.columnconfigure(0,weight=1)
         self.mesure_frame.columnconfigure(1,weight=1)
      else :
         print("self.mesure_frame == None")
      
   def _affiche_mesure(self):
      self.app.modif_canvas.set(True)

    
   def display_state(self,*args):
      etat = {"True" : "normal" , "False" : "disabled"}
      self.title_label.config(state=etat[str(self.flag_affiche_frame.get())])
      self.chek_affichage.config(state=etat[str(self.flag_affiche_frame.get())])
      self.label_afficheur_longueure.config(state=etat[str(self.flag_affiche_frame.get())])
      self.afficheur_longueure.config(state=etat[str(self.flag_affiche_frame.get())])
   
   def add_pt(self,event):
      if self.created == True:
         x_img = (event.x - self.app.img.coord_origine.get()['x']) / self.app.zoom_factor.get()
         y_img = (event.y - self.app.img.coord_origine.get()['y']) / self.app.zoom_factor.get()
         x_canvas , y_canvas = event.x , event.y
         for pt in self.pts.values():
            if not pt.created:
               pt.coord_pt_img = {"x": x_img, "y": y_img}
               pt.coord_pt_canvas = {"x": x_canvas, "y": y_canvas}
               pt.created = True
               break
      if self.pts['pt1'].created == True and self.pts['pt2'].created == True:
         self.longueur.set(str(self.calcul_distance()))
      
   
   def supprimer_pts(self):
      for pt in self.pts.values():
         pt.supprimer_pt()
   
   def maj_pos_pts(self):
      for pt in self.pts.values():
            if pt.created:
               x_canvas = (pt.coord_pt_img["x"] * self.app.zoom_factor.get()) + self.app.img.coord_origine.get()['x']
               y_canvas = (pt.coord_pt_img["y"] * self.app.zoom_factor.get()) + self.app.img.coord_origine.get()['y']
               pt.coord_pt_canvas = {"x": x_canvas, "y": y_canvas}
   
   def deplacer_pts(self,key_pt,event,deb_deplc_pt):
      dx , dy = event.x - deb_deplc_pt[0] , event.y - deb_deplc_pt[1]
      dx_img , dy_img = dx / self.app.zoom_factor.get() , dy / self.app.zoom_factor.get()
      coord_pt_act = self.pts[key_pt].coord_pt_img
      coord_pt = {'x' : coord_pt_act['x'] + dx_img , 'y' :coord_pt_act['y'] + dy_img}
      self.pts[key_pt].coord_pt_img = coord_pt
      self.pts[key_pt].coord_pt_canvas = {'x' : event.x, 'y' : event.y}
      if self.pts['pt1'].created == True and self.pts['pt2'].created == True:
         self.longueur.set(str(self.calcul_distance()))
   
   def calcul_distance(self):
      vect_dist = np.array([self.pts["pt1"].coord_pt_img['x'] - self.pts["pt2"].coord_pt_img['x'],
                            self.pts["pt1"].coord_pt_img['y'] - self.pts["pt2"].coord_pt_img['y']])
      dist = np.linalg.norm(vect_dist) * self.app.facteur_conversion.get()
      return round(dist,2)
   
      

      




class point():
   def __init__(self,color):
      self.color = color
      self.coord_pt_img = {"x":0,'y':0} # Les coordonnées du point sont selon l'image d'origine
      self.coord_pt_canvas = {"x":0,'y':0} 
      self.taille = 5 # diamètre du point
      self.id = None
      self.created = False  
   
   def supprimer_pt(self):
      self.coord_pt_img = {"x":0,'y':0} # Les coordonnées du point sont selon l'image d'origine
      self.coord_pt_canvas = {"x":0,'y':0} 
      self.taille = 5 # diamètre du point
      self.id = None
      self.created = False  
               

   

class btn_sauvegarde:
   def __init__(self,parent_frame,app):
      self.btn_sauvegarde_frame = tk.Frame(parent_frame)
      self.app = app
      self.app.flag_save_btn_affiche.trace_add("write",self.display_state)
      self.btn_sauvegarde_GUI()
   
   def btn_sauvegarde_GUI(self):
      self.btn = ttk.Button(self.btn_sauvegarde_frame,text="Sauvegarder la nouvelle echelle",command=self._save_scale_change,state="disabled")

      self.btn.grid(row=0,column=0,sticky='nsew',padx=(2,2),pady=(2,2))

      self.btn_sauvegarde_frame.columnconfigure(0,weight=1)

   def _save_scale_change(self):
      return None
   
   def display_state(self,*args):
      etat = {"True" : "normal" , "False" : "disabled"}
      self.btn.config(state=etat[str(self.app.flag_save_btn_affiche.get())])
   
   def _save_scale_change(self):
      self.btn_sauvegarde_frame.win = tk.Toplevel(self.btn_sauvegarde_frame)
      self.btn_sauvegarde_frame.win.title("Attention")
      self.btn_sauvegarde_frame.win.geometry("400x80")
      self.btn_sauvegarde_frame.win.grab_set()
      message = tk.Label(self.btn_sauvegarde_frame.win,text=f"Confirmer que vous voulez changer l'echelle selon 'Mesure Echelle' ?")
      btn_oui = tk.Button(self.btn_sauvegarde_frame.win,text="Oui",command=self.rep_confirmation_oui)
      btn_non = tk.Button(self.btn_sauvegarde_frame.win,text="Non",command=self.rep_confirmation_non)
      message.grid(row=0,column=0,columnspan=2,padx=(2,2),pady=(10,2))
      btn_oui.grid(row=1,column=0,sticky="we",padx=(2,2),pady=(10,2))
      btn_non.grid(row=1,column=1,sticky='we',padx=(2,2),pady=(10,2))
   
   def rep_confirmation_oui(self):
      self.app.facteur_conversion_app_princip.set(str(round(self.app.facteur_conversion.get(),2)))
      self.btn_sauvegarde_frame.win.destroy()
      return None
   
   def rep_confirmation_non(self):
      self.btn_sauvegarde_frame.win.destroy()
      return None

########################
#Geaphique###########
#####################
class image():
   def __init__(self):
      self.id_img = None #Reference de l'image affichée 
      self.tk_img = None #Reference du format Tkinter de l'image importée
      self.coord_origine = JSONVar(value={"x" : 0 , "y" : 0})#Coordonnées de l'origine de l'image
      # self.coord_origine = [0,0] #Coordonnées de l'origine de l'image
      self.Image_img = None #Reference de l'image importé (sans modifs)
      self.img_path = tk.StringVar(value="")
   
   def reboot(self):
      self.id_img = None 
      self.tk_img = None 
      self.coord_origine.set({"x" : 0 , "y" : 0})
      self.Image_img = None


class fenetre_image(tk.Canvas):
   def __init__(self,parent,app,*args,**kwargs):
      super().__init__(parent,*args,**kwargs)
      self.app = app
      self.app.img.img_path.trace_add("write",self._maj_fenetre)
      self.app.modif_canvas.trace_add("write",self._maj_fenetre)
      self.deb_deplc_img = []
      self.deb_deplc_pt = []
      self.pt_appuye = False
      self.key_pt = None

      self.bind("<ButtonPress-3>",self._deplacement)
      self.bind("<B3-Motion>", self._deplacement) 
      self.bind("<MouseWheel>", self._zoom)
      self.bind("<ButtonPress-1>", self._handl_pt)
      self.bind("<B1-Motion>", self._handl_pt)
   
   def _maj_fenetre(self,*args):
      path = self.app.img.img_path.get()
      self.app.img.Image_img = Image.open(path)
      img = self.app.img.Image_img
      new_w = int(img.width * self.app.zoom_factor.get())
      new_h = int(img.height * self.app.zoom_factor.get())
      img = img.resize((new_w, new_h), Image.LANCZOS)
      self.app.img.tk_image  = ImageTk.PhotoImage(img)
      self.delete('all')
      self.create_image(self.app.img.coord_origine.get()["x"],self.app.img.coord_origine.get()["y"],anchor="nw",image=self.app.img.tk_image)
      for mesure in self.app.list_mesures:
         if mesure.flag_affiche_ptLigne.get() == True:
            for pt in mesure.pts.values():
               if pt.created == True:
                  self.create_oval(pt.coord_pt_canvas["x"]-5, pt.coord_pt_canvas["y"]-5, 
                                 pt.coord_pt_canvas["x"]+5, pt.coord_pt_canvas["y"]+5, fill=pt.color)
            if mesure.pts['pt1'].created == True and mesure.pts['pt2'].created == True:
                self.create_line(mesure.pts['pt1'].coord_pt_canvas["x"], mesure.pts['pt1'].coord_pt_canvas["y"],
                                  mesure.pts['pt2'].coord_pt_canvas["x"], mesure.pts['pt2'].coord_pt_canvas["y"], fill=mesure.color, width=2)
         
   def _deplacement(self,event):
      if event.type == "4": #event.type vaut "4" si le bouton vient d'être pressé, c'est equivalent au start de déplacement (<ButtonPress-3>)
         self.deb_deplc_img = [event.x,event.y]
      if event.type ==  "6":#event.type vaut "6" si le bouton est pressé, c'est equivalent de déplacement(<B3-Motion>)
         dx , dy = event.x - self.deb_deplc_img[0] , event.y - self.deb_deplc_img[1]
         x_origine_act , y_origine_act = self.app.img.coord_origine.get()["x"] , self.app.img.coord_origine.get()["y"]
         self.app.img.coord_origine.set({"x":x_origine_act+dx , "y" : y_origine_act+dy})
         # self.img.coord_origine = [self.img.coord_origine[0] + dx , self.img.coord_origine[1] + dy]
         self.deb_deplc_img = [event.x,event.y] #On met à jour le début de déplacement
         for mesure in self.app.list_mesures:
            if mesure.created==True:
               mesure.maj_pos_pts()
         self._maj_fenetre()
   
   def _zoom(self,event):
      zoom_prec = self.app.zoom_factor.get()
      if event.delta > 0:
         self.app.zoom_factor.set(zoom_prec*1.1)
      else :
         self.app.zoom_factor.set(zoom_prec/1.1)
      factor_anc_nv = self.app.zoom_factor.get() / zoom_prec
      x_origine_act , y_origine_act = self.app.img.coord_origine.get()["x"] , self.app.img.coord_origine.get()["y"]
      coord_cible_img = [(event.x - x_origine_act) * factor_anc_nv, 
                        (event.y - y_origine_act) * factor_anc_nv]
      dx_dy = [coord_cible_img[0] + x_origine_act - event.x,
               coord_cible_img[1] + y_origine_act - event.y]
      self.app.img.coord_origine.set({"x":x_origine_act- dx_dy[0],
                                       "y":y_origine_act- dx_dy[1]})
      for mesure in self.app.list_mesures:
            if mesure.created==True:
               mesure.maj_pos_pts()
      self._maj_fenetre()

   def _handl_pt(self,event):
      if self.clic_on_img(event):
         if event.type == "4" :
            self.key_pt , self.pt_appuye = bool_pt_appuye(self.app.list_mesures[self.app.choix_mesure.get()] , event)
            if self.pt_appuye:
               self.deb_deplc_pt = [event.x,event.y]
            else:
               self.app.list_mesures[self.app.choix_mesure.get()].add_pt(event)
            self._maj_fenetre()
         if event.type == "6" and self.pt_appuye:
            self.app.list_mesures[self.app.choix_mesure.get()].deplacer_pts(self.key_pt,event,self.deb_deplc_pt)
            self.deb_deplc_pt = [event.x,event.y]
            self._maj_fenetre()

   def clic_on_img(self,event):
        image = self.app.img.Image_img
        x_good = event.x >= (self.app.img.coord_origine.get()['x']) and event.x <= (self.app.img.coord_origine.get()['x']+image.width*self.app.zoom_factor.get())
        y_good = event.y >= (self.app.img.coord_origine.get()['y']) and event.y <= (self.app.img.coord_origine.get()['y']+image.height*self.app.zoom_factor.get())
        return x_good and y_good

   
   
class interraction(tk.Frame):
   def __init__(self,parent,app,fi,*args,**kwargs):
      super().__init__(parent,*args,**kwargs)
      self.app = app
      self.fi = fi
      self.save_btn = btn_sauvegarde(self,self.app)
      self.app.mesures_supp.mesures_supp_frame = tk.Frame(self)
      for cle in self.app.mesures_supp.mes_mesures_supp.keys():
            self.app.mesures_supp.mes_mesures_supp[cle].mesure_frame = tk.Frame(self.app.mesures_supp.mesures_supp_frame)
            
      self.interraction_GUI()
   
   def interraction_GUI(self):
      img_ctrl = image_frame(self,self.app,self.fi)
      echelle_ctrl = Echelle_frame(self,self.app)
      self.app.mesures_supp.mesures_supp_GUI()
      self.save_btn.btn_sauvegarde_GUI()
      
      img_ctrl.grid(row=0,column=0,sticky="new",padx=(2,2),pady=(2,2))
      echelle_ctrl.grid(row=1,column=0,sticky="new",padx=(2,2),pady=(2,2))
      self.app.mesures_supp.mesures_supp_frame.grid(row=2,column=0,sticky="new",padx=(2,2),pady=(2,2))
      self.save_btn.btn_sauvegarde_frame.grid(row=3,column=0,sticky="new",padx=(2,2),pady=(2,2))

      self.columnconfigure(0,weight=1)


   

class AppState():
   def __init__(self,facteur_conversion_app_princip):
      self.je_rigole = 0
      self.img = image()
      self.zoom_factor = tk.DoubleVar(value=1.0)
      self.facteur_conversion = tk.DoubleVar(value=1.0)
      self.distance_saisie = tk.StringVar(value='0.00')
      self.choix_mesure = tk.IntVar(value=0)
      self.flag_mesures_supp_affiche = tk.BooleanVar(value=True)
      self.flage_changer_echelle_affiche = tk.BooleanVar(value=False)
      self.flag_echelle_frame = tk.BooleanVar(value=False)
      self.flag_save_btn_affiche = tk.BooleanVar(value=False)
      self.mesure_echelle = une_mesure(title="Mesure Echelle",color='red',num=0,app=self)
      self.mesures_supp = mesures_supp(app=self)
      self.list_mesures = [self.mesure_echelle , self.mesures_supp.mes_mesures_supp["Mesure_supp_1"],
                            self.mesures_supp.mes_mesures_supp["Mesure_supp_2"] , self.mesures_supp.mes_mesures_supp["Mesure_supp_3"]]
      self.modif_canvas = tk.BooleanVar(value=True)
      self.facteur_conversion_app_princip = facteur_conversion_app_princip
      # self.add_pt_flag = tk.BooleanVar(value=False)
      # self.mesures_supp = mesures_supp(self,self.app) 
      


class Application_calibrage(tk.Toplevel):
    def __init__(self,facteur_conversion_app_princip):
        super().__init__()
        self.title("Calibrage de camera")
        self.geometry("1100x700")
        self.resizable(False,False)
        self.facteur_conversion_app_princip = facteur_conversion_app_princip
        self.app = AppState(self.facteur_conversion_app_princip)


        fi = fenetre_image(self,self.app)
        interr = interraction(self,self.app,fi,width=250,bg="grey")


        #Disposition elt fenêtre#
        fi.grid(row=0,column=0,sticky="nsew",padx=(1,1),pady=(1,1))
        interr.grid(row=0,column=1,sticky="nse",padx=(1,1),pady=(1,1))
        interr.grid_propagate(False)
       
        #Organisation de la fenêtre#
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
      #   self.columnconfigure(1,weight=1)
        

# if __name__ == '__main__':
#   app = Application_calibrage()
#   app.mainloop()

