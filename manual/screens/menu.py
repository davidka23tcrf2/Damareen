import pygame
from ..ui.button import Button

class MenuScreen:
    def __init__(self, goto_arena, goto_shop):
        self.elements = []
        self.elements.append(Button((540,280,200,64),"Start Arena", goto_arena))
        self.elements.append(Button((540,360,200,64),"Open Shop", goto_shop))
    def handle_event(self, e):
        for el in self.elements: el.handle_event(e)
    def update(self, dt):
        for el in self.elements: el.update(dt)
    def draw(self, surf):
        surf.fill((10,10,30))
        for el in self.elements: el.draw(surf)
