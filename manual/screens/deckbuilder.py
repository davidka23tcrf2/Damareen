import pygame, math, os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory import inventory

from manual.ui.particles import ParticleManager
from manual.ui.vignette import create_red_vignette

sf = "configure"
pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 20)
BP12 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 12)

class DeckBuilderScreen:
    def __init__(self, goto_menu):
        self.goto_menu = goto_menu
        self.elements = []
        
        # Red vignette and particles
        self.particles = ParticleManager(mode="blood")
        self.vignette = create_red_vignette()
        # Removed background for black background
        
        # Back Button
        back_btn = Button(
            (30, 30, 180, 70),
            self.exit_screen,
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
        
        # Title
        self.elements.append(Label((640, 50, 0, 0), "Pakli összeállítása", font=BP, color=(255, 255, 255)))
        
        # Stats Label
        self.stats_label = Label((640, 90, 0, 0), "", font=BP, color=(255, 255, 0))
        self.elements.append(self.stats_label)
        
        # --- LEFT: Current Deck ---
        self.deck_area = pygame.Rect(50, 150, 400, 500)
        self.deck_scroll_y = 0
        self.deck_max_scroll = 0
        self.deck_buttons = []
        
        self.elements.append(Label((250, 130, 0, 0), "Jelenlegi Pakli", font=BP, color=(255, 255, 255)))

        # --- RIGHT: Collection ---
        self.coll_area = pygame.Rect(500, 150, 730, 500)
        self.coll_scroll_y = 0
        self.coll_max_scroll = 0
        self.coll_buttons = []
        
        self.elements.append(Label((865, 130, 0, 0), "Gyűjtemény", font=BP, color=(255, 255, 255)))

        self.scroll_speed = 20
        
        self.refresh_lists()

    def exit_screen(self):
        self.goto_menu()

    def refresh_lists(self):
        self.refresh_deck_list()
        self.refresh_collection_list()
        self.update_stats()

    def refresh_deck_list(self):
        self.deck_buttons = []
        y_off = 0
        card_h = 40
        spacing = 5
        
        for i, card in enumerate(inventory.PLAYERDECK):
            # Button for deck item
            w = self.deck_area.width
            h = card_h
            
            x = self.deck_area.x
            y = self.deck_area.y + y_off
            
            btn = Button((x, y, w, h), lambda c=card: self.remove_from_deck(c), None)
            btn.base_pos = (0, y_off) # Relative to deck area
            btn.card_ref = card
            
            self.deck_buttons.append(btn)
            y_off += card_h + spacing
            
        self.deck_max_scroll = max(0, y_off - self.deck_area.height)

    def refresh_collection_list(self):
        self.coll_buttons = []
        
        # Grid layout for collection
        cols = 2
        card_w = (self.coll_area.width - (cols-1)*10) // cols
        card_h = 40
        spacing_x, spacing_y = 10, 5
        
        # Show ALL cards in collection
        # If in deck, we will grey them out in draw() or handle click differently
        
        available_cards = inventory.PLAYERCARDS
        
        for i, card in enumerate(available_cards):
            row = i // cols
            col = i % cols
            
            x_rel = col * (card_w + spacing_x)
            y_rel = row * (card_h + spacing_y)
            
            x = self.coll_area.x + x_rel
            y = self.coll_area.y + y_rel
            
            btn = Button((x, y, card_w, card_h), lambda c=card: self.add_to_deck(c), None)
            btn.base_pos = (x_rel, y_rel) # Relative to coll area
            btn.card_ref = card
            
            self.coll_buttons.append(btn)
            
        total_rows = math.ceil(len(available_cards) / cols)
        total_h = total_rows * (card_h + spacing_y)
        self.coll_max_scroll = max(0, total_h - self.coll_area.height)

    def add_to_deck(self, card):
        if card in inventory.PLAYERDECK:
            return # Already in deck
            
        max_size = math.ceil(len(inventory.PLAYERCARDS) / 2)
        if len(inventory.PLAYERDECK) < max_size:
            inventory.PLAYERDECK.append(card)
            self.refresh_lists() # Rebuild lists to move card

    def remove_from_deck(self, card):
        if card in inventory.PLAYERDECK:
            inventory.PLAYERDECK.remove(card)
            self.refresh_lists()

    def update_stats(self):
        max_size = math.ceil(len(inventory.PLAYERCARDS) / 2)
        current = len(inventory.PLAYERDECK)
        self.stats_label.set_text(f"Pakli: {current} / {max_size}")

    def refresh_list(self):
        # Alias for external calls if any
        self.refresh_lists()

    def handle_event(self, event):
        for el in self.elements:
            el.handle_event(event)
            
        # Scrolling
        if event.type == pygame.MOUSEWHEEL:
            m_pos = pygame.mouse.get_pos()
            if self.deck_area.collidepoint(m_pos):
                self.deck_scroll_y -= event.y * self.scroll_speed
                self.deck_scroll_y = max(0, min(self.deck_scroll_y, self.deck_max_scroll))
            elif self.coll_area.collidepoint(m_pos):
                self.coll_scroll_y -= event.y * self.scroll_speed
                self.coll_scroll_y = max(0, min(self.coll_scroll_y, self.coll_max_scroll))
                
        # Deck Buttons
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            for btn in self.deck_buttons:
                if self.deck_area.collidepoint(event.pos):
                     btn.handle_event(event)
                     
            # Collection Buttons
            for btn in self.coll_buttons:
                if self.coll_area.collidepoint(event.pos):
                     btn.handle_event(event)

    def update(self, dt):
        self.particles.update(dt)
        
        for el in self.elements:
            el.update(dt)
            
        # Update deck buttons
        for btn in self.deck_buttons:
            btn.rect.topleft = (
                self.deck_area.x + btn.base_pos[0],
                self.deck_area.y + btn.base_pos[1] - self.deck_scroll_y
            )
            btn.update(dt)
            
        # Update collection buttons
        for btn in self.coll_buttons:
            btn.rect.topleft = (
                self.coll_area.x + btn.base_pos[0],
                self.coll_area.y + btn.base_pos[1] - self.coll_scroll_y
            )
            btn.update(dt)

    def draw_card_btn(self, surf, btn, area_rect):
        if btn.rect.bottom > area_rect.top and btn.rect.top < area_rect.bottom:
            card = btn.card_ref
            in_deck = card in inventory.PLAYERDECK
            
            s = pygame.Surface((btn.rect.width, btn.rect.height))
            
            # Different color if in deck (only for collection view?)
            # But this method is used for both...
            # If in deck area, it IS in deck.
            # If in collection area, it MIGHT be in deck.
            
            if area_rect == self.coll_area and in_deck:
                s.fill((100, 100, 100)) # Darker/Greyed out
            else:
                s.fill((200, 200, 200)) # Normal
                
            pygame.draw.rect(s, (0,0,0), s.get_rect(), 1)
            
            # Render Text: Name DMG/HP Power
            name = getattr(card, "name", "???")
            dmg = getattr(card, "dmg", "?")
            hp = getattr(card, "hp", "?")
            power = getattr(card, "power", "?")
            
            txt_str = f"{name} {dmg}/{hp} {power}"
            txt = BP12.render(txt_str, True, (0,0,0))
            s.blit(txt, txt.get_rect(midleft=(10, btn.rect.height//2)))
            
            surf.blit(s, btn.rect)

    def draw(self, surf):
        surf.fill((0, 0, 0))  # Black background
        # Draw particles
        self.particles.draw(surf)
        
        # Draw vignette
        surf.blit(self.vignette, (0, 0))
        
        for el in self.elements:
            el.draw(surf)
            
        # Draw Deck Area
        pygame.draw.rect(surf, (0, 0, 0), self.deck_area) # Opaque black
        pygame.draw.rect(surf, (255, 255, 255), self.deck_area, 2)
        
        surf.set_clip(self.deck_area)
        for btn in self.deck_buttons:
            self.draw_card_btn(surf, btn, self.deck_area)
        surf.set_clip(None)
        
        # Draw Collection Area
        pygame.draw.rect(surf, (0, 0, 0), self.coll_area) # Opaque black
        pygame.draw.rect(surf, (255, 255, 255), self.coll_area, 2)
        
        surf.set_clip(self.coll_area)
        for btn in self.coll_buttons:
            self.draw_card_btn(surf, btn, self.coll_area)
        surf.set_clip(None)
