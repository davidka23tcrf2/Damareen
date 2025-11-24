from manual.inventory import inventory
import pygame
import os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR

sf = "configure"
pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "PublicPixel.ttf"), 20)
BP15 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "PublicPixel.ttf"), 15)

class CollectionPopup:
    """Popup for configuring the player's card collection."""
    def __init__(self, close_callback, screen_size=(1280, 720)):
        screen_width, screen_height = screen_size
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Popup size and placement
        w, h = 832, 500
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        self.target_rect = pygame.Rect(x, y, w, h)
        self.rect = pygame.Rect(x, screen_height, w, h)  # start off-screen

        # Appearance
        self.bg_color = (70, 70, 90)  # Dark blue-grey
        self.border_color = (0, 0, 0)

        self.elements = []
        self.card_buttons = []

        # Close button
        closebtn = load_asset("closebutton.png", sf)
        self.close_btn = Button((0, 0, 98, 98), close_callback, closebtn)
        self.elements.append(self.close_btn)

        # Title
        self.elements.append(Label((w // 2, 40, 0, 0), "Gyűjtemény konfigurálása", font=BP, color=(255, 255, 255)))

        # List Area
        # Move down to avoid close button (height 98)
        # Width 700 to match cards. Center it: (832 - 700) // 2 = 66
        self.list_area = pygame.Rect(66, 110, 700, h - 130)
        self.scroll_y = 0
        self.scroll_speed = 20
        self.max_scroll = 0
        
        # Animation
        self.opening = True
        self.closing = False
        self.overlay_alpha = 0
        self.max_overlay_alpha = 150
        self.overlay_speed = 20
        self.active = True

        for el in self.elements:
            el.base_rect = el.rect.copy()

        self.refresh_list()

    def refresh_list(self):
        self.card_buttons = []
        y_off = 0
        
        # List all game cards
        cards = inventory.GAMECARDS
        
        # Grid layout? Or list? List is easier for names.
        # Let's do 2 columns if possible, or just one long list.
        # One long list for now.
        
        for i, card in enumerate(cards):
            w, h = 700, 40
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            
            # Check if in player collection
            in_collection = card in inventory.PLAYERCARDS
            
            bg_color = (100, 200, 100) if in_collection else (200, 100, 100)
            pygame.draw.rect(surf, bg_color, surf.get_rect(), border_radius=0)
            pygame.draw.rect(surf, (0,0,0), surf.get_rect(), width=2, border_radius=0)
            
            # Text
            status = "[+]" if in_collection else "[-]"
            name = card.name
            # Format: Name DMG/HP Power
            dmg = getattr(card, 'dmg', '?')
            hp = getattr(card, 'hp', '?')
            power = getattr(card, 'power', '?')
            txt_str = f"{status} {name} {dmg}/{hp} {power}"
            txt = BP15.render(txt_str, True, (0,0,0))
            surf.blit(txt, (10, 10))
            
            bx = (self.target_rect.width - w) // 2
            by = 110 + y_off
            
            btn = Button((bx, by, w, h), lambda c=card: self.toggle_card(c), surf)
            btn.base_pos = (bx, by)
            self.card_buttons.append(btn)
            y_off += 40
            
        # Calculate max scroll
        total_height = y_off
        self.max_scroll = max(0, total_height - self.list_area.height)

    def toggle_card(self, card):
        if card in inventory.PLAYERCARDS:
            inventory.PLAYERCARDS.remove(card)
        else:
            inventory.PLAYERCARDS.append(card)
        self.refresh_list()

    def reopen(self):
        if self.is_closed():
            self.rect.y = self.screen_height
            self.opening = True
            self.closing = False
            self.overlay_alpha = 0
            self.active = True
            self.refresh_list()

    def is_closed(self):
        return not self.opening and not self.closing and self.rect.y >= self.screen_height

    def close(self):
        self.closing = True
        self.opening = False

    def handle_event(self, event):
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            if not self.rect.collidepoint(event.pos):
                return True 

        for el in self.elements:
            el.handle_event(event)
            
        # Handle scrolling
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                 # Check if mouse is over list area (relative to screen)
                m_pos = pygame.mouse.get_pos()
                list_rect_screen = pygame.Rect(
                    self.rect.x + self.list_area.x,
                    self.rect.y + self.list_area.y,
                    self.list_area.width,
                    self.list_area.height
                )
                if list_rect_screen.collidepoint(m_pos):
                    self.scroll_y -= event.y * self.scroll_speed
                    self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
                    return True

        # Handle list buttons
        for btn in self.card_buttons:
            # Only handle event if button is visible in list area
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                if not self.list_area.collidepoint(
                    event.pos[0] - self.rect.x, 
                    event.pos[1] - self.rect.y
                ):
                    continue
            btn.handle_event(event)

        return True

    def update(self, dt):
        # Animation
        if self.opening:
            distance = self.rect.y - self.target_rect.y
            self.rect.y -= max(int(distance * 0.35), 5)
            self.overlay_alpha = min(self.overlay_alpha + self.overlay_speed, self.max_overlay_alpha)
            if self.rect.y <= self.target_rect.y:
                self.rect.y = self.target_rect.y
                self.opening = False
        elif self.closing:
            distance = self.screen_height - self.rect.y
            self.rect.y += max(int(distance * 0.35), 5)
            self.overlay_alpha = max(self.overlay_alpha - self.overlay_speed, 0)
            if self.rect.y >= self.screen_height:
                self.closing = False
                self.active = False

        # Update positions
        for el in self.elements:
            el.rect.topleft = (self.rect.x + el.base_rect.x, self.rect.y + el.base_rect.y)
            el.update(dt)
            
        for btn in self.card_buttons:
            btn.rect.topleft = (
                self.rect.x + btn.base_pos[0], 
                self.rect.y + btn.base_pos[1] - self.scroll_y
            )
            btn.update(dt)

    def draw(self, surf):
        if self.rect.y > self.screen_height and self.overlay_alpha <= 0:
            return

        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), flags=pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.overlay_alpha))
        surf.blit(overlay, (0, 0))

        # Popup BG
        pygame.draw.rect(surf, self.bg_color, self.rect)
        pygame.draw.rect(surf, self.border_color, self.rect, 2)

        # Draw elements
        for el in self.elements:
            el.draw(surf)
            
        # Draw list border
        # Calculate absolute rect for list area
        abs_list_rect = pygame.Rect(
            self.rect.x + self.list_area.x,
            self.rect.y + self.list_area.y,
            self.list_area.width,
            self.list_area.height
        )
        pygame.draw.rect(surf, (0, 0, 0), abs_list_rect, 2)
            
        # Draw list
        # Clip to list area
        surf.set_clip(abs_list_rect)
        for btn in self.card_buttons:
            # Only draw if within popup bounds roughly (optimization)
            # Actually, clip handles it visually, but we can skip drawing for perf
            if btn.rect.bottom > self.rect.top and btn.rect.top < self.rect.bottom:
                btn.draw(surf)
        surf.set_clip(None)
