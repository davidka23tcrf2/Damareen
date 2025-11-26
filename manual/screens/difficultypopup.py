import pygame, os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory import inventory

pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 40)
BP_TITLE = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 60)

class DifficultyPopup:
    def __init__(self, close_callback, screen_size=(1280, 720)):
        self.screen_width, self.screen_height = screen_size
        self.close_callback = close_callback
        
        # Popup dimensions
        w, h = 900, 550
        x = (self.screen_width - w) // 2
        y = (self.screen_height - h) // 2
        self.rect = pygame.Rect(x, y, w, h)
        
        # Horror theme colors
        self.bg_color = (15, 5, 5)  # Very dark red
        self.border_color = (180, 0, 0)  # Blood red
        self.glow_color = (100, 0, 0)  # Dark red glow
        
        self.elements = []
        
        # Title
        self.title_label = Label(
            (w // 2, 60, 0, 0), 
            "Válassz nehézséget!", 
            font=BP_TITLE, 
            color=(255, 200, 200)  # Light red tint
        )
        self.title_label.base_pos = (w // 2, 60)
        self.title_label.centered = True
        self.elements.append(self.title_label)
        
        # Buttons 0-10
        btn_size = 70
        gap = 25
        start_y = 180
        
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
            by = start_y + row * (btn_size + gap + 20)
            
            # Create button with horror styling
            btn = Button(
                (bx, by, btn_size, btn_size),
                lambda val=i: self.select_difficulty(val),
                None,
                text=str(i),
                font=BP,
                text_color=(200, 200, 200),  # Light grey
                bg_color=(40, 10, 10),  # Dark red background
                hover_bg_color=(180, 0, 0),  # Blood red on hover
                border_color=(120, 0, 0),  # Dark red border
                border_radius=8
            )
            # Store relative position for drawing
            btn.base_pos = (bx, by)
            self.elements.append(btn)

        self.active = True
        
        # Animation
        self.animation_time = 0.0
        self.animation_duration = 0.4  # Slightly longer for dramatic effect
        self.closing = False
        self.close_animation_time = 0.0
        
        # Pulsing glow effect
        self.glow_time = 0.0

    def select_difficulty(self, value):
        inventory.DIFFICULTY = value
        inventory.DIFFICULTY_SELECTED = True
        print(f"Difficulty selected: {value}")
        # Trigger closing animation instead of immediate close
        self.closing = True
        self.close_animation_time = 0.0

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
                if self.close_callback:
                    self.close_callback()
        else:
            self.animation_time += dt
        
        # Update glow pulsing
        self.glow_time += dt
        
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
        
        # Draw overlay with fade (darker for horror)
        overlay_alpha = int(230 * ease_progress)
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, overlay_alpha))
        surf.blit(overlay, (0, 0))
        
        # Scale popup from center
        scale = 0.85 + (0.15 * ease_progress)
        
        # Calculate scaled popup rect
        scaled_width = int(self.rect.width * scale)
        scaled_height = int(self.rect.height * scale)
        scaled_x = self.rect.centerx - scaled_width // 2
        scaled_y = self.rect.centery - scaled_height // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        
        # Pulsing glow effect (continues during closing)
        import math
        glow_intensity = 0.5 + 0.5 * math.sin(self.glow_time * 2)
        
        # Draw multiple glow layers for bleeding edge effect (bigger glow)
        for i in range(8, 0, -1):
            glow_offset = i * 15  # Increased from 8 to 15 for bigger glow
            glow_alpha = int(40 * glow_intensity * ease_progress / i)  # Increased base alpha
            glow_rect = scaled_rect.inflate(glow_offset * 2, glow_offset * 2)
            glow_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.glow_color, glow_alpha), glow_rect, border_radius=20)
            surf.blit(glow_surf, (0, 0))
        
        # Draw popup background
        bg_alpha = int(250 * ease_progress)
        bg_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (*self.bg_color, bg_alpha), scaled_rect, border_radius=15)
        surf.blit(bg_surf, (0, 0))
        
        # Draw border with glow
        border_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        border_alpha = int(255 * ease_progress)
        pygame.draw.rect(border_surf, (*self.border_color, border_alpha), scaled_rect, width=4, border_radius=15)
        surf.blit(border_surf, (0, 0))
        
        # Only draw content if animation is mostly complete
        if progress > 0.3:
            content_alpha = int(255 * ((progress - 0.3) / 0.7))
            
            # Draw title with drop shadow for depth
            if self.title_label:
                # Shadow
                shadow_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                shadow_text = BP_TITLE.render(self.title_label.text, True, (0, 0, 0))
                shadow_text.set_alpha(int(content_alpha * 0.7))
                shadow_pos = (self.rect.x + self.title_label.base_pos[0] + 3, 
                             self.rect.y + self.title_label.base_pos[1] + 3)
                shadow_rect = shadow_text.get_rect(center=shadow_pos)
                surf.blit(shadow_text, shadow_rect)
                
                # Main text
                main_text = BP_TITLE.render(self.title_label.text, True, self.title_label.color)
                main_text.set_alpha(content_alpha)
                main_pos = (self.rect.x + self.title_label.base_pos[0], 
                           self.rect.y + self.title_label.base_pos[1])
                main_rect = main_text.get_rect(center=main_pos)
                surf.blit(main_text, main_rect)
            
            # Draw buttons
            for el in self.elements:
                if el == self.title_label:
                    continue
                    
                # Ensure they are drawn at correct absolute position
                if hasattr(el, 'base_pos'):
                    el.rect.topleft = (self.rect.x + el.base_pos[0], self.rect.y + el.base_pos[1])
                
                # Create temp surface for alpha
                temp_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                el.draw(temp_surf)
                temp_surf.set_alpha(content_alpha)
                surf.blit(temp_surf, (0, 0))
