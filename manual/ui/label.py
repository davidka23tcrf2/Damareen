import pygame

class Label:
    def __init__(self, rect, text, font, color=(0, 0, 0)):
        """
        Creates a text label for Pygame using a rectangle for position/size.

        Args:
            rect (tuple): (x, y, width, height) for the label area.
            text (str): The text to display.
            font (pygame.font.Font): Preloaded Pygame font object.
            color (tuple): RGB color of the text.
        """
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.font = font

        # Save initial rect for popup-relative movement
        self.base_rect = self.rect.copy()

        # Render text surface
        self.rendered_text = self.font.render(self.text, True, self.color)
        self.text_rect = self.rendered_text.get_rect(center=self.rect.center)

    def set_text(self, new_text):
        """Update the label's text."""
        self.text = new_text
        self.rendered_text = self.font.render(self.text, True, self.color)
        self.update(0)  # update text_rect

    def set_color(self, new_color):
        """Change text color."""
        self.color = new_color
        self.rendered_text = self.font.render(self.text, True, self.color)
        self.update(0)

    def set_position(self, x, y):
        """Set the top-left position of the label."""
        self.rect.topleft = (x, y)
        self.update(0)

    def update(self, dt):
        """
        Call every frame. Keeps the text centered in the current rect.
        Also useful if the label is moving with a popup.
        """
        self.text_rect = self.rendered_text.get_rect(center=self.rect.center)

    def draw(self, surface):
        """Draw the label on the given surface."""
        surface.blit(self.rendered_text, self.text_rect)

    # Optional stubs for interface compatibility with buttons
    def handle_event(self, e):
        pass
