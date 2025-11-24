from manual.inventory import inventory, objects
import pygame
import os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.ui.text_entry import TextEntry
from manual.assets.assets import load_asset, ASSETS_DIR

sf = "configure"
pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 20)
BP26 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 26)
BP_BIG = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 32)  # big dmg/hp


class CardPopup:
    """Popup for creating a new card with text inputs and a 2x2 button grid (unique images)."""
    def __init__(self, close_callback, screen_size=(1280, 720)):
        screen_width, screen_height = screen_size
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Popup size and placement
        w, h = 832, 468
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        self.target_rect = pygame.Rect(x, y, w, h)
        self.rect = pygame.Rect(x, screen_height, w, h)  # start off-screen (bottom)

        # Appearance
        self.bg_color = (139, 69, 19)  # brown
        self.border_color = (0, 0, 0)

        # UI element lists
        self.elements = []         # labels / buttons that follow popup
        self.text_entries = []     # TextEntry objects
        self.grid_buttons = []     # the 4 grid buttons

        # For card preview
        self.preview_icons = []

        # --- CREATE BUTTON ---
        create_w, create_h = 350, 100
        create_x = 430
        create_y = 320

        create_img = pygame.Surface((create_w, create_h), pygame.SRCALPHA)

        # green rounded rect background
        pygame.draw.rect(
            create_img,
            (50, 200, 50),                      # green fill
            create_img.get_rect(),
            border_radius=0                    # rounded corners
        )

        # black outline
        pygame.draw.rect(
            create_img,
            (0, 0, 0),                          # border color
            create_img.get_rect(),
            width=4,
            border_radius=0
        )

        label = BP26.render("létrehozás", True, (0, 0, 0))
        label_rect = label.get_rect(center=(create_w // 2, create_h // 2))
        create_img.blit(label, label_rect)

        self.create_btn = Button(
            (create_x, create_y, create_w, create_h),
            self.create_card,
            create_img
        )
        self.elements.append(self.create_btn)

        # --- STATUS TEXT STATE (NOT a Label) ---
        self.status_counter = 0    # frames left to display "card created"

        # Close button (top-left inside popup)
        closebtn = load_asset("closebutton.png", sf)
        self.close_btn = Button((0, 0, 98, 98), close_callback, closebtn)
        self.elements.append(self.close_btn)

        # Labels (positions are relative inside popup; their base_rect will be recorded)
        self.elements.append(Label((450, 50, 0, 0), "Új kártya konfigurálása", font=BP26, color=(255, 255, 255)))
        self.elements.append(Label((450, 170, 0, 0), "Név", font=BP26, color=(255, 255, 255)))
        self.elements.append(Label((630, 220, 0, 0), "Sebzés", font=BP26, color=(255, 255, 255)))
        self.elements.append(Label((630, 270, 0, 0), "Életerő", font=BP26, color=(255, 255, 255)))

        # --- NAME TAKEN LABEL (above name textbox) ---
        # starts empty / hidden
        self.name_taken_label = Label(
            (525, 125, 0, 0),  # slightly above the name TextEntry at y=150
            "",
            font=BP,
            color=(255, 50, 50),
        )
        self.name_taken_visible = False
        self.last_name_checked = ""
        self.elements.append(self.name_taken_label)

        # Text entries (first = name, letters only; second = damage; third = health)
        y_positions = [150, 200, 250]
        for i, y_pos in enumerate(y_positions):
            if i == 0:
                entry = TextEntry((500, y_pos, 320, 40), font=BP26, max_length=8, letters_only=True)
            else:
                entry = TextEntry((730, y_pos, 90, 40), font=BP26, max_length=3, numeric_only=True)
            # store base_pos (relative coordinates inside popup)
            entry.base_pos = entry.rect.topleft
            self.text_entries.append(entry)

        # 2x2 button grid configuration
        self.grid_rows = 2
        self.grid_cols = 2
        self.button_size = 50
        self.button_spacing = 5
        grid_start_x = 410
        grid_start_y = 200

        # element images
        button_images = [
            "dirt.png",
            "water.png",
            "air.png",
            "fire.png",
        ]

        for index, img in enumerate(button_images):
            row = index // self.grid_cols
            col = index % self.grid_cols
            bx = grid_start_x + col * (self.button_size + self.button_spacing)
            by = grid_start_y + row * (self.button_size + self.button_spacing)

            # load and scale image to button size
            raw_img = load_asset(img, "elements")
            scaled_side = int(self.button_size)
            icon = pygame.transform.scale(raw_img, (scaled_side, scaled_side))

            # bigger icon for the card preview
            preview_icon = pygame.transform.scale(raw_img, (96, 96))
            self.preview_icons.append(preview_icon)

            # center icon inside button using image_offset
            offset_x = (self.button_size - scaled_side) // 2
            offset_y = (self.button_size - scaled_side) // 2

            btn = Button(
                (bx, by, self.button_size, self.button_size),
                lambda i=index: self.on_grid_button_index(i),
                icon,
                image_offset=(offset_x, offset_y),
            )
            btn.base_pos = btn.rect.topleft
            self.grid_buttons.append(btn)

        # Selector (highlight) that indicates currently selected button
        self.selector_color = (255, 255, 0)
        self.selected_index = 0

        if self.grid_buttons:
            start = self.grid_buttons[self.selected_index].base_pos
        else:
            start = (grid_start_x, grid_start_y)

        self.selector_rect = pygame.Rect(start, (self.button_size, self.button_size))
        # use float position for smooth sliding
        self.selector_pos = pygame.math.Vector2(self.selector_rect.topleft)

        # Animation & overlay
        self.opening = True
        self.closing = False
        self.overlay_alpha = 0
        self.max_overlay_alpha = 150
        self.overlay_speed = 20

        # Active (modal)
        self.active = True

        # Ensure base_rect for elements is saved now (so draw/update can use them)
        for el in self.elements:
            el.base_rect = el.rect.copy()

    def on_grid_button_index(self, index):
        """Called when a grid button is clicked (index 0..3)."""
        self.selected_index = index

    def is_closed(self):
        return not self.opening and not self.closing and self.rect.y >= self.screen_height

    # ---- helper: only enable create when all fields filled ----
    def is_create_enabled(self):
        if len(self.text_entries) < 3:
            return False
        name = self.text_entries[0].text.strip()
        dmg = self.text_entries[1].text.strip()
        hp = self.text_entries[2].text.strip()
        return bool(name and dmg and hp)

    def create_card(self):
        """Collects all card fields, saves, clears, shows 'card created', returns dict."""
        if not self.is_create_enabled():
            return None

        name = self.text_entries[0].text.strip()
        dmg_txt = self.text_entries[1].text.strip()
        hp_txt = self.text_entries[2].text.strip()

        # final name that will be used
        final_name = name if name else "???"
        normalized_new = final_name.strip().lower()

        # 🔒 DUPLICATE CHECK: prevent card with same name
        for card in inventory.GAMECARDS:
            existing_name = getattr(card, "name", None)
            if isinstance(existing_name, str):
                if existing_name.strip().lower() == normalized_new:
                    # same name already exists -> show label and block creation
                    self.name_taken_label.set_text("Név foglalt")
                    self.name_taken_visible = True
                    self.last_name_checked = normalized_new
                    return None

        # convert safely
        dmg = int(dmg_txt) if dmg_txt.isdigit() else 0
        hp = int(hp_txt) if hp_txt.isdigit() else 0

        # Hungarian element names according to index:
        element_names = ["fold", "viz", "levegő", "tuz"]
        element_name = element_names[self.selected_index] if 0 <= self.selected_index < len(element_names) else "fold"

        data = {
            "name": final_name,
            "dmg": dmg,
            "hp": hp,
            "element": element_name,
        }

        # save to inventory
        inventory.GAMECARDS.append(
            objects.Card("kartya", data["name"], data["dmg"], data["hp"], data["element"])
        )

        # ⬇️ CLEAR TEXT ENTRIES HARD
        for entry in self.text_entries:
            # best effort: use set_text if it exists
            if hasattr(entry, "set_text"):
                entry.set_text("")
            else:
                entry.text = ""
            if hasattr(entry, "cursor_pos"):
                entry.cursor_pos = 0

        # reset element index
        self.selected_index = 0

        # hide "name taken" if it was visible
        self.name_taken_visible = False
        self.name_taken_label.set_text("")
        self.last_name_checked = ""

        # show status "card created" for ~3 seconds
        self.status_counter = 60  # frames; adjust to your FPS

        return data

    def reopen(self):
        if self.is_closed():
            self.rect.y = self.screen_height
            self.opening = True
            self.closing = False
            self.overlay_alpha = 0
            self.active = True

    def handle_event(self, event):
        """
        Returns True if event handled (used by CONFIGURE to block propagation).
        """
        # Block mouse clicks outside popup while active
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            if not self.rect.collidepoint(event.pos):
                return True

        # Pass event to elements
        for el in self.elements:
            # don't let the create button handle events if fields are not filled
            if el is self.create_btn and not self.is_create_enabled():
                continue
            el.handle_event(event)

        # Pass event to text entries and grid buttons
        for entry in self.text_entries:
            entry.handle_event(event)
        for btn in self.grid_buttons:
            btn.handle_event(event)

        return True

    def update(self, dt):
        # Slide animation with easing (ease-out style)
        if self.opening:
            distance = self.rect.y - self.target_rect.y
            self.rect.y -= max(int(distance * 0.35), 5)
            self.overlay_alpha = min(self.overlay_alpha + self.overlay_speed, self.max_overlay_alpha)
            if self.rect.y <= self.target_rect.y:
                self.rect.y = self.target_rect.y
                self.opening = False
        elif self.closing:
            distance = self.screen_height - self.rect.y
            self.rect.y += max(int(distance * 0.35), 5)
            self.overlay_alpha = max(self.overlay_alpha - self.overlay_speed, 0)
            if self.rect.y >= self.screen_height:
                self.closing = False
                self.active = False

        # Update elements' positions relative to popup
        for el in self.elements:
            el.rect.topleft = (self.rect.x + el.base_rect.x, self.rect.y + el.base_rect.y)
            el.update(dt)

        # Move text entries relative to popup
        for entry in self.text_entries:
            entry.rect.topleft = (self.rect.x + entry.base_pos[0], self.rect.y + entry.base_pos[1])
            entry.update(dt)

        # Move and update grid buttons
        for btn in self.grid_buttons:
            btn.rect.topleft = (self.rect.x + btn.base_pos[0], self.rect.y + btn.base_pos[1])
            btn.update(dt)

        # --- Selector movement ---
        if self.grid_buttons:
            if self.opening or self.closing:
                # While popup is moving, lock selector to button (no smoothing)
                self.selector_pos = pygame.math.Vector2(
                    self.grid_buttons[self.selected_index].rect.topleft
                )
            else:
                # Popup is stationary -> smooth slide between buttons
                target = pygame.math.Vector2(self.grid_buttons[self.selected_index].rect.topleft)
                self.selector_pos += (target - self.selector_pos) * 0.3

            self.selector_rect.topleft = (round(self.selector_pos.x), round(self.selector_pos.y))

        # --- status timer ---
        if self.status_counter > 0:
            self.status_counter -= 1

        # --- hide "name taken" if user changed the name ---
        if self.name_taken_visible and self.text_entries:
            current_name = self.text_entries[0].text.strip().lower()
            if current_name != self.last_name_checked:
                self.name_taken_visible = False
                self.name_taken_label.set_text("")
                self.last_name_checked = ""

    def draw(self, surf):
        # Skip drawing when off-screen and overlay invisible
        if self.rect.y > self.screen_height and self.overlay_alpha <= 0:
            return

        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), flags=pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.overlay_alpha))
        surf.blit(overlay, (0, 0))

        # Popup background
        popup_surface = pygame.Surface((self.rect.width, self.rect.height))
        popup_surface.fill(self.bg_color)
        surf.blit(popup_surface, (self.rect.x, self.rect.y))
        pygame.draw.rect(surf, self.border_color, self.rect, 2)

        # --- CARD PREVIEW (left side) ---
        card_w, card_h = 240, 320
        card_x = self.rect.x + 120
        card_y = self.rect.y + 100
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        pygame.draw.rect(surf, (255, 255, 255), card_rect)
        pygame.draw.rect(surf, (0, 0, 0), card_rect, 2)

        # text values
        name = self.text_entries[0].text.strip() if self.text_entries else ""
        dmg = self.text_entries[1].text.strip() if len(self.text_entries) > 1 else ""
        hp = self.text_entries[2].text.strip() if len(self.text_entries) > 2 else ""

        if not name:
            name = "???"
        if not dmg:
            dmg = "?"
        if not hp:
            hp = "?"

        # --- name ---
        name_surf = BP26.render(name, True, (0, 0, 0))
        base_y = card_rect.y + 80
        name_rect = name_surf.get_rect(midtop=(card_rect.centerx, base_y))
        surf.blit(name_surf, name_rect)

        # --- BIG colored DMG / HP as "dmg/hp" ---
        dmg_surf = BP_BIG.render(str(dmg), True, (255, 50, 50))   # red
        slash_surf = BP_BIG.render("/", True, (0, 0, 0))          # black slash
        hp_surf = BP_BIG.render(str(hp), True, (50, 255, 50))     # green

        stats_y = name_rect.bottom + 15
        inner_spacing = 4  # space around slash

        total_width = (
            dmg_surf.get_width()
            + inner_spacing
            + slash_surf.get_width()
            + inner_spacing
            + hp_surf.get_width()
        )

        start_x = card_rect.centerx - total_width // 2

        dmg_rect = dmg_surf.get_rect(topleft=(start_x, stats_y))
        slash_rect = slash_surf.get_rect(topleft=(dmg_rect.right + inner_spacing, stats_y))
        hp_rect = hp_surf.get_rect(topleft=(slash_rect.right + inner_spacing, stats_y))

        surf.blit(dmg_surf, dmg_rect)
        surf.blit(slash_surf, slash_rect)
        surf.blit(hp_surf, hp_rect)

        stats_bottom = max(dmg_rect.bottom, slash_rect.bottom, hp_rect.bottom)

        # icon under dmg/hp
        if self.preview_icons:
            icon = self.preview_icons[self.selected_index]
            icon_rect = icon.get_rect(midtop=(card_rect.centerx, stats_bottom + 15))
            surf.blit(icon, icon_rect)
        # --- END CARD PREVIEW ---

        # Draw labels / close button / create button / name-taken label
        for el in self.elements:
            if el is self.create_btn and not self.is_create_enabled():
                # don't draw create button if fields are empty
                continue
            if el is self.name_taken_label and not self.name_taken_visible:
                # draw name-taken only when visible
                continue
            el.draw(surf)

        # Draw text entries
        for entry in self.text_entries:
            entry.draw(surf)

        # Draw grid buttons on top
        for btn in self.grid_buttons:
            btn.draw(surf)

        # Draw selector (outline) – thicker border
        pygame.draw.rect(surf, self.selector_color, self.selector_rect, 3)

        # --- STATUS TEXT ("card created") ---
        if self.status_counter > 0:
            status_surf = BP.render("Kártya létrehozva!", True, (0, 255, 0))
            status_rect = status_surf.get_rect(midbottom=(self.rect.x + 600, self.rect.y + 375))
            surf.blit(status_surf, status_rect)

    def close(self):
        self.closing = True
        self.opening = False
