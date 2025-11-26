import random
import pygame, os
from ..ui.button import Button
from ..ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory.inventory import ARMOR, PLAYERARMOR, COINS
from manual.ui.particles import ParticleManager
from manual.ui.vignette import create_red_vignette

# Fonts used in the shop UI
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 32)
BP_SMALL = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 24)
BP_50 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 50)

class ShopScreen:
    def __init__(self, goto_menu):
        self.goto_menu = goto_menu
        # Visual effects
        self.particles = ParticleManager(mode="blood")
        self.vignette = create_red_vignette()
        self.elements = []
        # Coins display
        self.coins_label = Label(rect=(1000, 50, 100, 100), text=f"Pikelyeid: {COINS}", font=BP_50, color=(255, 255, 0))
        self.elements.append(self.coins_label)
        # Back button
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
        
        # Message label for feedback (e.g. not enough coins)
        self.message_label = Label(rect=(640, 650, 100, 50), text="", font=BP_SMALL, color=(255, 50, 50))
        self.elements.append(self.message_label)
        self.message_timer = 0
        
        # Prepare shop data and UI slots
        self.shop_items = []
        self.item_buttons = []
        self.generate_shop_items()
        self.create_item_slots()

    def generate_shop_items(self):
        """Create four random armor entries with a defense percentage and cost.
        Defense is between 10‑20 %.
        Cost is linearly mapped: 10 % → 1 coin, 20 % → 5 coins.
        """
        self.shop_items = []
        for _ in range(4):
            armor = random.choice(ARMOR)
            defense = random.randint(10, 20)
            cost = 1 + int((defense - 10) * 0.4)  # 10→1, 20→5
            self.shop_items.append({
                "armor": armor,
                "defense": defense,
                "cost": cost,
                "sold": False,
            })

    def create_item_slots(self):
        """Create four button slots, smaller than before and positioned a bit higher.
        Layout: 2 × 2 grid centered horizontally.
        """
        self.item_buttons = []
        slot_w = 200  # smaller width
        slot_h = 250  # smaller height
        gap_x = 20
        gap_y = 20
        total_w = 2 * slot_w + gap_x
        total_h = 2 * slot_h + gap_y
        start_x = (1280 - total_w) // 2
        # Move the grid up (original was +50, now shift up by 30)
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
        """Purchase the item at *idx*.
        The item is removed from the shop (marked as sold) and added to the player's armor list.
        """
        import manual.inventory.inventory as inv
        item = self.shop_items[idx]
        if item["sold"]:
            print("Item already sold!")
            return
        if inv.COINS < item["cost"]:
            self.message_label.set_text("Nincs eleg pikkelyed!")
            self.message_timer = 2.0
            print(f"Not enough coins! Need {item['cost']}, have {inv.COINS}")
            return
        
        # Clear message if successful
        self.message_label.set_text("")
        # Deduct coins and add armor to the player's collection
        import copy
        inv.COINS -= item["cost"]
        
        # Create a unique instance of the armor and set its specific defense
        new_armor = copy.deepcopy(item["armor"])
        new_armor.defense = item["defense"]
        
        PLAYERARMOR.append(new_armor)
        item["sold"] = True
        # Update the displayed coin count
        self.coins_label.set_text(f"Pikelyek: {inv.COINS}")
        print(f"Purchased {new_armor.type} {new_armor.what} for {item['cost']} coins with {new_armor.defense}% defense!")

    def handle_event(self, e):
        for el in self.elements:
            el.handle_event(e)
        for btn in self.item_buttons:
            btn.handle_event(e)

    def update(self, dt):
        self.particles.update(dt)
        
        # Handle message timer
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
        # Draw each shop slot
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
                armor_img = pygame.transform.scale(item["armor"].img, (120, 120))
                surf.blit(armor_img, (x + (w - 120) // 2, y + 20))
                type_text = BP_SMALL.render(f"{item['armor'].type} {item['armor'].what}", True, (255, 255, 255))
                type_rect = type_text.get_rect(center=(x + w // 2, y + 160))
                surf.blit(type_text, type_rect)
                def_text = BP_SMALL.render(f"Vedelem: {item['defense']}%", True, (100, 255, 100))
                def_rect = def_text.get_rect(center=(x + w // 2, y + 200))
                surf.blit(def_text, def_rect)
                cost_text = BP.render(f"{item['cost']} Pikely", True, (255, 255, 0))
                cost_rect = cost_text.get_rect(center=(x + w // 2, y + 250))
                surf.blit(cost_text, cost_rect)
