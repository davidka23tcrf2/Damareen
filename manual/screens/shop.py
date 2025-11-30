import random
import pygame, os
from ..ui.button import Button
from ..ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory.inventory import PLAYERARMOR, COINS, SHOP_NEEDS_REFRESH, ARMOR
from manual.ui.particles import ParticleManager
from manual.ui.vignette import create_red_vignette
import copy
import manual.inventory.inventory as inv

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 32)
BP_SMALL = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 24)
BP_50 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 50)

class ShopScreen:
    def __init__(self, goto_menu):
        self.goto_menu = goto_menu
        self.particles = ParticleManager(mode="blood")
        self.vignette = create_red_vignette()
        self.elements = []

        self.coins_label = Label(rect=(1000, 50, 100, 100), text=f"Pikkelyeid: {COINS}", font=BP_50, color=(255, 255, 0))
        self.elements.append(self.coins_label)

        back_btn = Button(
            (30, 30, 180, 70),
            self.goto_menu,
            None,
            text="Vissza",
            font=BP_SMALL,
            text_color=(200, 200, 200),
            bg_color=None,
            hover_bg_color=(30, 30, 30),
            border_color=(200, 200, 200),
            border_radius=8,
        )
        self.elements.append(back_btn)

        self.message_label = Label(rect=(640, 650, 100, 50), text="", font=BP_SMALL, color=(255, 50, 50))
        self.elements.append(self.message_label)
        self.message_timer = 0

        # Load Buy Sound
        try:
            self.buy_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "sounds", "buy.mp3"))
            self.buy_sound.set_volume(0.5)
        except Exception as e:
            print(f"Failed to load buy sound: {e}")
            self.buy_sound = None

        self.shop_items = []
        self.item_buttons = []

        if SHOP_NEEDS_REFRESH:
            self.reset_shop()
        else:
            self.generate_shop_items()
            self.create_item_slots()

    def generate_shop_items(self):
        self.shop_items = []
        for _ in range(4):
            armor = random.choice(ARMOR)
            defense = random.randint(10, 20)
            cost = 1 + int((defense - 10) * 0.4)
            self.shop_items.append({
                "armor": armor,
                "defense": defense,
                "cost": cost,
                "sold": False,
            })

    def create_item_slots(self):
        self.item_buttons = []
        slot_w = 200
        slot_h = 250
        gap_x = 20
        gap_y = 20
        total_w = 2 * slot_w + gap_x
        total_h = 2 * slot_h + gap_y
        start_x = (1280 - total_w) // 2
        start_y = (720 - total_h) // 2 - 30
        for i in range(4):
            row = i // 2
            col = i % 2
            x = start_x + col * (slot_w + gap_x)
            y = start_y + row * (slot_h + gap_y)
            btn = Button(
                (x, y, slot_w, slot_h),
                lambda idx=i: self.buy_item(idx),
                None,
                text="",
                bg_color=(40, 40, 50),
                hover_bg_color=(60, 60, 70),
                border_color=(255, 255, 255),
                border_radius=10,
            )
            btn.rect_pos = (x, y, slot_w, slot_h)
            self.item_buttons.append(btn)

    def buy_item(self, idx):
        item = self.shop_items[idx]
        if item["sold"]:
            print("Item already sold!")
            return
        if inv.COINS < item["cost"]:
            self.message_label.set_text("Nincs eleg pikkelyed!")
            self.message_timer = 2.0
            print(f"Not enough coins! Need {item['cost']}, have {inv.COINS}")
            return

        self.message_label.set_text("")
        inv.COINS -= item["cost"]

        # Play buy sound
        if self.buy_sound:
            self.buy_sound.play()

        new_armor = copy.deepcopy(item["armor"])
        new_armor.defense = item["defense"]
        new_armor.image_name = item["armor"].image_name

        PLAYERARMOR.append(new_armor)
        item["sold"] = True
        self.coins_label.set_text(f"Pikkelyek: {inv.COINS}")
        print(f"Purchased {new_armor.type} {new_armor.what} for {item['cost']} coins with {new_armor.defense}% defense!")

    def handle_event(self, e):
        for el in self.elements:
            el.handle_event(e)
        for btn in self.item_buttons:
            btn.handle_event(e)

    def reset_shop(self):
        self.generate_shop_items()
        self.create_item_slots()
        inv.SHOP_NEEDS_REFRESH = False

    def update(self, dt):
        self.particles.update(dt)
        self.coins_label.set_text(f"Pikkelyek: {inv.COINS}")
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message_label.set_text("")
        for el in self.elements:
            el.update(dt)
        for btn in self.item_buttons:
            btn.update(dt)

    def draw(self, surf):
        surf.fill((0, 0, 0))
        self.particles.draw(surf)
        surf.blit(self.vignette, (0, 0))
        for el in self.elements:
            el.draw(surf)
        for i, btn in enumerate(self.item_buttons):
            item = self.shop_items[i]
            x, y, w, h = btn.rect_pos
            btn.draw(surf)
            if item["sold"]:
                overlay = pygame.Surface((w, h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                surf.blit(overlay, (x, y))
                sold_text = BP.render("ELADVA", True, (255, 50, 50))
                text_rect = sold_text.get_rect(center=(x + w // 2, y + h // 2))
                surf.blit(sold_text, text_rect)
            else:
                armor_img = pygame.transform.scale(
                    load_asset(item["armor"].image_name, "armor"),
                    (120, 120)
                )
                surf.blit(armor_img, (x + (w - 120) // 2, y + 20))
                type_text = BP_SMALL.render(f"{item['armor'].type} {item['armor'].what}", True, (255, 255, 255))
                type_rect = type_text.get_rect(center=(x + w // 2, y + 160))
                surf.blit(type_text, type_rect)
                def_text = BP_SMALL.render(f"Vedelem: {item['defense']}%", True, (100, 255, 100))
                def_rect = def_text.get_rect(center=(x + w // 2, y + 200))
                surf.blit(def_text, def_rect)
                cost_text = BP.render(f"{item['cost']} Pikkely", True, (255, 255, 0))
                cost_rect = cost_text.get_rect(center=(x + w // 2, y + 250))
                surf.blit(cost_text, cost_rect)