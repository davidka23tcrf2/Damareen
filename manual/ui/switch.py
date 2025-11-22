import pygame

class Switch:
    """
    Rectangular toggle switch with sliding knob animation.

    - rect: (x,y,w,h) or pygame.Rect
    - callback: function(new_state) called when the switch changes
    - speed: pixels per second for knob movement OR set to None to use easing
    - initial: initial boolean state
    - on_image/off_image/hover_image: optional images (kept for compatibility)
    """

    def __init__(self, rect, callback=None, initial=False,
                 on_image=None, off_image=None, hover_image=None,
                 speed=800):
        self.rect = pygame.Rect(rect)
        self.callback = callback

        self.on_image = on_image
        self.off_image = off_image
        self.hover_image = hover_image

        self.state = bool(initial)
        self.hover = False
        self._pressed = False

        # geometry
        self._pad = max(3, int(self.rect.height * 0.12))
        # knob is half the width (rectangular style)
        self._knob_w = max(8, (self.rect.width // 2) - (self._pad * 2))
        self._knob_h = self.rect.height - (self._pad * 2)

        # animation: knob_x is the current x coordinate of the knob
        # set initial position based on initial state
        self._left_x = self.rect.x + self._pad
        self._right_x = self.rect.right - self._pad - self._knob_w
        self._knob_x = self._right_x if self.state else self._left_x

        # animation control:
        # if speed is not None, use constant speed (pixels/sec) to move knob;
        # otherwise use easing (lerp) with factor in update.
        self.speed = speed  # pixels per second or None
        self._easing = 12.0  # used only if speed is None (higher = snappier)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self._pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self._pressed:
                self._pressed = False
                if self.rect.collidepoint(event.pos):
                    self.toggle()

    def update(self, dt):
        """
        dt: seconds since last frame (float)
        Moves the knob toward target x depending on self.state.
        """
        target = self._right_x if self.state else self._left_x

        if self._knob_x == target:
            return

        if self.speed is not None:
            # move at constant pixels/sec toward target
            direction = 1 if target > self._knob_x else -1
            move_amount = self.speed * dt * direction
            new_x = self._knob_x + move_amount
            # clamp to avoid overshoot
            if direction == 1:
                self._knob_x = min(new_x, target)
            else:
                self._knob_x = max(new_x, target)
        else:
            # easing (lerp) approach - frame-rate independent-ish
            t = 1 - pow(1 - min(1.0, self._easing * dt), 1.0)
            self._knob_x = self._knob_x + (target - self._knob_x) * t

    def draw(self, surf):
        # — IMAGE MODE — (kept for compatibility)
        if self.hover_image and self.hover:
            img = pygame.transform.smoothscale(self.hover_image, self.rect.size)
            surf.blit(img, self.rect.topleft)
            return

        if self.on_image is not None and self.off_image is not None:
            img = self.on_image if self.state else self.off_image
            img = pygame.transform.smoothscale(img, self.rect.size)
            surf.blit(img, self.rect.topleft)
            return

        # — RECTANGLE MODE WITH SLIDING KNOB —
        bg_color = (0, 160, 70) if self.state else (110, 110, 110)
        if self.hover:
            bg_color = tuple(min(255, c + 18) for c in bg_color)

        # background
        pygame.draw.rect(surf, bg_color, self.rect)

        # knob rect using current animated _knob_x
        knob_rect = pygame.Rect(int(self._knob_x),
                                self.rect.y + self._pad,
                                self._knob_w,
                                self._knob_h)
        # knob shadow
        shadow_rect = knob_rect.move(2, 2)
        # try alpha-friendly drawing: create a temporary surface for shadow if you want true alpha.
        pygame.draw.rect(surf, (0, 0, 0, 80), shadow_rect)
        pygame.draw.rect(surf, (245, 245, 245), knob_rect)

        # border
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)

    def toggle(self):
        old = self.state
        self.state = not self.state
        # optionally ensure target starts from exact position (prevents tiny drift)
        # Not changing _knob_x here so animation flows from current position.
        if callable(self.callback):
            try:
                self.callback(self.state)
            except TypeError:
                self.callback()

    def set_state(self, v: bool):
        self.state = bool(v)
        # optionally snap knob to exact target immediately:
        # self._knob_x = self._right_x if self.state else self._left_x

    def get_state(self) -> bool:
        return self.state
