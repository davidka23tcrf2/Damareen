from manual.assets.assets import load_asset
from manual.ui.button import Button
from manual.saving import load
from manual.assets.assets import ASSETS_DIR
import os, pygame

pygame.init()

sf = "gameloader"
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "PublicPixel.ttf"), 12)

class GameLoader:
    def __init__(self, goto_menu, goto_start):
        self.elements = []
        self.goto_menu = goto_menu

        self.bg = load_asset("bg.png", sf)
        back = load_asset("backbutton.png", sf)
        self.save_img = load_asset("save.png", sf)

        self.elements.append(Button((0, 0, 100, 100), goto_start, back))
        
        self.save_buttons = []
        self.reload_saves()

    def reload_saves(self):
        self.save_buttons = []
        saves = load.get_save_files()

        start_y = 150  # top margin
        cols = 6  # max number of columns per row
        x_spacing = 50  # horizontal spacing between buttons
        y_spacing = 50  # vertical spacing between buttons
        button_width, button_height = 144, 182

        for row_index, row_start in enumerate(range(0, len(saves), cols)):
            row_saves = saves[row_start:row_start + cols]
            num_in_row = len(row_saves)

            total_width = num_in_row * button_width + (num_in_row - 1) * x_spacing
            start_x = (1280 - total_width) // 2

            for col_index, s in enumerate(row_saves):
                save_num = s["save_num"]
                cards = s["cards"]
                enemies = s["enemies"]
                filename = s["file"]

                text = f"Környezet {save_num}\n\n\n{cards} Kártya\n\n\n{enemies} Kazamata"

                x = start_x + col_index * (button_width + x_spacing)
                y = start_y + row_index * (button_height + y_spacing)

                def make_load_callback(path=filename):
                    return lambda: self.load_and_go(path)

                btn = Button(
                    (x, y, button_width, button_height),
                    make_load_callback(),
                    self.save_img,
                    text=text,
                    font=BP,
                    text_color=(0, 0, 0)
                )
                self.save_buttons.append(btn)

    def load_and_go(self, filepath):
        load.load_game(filepath)
        self.goto_menu()

    def handle_event(self, e):
        for el in self.elements + self.save_buttons:
            el.handle_event(e)

    def update(self, dt):
        for el in self.elements + self.save_buttons:
            el.update(dt)

    def draw(self, surf):
        surf.blit(self.bg, (0, 0))
        for el in self.elements + self.save_buttons:
            el.draw(surf)
