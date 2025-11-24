import pygame, os
from ..ui.button import Button
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory import inventory

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "PublicPixel.ttf"), 20)

class MenuScreen:
    def __init__(self, goto_arena, goto_shop, goto_deckbuilder):
        self.elements = []
        self.goto_arena = goto_arena
        self.goto_shop = goto_shop
        self.goto_deckbuilder = goto_deckbuilder
        
        self.bg = load_asset("bg.png", "configure") # Reusing bg
        
        # Deck Builder Button
        self.elements.append(Button(
            (50, 300, 300, 60), # Moved to left
            self.goto_deckbuilder,
            None,
            text="Pakli összeállítása",
            font=BP,
            text_color=(255, 255, 255)
        ))
        
        # New Fight Button (Bottom Right)
        self.fight_btn = Button(
            (1280 - 250, 720 - 100, 200, 60),
            self.try_goto_arena,
            None,
            text="Új harc",
            font=BP,
            text_color=(255, 255, 255)
        )
        self.elements.append(self.fight_btn)

    def try_goto_arena(self):
        if len(inventory.PLAYERDECK) > 0:
            self.goto_arena()

    def handle_event(self, e):
        for el in self.elements: el.handle_event(e)
        
    def update(self, dt):
        # Update Fight Button State
        if len(inventory.PLAYERDECK) > 0:
            self.fight_btn.text_color = (255, 255, 255) # Enabled color
        else:
            self.fight_btn.text_color = (100, 100, 100) # Disabled color
            
        for el in self.elements: el.update(dt)
        
    def draw(self, surf):
        surf.blit(self.bg, (0,0))
        
        # Draw button backgrounds manually since we passed None image
        for el in self.elements:
            if isinstance(el, Button) and el.normal_image is None:
                color = (50, 50, 150)
                if el == self.fight_btn and len(inventory.PLAYERDECK) == 0:
                    color = (50, 50, 50) # Disabled bg
                pygame.draw.rect(surf, color, el.rect, border_radius=10)
                pygame.draw.rect(surf, (200, 200, 200), el.rect, 2, border_radius=10)
                
            el.draw(surf)
