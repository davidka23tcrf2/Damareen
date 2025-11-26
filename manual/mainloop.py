import pygame, sys, json, os
from manual.screens.configure import CONFIGURE
from manual.screens.inventory import InventoryScreen
from manual.screens.start import StartScreen
from manual.ui.ui_manager import UIStateManager
from manual.screens.shop import ShopScreen
from manual.screens.arena import ArenaScreen
from manual.screens.menu import MenuScreen
from manual.screens.gameloader import GameLoader
from manual.screens.deckbuilder import DeckBuilderScreen
from manual.screens.savedgames import SavedGamesScreen
from manual.ui.global_settings_popup import GlobalSettingsPopup
from manual.screens.settingspopup import SettingsPopup

def ml():
    """Main game loop - only runs when explicitly called"""
    # Initialize pygame only when UI is needed
    pygame.init()
    SCREEN_SIZE = (1280, 720)
    SCREEN = pygame.display.set_mode(SCREEN_SIZE)
    CLOCK = pygame.time.Clock()
    pygame.display.set_caption("Damareen")
    ui = UIStateManager(SCREEN_SIZE)

    def goto_shop(): ui.switch_to("SHOP", duration=0.5)
    def goto_arena():
        ui.screens["ARENA"].setup_combat()
        ui.switch_to("ARENA", duration=0.5)
    def goto_menu():
        ui.screens["CONFIGURE"].stop_music()
        ui.switch_to("MENU", duration=0.5)
    def goto_inventory():
        # Refresh inventory display before showing the screen
        ui.screens["INVENTORY"].refresh_inventory()
        ui.set("INVENTORY")
    def goto_deckbuilder():
        ui.screens["DECKBUILDER"].refresh_list()
        ui.switch_to("DECKBUILDER", duration=0.5)
    def goto_gameloader():
        ui.screens["GAMELOADER"].reload_saves()
        ui.switch_to("GAMELOADER", duration=0.5)
    def goto_configure():
        ui.screens["CONFIGURE"].start_music()
        ui.switch_to("CONFIGURE", duration=0.5)
    def goto_start():
        ui.screens["CONFIGURE"].stop_music()
        ui.switch_to("START", duration=0.5)
    def goto_savedgames():
        ui.screens["SAVEDGAMES"].reload_saves()
        ui.switch_to("SAVEDGAMES", duration=0.5)

    ui.add("SHOP", ShopScreen(goto_menu))
    ui.add("ARENA", ArenaScreen(goto_shop, goto_menu, goto_start))
    ui.add("DECKBUILDER", DeckBuilderScreen(goto_menu))
    ui.add("MENU", MenuScreen(goto_arena, goto_shop, goto_deckbuilder, goto_inventory))
    ui.add("START", StartScreen(goto_configure, goto_gameloader, goto_savedgames))
    ui.add("GAMELOADER", GameLoader(goto_menu, goto_start))
    ui.add("CONFIGURE", CONFIGURE(goto_start, goto_menu))
    ui.add("SAVEDGAMES", SavedGamesScreen(goto_start, goto_menu))
    ui.add("INVENTORY", InventoryScreen(goto_menu))

    ui.set("START")

    # Global settings popup
    global_settings_popup = None
    settings_popup = None  # Full settings popup for menu
    
    def toggle_global_settings():
        nonlocal global_settings_popup, settings_popup
        
        # If in menu, use the full SettingsPopup
        if ui.active == ui.screens.get("MENU"):
            # Close any active popups first
            menu_screen = ui.screens["MENU"]
            if hasattr(menu_screen, 'difficulty_popup') and menu_screen.difficulty_popup and menu_screen.difficulty_popup.active:
                menu_screen.difficulty_popup.active = False
                menu_screen.difficulty_popup = None
            if hasattr(menu_screen, 'dungeon_popup') and menu_screen.dungeon_popup and menu_screen.dungeon_popup.active:
                menu_screen.dungeon_popup.active = False
                menu_screen.dungeon_popup = None
            
            if settings_popup and settings_popup.active:
                settings_popup.close()
            else:
                settings_popup = SettingsPopup(close_callback=lambda: None)
        else:
            # Otherwise use the simplified global settings
            if global_settings_popup and global_settings_popup.active:
                global_settings_popup.close()
            else:
                global_settings_popup = GlobalSettingsPopup(close_callback=lambda: None)

    while True:
        dt = CLOCK.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Global ESC key for settings
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                toggle_global_settings()
                continue
            
            # If global settings is active, it handles events
            if global_settings_popup and global_settings_popup.active:
                global_settings_popup.handle_event(event)
            elif settings_popup and settings_popup.active:
                settings_popup.handle_event(event)
            else:
                ui.handle_event(event)
        
        # Update global settings if active
        if global_settings_popup and global_settings_popup.active:
            global_settings_popup.update(dt)
        if settings_popup and settings_popup.active:
            settings_popup.update(dt)
        
        ui.update(dt)
        ui.draw(SCREEN)
        
        # Draw global settings on top of everything
        if global_settings_popup and global_settings_popup.active:
            global_settings_popup.draw(SCREEN)
        if settings_popup and settings_popup.active:
            settings_popup.draw(SCREEN)
        
        pygame.display.flip()
