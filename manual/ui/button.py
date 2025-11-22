import pygame

class Button:
    def __init__(
        self,
        rect,
        callback,
        normal_image,
        hover_image=None,          # now optional
        text="",
        font=None,
        font_size=28,
        text_color=(255, 255, 255),
        center_x=False,
        hover_callback=None,
        screen_width=1280,
        image_offset=(0, 0)
    ):
        self.rect = pygame.Rect(rect)
        if center_x:
            self.rect.x = screen_width // 2 - self.rect.width // 2

        self.callback = callback
        self.hover_callback = hover_callback

        self.normal_image = normal_image

        # Auto-generate hover image if none provided
        if hover_image is None and normal_image is not None:
            self.hover_image = self._make_hover_image(normal_image)
        else:
            self.hover_image = hover_image

        self.hover = False
        self._prev_hover = False

        self.text = text
        self.text_color = text_color
        self.image_offset = image_offset

        # Setup font
        if isinstance(font, pygame.font.Font):
            self.font = font
        else:
            self.font = pygame.font.SysFont(font or "Arial", font_size)

    def _make_hover_image(self, img: pygame.Surface) -> pygame.Surface:
        """
        Creates a lighter version of the normal image by adding brightness.
        """
        hover_img = img.copy()
        brighten = 40  # increase for stronger hover effect
        hover_img.fill(
            (brighten, brighten, brighten),
            special_flags=pygame.BLEND_RGB_ADD
        )
        return hover_img

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
        # choose image based on hover
        image = self.hover_image if self.hover else self.normal_image

        if image is not None:
            surf.blit(
                image,
                (self.rect.x + self.image_offset[0], self.rect.y + self.image_offset[1])
            )

        # draw text if provided
        if self.text:
            lines = self.text.split("\n")
            total_height = sum(self.font.size(line)[1] for line in lines)
            start_y = self.rect.centery - total_height // 2

            for line in lines:
                text_surf = self.font.render(line, True, self.text_color)
                text_rect = text_surf.get_rect(center=(self.rect.centerx, start_y))
                surf.blit(text_surf, text_rect)
                start_y += self.font.size(line)[1]

        # debug outline (remove this line if you don’t want red borders)
        pygame.draw.rect(surf, (255, 0, 0), self.rect, 2)
