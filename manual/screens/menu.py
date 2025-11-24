import pygame, os
from ..ui.button import Button
from ..ui.label import Label
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory import inventory
from manual.screens.difficultypopup import DifficultyPopup
from manual.screens.settingspopup import SettingsPopup
<<<<<<< Updated upstream
from manual.screens.dungeonpopup import DungeonPopup
=======
>>>>>>> Stashed changes
from manual.ui import theme
from manual.ui.particles import ParticleManager

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 20)

class MenuScreen:
    def __init__(self, goto_arena, goto_shop, goto_deckbuilder):
        self.elements = []
        self.goto_arena = goto_arena
        self.goto_shop = goto_shop
        self.goto_deckbuilder = goto_deckbuilder
        
<<<<<<< Updated upstream
        # Deck Builder Button (Bigger)
        self.elements.append(Button(
            (50, 300, 400, 80),
=======
        # Deck Builder Button
        self.elements.append(Button(
            (50, 300, 300, 60),
>>>>>>> Stashed changes
            self.goto_deckbuilder,
            None,
            text="Pakli összeállítása",
            font=BP,
            text_color=theme.TEXT_WHITE,
            bg_color=theme.PRIMARY,
            hover_bg_color=theme.PRIMARY_HOVER
        ))
        
        # New Fight Button (Bigger)
        self.fight_btn = Button(
            (1280 - 350, 720 - 120, 300, 80),
            self.try_goto_arena,
            None,
            text="Új harc",
            font=BP,
            text_color=theme.TEXT_WHITE,
            bg_color=theme.PRIMARY,
            hover_bg_color=theme.PRIMARY_HOVER
        )
        self.elements.append(self.fight_btn)
        
<<<<<<< Updated upstream
        # Settings button (Bigger)
        self.settings_btn = Button(
            (1280 - 200, 20, 180, 60),
=======
        # Settings button (top-right)
        self.settings_btn = Button(
            (1280 - 160, 20, 140, 50),
>>>>>>> Stashed changes
            self.open_settings,
            None,
            text="⚙ Beállítások",
            font=BP,
            text_color=theme.TEXT_WHITE,
            bg_color=theme.SECONDARY,
            hover_bg_color=theme.SECONDARY_HOVER,
            border_radius=8
        )
        self.elements.append(self.settings_btn)
        
<<<<<<< Updated upstream
        # Dungeon Selector Button
        self.dungeon_btn = Button(
            (1280 - 350, 720 - 200, 300, 60),
            self.open_dungeon_popup,
            None,
            text="Kazamata kiválasztása",
            font=BP,
            text_color=theme.TEXT_WHITE,
            bg_color=theme.SECONDARY,
            hover_bg_color=theme.SECONDARY_HOVER,
            border_radius=8
        )
        self.elements.append(self.dungeon_btn)
        
        self.difficulty_popup = None
        self.settings_popup = None
        self.dungeon_popup = None
        
        self.update_dungeon_label()

    def update_dungeon_label(self):
        if not inventory.ENEMIES:
            self.dungeon_btn.text = "Nincs elérhető kazamata"
        else:
            idx = inventory.SELECTED_DUNGEON_INDEX
            # Ensure index is valid
            if idx >= len(inventory.ENEMIES):
                inventory.SELECTED_DUNGEON_INDEX = 0
                idx = 0
            
            dungeon_name = inventory.ENEMIES[idx].name
            self.dungeon_btn.text = f"{dungeon_name}"
=======
        self.difficulty_popup = None
        self.settings_popup = None
>>>>>>> Stashed changes

    def try_goto_arena(self):
        if len(inventory.PLAYERDECK) > 0 and inventory.ENEMIES:
            self.goto_arena()

    def open_settings(self):
        if not self.settings_popup:
            self.settings_popup = SettingsPopup(self.close_settings_popup)
<<<<<<< Updated upstream
            
    def open_dungeon_popup(self):
        if not self.dungeon_popup and inventory.ENEMIES:
            self.dungeon_popup = DungeonPopup(self.close_dungeon_popup)
=======
>>>>>>> Stashed changes
    
    def handle_event(self, e):
        if self.settings_popup and self.settings_popup.active:
            handled = self.settings_popup.handle_event(e)
            if handled: return
        
        if self.difficulty_popup and self.difficulty_popup.active:
            handled = self.difficulty_popup.handle_event(e)
            if handled: return
<<<<<<< Updated upstream
            
        if self.dungeon_popup and self.dungeon_popup.active:
            handled = self.dungeon_popup.handle_event(e)
            if handled: return
=======
>>>>>>> Stashed changes

        for el in self.elements: el.handle_event(e)
        
    def update(self, dt):
        # Settings popup takes priority
        if self.settings_popup and self.settings_popup.active:
            self.settings_popup.update(dt)
            return

        # Check if difficulty is selected
        if not inventory.DIFFICULTY_SELECTED and self.difficulty_popup is None:
            self.difficulty_popup = DifficultyPopup(self.close_difficulty_popup)
            
        if self.difficulty_popup and self.difficulty_popup.active:
            self.difficulty_popup.update(dt)
            return
<<<<<<< Updated upstream
            
        if self.dungeon_popup and self.dungeon_popup.active:
            self.dungeon_popup.update(dt)
            return

        # Update Fight Button State
        if len(inventory.PLAYERDECK) > 0 and inventory.ENEMIES:
=======

        # Update Fight Button State
        if len(inventory.PLAYERDECK) > 0:
>>>>>>> Stashed changes
            self.fight_btn.bg_color = theme.PRIMARY
            self.fight_btn.hover_bg_color = theme.PRIMARY_HOVER
        else:
            self.fight_btn.bg_color = theme.SECONDARY
            self.fight_btn.hover_bg_color = theme.SECONDARY
            
<<<<<<< Updated upstream
        for el in self.elements:
            el.update(dt)

    def draw(self, surf):
        # Draw background (black)
        surf.fill((0, 0, 0))
        
        # Draw elements
        for el in self.elements:
            el.draw(surf)
            
        # Draw popups
        if self.difficulty_popup and self.difficulty_popup.active:
            self.difficulty_popup.draw(surf)
            
        if self.settings_popup and self.settings_popup.active:
            self.settings_popup.draw(surf)
            
        if self.dungeon_popup and self.dungeon_popup.active:
            self.dungeon_popup.draw(surf)

    def close_difficulty_popup(self):
        self.difficulty_popup = None

    def close_settings_popup(self):
        self.settings_popup = None
        
    def close_dungeon_popup(self):
        self.dungeon_popup = None
        self.update_dungeon_label()
=======
        for el in self.elements: el.update(dt)
        
    def draw(self, surf):
        # Fill with black
        surf.fill((0, 0, 0))
        
        for el in self.elements:
            el.draw(surf)
            
        if self.difficulty_popup and self.difficulty_popup.active:
            self.difficulty_popup.draw(surf)
        
        if self.settings_popup and self.settings_popup.active:
            self.settings_popup.draw(surf)

    def close_difficulty_popup(self):
        self.difficulty_popup = None
    
    def close_settings_popup(self):
        self.settings_popup = None
>>>>>>> Stashed changes
