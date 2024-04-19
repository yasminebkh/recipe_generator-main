import random
import string
from io import BytesIO
from PIL import Image, ImageTk, ImageOps
import requests
import tkinter as tk
import threading

WINDOW_TITLE = "Recipe App"
RECIPE_IMAGE_WIDTH = 150
RECIPE_IMAGE_HEIGHT = 150
DEFAULT_IMAGE_URL = "https://www.mageworx.com/blog/wp-content/uploads/2012/06/Page-Not-Found-13.jpg"


class RecipeApp(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.window = tk.Tk()
        self.window.geometry("")
        self.window.configure(bg="#FDF7E4")
        self.window.title(WINDOW_TITLE)

        self.waiting_label = tk.Label(self.window, text="", font=("Times New Roman", 14, "bold"))
        self.waiting_label.grid(row=2, column=0, columnspan=3, pady=10, sticky="nsew")

        self.search_label = tk.Label(self.window, text="Search Recipe", bg="#ea86b6", font=("Times New Roman", 14))
        self.search_label.grid(column=0, row=0, padx=5)

        self.search_entry = tk.Entry(master=self.window, width=40, font=("Times New Roman", 14))
        self.search_entry.grid(column=1, row=0, padx=5, pady=10)

        self.search_button = tk.Button(self.window, text="Search", highlightbackground="#ea86b6",
                                       command=self._run_search_query, font=("Times New Roman", 14))
        self.search_button.grid(column=2, row=0, padx=5)


        #est une zone rectangulaire sur laquelle vous pouvez dessiner des formes, du texte et placer des images.
        # C'est une surface où vous pouvez créer des éléments graphiques de manière dynamique ou statique.
        # Create a Canvas widget for scrolling
        self.canvas = tk.Canvas(self.window)
        self.canvas.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Create a frame inside the canvas to hold the content
        self.result_frame = tk.Frame(self.canvas, bg="#ffffff")
        self.canvas.create_window((0, 0), window=self.result_frame, anchor="center")

        # Create a vertical scrollbar linked to the canvas
        self.scrollbar = tk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=1, column=3, sticky="ns")
        self.result_frame.grid_columnconfigure(3, weight=1)

        ###############

        # Configure the canvas to scroll vertically
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.default_image = Image.open(BytesIO(requests.get(DEFAULT_IMAGE_URL).content))

        # Set row and column weights to allow expansion
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_columnconfigure(2, weight=1)


        self.loading_color = "#F11A7B"  # Couleur de chargement

        # Styliser le message de chargement
        self.waiting_label.configure(font=("Arial", 16, "italic"), fg=self.loading_color)


    def _run_search_query(self):
        # Afficher un message de chargement
        self.waiting_label.config(text="Loading...", font=("Times New Roman", 16, "italic"))
        # Afficher un message de chargement stylisé et animé
        self.animate_loading()
        #query = self.search_entry.get()
        # Run the search query in a separate thread
        search_thread = threading.Thread(target=self._run_search_query_background)
        search_thread.start()
        #recipes = self.trouver_recette([query])
        #if recipes:
        #    self.afficher_recettes(recipes)

    def _update_gui(self, recipes):
        # Masquez le message d'attente
        self.waiting_label.config(text="")
        #This will update the display of windows but not process events caused by the user.
        self.window.update_idletasks()
        # Display the recipes
        if recipes:
            # Masquer le message d'attente
            self.waiting_label.config(text="recipes found", font=("Times New Roman", 16, "italic"))
        else:
            # Afficher un message si aucune recette n'est trouvée
            self.waiting_label.config(text="No recipes found.", font=("Times New Roman", 16, "italic"))

    def _run_search_query_background(self):
        query = self.search_entry.get()
        recipes = self.trouver_recette([query])
        if recipes:
            self.afficher_recettes(recipes)
        self.window.after(0, lambda: self._update_gui(recipes))


    def toggle_loading_color(self):
        # Alternance de couleurs pour créer un effet de clignotement
        if self.loading_color == "#F11A7B":
            self.loading_color = "#3E001F"
        else:
            self.loading_color = "#F11A7B"
        # Appliquer la nouvelle couleur au label de chargement
        self.waiting_label.config(fg=self.loading_color)
        # Continuer l'animation
        self.animate_loading()

    def animate_loading(self):
        # Changer la couleur du texte de chargement de façon clignotante
        self.waiting_label.after(500, self.toggle_loading_color)


    def trouver_recette(self, ingredients):
        base_url = 'https://api.spoonacular.com/recipes/findByIngredients'
        ingr_string = ','.join(ingredients)
        params = {
            'ingredients': ingr_string,
            'apiKey': self.api_key,
            'number': 6,
            'random': ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            # Append a random query string
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            recettes = response.json()
            return recettes
        else:
            return None

    def afficher_recettes(self, recettes):
        if recettes:
            print("Recettes trouvées:")
            for idx, recette in enumerate(recettes):
                title = recette.get('title')
                title_label = tk.Label(self.result_frame, text=title, bg="#ffffff",font=("Times New Roman", 14, "bold"))
                title_label.grid(row=idx, column=0, sticky='w', ipadx=10,ipady=10)  # Ajoutez ipadx et ipady pour le centrage
                image_url = recette.get('image')
                try:
                    response = requests.get(image_url)
                    img = Image.open(BytesIO(response.content))
                    border_size = 10
                    img_with_border = ImageOps.expand(img, border=border_size, fill='gray')
                except Exception as e:
                    print(f"Erreur lors du chargement de l'image : {e}")
                    img_with_border = ImageOps.expand(self.default_image, border=border_size, fill='gray')

                img = img.resize((RECIPE_IMAGE_WIDTH * 2, RECIPE_IMAGE_HEIGHT * 2))
                photo = ImageTk.PhotoImage(img_with_border)
                img_label = tk.Label(self.result_frame, image=photo, bg="#ffffff")
                img_label.image = photo
                img_label.grid(row=idx, column=1, sticky='nsew', ipadx=10,ipady=10)  # Ajoutez ipadx et ipady pour le centrage

                missed_ingredient_count = recette.get('missedIngredientCount')
                missing_ingredients = recette.get('missedIngredients')
                if missed_ingredient_count:
                    info_text = f"Missing Ingredients: {missed_ingredient_count}\n"
                    for ingredient in missing_ingredients:
                        info_text += f"- {ingredient.get('name')}\n"
                    info_label = tk.Label(self.result_frame, text=info_text, bg="#ffffff", justify='left',font=("Times New Roman", 14, "bold"))
                    info_label.grid(row=idx, column=2, sticky='w', ipadx=10,ipady=10)  # Ajoutez ipadx et ipady pour le centrage

                    title_label.configure(bg="#ffffff")
                    img_label.configure(bg="#ffffff")

                    # Set row weights for the result_frame to allow expansion
                    self.result_frame.grid_rowconfigure(idx, weight=1)
                    self.result_frame.grid_rowconfigure(idx + 1, weight=1)
                    self.result_frame.grid_rowconfigure(idx + 2, weight=1)

                # Set row weights for the result_frame to allow expansion
                # self.result_frame.grid_rowconfigure(idx, weight=1)

                # Set column weights for the result_frame to allow expansion
                self.result_frame.grid_columnconfigure(0, weight=1)
                self.result_frame.grid_columnconfigure(1, weight=1)
                self.result_frame.grid_columnconfigure(2, weight=1)
                self.result_frame.grid_columnconfigure(3, weight=1)

                info_label.configure(bg="#ffffff")
                #Cela mettra à jour l'affichage des fenêtres mais ne traitera pas les événements provoqués par l'utilisateur.
                self.canvas.update_idletasks()
                # Cela signifie que lorsque vous faites défiler le contenu du canevas, la zone visible sera limitée à la région définie par la boîte englobante calculée, et le défilement sera activé si les éléments dépassent cette région.
                self.canvas.config(scrollregion=self.canvas.bbox("all"))
            else:
                print("Aucune recette trouvée.")

    def run_app(self):
        self.window.mainloop()


if __name__ == "__main__":
    APP_KEY = "6eaa8fdb6e0d496fb8cbdaf2e4248f52"

    recipe_app = RecipeApp(APP_KEY)
    recipe_app.run_app()