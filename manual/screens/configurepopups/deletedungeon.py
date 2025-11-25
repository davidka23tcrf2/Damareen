from manual.inventory import inventory
import pygame
import os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR

sf = "configure"
pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 24)
BP26 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 30)

class DeleteDungeonPopup:
    """Popup that lists existing dungeons (enemies) and lets you delete one."""

    def __init__(self, close_callback, screen_size=(1280, 720)):
        screen_width, screen_height = screen_size
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Popup size and placement
        w, h = 832, 468
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        self.target_rect = pygame.Rect(x, y, w, h)
        self.rect = pygame.Rect(x, screen_height, w, h)

        # Colors
        self.bg_color = (100, 50, 50) # Dark red/brown
        self.border_color = (0, 0, 0)

        self.elements = []
        self.card_buttons = []
        self.selected_index = -1

        # Scrolling
        self.scroll_offset = 0
        self.list_x = 120
        self.list_y = 120
        self.row_h = 40
        self.row_spacing = 0
        self.row_w = 550
        self.list_visible_height = h - self.list_y - 120
        self.min_scroll_offset = 0
        self.max_scroll_offset = 0

        # Close Button
        close_img = load_asset("closebutton.png", sf)
        self.close_btn = Button((0, 0, 98, 98), close_callback, close_img)
        self.elements.append(self.close_btn)

        # Title
        self.elements.append(
            Label((350, 50, 0, 0), "Kazamata törlése", font=BP26, color=(255, 255, 255))
        )

        # Delete Button
        del_w, del_h = 250, 80
        del_x, del_y = 500, 350

        del_surface = pygame.Surface((del_w, del_h), pygame.SRCALPHA)
        pygame.draw.rect(del_surface, (200, 50, 50), del_surface.get_rect(), border_radius=0)
        pygame.draw.rect(del_surface, (0, 0, 0), del_surface.get_rect(), width=4, border_radius=0)
        del_label = BP26.render("Törlés", True, (0, 0, 0))
        del_label_rect = del_label.get_rect(center=(del_w // 2, del_h // 2))
        del_surface.blit(del_label, del_label_rect)

        self.delete_btn = Button(
            (del_x, del_y, del_w, del_h),
            self.delete_selected,
            del_surface
        )
        self.elements.append(self.delete_btn)

        self.status_counter = 0
        self.selector_color = (255, 0, 0)
        self.selector_rect = None

        self.opening = True
        self.closing = False
        self.overlay_alpha = 0
        self.max_overlay_alpha = 150
        self.overlay_speed = 20
        self.active = True

        self.build_list()

        for el in self.elements:
            el.base_rect = el.rect.copy()

    def _recalculate_scroll_limits(self):
        total_rows = len(self.card_buttons)
        if total_rows == 0:
            self.scroll_offset = 0
            self.min_scroll_offset = 0
            self.max_scroll_offset = 0
            return

        content_height = total_rows * (self.row_h + self.row_spacing) - self.row_spacing
        if content_height <= self.list_visible_height:
            self.min_scroll_offset = 0
            self.max_scroll_offset = 0
        else:
            self.max_scroll_offset = 0
            self.min_scroll_offset = self.list_visible_height - content_height

        self.scroll_offset = max(self.min_scroll_offset, min(self.scroll_offset, self.max_scroll_offset))

    def _get_list_clip_rect_global(self):
        return pygame.Rect(
            self.rect.x + self.list_x,
            self.rect.y + self.list_y,
            self.row_w,
            self.list_visible_height,
        )

    def build_list(self):
        self.card_buttons.clear()
        self.selected_index = -1
        self.selector_rect = None
        self.scroll_offset = 0

        for i, enemy in enumerate(inventory.ENEMIES):
            y = self.list_y + i * (self.row_h + self.row_spacing)

            row_surface = pygame.Surface((self.row_w, self.row_h), pygame.SRCALPHA)
            pygame.draw.rect(row_surface, (230, 230, 230), row_surface.get_rect())
            pygame.draw.rect(row_surface, (50, 50, 50), row_surface.get_rect(), 1)

            name = getattr(enemy, "name", "???")
            type_ = getattr(enemy, "type", "?")
            reward = getattr(enemy, "reward", "None")
            if reward is None: reward = "Nincs"

            text = f"{name} ({type_}) - {reward}"
            text_surf = BP.render(text, True, (0, 0, 0))
            text_rect = text_surf.get_rect(midleft=(10, self.row_h // 2))
            row_surface.blit(text_surf, text_rect)

            btn = Button(
                (self.list_x, y, self.row_w, self.row_h),
                lambda idx=i: self.select_item(idx),
                row_surface
            )
            btn.base_pos = btn.rect.topleft
            self.card_buttons.append(btn)

        if self.card_buttons:
            self.selected_index = 0
            first_rect = self.card_buttons[0].rect
            self.selector_rect = pygame.Rect(first_rect.topleft, first_rect.size)

        self._recalculate_scroll_limits()

    def select_item(self, index):
        if 0 <= index < len(self.card_buttons):
            self.selected_index = index
            btn_rect = self.card_buttons[index].rect
            self.selector_rect = pygame.Rect(btn_rect.topleft, btn_rect.size)

    def delete_selected(self):
        if self.selected_index < 0 or self.selected_index >= len(inventory.ENEMIES):
            return

        del inventory.ENEMIES[self.selected_index]
        self.build_list()
        self.status_counter = 60

    def is_closed(self):
        return not self.opening and not self.closing and self.rect.y >= self.screen_height

    def reopen(self):
        if self.is_closed():
            self.rect.y = self.screen_height
            self.opening = True
            self.closing = False
            self.overlay_alpha = 0
            self.active = True
            self.build_list()

    def handle_event(self, event):
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            if not self.rect.collidepoint(event.pos):
                return True

        list_clip = self._get_list_clip_rect_global()

        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if list_clip.collidepoint(mx, my):
                scroll_step = 20
                self.scroll_offset += event.y * scroll_step
                self.scroll_offset = max(
                    self.min_scroll_offset, min(self.scroll_offset, self.max_scroll_offset)
                )

        for el in self.elements:
            if el is self.delete_btn and (self.selected_index < 0 or not self.card_buttons):
                continue
            el.handle_event(event)

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            for btn in self.card_buttons:
                if btn.rect.colliderect(list_clip):
                    btn.handle_event(event)
        else:
            for btn in self.card_buttons:
                btn.handle_event(event)

        return True

    def update(self, dt):
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

        for el in self.elements:
            el.rect.topleft = (self.rect.x + el.base_rect.x, self.rect.y + el.base_rect.y)
            el.update(dt)

        for btn in self.card_buttons:
            base_x, base_y = btn.base_pos
            btn.rect.topleft = (
                self.rect.x + base_x,
                self.rect.y + base_y + self.scroll_offset
            )
            btn.update(dt)

        if self.selector_rect and 0 <= self.selected_index < len(self.card_buttons):
            btn_rect = self.card_buttons[self.selected_index].rect
            self.selector_rect.topleft = btn_rect.topleft
            self.selector_rect.size = btn_rect.size

        if self.status_counter > 0:
            self.status_counter -= 1

    def draw(self, surf):
        if self.rect.y > self.screen_height and self.overlay_alpha <= 0:
            return

        overlay = pygame.Surface((self.screen_width, self.screen_height), flags=pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.overlay_alpha))
        surf.blit(overlay, (0, 0))

        pygame.draw.rect(surf, self.bg_color, self.rect)
        pygame.draw.rect(surf, self.border_color, self.rect, 2)

        for el in self.elements:
            if el is self.delete_btn and not self.card_buttons:
                continue
            el.draw(surf)

        list_clip = self._get_list_clip_rect_global()
        list_bg = pygame.Surface((list_clip.width, list_clip.height), pygame.SRCALPHA)
        list_bg.fill((80, 40, 20, 180))
        surf.blit(list_bg, list_clip.topleft)
        pygame.draw.rect(surf, (255, 255, 255), list_clip, 2)

        old_clip = surf.get_clip()
        surf.set_clip(list_clip)

        if not self.card_buttons:
            empty_text = BP.render("Nincsenek kazamaták!", True, (255, 255, 255))
            empty_rect = empty_text.get_rect(center=list_clip.center)
            surf.blit(empty_text, empty_rect)
        else:
            for btn in self.card_buttons:
                btn.draw(surf)
            if self.selector_rect:
                pygame.draw.rect(surf, self.selector_color, self.selector_rect, 4)

        surf.set_clip(old_clip)

        if self.status_counter > 0:
            status_surf = BP.render("Kazamata törölve!", True, (255, 255, 0))
            status_rect = status_surf.get_rect(
                midbottom=(self.rect.x + self.rect.width - 200, self.rect.y + self.rect.height - 20)
            )
            surf.blit(status_surf, status_rect)

    def close(self):
        self.closing = True
        self.opening = False
