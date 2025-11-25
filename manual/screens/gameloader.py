import os, pygame
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.ui.button import Button
from manual.saving import load
from manual.ui import theme

pygame.init()

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 24)
TITLE_FONT = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 56)

class GameLoader:
    def __init__(self, goto_menu, goto_start):
        self.elements = []
        self.goto_menu = goto_menu
        self.goto_start = goto_start
        
        # Create gradient background
        self.gradient_bg = self._create_gradient_background()
        
        # Selected save tracking
        self.selected_save = None
        self.selected_save_index = -1
        
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
        
        saves = load.get_save_files()

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
                save_num = s["save_num"]
                cards = s["cards"]
                enemies = s["enemies"]
                filename = s["file"]

                text = f"Kornyezet {save_num}\n\n{cards} Kartya\n{enemies} Kazamata"

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
            load.load_game(self.selected_save["file"])
            self.goto_menu()

    def delete_selected_save(self):
        if self.selected_save:
            filepath = os.path.join(load.SAVES_DIR, self.selected_save["file"])
            try:
                os.remove(filepath)
                print(f"Deleted save: {filepath}")
            except Exception as e:
                print(f"Error deleting save: {e}")
            
            self.reload_saves()

    def handle_event(self, e):
        for el in self.elements + self.save_buttons + self.action_buttons:
            el.handle_event(e)

    def update(self, dt):
        for el in self.elements + self.save_buttons + self.action_buttons:
            el.update(dt)

    def draw(self, surf):
        # Draw gradient background
        surf.blit(self.gradient_bg, (0, 0))
        
        title_surf = TITLE_FONT.render("Kornyezet Betoltes", True, (255, 50, 50))
        title_rect = title_surf.get_rect(center=(640, 90))
        surf.blit(title_surf, title_rect)
        
        for i, btn in enumerate(self.save_buttons):
            if i == self.selected_save_index:
                pygame.draw.rect(surf, (255, 50, 50), btn.rect.inflate(10, 10), 4, border_radius=10)
            
            btn.draw(surf)
            
        for el in self.elements + self.action_buttons:
            el.draw(surf)
