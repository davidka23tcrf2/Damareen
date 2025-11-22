import pygame

def ease_in_out(t):
    """Quadratic ease-in-out easing"""
    if t < 0.5:
        return 2 * t * t
    return -1 + (4 - 2 * t) * t

class UIStateManager:
    def __init__(self, screen_size):
        self.screens = {}
        self.active = None
        self.next_screen = None
        self.is_transitioning = False
        self.transition_progress = 0.0
        self.transition_duration = 0.5
        self.screen_size = screen_size
        self.transition_callback = None

        # Card swipe properties
        self.card_color = (0, 0, 0)          # black card
        self.card_width_ratio = 0.06         # narrower card (6% of screen width)
        self.shadow_width = 10               # width of gradient shadow
        self.last_direction_left_to_right = True

    def add(self, name, screen):
        self.screens[name] = screen

    def set(self, name):
        self.active = self.screens[name]

    def switch_to(self, name, duration=None, callback=None):
        if self.is_transitioning:
            return
        self.next_screen = self.screens[name]
        self.transition_progress = 0.0
        self.transition_duration = duration if duration else self.transition_duration
        self.is_transitioning = True
        self.transition_callback = callback
        # Alternate direction
        self.last_direction_left_to_right = not self.last_direction_left_to_right

    def handle_event(self, event):
        if self.active:
            self.active.handle_event(event)
        if self.is_transitioning and self.next_screen:
            self.next_screen.handle_event(event)

    def update(self, dt):
        if self.is_transitioning:
            self.transition_progress += dt / self.transition_duration
            if self.transition_progress >= 1.0:
                self.transition_progress = 1.0
                self.active = self.next_screen
                self.next_screen = None
                self.is_transitioning = False
                if self.transition_callback:
                    self.transition_callback()
        if self.active:
            self.active.update(dt)
        if self.is_transitioning and self.next_screen:
            self.next_screen.update(dt)

    def draw(self, surf):
        w, h = self.screen_size

        # Draw active screen
        if self.active:
            self.active.draw(surf)

        if self.is_transitioning and self.next_screen:
            t = ease_in_out(self.transition_progress)

            # Draw next screen fully in background
            next_surface = pygame.Surface((w, h)).convert_alpha()
            next_surface.fill((0,0,0,0))
            self.next_screen.draw(next_surface)
            surf.blit(next_surface, (0,0))

            # Determine card position
            card_width = int(w * self.card_width_ratio)
            direction = self.last_direction_left_to_right

            # Draw old/new screen slices
            if direction:
                # Left → Right
                card_x = int(-card_width + t * (w + card_width))
                if card_x > 0:
                    surf.blit(next_surface, (0,0), area=pygame.Rect(0,0,card_x,h))
                if card_x < w:
                    old_surface = pygame.Surface((w,h)).convert_alpha()
                    old_surface.fill((0,0,0,0))
                    self.active.draw(old_surface)
                    surf.blit(old_surface, (card_x,0), area=pygame.Rect(card_x,0,w-card_x,h))
            else:
                # Right → Left
                card_x = int(w - t * (w + card_width))
                if card_x > 0:
                    old_surface = pygame.Surface((w,h)).convert_alpha()
                    old_surface.fill((0,0,0,0))
                    self.active.draw(old_surface)
                    surf.blit(old_surface, (0,0), area=pygame.Rect(0,0,card_x,h))
                if card_x < w:
                    surf.blit(next_surface, (card_x,0), area=pygame.Rect(card_x,0,w-card_x,h))

            # Draw the black card (straight edges)
            card_rect = pygame.Rect(card_x, 0, card_width, h)
            pygame.draw.rect(surf, self.card_color, card_rect)

            # Draw soft gradient shadow along trailing edge
            shadow_surface = pygame.Surface((card_width, h), pygame.SRCALPHA)
            for i in range(self.shadow_width):
                alpha = int(120 * (1 - i / self.shadow_width))
                if direction:
                    # Shadow on right side
                    shadow_surface.fill((0,0,0,alpha), rect=pygame.Rect(card_width-1-i,0,1,h))
                else:
                    # Shadow on left side
                    shadow_surface.fill((0,0,0,alpha), rect=pygame.Rect(i,0,1,h))
            surf.blit(shadow_surface, card_rect.topleft)
