# codé en utf 8
# Date : du 06/10/2025 au 27/10/2025 
# Auteurs : Rayane Chekatt / Lino Battesti
# Le programme permet de créer la balle, son mouvement et ses collisions avec la fenetre
# To do list : None


from tkinter import Canvas
from random import uniform
from math import pi, cos, sin

# --- Constantes globales ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
ball_r = 8


class Ball:
    """Classe représentant la balle du casse-brique."""

    def __init__(self, canvas: Canvas, ball_r: int):
        """
        Entrée :
            - canvas (Canvas) : zone de dessin
            - ball_r (int) : rayon de la balle
        Sortie : None
        But : initialiser la balle avec une direction et une vitesse aléatoires
        """
        self.canvas = canvas
        self.__r = ball_r

        # Vitesse et direction initiales aléatoires
        self.__velocity = uniform(1.8, 2) * 3
        self.__angle = uniform(0, 2 * pi)

        # Position initiale (au centre)
        self.__x = WINDOW_WIDTH / 2
        self.__y = WINDOW_HEIGHT / 2

        # Composantes du déplacement
        self.__dx = self.__velocity * cos(self.__angle)
        self.__dy = self.__velocity * sin(self.__angle)

        # Création de l’ovale représentant la balle
        self.__ball = canvas.create_oval(
            self.__x - self.__r, self.__y - self.__r,
            self.__x + self.__r, self.__y + self.__r,
            width=5, fill='white'
        )

    def reset_pos(self):
        """
        Entrée : None
        Sortie : None
        But : replacer la balle au centre et redéfinir une direction aléatoire
        """
        self.__x = WINDOW_WIDTH / 2
        self.__y = WINDOW_HEIGHT / 2
        self.__velocity = uniform(1.8, 2) * 3
        self.__angle = uniform(1, 2 * pi - 1)
        self.__dx = self.__velocity * cos(self.__angle)
        self.__dy = self.__velocity * sin(self.__angle)

    def update(self):
        """
        Entrée : None
        Sortie : None
        But : mettre à jour la position de la balle et gérer les rebonds sur les bords
        """
        # Collision mur droit
        if self.__r + self.__x + self.__dx > WINDOW_WIDTH:
            self.__x = 2 * (WINDOW_WIDTH - self.__r) - self.__x
            self.__dx = -self.__dx  # inversion du sens horizontal

        # Collision mur gauche
        if self.__x - self.__r + self.__dx < 0:
            self.__x = 2 * self.__r - self.__x
            self.__dx = -self.__dx

        # Collision plafond
        if self.__y - self.__r + self.__dy < 0:
            self.__y = 2 * self.__r - self.__y
            self.__dy = -self.__dy  # inversion du sens vertical

        # Mise à jour des coordonnées
        self.__x += self.__dx
        self.__y += self.__dy

        # Mise à jour de la position graphique sur le canvas
        self.canvas.coords(
            self.__ball,
            self.__x - self.__r, self.__y - self.__r,
            self.__x + self.__r, self.__y + self.__r
        )

    def coords(self):
        """Entrée : None | Sortie : liste [x1, y1, x2, y2] | But : renvoyer les coordonnées de la balle"""
        return self.canvas.coords(self.__ball)
