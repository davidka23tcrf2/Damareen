import pygame
from manual.ui.button import Button
from manual.ui.label import Label

class CONFIGURE:
    def __init__(self, goto_menu):
        self.elements = []

        self.title = Label((540, 100, 200, 50), "Configure a new game env", font_size=48)

        # Simple start button to go to menu
        normal_img = pygame.Surface((200, 50))
        normal_img.fill((100,100,250))
        hover_img = pygame.Surface((200, 50))
        hover_img.fill((150,150,255))

        self.elements.append(
            Button((540, 300, 200, 50), goto_menu, normal_img, hover_img)
        )

    def handle_event(self, e):
        for el in self.elements:
            el.handle_event(e)

    def update(self, dt):
        for el in self.elements:
            el.update(dt)

    def draw(self, surf):
        surf.fill((30,30,30))
        self.title.draw(surf)
        for el in self.elements:
            el.draw(surf)
