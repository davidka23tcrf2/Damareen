import pygame, os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.ui.switch import Switch
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory import inventory

from manual.screens.configurepopups.newcard import CardPopup  # import popup here

pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "PublicPixel.ttf"), 20)
sf = "configure"


class CONFIGURE:
    def __init__(self, goto_start, goto_menu):
        self.elements = []

        back = load_asset("backbutton.png", sf)
        self.paper = load_asset("paper.png", sf)
        self.paper = pygame.transform.scale(self.paper, (1000, 720))
        self.bg = load_asset("bg.png", sf)

        self.elements.append(Label((250, 70, 0, 0), "Bolt:", font=BP))
        self.elements.append(Label((750, 70, 0, 0), "Új kártya létrehozása", font=BP))

        self.switch = Switch((325, 50, 120, 50), callback=self.on_toggle, initial=False)

        self.elements.append(Button((0, 0, 100, 100), goto_start, back))

        # Button to open the popup
        popup_icon = load_asset("new.png", sf)
        self.elements.append(Button((975, 35, 75, 75), self.toggle_popup, popup_icon, image_offset=(-13, -11)))

        self.card_popup = None

    def on_toggle(self):
        inventory.SHOP_ENABLED = not inventory.SHOP_ENABLED

    def toggle_popup(self):
        if self.card_popup:
            if self.card_popup.is_closed():
                # Reopen the popup if it was closed
                self.card_popup.reopen()
            else:
                # Otherwise, close it
                self.card_popup.close()
        else:
            # Otherwise, create a new popup
            self.card_popup = CardPopup(close_callback=self.toggle_popup)

    def handle_event(self, e):
        # If popup exists and is active, let it handle events first
        if self.card_popup and getattr(self.card_popup, "active", False):
            handled = self.card_popup.handle_event(e)
            if handled:
                return  # Block event from going to other elements

        # Otherwise handle elements normally
        for el in self.elements:
            el.handle_event(e)
        self.switch.handle_event(e)

    def update(self, dt):
        # If popup exists and is active, only update the popup
        if self.card_popup and getattr(self.card_popup, "active", False):
            self.card_popup.update(dt)
            if getattr(self.card_popup, "closing", False) and self.card_popup.is_closed():
                self.card_popup = None
        else:
            # No active popup, update normal UI
            for el in self.elements:
                el.update(dt)
            self.switch.update(dt)

    def draw(self, surf):
        surf.blit(self.bg, (0, 0))
        surf.blit(self.paper, (140, 0))

        for el in self.elements:
            el.draw(surf)
        self.switch.draw(surf)

        if self.card_popup:
            self.card_popup.draw(surf)
