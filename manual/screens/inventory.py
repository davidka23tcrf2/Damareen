
import pygame, os
from ..ui.button import Button
from ..ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR


BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 80)
class InventoryScreen:
    def __init__(self, goto_shop):
        self.bg = load_asset("bg.png", "inventory")
        self.elements = []
        Inventtory = Label(rect=(600, 50, 100, 100), text="Inventory", font=BP)
        self.elements.append(Inventtory)

    def CreateItemSlot(self, surface, color, start, end, thickness=1, fill_color=None):
        x1, y1 = start
        x2, y2 = end

        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)

        pygame.draw.line(surface, color, (left, top), (right, top), thickness)
        pygame.draw.line(surface, color, (right, top), (right, bottom), thickness)
        pygame.draw.line(surface, color, (right, bottom), (left, bottom), thickness)
        pygame.draw.line(surface, color, (left, bottom), (left, top), thickness)

        if fill_color is None:
            fill_color = color

        inner_left = left + thickness
        inner_top = top + thickness
        inner_width = (right - left) - thickness * 2
        inner_height = (bottom - top) - thickness * 2

        if inner_width > 0 and inner_height > 0:
            pygame.draw.rect(surface, fill_color,
                             (inner_left, inner_top, inner_width, inner_height))
    def handle_event(self, e):
        for el in self.elements: el.handle_event(e)

    def update(self, dt):
        for el in self.elements: el.update(dt)

    def draw(self, surf):
        surf.blit(self.bg, (0,0))
        self.CreateItemSlot(surf,
                            color=(255, 255, 255),  # keret színe
                            start=(900, 200),
                            end=(950, 250),
                            thickness=2,
                            fill_color=(220, 220, 220))



        for el in self.elements: el.draw(surf)
