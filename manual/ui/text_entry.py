import pygame
from manual.ui import theme

class TextEntry:
    """Simple but full-featured text entry field for Pygame."""

    def __init__(self, rect, font, color=theme.TEXT_WHITE, bg_color=theme.BG_INPUT,
                 max_length=None, numeric_only=False, letters_only=False):
        self.rect = pygame.Rect(rect)
        self.base_pos = self.rect.topleft
        self.font = font
        self.color = color
        self.bg_color = bg_color
        self.border_color = theme.BORDER_COLOR
        self.focus_color = theme.BORDER_FOCUS

        self.text = ""
        self.active = False

        self.max_length = max_length
        self.numeric_only = bool(numeric_only)
        self.letters_only = bool(letters_only)

        # caret blinking
        self.caret_visible = True
        self.caret_timer = 0.0
        self.caret_blink_interval = 0.5

        # padding
        self.padding_x = 10
        self.padding_y = max(0, (self.rect.height - self.font.get_height()) // 2)

        self._rebuild_render()

    def _rebuild_render(self):
        self.text_surf = self.font.render(self.text, True, self.color)
        self.caret_x = self.rect.x + self.padding_x + self.text_surf.get_width()

    def focus(self):
        self.active = True
        self.caret_visible = True
        self.caret_timer = 0.0

    def unfocus(self):
        self.active = False
        self.caret_visible = False

    def set_text(self, s: str):
        self.text = s
        self._rebuild_render()

    def get_text(self) -> str:
        return self.text

    def set_position(self, x, y):
        self.rect.topleft = (x, y)
        self.base_pos = (x, y)
        self._rebuild_render()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.focus()
                return True
            else:
                if self.active:
                    self.unfocus()
                return False

        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
                    self._rebuild_render()
                return True
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.unfocus()
                return True
            if event.key == pygame.K_TAB:
                self.unfocus()
                return "TAB"
            
            ch = event.unicode
            if not ch:
                return True
            
            if self.letters_only and not ch.isalpha():
                return True
            if self.numeric_only:
                if not (ch.isdigit() or (ch == '-' and len(self.text) == 0)):
                    return True
            
            if self.max_length is None or len(self.text) < self.max_length:
                self.text += ch
                self._rebuild_render()
            return True

        return False

    def update(self, dt):
        if self.active:
            self.caret_timer += dt
            if self.caret_timer >= self.caret_blink_interval:
                self.caret_timer -= self.caret_blink_interval
                self.caret_visible = not self.caret_visible
        else:
            self.caret_visible = False

    def draw(self, surf):
        # Background
        pygame.draw.rect(surf, self.bg_color, self.rect, border_radius=theme.BORDER_RADIUS)
        
        # Border (highlight if active)
        border_col = self.focus_color if self.active else self.border_color
        pygame.draw.rect(surf, border_col, self.rect, 2, border_radius=theme.BORDER_RADIUS)
        
        # Text
        surf.blit(self.text_surf, (self.rect.x + self.padding_x, self.rect.y + self.padding_y))
        
        # Caret
        if self.active and self.caret_visible:
            caret_x = self.rect.x + self.padding_x + self.text_surf.get_width()
            top = self.rect.y + self.padding_y
            bottom = top + self.font.get_height()
            pygame.draw.line(surf, self.color, (caret_x, top), (caret_x, bottom), 2)
