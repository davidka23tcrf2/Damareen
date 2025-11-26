import pygame, os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.ui.switch import Switch
from manual.ui.text_entry import TextEntry
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory import inventory

from manual.screens.configurepopups.newcard import CardPopup
from manual.screens.configurepopups.deletecard import CardDeletePopup  # <-- new import
from manual.screens.configurepopups.newleadercard import NewLeaderCardPopup
from manual.screens.configurepopups.collectionpopup import CollectionPopup
from manual.screens.configurepopups.newdungeon import NewDungeonPopup
from manual.screens.configurepopups.deletedungeon import DeleteDungeonPopup

from manual.saving import save as saving  # module with save_game()

pygame.init()
pygame.mixer.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 24)
BP_SMALL = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 16)
BP30 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 30)
BP40 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 40)
BP50 = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "BoldPixels.ttf"), 50)
sf = "configure"
sf = "configure"


class CONFIGURE:
    def __init__(self, goto_start, goto_menu):
        self.elements = []
        self.goto_menu = goto_menu  # <-- store so we can jump to menu after saving
        
        # Load and prepare elevator music
        music_path = os.path.join(ASSETS_DIR, "sounds", "Elevator-music.mp3")
        try:
            pygame.mixer.music.load(music_path)
            self.music_loaded = True
        except Exception as e:
            print(f"Failed to load elevator music: {e}")
            self.music_loaded = False

        self.bg = load_asset("bg.png", sf)
        self.bg = pygame.transform.scale(self.bg, (1280, 720))

        self.elements.append(Label((260, 155, 0, 0), "Bolt:", font=BP40, color=(255, 255, 255)))
        self.elements.append(Label((700, 70, 0, 0), "Kártyák kezelése", font=BP50, color=(255, 255, 255)))

        self.switch = Switch((325, 130, 120, 50), callback=self.on_toggle, initial=False)

        self.switch = Switch((325, 130, 120, 50), callback=self.on_toggle, initial=False)

        # back button
        back_img = load_asset("backbutton.png", sf)
        self.back_btn = Button(
            (30, 30, 98, 98),
            goto_start,
            back_img
        )
        self.elements.append(self.back_btn)

        # --- KÁRTYÁK KEZELÉSE BUTTONS ---

        # New card (plus icon)
        new_icon = load_asset("new.png", sf)
        self.new_card_btn = Button(
            (900, 35, 75, 75),
            self.toggle_new_popup,
            new_icon,
            image_offset=(-13, -11),
        )
        self.elements.append(self.new_card_btn)

        # Delete card (trash icon)
        delete_icon = load_asset("delete.png", sf)
        delete_icon = pygame.transform.smoothscale(delete_icon, (85, 85))
        self.delete_card_btn = Button(
            (975, 55, 75, 30),
            self.toggle_delete_popup,
            delete_icon,
            image_offset=(-5, -26),
        )
        self.elements.append(self.delete_card_btn)

        # New Leader Card (plus icon, same as new card but with label)
        # Label for "Új vezérkártya"
        # Aligned with "Kártyák kezelése" at x=730, but lower down
        # User requested "more right" -> let's try 850
        self.elements.append(Label((720, 210, 0, 0), "Új vezérkártya", font=BP40, color=(255, 255, 255)))
        
        self.new_leader_btn = Button(
            (870, 170, 75, 75), # Next to the label (label ~200px wide? 680+200=880 -> 900 seems okay)
            self.toggle_leader_popup,
            new_icon, # reusing the same new icon
            image_offset=(-13, -11), # Adjust offset for smaller button if needed, or keep same
        )
        self.elements.append(self.new_leader_btn)

        # --- SAVE & "LOAD" button (bottom) ---
        # (now: save + go to menu, no actual load, no clearing inv)
        save_load_w, save_load_h = 350, 80
        save_load_x = 600
        save_load_y = 630

        save_load_img = pygame.Surface((save_load_w, save_load_h), pygame.SRCALPHA)
        # blue background
        pygame.draw.rect(
            save_load_img,
            (80, 140, 255),
            save_load_img.get_rect(),
            border_radius=0
        )
        # black outline
        pygame.draw.rect(
            save_load_img,
            (0, 0, 0),
            save_load_img.get_rect(),
            width=3,
            border_radius=0
        )
        txt = BP40.render("Mentés&Betöltés", True, (255, 255, 255))
        txt_rect = txt.get_rect(center=(save_load_w // 2, save_load_h // 2))
        save_load_img.blit(txt, txt_rect)

        self.save_load_btn = Button(
            (save_load_x, save_load_y, save_load_w, save_load_h),
            self.on_save_and_load,
            save_load_img,
        )
        self.elements.append(self.save_load_btn)

        # --- SAVE ONLY button (bottom, left of it) ---
        save_w, save_h = 220, 80
        save_x = 360
        save_y = 630

        save_img = pygame.Surface((save_w, save_h), pygame.SRCALPHA)
        pygame.draw.rect(
            save_img,
            (80, 140, 255),      # same blue
            save_img.get_rect(),
            border_radius=0
        )
        pygame.draw.rect(
            save_img,
            (0, 0, 0),
            save_img.get_rect(),
            width=3,
            border_radius=0
        )
        txt2 = BP40.render("Mentés", True, (255, 255, 255))
        txt2_rect = txt2.get_rect(center=(save_w // 2, save_h // 2))
        save_img.blit(txt2, txt2_rect)

        self.save_btn = Button(
            (save_x, save_y, save_w, save_h),
            self.on_save_only,
            save_img,
        )
        self.save_btn = Button(
            (save_x, save_y, save_w, save_h),
            self.on_save_only,
            save_img,
        )
        self.elements.append(self.save_btn)

        # Save Name Input
        self.elements.append(Label((save_x + 50, save_y - 30, 0, 0), "Név:", font=BP40, color=(255, 255, 255)))
        self.save_name_input = TextEntry(
            (save_x + 100, save_y - 50, save_load_w + (save_load_x - save_x) - 100, 40),
            font=BP40,
            bg_color=(50, 50, 50),
            color=(255, 255, 255)
        )
        self.elements.append(self.save_name_input)

        # Popups
        self.card_popup = None        # new-card popup
        self.delete_popup = None      # delete-card popup
        self.leader_popup = None      # new-leader-card popup

        # Timer for save message
        self.save_message_timer = 0
        self.saved_label = Label((360, 630, 220, 80), "Környezet elmentve!", font=BP30, color=(0, 255, 0))

        # --- COLLECTION CONFIGURATION ---
        # Gear icon
        gear_icon = load_asset("gear.png", sf)
        gear_icon = pygame.transform.smoothscale(gear_icon, (60, 60))
        
        # Label "Gyűjtemény konfigurálása"
        # Position: Let's put it below "Új vezérkártya" section.
        # "Új vezérkártya" is at y=200 (label) and y=170 (button).
        # Let's go down to y=300.
        self.elements.append(Label((650, 355, 0, 0), "Gyűjtemény konfigurálása", font=BP40, color=(255, 255, 255)))
        
        self.collection_btn = Button(
            (880, 320, 70, 70), # Right of the label
            self.toggle_collection_popup,
            gear_icon,
            image_offset=(5, 5)
        )
        self.elements.append(self.collection_btn)
        
        self.collection_popup = None

        # --- KAZAMATÁK KEZELÉSE ---
        # Label "Kazamaták kezelése"
        # Position: Below Collection section. Collection label at y=350.
        # Let's go down to y=450.
        self.elements.append(Label((600, 500, 0, 0), "Kazamaták kezelése", font=BP40, color=(255, 255, 255)))
        
        # New Dungeon (plus icon)
        # Reusing new_icon
        self.new_dungeon_btn = Button(
            (800, 465, 75, 75),
            self.toggle_new_dungeon_popup,
            new_icon,
            image_offset=(-13, -11),
        )
        self.elements.append(self.new_dungeon_btn)
        
        # Delete Dungeon (trash icon)
        # Reusing delete_icon
        self.delete_dungeon_btn = Button(
            (873, 490, 75, 30),
            self.toggle_delete_dungeon_popup,
            delete_icon,
            image_offset=(-5, -26),
        )
        self.elements.append(self.delete_dungeon_btn)
        
        self.new_dungeon_popup = None
        self.delete_dungeon_popup = None
        
        self.hidden_btn = None # Track which button is hidden by feedback label
    
    def start_music(self):
        """Start playing elevator music when entering the configure screen."""
        if self.music_loaded:
            try:
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                pygame.mixer.music.set_volume(0.3)  # Set volume to 30%
            except Exception as e:
                print(f"Failed to play elevator music: {e}")
    
    def stop_music(self):
        """Stop playing elevator music when leaving the configure screen."""
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Failed to stop elevator music: {e}")

    def on_toggle(self):
        inventory.SHOP_ENABLED = not inventory.SHOP_ENABLED

    # ---------- SAVE / LOAD HANDLERS ----------

    def on_save_and_load(self):
        """
        Save current state and go to the menu.
        No load, no clearing inventory.
        """
        name = self.save_name_input.get_text().strip()
        if not name:
            # Show error
            self.saved_label.set_text("Adj meg egy nevet!")
            self.saved_label.color = (255, 0, 0)
            self.saved_label.rect = self.save_load_btn.rect.copy() # Match button size/pos
            
            self.hidden_btn = self.save_load_btn
            if self.save_load_btn in self.elements:
                self.elements.remove(self.save_load_btn)
            if self.saved_label not in self.elements:
                self.elements.append(self.saved_label)
            
            self.save_message_timer = 1.5
            return

        try:
            saving.save_game(name)
        except Exception as e:
            print("Error in save:", e)

        if self.goto_menu:
            self.goto_menu()

    def on_save_only(self):
        """
        Save current state and then clear the inventory completely.
        (Only clear when saving-only, as requested.)
        """
        name = self.save_name_input.get_text().strip()
        if not name:
            # Show error
            self.saved_label.set_text("Adj meg egy nevet!")
            self.saved_label.color = (255, 0, 0)
            self.saved_label.rect = self.save_btn.rect.copy()
            
            self.hidden_btn = self.save_btn
            if self.save_btn in self.elements:
                self.elements.remove(self.save_btn)
            if self.saved_label not in self.elements:
                self.elements.append(self.saved_label)
            
            self.save_message_timer = 1.5
            return

        try:
            saving.save_game(name)
        except Exception as e:
            print("Error in save:", e)

        # clear inventory after saving
        inventory.GAMECARDS.clear()
        inventory.PLAYERCARDS.clear()
        inventory.ENEMIES.clear()

        # Success feedback
        self.saved_label.set_text("Környezet elmentve!")
        self.saved_label.color = (0, 255, 0)
        self.saved_label.rect = self.save_btn.rect.copy()

        self.hidden_btn = self.save_btn
        if self.save_btn in self.elements:
            self.elements.remove(self.save_btn)
        
        if self.saved_label not in self.elements:
            self.elements.append(self.saved_label)
        
        # Set timer to 1 second
        self.save_message_timer = 1.0

    # ---------- POPUP TOGGLES ----------

    def toggle_new_popup(self):
        # if delete popup is open, close it first
        if self.delete_popup and getattr(self.delete_popup, "active", False):
            self.delete_popup.close()
            return
        
        if self.leader_popup and getattr(self.leader_popup, "active", False):
            self.leader_popup.close()
            return

        if self.card_popup:
            if self.card_popup.is_closed():
                self.card_popup.reopen()
            else:
                self.card_popup.close()
        else:
            self.card_popup = CardPopup(close_callback=self.toggle_new_popup)

    def toggle_delete_popup(self):
        # if new popup is open, close it first
        if self.card_popup and getattr(self.card_popup, "active", False):
            self.card_popup.close()
            return

        if self.delete_popup:
            if self.delete_popup.is_closed():
                self.delete_popup.reopen()
            else:
                self.delete_popup.close()
        else:
            self.delete_popup = CardDeletePopup(close_callback=self.toggle_delete_popup)

    def toggle_leader_popup(self):
        # close others
        if self.card_popup and getattr(self.card_popup, "active", False):
            self.card_popup.close()
            return
        if self.delete_popup and getattr(self.delete_popup, "active", False):
            self.delete_popup.close()
            return

        if self.leader_popup:
            if self.leader_popup.is_closed():
                self.leader_popup.reopen()
            else:
                self.leader_popup.close()
        else:
            self.leader_popup = NewLeaderCardPopup(close_callback=self.toggle_leader_popup)

    def toggle_collection_popup(self):
        # close others
        if self.card_popup and getattr(self.card_popup, "active", False):
            self.card_popup.close()
        if self.delete_popup and getattr(self.delete_popup, "active", False):
            self.delete_popup.close()
        if self.leader_popup and getattr(self.leader_popup, "active", False):
            self.leader_popup.close()
            
        if self.collection_popup:
            if self.collection_popup.is_closed():
                self.collection_popup.reopen()
            else:
                self.collection_popup.close()
        else:
            self.collection_popup = CollectionPopup(close_callback=self.toggle_collection_popup)

    def toggle_new_dungeon_popup(self):
        # Close others
        self._close_all_popups_except("new_dungeon")
        
        if self.new_dungeon_popup:
            if self.new_dungeon_popup.is_closed():
                self.new_dungeon_popup.reopen()
            else:
                self.new_dungeon_popup.close()
        else:
            self.new_dungeon_popup = NewDungeonPopup(close_callback=self.toggle_new_dungeon_popup)

    def toggle_delete_dungeon_popup(self):
        # Close others
        self._close_all_popups_except("delete_dungeon")
        
        if self.delete_dungeon_popup:
            if self.delete_dungeon_popup.is_closed():
                self.delete_dungeon_popup.reopen()
            else:
                self.delete_dungeon_popup.close()
        else:
            self.delete_dungeon_popup = DeleteDungeonPopup(close_callback=self.toggle_delete_dungeon_popup)

    def _close_all_popups_except(self, keep):
        if keep != "card" and self.card_popup and getattr(self.card_popup, "active", False):
            self.card_popup.close()
        if keep != "delete_card" and self.delete_popup and getattr(self.delete_popup, "active", False):
            self.delete_popup.close()
        if keep != "leader" and self.leader_popup and getattr(self.leader_popup, "active", False):
            self.leader_popup.close()
        if keep != "collection" and self.collection_popup and getattr(self.collection_popup, "active", False):
            self.collection_popup.close()
        if keep != "new_dungeon" and self.new_dungeon_popup and getattr(self.new_dungeon_popup, "active", False):
            self.new_dungeon_popup.close()
        if keep != "delete_dungeon" and self.delete_dungeon_popup and getattr(self.delete_dungeon_popup, "active", False):
            self.delete_dungeon_popup.close()

    # ---------- EVENT HANDLING ----------

    def handle_event(self, e):
        # Popups are modal: if delete popup is active, it gets events first
        if self.delete_popup and getattr(self.delete_popup, "active", False):
            handled = self.delete_popup.handle_event(e)
            if handled:
                return

        # then new-card popup
        if self.card_popup and getattr(self.card_popup, "active", False):
            handled = self.card_popup.handle_event(e)
            if handled:
                return

        # then leader popup
        if self.leader_popup and getattr(self.leader_popup, "active", False):
            handled = self.leader_popup.handle_event(e)
            if handled:
                return

        # then collection popup
        if self.collection_popup and getattr(self.collection_popup, "active", False):
            handled = self.collection_popup.handle_event(e)
            if handled:
                return

        # then new dungeon popup
        if self.new_dungeon_popup and getattr(self.new_dungeon_popup, "active", False):
            handled = self.new_dungeon_popup.handle_event(e)
            if handled:
                return

        # then delete dungeon popup
        if self.delete_dungeon_popup and getattr(self.delete_dungeon_popup, "active", False):
            handled = self.delete_dungeon_popup.handle_event(e)
            if handled:
                return

        # Otherwise handle normal UI
        for el in self.elements:
            el.handle_event(e)
        self.switch.handle_event(e)

    # ---------- UPDATE ----------

    def update(self, dt):
        # Handle save message timer (always run, even with popups open)
        if self.save_message_timer > 0:
            self.save_message_timer -= dt
            if self.save_message_timer <= 0:
                self.save_message_timer = 0
                # Restore button
                if self.saved_label in self.elements:
                    self.elements.remove(self.saved_label)
                
                if self.hidden_btn and self.hidden_btn not in self.elements:
                    self.elements.append(self.hidden_btn)
                    self.hidden_btn = None
        
        # Prioritize popups; if any active, don't update base UI
        if self.delete_popup and getattr(self.delete_popup, "active", False):
            self.delete_popup.update(dt)
            if getattr(self.delete_popup, "closing", False) and self.delete_popup.is_closed():
                self.delete_popup = None
            return

        if self.card_popup and getattr(self.card_popup, "active", False):
            self.card_popup.update(dt)
            if getattr(self.card_popup, "closing", False) and self.card_popup.is_closed():
                self.card_popup = None
            return

        if self.leader_popup and getattr(self.leader_popup, "active", False):
            self.leader_popup.update(dt)
            if getattr(self.leader_popup, "closing", False) and self.leader_popup.is_closed():
                self.leader_popup = None
            return

        if self.collection_popup and getattr(self.collection_popup, "active", False):
            self.collection_popup.update(dt)
            if getattr(self.collection_popup, "closing", False) and self.collection_popup.is_closed():
                self.collection_popup = None
            return

        if self.new_dungeon_popup and getattr(self.new_dungeon_popup, "active", False):
            self.new_dungeon_popup.update(dt)
            if getattr(self.new_dungeon_popup, "closing", False) and self.new_dungeon_popup.is_closed():
                self.new_dungeon_popup = None
            return

        if self.delete_dungeon_popup and getattr(self.delete_dungeon_popup, "active", False):
            self.delete_dungeon_popup.update(dt)
            if getattr(self.delete_dungeon_popup, "closing", False) and self.delete_dungeon_popup.is_closed():
                self.delete_dungeon_popup = None
            return

        # No active popup -> update normal UI
        for el in self.elements:
            el.update(dt)
        self.switch.update(dt)
        self.save_name_input.update(dt)

    # ---------- DRAW ----------


    def draw(self, surf):
        surf.blit(self.bg, (0, 0))

        for el in self.elements:
            el.draw(surf)
        self.switch.draw(surf)
        self.save_name_input.draw(surf)

        # Draw popups on top of UI
        if self.card_popup:
            self.card_popup.draw(surf)
        if self.delete_popup:
            self.delete_popup.draw(surf)
        if self.leader_popup:
            self.leader_popup.draw(surf)
        if self.collection_popup:
            self.collection_popup.draw(surf)
        if self.new_dungeon_popup:
            self.new_dungeon_popup.draw(surf)
        if self.delete_dungeon_popup:
            self.delete_dungeon_popup.draw(surf)
