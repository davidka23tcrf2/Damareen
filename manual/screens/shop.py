import random

import pygame, os
from ..ui.button import Button
from ..ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory.inventory import ARMOR
import math


BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 30)




class ShopScreen:
    def __init__(self, goto_arena):

        self.InfoPanel = False
        self.randnum = random.randint(0, len(ARMOR) - 1)
        self.randnum1 = random.randint(0, len(ARMOR) - 1)
        self.elements = []
        self.item_slots = []
        self.item_labels = []
        self.mx, self.my = pygame.mouse.get_pos()
        self.info = load_asset("info.png", "shop")
        self.bg_img = load_asset("WeaponMarket.png", "shop")
        normal = load_asset("armors.png", "shop")

        self.item_img = load_asset("itemstable.png", "shop")
        self.iw = int(self.item_img.get_width() * 0.25)
        self.ih = int(self.item_img.get_height() * 0.25)

        self.item_img = pygame.transform.scale(self.item_img, (self.iw, self.ih))
        self.item_pos = (200, 200)

        self.ThePanel = False

        w = int(normal.get_width() * 0.25)
        h = int(normal.get_height() * 0.25)
        normal_small = pygame.transform.scale(normal, (w, h))


        hover_small = normal_small


        button = Button(
            rect=(200, 1, w, h-40),
            callback=self.OpenMarket,
            normal_image=normal_small,
            hover_image=hover_small
        )
        self.elements.append(button)

    def handle_event(self, e):
        for el in self.elements:
            el.handle_event(e)

    def update(self, dt):
        for el in self.elements:
            el.update(dt)


    def draw(self, surf):


        surf.blit(self.bg_img, (0, 0))
        self.bg_img = pygame.transform.scale(self.bg_img, (1283, 754))

        if self.InfoPanel:

            surf.blit(self.info, (410.5, 100))
            self.info = pygame.transform.scale(self.info, (500, 500))

        for el in self.elements:
            el.draw(surf)





    def CreateInfoPanel(self, num):


        if not self.InfoPanel:


            self.InfoPanel = True
            self.Name = Label(rect=(610, 200, 100, 100), text=f'{ARMOR[num].what} \n Buzi' , font=BP, color=(255, 255, 255))

            self.elements.append(self.Name)
        else:
            self.InfoPanel = False
            self.elements.remove(self.Name)


    def CaItemSlot(self, name, x, y, num):
        InfoH =  int(ARMOR[self.randnum].img.get_height())
        InfoW = int(ARMOR[self.randnum].img.get_width())



        self.button = Button(
            rect=(x+20, y + 35, self.iw-20, self.ih - 40),
            callback=lambda: print("fasz"),
            normal_image=self.item_img,
            hover_image=self.item_img,



        )
        icon_x = (x + 30) + ((self.iw - 20) - InfoW) // 2
        icon_y = (y + 85) + ((self.ih - 40) - InfoH) // 2

        self.button1 = Button(
            rect=(icon_x, icon_y, InfoW, InfoH),
            callback="",
            hover_callback=lambda: self.CreateInfoPanel(num),
            normal_image=ARMOR[num].img,
            hover_image=ARMOR[num].img,


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
            self.CaItemSlot("Geci", 180, 180, self.randnum1)
            self.CaItemSlot("Hülye", 180, 400, self.randnum)

            self.ThePanel = True


