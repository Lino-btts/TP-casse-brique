import math, random
import tkinter as tk
import csv

from ball import Ball
from brick import Brick
from raquette import Raquette

# --- Constantes ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 12
PADDLE_Y_OFFSET = 40
ball_r = 8
BRICK_ROWS = 6
BRICK_COLUMNS = 10
BRICK_WIDTH = 70
BRICK_HEIGHT = 20
BRICK_PADDING = 6
TOP_OFFSET = 60
INITIAL_LIVES = 3


class Fenetre:
    """Classe principale du jeu Casse-Brique.
    Gère l'interface, les objets (balles, raquettes, briques), et la logique du jeu.
    """

    def __init__(self, window, difficulte):
        """
        Entrée : 
            - window (tk.Tk) : fenêtre principale
            - difficulte (int) : nombre de coups nécessaires pour casser une brique
        Sortie : None
        But : initialiser la fenêtre de jeu et les éléments graphiques
        """
        self.__INITIAL_LIVES = 3
        self.__score = 0
        self.__pause = 1
        self.__hits = difficulte

        # --- Création de la fenêtre ---
        self.__fenetre = window
        for i in self.__fenetre.winfo_children():
            i.destroy()  # supprime les widgets précédents (utile lors d’un retour au menu)

        self.__fenetre.title('Casse brique')
        self.__fenetre.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')

        # Création du canvas principal du jeu
        self.__canvas = tk.Canvas(self.__fenetre, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                                  bd=0, highlightthickness=0, background='black')

        # --- Vies (représentées par des ovales en haut à droite) ---
        self.__liste_vies = [self.__canvas.create_oval(710 + 30*i, 10, 730 + 30*i, 30,
                                                       width=5, fill='pink') for i in range(3)]
        self.__vies = len(self.__liste_vies)

        # --- Score ---
        self.__score_text = self.__canvas.create_text(10, 10, anchor="nw", font=("Helvetica", 14),
                                                      text=f"Score: {self.__score}", fill='white')

        # --- Création des objets du jeu ---
        self.__raquette = Raquette(self.__canvas)
        self.__ball = Ball(self.__canvas, ball_r)
        self.__bricks = []

        # --- Liens clavier ---
        self.__fenetre.bind("<Left>", self.__raquette.move_left)
        self.__fenetre.bind("<Right>", self.__raquette.move_right)
        self.__fenetre.bind("<KeyRelease-Left>", self.__raquette.stop)
        self.__fenetre.bind("<KeyRelease-Right>", self.__raquette.stop)
        self.__fenetre.bind('<p>', self.pause)

    def pause(self, event=None):
        """
        Entrée : event (optionnel)
        Sortie : None
        But : Mettre le jeu en pause ou le relancer
        """
        self.__pause = 0 if self.__pause == 1 else 1
        self.update_loop()

    def end_game(self, etat):
        """
        Entrée :
            - etat (str) : texte affiché (victoire/défaite)
        Sortie : None
        But : Gérer la fin de partie (enregistrer les scores et revenir au menu)
        """
        # Lecture des scores existants
        with open("score.csv", mode="r", encoding="utf-8") as fichier:
            reader = csv.reader(fichier)
            scores = [int(ligne[0]) for ligne in reader if ligne]
            scores.append(self.__score)
            if len(scores) > 10:
                scores = scores[-10:]  # conserve les 10 derniers scores

        # Réécriture du fichier
        with open("score.csv", mode="w", newline="", encoding="utf-8") as fichier:
            writer = csv.writer(fichier)
            for score in scores:
                writer.writerow([score])

        # Nettoyage de la fenêtre et retour au menu
        for i in self.__fenetre.winfo_children():
            i.destroy()
        Menu(self.__fenetre, etat)

    def update_loop(self):
        """
        Entrée : None
        Sortie : None
        But : boucle principale du jeu (rafraîchissement 60 FPS)
        """
        self.display_update()

        if self.__vies != 0 and self.__pause == 0:
            self.__raquette.update()
            rx1, ry1, rx2, ry2 = self.__raquette.coords()
            self.__ball.update()
            self.collisions()

            # Si la balle tombe sous la raquette
            if self.__ball._Ball__y > ry2:
                self.__canvas.delete(self.__liste_vies[0])
                self.__liste_vies.remove(self.__liste_vies[0])
                self.__vies = len(self.__liste_vies)
                self.__ball.reset_pos()

            # Conditions de fin
            if self.__vies == 0:
                self.end_game('You lost ! ( skill issue )')
            if len(self.__bricks) == 0:
                self.end_game('You won !')

            # Relance la boucle après 16 ms (≈ 60 FPS)
            self.__fenetre.after(16, self.update_loop)

    def display_update(self):
        """
        Entrée : None
        Sortie : None
        But : mettre à jour les affichages dynamiques (score)
        """
        self.__canvas.itemconfig(self.__score_text, text=f"Score: {self.__score}")

    def collisions(self):
        """
        Entrée : None
        Sortie : None
        But : gérer les collisions entre la balle, la raquette et les briques
        """
        bx1, by1, bx2, by2 = self.__ball.coords()
        cx = (bx1 + bx2) / 2  # centre X de la balle
        cy = (by1 + by2) / 2  # centre Y de la balle
        r = ball_r

        # --- Collision balle/raquette ---
        rx1, ry1, rx2, ry2 = self.__raquette.coords()
        if bx2 >= rx1 and bx1 <= rx2 and by2 >= ry1 and by1 <= ry2:
            overlap_x = min(rx2, bx2) - max(rx1, bx1)
            overlap_y = min(ry2, by2) - max(ry1, by1)

            # Inversion de direction selon le type de contact
            if overlap_x < overlap_y:
                self.__ball._Ball__dx = -self.__ball._Ball__dx
            else:
                self.__ball._Ball__dy = -self.__ball._Ball__dy

        # --- Collision balle/briques ---
        for brick in list(self.__bricks):
            x1, y1, x2, y2 = brick.coords()
            if bx2 >= x1 and bx1 <= x2 and by2 >= y1 and by1 <= y2:
                overlap_x = min(x2, bx2) - max(x1, bx1)
                overlap_y = min(y2, by2) - max(y1, by1)
                brick.hits -= 1  # réduit la résistance de la brique

                # Inversion de direction selon le côté touché
                if overlap_x < overlap_y:
                    self.__ball._Ball__dx = -self.__ball._Ball__dx
                else:
                    self.__ball._Ball__dy = -self.__ball._Ball__dy

                # Si la brique est détruite
                if brick.hits == 0:
                    self.__canvas.delete(brick.id)
                    self.__bricks.remove(brick)
                    self.__score += 10
                break  # on ne traite qu’une collision par frame

    def create_bricks(self):
        """
        Entrée : None
        Sortie : None
        But : créer la grille de briques en fonction de la difficulté
        """
        indice = 0
        colors = ['red', 'blue', 'green', 'spring green', 'gold', 'cyan', 'deep pink', 'magenta2', 'SlateBlue1']

        # Calcule le décalage pour centrer les briques
        start_x = (WINDOW_WIDTH - (BRICK_COLUMNS * BRICK_WIDTH + (BRICK_COLUMNS - 1) * BRICK_PADDING)) / 2
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLUMNS):
                x1 = start_x + col * (BRICK_WIDTH + BRICK_PADDING)
                y1 = TOP_OFFSET + row * (BRICK_HEIGHT + BRICK_PADDING)
                x2 = x1 + BRICK_WIDTH
                y2 = y1 + BRICK_HEIGHT
                brick = Brick(self.__canvas, x1, y1, x2, y2, color=colors[indice], hits=self.__hits)
                self.__bricks.append(brick)
                indice = (indice + 1) % len(colors)  # alterne les couleurs

    def game(self):
        """
        Entrée : None
        Sortie : None
        But : lancer la partie (création des briques, boucle du jeu)
        """
        self.create_bricks()
        self.update_loop()
        self.__canvas.pack()
        self.__fenetre.mainloop()


class Menu:
    """Classe d’affichage du menu principal (choix difficulté, lancement de partie, etc.)"""

    def __init__(self, root, etat):
        """
        Entrée :
            - root (tk.Tk) : fenêtre principale
            - etat (str) : message affiché ("You won", "You lost", etc.)
        Sortie : None
        But : créer le menu d’accueil du jeu
        """
        self.__window = root
        self.__photo = tk.PhotoImage(file='cassebrique.png')
        self.__largeur = self.__photo.width()
        self.__hauteur = self.__photo.height()
        self.__window.geometry(f"{self.__largeur}x{self.__hauteur}")
        self.__lbl = tk.Label(self.__window, image=self.__photo)
        self.__lbl.place(x=0, y=0, relwidth=1, relheight=1)
        self.__window.resizable(False, False)

        # Texte du message de fin
        self.__texte = tk.Label(self.__window, text=etat, bg='#f86a00', font=("Helvetica", 24),
                                fg='#00006c', justify='center')
        self.__texte.pack()

        # Boutons
        self.__difficulty = 1
        self.__boutton_jeu = tk.Button(self.__window, text='LANCER UNE PARTIE', fg='#00006c',
                                       width=18, height=2, background='#f86a00',
                                       highlightbackground='black', highlightthickness=2,
                                       command=self.lancerjeu)
        self.__boutton_jeu.place(x=self.__largeur*(2/5) - 190, y=self.__hauteur*(3/7))
        self.__boutton_jeu2 = tk.Button(self.__window, text='QUITTER', fg='#f86a00',
                                        width=6, height=1, background='#00006c',
                                        highlightbackground='black', highlightthickness=2,
                                        command=self.__window.destroy)

        # Boutons de difficulté
        self.__boutton_difficulty1 = tk.Button(self.__window, text='Difficulté 1', fg='#00006c',
                                               width=18, height=2, background='#f86a00',
                                               highlightbackground='black', highlightthickness=2,
                                               command=self.difficulty)
        self.__boutton_difficulty1.place(x=self.__largeur*(2/5) + 10, y=self.__hauteur*(3/7))

        self.__boutton_difficulty2 = tk.Button(self.__window, text='Difficulté 2', fg='#00006c',
                                               width=18, height=2, background='#f86a00',
                                               highlightbackground='black', highlightthickness=2,
                                               command=self.difficulty2)
        self.__boutton_difficulty2.place(x=self.__largeur*(2/5) + 210, y=self.__hauteur*(3/7))
        self.__boutton_jeu2.place(x=10, y=self.__hauteur - 30)
        self.__window.bind('<o>', self.regles)

        # Affichage des scores
        self.__liste_score = self.get_score()
        self.__texte_score = '/'.join(map(str, self.__liste_score))
        self.__scores = tk.Label(self.__window,
                                 text=f"derniers scores:{self.__texte_score}",
                                 bg='#f86a00', font=("Helvetica", 14),
                                 fg='#00006c', justify='center')
        self.__scores.place(x=self.__largeur/2 - 200, y=self.__hauteur-30)
        self.__window.mainloop()

    def regles(self, event=None):
        """
        Entrée : event (optionnel)
        Sortie : None
        But : afficher une fenêtre avec les règles du jeu
        """
        f_regles = tk.Toplevel()
        meme = tk.PhotoImage(file='johnpork.png')
        f_regles.geometry(f"{meme.width()}x{meme.height()}")
        label = tk.Label(f_regles, image=meme)
        label.pack()
        f_regles.mainloop()

    def difficulty(self):
        """Entrée/Sortie : None | But : définir la difficulté sur 1"""
        self.__difficulty = 1

    def difficulty2(self):
        """Entrée/Sortie : None | But : définir la difficulté sur 2"""
        self.__difficulty = 2

    def lancerjeu(self):
        """
        Entrée : None
        Sortie : None
        But : lancer la partie avec la difficulté choisie
        """
        self.__fenetre = Fenetre(self.__window, self.__difficulty)
        self.__fenetre.game()

    def get_score(self):
        """
        Entrée : None
        Sortie : list[int]
        But : lire les 10 derniers scores depuis le fichier CSV
        """
        with open("score.csv", mode="r", encoding="utf-8") as fichier:
            reader = csv.reader(fichier)
            scores = [int(ligne[0]) for ligne in reader if ligne]
            if len(scores) > 10:
                scores = scores[-10:]
        return scores


if __name__ == "__main__":
    """Point d’entrée du programme"""
    root = tk.Tk()
    Menu(root, None)




