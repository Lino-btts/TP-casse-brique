# codé en utf 8
# Date : du 06/10/2025 au 27/10/2025 
# Auteurs : Rayane Chekatt / Lino Battesti
# Le programme permet de créer la fenetre du jeu et de gérer la difficulté, les vies, le scores, 
# la possibilité de mettre en pause et la fin de partie.
# To do list : None


from tkinter import Tk, Canvas, Label, Button, PhotoImage, Toplevel
from csv import reader, writer
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
            - window (Tk) : fenêtre principale
            - difficulte (int) : nombre de coups nécessaires pour casser une brique
        Sortie : None
        """
        self.__INITIAL_LIVES = 3
        self.__score = 0
        self.__pause = 1
        self.__hits = difficulte

        # --- Création de la fenêtre ---
        self.__fenetre = window
        for i in self.__fenetre.winfo_children():
            i.destroy()  # supprime les widgets précédents (utile au retour au menu)

        self.__fenetre.title('Casse brique')
        self.__fenetre.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')

        # --- Canvas principal ---
        self.__canvas = Canvas(
            self.__fenetre,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bd=0,
            highlightthickness=0,
            background='black'
        )

        # --- Vies ---
        self.__liste_vies = [
            self.__canvas.create_oval(710 + 30 * i, 10, 730 + 30 * i, 30, width=5, fill='pink')
            for i in range(3)
        ]
        self.__vies = len(self.__liste_vies)

        # --- Score ---
        self.__score_text = self.__canvas.create_text(
            10, 10, anchor="nw", font=("Helvetica", 14),
            text=f"Score: {self.__score}", fill='white'
        )

        # --- Objets du jeu ---
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
        """Met le jeu en pause ou le relance."""
        self.__pause = 0 if self.__pause == 1 else 1
        self.update_loop()

    def end_game(self, etat):
        """Gère la fin de partie (enregistre le score et revient au menu)."""
        with open("score.csv", mode="r", encoding="utf-8") as fichier:
            scores = [int(ligne[0]) for ligne in reader(fichier) if ligne]
            scores.append(self.__score)
            if len(scores) > 10:
                scores = scores[-10:]

        with open("score.csv", mode="w", newline="", encoding="utf-8") as fichier:
            w = writer(fichier)
            for score in scores:
                w.writerow([score])

        for i in self.__fenetre.winfo_children():
            i.destroy()
        Menu(self.__fenetre, etat)

    def update_loop(self):
        """Boucle principale du jeu (≈60 FPS)."""
        self.display_update()

        if self.__vies != 0 and self.__pause == 0:
            self.__raquette.update()
            self.__ball.update()
            self.collisions()

            # Si la balle tombe sous la raquette
            if self.__ball._Ball__y > WINDOW_HEIGHT - PADDLE_Y_OFFSET + 10:
                self.__canvas.delete(self.__liste_vies[0])
                self.__liste_vies.pop(0)
                self.__vies = len(self.__liste_vies)
                self.__ball.reset_pos()

            # Conditions de fin
            if self.__vies == 0:
                self.end_game('You lost ! ( skill issue )')
            if not self.__bricks:
                self.end_game('You won !')

            self.__fenetre.after(16, self.update_loop)

    def display_update(self):
        """Met à jour les éléments affichés (score, etc.)."""
        self.__canvas.itemconfig(self.__score_text, text=f"Score: {self.__score}")

    def collisions(self):
        """Gère les collisions entre balle, raquette et briques."""
        bx1, by1, bx2, by2 = self.__ball.coords()

        # --- Raquette ---
        rx1, ry1, rx2, ry2 = self.__raquette.coords()
        if bx2 >= rx1 and bx1 <= rx2 and by2 >= ry1 and by1 <= ry2:
            overlap_x = min(rx2, bx2) - max(rx1, bx1)
            overlap_y = min(ry2, by2) - max(ry1, by1)
            if overlap_x < overlap_y:
                self.__ball._Ball__dx = -self.__ball._Ball__dx
            else:
                self.__ball._Ball__dy = -self.__ball._Ball__dy

        # --- Briques ---
        for brick in list(self.__bricks):
            x1, y1, x2, y2 = brick.coords()
            if bx2 >= x1 and bx1 <= x2 and by2 >= y1 and by1 <= y2:
                overlap_x = min(x2, bx2) - max(x1, bx1)
                overlap_y = min(y2, by2) - max(y1, by1)
                brick.hits -= 1

                if overlap_x < overlap_y:
                    self.__ball._Ball__dx = -self.__ball._Ball__dx
                else:
                    self.__ball._Ball__dy = -self.__ball._Ball__dy

                if brick.hits == 0:
                    self.__canvas.delete(brick.id)
                    self.__bricks.remove(brick)
                    self.__score += 10
                break

    def create_bricks(self):
        """Crée la grille de briques en fonction de la difficulté."""
        colors = ['red', 'blue', 'green', 'spring green', 'gold',
                  'cyan', 'deep pink', 'magenta2', 'SlateBlue1']
        start_x = (WINDOW_WIDTH - (BRICK_COLUMNS * BRICK_WIDTH + (BRICK_COLUMNS - 1) * BRICK_PADDING)) / 2
        color_idx = 0

        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLUMNS):
                x1 = start_x + col * (BRICK_WIDTH + BRICK_PADDING)
                y1 = TOP_OFFSET + row * (BRICK_HEIGHT + BRICK_PADDING)
                x2 = x1 + BRICK_WIDTH
                y2 = y1 + BRICK_HEIGHT
                brick = Brick(self.__canvas, x1, y1, x2, y2,
                              color=colors[color_idx], hits=self.__hits)
                self.__bricks.append(brick)
                color_idx = (color_idx + 1) % len(colors)

    def game(self):
        """Lance la partie."""
        self.create_bricks()
        self.update_loop()
        self.__canvas.pack()
        self.__fenetre.mainloop()


class Menu:
    """Classe du menu principal (choix difficulté, lancement, etc.)."""

    def __init__(self, root, etat):
        self.__window = root
        self.__photo = PhotoImage(file='cassebrique.png')
        self.__largeur = self.__photo.width()
        self.__hauteur = self.__photo.height()
        self.__window.geometry(f"{self.__largeur}x{self.__hauteur}")
        self.__lbl = Label(self.__window, image=self.__photo)
        self.__lbl.place(x=0, y=0, relwidth=1, relheight=1)
        self.__window.resizable(False, False)

        self.__texte = Label(
            self.__window, text=etat, bg='#f86a00',
            font=("Helvetica", 24), fg='#00006c', justify='center'
        )
        self.__texte.pack()

        # --- Boutons ---
        self.__difficulty = 1
        Button(
            self.__window, text='LANCER UNE PARTIE', fg='#00006c',
            width=18, height=2, background='#f86a00',
            highlightbackground='black', highlightthickness=2,
            command=self.lancerjeu
        ).place(x=self.__largeur * (2 / 5) - 190, y=self.__hauteur * (3 / 7))

        Button(
            self.__window, text='QUITTER', fg='#f86a00',
            width=6, height=1, background='#00006c',
            highlightbackground='black', highlightthickness=2,
            command=self.__window.destroy
        ).place(x=10, y=self.__hauteur - 30)

        Button(
            self.__window, text='Difficulté 1', fg='#00006c',
            width=18, height=2, background='#f86a00',
            highlightbackground='black', highlightthickness=2,
            command=self.difficulty
        ).place(x=self.__largeur * (2 / 5) + 10, y=self.__hauteur * (3 / 7))

        Button(
            self.__window, text='Difficulté 2', fg='#00006c',
            width=18, height=2, background='#f86a00',
            highlightbackground='black', highlightthickness=2,
            command=self.difficulty2
        ).place(x=self.__largeur * (2 / 5) + 210, y=self.__hauteur * (3 / 7))


        # --- Affichage des scores ---
        self.__liste_score = self.get_score()
        texte_score = '/'.join(map(str, self.__liste_score))
        Label(
            self.__window, text=f"derniers scores: {texte_score}",
            bg='#f86a00', font=("Helvetica", 14),
            fg='#00006c', justify='center'
        ).place(x=self.__largeur / 2 - 200, y=self.__hauteur - 30)
        self.__window.bind('<o>',self.regles)
        self.__window.mainloop()

    def difficulty(self):
        """Définit la difficulté à 1."""
        self.__difficulty = 1

    def difficulty2(self):
        """Définit la difficulté à 2."""
        self.__difficulty = 2

    def lancerjeu(self):
        """Lance la partie avec la difficulté choisie."""
        fen = Fenetre(self.__window, self.__difficulty)
        fen.game()
        
    def regles(self, event = None):
        f_regles = Toplevel()
        meme = PhotoImage(file ='emoji.png')
        f_regles.geometry(f"{meme.width()}x{meme.height()}")
        label= Label(f_regles,image = meme)
        #label.place(x=0, y=0, relwidth=1, relheight=1)
        label.pack()
        f_regles.mainloop()
        
    def get_score(self):
        """Lit les 10 derniers scores depuis le fichier CSV."""
        with open("score.csv", mode="r", encoding="utf-8") as fichier:
            data = [int(ligne[0]) for ligne in reader(fichier) if ligne]
            return data[-10:] if len(data) > 10 else data


if __name__ == "__main__":
    """Point d'entrée du programme"""
    root = Tk()
    Menu(root, None)


