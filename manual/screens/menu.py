import pygame
from ..ui.button import Button
from manual.assets.assets import load_asset

class MenuScreen:
    def __init__(self, goto_arena, goto_shop):
        self.elements = []
        # Load button images

<<<<<<< HEAD
        # Buttons
        self.elements.append(Button((400, 200, 200, 50), goto_shop,
                                    normal_btn_img, hover_btn_img))
=======
>>>>>>> 1f0f6d36b5c56be8b3f56db7bac76b869d145dcc
    def handle_event(self, e):
        for el in self.elements: el.handle_event(e)
    def update(self, dt):
        for el in self.elements: el.update(dt)
    def draw(self, surf):
        surf.fill((10,10,30))
        for el in self.elements: el.draw(surf)
