from manual.inventory import inventory, objects
import pygame
import os
import random
from manual.ui.button import Button
from manual.ui.label import Label
from manual.ui.text_entry import TextEntry
from manual.assets.assets import load_asset, ASSETS_DIR

sf = "configure"
pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 20)
BP2 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 2)
BP5 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 5)
BP8 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 8)
BP10 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 10)
BP12 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 12)
BP14 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 14)
BP15 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 15)
BP26 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 26)

class NewDungeonPopup:
    """Popup for creating a new Dungeon (Enemy) with manual card selection."""
    def __init__(self, close_callback, screen_size=(1280, 720)):
        screen_width, screen_height = screen_size
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Popup size and placement (Larger: 1000x600)
        w, h = 1000, 600
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        self.target_rect = pygame.Rect(x, y, w, h)
        self.rect = pygame.Rect(x, screen_height, w, h)

        # Appearance
        self.bg_color = (100, 50, 50)  # Dark red/brown
        self.border_color = (0, 0, 0)

        self.elements = []
        self.text_entries = []
        self.type_buttons = []
        self.reward_buttons = []
        
        # --- LEFT COLUMN (Controls) ---
        left_x = 50
        
        # Close button
        closebtn = load_asset("closebutton.png", sf)
        self.close_btn = Button((0, 0, 98, 98), close_callback, closebtn)
        self.elements.append(self.close_btn)

        # Title
        self.elements.append(Label((w // 2, 40, 0, 0), "Új kazamata", font=BP26, color=(255, 255, 255)))

        # Name Input
        self.elements.append(Label((left_x + 20, 120, 0, 0), "Név:", font=BP, color=(255, 255, 255)))
        # User requested: allow spaces, more chars, smaller font
        # User requested: allow spaces, more chars, smaller font
        self.name_entry = TextEntry((left_x + 100, 100, 300, 40), font=BP14, max_length=20, letters_only=False)
        self.name_entry.base_pos = self.name_entry.rect.topleft
        self.text_entries.append(self.name_entry)
        
        # Error Label for Name
        self.name_error_label = Label((left_x + 100, 80, 0, 0), "", font=BP12, color=(255, 0, 0))
        self.elements.append(self.name_error_label)

        # Type Selection
        self.selected_type = "egyszeru" # egyszeru, kis, nagy
        
        type_y = 200
        self.elements.append(Label((left_x + 20, type_y + 20, 0, 0), "Típus:", font=BP, color=(255, 255, 255)))
        
        # Type Buttons
        btn_w, btn_h = 130, 55
        
        # Simple Button
        simp_img = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(simp_img, (50, 200, 50), simp_img.get_rect(), border_radius=0)
        pygame.draw.rect(simp_img, (0,0,0), simp_img.get_rect(), width=2, border_radius=0)
        simp_txt = BP12.render("Egyszerű", True, (255,255,255))
        simp_img.blit(simp_txt, simp_txt.get_rect(center=(btn_w//2, btn_h//2)))
        
        self.simp_btn = Button((left_x + 100, type_y, btn_w, btn_h), lambda: self.set_type("egyszeru"), simp_img)
        self.simp_btn.base_pos = self.simp_btn.rect.topleft
        self.simp_btn.type_val = "egyszeru"
        self.simp_btn.label = "Egyszerű"
        self.type_buttons.append(self.simp_btn)
        
        # Normal Button
        norm_img = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(norm_img, (50, 50, 200), norm_img.get_rect(), border_radius=0)
        pygame.draw.rect(norm_img, (0,0,0), norm_img.get_rect(), width=2, border_radius=0)
        norm_txt = BP12.render("Normál", True, (255,255,255))
        norm_img.blit(norm_txt, norm_txt.get_rect(center=(btn_w//2, btn_h//2)))
        
        self.norm_btn = Button((left_x + 100 + 140, type_y, btn_w, btn_h), lambda: self.set_type("kis"), norm_img)
        self.norm_btn.base_pos = self.norm_btn.rect.topleft
        self.norm_btn.type_val = "kis"
        self.norm_btn.label = "Kis"
        self.type_buttons.append(self.norm_btn)
        
        # Boss Button
        boss_img = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(boss_img, (200, 50, 50), boss_img.get_rect(), border_radius=0)
        pygame.draw.rect(boss_img, (0,0,0), boss_img.get_rect(), width=2, border_radius=0)
        boss_txt = BP12.render("Nagy", True, (255,255,255))
        boss_img.blit(boss_txt, boss_txt.get_rect(center=(btn_w//2, btn_h//2)))
        
        self.boss_btn = Button((left_x + 100 + 280, type_y, btn_w, btn_h), lambda: self.set_type("nagy"), boss_img)
        self.boss_btn.base_pos = self.boss_btn.rect.topleft
        self.boss_btn.type_val = "nagy"
        self.boss_btn.label = "Nagy"
        self.type_buttons.append(self.boss_btn)

        # Reward Selection
        self.selected_reward = "sebzes" # sebzes, eletero, None
        
        reward_y = 280
        self.elements.append(Label((left_x + 70, reward_y + 20, 0, 0), "Jutalom:", font=BP, color=(255, 255, 255)))
        
        # Reward Buttons
        # Sebzes
        seb_img = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(seb_img, (200, 50, 50), seb_img.get_rect(), border_radius=0)
        pygame.draw.rect(seb_img, (0,0,0), seb_img.get_rect(), width=2, border_radius=0)
        seb_txt = BP12.render("Sebzés", True, (0,0,0))
        seb_img.blit(seb_txt, seb_txt.get_rect(center=(btn_w//2, btn_h//2)))
        
        self.seb_btn = Button((left_x + 150, reward_y, btn_w, btn_h), lambda: self.set_reward("sebzes"), seb_img)
        self.seb_btn.base_pos = self.seb_btn.rect.topleft
        self.seb_btn.reward_val = "sebzes"
        self.seb_btn.label = "Sebzés"
        self.reward_buttons.append(self.seb_btn)
        
        # Eletero
        el_img = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(el_img, (50, 200, 50), el_img.get_rect(), border_radius=0)
        pygame.draw.rect(el_img, (0,0,0), el_img.get_rect(), width=2, border_radius=0)
        el_txt = BP12.render("Életerő", True, (0,0,0))
        el_img.blit(el_txt, el_txt.get_rect(center=(btn_w//2, btn_h//2)))
        
        self.el_btn = Button((left_x + 150 + 140, reward_y, btn_w, btn_h), lambda: self.set_reward("eletero"), el_img)
        self.el_btn.base_pos = self.el_btn.rect.topleft
        self.el_btn.reward_val = "eletero"
        self.el_btn.label = "Életerő"
        self.reward_buttons.append(self.el_btn)

        # Requirements Label
        self.req_label = Label((left_x + 250, 380, 0, 0), "", font=BP15, color=(255, 255, 0))
        self.elements.append(self.req_label)
        
        # Create Button
        create_w, create_h = 250, 60
        create_x = left_x + 100
        create_y = 480
        
        create_surf = pygame.Surface((create_w, create_h), pygame.SRCALPHA)
        pygame.draw.rect(create_surf, (50, 200, 50), create_surf.get_rect(), border_radius=0)
        pygame.draw.rect(create_surf, (0, 0, 0), create_surf.get_rect(), width=3, border_radius=0)
        create_txt = BP.render("Létrehozás", True, (0,0,0))
        create_surf.blit(create_txt, create_txt.get_rect(center=(create_w//2, create_h//2)))
        
        self.create_btn = Button((create_x, create_y, create_w, create_h), self.create_dungeon, create_surf)
        self.create_btn.base_pos = (create_x, create_y)
        self.elements.append(self.create_btn)

        # --- RIGHT COLUMN (Card List) ---
        self.list_area = pygame.Rect(580, 100, 400, 450)
        self.card_buttons = []
        self.selected_cards = [] # List of card objects
        self.scroll_y = 0
        self.scroll_speed = 20
        self.max_scroll = 0
        
        self.refresh_card_list()

        # Status
        self.status_counter = 0
        self.error_msg = ""

        # Animation
        self.opening = True
        self.closing = False
        self.overlay_alpha = 0
        self.max_overlay_alpha = 150
        self.overlay_speed = 20
        self.active = True

        for el in self.elements:
            el.base_rect = el.rect.copy()
            
        self.update_requirements_text()

    def update_requirements_text(self):
        # Update requirement text based on type
        reqs = {
            "egyszeru": "Kell: 1 Normál",
            "kis": "Kell: 3 Normál, 1 Vezér",
            "nagy": "Kell: 5 Normál, 1 Vezér"
        }
        
        # Count current selection
        n_norm = len([c for c in self.selected_cards if getattr(c, "type", "") == "kartya"])
        n_lead = len([c for c in self.selected_cards if getattr(c, "type", "") == "vezer"])
        
        txt = f"{reqs[self.selected_type]}\nJelenleg: {n_norm} Normál, {n_lead} Vezér"
        self.req_label.set_text(txt)

    def refresh_card_list(self):
        self.card_buttons = []
        y_off = 0
        
        for i, card in enumerate(inventory.GAMECARDS):
            # Create button for list item
            w, h = self.list_area.width, 40
            # list_area is relative to popup
            # We need absolute coordinates for Button init?
            # Button expects absolute coordinates usually.
            # But we update it in update().
            # Let's calculate absolute pos assuming popup is at self.rect
            
            bx_rel = self.list_area.x
            by_rel = self.list_area.y + y_off
            
            bx_abs = self.rect.x + bx_rel
            by_abs = self.rect.y + by_rel
            
            # We'll draw the button content in draw() to handle selection state dynamically
            # But we need a button object for hit detection
            btn = Button((bx_abs, by_abs, w, h), lambda c=card: self.toggle_card(c), None)
            btn.base_pos = (bx_rel, by_rel) # Relative to popup
            btn.card_ref = card
            
            self.card_buttons.append(btn)
            y_off += 40
            
        self.max_scroll = max(0, y_off - self.list_area.height)

    def toggle_card(self, card):
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        else:
            self.selected_cards.append(card)
        self.update_requirements_text()

    def set_type(self, t):
        self.selected_type = t
        if t == "nagy":
            self.selected_reward = None
        elif self.selected_reward is None:
            self.selected_reward = "sebzes"
        self.update_requirements_text()

    def set_reward(self, r):
        if self.selected_type != "nagy":
            self.selected_reward = r

    def create_dungeon(self):
        name = self.name_entry.text.strip()
        if not name:
            self.error_msg = "Adj meg egy nevet!"
            self.status_counter = 60
            return
            
        # Check duplicate name
        for e in inventory.ENEMIES:
            if e.name == name:
                self.name_error_label.set_text("Név már létezik!")
                self.error_msg = "Név hiba!"
                self.status_counter = 60
                return
        self.name_error_label.set_text("")

        # Validate Cards
        normal_cards = [c for c in self.selected_cards if getattr(c, "type", "") == "kartya"]
        leader_cards = [c for c in self.selected_cards if getattr(c, "type", "") == "vezer"]
        
        valid = False
        if self.selected_type == "egyszeru":
            if len(normal_cards) == 1 and len(leader_cards) == 0:
                valid = True
            else:
                self.error_msg = "Kell: 1 Normál!"
                
        elif self.selected_type == "kis":
            if len(normal_cards) == 3 and len(leader_cards) == 1:
                valid = True
            else:
                self.error_msg = "Kell: 3 Normál, 1 Vezér!"
                
        elif self.selected_type == "nagy":
            if len(normal_cards) == 5 and len(leader_cards) == 1:
                valid = True
            else:
                self.error_msg = "Kell: 5 Normál, 1 Vezér!"

        if not valid:
            self.status_counter = 60
            return

        # Create Enemy
        # We need to copy the cards? Or reference them?
        # Usually decks contain copies so they can be modified (hp) without affecting original
        import copy
        deck = [copy.deepcopy(c) for c in self.selected_cards]
        
        new_enemy = objects.Enemy(self.selected_type, name, deck, self.selected_reward)
        inventory.ENEMIES.append(new_enemy)
        
        self.error_msg = ""
        self.status_counter = 60 # Success message
        self.name_entry.set_text("")
        self.selected_cards = []
        self.update_requirements_text()

    def reopen(self):
        if self.is_closed():
            self.rect.y = self.screen_height
            self.opening = True
            self.closing = False
            self.overlay_alpha = 0
            self.active = True
            self.error_msg = ""
            self.name_error_label.set_text("")
            self.selected_cards = []
            self.refresh_card_list()
            self.update_requirements_text()

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
        
        self.name_entry.handle_event(event)
        
        for btn in self.type_buttons:
            btn.handle_event(event)
            
        if self.selected_type != "nagy":
            for btn in self.reward_buttons:
                btn.handle_event(event)
                
        # Handle Scrolling
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
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

        # Handle Card List Buttons
        for btn in self.card_buttons:
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                if not self.list_area.collidepoint(
                    event.pos[0] - self.rect.x, 
                    event.pos[1] - self.rect.y
                ):
                    continue
            btn.handle_event(event)

        return True

    def update(self, dt):
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

        for el in self.elements:
            el.rect.topleft = (self.rect.x + el.base_rect.x, self.rect.y + el.base_rect.y)
            el.update(dt)
            
        self.name_entry.rect.topleft = (self.rect.x + self.name_entry.base_pos[0], self.rect.y + self.name_entry.base_pos[1])
        self.name_entry.update(dt)
        
        for btn in self.type_buttons:
            btn.rect.topleft = (self.rect.x + btn.base_pos[0], self.rect.y + btn.base_pos[1])
            btn.update(dt)
            
        for btn in self.reward_buttons:
            btn.rect.topleft = (self.rect.x + btn.base_pos[0], self.rect.y + btn.base_pos[1])
            btn.update(dt)
            
        # Update Card Buttons
        for btn in self.card_buttons:
            # base_pos is relative to popup (e.g. 550, 100)
            # We need to add popup pos + scroll
            # But scroll only affects Y
            # And we need to keep X relative to popup
            
            # btn.base_pos[0] is list_area.x (550)
            # btn.base_pos[1] is list_area.y + offset (100 + ...)
            
            btn.rect.topleft = (
                self.rect.x + btn.base_pos[0], 
                self.rect.y + btn.base_pos[1] - self.scroll_y
            )
            btn.update(dt)

        if self.status_counter > 0:
            self.status_counter -= 1

    def draw(self, surf):
        if self.rect.y > self.screen_height and self.overlay_alpha <= 0:
            return

        overlay = pygame.Surface((self.screen_width, self.screen_height), flags=pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.overlay_alpha))
        surf.blit(overlay, (0, 0))

        pygame.draw.rect(surf, self.bg_color, self.rect)
        pygame.draw.rect(surf, self.border_color, self.rect, 2)

        for el in self.elements:
            el.draw(surf)
            
        self.name_entry.draw(surf)
        
        # Draw Type Buttons
        for btn in self.type_buttons:
            s = pygame.Surface((btn.rect.width, btn.rect.height))
            if self.selected_type == btn.type_val:
                s.fill((100, 200, 100))
            else:
                s.fill((200, 200, 200))
            pygame.draw.rect(s, (0,0,0), s.get_rect(), 2)
            txt = BP15.render(btn.label, True, (0,0,0))
            s.blit(txt, txt.get_rect(center=(btn.rect.width//2, btn.rect.height//2)))
            surf.blit(s, btn.rect)
            
        # Draw Reward Buttons
        if self.selected_type != "nagy":
            for btn in self.reward_buttons:
                s = pygame.Surface((btn.rect.width, btn.rect.height))
                if self.selected_reward == btn.reward_val:
                    s.fill((100, 200, 100))
                else:
                    s.fill((200, 200, 200))
                pygame.draw.rect(s, (0,0,0), s.get_rect(), 2)
                txt = BP15.render(btn.label, True, (0,0,0))
                s.blit(txt, txt.get_rect(center=(btn.rect.width//2, btn.rect.height//2)))
                surf.blit(s, btn.rect)

        # Draw Card List
        abs_list_rect = pygame.Rect(
            self.rect.x + self.list_area.x,
            self.rect.y + self.list_area.y,
            self.list_area.width,
            self.list_area.height
        )
        
        # Background for list
        pygame.draw.rect(surf, (80, 40, 20), abs_list_rect)
        pygame.draw.rect(surf, (0, 0, 0), abs_list_rect, 2)
        
        surf.set_clip(abs_list_rect)
        
        for btn in self.card_buttons:
            # Only draw if visible
            if btn.rect.bottom > abs_list_rect.top and btn.rect.top < abs_list_rect.bottom:
                # Draw button content
                card = btn.card_ref
                selected = card in self.selected_cards
                
                s = pygame.Surface((btn.rect.width, btn.rect.height))
                if selected:
                    s.fill((100, 150, 100)) # Greenish if selected
                else:
                    s.fill((200, 200, 200))
                
                pygame.draw.rect(s, (0,0,0), s.get_rect(), 1)
                if selected:
                    pygame.draw.rect(s, (0, 255, 0), s.get_rect(), 3)
                
                # Text: Name (Type)
                # Text: Name (Type)
                type_str = getattr(card, "type", "?")
                if type_str == "kartya":
                    type_str = "normál"
                name_str = getattr(card, "name", "???")
                
                # Stats
                dmg = getattr(card, "dmg", 0)
                hp = getattr(card, "hp", 0)
                power = getattr(card, "power", "")
                
                # Draw Name
                txt_name = BP12.render(f"{name_str} ({type_str})", True, (0,0,0))
                s.blit(txt_name, txt_name.get_rect(topleft=(10, 5)))
                
                # Draw Stats
                stats_str = f"S:{dmg} É:{hp} E:{power}"
                txt_stats = BP10.render(stats_str, True, (50, 50, 50))
                s.blit(txt_stats, txt_stats.get_rect(bottomleft=(10, btn.rect.height - 5)))
                
                # Draw Selection Order Number
                if selected:
                    order_idx = self.selected_cards.index(card) + 1
                    # Draw a small circle with the number
                    circle_radius = 12
                    circle_center = (btn.rect.width - 20, btn.rect.height // 2)
                    pygame.draw.circle(s, (255, 255, 0), circle_center, circle_radius)
                    pygame.draw.circle(s, (0, 0, 0), circle_center, circle_radius, 1)
                    
                    num_txt = BP12.render(str(order_idx), True, (0, 0, 0))
                    num_rect = num_txt.get_rect(center=circle_center)
                    s.blit(num_txt, num_rect)
                
                surf.blit(s, btn.rect)
                
        surf.set_clip(None)

        # Status / Error
        if self.status_counter > 0:
            if self.error_msg:
                msg = BP.render(self.error_msg, True, (255, 0, 0))
            else:
                msg = BP.render("Kazamata létrehozva!", True, (0, 255, 0))
            
            r = msg.get_rect(midbottom=(self.rect.centerx, self.rect.bottom - 10))
            surf.blit(msg, r)
