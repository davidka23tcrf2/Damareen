import pygame
import os
from manual.ui import theme
from manual.assets.assets import ASSETS_DIR

class Button:
    # Load button press sound once for all buttons
    _button_sound = None
    _sound_loaded = False
    
    @classmethod
    def _load_sound(cls):
        """Load the button press sound once"""
        if not cls._sound_loaded:
            try:
                sound_path = os.path.join(ASSETS_DIR, "sounds", "button_press.mp3")
                cls._button_sound = pygame.mixer.Sound(sound_path)
                cls._button_sound.set_volume(0.3)  # Set volume to 30%
                cls._sound_loaded = True
            except Exception as e:
                print(f"Warning: Could not load button press sound: {e}")
                cls._sound_loaded = True  # Mark as loaded to avoid repeated attempts
    
    def __init__(
        self,
        rect,
        callback,
        normal_image=None,         # Optional now
        hover_image=None,
        text="",
        font=None,
        font_size=20,
        text_color=theme.TEXT_WHITE,
        bg_color=theme.PRIMARY,    # Default theme color
        hover_bg_color=theme.PRIMARY_HOVER,
        border_color=theme.BORDER_COLOR,
        border_radius=theme.BORDER_RADIUS,
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
        self.hover_image = hover_image
        
        # Auto-generate hover image if none provided but normal exists
        if self.normal_image and not self.hover_image:
             self.hover_image = self._make_hover_image(self.normal_image)

        self.text = text
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_bg_color = hover_bg_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.image_offset = image_offset

        self.hover = False
        self._prev_hover = False
        
        # Load button press sound (only happens once for all buttons)
        Button._load_sound()
        
        # Setup font
        if isinstance(font, pygame.font.Font):
            self.font = font
        else:
            self.font = pygame.font.SysFont("Arial", font_size)

    def _make_hover_image(self, img: pygame.Surface) -> pygame.Surface:
        hover_img = img.copy()
        brighten = 40
        hover_img.fill(
            (brighten, brighten, brighten),
            special_flags=pygame.BLEND_RGB_ADD
        )
        return hover_img

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(e.pos):
                # Play button press sound
                if Button._button_sound:
                    try:
                        Button._button_sound.play()
                    except Exception as e:
                        print(f"Warning: Could not play button press sound: {e}")
                
                if self.callback:
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
        # 1. Draw Background (if no image or if we want a bg behind image)
        
        current_bg = self.hover_bg_color if self.hover else self.bg_color
        
        if self.normal_image is None:
            # Only draw background fill if color is provided (not None)
            if current_bg is not None:
                pygame.draw.rect(surf, current_bg, self.rect, border_radius=self.border_radius)
            
            # Draw border
            # If transparent, maybe we want border color to change on hover?
            # For now, keep border_color constant unless we want to change it.
            # Let's use text_color for border if transparent? Or just keep border_color.
            pygame.draw.rect(surf, self.border_color, self.rect, width=2, border_radius=self.border_radius)
            
            # Hover glow effect (optional)
            if self.hover:
                pygame.draw.rect(surf, (255, 255, 255), self.rect, width=2, border_radius=self.border_radius)

        # 2. Draw Image
        image = self.hover_image if self.hover else self.normal_image
        if image is not None:
            surf.blit(
                image,
                (self.rect.x + self.image_offset[0], self.rect.y + self.image_offset[1])
            )

        # 3. Draw Text
        if self.text:
            lines = self.text.split("\n")
            # Calculate total height
            line_heights = [self.font.size(line)[1] for line in lines]
            total_height = sum(line_heights)
            
            current_y = self.rect.centery - total_height // 2
            
            for line in lines:
                text_surf = self.font.render(line, True, self.text_color)
                text_rect = text_surf.get_rect(center=(self.rect.centerx, current_y + text_surf.get_height() // 2))
                surf.blit(text_surf, text_rect)
                current_y += text_surf.get_height()
