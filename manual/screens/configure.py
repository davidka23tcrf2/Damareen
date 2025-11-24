import pygame, os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.ui.switch import Switch
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
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 20)
BP_SMALL = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 12)
sf = "configure"


class CONFIGURE:
    def __init__(self, goto_start, goto_menu):
        self.elements = []
        self.goto_menu = goto_menu  # <-- store so we can jump to menu after saving

        # Removed background for black background

        self.elements.append(Label((250, 150, 0, 0), "Bolt:", font=BP))
        self.elements.append(Label((730, 70, 0, 0), "Kártyák kezelése", font=BP))

        self.switch = Switch((325, 130, 120, 50), callback=self.on_toggle, initial=False)

        # back button
        back_btn = Button(
            (30, 30, 180, 70),
            goto_start,
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
        self.elements.append(Label((710, 200, 0, 0), "Új vezérkártya", font=BP))
        
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
        txt = BP.render("Mentés&Betöltés", True, (0, 0, 0))
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
        txt2 = BP.render("Mentés", True, (0, 0, 0))
        txt2_rect = txt2.get_rect(center=(save_w // 2, save_h // 2))
        save_img.blit(txt2, txt2_rect)

        self.save_btn = Button(
            (save_x, save_y, save_w, save_h),
            self.on_save_only,
            save_img,
        )
        self.elements.append(self.save_btn)

        # Popups
        self.card_popup = None        # new-card popup
        self.delete_popup = None      # delete-card popup
        self.leader_popup = None      # new-leader-card popup

        # Timer for save message
        self.save_message_timer = 0
        self.saved_label = Label((360, 630, 220, 80), "kornyezet elmentve!", font=BP_SMALL)

        # --- COLLECTION CONFIGURATION ---
        # Gear icon
        gear_icon = load_asset("gear.png", sf)
        gear_icon = pygame.transform.smoothscale(gear_icon, (60, 60))
        
        # Label "Gyűjtemény konfigurálása"
        # Position: Let's put it below "Új vezérkártya" section.
        # "Új vezérkártya" is at y=200 (label) and y=170 (button).
        # Let's go down to y=300.
        self.elements.append(Label((630, 350, 0, 0), "Gyűjtemény konfigurálása", font=BP))
        
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
        self.elements.append(Label((600, 500, 0, 0), "Kazamaták kezelése", font=BP))
        
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

    def on_toggle(self):
        inventory.SHOP_ENABLED = not inventory.SHOP_ENABLED

    # ---------- SAVE / LOAD HANDLERS ----------

    def on_save_and_load(self):
        """
        Save current state and go to the menu.
        No load, no clearing inventory.
        """
        try:
            saving.save_game()
        except Exception as e:
            print("Error in save:", e)

        if self.goto_menu:
            self.goto_menu()

    def on_save_only(self):
        """
        Save current state and then clear the inventory completely.
        (Only clear when saving-only, as requested.)
        """
        try:
            saving.save_game()
        except Exception as e:
            print("Error in save:", e)

        # clear inventory after saving
        inventory.GAMECARDS.clear()
        inventory.PLAYERCARDS.clear()
        inventory.ENEMIES.clear()

        # Remove the save button
        if self.save_btn in self.elements:
            self.elements.remove(self.save_btn)
        
        # Add the "kornyezet elmentve!" label
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

        # Handle save message timer
        if self.save_message_timer > 0:
            self.save_message_timer -= dt
            if self.save_message_timer <= 0:
                self.save_message_timer = 0
                # Restore button
                if self.saved_label in self.elements:
                    self.elements.remove(self.saved_label)
                if self.save_btn not in self.elements:
                    self.elements.append(self.save_btn)

    # ---------- DRAW ----------


    def draw(self, surf):
        surf.fill((0, 0, 0))  # Black background

        for el in self.elements:
            el.draw(surf)
        self.switch.draw(surf)

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
