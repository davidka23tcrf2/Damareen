import pygame, os
from manual.ui.button import Button
from manual.ui.label import Label
from manual.ui.switch import Switch
from manual.assets.assets import load_asset, ASSETS_DIR
from manual.inventory import inventory

from manual.screens.configurepopups.newcard import CardPopup
from manual.screens.configurepopups.deletecard import CardDeletePopup  # <-- new import
from manual.screens.configurepopups.newleadercard import NewLeaderCardPopup

from manual.saving import save as saving  # module with save_game()

pygame.init()
BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "PublicPixel.ttf"), 20)
sf = "configure"


class CONFIGURE:
    def __init__(self, goto_start, goto_menu):
        self.elements = []
        self.goto_menu = goto_menu  # <-- store so we can jump to menu after saving

        back = load_asset("backbutton.png", sf)
        self.paper = load_asset("paper.png", sf)
        self.paper = pygame.transform.scale(self.paper, (1000, 720))
        self.bg = load_asset("bg.png", sf)

        self.elements.append(Label((250, 70, 0, 0), "Bolt:", font=BP))
        self.elements.append(Label((730, 70, 0, 0), "Kártyák kezelése", font=BP))

        self.switch = Switch((325, 50, 120, 50), callback=self.on_toggle, initial=False)

        # back button
        self.elements.append(Button((0, 0, 100, 100), goto_start, back))

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
            (975, 35, 75, 75),
            self.toggle_delete_popup,
            delete_icon,
            image_offset=(-5, -5),
        )
        self.elements.append(self.delete_card_btn)

        # New Leader Card (plus icon, same as new card but with label)
        # Label for "Új vezérkártya"
        # Aligned with "Kártyák kezelése" at x=730, but lower down
        # User requested "more right" -> let's try 850
        self.elements.append(Label((710, 200, 0, 0), "Új vezérkártya", font=BP))
        
        self.new_leader_btn = Button(
            (870, 170, 60, 60), # Next to the label (label ~200px wide? 680+200=880 -> 900 seems okay)
            self.toggle_leader_popup,
            new_icon, # reusing the same new icon
            image_offset=(-20, -18), # Adjust offset for smaller button if needed, or keep same
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
            border_radius=18
        )
        # black outline
        pygame.draw.rect(
            save_load_img,
            (0, 0, 0),
            save_load_img.get_rect(),
            width=3,
            border_radius=18
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
            border_radius=18
        )
        pygame.draw.rect(
            save_img,
            (0, 0, 0),
            save_img.get_rect(),
            width=3,
            border_radius=18
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

        # No active popup -> update normal UI
        for el in self.elements:
            el.update(dt)
        self.switch.update(dt)

    # ---------- DRAW ----------

    def draw(self, surf):
        surf.blit(self.bg, (0, 0))
        surf.blit(self.paper, (140, 0))

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
