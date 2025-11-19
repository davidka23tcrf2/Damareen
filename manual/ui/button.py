import pygame
class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = pygame.font.SysFont(None, 28)
        self.hover = False
    def handle_event(self, e):
        if e.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(e.pos)
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.callback()
    def update(self, dt):
        pass
    def draw(self, surf):
        color = (180,180,180) if self.hover else (120,120,120)
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        t = self.font.render(self.text, True, (255,255,255))
        surf.blit(t, t.get_rect(center=self.rect.center))