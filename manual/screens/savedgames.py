import pygame
import os
from manual.ui.button import Button
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.saving import load
from manual.ui import theme

pygame.init()

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 24)
TITLE_FONT = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 56)

class SavedGamesScreen:
    def __init__(self, goto_start, goto_menu):
        self.elements = []
        self.goto_start = goto_start
        self.goto_menu = goto_menu
        
        # Create gradient background
        self.gradient_bg = self._create_gradient_background()
        
        # Selected save tracking
        self.selected_save = None
        self.selected_save_index = -1
        
        # Scrolling
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Action buttons (Load / Delete)
        self.action_buttons = []
        
        # Load button
        self.load_btn = Button(
            (1280 - 450, 620, 200, 70),
            self.load_selected_save,
            None,
            text="Betoltes",
            font=BP,
            text_color=(255, 50, 50),
            bg_color=None,
            hover_bg_color=(50, 10, 10),
            border_color=(255, 50, 50),
            border_radius=8
        )
        
        # Delete button
        self.delete_btn = Button(
            (1280 - 220, 620, 200, 70),
            self.delete_selected_save,
            None,
            text="Torles",
            font=BP,
            text_color=(255, 50, 50),
            bg_color=None,
            hover_bg_color=(50, 10, 10),
            border_color=(255, 50, 50),
            border_radius=8
        )
        
        # Back button
        back_btn = Button(
            (30, 30, 180, 70),
            goto_start,
            None,
            text="Vissza",
            font=BP,
            text_color=(200, 200, 200),
            bg_color=None,
            hover_bg_color=(30, 30, 30),
            border_color=(200, 200, 200),
            border_radius=8
        )
        self.elements.append(back_btn)
        
        self.save_buttons = []
        self.reload_saves()
    
    def _create_gradient_background(self):
        """
        Creates a vertical gradient from dark red at top to black at bottom.
        """
        gradient = pygame.Surface((1280, 720))
        for y in range(720):
            # Interpolate from dark red (30, 0, 0) at top to black (0, 0, 0) at bottom
            t = y / 720.0
            r = int(30 * (1 - t))
            color = (r, 0, 0)
            pygame.draw.line(gradient, color, (0, y), (1280, y))
        return gradient

    def reload_saves(self):
        self.save_buttons = []
        self.selected_save = None
        self.selected_save_index = -1
        self.action_buttons = []
        
        saves = load.get_game_saves()

        start_y = 180
        cols = 4
        x_spacing = 60
        y_spacing = 60
        button_width, button_height = 240, 160

        for row_index, row_start in enumerate(range(0, len(saves), cols)):
            row_saves = saves[row_start:row_start + cols]
            num_in_row = len(row_saves)

            total_width = num_in_row * button_width + (num_in_row - 1) * x_spacing
            start_x = (1280 - total_width) // 2

            for col_index, s in enumerate(row_saves):
                filename = s["filename"]
                coins = s["coins"]
                cards = s["cards"]

                display_name = filename.replace("game_", "").replace(".json", "")
                text = f"{display_name}\n\n{coins} Coins\n{cards} Cards"

                x = start_x + col_index * (button_width + x_spacing)
                y = start_y + row_index * (button_height + y_spacing)

                idx = row_start + col_index
                
                def make_select_callback(index=idx, save_data=s):
                    return lambda: self.select_save(index, save_data)

                btn = Button(
                    (x, y, button_width, button_height),
                    make_select_callback(),
                    None,
                    text=text,
                    font=BP,
                    text_color=(255, 255, 255),
                    bg_color=(20, 20, 30),
                    hover_bg_color=(40, 40, 50),
                    border_color=(200, 200, 200),
                    border_radius=8
                )
                self.save_buttons.append(btn)

    def select_save(self, index, save_data):
        self.selected_save = save_data
        self.selected_save_index = index
        
        if self.load_btn not in self.action_buttons:
            self.action_buttons.append(self.load_btn)
        if self.delete_btn not in self.action_buttons:
            self.action_buttons.append(self.delete_btn)

    def load_selected_save(self):
        if self.selected_save:
            load.load_game_state(self.selected_save["filename"])
            self.goto_menu()

    def delete_selected_save(self):
        if self.selected_save:
            filepath = os.path.join(load.GAMES_DIR, self.selected_save["filename"])
            try:
                os.remove(filepath)
                print(f"Deleted save: {filepath}")
            except Exception as e:
                print(f"Error deleting save: {e}")
            
            self.reload_saves()

    def handle_event(self, e):
        # Handle mouse wheel scrolling
        if e.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= e.y * 30  # Scroll speed
            self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
        
        for el in self.elements + self.save_buttons + self.action_buttons:
            el.handle_event(e)

    def update(self, dt):
        for el in self.elements + self.save_buttons + self.action_buttons:
            el.update(dt)

    def draw(self, surf):
        # Draw gradient background
        surf.blit(self.gradient_bg, (0, 0))
        
        title_surf = TITLE_FONT.render("Mentett Jatekok", True, (255, 50, 50))
        title_rect = title_surf.get_rect(center=(640, 90))
        surf.blit(title_surf, title_rect)
        
        # Calculate max scroll based on content height
        if self.save_buttons:
            last_btn = self.save_buttons[-1]
            content_height = last_btn.rect.bottom - 180
            visible_height = 720 - 180 - 100  # Screen height - start_y - bottom margin
            self.max_scroll = max(0, content_height - visible_height)
        
        # Create a clipping surface for scrollable area
        clip_rect = pygame.Rect(0, 150, 1280, 470)
        surf.set_clip(clip_rect)
        
        for i, btn in enumerate(self.save_buttons):
            # Adjust button position based on scroll offset
            original_y = btn.rect.y
            btn.rect.y -= self.scroll_offset
            
            # Only draw if visible
            if btn.rect.bottom > 150 and btn.rect.top < 620:
                if i == self.selected_save_index:
                    pygame.draw.rect(surf, (255, 50, 50), btn.rect.inflate(10, 10), 4, border_radius=10)
                btn.draw(surf)
            
            # Restore original position
            btn.rect.y = original_y
        
        # Remove clipping
        surf.set_clip(None)
        
        # Draw scrollbar if content is scrollable
        if self.max_scroll > 0:
            scrollbar_x = 1250
            scrollbar_y = 150
            scrollbar_height = 470
            scrollbar_width = 8
            
            # Background track
            pygame.draw.rect(surf, (50, 50, 50), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), border_radius=4)
            
            # Calculate thumb size and position
            visible_ratio = scrollbar_height / (scrollbar_height + self.max_scroll)
            thumb_height = max(30, int(scrollbar_height * visible_ratio))
            thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * (self.scroll_offset / self.max_scroll))
            
            # Scrollbar thumb
            pygame.draw.rect(surf, (255, 50, 50), (scrollbar_x, thumb_y, scrollbar_width, thumb_height), border_radius=4)
        
        for el in self.elements + self.action_buttons:
            el.draw(surf)
