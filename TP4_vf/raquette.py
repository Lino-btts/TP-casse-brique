# codé en utf 8
# Date : du 06/10/2025 au 27/10/2025 
# Auteurs : Rayane Chekatt / Lino Battesti
# Le programme permet de créer la raquette et de gérer son mouvement.
# To do list : None

from tkinter import Canvas

class Raquette:
    """Classe représentant la raquette contrôlée par le joueur."""

    def __init__(self, canvas: Canvas, width=100, height=12):
        """
        Entrée :
            - canvas (Canvas) : zone de dessin du jeu
            - width (int) : largeur de la raquette
            - height (int) : hauteur de la raquette
        Sortie : None
        But : créer la raquette et initialiser ses propriétés (position, vitesse)
        """
        self.canvas = canvas
        self.width = width
        self.height = height

        # Position de départ centrée horizontalement
        start_x = (800 - width) / 2
        start_y = 600 - 40  # légèrement au-dessus du bas de la fenêtre

        self.id = canvas.create_rectangle(
            start_x, start_y,
            start_x + width, start_y + height,
            fill="blue" )
        

        self.x = 0  # vitesse horizontale
        self.canvas_width = 800
        self.move_speed = 10  # vitesse de déplacement par tick

    def move_left(self, event=None):
        """Entrée : event | Sortie : None | But : déplacer la raquette vers la gauche"""
        self.x = -self.move_speed

    def move_right(self, event=None):
        """Entrée : event | Sortie : None | But : déplacer la raquette vers la droite"""
        self.x = self.move_speed

    def stop(self, event=None):
        """Entrée : event | Sortie : None | But : arrêter le mouvement de la raquette"""
        self.x = 0

    def update(self):
        """
        Entrée : None
        Sortie : None
        But : mettre à jour la position de la raquette en fonction de sa vitesse
        """
        x1, y1, x2, y2 = self.canvas.coords(self.id)

        # Nouvelles coordonnées en fonction du déplacement horizontal
        new_x1 = x1 + self.x
        new_x2 = x2 + self.x

        # Gestion des limites de l’écran
        if new_x1 < 0:  # à gauche
            new_x1 = 0
            new_x2 = self.width
        if new_x2 > self.canvas_width:  # à droite
            new_x2 = self.canvas_width
            new_x1 = new_x2 - self.width

        # Appliquer les nouvelles coordonnées à la raquette
        self.canvas.coords(self.id, new_x1, y1, new_x2, y2)

    def coords(self):
        """Entrée : None | Sortie : liste [x1, y1, x2, y2] | But : retourner la position actuelle"""
        return self.canvas.coords(self.id)
