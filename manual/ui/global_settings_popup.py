import pygame
import os
import sys
from manual.ui.button import Button
from manual.ui.label import Label
from manual.assets.assets import ASSETS_DIR
from manual.ui import theme
from manual.inventory import inventory

pygame.init()

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 28)
TITLE_FONT = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 48)

class GlobalSettingsPopup:
    """Simplified settings popup with only volume control and exit - accessible from anywhere."""
    def __init__(self, close_callback, screen_size=(1280, 720)):
        self.close_callback = close_callback
        self.active = True
        self.screen_size = screen_size
        
        w, h = screen_size
        
        # Popup dimensions
        popup_width = 500
        popup_height = 400
        popup_x = (w - popup_width) // 2
        popup_y = (h - popup_height) // 2
        
        self.popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        
        # Animation
        self.animation_time = 0.0
        self.animation_duration = 0.3  # seconds
        self.closing = False
        self.close_animation_time = 0.0
        
        # Overlay
        self.overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 200))
        
        # Title
        self.title_label = Label(
            (w // 2 - 150, popup_y + 40, 300, 60),
            "Beallitasok",
            font=TITLE_FONT,
            color=(255, 255, 255)
        )
        
        # Buttons
        btn_width = 350
        btn_height = 70
        btn_x = popup_x + (popup_width - btn_width) // 2
        
        # Red theme colors
        RED_BRIGHT = (255, 50, 50)
        
        # Volume slider - load from inventory
        self.volume_value = inventory.VOLUME
        
        self.volume_label = Label(
            (btn_x, popup_y + 120, btn_width, 40),
            f"Hangero: {self.volume_value}%",
            font=BP,
            color=(255, 255, 255)
        )
        
        self.volume_slider_rect = pygame.Rect(btn_x, popup_y + 170, btn_width, 25)
        self.volume_dragging = False
        
        # Exit button
        self.exit_btn = Button(
            (btn_x, popup_y + 240, btn_width, btn_height),
            self.exit_game,
            None,
            text="Kilepes",
            font=BP,
            text_color=RED_BRIGHT,
            bg_color=None,
            hover_bg_color=(50, 10, 10),
            border_color=RED_BRIGHT,
            border_radius=8
        )
    
    def exit_game(self):
        pygame.quit()
        sys.exit()
    
    def close(self):
        self.closing = True
        self.close_animation_time = 0.0
    
    def handle_event(self, event):
        # Block ALL mouse events from passing through
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            # Check if clicking outside popup to close
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.popup_rect.collidepoint(event.pos):
                    return True  # Block but don't process
        
        # Volume slider
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.volume_slider_rect.collidepoint(event.pos):
                self.volume_dragging = True
                self.update_volume_from_mouse(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.volume_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.volume_dragging:
            self.update_volume_from_mouse(event.pos[0])
        
        # Exit button
        self.exit_btn.handle_event(event)
        
        # ESC to close
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
        
        return True  # Block all events from passing through
    
    def update_volume_from_mouse(self, mouse_x):
        slider_x = self.volume_slider_rect.x
        slider_width = self.volume_slider_rect.width
        relative_x = max(0, min(mouse_x - slider_x, slider_width))
        self.volume_value = int((relative_x / slider_width) * 100)
        inventory.VOLUME = self.volume_value
        pygame.mixer.music.set_volume(self.volume_value / 100.0)
        self.volume_label.set_text(f"Hangero: {self.volume_value}%")
    
    def update(self, dt):
        if self.closing:
            self.close_animation_time += dt
            if self.close_animation_time >= self.animation_duration:
                self.active = False
                if self.close_callback:
                    self.close_callback()
        else:
            self.animation_time += dt
            if self.animation_time > self.animation_duration:
                self.animation_time = self.animation_duration
        
        self.exit_btn.update(dt)
    
    def draw(self, surf):
        # Determine animation progress based on state
        if self.closing:
            # Reverse animation for closing
            progress = 1.0 - min(1.0, self.close_animation_time / self.animation_duration)
        else:
            # Normal opening animation
            progress = min(1.0, self.animation_time / self.animation_duration)
        
        # Ease out cubic
        ease_progress = 1 - pow(1 - progress, 3)
        
        # Draw overlay with fade-in/out
        overlay_alpha = int(200 * ease_progress)
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, overlay_alpha))
        surf.blit(overlay, (0, 0))
        
        # Scale popup from center
        scale = 0.8 + (0.2 * ease_progress)
        
        # Calculate scaled popup rect
        scaled_width = int(self.popup_rect.width * scale)
        scaled_height = int(self.popup_rect.height * scale)
        scaled_x = self.popup_rect.centerx - scaled_width // 2
        scaled_y = self.popup_rect.centery - scaled_height // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        
        # Draw popup background and border
        pygame.draw.rect(surf, (40, 40, 50), scaled_rect, border_radius=15)
        pygame.draw.rect(surf, (255, 50, 50), scaled_rect, width=3, border_radius=15)
        
        # Only draw content if animation is mostly complete
        if progress > 0.3:
            content_alpha = int(255 * ((progress - 0.3) / 0.7))
            
            # Draw title
            title_surf = TITLE_FONT.render("Beallitasok", True, (255, 255, 255))
            title_surf.set_alpha(content_alpha)
            title_rect = title_surf.get_rect(center=(self.popup_rect.centerx, self.popup_rect.y + 70))
            surf.blit(title_surf, title_rect)
            
            # Draw volume label
            vol_surf = BP.render(f"Hangero: {self.volume_value}%", True, (255, 255, 255))
            vol_surf.set_alpha(content_alpha)
            vol_rect = vol_surf.get_rect(topleft=(self.volume_label.rect.x, self.volume_label.rect.y))
            surf.blit(vol_surf, vol_rect)
            
            # Draw volume slider
            slider_surf = pygame.Surface((self.volume_slider_rect.width, self.volume_slider_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(slider_surf, (100, 100, 100), slider_surf.get_rect(), border_radius=5)
            fill_width = int((self.volume_value / 100.0) * self.volume_slider_rect.width)
            fill_rect = pygame.Rect(0, 0, fill_width, self.volume_slider_rect.height)
            pygame.draw.rect(slider_surf, (255, 50, 50), fill_rect, border_radius=5)
            slider_surf.set_alpha(content_alpha)
            surf.blit(slider_surf, self.volume_slider_rect.topleft)
            
            # Draw exit button with alpha
            btn_surf = pygame.Surface(self.screen_size, pygame.SRCALPHA)
            self.exit_btn.draw(btn_surf)
            btn_surf.set_alpha(content_alpha)
            surf.blit(btn_surf, (0, 0))
