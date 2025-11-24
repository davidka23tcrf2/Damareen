import pygame, os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory import inventory

pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 36)
BP_TITLE = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 50)

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
            "Válassz nehézséget", 
            font=BP_TITLE, 
            color=(255, 255, 255)
        )
        self.title_label.base_pos = (w // 2, 50)
        self.elements.append(self.title_label)
        
        # Buttons 0-10
        btn_size = 60
        gap = 20
        start_x = (w - (6 * btn_size + 5 * gap)) // 2  # 6 buttons per row
        start_y = 150
        
        for i in range(0, 11):
            row = i // 6
            col = i % 6
            
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
        for el in self.elements:
            el.update(dt)

    def draw(self, surf):
        if not self.active: return
        
        # Draw overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surf.blit(overlay, (0, 0))
        
        # Draw popup background
        pygame.draw.rect(surf, self.bg_color, self.rect, border_radius=0)
        pygame.draw.rect(surf, self.border_color, self.rect, 3, border_radius=0)
        
        # Draw elements
        for el in self.elements:
            # Ensure they are drawn at correct absolute position
            if hasattr(el, 'base_pos'):
                if isinstance(el, Label) and getattr(el, 'centered', False):
                     center_x = self.rect.x + el.base_pos[0]
                     center_y = self.rect.y + el.base_pos[1]
                     el.rect.center = (center_x, center_y)
                else:
                    el.rect.topleft = (self.rect.x + el.base_pos[0], self.rect.y + el.base_pos[1])

            el.draw(surf)
