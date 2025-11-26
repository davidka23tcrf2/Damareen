from manual.screens.configurepopups.newdungeon import BP36
from manual.inventory import inventory, objects
import pygame
import os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.ui.text_entry import TextEntry
from manual.assets.assets import load_asset, ASSETS_DIR

sf = "configure"
pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 24)
BP15 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 18)
BP12 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 14)
BP26 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 30)
BP_BIG = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 36)

class NewLeaderCardPopup:
    """Popup for creating a new LEADER card (vezérkártya)."""
    def __init__(self, close_callback, screen_size=(1280, 720)):
        screen_width, screen_height = screen_size
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Popup size and placement
        w, h = 832, 468
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        self.target_rect = pygame.Rect(x, y, w, h)
        self.rect = pygame.Rect(x, screen_height, w, h)  # start off-screen

        # Appearance
        self.bg_color = (139, 69, 19)  # brown (same as newcard.py)
        self.border_color = (0, 0, 0)

        self.elements = []
        self.text_entries = []
        self.card_buttons = [] # buttons to select existing cards
        self.type_buttons = [] # damage vs hp

        # Selection state
        self.selected_card_index = -1
        self.selector_rect = None
        
        # Type Selector Animation
        self.type_selector_rect = pygame.Rect(0, 0, 0, 0) # Will be set in init
        self.type_selector_pos = pygame.math.Vector2(0, 0)

        # --- CREATE BUTTON ---
        create_w, create_h = 350, 80
        create_x = 430
        create_y = 350

        create_img = pygame.Surface((create_w, create_h), pygame.SRCALPHA)
        pygame.draw.rect(create_img, (50, 200, 50), create_img.get_rect(), border_radius=0)
        pygame.draw.rect(create_img, (0, 0, 0), create_img.get_rect(), width=4, border_radius=0)
        
        # User requested "smalles so text fits" -> Using BP12
        label = BP26.render("Vezérkártya létrehozása", True, (0, 0, 0))
        label_rect = label.get_rect(center=(create_w // 2, create_h // 2))
        create_img.blit(label, label_rect)

        self.create_btn = Button(
            (create_x, create_y, create_w, create_h),
            self.create_leader_card,
            create_img
        )
        self.elements.append(self.create_btn)

        # Status text counter
        self.status_counter = 0

        # Close button
        closebtn = load_asset("closebutton.png", sf)
        self.close_btn = Button((0, 0, 98, 98), close_callback, closebtn)
        self.elements.append(self.close_btn)

        # Labels
        self.elements.append(Label((400, 50, 0, 0), "Új vezérkártya", font=BP36, color=(255, 255, 255)))
        
        # Prefix input - moved to right side to avoid overlap
        # User requested "more right by more"
        # Align label with input: Input is at y=130, height=40. Center y=150.
        # Label font BP (20). To center, y should be approx 140? 
        # User said "elonev til doesnt align up with the textentry".
        # Let's try moving label Y to 142 to center it better visually with the text entry text.
        self.elements.append(Label((550, 150, 0, 0), "Előnév:", font=BP36, color=(255, 255, 255)))
        # User requested: more chars, smaller font, still no spaces
        self.prefix_entry = TextEntry((620, 130, 180, 40), font=BP26, max_length=11, letters_only=True)
        self.prefix_entry.base_pos = self.prefix_entry.rect.topleft
        self.text_entries.append(self.prefix_entry)
        
        # Error label for duplicate name
        # Position above text entry (y=130), so maybe y=100
        self.error_label = Label((620, 100, 0, 0), "", font=BP12, color=(255, 0, 0))
        self.elements.append(self.error_label)

        # Card Selection List
        # Adjusted width to match buttons
        self.card_list_area = pygame.Rect(50, 100, 360, 300)
        self.selected_card = None
        self.card_list_area = pygame.Rect(50, 100, 360, 300)
        self.selected_card = None
        self.scroll_y = 0
        self.scroll_speed = 20
        self.max_scroll = 0
        
        # Type selection (Damage vs HP)
        self.selected_type = "damage" # or "hp"
        
        # Create buttons for Damage / HP
        # Bigger, touching each other, smaller text
        btn_w, btn_h = 160, 80
        btn_y = 220
        
        # Damage Button
        # Damage Button
        dmg_img = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(dmg_img, (200, 50, 50), dmg_img.get_rect(), border_radius=0)
        pygame.draw.rect(dmg_img, (0,0,0), dmg_img.get_rect(), width=2, border_radius=0)
        # Smaller font
        dmg_txt = BP26.render("Sebzés", True, (0,0,0)) 
        dmg_img.blit(dmg_txt, dmg_txt.get_rect(center=(btn_w//2, btn_h//2)))
        
        self.dmg_btn = Button((450, btn_y, btn_w, btn_h), lambda: self.set_type("damage"), dmg_img)
        self.dmg_btn.base_pos = self.dmg_btn.rect.topleft
        self.type_buttons.append(self.dmg_btn)
        
        # HP Button
        hp_img = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(hp_img, (50, 200, 50), hp_img.get_rect(), border_radius=0)
        pygame.draw.rect(hp_img, (0,0,0), hp_img.get_rect(), width=2, border_radius=0)
        # Smaller font
        hp_txt = BP26.render("Életerő", True, (0,0,0))
        hp_img.blit(hp_txt, hp_txt.get_rect(center=(btn_w//2, btn_h//2)))

        self.hp_btn = Button((450 + btn_w, btn_y, btn_w, btn_h), lambda: self.set_type("hp"), hp_img)
        self.hp_btn.base_pos = self.hp_btn.rect.topleft
        self.type_buttons.append(self.hp_btn)
        
        # Initialize type selector position
        start_btn = self.dmg_btn
        self.type_selector_rect = pygame.Rect(start_btn.rect.topleft, start_btn.rect.size)
        self.type_selector_pos = pygame.math.Vector2(start_btn.rect.topleft)

        # Animation
        self.opening = True
        self.closing = False
        self.overlay_alpha = 0
        self.max_overlay_alpha = 150
        self.overlay_speed = 20
        self.active = True

        for el in self.elements:
            el.base_rect = el.rect.copy()
            
        self.refresh_card_list()

    def refresh_card_list(self):
        """Populate card_buttons with existing cards of type 'kartya'."""
        self.card_buttons = []
        y_off = 0
        # Filter for type="kartya"
        cards = [c for c in inventory.GAMECARDS if getattr(c, "type", "") == "kartya"]
        
        for i, card in enumerate(cards):
            # Create a button for each card
            # Width should match card_list_area width (360) minus padding/borders
            w, h = 360, 40 
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Use same bg color as popup or transparent-ish
            # User said "bg should follow the exact same color"
            # Use same bg color as deletecard popup list items
            surf.fill((230, 230, 230)) 
            pygame.draw.rect(surf, (50,50,50), surf.get_rect(), 1)
            
            # Format: Name DMG/HP Power
            name = card.name
            dmg = getattr(card, "dmg", "?")
            hp = getattr(card, "hp", "?")
            power = getattr(card, "power", "?")
            
            txt_str = f"{name} {dmg}/{hp} {power}"
            txt = BP.render(txt_str, True, (0,0,0)) # Black text
            surf.blit(txt, (10, 10))
            
            # Position relative to list area start
            bx = self.card_list_area.x
            by = self.card_list_area.y + y_off
            
            # We need to capture 'i' and 'card'
            btn = Button((bx, by, w, h), lambda c=card, idx=i: self.select_card(c, idx), surf)
            btn.base_pos = (bx, by)
            btn.base_pos = (bx, by)
            self.card_buttons.append(btn)
            y_off += 40 # tighter spacing
            
        # Calculate max scroll
        total_height = y_off
        self.max_scroll = max(0, total_height - self.card_list_area.height)

        # Auto-select first card if none selected and list is not empty
        if self.card_buttons and not self.selected_card:
            if cards: # Ensure cards list corresponds to buttons
                self.select_card(cards[0], 0)

    def select_card(self, card, index):
        self.selected_card = card
        self.selected_card_index = index
        
        # Update selector rect
        if 0 <= index < len(self.card_buttons):
            btn = self.card_buttons[index]
            # Selector rect relative to popup, same as button base_pos
            self.selector_rect = pygame.Rect(btn.base_pos[0], btn.base_pos[1], btn.rect.width, btn.rect.height)

    def set_type(self, t):
        self.selected_type = t

    def is_create_enabled(self):
        if not self.selected_card:
            return False
        if not self.prefix_entry.text.strip():
            return False
        return True

    def create_leader_card(self):
        if not self.is_create_enabled():
            return

        prefix = self.prefix_entry.text.strip()
        original = self.selected_card
        new_name = f"{prefix} {original.name}"
        
        # Check for duplicates
        for c in inventory.GAMECARDS:
            if c.name == new_name:
                # Name already exists
                self.error_label.set_text("Név már létezik!")
                return
        
        # Clear error if valid
        self.error_label.set_text("")
        
        # Logic update:
        # Power remains the same as original.
        # If "damage" selected -> double damage.
        # If "hp" selected -> double hp.
        
        new_dmg = original.dmg
        new_hp = original.hp
        
        if self.selected_type == "damage":
            new_dmg *= 2
        elif self.selected_type == "hp":
            new_hp *= 2
        
        new_card = objects.Card(
            "vezer",
            new_name,
            new_dmg,
            new_hp,
            original.power # keep original power
        )
        inventory.GAMECARDS.append(new_card)
        
        # Feedback
        self.status_counter = 60
        self.prefix_entry.set_text("")
        self.error_label.set_text("")
        self.selected_card = None
        self.selected_card_index = -1
        self.selector_rect = None
        
        # Hide button for a sec? User said "button disappearing for a sec"
        # We can handle that by checking status_counter in draw/update

    def reopen(self):
        if self.is_closed():
            self.rect.y = self.screen_height
            self.opening = True
            self.closing = False
            self.overlay_alpha = 0
            self.active = True
            self.error_label.set_text("") # Clear error on reopen
            self.refresh_card_list() # Refresh list on reopen

    def is_closed(self):
        return not self.opening and not self.closing and self.rect.y >= self.screen_height

    def close(self):
        self.closing = True
        self.opening = False

    def handle_event(self, event):
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            if not self.rect.collidepoint(event.pos):
                return True # Block clicks outside

        for el in self.elements:
            if el is self.create_btn and (not self.is_create_enabled() or self.status_counter > 0):
                continue
            el.handle_event(event)

        self.prefix_entry.handle_event(event)
        
        # Handle type buttons
        for btn in self.type_buttons:
            btn.handle_event(event)
            
        # Handle scrolling
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                 # Check if mouse is over list area (relative to screen)
                m_pos = pygame.mouse.get_pos()
                list_rect_screen = pygame.Rect(
                    self.rect.x + self.card_list_area.x,
                    self.rect.y + self.card_list_area.y,
                    self.card_list_area.width,
                    self.card_list_area.height
                )
                if list_rect_screen.collidepoint(m_pos):
                    self.scroll_y -= event.y * self.scroll_speed
                    self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
                    return True

        # Handle card list buttons
        # We need to adjust event pos or button rects for scrolling?
        # Easier: Update button rects in update() based on scroll, then handle event normally.
        # BUT we must only handle click if within list area.
        
        for btn in self.card_buttons:
            # Only handle event if button is visible in list area
            # We can check this by checking if the mouse click is within the list area
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                if not self.card_list_area.collidepoint(
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
            
        self.prefix_entry.rect.topleft = (self.rect.x + self.prefix_entry.base_pos[0], self.rect.y + self.prefix_entry.base_pos[1])
        self.prefix_entry.update(dt)
        
        for btn in self.type_buttons:
            btn.rect.topleft = (self.rect.x + btn.base_pos[0], self.rect.y + btn.base_pos[1])
            btn.update(dt)
            
        for btn in self.card_buttons:
            # Apply scroll offset
            btn.rect.topleft = (
                self.rect.x + btn.base_pos[0], 
                self.rect.y + btn.base_pos[1] - self.scroll_y
            )
            btn.update(dt)

        if self.status_counter > 0:
            self.status_counter -= 1
            
        # --- Type Selector Animation ---
        if self.opening or self.closing:
             # Lock to target during popup open/close
            if self.selected_type == "damage":
                target_btn = self.dmg_btn
            else:
                target_btn = self.hp_btn
            self.type_selector_pos = pygame.math.Vector2(target_btn.rect.topleft)
        else:
            # Smooth slide
            if self.selected_type == "damage":
                target_btn = self.dmg_btn
            else:
                target_btn = self.hp_btn
            
            target_pos = pygame.math.Vector2(target_btn.rect.topleft)
            self.type_selector_pos += (target_pos - self.type_selector_pos) * 0.2 # Smooth factor
            
        self.type_selector_rect.topleft = (round(self.type_selector_pos.x), round(self.type_selector_pos.y))
        self.type_selector_rect.size = self.dmg_btn.rect.size # Assuming same size

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
            if el is self.create_btn:
                if not self.is_create_enabled() or self.status_counter > 0:
                    continue
            el.draw(surf)
            
        self.prefix_entry.draw(surf)
        
        # Draw type buttons
        for btn in self.type_buttons:
            btn.draw(surf)
            
        # Draw type selector highlight (animated)
        pygame.draw.rect(surf, (255, 255, 0), self.type_selector_rect, 4)

        # Draw card list
        # List area background (optional, maybe just border)
        list_bg_rect = pygame.Rect(self.rect.x + self.card_list_area.x, self.rect.y + self.card_list_area.y, 
                              self.card_list_area.width, self.card_list_area.height)
        pygame.draw.rect(surf, (0, 0, 0), list_bg_rect, 2)
        
        # Draw card buttons
        if not self.card_buttons:
            # Show empty message if no cards
            # User requested: white and smaller
            # Use BP15
            empty_text = BP36.render("Nincsenek kártyák!", True, (255, 255, 255)) # White text
            empty_rect = empty_text.get_rect(center=list_bg_rect.center)
            surf.blit(empty_text, empty_rect)
        else:
            # Clip to list area
            surf.set_clip(list_bg_rect)
            for btn in self.card_buttons:
                btn.draw(surf)
            surf.set_clip(None)
            
        # Draw persistent selection highlight for card list
            
        # Draw persistent selection highlight for card list
        if self.selector_rect:
            # selector_rect is relative to popup
            # Apply scroll to selector
            abs_sel_rect = pygame.Rect(
                self.rect.x + self.selector_rect.x,
                self.rect.y + self.selector_rect.y - self.scroll_y,
                self.selector_rect.width,
                self.selector_rect.height
            )
            
            # Clip selector drawing too
            surf.set_clip(list_bg_rect)
            # User requested "selector red for the cards"
            pygame.draw.rect(surf, (255, 0, 0), abs_sel_rect, 3)
            surf.set_clip(None)

        # Status text
        if self.status_counter > 0:
            status_surf = BP.render("Vezérkártya létrehozva!", True, (0, 255, 0))
            status_rect = status_surf.get_rect(midbottom=(self.rect.x + 600, self.rect.y + 450))
            surf.blit(status_surf, status_rect)
