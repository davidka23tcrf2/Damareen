import pygame
from manual.ui.button import Button
from manual.ui.label import Label
from manual.assets.assets import load_asset

class StartScreen:
    def __init__(self, start_new_game, load_game):
        self.elements = []

        # Load button images
        normal_btn_img = load_asset("button.png")
        hover_btn_img = load_asset("button.png")

        # Buttons
        self.elements.append(Button((400, 200, 200, 50), start_new_game,
                                    normal_btn_img, hover_btn_img))
        self.elements.append(Button((400, 300, 200, 50), load_game,
                                    normal_btn_img, hover_btn_img))

        # Labels
        self.title = Label((400, 50, 200, 50), "My Game", font_size=40)

    def handle_event(self, e):
        for el in self.elements:
            el.handle_event(e)

    def update(self, dt):
        for el in self.elements:
            el.update(dt)

    def draw(self, surf):
        surf.fill((30, 20, 40))
        self.title.draw(surf)
        for el in self.elements:
            el.draw(surf)
