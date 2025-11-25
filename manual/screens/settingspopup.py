import pygame
import os
import sys
from manual.ui.button import Button
from manual.ui.label import Label
from manual.ui.text_entry import TextEntry
from manual.assets.assets import ASSETS_DIR
from manual.ui import theme
from manual.saving import save
from manual.inventory import inventory

pygame.init()

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 28)
TITLE_FONT = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 48)

class SettingsPopup:
    def __init__(self, close_callback, screen_size=(1280, 720)):
        self.close_callback = close_callback
        self.active = True
        self.screen_size = screen_size
        
        w, h = screen_size
        
        # Popup dimensions
        popup_width = 700
        popup_height = 600
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
            "Beallitasok",  # English-only characters (Settings)
            font=TITLE_FONT,
            color=(255, 255, 255)
        )
        
        # Buttons (start screen style - outline only)
        btn_width = 400
        btn_height = 70
        btn_x = popup_x + (popup_width - btn_width) // 2
        
        # Red theme colors
        RED_BRIGHT = (255, 50, 50)
        
        # Name Label
        self.name_label = Label(
            (btn_x, popup_y + 80, btn_width, 30),
            "Név:",
            font=BP,
            color=(255, 255, 255)
        )
        
        # Save Name Input
        self.save_name_input = TextEntry(
            (btn_x, popup_y + 110, btn_width, 35),
            font=BP,
            bg_color=(50, 50, 50),
            color=(255, 255, 255)
        )

        # Save Feedback Label
        self.save_feedback_label = Label(
            (btn_x, popup_y + 225, btn_width, 30),
            "",
            font=BP,
            color=(0, 255, 0)
        )
        self.feedback_timer = 0.0
        
        # Overwrite confirmation state
        self.pending_overwrite_name = None
        self.save_success = False  # Track if save was successful to hide button

        # Save Game button
        self.save_btn = Button(
            (btn_x, popup_y + 150, btn_width, btn_height),
            self.save_game,
            None,
            text="Jatek mentese",  # English-only
            font=BP,
            text_color=RED_BRIGHT,
            bg_color=None,  # Transparent
            hover_bg_color=(50, 10, 10),
            border_color=RED_BRIGHT,
            border_radius=8
        )
        
        # Confirm Overwrite button (hidden by default)
        self.confirm_btn = Button(
            (btn_x, popup_y + 150, btn_width // 2 - 10, btn_height),
            self.confirm_overwrite,
            None,
            text="Igen",
            font=BP,
            text_color=(0, 255, 0),
            bg_color=None,
            hover_bg_color=(10, 50, 10),
            border_color=(0, 255, 0),
            border_radius=8
        )
        
        # Cancel Overwrite button (hidden by default)
        self.cancel_btn = Button(
            (btn_x + btn_width // 2 + 10, popup_y + 150, btn_width // 2 - 10, btn_height),
            self.cancel_overwrite,
            None,
            text="Nem",
            font=BP,
            text_color=(255, 50, 50),
            bg_color=None,
            hover_bg_color=(50, 10, 10),
            border_color=(255, 50, 50),
            border_radius=8
        )
        
        # Volume slider - load from inventory
        self.volume_value = inventory.VOLUME
        
        self.volume_label = Label(
            (btn_x, popup_y + 250, btn_width, 40),
            f"Hangero: {self.volume_value}%",  # English-only
            font=BP,
            color=(255, 255, 255)
        )
        
        self.volume_slider_rect = pygame.Rect(btn_x, popup_y + 300, btn_width, 25)
        # self.volume_value = 50  # Removed hardcoded reset
        self.dragging_slider = False
        
        # Quit button
        self.quit_btn = Button(
            (btn_x, popup_y + 360, btn_width, btn_height),
            self.quit_game,
            None,
            text="Kilepes",  # English-only
            font=BP,
            text_color=RED_BRIGHT,
            bg_color=None,
            hover_bg_color=(50, 10, 10),
            border_color=RED_BRIGHT,
            border_radius=8
        )
        
        # Close button
        self.close_btn = Button(
            (btn_x, popup_y + 460, btn_width, btn_height),
            self.close,
            None,
            text="Bezaras",  # English-only
            font=BP,
            text_color=(200, 200, 200),
            bg_color=None,
            hover_bg_color=(30, 30, 30),
            border_color=(200, 200, 200),
            border_radius=8
        )
        
        self.buttons = [self.save_btn, self.quit_btn, self.close_btn]
    
    def save_game(self):
        save_name = self.save_name_input.get_text().strip()
        
        # Check if name is provided
        if not save_name:
            self.save_feedback_label.text = "Adj meg egy nevet!"
            self.save_feedback_label.color = (255, 0, 0)
            self.feedback_timer = 2.0
            return
        
        # Check if file already exists
        filename = f"{save_name}.json" if not save_name.endswith(".json") else save_name
        filepath = os.path.join(save.GAMES_DIR, filename)
        
        if os.path.exists(filepath):
            # Ask for confirmation
            self.pending_overwrite_name = save_name
            self.save_feedback_label.text = "Biztos felulirod a mar letezo fajlt?"
            self.save_feedback_label.color = (255, 255, 0)
            self.feedback_timer = 0  # Keep showing
            return
        
        # Save the game
        self._do_save(save_name)
    
    def _do_save(self, save_name):
        try:
            filename = save.save_game_state(save_name)
            print(f"Game saved: {filename}")
            
            # Show feedback
            self.save_feedback_label.text = "Jatek elmentve!"
            self.save_feedback_label.color = (0, 255, 0)
            self.feedback_timer = 1.5
            self.pending_overwrite_name = None
            self.save_success = True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            self.save_feedback_label.text = "Hiba a mentesnel!"
            self.save_feedback_label.color = (255, 0, 0)
            self.feedback_timer = 2.0
            self.pending_overwrite_name = None
            self.save_success = False
    
    def confirm_overwrite(self):
        if self.pending_overwrite_name:
            self._do_save(self.pending_overwrite_name)
    
    def cancel_overwrite(self):
        self.pending_overwrite_name = None
        self.save_feedback_label.text = ""
        self.feedback_timer = 0
    
    def quit_game(self):
        pygame.quit()
        sys.exit()
    
    def close(self):
        self.closing = True
        self.close_animation_time = 0.0
    
    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            # Check if clicking on slider
            if self.volume_slider_rect.collidepoint(e.pos):
                self.dragging_slider = True
                self.update_volume_from_mouse(e.pos[0])
                return True
        
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.dragging_slider = False
        
        elif e.type == pygame.MOUSEMOTION:
            if self.dragging_slider:
                self.update_volume_from_mouse(e.pos[0])
                return True
        
        # Handle text entry
        if self.save_name_input.handle_event(e):
            return True

        # Handle button events
        if self.pending_overwrite_name:
            # Show confirmation buttons
            self.confirm_btn.handle_event(e)
            self.cancel_btn.handle_event(e)
        else:
            # Show normal buttons
            for btn in self.buttons:
                btn.handle_event(e)
        
        # Block events from passing through
        if e.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.KEYDOWN):
            return True
        
        return False
    
    def update_volume_from_mouse(self, mouse_x):
        # Calculate volume based on mouse position
        rel_x = mouse_x - self.volume_slider_rect.x
        self.volume_value = max(0, min(100, int((rel_x / self.volume_slider_rect.width) * 100)))
        self.volume_label.text = f"Hangero: {self.volume_value}%"
        
        # Save to inventory
        inventory.VOLUME = self.volume_value
        
        # Apply to pygame mixer (0.0 to 1.0)
        try:
            pygame.mixer.music.set_volume(self.volume_value / 100.0)
        except:
            pass  # Ignore if no music is playing
    
    def update(self, dt):
        if self.closing:
            self.close_animation_time += dt
            if self.close_animation_time >= self.animation_duration:
                self.active = False
                if self.close_callback:
                    self.close_callback()
        else:
            self.animation_time += dt
        
        for btn in self.buttons:
            btn.update(dt)
            
        self.save_name_input.update(dt)
        
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.save_feedback_label.text = ""
                self.save_success = False  # Reset success state
    
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
        
        # Create a temporary surface for the entire popup with alpha
        popup_surf = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        
        # Draw popup background and border to temporary surface
        pygame.draw.rect(popup_surf, (0, 0, 0), scaled_rect, border_radius=15)
        pygame.draw.rect(popup_surf, (255, 50, 50), scaled_rect, width=3, border_radius=15)
        
        # Apply alpha to entire popup (border + background)
        popup_alpha = int(255 * ease_progress)
        popup_surf.set_alpha(popup_alpha)
        surf.blit(popup_surf, (0, 0))
        
        # Only draw content if animation is mostly complete
        if progress > 0.3:
            content_alpha = int(255 * ((progress - 0.3) / 0.7))
            
            # Draw title
            title_surf = TITLE_FONT.render(self.title_label.text, True, (255, 255, 255))
            title_surf.set_alpha(content_alpha)
            title_rect = title_surf.get_rect(center=(self.popup_rect.centerx, self.popup_rect.y + 70))
            surf.blit(title_surf, title_rect)
            
            # Create a temporary surface for buttons with alpha
            button_surf = pygame.Surface(self.screen_size, pygame.SRCALPHA)
            
            # Draw name label
            name_surf = BP.render(self.name_label.text, True, (255, 255, 255))
            name_surf.set_alpha(content_alpha)
            surf.blit(name_surf, self.name_label.rect.topleft)
            
            # Draw buttons to temporary surface
            if self.pending_overwrite_name:
                # During confirmation, show confirmation buttons but keep other UI visible
                self.confirm_btn.draw(button_surf)
                self.cancel_btn.draw(button_surf)
                # Draw quit and close buttons
                self.quit_btn.draw(button_surf)
                self.close_btn.draw(button_surf)
            elif self.save_success:
                # During success message, hide save button but show others
                self.quit_btn.draw(button_surf)
                self.close_btn.draw(button_surf)
            else:
                # Normal state - draw all buttons
                for btn in self.buttons:
                    btn.draw(button_surf)
            
            self.save_name_input.draw(button_surf)
            
            # Draw feedback label with alpha
            if self.save_feedback_label.text:
                feedback_surf = BP.render(self.save_feedback_label.text, True, self.save_feedback_label.color)
                feedback_surf.set_alpha(content_alpha)
                feedback_rect = feedback_surf.get_rect(topleft=self.save_feedback_label.rect.topleft)
                surf.blit(feedback_surf, feedback_rect)
            
            # Apply alpha to button surface
            button_surf.set_alpha(content_alpha)
            surf.blit(button_surf, (0, 0))
            
            # Draw volume label
            vol_surf = BP.render(self.volume_label.text, True, (255, 255, 255))
            vol_surf.set_alpha(content_alpha)
            vol_rect = vol_surf.get_rect(center=(self.volume_slider_rect.centerx, self.volume_slider_rect.y - 30))
            surf.blit(vol_surf, vol_rect)
            
            # Draw volume slider with alpha
            slider_surf = pygame.Surface(self.screen_size, pygame.SRCALPHA)
            
            # Background
            pygame.draw.rect(slider_surf, (50, 50, 50), self.volume_slider_rect, border_radius=12)
            # Fill
            fill_width = int((self.volume_value / 100) * self.volume_slider_rect.width)
            fill_rect = pygame.Rect(
                self.volume_slider_rect.x,
                self.volume_slider_rect.y,
                fill_width,
                self.volume_slider_rect.height
            )
            pygame.draw.rect(slider_surf, (255, 50, 50), fill_rect, border_radius=12)
            # Border
            pygame.draw.rect(slider_surf, (255, 50, 50), self.volume_slider_rect, width=2, border_radius=12)
            
            # Apply alpha to slider
            slider_surf.set_alpha(content_alpha)
            surf.blit(slider_surf, (0, 0))
