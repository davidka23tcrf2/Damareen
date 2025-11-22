import pygame
import os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.ui.text_entry import TextEntry
from manual.assets.assets import load_asset, ASSETS_DIR

sf = "configure"
pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "PublicPixel.ttf"), 20)
BP26 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "PublicPixel.ttf"), 26)


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

        # Close button (top-left inside popup)
        closebtn = load_asset("closebutton.png", sf)
        self.close_btn = Button((0, 0, 98, 98), close_callback, closebtn)
        self.elements.append(self.close_btn)

        # Labels (positions are relative inside popup; their base_rect will be recorded)
        self.elements.append(Label((450, 50, 0, 0), "Új kártya konfigurálása", font=BP26, color=(255, 255, 255)))
        self.elements.append(Label((450, 170, 0, 0), "Név", font=BP26, color=(255, 255, 255)))
        self.elements.append(Label((630, 220, 0, 0), "Sebzés", font=BP26, color=(255, 255, 255)))
        self.elements.append(Label((630, 270, 0, 0), "Életerő", font=BP26, color=(255, 255, 255)))

        # Text entries (first = name, letters only; second = damage; third = health)
        y_positions = [150, 200, 250]
        for i, y_pos in enumerate(y_positions):
            if i == 0:
                entry = TextEntry((500, y_pos, 320, 40), font=BP26, max_length=12, letters_only=True)
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

            # load and scale image to 1/4 button area (half width/height)
            raw_img = load_asset(img, "elements")
            scaled_side = int(self.button_size)  # half size -> 1/4 area
            icon = pygame.transform.scale(raw_img, (scaled_side, scaled_side))

            # center icon inside button using image_offset
            offset_x = (self.button_size - scaled_side) // 2
            offset_y = (self.button_size - scaled_side) // 2

            btn = Button(
                (bx, by, self.button_size, self.button_size),
                lambda i=index: self.on_grid_button_index(i),
                icon,
                # no explicit hover image: Button will auto-generate a lighter one
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

        # Draw labels / close button
        for el in self.elements:
            el.draw(surf)

        # Draw text entries
        for entry in self.text_entries:
            entry.draw(surf)

        # Draw grid buttons on top
        for btn in self.grid_buttons:
            btn.draw(surf)

        # Draw selector (outline) – thicker border
        pygame.draw.rect(surf, self.selector_color, self.selector_rect, 3)

    def close(self):
        self.closing = True
        self.opening = False
