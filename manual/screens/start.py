from manual.ui.button import Button
from manual.ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.ui import theme
from manual.ui.particles import ParticleManager
import os, pygame, math

pygame.init()

# Load Saphifen Font
SAPHIFEN_PATH = os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf")
BUTTON_FONT = pygame.font.Font(SAPHIFEN_PATH, 32)
TITLE_FONT = pygame.font.Font(SAPHIFEN_PATH, 96)


class StartScreen:
    def __init__(self, config, load_game, continue_game):
        self.elements = []
        
        # Particles (Red Dust)
        self.particles = ParticleManager(mode="blood")  # Reusing blood mode for red particles

        # Buttons with Red Outline Style
        btn_width = 350
        btn_height = 70
        center_x = 1280 // 2 - btn_width // 2
        
        # Red Theme Colors
        RED_BRIGHT = (255, 50, 50)
        RED_DARK = (150, 0, 0)
        
        # Helper to create outline button
        def make_outline_btn(y, text, callback):
            return Button(
                (center_x, y, btn_width, btn_height),
                callback,
                None,
                text=text,
                font=BUTTON_FONT,
                text_color=RED_BRIGHT,
                bg_color=None,  # Transparent
                hover_bg_color=(50, 10, 10),  # Subtle red tint on hover
                border_color=RED_BRIGHT,
                border_radius=8
            )
        
<<<<<<< Updated upstream
        self.elements.append(make_outline_btn(350, "Kornyezetek", load_game))
        self.elements.append(make_outline_btn(440, "Uj kornyezet", config))
        self.elements.append(make_outline_btn(530, "Jatek folytatasa", continue_game))
=======
        self.elements.append(make_outline_btn(350, "LOAD GAME", load_game))
        self.elements.append(make_outline_btn(440, "SETTINGS", config))
        self.elements.append(make_outline_btn(530, "CONTINUE", continue_game))
>>>>>>> Stashed changes

        # Lighting Setup
        self.light_mask = pygame.Surface((1280, 720))
        # Bigger radius for wide flashlight with long, smooth fade
        self.flashlight_img = self._create_flashlight_gradient(650)

    def _create_flashlight_gradient(self, radius):
        """
        Creates a large, smooth radial gradient used as the flashlight mask.
        Uses a smoothstep falloff for a soft edge and big fade.
        """
        # Work at a lower resolution then scale up for performance & smoothness
        tex_size = 512
        tex_radius = tex_size // 2
        texture = pygame.Surface((tex_size, tex_size), pygame.SRCALPHA)

        for y in range(tex_size):
            for x in range(tex_size):
                dx = x - tex_radius
                dy = y - tex_radius
                dist = math.sqrt(dx * dx + dy * dy)

                if dist < tex_radius:
                    # Normalized distance from center [0, 1]
                    t = dist / tex_radius

                    # Smoothstep-style curve for smooth falloff:
                    # base_smooth goes from 0 at center to 1 at edge
                    base_smooth = 3 * t * t - 2 * t * t * t
                    # invert so center = 1, edge = 0
                    smooth = 1.0 - base_smooth

                    intensity = int(255 * smooth)
                    # Grey value in RGB, alpha 255
                    texture.set_at((x, y), (intensity, intensity, intensity, 255))

        # Scale to desired radius in screen space
        return pygame.transform.smoothscale(texture, (radius * 2, radius * 2))

    def handle_event(self, e):
        for el in self.elements:
            el.handle_event(e)

    def update(self, dt):
        self.particles.update(dt)
        for el in self.elements:
            el.update(dt)

    def draw(self, surf):
        # 1. Fill Background Black
        surf.fill((0, 0, 0))
        
        # 2. Draw Particles
        self.particles.draw(surf)
        
        # 3. Draw Title
        title_surf = TITLE_FONT.render("DAMAREEN", True, (255, 20, 20))
        title_rect = title_surf.get_rect(center=(640, 180))
        # Add a subtle glow/shadow to title
        shadow_surf = TITLE_FONT.render("DAMAREEN", True, (100, 0, 0))
        surf.blit(shadow_surf, title_rect.move(4, 4))
        surf.blit(title_surf, title_rect)
        
        # 4. Draw Elements
        for el in self.elements:
            el.draw(surf)
            
        # 5. Apply Flashlight Mask
        # Ambient light is PITCH BLACK
        self.light_mask.fill((0, 0, 0))
        
        # Draw flashlight at mouse pos
        mx, my = pygame.mouse.get_pos()
        offset_x = mx - self.flashlight_img.get_width() // 2
        offset_y = my - self.flashlight_img.get_height() // 2
        
        # Add the flashlight gradient into the mask
        self.light_mask.blit(self.flashlight_img, (offset_x, offset_y), special_flags=pygame.BLEND_RGBA_ADD)
        
        # Multiply screen by mask: white = fully visible, black = fully dark
        surf.blit(self.light_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
