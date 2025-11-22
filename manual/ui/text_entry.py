import pygame

class TextEntry:
    """Simple but full-featured text entry field for Pygame.

    - rect: (x,y,w,h)
    - font: pygame.font.Font
    - numeric_only / letters_only: filters input
    - max_length: optional int
    """

    def __init__(self, rect, font, color=(0,0,0), bg_color=(255,255,255),
                 max_length=None, numeric_only=False, letters_only=False):
        self.rect = pygame.Rect(rect)
        self.base_pos = self.rect.topleft  # useful for popup-relative placement
        self.font = font
        self.color = color
        self.bg_color = bg_color

        self.text = ""
        self.active = False

        self.max_length = max_length
        self.numeric_only = bool(numeric_only)
        self.letters_only = bool(letters_only)

        # caret blinking
        self.caret_visible = True
        self.caret_timer = 0.0
        self.caret_blink_interval = 0.5  # seconds

        # padding for text inside box
        self.padding_x = 6
        self.padding_y = max(0, (self.rect.height - self.font.get_height()) // 2)

        # cached rendered surface
        self._rebuild_render()

    # ---- internal helpers ----
    def _rebuild_render(self):
        self.text_surf = self.font.render(self.text, True, self.color)
        # caret x position relative to rect
        self.caret_x = self.rect.x + self.padding_x + self.text_surf.get_width()

    # ---- public API ----
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

    # ---- event handling ----
    def handle_event(self, event):
        """
        Handle a pygame event.

        Returns:
            True if the event was handled (should not propagate).
            Or returns the string 'TAB' if user pressed Tab while focused (useful to move focus).
            False if not handled.
        """
        # Mouse click: focus/unfocus
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.focus()
                return True
            else:
                # clicking outside unfocuses
                if self.active:
                    self.unfocus()
                return False

        # If not focused, we generally don't handle keyboard events
        if not self.active:
            return False

        # Keyboard while focused
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
                    self._rebuild_render()
                return True
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                # commit / unfocus on Enter (customize if you want different behaviour)
                self.unfocus()
                return True
            if event.key == pygame.K_TAB:
                # signal to caller to focus next field
                self.unfocus()
                return "TAB"
            # ordinary character input
            ch = event.unicode
            if not ch:
                return True  # swallow non-character keys
            # filters
            if self.letters_only and not ch.isalpha():
                return True
            if self.numeric_only:
                # allow digits and leading '-' for negative numbers
                if not (ch.isdigit() or (ch == '-' and len(self.text) == 0)):
                    return True
            # max length
            if self.max_length is None or len(self.text) < self.max_length:
                self.text += ch
                self._rebuild_render()
            return True

        return False

    # ---- time-based updates (caret blink) ----
    def update(self, dt):
        if self.active:
            self.caret_timer += dt
            if self.caret_timer >= self.caret_blink_interval:
                self.caret_timer -= self.caret_blink_interval
                self.caret_visible = not self.caret_visible
        else:
            self.caret_visible = False

    # ---- drawing ----
    def draw(self, surf):
        # background
        pygame.draw.rect(surf, self.bg_color, self.rect)
        # border
        pygame.draw.rect(surf, (0,0,0), self.rect, 2)
        # text
        surf.blit(self.text_surf, (self.rect.x + self.padding_x, self.rect.y + self.padding_y))
        # caret
        if self.active and self.caret_visible:
            caret_x = self.rect.x + self.padding_x + self.text_surf.get_width()
            top = self.rect.y + self.padding_y
            bottom = top + self.font.get_height()
            pygame.draw.line(surf, self.color, (caret_x, top), (caret_x, bottom), 2)
