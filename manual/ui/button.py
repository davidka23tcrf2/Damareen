import pygame

class Button:
    def __init__(self, rect, callback, normal_image, hover_image, hover_callback=None):
        self.rect = pygame.Rect(rect)
        self.callback = callback
        self.hover_callback = hover_callback
        self.normal_image = normal_image
        self.hover_image = hover_image
        self.hover = False

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
