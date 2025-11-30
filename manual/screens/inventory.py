import pygame, os
import time
from ..ui.button import Button
from ..ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory.inventory import PLAYERARMOR, EQUIPPED_ARMOR
from manual.ui.particles import ParticleManager
from manual.ui.vignette import create_red_vignette

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 32)
BP_SMALL = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 18)


class InventoryScreen:
    def __init__(self, goto_mainmenu):
        self.goto_mainmenu = goto_mainmenu

        self.particles = ParticleManager(mode="blood")
        self.vignette = create_red_vignette()

        self.bg = load_asset("bg.png", "inventory")
        self.character = load_asset("body.png", "character")

        # Element icons
        try:
            self.element_icons = {
                "fold": load_asset("fold.png", "cards"),
                "viz": load_asset("viz.png", "cards"),
                "tuz": load_asset("tuz.png", "cards"),
                "levego": load_asset("levego.png", "cards"),
            }
        except:
            self.element_icons = {}

        self.elements = []
        self.slots = []

        # Title
        title = Label(rect=(640, 30, 80, 100), text="Targyak", font=BP, color=(255, 255, 255))
        self.elements.append(title)

        # Back button
        back_btn = Button(
            (30, 30, 180, 70), self.goto_mainmenu, None,
            text="Vissza", font=BP_SMALL,
            text_color=(200, 200, 200),
            bg_color=None,
            hover_bg_color=(30, 30, 30),
            border_color=(200, 200, 200), border_radius=8
        )
        self.elements.append(back_btn)

        # Scroll settings
        self.scroll_y = 0
        self.scroll_speed = 20
        self.max_scroll = 0
        self.scroll_block_until = 0
        self.scroll_block_duration = 0.2

        self.inventory_area = pygame.Rect(750, 100, 500, 550)
        self.equipped_item_rects = {}

        # Layout for equipped items (easy to tweak pos & size per slot)
        # what: "sapka" (helmet), "mellvert" (chestplate), "nadrag" (leggings), "cipo" (boots)
        self.equipped_layout = {
            "mellvert": {"pos": (340, 285), "size": (230, 215)},  # chestplate
            "nadrag":   {"pos": (370, 430), "size": (170, 185)},  # leggings
            "cipo":     {"pos": (365, 540), "size": (175, 120)},  # boots
            "sapka":    {"pos": (380, 90), "size": (150, 150)},  # helmet
        }

        # Draw order: chestplate -> leggings -> boots -> helmet
        self.equipped_draw_order = ["mellvert", "nadrag", "cipo", "sapka"]

        self._build_slots()

    # -----------------------------------------------------------
    def _build_slots(self):
        """Build inventory slots for PLAYERARMOR."""
        self.slots = []
        if not PLAYERARMOR:
            self.max_scroll = 0
            return

        cols = 4
        slot_w = 110
        slot_h = 110
        gap_x = 10
        gap_y = 10

        for i, armor in enumerate(PLAYERARMOR):
            row = i // cols
            col = i % cols

            self.slots.append({
                "armor": armor,
                "x_offset": col * (slot_w + gap_x),
                "y_offset": row * (slot_h + gap_y),
                "width": slot_w,
                "height": slot_h,
                "index": i,
            })

        rows = (len(self.slots) + cols - 1) // cols
        total_h = rows * (slot_w + gap_y)

        self.max_scroll = max(0, total_h - self.inventory_area.height)

    # -----------------------------------------------------------
    def AddItem(self, idx):
        """Equip armor from inventory."""
        armor = PLAYERARMOR[idx]

        # Remove same slot item
        EQUIPPED_ARMOR[:] = [a for a in EQUIPPED_ARMOR if a.what != armor.what]

        # Equip new armor (store the whole Armor object)
        EQUIPPED_ARMOR.append(armor)

        print(f"Equipped: {armor.what}")

    # -----------------------------------------------------------
    def unequip_item(self, slot_name):
        EQUIPPED_ARMOR[:] = [a for a in EQUIPPED_ARMOR if a.what != slot_name]
        print(f"Unequipped: {slot_name}")

    # -----------------------------------------------------------
    def handle_event(self, e):
        # Scroll
        if e.type == pygame.MOUSEWHEEL:
            if self.inventory_area.collidepoint(pygame.mouse.get_pos()):
                old = self.scroll_y
                self.scroll_y -= e.y * self.scroll_speed
                self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
                if old != self.scroll_y:
                    self.scroll_block_until = time.time() + self.scroll_block_duration

        # Clicks
        if e.type == pygame.MOUSEBUTTONDOWN:
            # Ignore mouse wheel buttons (4 = scroll up, 5 = scroll down)
            if e.button in (4, 5):
                return

            if time.time() < self.scroll_block_until:
                return

            mouse = pygame.mouse.get_pos()

            # Click equipped item to unequip
            for slot, rect in self.equipped_item_rects.items():
                if rect.collidepoint(mouse):
                    self.unequip_item(slot)
                    return

            # Click inventory
            if self.inventory_area.collidepoint(mouse):
                for slot in self.slots:
                    x = self.inventory_area.x + slot["x_offset"] + 10
                    y = self.inventory_area.y + slot["y_offset"] - self.scroll_y + 10
                    rect = pygame.Rect(x, y, slot["width"], slot["height"])

                    if rect.collidepoint(mouse):
                        self.AddItem(slot["index"])
                        return

        for el in self.elements:
            el.handle_event(e)

    # -----------------------------------------------------------
    def update(self, dt):
        self.particles.update(dt)
        for el in self.elements:
            el.update(dt)

    # -----------------------------------------------------------
    def draw(self, surf):
        surf.fill((0, 0, 0))
        self.particles.draw(surf)
        surf.blit(self.vignette, (0, 0))

        # Character background

        surf.blit(pygame.transform.scale(self.character, (400, 725)), (250, 10))

        # ---------------- EQUIPPED ITEMS ------------------
        self.equipped_item_rects = {}

        # Map slot name -> armor object
        equipped_by_slot = {}
        for armor in EQUIPPED_ARMOR:
            equipped_by_slot[armor.what] = armor

        # Draw in fixed order: chestplate -> leggings -> boots -> helmet
        for slot_name in self.equipped_draw_order:
            armor = equipped_by_slot.get(slot_name)
            if not armor:
                continue

            layout = self.equipped_layout.get(slot_name, {})
            pos = layout.get("pos", (250, 300))
            size = layout.get("size", (150, 150))

            img = load_asset(armor.image_name, "armor")
            img_scaled = pygame.transform.scale(img, size)

            surf.blit(img_scaled, pos)

            self.equipped_item_rects[slot_name] = pygame.Rect(
                pos[0], pos[1], img_scaled.get_width(), img_scaled.get_height()
            )

        # ---------------- INVENTORY GRID ------------------
        pygame.draw.rect(surf, (20, 20, 30), self.inventory_area)
        pygame.draw.rect(surf, (255, 255, 255), self.inventory_area, 3)
        surf.set_clip(self.inventory_area)

        if not self.slots:
            t = BP_SMALL.render("Nincs targy - menj a boltba!", True, (200, 200, 200))
            surf.blit(t, t.get_rect(center=self.inventory_area.center))
        else:
            for slot in self.slots:
                armor = slot["armor"]

                x = self.inventory_area.x + slot["x_offset"] + 10
                y = self.inventory_area.y + slot["y_offset"] - self.scroll_y + 10

                rect = pygame.Rect(x, y, slot["width"], slot["height"])
                if rect.bottom < self.inventory_area.y or rect.top > self.inventory_area.bottom:
                    continue

                pygame.draw.rect(surf, (40, 40, 50), rect)
                pygame.draw.rect(surf, (100, 100, 100), rect, 2)

                img = load_asset(armor.image_name, "armor")
                surf.blit(pygame.transform.scale(img, (70, 70)), (x + 5, y + 5))

                # Element icon
                if armor.type in self.element_icons:
                    icon = pygame.transform.scale(self.element_icons[armor.type], (30, 30))
                    surf.blit(icon, (x + 75, y + 5))

                # Defense text
                defense = getattr(armor, "defense", 15)
                txt = BP_SMALL.render(f"{defense}%", True, (255, 255, 0))
                surf.blit(txt, (x + 5, y + 85))

        surf.set_clip(None)

        # Scroll bar
        if self.max_scroll > 0:
            bar_x = self.inventory_area.right - 15
            bar_y = self.inventory_area.y
            bar_h = self.inventory_area.height

            pygame.draw.rect(surf, (50, 50, 50), (bar_x, bar_y, 10, bar_h))

            h = max(30, int((self.inventory_area.height /
                             (self.inventory_area.height + self.max_scroll)) * bar_h))
            y = bar_y + int((self.scroll_y / self.max_scroll) * (bar_h - h))

            pygame.draw.rect(surf, (255, 50, 50), (bar_x, y, 10, h))

        for el in self.elements:
            el.draw(surf)

    # -----------------------------------------------------------
    def refresh_inventory(self):
        self._build_slots()
