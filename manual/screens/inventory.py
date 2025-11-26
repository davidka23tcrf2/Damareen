import pygame, os
from ..ui.button import Button
from ..ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory.inventory import PLAYERARMOR, EquipedItems
from manual.ui.particles import ParticleManager
from manual.ui.vignette import create_red_vignette

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 32)
BP_SMALL = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 18)


class InventoryScreen:
    def __init__(self, goto_mainmenu):
        self.goto_mainmenu = goto_mainmenu

        # Red vignette and particles
        self.particles = ParticleManager(mode="blood")
        self.vignette = create_red_vignette()

        self.bg = load_asset("bg.png", "inventory")
        self.item = load_asset("1.png", "inventory")
        self.character = load_asset("body.png", "character")

        # Load element type icons
        try:
            self.element_icons = {
                "fold": load_asset("fold.png", "cards"),
                "viz": load_asset("viz.png", "cards"),
                "tuz": load_asset("tuz.png", "cards"),
                "levego": load_asset("levego.png", "cards"),
            }
        except:
            # Fallback if icons don't exist
            self.element_icons = {}

        self.elements = []

        # Title
        title = Label(
            rect=(640, 30, 100, 100),
            text="Targyak",
            font=BP,
            color=(255, 255, 255),
        )
        self.elements.append(title)

        # Back button
        back_btn = Button(
            (30, 30, 180, 70),
            self.goto_mainmenu,
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

        # Scrollable inventory list (4 columns)
        self.scroll_y = 0
        self.max_scroll = 0
        self.scroll_speed = 20
        self.inventory_area = pygame.Rect(750, 100, 500, 550)
        
        # Track scrolling state to prevent clicks during scroll
        self.scroll_block_duration = 0.2  # seconds
        self.scroll_block_until = 0       # time.time() until which clicks are ignored

        self.slots = []
        self._build_slots()

        # Equipped item clickable areas
        self.equipped_item_rects = {}

    def _build_slots(self):
        """Build scrollable inventory slots in 4-column grid"""
        self.slots = []

        # Handle empty inventory
        if not PLAYERARMOR:
            self.max_scroll = 0
            return

        cols = 4
        slot_w = 110
        slot_h = 110
        x_gap = 10
        y_gap = 10

        start_x = 760  # kept for clarity, but incorporated into offsets below
        start_y = 110

        for i, armor in enumerate(PLAYERARMOR):
            row = i // cols
            col = i % cols
            x_offset = col * (slot_w + x_gap)
            y_offset = row * (slot_h + y_gap)

            self.slots.append(
                {
                    "armor": armor,
                    "x_offset": x_offset,
                    "y_offset": y_offset,
                    "width": slot_w,
                    "height": slot_h,
                    "index": i,
                }
            )

        # Calculate max scroll
        if self.slots:
            num_rows = (len(self.slots) + cols - 1) // cols
            total_height = num_rows * (slot_h + y_gap)
            self.max_scroll = max(0, total_height - self.inventory_area.height)

    def AddItem(self, idx):
        """Equip an item from inventory"""
        armor = PLAYERARMOR[idx]
        defense = armor.defense if armor.defense is not None else 15

        # Check if already equipped
        for i, item in enumerate(EquipedItems[:]):
            # Handle both tuple and object formats
            if isinstance(item, tuple):
                item_type, item_what, item_img, item_defense = item
            else:
                item_type = item.type
                item_what = item.what
                item_img = item.img
                item_defense = getattr(item, "defense", defense)

            if item_what == armor.what:
                print("Kiszedve")
                if item_type == armor.type:
                    EquipedItems.remove(item)
                else:
                    EquipedItems.remove(item)
                    EquipedItems.append((armor.type, armor.what, armor.img, defense))
                return

        EquipedItems.append((armor.type, armor.what, armor.img, defense))
        print("Beteve")

    def unequip_item(self, slot_name):
        """Remove equipped item from the slot"""
        for item in EquipedItems[:]:
            # Handle both tuple and object formats
            if isinstance(item, tuple):
                item_what = item[1]
            else:
                item_what = item.what

            if item_what == slot_name:
                EquipedItems.remove(item)
                print(f"Unequipped {slot_name}")
                break

    def CreateItemSlot(self, surface, color, start, end, thickness=1, fill_color=None):
        """Draw a bordered rectangle"""
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
            pygame.draw.rect(
                surface, fill_color, (inner_left, inner_top, inner_width, inner_height)
            )

    def handle_event(self, e):
        import time

        # Handle scrolling via MOUSEWHEEL
        if e.type == pygame.MOUSEWHEEL:
            if self.inventory_area.collidepoint(pygame.mouse.get_pos()):
                old_scroll = self.scroll_y
                self.scroll_y -= e.y * self.scroll_speed
                self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

                # If scroll position changed, block clicks for a short time
                if old_scroll != self.scroll_y:
                    self.scroll_block_until = time.time() + self.scroll_block_duration

        # Handle clicks - but ONLY if we haven't scrolled recently
        if e.type == pygame.MOUSEBUTTONDOWN:
            # Ignore scroll-wheel "button" events entirely (4/5)
            if getattr(e, "button", None) in (4, 5):
                return

            current_time = time.time()
            if current_time < self.scroll_block_until:
                # We recently scrolled; treat this as part of scrolling, not a click
                return

            mouse_pos = pygame.mouse.get_pos()

            # Check equipped item clicks
            for slot_name, rect in self.equipped_item_rects.items():
                if rect.collidepoint(mouse_pos):
                    self.unequip_item(slot_name)
                    break

            # Check inventory item clicks (only if mouse is in inventory area)
            if self.inventory_area.collidepoint(mouse_pos):
                for slot in self.slots:
                    slot_x = self.inventory_area.x + slot["x_offset"] + 10
                    slot_y = (
                        self.inventory_area.y
                        + slot["y_offset"]
                        - self.scroll_y
                        + 10
                    )
                    slot_rect = pygame.Rect(
                        slot_x, slot_y, slot["width"], slot["height"]
                    )

                    # Check if slot is visible and clicked
                    if slot_rect.collidepoint(mouse_pos):
                        # Only equip if the slot is actually visible in the scrollable area
                        if (
                            slot_y >= self.inventory_area.y
                            and slot_y + slot["height"] <= self.inventory_area.bottom
                        ):
                            self.AddItem(slot["index"])
                            break

        for el in self.elements:
            el.handle_event(e)

    def update(self, dt):
        self.particles.update(dt)
        for el in self.elements:
            el.update(dt)

    def draw(self, surf):
        surf.fill((0, 0, 0))  # Black background

        # Draw particles
        self.particles.draw(surf)

        # Draw vignette
        surf.blit(self.vignette, (0, 0))

        # Draw character area with fixed border
        self.CreateItemSlot(
            surf,
            color=(255, 255, 255),
            start=(200, 150),
            end=(500, 700),
            thickness=3,
            fill_color=(20, 20, 30),
        )
        character_s = pygame.transform.scale(self.character, (300, 550))
        surf.blit(character_s, (200, 150))

        # Clear equipped item rects
        self.equipped_item_rects = {}

        # Draw equipped items (directly clickable)
        if len(EquipedItems) > 0:
            # Sort items for drawing order: Mellvert -> Nadrag -> Cipo -> Sapka
            # This ensures Chestplate is drawn first (bottom), then Leggings, then Shoes (top)
            draw_order = ["mellvert", "nadrag", "cipo", "sapka"]
            
            # Map items by slot
            items_by_slot = {}
            for item in EquipedItems:
                if isinstance(item, tuple):
                    slot = item[1]
                else:
                    slot = item.what
                items_by_slot[slot] = item
            
            for slot in draw_order:
                if slot in items_by_slot:
                    item = items_by_slot[slot]
                    
                    # Handle both tuple and object formats
                    if isinstance(item, tuple):
                        item_type, item_what, item_img, item_defense = item
                    else:
                        item_type = item.type
                        item_what = item.what
                        item_img = item.img
                        item_defense = getattr(item, "defense", 15)

                    if item_what == "mellvert":
                        img = pygame.transform.scale(item_img, (225, 150))
                        pos = (240, 351)
                        surf.blit(img, pos)
                        self.equipped_item_rects["mellvert"] = pygame.Rect(
                            pos[0], pos[1], 225, 150
                        )
                    elif item_what == "sapka":
                        img1 = pygame.transform.scale(item_img, (175, 130))
                        pos = (270, 200)
                        surf.blit(img1, pos)
                        self.equipped_item_rects["sapka"] = pygame.Rect(
                            pos[0], pos[1], 175, 130
                        )
                    elif item_what == "cipo":
                        img3 = pygame.transform.scale(item_img, (175, 100))
                        pos = (270, 500)
                        surf.blit(img3, pos)
                        self.equipped_item_rects["cipo"] = pygame.Rect(
                            pos[0], pos[1], 175, 100
                        )
                    elif item_what == "nadrag":
                        img2 = pygame.transform.scale(item_img, (175, 100))
                        pos = (270, 450)
                        surf.blit(img2, pos)
                        self.equipped_item_rects["nadrag"] = pygame.Rect(
                            pos[0], pos[1], 175, 100
                        )

        # Draw inventory area background
        pygame.draw.rect(surf, (20, 20, 30), self.inventory_area)
        pygame.draw.rect(surf, (255, 255, 255), self.inventory_area, 3)

        # Set clipping for scrollable area
        surf.set_clip(self.inventory_area)

        # Draw inventory items in 4-column grid
        if not self.slots:
            # Display empty message
            empty_text = BP_SMALL.render(
                "Nincs targy - menj a boltba!", True, (200, 200, 200)
            )
            text_rect = empty_text.get_rect(
                center=(self.inventory_area.centerx, self.inventory_area.centery)
            )
            surf.blit(empty_text, text_rect)
        else:
            for slot in self.slots:
                armor = slot["armor"]
                slot_x = self.inventory_area.x + slot["x_offset"] + 10
                slot_y = (
                    self.inventory_area.y + slot["y_offset"] - self.scroll_y + 10
                )

                # Only draw if visible
                if (
                    slot_y + slot["height"] < self.inventory_area.y
                    or slot_y > self.inventory_area.bottom
                ):
                    continue

                slot_rect = pygame.Rect(
                    slot_x, slot_y, slot["width"], slot["height"]
                )

                # Draw slot background
                pygame.draw.rect(surf, (40, 40, 50), slot_rect)
                pygame.draw.rect(surf, (100, 100, 100), slot_rect, 2)

                # Draw armor image
                armor_img = pygame.transform.scale(armor.img, (70, 70))
                surf.blit(armor_img, (slot_x + 5, slot_y + 5))

                # Draw element icon
                if armor.type in self.element_icons:
                    icon = pygame.transform.scale(
                        self.element_icons[armor.type], (30, 30)
                    )
                    surf.blit(icon, (slot_x + 75, slot_y + 5))

                # Draw defense value (static)
                defense = armor.defense if armor.defense is not None else 15
                defense_text = BP_SMALL.render(
                    f"{defense}%", True, (255, 255, 0)
                )
                surf.blit(defense_text, (slot_x + 5, slot_y + 85))

        surf.set_clip(None)

        # Draw scrollbar if needed
        if self.max_scroll > 0:
            scrollbar_x = self.inventory_area.right - 15
            scrollbar_y = self.inventory_area.y
            scrollbar_height = self.inventory_area.height

            # Background
            pygame.draw.rect(
                surf,
                (50, 50, 50),
                (scrollbar_x, scrollbar_y, 10, scrollbar_height),
            )

            # Handle
            handle_height = max(
                30,
                int(
                    (self.inventory_area.height
                     / (self.inventory_area.height + self.max_scroll))
                    * scrollbar_height
                ),
            )
            handle_y = scrollbar_y + int(
                (self.scroll_y / self.max_scroll)
                * (scrollbar_height - handle_height)
            )
            pygame.draw.rect(
                surf, (255, 50, 50), (scrollbar_x, handle_y, 10, handle_height)
            )

        # Draw UI elements
        for el in self.elements:
            el.draw(surf)

    def refresh_inventory(self):
        """Refresh inventory display when items are added/removed"""
        # Rebuild slots
        self._build_slots()
