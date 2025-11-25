
import pygame, os
from ..ui.button import Button
from ..ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory.inventory import PLAYERARMOR, EquipedItems

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 80)
class InventoryScreen:
    def __init__(self, goto_mainmenu):

        self.bg = load_asset("bg.png", "inventory")
        self.item = load_asset("1.png", "inventory")
        self.character = load_asset("body.png", "character")
        self.boots = load_asset("boots(no).png", "inventory")
        self.elements = []
        Inventtory = Label(rect=(600, 0, 100, 100), text="Inventory", font=BP)

        self.elements.append(Inventtory)

        self.slots = []

        self._build_slots()

    def _build_slots(self):
        self.SlotsIndex = 0
        inv_x = 750
        inv_y = 100
        cols = 5
        total_slots = 30
        slot_w = 9
        slot_h = 90
        x_gap = 100
        y_gap = 10

        for i in range(total_slots):
            col = i % cols

            row = i // cols
            x = inv_x + col * (slot_w + x_gap)
            y = inv_y + row * (slot_h + y_gap)
            self.slots.append((x, y, slot_w, slot_h))

        for index, (x, y, w, h) in enumerate(self.slots):
            iw = int(self.item.get_width() * 1)
            ih = int(self.item.get_height() * 1)
            has_item = index < len(PLAYERARMOR) and len(PLAYERARMOR) > 0

            if has_item:
                slots = Button(
                    rect=(x, y, iw, ih),
                    callback=lambda dx=index: self.AddItem(dx),
                    normal_image=self.item,
                )
                self.Items = Button(
                    rect=(x, y, iw, ih),
                    callback=lambda: print(),
                    hover_callback=lambda: print('item'),
                    normal_image=PLAYERARMOR[index].img,
                    image_offset=(10, 20)

                )
                self.elements.append(slots)
                self.elements.append(self.Items)
            else:
                slots = Button(
                    rect=(x, y, iw, ih),
                    callback=lambda: print('fasz'),
                    normal_image=self.item,
                    hover_image=self.item,
                )
                self.elements.append(slots)

    def AddItem(self, idx):
        if len(EquipedItems) <= 0:
            EquipedItems.append(PLAYERARMOR[idx])
            return

        for i in EquipedItems:
            if i.what == PLAYERARMOR[idx].what:


                print("Kiszedve")
                if i.type == PLAYERARMOR[idx].type:
                    EquipedItems.remove(i)

                else:
                    EquipedItems.remove(i)
                    EquipedItems.append(PLAYERARMOR[idx])
                return


        EquipedItems.append(PLAYERARMOR[idx])
        print("Betéve")


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

        inner_left = left + thickness - 4
        inner_top = top + thickness - 4
        inner_width = (right - left) - thickness * 1
        inner_height = (bottom - top) - thickness * 1
        if inner_width > 0 and inner_height > 0:
            pygame.draw.rect(surface, fill_color,
                             (inner_left, inner_top, inner_width, inner_height))
    def handle_event(self, e):
        for el in self.elements: el.handle_event(e)

    def update(self, dt):
        for el in self.elements: el.update(dt)

    def draw(self, surf):
        surf.blit(self.bg, (0,0))

        self.CreateItemSlot(surf, color=(0,0,0), start=(200,150), end=(500,700), thickness=10, fill_color=(10,20,30))
        character_s = pygame.transform.scale(self.character, (400, 400))
        surf.blit(character_s, (150,200))
        if len(EquipedItems) > 0:
            for i in EquipedItems:
                if i.what == "mellvert":
                    img = pygame.transform.scale(i.img, (225, 150))
                    surf.blit(img, (240, 351))
                elif i.what == "sapka":
                    img1 = pygame.transform.scale(i.img, (175, 130))
                    surf.blit(img1, (270, 200))
                elif i.what == "nadrag":
                    img2 = pygame.transform.scale(i.img, (175, 100))
                    surf.blit(img2, (270, 450))
                elif i.what == "cipo":
                    img3 = pygame.transform.scale(i.img, (175, 100))
                    surf.blit(img3, (270, 500))

        for el in self.elements: el.draw(surf)

