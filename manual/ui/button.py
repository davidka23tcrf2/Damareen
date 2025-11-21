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
        self._prev_hover = False

        self.text = text
        self.text_color = text_color

        if isinstance(font, pygame.font.Font):
            self.font = font
        else:
            self.font = pygame.font.SysFont(font or "Arial", font_size)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.callback()

    def update(self, dt):
        pos = pygame.mouse.get_pos()
        is_hovering = self.rect.collidepoint(pos)
        if is_hovering and not self._prev_hover:
            if self.hover_callback:
                self.hover_callback()
        self.hover = is_hovering
        self._prev_hover = is_hovering

    def draw(self, surf):
        image = self.hover_image if self.hover else self.normal_image
        surf.blit(image, self.rect)

        if self.text:
            lines = self.text.split("\n")

            # vertical positioning
            total_height = sum(self.font.size(line)[1] for line in lines)
            start_y = self.rect.centery - total_height // 2

            # draw each line centered
            for line in lines:
                text_surf = self.font.render(line, True, self.text_color)
                text_rect = text_surf.get_rect(center=(self.rect.centerx, start_y))
                surf.blit(text_surf, text_rect)
                start_y += self.font.size(line)[1]

        pygame.draw.rect(surf, (255, 0, 0), self.rect, 2)

