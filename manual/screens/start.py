from manual.ui.button import Button
from manual.ui.label import Label
from manual.assets.assets import load_asset
from manual.assets.assets import ASSETS_DIR
import os, pygame

pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "PublicPixel.ttf"), 13)
class StartScreen:
    def __init__(self, config, load_game):
        self.elements = []

        self.BG = load_asset("startbg.png", "start")

        # Load button images
        btn = load_asset("button.png", "start")
        btnhover = load_asset("buttonhover.png", "start")

        # Buttons
        self.elements.append(Button((0, 300, 350, 125), load_game,btn, btnhover, "Környezet betöltése", font=BP, center_x=True))
        self.elements.append(Button((0, 450, 350, 125), config,btn, btnhover, "Környezet konfigurálása", font=BP, center_x=True))

        # Labels
        self.title = Label((400, 50, 200, 50), "Damareen", font_size=40)

    def handle_event(self, e):
        for el in self.elements:
            el.handle_event(e)

    def update(self, dt):
        for el in self.elements:
            el.update(dt)

    def draw(self, surf):
        surf.blit(self.BG, (0, 0))
        for el in self.elements:
            el.draw(surf)
