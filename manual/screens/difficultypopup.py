import pygame, os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory import inventory

pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 36)
BP_TITLE = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 50)

class DifficultyPopup:
    def __init__(self, close_callback, screen_size=(1280, 720)):
        self.screen_width, self.screen_height = screen_size
        self.close_callback = close_callback
        
        # Popup dimensions
        w, h = 800, 500
        x = (self.screen_width - w) // 2
        y = (self.screen_height - h) // 2
        self.rect = pygame.Rect(x, y, w, h)
        
        self.bg_color = (0, 0, 0)
        self.border_color = (255, 50, 50)
        
        self.elements = []
        
        # Title
        self.title_label = Label(
            (w // 2, 50, 0, 0), 
            "Válassz nehézséget!", 
            font=BP_TITLE, 
            color=(255, 255, 255)
        )
        self.title_label.base_pos = (w // 2, 150)
        self.elements.append(self.title_label)
        
        # Buttons 0-10
        btn_size = 60
        gap = 20
        start_y = 200
        
        for i in range(0, 11):
            row = i // 6
            col = i % 6
            
            # First row has 6 buttons, second row has 5
            if row == 0:
                # First row: 6 buttons
                start_x = (w - (6 * btn_size + 5 * gap)) // 2
            else:
                # Second row: 5 buttons - center them
                start_x = (w - (5 * btn_size + 4 * gap)) // 2
            
            bx = start_x + col * (btn_size + gap)
            by = start_y + row * (btn_size + gap)
            
            # Create button
            btn = Button(
                (bx, by, btn_size, btn_size),
                lambda val=i: self.select_difficulty(val),
                None,
                text=str(i),
                font=BP,
                text_color=(255, 50, 50),
                bg_color=None,
                hover_bg_color=(50, 10, 10),
                border_color=(255, 50, 50),
                border_radius=0
            )
            # Store relative position for drawing
            btn.base_pos = (bx, by)
            self.elements.append(btn)

        self.active = True
        
        # Animation
        self.animation_time = 0.0
        self.animation_duration = 0.3  # seconds
        self.closing = False
        self.close_animation_time = 0.0

    def select_difficulty(self, value):
        inventory.DIFFICULTY = value
        inventory.DIFFICULTY_SELECTED = True
        print(f"Difficulty selected: {value}")
        self.close_callback()
        self.active = False

    def handle_event(self, event):
        if not self.active: return
        
        # Absorb clicks inside popup
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            if not self.rect.collidepoint(event.pos):
                return True

        for el in self.elements:
            # Update rect to be absolute before handling event
            if hasattr(el, 'base_pos'):
                if isinstance(el, Label) and getattr(el, 'centered', False):
                     center_x = self.rect.x + el.base_pos[0]
                     center_y = self.rect.y + el.base_pos[1]
                     el.rect.center = (center_x, center_y)
                else:
                    el.rect.topleft = (self.rect.x + el.base_pos[0], self.rect.y + el.base_pos[1])
                
            el.handle_event(event)
            
        return True

    def update(self, dt):
        if not self.active: return
        
        # Update animation
        if self.closing:
            self.close_animation_time += dt
            if self.close_animation_time >= self.animation_duration:
                self.active = False
        else:
            self.animation_time += dt
        
        for el in self.elements:
            el.update(dt)

    def draw(self, surf):
        if not self.active: return
        
        # Determine animation progress
        if self.closing:
            progress = 1.0 - min(1.0, self.close_animation_time / self.animation_duration)
        else:
            progress = min(1.0, self.animation_time / self.animation_duration)
        
        # Ease out cubic
        ease_progress = 1 - pow(1 - progress, 3)
        
        # Draw overlay with fade
        overlay_alpha = int(200 * ease_progress)
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, overlay_alpha))
        surf.blit(overlay, (0, 0))
        
        # Scale popup from center
        scale = 0.8 + (0.2 * ease_progress)
        
        # Calculate scaled popup rect
        scaled_width = int(self.rect.width * scale)
        scaled_height = int(self.rect.height * scale)
        scaled_x = self.rect.centerx - scaled_width // 2
        scaled_y = self.rect.centery - scaled_height // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        
        # Draw popup background and border
        pygame.draw.rect(surf, self.bg_color, scaled_rect, border_radius=15)
        pygame.draw.rect(surf, self.border_color, scaled_rect, width=3, border_radius=15)
        
        # Only draw content if animation is mostly complete
        if progress > 0.3:
            content_alpha = int(255 * ((progress - 0.3) / 0.7))
            
            # Draw elements with alpha
            for el in self.elements:
                # Ensure they are drawn at correct absolute position
                if hasattr(el, 'base_pos'):
                    if isinstance(el, Label) and getattr(el, 'centered', False):
                         center_x = self.rect.x + el.base_pos[0]
                         center_y = self.rect.y + el.base_pos[1]
                         el.rect.center = (center_x, center_y)
                    else:
                        el.rect.topleft = (self.rect.x + el.base_pos[0], self.rect.y + el.base_pos[1])
                
                # Create temp surface for alpha
                temp_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                el.draw(temp_surf)
                temp_surf.set_alpha(content_alpha)
                surf.blit(temp_surf, (0, 0))
