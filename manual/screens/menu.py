import pygame
from ..ui.button import Button
from manual.assets.assets import load_asset

class MenuScreen:
    def __init__(self, goto_arena, goto_shop):
        self.elements = []
        # Load button images
        normal_btn_img = load_asset("button.png")
        hover_btn_img = load_asset("button.png")

        # Buttons
        self.elements.append(Button((400, 200, 200, 50), goto_shop,
                                    normal_btn_img, hover_btn_img))
    def handle_event(self, e):
        for el in self.elements: el.handle_event(e)
    def update(self, dt):
        for el in self.elements: el.update(dt)
    def draw(self, surf):
        surf.fill((10,10,30))
        for el in self.elements: el.draw(surf)
