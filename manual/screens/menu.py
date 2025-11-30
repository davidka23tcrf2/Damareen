import pygame, os, math
from ..ui.button import Button
from ..ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory import inventory
from manual.inventory.inventory import EQUIPPED_ARMOR  # for equipped gear
from manual.screens.difficultypopup import DifficultyPopup
from manual.screens.settingspopup import SettingsPopup
from manual.screens.dungeonpopup import DungeonPopup
from manual.ui import theme
from manual.ui.particles import ParticleManager
from manual.ui.vignette import create_red_vignette

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 20)
TITLE_FONT = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 80)
HINT_FONT = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 16)


class MenuScreen:
    def __init__(self, goto_arena, goto_shop, goto_deckbuilder, goto_inventory):
        self.elements = []
        self.goto_arena = goto_arena
        self.goto_shop = goto_shop
        self.goto_deckbuilder = goto_deckbuilder
        self.goto_inventory = goto_inventory

        # ---------- TITLE (Flickery horror logo) ----------
        self.title_label = Label(
            (0, 30, 1280, 90),
            "Damareen",
            font=TITLE_FONT,
            color=(220, 40, 40)
        )
        self.elements.append(self.title_label)

        # Helper to style buttons consistently
        def make_btn(rect, text, callback, primary=False, small=False):
            font = BP if small else BP
            if primary:
                bg = (15, 15, 15)
                hover = (80, 5, 5)
                border = (200, 30, 30)
            else:
                bg = (10, 10, 15)
                hover = (50, 10, 20)
                border = (120, 40, 40)

            return Button(
                rect,
                callback,
                None,
                text=text,
                font=font,
                text_color=(230, 230, 230),
                bg_color=bg,
                hover_bg_color=hover,
                border_color=border,
                border_radius=12
            )

        # ---------- LEFT SIDE BUTTONS ----------
        self.elements.append(make_btn(
            (50, 300, 400, 80),
            "Pakli összeállítása",
            self.goto_deckbuilder,
            primary=True
        ))

        self.inventory_btn = make_btn(
            (50, 400, 400, 70),
            "Tárgyak",
            self.goto_inventory,
            primary=False
        )
        self.elements.append(self.inventory_btn)

        # ---------- RIGHT SIDE BUTTONS ----------
        # Shop ("Bolt") now on the RIGHT side
        self.shop_btn = make_btn(
            (1280 - 390, 720 - 420, 360, 90),
            "Bolt",
            self.goto_shop,
            primary=True
        )
        self.elements.append(self.shop_btn)

        self.dungeon_btn = make_btn(
            (1280 - 350, 720 - 210, 300, 60),
            "Kazamata kiválasztása",
            self.open_dungeon_popup,
            primary=False
        )
        self.elements.append(self.dungeon_btn)

        self.fight_btn = make_btn(
            (1280 - 350, 720 - 130, 300, 80),
            "Új harc",
            self.try_goto_arena,
            primary=True
        )
        self.elements.append(self.fight_btn)

        # ---------- POPUPS ----------
        self.difficulty_popup = None
        self.settings_popup = None  # still supported if opened from elsewhere
        self.dungeon_popup = None

        # ---------- FX ----------
        self.particle_manager = ParticleManager(screen_width=1280, screen_height=720, mode="horror")
        self.vignette = create_red_vignette()

        self.warning_label = Label(
            (1280 - 350, 720 - 160, 300, 30),
            "",
            font=BP,
            color=(255, 50, 50)
        )
        self.elements.append(self.warning_label)
        self.warning_timer = 0

        # Time for breathing / flicker
        self.time = 0.0

        # Cached scanline surface
        self._scanline_surf = None

        # Layout for equipped armor (relative to body)
        self._equipped_layout = {
            "mellvert": {"offset": (90, 275), "size": (230, 215)},  # chestplate
            "nadrag":   {"offset": (120, 420), "size": (170, 185)},  # leggings
            "cipo":     {"offset": (115, 530), "size": (175, 120)},  # boots
            "sapka":    {"offset": (130, 80),  "size": (150, 150)},  # helmet
        }
        self._equipped_draw_order = ["mellvert", "nadrag", "cipo", "sapka"]

    # ---------------------------------------------------
    def update_dungeon_label(self):
        if not inventory.ENEMIES:
            self.dungeon_btn.text = "Nincsenek kazamaták"
        else:
            idx = inventory.SELECTED_DUNGEON_INDEX
            if idx < 0 or idx >= len(inventory.ENEMIES):
                self.dungeon_btn.text = "Kazamata kiválasztása"
            else:
                dungeon_name = inventory.ENEMIES[idx].name
                self.dungeon_btn.text = f"{dungeon_name}"

    def try_goto_arena(self):
        if len(inventory.PLAYERDECK) == 0:
            self.warning_label.set_text("A paklid üres!")
            self.warning_timer = 2.0
            return

        if not inventory.ENEMIES:
            self.warning_label.set_text("Nincsenek elérhető kazamaták!")
            self.warning_timer = 2.0
            return

        if inventory.SELECTED_DUNGEON_INDEX < 0 or inventory.SELECTED_DUNGEON_INDEX >= len(inventory.ENEMIES):
            self.warning_label.set_text("Nincs kiválasztott kazamata!")
            self.warning_timer = 2.0
            return

        self.goto_arena()

    # keep this in case something else calls it, but no settings button anymore
    def open_settings(self):
        if not self.settings_popup:
            self.settings_popup = SettingsPopup(self.close_settings_popup)

    def open_dungeon_popup(self):
        if not self.dungeon_popup and inventory.ENEMIES:
            self.dungeon_popup = DungeonPopup(self.close_dungeon_popup)

    def handle_event(self, e):
        if self.settings_popup and self.settings_popup.active:
            handled = self.settings_popup.handle_event(e)
            if handled:
                return

        if self.difficulty_popup and self.difficulty_popup.active:
            handled = self.difficulty_popup.handle_event(e)
            if handled:
                return

        if self.dungeon_popup and self.dungeon_popup.active:
            handled = self.dungeon_popup.handle_event(e)
            if handled:
                return

        for el in self.elements:
            if not inventory.SHOP_ENABLED:
                if el == self.shop_btn or el == self.inventory_btn:
                    continue
            el.handle_event(e)

    def update(self, dt):
        self.time += dt

        if self.settings_popup and self.settings_popup.active:
            self.settings_popup.update(dt)
            return

        if not inventory.DIFFICULTY_SELECTED and self.difficulty_popup is None:
            self.difficulty_popup = DifficultyPopup(self.close_difficulty_popup)

        if self.difficulty_popup and self.difficulty_popup.active:
            self.difficulty_popup.update(dt)
            return

        if self.dungeon_popup and self.dungeon_popup.active:
            self.dungeon_popup.update(dt)
            return

        if len(inventory.PLAYERDECK) > 0 and inventory.ENEMIES:
            self.fight_btn.bg_color = (25, 25, 25)
            self.fight_btn.hover_bg_color = (90, 5, 5)
        else:
            self.fight_btn.bg_color = (10, 10, 15)
            self.fight_btn.hover_bg_color = (40, 10, 20)

        self.particle_manager.update(dt)

        if self.warning_timer > 0:
            self.warning_timer -= dt
            if self.warning_timer <= 0:
                self.warning_label.set_text("")

        # Flicker title color a bit (horror effect)
        flicker = 0.5 + 0.5 * math.sin(self.time * 12.0)
        r = 180 + int(40 * flicker)
        self.title_label.color = (r, 20, 20)

        for el in self.elements:
            if not inventory.SHOP_ENABLED:
                if el == self.shop_btn or el == self.inventory_btn:
                    continue
            el.update(dt)

    def _ensure_gradient(self, width, height):
        if not hasattr(self, '_gradient_surf') or self._gradient_surf.get_size() != (width, height):
            top_color = theme.BG_DARK
            bottom_color = (5, 5, 10)

            grad_strip = pygame.Surface((1, height))
            for y in range(height):
                t = y / height
                r = top_color[0] * (1 - t) + bottom_color[0] * t
                g = top_color[1] * (1 - t) + bottom_color[1] * t
                b = top_color[2] * (1 - t) + bottom_color[2] * t
                grad_strip.set_at((0, y), (int(r), int(g), int(b)))

            self._gradient_surf = pygame.transform.scale(grad_strip, (width, height))

        # Build scanline layer if needed
        if self._scanline_surf is None or self._scanline_surf.get_size() != (width, height):
            self._scanline_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            for y in range(0, height, 4):
                pygame.draw.line(self._scanline_surf, (0, 0, 0, 40), (0, y), (width, y))

    def _draw_equipped_character(self, surf):
        """Draws the equipped character in the center with no background panel."""
        w, h = surf.get_size()
        center = (w // 2, h // 2 + 40)

        # Breathing animation
        breath_phase = self.time
        breath_offset = int(6 * math.sin(breath_phase * 2.0))
        breath_scale = 1.0 + 0.02 * math.sin(breath_phase * 1.5)
        base_scale = 1.05 * breath_scale

        # Body sprite
        body = load_asset("body.png", "character")
        body_w, body_h = 400, 725
        body_w_scaled = int(body_w * base_scale)
        body_h_scaled = int(body_h * base_scale)

        body_img = pygame.transform.smoothscale(body, (body_w_scaled, body_h_scaled))
        body_rect = body_img.get_rect(center=(center[0], center[1] + breath_offset))

        # Shadow (soft ellipse under feet)
        shadow_rect = pygame.Rect(0, 0, int(body_w_scaled * 0.7), int(body_h_scaled * 0.09))
        shadow_rect.center = (body_rect.centerx, body_rect.bottom - int(body_h_scaled * 0.04))
        shadow = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 110), shadow.get_rect())
        surf.blit(shadow, shadow_rect.topleft)

        # Draw body
        surf.blit(body_img, body_rect.topleft)

        # Equipped items
        equipped_by_slot = {armor.what: armor for armor in EQUIPPED_ARMOR}

        for slot_name in self._equipped_draw_order:
            armor = equipped_by_slot.get(slot_name)
            layout = self._equipped_layout.get(slot_name)
            if not armor or not layout:
                continue

            offset = layout["offset"]
            size = layout["size"]

            # Scale with body
            w_scaled = int(size[0] * base_scale)
            h_scaled = int(size[1] * base_scale)

            try:
                img = load_asset(armor.image_name, "armor")
            except Exception:
                continue

            img_scaled = pygame.transform.smoothscale(img, (w_scaled, h_scaled))

            pos = (
                body_rect.x + int(offset[0] * base_scale),
                body_rect.y + int(offset[1] * base_scale),
            )
            surf.blit(img_scaled, pos)

    def draw(self, surf):
        self._ensure_gradient(surf.get_width(), surf.get_height())
        surf.blit(self._gradient_surf, (0, 0))

        # Particles behind character
        self.particle_manager.draw(surf)

        # Red vignette (dark edges, horror feel)
        surf.blit(self.vignette, (0, 0))

        # Film grain / scanlines
        if self._scanline_surf:
            surf.blit(self._scanline_surf, (0, 0))

        # Centered character with current armor, no background rectangle
        self._draw_equipped_character(surf)

        # UI elements
        for el in self.elements:
            if not inventory.SHOP_ENABLED:
                if el == self.shop_btn or el == self.inventory_btn:
                    continue
            el.draw(surf)
        
        # Draw hint text (ESC for settings) - centered below title
        hint_text = HINT_FONT.render("ESC a beállításokhoz", True, (150, 50, 50))
        hint_rect = hint_text.get_rect(center=(640, 130))
        surf.blit(hint_text, hint_rect)

        if self.difficulty_popup and self.difficulty_popup.active:
            self.difficulty_popup.draw(surf)

        if self.settings_popup and self.settings_popup.active:
            self.settings_popup.draw(surf)

        if self.dungeon_popup and self.dungeon_popup.active:
            self.dungeon_popup.draw(surf)

    def close_difficulty_popup(self):
        self.difficulty_popup = None

    def close_settings_popup(self):
        self.settings_popup = None

    def close_dungeon_popup(self):
        self.dungeon_popup = None
        self.update_dungeon_label()
