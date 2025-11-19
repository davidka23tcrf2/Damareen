import pygame
from ..ui.button import Button

class ArenaScreen:
    def __init__(self, goto_shop, state):
        self.elements = []
        self.state = state
    def handle_event(self, e):
        for el in self.elements: el.handle_event(e)
    def update(self, dt):
        for el in self.elements: el.update(dt)
    def draw(self, surf):
        surf.fill((20,40,20))
        for el in self.elements: el.draw(surf)
