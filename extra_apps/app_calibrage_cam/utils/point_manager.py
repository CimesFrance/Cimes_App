import numpy as np


def bool_pt_appuye(mesure,event):
    key_pt , pt_appuye = -1 , False
    for key, pt in mesure.pts.items():
        vect_dist = np.array([pt.coord_pt_canvas["x"]-event.x,pt.coord_pt_canvas["y"]-event.y])
        dist = np.linalg.norm(vect_dist) 
        if dist <= pt.taille:
            key_pt , pt_appuye = key , True
            break
    return key_pt , pt_appuye