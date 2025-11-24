import pygame, os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory import inventory

pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 36)
BP_TITLE = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 50)

class DungeonPopup:
    def __init__(self, close_callback, screen_size=(1280, 720)):
        self.screen_width, self.screen_height = screen_size
        self.close_callback = close_callback
        
        # Popup dimensions
        w, h = 800, 600
        x = (self.screen_width - w) // 2
        y = (self.screen_height - h) // 2
        self.rect = pygame.Rect(x, y, w, h)
        
        self.bg_color = (0, 0, 0)
        self.border_color = (255, 50, 50)
        
        self.elements = []
        
        # Title
        self.title_label = Label(
            (w // 2, 50, 0, 0), 
            "Válassz kazamatát", 
            font=BP_TITLE, 
            color=(255, 255, 255)
        )
        self.title_label.base_pos = (w // 2, 50)
        self.elements.append(self.title_label)
        
        # Dungeon List
        btn_width = 600
        btn_height = 60
        gap = 15
        start_y = 120
        
        # Scroll offset
        self.scroll_y = 0
        self.max_scroll = 0
        
        # Content surface for scrolling
        self.content_height = len(inventory.ENEMIES) * (btn_height + gap)
        self.viewport_height = h - 140
        
        if self.content_height > self.viewport_height:
            self.max_scroll = self.content_height - self.viewport_height
        
        for i, enemy in enumerate(inventory.ENEMIES):
            by = start_y + i * (btn_height + gap)
            
            # Create button
            btn = Button(
                ((w - btn_width) // 2, by, btn_width, btn_height),
                lambda idx=i: self.select_dungeon(idx),
                None,
                text=enemy.name,
                font=BP,
                text_color=(255, 50, 50),
                bg_color=None,
                hover_bg_color=(50, 10, 10),
                border_color=(255, 50, 50),
                border_radius=0
            )
            # Store relative position
            btn.base_pos = ((w - btn_width) // 2, by)
            self.elements.append(btn)

        self.active = True

    def select_dungeon(self, index):
        inventory.SELECTED_DUNGEON_INDEX = index
        print(f"Dungeon selected: {inventory.ENEMIES[index].name}")
        self.close_callback()
        self.active = False

    def handle_event(self, event):
        if not self.active: return
        
        # Absorb clicks inside popup
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            if not self.rect.collidepoint(event.pos):
                return True
                
            # Handle scrolling
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Scroll up
                    self.scroll_y = max(0, self.scroll_y - 30)
                elif event.button == 5: # Scroll down
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 30)

        for el in self.elements:
            # Update rect to be absolute before handling event
            if hasattr(el, 'base_pos'):
                bx, by = el.base_pos
                # Apply scroll
                by -= self.scroll_y
                
                # Only handle events if button is visible in viewport
                if 120 <= by <= self.rect.height - 20:
                    el.rect.topleft = (self.rect.x + bx, self.rect.y + by)
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
        
        # Draw elements with clipping
        clip_rect = pygame.Rect(self.rect.x, self.rect.y + 100, self.rect.width, self.rect.height - 120)
        surf.set_clip(clip_rect)
        
        for el in self.elements:
            # Skip title label in scroll loop
            if el == self.title_label: continue
            
            if hasattr(el, 'base_pos'):
                bx, by = el.base_pos
                by -= self.scroll_y
                el.rect.topleft = (self.rect.x + bx, self.rect.y + by)
                el.draw(surf)
                
        surf.set_clip(None)
        
        # Draw title (always on top)
        if hasattr(self.title_label, 'base_pos'):
            center_x = self.rect.x + self.title_label.base_pos[0]
            center_y = self.rect.y + self.title_label.base_pos[1]
            self.title_label.rect.center = (center_x, center_y)
            self.title_label.draw(surf)
            
        # Draw Scrollbar if needed
        if self.max_scroll > 0:
            scrollbar_width = 10
            scrollbar_height = self.viewport_height
            scrollbar_x = self.rect.right - 20
            scrollbar_y = self.rect.y + 100
            
            # Background
            pygame.draw.rect(surf, (50, 50, 50), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
            
            # Handle
            handle_height = max(30, int((self.viewport_height / self.content_height) * self.viewport_height))
            handle_y = scrollbar_y + int((self.scroll_y / self.max_scroll) * (scrollbar_height - handle_height))
            
            pygame.draw.rect(surf, (255, 50, 50), (scrollbar_x, handle_y, scrollbar_width, handle_height))
