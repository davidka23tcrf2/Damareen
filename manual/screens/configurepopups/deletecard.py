from manual.inventory import inventory
import pygame
import os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR

sf = "configure"
pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "PublicPixel.ttf"), 20)
BP26 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "PublicPixel.ttf"), 26)


class CardDeletePopup:
    """Popup that lists existing cards and lets you delete one."""

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

        # Colors
        self.bg_color = (139, 69, 19)
        self.border_color = (0, 0, 0)

        # UI collections
        self.elements = []       # labels, close, delete button
        self.card_buttons = []   # per-card row buttons

        self.selected_index = -1  # no selection initially

        # --- SCROLLING / LIST GEOMETRY ---
        self.scroll_offset = 0
        self.list_x = 120
        self.list_y = 120
        self.row_h = 40
        self.row_spacing = 0
        self.row_w = 550
        # visible height of the list inside the popup
        self.list_visible_height = h - self.list_y - 120
        self.min_scroll_offset = 0
        self.max_scroll_offset = 0

        # --- CLOSE BUTTON ---
        close_img = load_asset("closebutton.png", sf)
        self.close_btn = Button((0, 0, 98, 98), close_callback, close_img)
        self.elements.append(self.close_btn)

        # --- TITLE LABEL ---
        self.elements.append(
            Label((350, 50, 0, 0), "Kártya törlése", font=BP26, color=(255, 255, 255))
        )

        # --- DELETE BUTTON ---
        del_w, del_h = 250, 80
        del_x, del_y = 500, 350

        del_surface = pygame.Surface((del_w, del_h), pygame.SRCALPHA)
        pygame.draw.rect(
            del_surface,
            (200, 50, 50),
            del_surface.get_rect(),
            border_radius=20
        )
        pygame.draw.rect(
            del_surface,
            (0, 0, 0),
            del_surface.get_rect(),
            width=4,
            border_radius=20
        )
        del_label = BP26.render("Törlés", True, (0, 0, 0))
        del_label_rect = del_label.get_rect(center=(del_w // 2, del_h // 2))
        del_surface.blit(del_label, del_label_rect)

        self.delete_btn = Button(
            (del_x, del_y, del_w, del_h),
            self.delete_selected,
            del_surface
        )
        self.elements.append(self.delete_btn)

        # --- STATUS TEXT (timer) ---
        self.status_counter = 0

        # --- SELECTION HIGHLIGHT RECT ---
        self.selector_color = (255, 0, 0)
        self.selector_rect = None

        # --- ANIMATION & OVERLAY ---
        self.opening = True
        self.closing = False
        self.overlay_alpha = 0
        self.max_overlay_alpha = 150
        self.overlay_speed = 20
        self.active = True

        # Build the card list once
        self.build_card_list()

        # Save base_rect for all static elements
        for el in self.elements:
            el.base_rect = el.rect.copy()

    # ---------- SCROLL HELPERS ----------

    def _recalculate_scroll_limits(self):
        """Recalculate min/max scroll offset based on total list height."""
        total_rows = len(self.card_buttons)
        if total_rows == 0:
            self.scroll_offset = 0
            self.min_scroll_offset = 0
            self.max_scroll_offset = 0
            return

        content_height = total_rows * (self.row_h + self.row_spacing) - self.row_spacing

        if content_height <= self.list_visible_height:
            # Everything fits: no scrolling needed
            self.min_scroll_offset = 0
            self.max_scroll_offset = 0
        else:
            # scroll_offset is 0 at top; becomes negative as we scroll down
            self.max_scroll_offset = 0
            self.min_scroll_offset = self.list_visible_height - content_height  # negative

        # Clamp
        self.scroll_offset = max(self.min_scroll_offset, min(self.scroll_offset, self.max_scroll_offset))

    def _get_list_clip_rect_global(self):
        """Return the list viewport rect in *screen* coordinates."""
        return pygame.Rect(
            self.rect.x + self.list_x,
            self.rect.y + self.list_y,
            self.row_w,
            self.list_visible_height,
        )

    # ---------- CARD LIST BUILD / REBUILD ----------

    def build_card_list(self):
        """Create one button per card in inventory.GAMECARDS."""
        self.card_buttons.clear()
        self.selected_index = -1
        self.selector_rect = None
        self.scroll_offset = 0  # reset scroll to top when rebuilt

        for i, card in enumerate(inventory.GAMECARDS):
            y = self.list_y + i * (self.row_h + self.row_spacing)

            row_surface = pygame.Surface((self.row_w, self.row_h), pygame.SRCALPHA)
            pygame.draw.rect(row_surface, (230, 230, 230), row_surface.get_rect())
            pygame.draw.rect(row_surface, (50, 50, 50), row_surface.get_rect(), 1)

            name = getattr(card, "name", "???")
            dmg = getattr(card, "damage", getattr(card, "dmg", "?"))
            hp = getattr(card, "health", getattr(card, "hp", "?"))
            power = getattr(card, "power", "?")

            # TEXT FORMAT: name dmg/health power
            text = f"{name}  {dmg}/{hp}  {power}"
            text_surf = BP.render(text, True, (0, 0, 0))
            text_rect = text_surf.get_rect(midleft=(10, self.row_h // 2))
            row_surface.blit(text_surf, text_rect)

            btn = Button(
                (self.list_x, y, self.row_w, self.row_h),
                lambda idx=i: self.select_card(idx),
                row_surface
            )
            # store base_pos relative to popup (without scroll)
            btn.base_pos = btn.rect.topleft
            self.card_buttons.append(btn)

        # if there is at least one card, select the first by default
        if self.card_buttons:
            self.selected_index = 0
            first_rect = self.card_buttons[0].rect
            self.selector_rect = pygame.Rect(first_rect.topleft, first_rect.size)

        # recalc scroll bounds based on new content
        self._recalculate_scroll_limits()

    # ---------- ACTIONS ----------

    def select_card(self, index: int):
        if 0 <= index < len(self.card_buttons):
            self.selected_index = index
            btn_rect = self.card_buttons[index].rect
            self.selector_rect = pygame.Rect(btn_rect.topleft, btn_rect.size)

    def delete_selected(self):
        """Delete the currently selected card from inventory."""
        if self.selected_index < 0 or self.selected_index >= len(inventory.GAMECARDS):
            return

        # remove from GAMECARDS
        del inventory.GAMECARDS[self.selected_index]

        # rebuild list and selector
        self.build_card_list()

        # show status message for ~1 second (60fps)
        self.status_counter = 60

    # ---------- POPUP STATE ----------

    def is_closed(self):
        return not self.opening and not self.closing and self.rect.y >= self.screen_height

    def reopen(self):
        if self.is_closed():
            self.rect.y = self.screen_height
            self.opening = True
            self.closing = False
            self.overlay_alpha = 0
            self.active = True
            # always rebuild list when reopened (in case cards changed)
            self.build_card_list()

    # ---------- EVENT / UPDATE / DRAW ----------

    def handle_event(self, event):
        # Block clicks outside popup
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            if not self.rect.collidepoint(event.pos):
                return True

        list_clip = self._get_list_clip_rect_global()

        # --- SCROLL WHEEL ---
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            # Only scroll if mouse is over the list area (more intuitive)
            if list_clip.collidepoint(mx, my):
                scroll_step = 20  # pixels per wheel notch
                self.scroll_offset += event.y * scroll_step
                self.scroll_offset = max(
                    self.min_scroll_offset, min(self.scroll_offset, self.max_scroll_offset)
                )

        # Elements (close + delete)
        for el in self.elements:
            # disable delete button if nothing is selected or no cards
            if el is self.delete_btn and (self.selected_index < 0 or not self.card_buttons):
                continue
            el.handle_event(event)

        # Card row buttons – ignore clicks outside the visible list window
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            for btn in self.card_buttons:
                if btn.rect.colliderect(list_clip):
                    btn.handle_event(event)
        else:
            # non-mouse-button events (e.g. hover) can still update normally
            for btn in self.card_buttons:
                btn.handle_event(event)

        return True

    def update(self, dt):
        # Slide animation
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

        # Update elements' positions
        for el in self.elements:
            el.rect.topleft = (self.rect.x + el.base_rect.x, self.rect.y + el.base_rect.y)
            el.update(dt)

        # Update card buttons relative to popup + scroll
        for btn in self.card_buttons:
            base_x, base_y = btn.base_pos
            btn.rect.topleft = (
                self.rect.x + base_x,
                self.rect.y + base_y + self.scroll_offset
            )
            btn.update(dt)

        # Move selector with selected card row
        if self.selector_rect and 0 <= self.selected_index < len(self.card_buttons):
            btn_rect = self.card_buttons[self.selected_index].rect
            self.selector_rect.topleft = btn_rect.topleft
            self.selector_rect.size = btn_rect.size

        # Status timer
        if self.status_counter > 0:
            self.status_counter -= 1

    def draw(self, surf):
        if self.rect.y > self.screen_height and self.overlay_alpha <= 0:
            return

        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), flags=pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.overlay_alpha))
        surf.blit(overlay, (0, 0))

        # Popup background
        popup_surface = pygame.Surface((self.rect.width, self.rect.height))
        popup_surface.fill(self.bg_color)
        surf.blit(popup_surface, (self.rect.x, self.rect.y))
        pygame.draw.rect(surf, self.border_color, self.rect, 2)

        # Draw elements (title, close, delete)
        for el in self.elements:
            # don't draw delete button if there are no cards
            if el is self.delete_btn and not self.card_buttons:
                continue
            el.draw(surf)

        # --- LIST CLIP WINDOW + BORDER ---
        list_clip = self._get_list_clip_rect_global()

        # subtle darker background inside list area
        list_bg = pygame.Surface((list_clip.width, list_clip.height), pygame.SRCALPHA)
        list_bg.fill((80, 40, 20, 180))
        surf.blit(list_bg, list_clip.topleft)

        # clear, single border around the scroll area
        pygame.draw.rect(surf, (255, 255, 255), list_clip, 2)

        # Show scroll arrows if applicable (visual hint it's scrollable)
        can_scroll_up = self.scroll_offset < self.max_scroll_offset
        can_scroll_down = self.scroll_offset > self.min_scroll_offset

        if can_scroll_up:
            arrow_up = BP.render("▲", True, (255, 255, 255))
            arrow_up_rect = arrow_up.get_rect(midtop=(list_clip.centerx, list_clip.top + 4))
            surf.blit(arrow_up, arrow_up_rect)

        if can_scroll_down:
            arrow_down = BP.render("▼", True, (255, 255, 255))
            arrow_down_rect = arrow_down.get_rect(midbottom=(list_clip.centerx, list_clip.bottom - 4))
            surf.blit(arrow_down, arrow_down_rect)

        # Set clipping so rows are visually cut off at top/bottom
        old_clip = surf.get_clip()
        surf.set_clip(list_clip)

        # If there are no cards, display a centered message inside the list area
        if not self.card_buttons:
            empty_text = BP.render("Nincsenek kártyák!", True, (255, 255, 255))
            empty_rect = empty_text.get_rect(center=list_clip.center)
            surf.blit(empty_text, empty_rect)
        else:
            # Draw card rows (clipped)
            for btn in self.card_buttons:
                btn.draw(surf)

            # Draw selection highlight (also clipped)
            if self.selector_rect:
                pygame.draw.rect(surf, self.selector_color, self.selector_rect, 4)

        # Restore clip
        surf.set_clip(old_clip)

        # Status text
        if self.status_counter > 0:
            status_surf = BP.render("Kártya törölve!", True, (255, 255, 0))
            status_rect = status_surf.get_rect(
                midbottom=(self.rect.x + self.rect.width - 200, self.rect.y + self.rect.height - 20)
            )
            surf.blit(status_surf, status_rect)

    def close(self):
        self.closing = True
        self.opening = False
