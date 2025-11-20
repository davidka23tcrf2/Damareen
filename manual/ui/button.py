import pygame

class Button:
    def __init__(self, rect, callback, normal_image, hover_image, text="", font=None, font_size=28, text_color=(255,255,255),
                 center_x=False, hover_callback=None, screen_width=1280):
        self.rect = pygame.Rect(rect)
        if center_x:
            self.rect.x = screen_width // 2 - self.rect.width // 2

        self.callback = callback
        self.hover_callback = hover_callback
        self.normal_image = normal_image
        self.hover_image = hover_image
        self.hover = False

        self.text = text
        self.text_color = text_color

        # If font is a pygame.font.Font object, use it directly
        # If font is a string, create a SysFont with the given size
        if isinstance(font, pygame.font.Font):
            self.font = font
        else:
            self.font = pygame.font.SysFont(font or "Arial", font_size)

    def handle_event(self, e):
        is_hovering = self.rect.collidepoint(pygame.mouse.get_pos())
        if is_hovering and not self.hover:
            self.hover = True
            if self.hover_callback:
                self.hover_callback()
        elif not is_hovering and self.hover:
            self.hover = False
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.callback()

    def update(self, dt):
        pass

    def draw(self, surf):
        image = self.hover_image if self.hover else self.normal_image
        surf.blit(image, self.rect)

        if self.text:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surf.blit(text_surf, text_rect)

        # Debug border
        pygame.draw.rect(surf, (255, 0, 0), self.rect, 2)
