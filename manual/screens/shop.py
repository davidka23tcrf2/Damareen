import pygame
from ..ui.button import Button
from ..ui.label import Label
from manual.assets.assets import load_asset





class ShopScreen:
    def __init__(self, goto_arena):
        self.elements = []
        self.item_slots = []
        self.item_labels = []
        self.items = [
            ["Sisak", 20],
            ["Mellvért", 30]
        ]

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




        for el in self.elements:
            el.draw(surf)

    def CaItemSlot(self, name, x, y):
        self.my_label = Label(
            rect=(x, y+170, self.iw, 30),
            text=name,
            font_name="ButtonText.ttf",
            font_size=20,
            color=(255, 255, 255)
        )

        self.button = Button(
            rect=(x, y + 35, self.iw, self.ih - 40),
            callback=lambda: print("fasz"),
            normal_image=self.item_img,
            hover_image=self.item_img,
        )

        self.elements.append(self.button)
        self.elements.append(self.my_label)
        self.item_slots.append(self.button)
        self.item_slots.append(self.my_label)
        return self.my_label, name


    def OpenMarket(self):
        if self.ThePanel:
            self.ThePanel = False
            for i in self.item_slots:
                self.elements.remove(i)
                self.item_slots = []
            for i in self.item_labels:
                self.elements.remove(i)
                self.item_labels = []

        else:
            self.CaItemSlot(str(self.items[0][0]), 212, 200)
            self.CaItemSlot(str(self.items[1][0]), 212, 420)

            self.ThePanel = True


