import pygame
from ..ui.button import Button
from manual.assets.assets import load_asset

class MenuScreen:
    def __init__(self, goto_arena, goto_shop):
        self.elements = []

    def handle_event(self, e):
        for el in self.elements: el.handle_event(e)
    def update(self, dt):
        for el in self.elements: el.update(dt)
    def draw(self, surf):
        surf.fill((10,10,30))
        for el in self.elements: el.draw(surf)
