import pygame, sys, json, os

def ml():
    """Main game loop - only runs when explicitly called"""

    # --- Init pygame ---
    pygame.init()
    pygame.mixer.init()

    # --- Window & basic drawing asap so we don't get a dead / white screen ---
    SCREEN_SIZE = (1280, 720)
    SCREEN = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Damareen")
    CLOCK = pygame.time.Clock()

    # Immediate black screen (prevents white flash)
    SCREEN.fill((0, 0, 0))
    pygame.display.flip()

    # --- Imports (after pygame init & window created) ---
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
    from manual.ui.grain import GrainEffect

    # --- UI State Manager ---
    ui = UIStateManager(SCREEN_SIZE)

    # --- Grain Effect ---
    grain = GrainEffect(SCREEN_SIZE[0], SCREEN_SIZE[1], intensity=40)

    # --- Music State ---
    current_music = None  # "horror" or None

    def start_horror_music():
        """Ensure horror background music is playing in a loop."""
        nonlocal current_music
        if current_music == "horror":
            return
        try:
            pygame.mixer.music.load(os.path.join("manual", "assets", "sounds", "horrorbg.mp3"))
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.3)
            current_music = "horror"
        except Exception as e:
            print(f"Failed to play horrorbg: {e}")
            current_music = None

    def start_fight_music():
        """Ensure fight music is playing in a loop."""
        nonlocal current_music
        if current_music == "fight":
            return
        try:
            pygame.mixer.music.load(os.path.join("manual", "assets", "sounds", "fight.mp3"))
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.3)
            current_music = "fight"
        except Exception as e:
            print(f"Failed to play fight music: {e}")
            current_music = None

    def start_menu_music():
        """Ensure menu music is playing in a loop."""
        nonlocal current_music
        if current_music == "menu":
            return
        try:
            pygame.mixer.music.load(os.path.join("manual", "assets", "sounds", "menu.mp3"))
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.3)
            current_music = "menu"
        except Exception as e:
            print(f"Failed to play menu music: {e}")
            current_music = None

    def stop_any_music():
        """Stop whatever music is currently playing."""
        nonlocal current_music
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        current_music = None

    def manage_music(target_screen_name: str):
        """
        Central place to control music when changing screens.

        Rules:
        - CONFIGURE: stop horror, configure screen handles its own music.
        - ARENA: play fight music.
        - MENU, SHOP, INVENTORY, DECKBUILDER: play menu music.
        - Everything else (START, GAMELOADER, SAVEDGAMES): ensure horror music is playing.
        """
        nonlocal current_music

        # Going TO CONFIGURE
        if target_screen_name == "CONFIGURE":
            if current_music == "horror":
                stop_any_music()
            # CONFIGURE screen can have its own start_music/stop_music methods
            if "CONFIGURE" in ui.screens:
                configure_screen = ui.screens["CONFIGURE"]
                if hasattr(configure_screen, "start_music"):
                    configure_screen.start_music()
            return

        # If we are LEAVING CONFIGURE
        if ui.active == ui.screens.get("CONFIGURE"):
            configure_screen = ui.screens.get("CONFIGURE")
            if configure_screen and hasattr(configure_screen, "stop_music"):
                configure_screen.stop_music()

        # Handle ARENA
        if target_screen_name == "ARENA":
            start_fight_music()
            return

        # Handle Menu-related screens
        if target_screen_name in ["MENU", "SHOP", "INVENTORY", "DECKBUILDER"]:
            start_menu_music()
            return

        # For all other screens, keep horror bg music
        start_horror_music()

    # --- Screen switch helpers (lazy-create screens so startup is lighter) ---

    def goto_shop():
        manage_music("SHOP")
        ui.switch_to("SHOP", duration=0.5)

    def goto_arena():
        manage_music("ARENA")
        ui.screens["ARENA"].setup_combat()
        ui.switch_to("ARENA", duration=0.5)

    def goto_menu():
        manage_music("MENU")
        # Reset shop with new items after fights
        if ui.active == ui.screens.get("ARENA"):
            ui.screens["SHOP"].reset_shop()
        ui.switch_to("MENU", duration=0.5)

    def goto_inventory():
        manage_music("INVENTORY")
        ui.screens["INVENTORY"].refresh_inventory()
        ui.set("INVENTORY")

    def goto_deckbuilder():
        manage_music("DECKBUILDER")
        ui.screens["DECKBUILDER"].refresh_list()
        ui.switch_to("DECKBUILDER", duration=0.5)

    def goto_gameloader():
        manage_music("GAMELOADER")
        ui.screens["GAMELOADER"].reload_saves()
        ui.switch_to("GAMELOADER", duration=0.5)

    def goto_configure():
        manage_music("CONFIGURE")
        ui.switch_to("CONFIGURE", duration=0.5)

    def goto_start():
        # START screen uses horror by default
        manage_music("START")
        ui.switch_to("START", duration=0.5)

    def goto_savedgames():
        manage_music("SAVEDGAMES")
        ui.screens["SAVEDGAMES"].reload_saves()
        ui.switch_to("SAVEDGAMES", duration=0.5)

    # --- Create all screens at startup for instant navigation ---
    # Show loading screen
    SCREEN.fill((0, 0, 0))
    loading_font = pygame.font.SysFont("Arial", 48)
    loading_text = loading_font.render("Jatek betoltese...", True, (255, 255, 255))
    loading_rect = loading_text.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2))
    SCREEN.blit(loading_text, loading_rect)
    pygame.display.flip()
    
    # Clear event queue to block input during loading
    pygame.event.clear()
    
    ui.add("START", StartScreen(goto_configure, goto_gameloader, goto_savedgames))
    pygame.event.clear()  # Clear events after each screen
    
    ui.add("MENU", MenuScreen(goto_arena, goto_shop, goto_deckbuilder, goto_inventory))
    pygame.event.clear()
    
    ui.add("SHOP", ShopScreen(goto_menu))
    pygame.event.clear()
    
    ui.add("ARENA", ArenaScreen(goto_shop, goto_menu, goto_start))
    pygame.event.clear()
    
    ui.add("DECKBUILDER", DeckBuilderScreen(goto_menu))
    pygame.event.clear()
    
    ui.add("INVENTORY", InventoryScreen(goto_menu))
    pygame.event.clear()
    
    ui.add("GAMELOADER", GameLoader(goto_menu, goto_start))
    pygame.event.clear()
    
    ui.add("CONFIGURE", CONFIGURE(goto_start, goto_menu))
    pygame.event.clear()
    
    ui.add("SAVEDGAMES", SavedGamesScreen(goto_start, goto_menu))
    pygame.event.clear()
    
    ui.set("START")
    start_horror_music()  # start music once game is ready

    # --- Global settings popups ---
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

    # --- Main game loop ---
    while True:
        dt = CLOCK.tick(60) / 1000.0

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Global ESC key for settings
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                toggle_global_settings()
                continue

            # If a popup is active, it eats the events
            if global_settings_popup and global_settings_popup.active:
                global_settings_popup.handle_event(event)
            elif settings_popup and settings_popup.active:
                settings_popup.handle_event(event)
            else:
                ui.handle_event(event)

        # Updates
        if global_settings_popup and global_settings_popup.active:
            global_settings_popup.update(dt)
        if settings_popup and settings_popup.active:
            settings_popup.update(dt)

        grain.update(dt)
        ui.update(dt)

        # Drawing
        ui.draw(SCREEN)

        # Calculate Grain Alpha based on transition
        grain_alpha = 1.0
        configure_screen = ui.screens.get("CONFIGURE")

        if ui.is_transitioning:
            # If going TO Configure -> Fade Out
            if ui.next_screen == configure_screen:
                grain_alpha = 1.0 - ui.transition_progress
            # If coming FROM Configure -> Fade In
            elif ui.active == configure_screen:
                grain_alpha = ui.transition_progress
        else:
            # Static state
            if ui.active == configure_screen:
                grain_alpha = 0.0

        # Draw Grain if visible
        if grain_alpha > 0:
            grain.draw(SCREEN, alpha_mult=grain_alpha)

        # Draw global settings on top of everything
        if global_settings_popup and global_settings_popup.active:
            global_settings_popup.draw(SCREEN)
        if settings_popup and settings_popup.active:
            settings_popup.draw(SCREEN)

        pygame.display.flip()
