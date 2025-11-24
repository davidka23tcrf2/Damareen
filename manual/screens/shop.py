import random
import pygame, os
from ..ui.button import Button
from ..ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory.inventory import ARMOR
from manual.ui.particles import ParticleManager
from manual.ui.vignette import create_red_vignette
import math
import manual.mainloop

<<<<<<< Updated upstream
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 30)
=======

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 30)



>>>>>>> Stashed changes

class ShopScreen:
    def __init__(self, goto_arena):
        self.InfoPanel = False
        self.randnum = random.randint(0, len(ARMOR) - 1)
        self.randnum1 = random.randint(0, len(ARMOR) - 1)
        self.RandPercent = random.randint(10, 25)
        self.RandPercent1 = random.randint(10, 25)

        self.elements = []
        self.item_slots = []
        self.item_labels = []
        self.mx, self.my = pygame.mouse.get_pos()
        self.info = load_asset("info.png", "shop")
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        
        # Red vignette and particles
        self.particles = ParticleManager(mode="blood")
        self.vignette = create_red_vignette()
        
=======
        # Removed background image for black background
>>>>>>> Stashed changes
=======
        # Removed background image for black background
>>>>>>> Stashed changes
        normal = load_asset("armors.png", "shop")
        ExitMenu = load_asset("BackMenu.png", "shop")

        self.LittleInfo = Label(rect=(900, 650, 1, 1), text='Ahhoz, hogy vasarolj kattints ra a tablara \\n ahhoz, hogy meznezd az informaciokat vidd a kurzort a targyak ikonjara.', font=BP, color=(255, 255, 255))

        self.item_img = load_asset("itemstable.png", "shop")
        self.iw = int(self.item_img.get_width() * 0.25)
        self.ih = int(self.item_img.get_height() * 0.25)

        self.item_img = pygame.transform.scale(self.item_img, (self.iw, self.ih))
        self.item_pos = (200, 200)

        self.ThePanel = False

        w = int(normal.get_width() * 0.25)
        h = int(normal.get_height() * 0.25)
        normal_small = pygame.transform.scale(normal, (w, h))
        ExitMenuS = pygame.transform.scale(ExitMenu, (w, h))

        hover_small = normal_small

        Armors = Button(
            rect=(200, 1, w, h-40),
            callback=self.OpenMarket,
            normal_image=normal_small,
            hover_image=hover_small
        )

        ExitButton = Button(
            rect=(1050, 1, w-60, h-100),
            callback=lambda: manual.mainloop.ui.set("START"),
            normal_image=ExitMenuS,
            hover_image=ExitMenuS,
            image_offset=(-35, -50)
        )

        self.elements.append(ExitButton)
        self.elements.append(Armors)

    def handle_event(self, e):
        for el in self.elements:
            el.handle_event(e)

    def update(self, dt):
        self.particles.update(dt)
        for el in self.elements:
            el.update(dt)

    def draw(self, surf):
<<<<<<< Updated upstream
        surf.fill((0, 0, 0))  # Black background
        
        # Draw particles
        self.particles.draw(surf)
        
        # Draw vignette
        surf.blit(self.vignette, (0, 0))
        
        self.elements.append(self.LittleInfo)
=======


        surf.fill((0, 0, 0))  # Black background
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

        if self.InfoPanel:
            surf.blit(self.info, (410.5, 100))
            self.info = pygame.transform.scale(self.info, (500, 500))

        for el in self.elements:
            el.draw(surf)

    def CreateInfoPanel(self, num, percent):
        if not self.InfoPanel:
            self.InfoPanel = True
            self.Name = Label(rect=(610, 250, 100, 100), text=f'{ARMOR[num].type} {ARMOR[num].what} \\n vedekezesi aranya: {percent}% \\n\\n Ara: X pikely \\n\\n Ez targy vedelmet \\n nyujt X fajta \\n kartyak ellen', font=BP, color=(255, 255, 255))
            self.elements.append(self.Name)
        else:
            self.InfoPanel = False
            self.elements.remove(self.Name)

    def CaItemSlot(self, name, x, y, num, percent):
        InfoH = int(ARMOR[self.randnum].img.get_height())
        InfoW = int(ARMOR[self.randnum].img.get_width())

        self.button = Button(
            rect=(x+20, y + 35, self.iw-20, self.ih - 40),
            callback=lambda: print(ARMOR[num]),
            normal_image=self.item_img,
            hover_image=self.item_img,
        )
        icon_x = (x + 30) + ((self.iw - 20) - InfoW) // 2
        icon_y = (y + 85) + ((self.ih - 40) - InfoH) // 2

        self.button1 = Button(
            rect=(icon_x, icon_y, InfoW, InfoH),
            callback="",
            hover_callback=lambda: self.CreateInfoPanel(num, percent),
            normal_image=ARMOR[num].img,
        )
        self.elements.append(self.button)
        self.elements.append(self.button1)

        self.item_slots.append(self.button)
        self.item_slots.append(self.button1)

        return name

    def OpenMarket(self):
        if self.ThePanel:
            self.ThePanel = False
            for i in self.item_slots:
                self.elements.remove(i)
                self.item_slots = []
        else:
            self.CaItemSlot("Armor", 180, 180, self.randnum1, self.RandPercent)
            self.CaItemSlot("Armor1", 180, 400, self.randnum, self.RandPercent1)
            self.ThePanel = True
