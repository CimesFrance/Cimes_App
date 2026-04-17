import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.optimize import minimize
from scipy.interpolate import interp1d
import copy

from utils.utils_change_corr_params.import_manager import importer_image_tk,info_extract_courbe_numerique
from utils.utils_change_corr_params.correction_manager import inv_correct,correct,calc_erreur,erreur_minim


class une_courbe_affiche(tk.Frame):
    """Cette classe permet de construire un carré, le titre du graphe et un check button propre à chaque courbe"""
    def __init__(self,parent,un_cumul,graphe,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        
        self.graphe = graphe
        self.un_cumul = un_cumul
        self.un_cumul.show_courbe_elt.trace_add("write",self.affiche_elt_courbe)

        self._une_courbe_frame_GUI()

    def _une_courbe_frame_GUI(self):
        self.color_square = tk.Label(self, bg=self.un_cumul.Color, width=2, height=1, relief="raised",state="disabled")
        self.label_check_affichage_courbe = tk.Label(self,text=self.un_cumul.Name,state="disabled")
        self.check_affichage_courbe = tk.Checkbutton(self,state="disabled",variable=self.un_cumul.flag_affichage
                                        ,command=self.maj_cumul_courbe,onvalue=1, offvalue=0)

        self.color_square.grid(row=0,column=0,sticky='w',padx=(2,2),pady=(2,2))
        self.label_check_affichage_courbe.grid(row=0,column=1,sticky="ew",padx=(2,2),pady=(2,2))
        self.check_affichage_courbe.grid(row=0,column=2,sticky='e',padx=(2,2),pady=(2,2))

        for i in range(3):
            self.columnconfigure(i,weight=1)

    def affiche_elt_courbe(self,*args):
        etat = {"True" : "normal" , "False" : "disabled"}
        self.color_square.config(state=etat[str(self.un_cumul.show_courbe_elt.get())])
        self.label_check_affichage_courbe.config(state=etat[str(self.un_cumul.show_courbe_elt.get())])
        self.check_affichage_courbe.config(state=etat[str(self.un_cumul.show_courbe_elt.get())])
    def maj_cumul_courbe(self):
        self.graphe._maj_cumuls()
        self.graphe.canvas_my_graph.draw()




class courbes_frame(tk.Frame):
    """Regroupe tout les afficheurs de courbes avec un titre"""
    def __init__(self,parent,app,graphe,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        self.app = app

        self.my_granulos = app.my_granulos
        self.graphe = graphe
        self._courbes_frame_GUI()

    def _courbes_frame_GUI(self):
        titre_affichage_courbes = tk.Label(self,text = "Courbes",font=("Arial", 14, "bold"))
        self.courbe_num = une_courbe_affiche(self,self.my_granulos.num,self.graphe)# Courbe avec correction actuelle
        self.courbe_originale = une_courbe_affiche(self,self.my_granulos.originale,self.graphe)# Courbe avan ancienne corrrection
        self.courbe_prat = une_courbe_affiche(self,self.my_granulos.prat,self.graphe)
        
         
        titre_affichage_courbes.grid(row=0,sticky="nsew",padx=(2,2),pady=(2,2))
        self.courbe_num.grid(row=1,column=0,sticky="nsew",padx=(2,2),pady=(2,2))
        self.courbe_originale.grid(row=2,column=0,sticky="nsew",padx=(2,2),pady=(2,2))
        self.courbe_prat.grid(row=3,column=0,sticky="nsew",padx=(2,2),pady=(2,2))
        
        self.columnconfigure(0,weight=2)



class cumul:
    """Classe contenant les informations d'UN SEUL CUMUL"""
    def __init__(self,Name,Color,granulo,logo):
        self.Name = Name #Format str
        self.Color = Color #Format str
        self.granulo = granulo #format List, contenant la granulo
        self.logo = logo #image format tk
        self.flag_affichage = tk.IntVar(value=0)
        self.show_courbe_elt = tk.BooleanVar(value=False)
        


class mes_cumuls:
    """Classe contenant tout les cumuls de l'application"""
    def __init__(self):
        self.num = cumul(Name="Courbe numérique corrigée",Color='red',granulo=None,logo=importer_image_tk("photo camera.png")) 
        self.originale = cumul(Name="Courbe numérique originale",Color='Blue',granulo=None,logo=None) 
        self.prat = cumul(Name="Courbe réelle tamisée",Color='green',granulo=None,logo=importer_image_tk("logo tamis.png"))


class graphe(tk.Frame):
    def __init__(self,parent,app,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        self.app = app
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self._maj_cumuls()

        self.canvas_my_graph = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_my_graph.draw()
        self.canvas_my_graph.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _maj_cumuls(self):
        self.ax.cla()
        dict_infos = {"num":{"flag":self.app.my_granulos.num.flag_affichage.get(),"courbe":self.app.my_granulos.num.granulo,"name":self.app.my_granulos.num.Name,"color":self.app.my_granulos.num.Color},
                 "originale" : {"flag" : self.app.my_granulos.originale.flag_affichage.get(), "courbe" : self.app.my_granulos.originale.granulo,"name":self.app.my_granulos.originale.Name,"color":self.app.my_granulos.originale.Color},
                 "prat" : {"flag" : self.app.my_granulos.prat.flag_affichage.get(), "courbe" : self.app.my_granulos.prat.granulo,"name":self.app.my_granulos.prat.Name,"color":self.app.my_granulos.prat.Color}}
        for info in dict_infos.values():
            if info["flag"] == 1 and info["courbe"] != None:
                self.ax.plot(info["courbe"]["x_axis"], info["courbe"]["y_axis"],label=info["name"],color=info["color"])
        self.ax.legend()
        self.ax.grid(True)
        self.ax.set_ylabel("Pourcentage de passants cumulés(%)")
        self.ax.set_xlabel("Tamis(mm)")
        self.ax.set_xlim(0, 90)
        self.ax.set_ylim(0, 110)
        


class import_granulo_frame(tk.Frame):
    """Importation d'une courbe exterieur"""
    def __init__(self,parent,app,graphe,type,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        
        self.app = app
        self.graphe = graphe
        self.type = type
        self.tk_img_import_logo = importer_image_tk("logodownload.png")

        self.choix_granulo()

        self._import_granulo_frame_GUI()

    def _import_granulo_frame_GUI(self):
        photo = tk.Label(self,image=self.logo)
        label_import = tk.Label(self,text=self.txt)
        btn_import = ttk.Button(self,image=self.tk_img_import_logo,command=lambda : self._import())

        photo.grid(row=0,column=0,padx=(2,2),pady=(2,2))
        label_import.grid(row=0,column=1,sticky='w',padx=(2,2),pady=(2,2))
        btn_import.grid(row=0,column=2,sticky='e',padx=(2,2),pady=(2,2))

        for i in range(3):
            self.columnconfigure(i,weight=1)
    
    def choix_granulo(self):
        if self.type == 'num':
            self.logo = self.app.my_granulos.num.logo
            self.txt = "Importer courbe numérique"
        if self.type == 'tamis':
            self.logo = self.app.my_granulos.prat.logo
            self.txt = "Importer la courbe réelle"

    def _import(self):
        if self.type == 'num':
            path = filedialog.askopenfilename(title="Selectionner un fichier d\'anlyse numérique",
                                            filetypes=[("Fichiers ZIP", "*.zip")])
            if not path:
                print("Erreur : Aucune fichier n'a été selectionné")
            else:
                granulo , correct_var = info_extract_courbe_numerique(path)
                self.maj_var_num(granulo,correct_var)
                self.maj_affichage_num()
        elif self.type == 'tamis':
            path = filedialog.askopenfilename(title="Selectionner un fichier d\'anlyse numérique",
                                          filetypes=[("Fichiers Excel", "*.xlsx")])    
            if not path:
                print("Erreur : Aucune fichier n'a été selectionné")
            else:
                df = pd.read_excel(path)
                self.maj_var_prat(df)
                self. maj_affichage_prat()
        else:
            print("Error import type")
        self.error_handle()

    
    def maj_var_num(self,granulo,correct_var):
        """maj des variables après importation de courbe numérique corrigée"""
        self.app.my_granulos.num.granulo = {'x_axis':granulo["tamis"],"y_axis":granulo["cumul"]}
        scale_imprt = correct_var["Scale"]
        offset_imprt = correct_var["Offset"]
        self.app.var_correct["var_act"]["scale"].set(str(scale_imprt))
        self.app.var_correct["var_act"]["offset"].set(str(offset_imprt))
        inv_corr_x_axes = inv_correct(granulo["tamis"],scale_imprt,offset_imprt)
        self.app.my_granulos.originale.granulo = {"x_axis" : inv_corr_x_axes , "y_axis" : granulo["cumul"]}
        self.app.my_granulos.originale.flag_affichage.set(1)
        self.app.my_granulos.num.flag_affichage.set(1)

    def maj_affichage_num(self):
        """maj de l'affichage après importation de la courbe numérique corrigée"""
        self.app.show_correct_frame_act.set(1)
        self.app.my_granulos.num.show_courbe_elt.set(True)
        self.app.my_granulos.originale.show_courbe_elt.set(True)
        self.app.show_param_nv.set(True)
        self.app.flag_affiche_btn_sauvegarde.set(True)
        self.graphe._maj_cumuls()
        self.graphe.canvas_my_graph.draw()
    
    def maj_var_prat(self,df):
        """maj des variabes après importation de la courbe réelle tamisée"""
        self.app.my_granulos.prat.granulo = {'x_axis':df["Tamis(mm)"].tolist(),"y_axis":df["Cumul(%)"].tolist()}
        self.app.my_granulos.prat.flag_affichage.set(1)
    
    def maj_affichage_prat(self):
        """maj de l'affichage après importation de courbe réelle tamisée"""
        self.app.my_granulos.prat.show_courbe_elt.set(True)
        self.graphe._maj_cumuls()
        self.graphe.canvas_my_graph.draw()
    
    def error_handle(self):
        if self.app.my_granulos.num.granulo != None and self.app.my_granulos.prat.granulo != None:
            self.app.erreur.set(str(calc_erreur(np.array(self.app.my_granulos.num.granulo["x_axis"]),
                                                np.array(self.app.my_granulos.num.granulo["y_axis"]),
                                                np.array(self.app.my_granulos.prat.granulo["x_axis"]),
                                                np.array(self.app.my_granulos.prat.granulo["y_axis"]))))
            self.app.flag_affiche_erreur.set(True)
    


        

class barre_correct_frame_act(tk.Frame):
    def __init__(self,parent,app,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        self.app = app
        self.var_correct_act = app.var_correct['var_act'] 
        self.app.show_correct_frame_act.trace_add("write",self.affiche_elt_correct_frame_act)
        self._barre_correct_frame_act_GUI()

    def _barre_correct_frame_act_GUI(self):
        tite = tk.Label(self,text="Paramètres de correction actuels",font=("Arial", 10, "bold"))
        scale_label = tk.Label(self,text='scale')
        self.scale_affiche = tk.Label(self,textvariable=self.var_correct_act["scale"],state='disabled')
        offset_label = tk.Label(self,text='offset') 
        self.offset_affiche = tk.Label(self,textvariable=self.var_correct_act["offset"],state='disabled') 

        tite.grid(row=0,column=0,columnspan=2,sticky='we',padx=(2,2),pady=(2,2))
        scale_label.grid(row=1,column=0,sticky='we',padx=(2,2),pady=(2,2))
        offset_label.grid(row=1,column=1,sticky='we',padx=(2,2),pady=(2,2))
        self.scale_affiche.grid(row=2,column=0,sticky='we',padx=(2,2),pady=(2,2))
        self.offset_affiche.grid(row=2,column=1,sticky='we',padx=(2,2),pady=(2,2))

        for i in range(2):
            self.columnconfigure(i,weight=1)
    
    def affiche_elt_correct_frame_act(self,*args):
        if self.app.show_correct_frame_act.get() == True:
            self.scale_affiche.config(state='normal')
            self.offset_affiche.config(state='normal')
        else:
            self.scale_affiche.config(state='disabled')
            self.offset_affiche.config(state='disabled')

class donnees_ext_frame(tk.Frame):
    """S'occupe d'organiser la partie importation de données exterieurs"""
    def __init__(self,parent,app,graphe,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)

        self.app = app
        self.graphe = graphe
        self._donnees_ext_frame_GUI()
    
    def _donnees_ext_frame_GUI(self):
        titre = tk.Label(self,text="Données Exterieurs",font=("Arial", 14, "bold"))
        self.param_correct_act = barre_correct_frame_act(self,self.app)
        import_num = import_granulo_frame(self,self.app,self.graphe,'num')
        import_reelle = import_granulo_frame(self,self.app,self.graphe,'tamis')
        separator = tk.Frame(self, bg="black", height=2)
        
        titre.grid(row=0,column=0,columnspan=3,sticky='nsew',padx=(2,2),pady=(2,2))
        import_num.grid(row=1,column=0,sticky='nsew',padx=(2,2),pady=(2,2))
        import_reelle.grid(row=2,column=0,sticky='nsew',padx=(2,2),pady=(2,2))
        separator.grid(row=3,column=0,sticky='nsew',padx=(2,2),pady=(2,2))
        self.param_correct_act.grid(row=4,column=0,sticky='nsew',padx=(2,2),pady=(2,2))
        
        self.columnconfigure(0,weight=2)


class barre_correct_frame_nv(tk.Frame):
    def __init__(self,parent,app,graphe,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        self.my_granulos = app.my_granulos
        self.var_correct_nv = app.var_correct['var_nv']
        self.graphe = graphe
        self.app = app
        self.app.show_param_nv.trace_add("write",self._affiche_param_corr_nv)
        self._barre_correct_frame_GUI()

    def _barre_correct_frame_GUI(self):
        tite = tk.Label(self,text="Nouveaux paramètres de correction",font=("Arial", 10, "bold"))
        scale_entry_label = tk.Label(self,text='scale')
        self.scale_entry = tk.Entry(self,textvariable=self.var_correct_nv["scale"],state='disabled')
        offset_entry_label = tk.Label(self,text='offset') 
        self.offset_entry = tk.Entry(self,textvariable=self.var_correct_nv["offset"],state='disabled') 
        self.validat_btn = ttk.Button(self,text='valider',command=lambda : self._validate_corr_change(),state='disabled')

        tite.grid(row=0,column=0,columnspan=3,sticky='we',padx=(2,2),pady=(2,2))
        scale_entry_label.grid(row=1,column=0,sticky='we',padx=(2,2),pady=(2,2))
        offset_entry_label.grid(row=1,column=1,sticky='we',padx=(2,2),pady=(2,2))
        self.scale_entry.grid(row=2,column=0,sticky='we',padx=(2,2),pady=(2,2))
        self.offset_entry.grid(row=2,column=1,sticky='we',padx=(2,2),pady=(2,2))
        self.validat_btn.grid(row=2,column=2,sticky='we',padx=(2,2),pady=(2,2))

        for i in range(3):
            self.columnconfigure(i,weight=1)
    
    def _validate_corr_change(self):
        scale = float(self.var_correct_nv["scale"].get())
        if scale < 0:
            scale = 0.001
            self.var_correct_nv["scale"].set(str(0.001))
        offset = float(self.var_correct_nv["offset"].get())
        corr_x_axes = correct(self.my_granulos.originale.granulo["x_axis"],scale,offset)
        self.my_granulos.num.granulo = {"x_axis" : corr_x_axes , "y_axis" : self.my_granulos.originale.granulo["y_axis"]}
        self.graphe._maj_cumuls()
        self.graphe.canvas_my_graph.draw()
        if self.app.my_granulos.prat.granulo != None and self.app.my_granulos.num.granulo != None:
            self.app.erreur.set(str(calc_erreur(np.array(self.app.my_granulos.num.granulo["x_axis"]),
                                                    np.array(self.app.my_granulos.num.granulo["y_axis"]),
                                                    np.array(self.app.my_granulos.prat.granulo["x_axis"]),
                                                    np.array(self.app.my_granulos.prat.granulo["y_axis"]))))
        
      
    def _affiche_param_corr_nv(self,*args):
        etat = {"True" : "normal" , "False" : "disabled"}
        self.scale_entry.config(state=etat[str(self.app.show_param_nv.get())])
        self.offset_entry.config(state=etat[str(self.app.show_param_nv.get())])
        self.validat_btn.config(state=etat[str(self.app.show_param_nv.get())])

class correct_frame(tk.Frame):
    def __init__(self,parent,app,graphe,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)

        self.app = app
        self.my_granulos = app.my_granulos
        self.graphe = graphe
        self.var_correct = app.var_correct
        self.erreur = app.erreur
        self.app.flag_affiche_erreur.trace_add("write",self.affiche_erreur_btn_auto)
        self.app.flag_affiche_btn_sauvegarde.trace_add("write",self.affiche_btn_sauvegarde)

        self._auto_error_fram_GUI()
        self._correct_frame_GUI()

    def _auto_error_fram_GUI(self):
        self.auto_err = tk.Frame(self)
        afficheur_err_label = tk.Label(self.auto_err,text="Erreur : ")
        self.afficheur_err = tk.Label(self.auto_err,textvariable=self.erreur,state="disabled")
        self.btn_auto_corr = ttk.Button(self.auto_err,text="Correction Auto",command=self._correction_auto,state="disabled")
        

        afficheur_err_label.grid(row=0,column=0,sticky="w",padx=(2,2),pady=(2,2))
        self.afficheur_err.grid(row=0,column=1,sticky="w",padx=(2,2),pady=(2,2))
        self.btn_auto_corr.grid(row=0,column=2,sticky="e",padx=(2,2),pady=(2,2))

        self.auto_err.columnconfigure(2,weight=1)
    
    def affiche_erreur_btn_auto(self,*args):
        etat = {"True" : "normal" , "False" : "disabled"}
        self.afficheur_err.config(state=etat[str(self.app.flag_affiche_erreur.get())])
        self.btn_auto_corr.config(state=etat[str(self.app.flag_affiche_erreur.get())])
    
    def affiche_btn_sauvegarde(self,*args):
        etat = {"True" : "normal" , "False" : "disabled"}
        self.save_btn.config(state=etat[str(self.app.flag_affiche_btn_sauvegarde.get())])


    def _correct_frame_GUI(self):
        title = tk.Label(self,text="Correction",font=("Arial", 14, "bold"))
        separator = tk.Frame(self, bg="black", height=2)
        param_correct_nv = barre_correct_frame_nv(self,self.app,self.graphe)
        self.save_btn = ttk.Button(self,text="Sauvegarder les nouveaux paramètres",command=self._save_new_corr_params,state="disabled")

        title.grid(row=0,column=0,columnspan=3,sticky="nsew",padx=(2,2),pady=(2,2))
        self.auto_err.grid(row=1,column=0,columnspan=3,sticky="nsew",padx=(2,2),pady=(2,2))
        separator.grid(row=2,column=0,columnspan=3,sticky="nsew",padx=(2,2),pady=(2,2))
        param_correct_nv.grid(row=3,column=0,columnspan=3,sticky="nsew",padx=(2,2),pady=(2,2))
        self.save_btn.grid(row=4,column=0,columnspan=3,sticky="nsew",padx=(2,2),pady=(2,2))

        self.columnconfigure(0,weight=1)
    
    def _correction_auto(self):
        param0 = [1.0 , 0.0]
        tamis_originale = np.array(self.my_granulos.originale.granulo["x_axis"])
        cumulatif_originale = np.array(self.my_granulos.originale.granulo["y_axis"])
        tamis_pratique = np.array(self.my_granulos.prat.granulo["x_axis"])
        cumulatif_pratique = np.array(self.my_granulos.prat.granulo["y_axis"])
        res = minimize(
        erreur_minim,
        param0,
        args=(tamis_originale, cumulatif_originale,
            tamis_pratique, cumulatif_pratique),
        bounds = [(1e-6, None), (None, None)]   
        )
        scale_nv , offset_nv = res.x
        self.var_correct["var_nv"]["scale"].set(str(round(scale_nv,3)))
        self.var_correct["var_nv"]["offset"].set(str(round(offset_nv,3)))
        tamis_orig = self.my_granulos.originale.granulo["x_axis"]
        self.my_granulos.num.granulo["x_axis"] =  correct(tamis_orig,scale_nv,offset_nv)
        self.graphe._maj_cumuls()
        self.graphe.canvas_my_graph.draw()
        self.app.erreur.set(str(calc_erreur(np.array(self.app.my_granulos.num.granulo["x_axis"]),
                                                np.array(self.app.my_granulos.num.granulo["y_axis"]),
                                                np.array(self.app.my_granulos.prat.granulo["x_axis"]),
                                                np.array(self.app.my_granulos.prat.granulo["y_axis"]))))
    
    def _save_new_corr_params(self):
        self.win=tk.Toplevel(self)
        self.win.title("Attention !")
        self.win.geometry("600x80")
        self.win.grab_set()
        message = tk.Label(self.win,text="Etes vous sur de vouloir mettre à jour les nouveaux paramètre de correction sur l'application principale ?")
        btn_oui = tk.Button(self.win,text="Oui",command=self.rep_confirmation_oui)
        btn_non = tk.Button(self.win,text="Non",command=self.rep_confirmation_non)
        message.grid(row=0,column=0,columnspan=2,padx=(2,2),pady=(10,2))
        btn_oui.grid(row=1,column=0,sticky="we",padx=(2,2),pady=(10,2))
        btn_non.grid(row=1,column=1,sticky='we',padx=(2,2),pady=(10,2))
        self.win.columnconfigure(0,weight=1)
        self.win.columnconfigure(1,weight=1)
    
    def rep_confirmation_oui(self):
        new_scale = float(self.var_correct["var_nv"]["scale"].get())
        new_offset = float(self.var_correct["var_nv"]["offset"].get())
        self.app.param_corr_app_princ["scale"].set(new_scale)
        self.app.param_corr_app_princ["offset"].set(new_offset)
        self.win.destroy()
        return None
    
    def rep_confirmation_non(self):
        self.win.destroy()
        return None

class interfaceCommunication(tk.Frame):
    def __init__(self,parent,app,graphe,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)

        #Variables 
        self.app = app
        self.graphe = graphe

         #Graphique
        self._interfaceCommunication_GUI()

    def _interfaceCommunication_GUI(self):
       
        eplac_donnees_ext = donnees_ext_frame(self,self.app,self.graphe)
        eplac_courbes = courbes_frame(self,self.app,self.graphe)
        eplac_corr = correct_frame(self,self.app,self.graphe)

        eplac_donnees_ext.grid(row=0,columnspan=3,sticky='nsew',padx=(2,2),pady=(2,2))
        eplac_courbes.grid(row=1,columnspan=3,sticky='nsew',padx=(2,2),pady=(2,2))
        eplac_corr.grid(row=2,columnspan=3,sticky='nsew',padx=(2,2),pady=(2,2))
    
        self.columnconfigure(0,weight=2)


class AppState:
    """Classe contenant les variables partagés de l'application"""
    def __init__(self,param_corr_app_princ):
        self.my_granulos = mes_cumuls()
        self.var_correct = {"var_act" : None , "var_nv" : None}
        for key in self.var_correct:
            self.var_correct[key] = {"scale" : tk.StringVar(value="1.00") , "offset" : tk.StringVar(value="0.00")}
        self.erreur = tk.StringVar(value="0.00")
        self.show_correct_frame_act = tk.BooleanVar(value=False)
        self.show_correct_frame = tk.BooleanVar(value=False)
        self.show_courbes_frame = tk.BooleanVar(value=False)
        self.flag_affiche_erreur = tk.BooleanVar(value=False)
        self.show_param_nv = tk.BooleanVar(value=False)
        self.flag_affiche_btn_sauvegarde = tk.BooleanVar(value=False)
        self.param_corr_app_princ = param_corr_app_princ


class appReglageParamsCorrectEmpririque(tk.Toplevel):
    """Application qui permet de changer les paramètres de correction empirique ("scale" et "offset") appliqués à la courbe numérique"""
    def __init__(self,param_corr_app_princ,*args,**kwargs):
        super().__init__(*args,**kwargs)

        #Variables
        self.param_corr_app_princ = param_corr_app_princ
        self.app = AppState(self.param_corr_app_princ)

        #Dimensionnement de la fenêtre
        self.geometry("1000x750")
        self.resizable(False, False)
        self.title("CIMES - Changer les paramètres de correction")

        #Créer une interface d'interration avec l'utilisateur
        self.graphe = graphe(self,self.app)
        iC = interfaceCommunication(self,self.app,self.graphe,width = 300,bg='grey')
        
        #Graphique
        iC.grid(row=0,column=0,sticky='nsew',padx=(2,2),pady=(2,2))
        iC.grid_propagate(False)
        self.graphe.grid(row=0,column=1,sticky='nsew')

        self.rowconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
  

        
# if __name__ == '__main__':
#   app = appReglageParamsCorrectEmpririque()
#   app.mainloop()
