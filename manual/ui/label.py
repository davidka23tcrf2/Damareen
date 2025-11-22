import pygame

class Label:
    def __init__(self, rect, text, font, color=(0, 0, 0)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.font = font

        self.base_rect = self.rect.copy()

        # NEW: render multiline
        self._render_multiline()

    def _render_multiline(self):
        """Render text with newline support, but change nothing else."""
        lines = self.text.split("\n")

        # Render each line
        self.rendered_lines = [self.font.render(line, True, self.color) for line in lines]

        # Compute total height
        total_height = sum(line.get_height() for line in self.rendered_lines)
        y = self.rect.centery - total_height // 2

        # Compute rects for each line
        self.text_rects = []
        for surf in self.rendered_lines:
            rect = surf.get_rect(center=(self.rect.centerx, y + surf.get_height() // 2))
            self.text_rects.append(rect)
            y += surf.get_height()

    def set_text(self, new_text):
        self.text = new_text
        self._render_multiline()

    def set_color(self, new_color):
        self.color = new_color
        self._render_multiline()

    def set_position(self, x, y):
        self.rect.topleft = (x, y)
        self._render_multiline()

    def update(self, dt):
        # keeps compatibility
        self._render_multiline()

    def draw(self, surface):
        for surf, rect in zip(self.rendered_lines, self.text_rects):
            surface.blit(surf, rect)

    def handle_event(self, e):
        pass
