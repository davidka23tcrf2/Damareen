# label.py
import pygame

class Label:
    def __init__(self, rect, text, font_name="arial", font_size=30, color=(255, 255, 255)):
        """
        Creates a text label for Pygame using a rectangle for position/size.

        Args:
            rect (tuple): (x, y, width, height) for the label area.
            text (str): The text to display.
            font_name (str): Font type.
            font_size (int): Font size.
            color (tuple): RGB color of the text.
        """
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont(font_name, font_size)
        self.update_render()

    def update_render(self):
        """Render the text and center it inside the rect."""
        self.rendered_text = self.font.render(self.text, True, self.color)
        self.text_rect = self.rendered_text.get_rect(center=self.rect.center)

    def set_text(self, new_text):
        self.text = new_text
        self.update_render()

    def set_color(self, new_color):
        self.color = new_color
        self.update_render()

    def set_position(self, x, y):
        self.rect.topleft = (x, y)
        self.update_render()

    def draw(self, surface):
        surface.blit(self.rendered_text, self.text_rect)

    # Optional stubs to match Button interface
    def handle_event(self, e):
        pass

    def update(self, dt):
        pass
