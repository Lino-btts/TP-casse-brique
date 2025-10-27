import tkinter as tk

class Brick:
    """Classe représentant une brique à casser."""

    def __init__(self, canvas, x1, y1, x2, y2, color="orange", hits=None):
        """
        Entrée :
            - canvas (tk.Canvas) : zone de dessin
            - (x1, y1, x2, y2) (float) : coordonnées du rectangle
            - color (str) : couleur de la brique
            - hits (int) : nombre de coups nécessaires pour la casser
        Sortie : None
        But : créer une brique avec une résistance donnée
        """
        self.__canvas = canvas
        self.hits = hits
        # Création du rectangle sur le canvas
        self.id = canvas.create_rectangle(x1, y1, x2, y2, fill=color,
                                          width=1, outline="black")

    def coords(self):
        """Entrée : None | Sortie : liste [x1, y1, x2, y2] | But : retourner les coordonnées de la brique"""
        return self.__canvas.coords(self.id)
