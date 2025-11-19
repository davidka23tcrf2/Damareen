import pygame
from ..ui.button import Button
from ..ui.label import Label

class ShopScreen:
    def __init__(self, goto_arena, state):
        self.elements = []
        self.state = state
        self.elements.append(Button((980,600,220,48), "Back", goto_arena))
        self.elements.append(Label((980,20,220,32), f"Currency: {self.state.get('currency',0)}"))
    def handle_event(self, e):
        for el in self.elements: el.handle_event(e)
    def update(self, dt):
        for el in self.elements: el.update(dt)
    def draw(self, surf):
        surf.fill((30,20,40))
        for el in self.elements: el.draw(surf)
