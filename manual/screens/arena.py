import pygame
import random
import os
import math

from ..ui.button import Button
from manual.assets.assets import ASSETS_DIR, load_asset
from manual.ui.particles import ParticleManager
from manual.ui.vignette import create_red_vignette
from manual.inventory import inventory, objects
from auto import card as card_logic
from manual.saving import save
from manual.ui import theme

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 24)
SMALL_FONT = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 18)
DMG_FONT = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 32)
TITLE_FONT = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 64)

DECK_PLAYER_POS = (150, 360)
DECK_DUNGEON_POS = (1130, 360)
CENTER_PLAYER_POS = (540, 360)
CENTER_DUNGEON_POS = (740, 360)

# Make cards WAY larger
CARD_W = 260
CARD_H = 360


class FloatingText:
    def __init__(self, x, y, text, color, duration=1.0):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.duration = duration
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        self.y -= 30 * dt

    def draw(self, surf):
        if self.timer >= self.duration:
            return
        alpha = max(0, 255 * (1 - self.timer / self.duration))
        txt_surf = DMG_FONT.render(self.text, True, self.color)
        txt_surf.set_alpha(int(alpha))
        surf.blit(txt_surf, (self.x - txt_surf.get_width() // 2, self.y))


class ArenaScreen:
    def __init__(self, goto_shop, goto_menu, goto_start):
        self.goto_shop = goto_shop
        self.goto_menu = goto_menu
        self.goto_start = goto_start
        self.elements = []

        self.particles = ParticleManager(mode="blood")
        self.vignette = create_red_vignette()

        self.element_icons = {
            "fold": load_asset("dirt.png", "elements"),
            "viz": load_asset("water.png", "elements"),
            "levego": load_asset("air.png", "elements"),
            "tuz": load_asset("fire.png", "elements")
        }
        # Make icons larger
        for key in self.element_icons:
            self.element_icons[key] = pygame.transform.scale(self.element_icons[key], (96, 96))

        self.state = "START"      # START, FIGHT, WIN, LOSE
        self.turn = "DUNGEON"     # DUNGEON or PLAYER

        self.anim_phase = "ENTER"  # ENTER, IDLE, LUNGE, IMPACT, RETURN, DEATH
        self.anim_timer = 0

        self.player_card_pos = list(DECK_PLAYER_POS)
        self.dungeon_card_pos = list(DECK_DUNGEON_POS)
        self.floating_texts = []

        self.player_card_idx = 0
        self.dungeon_card_idx = 0
        self.current_player_card = None
        self.current_dungeon_card = None

        self.logs = []
        self.max_logs = 5

        self.setup_combat()

        self.next_btn = Button(
            (1280 - 250, 720 - 100, 200, 60),
            self.finish_combat,
            None,
            text="Tovabb",
            font=BP,
            text_color=theme.TEXT_WHITE,
            bg_color=theme.PRIMARY,
            hover_bg_color=theme.PRIMARY_HOVER
        )

        try:
            self.hit_sound = pygame.mixer.Sound(
                os.path.join(ASSETS_DIR, "sounds", "hit.wav")
            )
            self.hit_sound.set_volume(0.5)
        except Exception as e:
            print(f"Failed to load hit sound: {e}")
            self.hit_sound = None

    # -------------------------------------------------------------------------
    # COMBAT SETUP & LOGIC
    # -------------------------------------------------------------------------
    def setup_combat(self):
        self.logs = []
        self.floating_texts = []

        # Reset player cards HP
        for card in inventory.PLAYERDECK:
            card.reset()

        # Select dungeon
        if inventory.ENEMIES and 0 <= inventory.SELECTED_DUNGEON_INDEX < len(inventory.ENEMIES):
            self.dungeon = inventory.ENEMIES[inventory.SELECTED_DUNGEON_INDEX]
            # Ensure Enemy has a reset() method
            if hasattr(self.dungeon, "reset"):
                self.dungeon.reset()
        else:
            self.dungeon = None
            self.state = "WIN"
            return

        self.player_card_idx = 0
        self.dungeon_card_idx = 0
        self.update_current_cards()
        self.log("Harc kezdodik!")
        self.state = "FIGHT"
        self.turn = "DUNGEON"
        self.anim_phase = "ENTER"
        self.anim_timer = 0
        self.player_card_pos = list(DECK_PLAYER_POS)
        self.dungeon_card_pos = list(DECK_DUNGEON_POS)

    def update_current_cards(self):
        if self.player_card_idx < len(inventory.PLAYERDECK):
            self.current_player_card = inventory.PLAYERDECK[self.player_card_idx]
        else:
            self.current_player_card = None

        if self.dungeon and self.dungeon_card_idx < len(self.dungeon.deck):
            self.current_dungeon_card = self.dungeon.deck[self.dungeon_card_idx]
        else:
            self.current_dungeon_card = None

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    # -------------------------------------------------------------------------
    # INPUT / UPDATE
    # -------------------------------------------------------------------------
    def handle_event(self, e):
        if self.state in ["WIN", "LOSE"]:
            self.next_btn.handle_event(e)

    def update(self, dt):
        self.particles.update(dt)
        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.timer < ft.duration]

        if self.state == "FIGHT":
            self.update_combat_logic(dt)
        elif self.state in ["WIN", "LOSE"]:
            self.next_btn.update(dt)

    def update_combat_logic(self, dt):
        self.anim_timer += dt

        if self.anim_phase == "ENTER":
            duration = 0.4
            t = min(1.0, self.anim_timer / duration)
            t = 1 - (1 - t) ** 3

            # Animate player card from deck to center
            self.player_card_pos[0] = DECK_PLAYER_POS[0] + (CENTER_PLAYER_POS[0] - DECK_PLAYER_POS[0]) * t
            self.player_card_pos[1] = DECK_PLAYER_POS[1] + (CENTER_PLAYER_POS[1] - DECK_PLAYER_POS[1]) * t

            # Animate dungeon card from deck to center
            self.dungeon_card_pos[0] = DECK_DUNGEON_POS[0] + (CENTER_DUNGEON_POS[0] - DECK_DUNGEON_POS[0]) * t
            self.dungeon_card_pos[1] = DECK_DUNGEON_POS[1] + (CENTER_DUNGEON_POS[1] - DECK_DUNGEON_POS[1]) * t

            if self.anim_timer >= duration:
                self.player_card_pos = list(CENTER_PLAYER_POS)
                self.dungeon_card_pos = list(CENTER_DUNGEON_POS)
                self.anim_phase = "IDLE"
                self.anim_timer = 0

        elif self.anim_phase == "IDLE":
            if self.anim_timer >= 0.4:
                self.start_attack_anim()

        elif self.anim_phase == "LUNGE":
            t = min(1.0, self.anim_timer / 0.2)
            start = CENTER_DUNGEON_POS if self.turn == "DUNGEON" else CENTER_PLAYER_POS
            target = CENTER_PLAYER_POS if self.turn == "DUNGEON" else CENTER_DUNGEON_POS
            mid_x = start[0] + (target[0] - start[0]) * 0.6

            if self.turn == "DUNGEON":
                curr = self.dungeon_card_pos
            else:
                curr = self.player_card_pos

            curr[0] = start[0] + (mid_x - start[0]) * t

            if t >= 1.0:
                self.execute_attack_hit()

        elif self.anim_phase == "IMPACT":
            if self.anim_timer >= 0.15:
                self.anim_phase = "RETURN"
                self.anim_timer = 0

        elif self.anim_phase == "RETURN":
            t = min(1.0, self.anim_timer / 0.2)
            start = CENTER_DUNGEON_POS if self.turn == "DUNGEON" else CENTER_PLAYER_POS
            target = CENTER_PLAYER_POS if self.turn == "DUNGEON" else CENTER_DUNGEON_POS
            mid_x = start[0] + (target[0] - start[0]) * 0.6

            if self.turn == "DUNGEON":
                curr = self.dungeon_card_pos
            else:
                curr = self.player_card_pos

            curr[0] = mid_x + (start[0] - mid_x) * t

            if t >= 1.0:
                self.player_card_pos = list(CENTER_PLAYER_POS)
                self.dungeon_card_pos = list(CENTER_DUNGEON_POS)
                self.check_death_or_next_turn()

        elif self.anim_phase == "DEATH":
            if self.anim_timer >= 0.5:
                self.handle_death_completion()

    def start_attack_anim(self):
        if not self.current_player_card or not self.current_dungeon_card:
            self.check_win_condition()
            return
        self.anim_phase = "LUNGE"
        self.anim_timer = 0

    def execute_attack_hit(self):
        attacker = self.current_dungeon_card if self.turn == "DUNGEON" else self.current_player_card
        defender = self.current_player_card if self.turn == "DUNGEON" else self.current_dungeon_card
        attacker_name = "Kazamata" if self.turn == "DUNGEON" else "Jatekos"

        multiplier = card_logic.get_type_multiplier(attacker.power, defender.power)
        base_damage = attacker.dmg * multiplier
        difficulty = getattr(inventory, "DIFFICULTY", 0)

        rnd = random.random()
        if self.turn == "DUNGEON":
            damage = round(base_damage * (1 + rnd * difficulty / 10))
        else:
            damage = round(base_damage * (1 - rnd * difficulty / 20))

        # Apply armor defense if player defending
        if self.turn == "DUNGEON":
            armor_defense = 0
            for armor in inventory.EQUIPPED_ARMOR:
                if hasattr(armor, "type") and hasattr(armor, "defense"):
                    if armor.type == attacker.power:
                        armor_defense += armor.defense
            if armor_defense > 0:
                damage = int(damage * (1 - armor_defense / 100))

        # Ensure damage is at least 1
        damage = max(1, damage)

        defender.hp -= damage
        defender.hp = max(0, defender.hp)

        if self.hit_sound:
            self.hit_sound.play()

        target_pos = CENTER_PLAYER_POS if self.turn == "DUNGEON" else CENTER_DUNGEON_POS
        if multiplier > 1:
            color = theme.DANGER
        elif multiplier < 1:
            color = theme.WARNING
        else:
            color = theme.TEXT_WHITE

        self.floating_texts.append(
            FloatingText(target_pos[0], target_pos[1] - 140, f"-{damage}", color)
        )

        self.log(f"{attacker_name} tamad: {damage} ({multiplier}x)")
        self.anim_phase = "IMPACT"
        self.anim_timer = 0

    def check_death_or_next_turn(self):
        dead = None
        if self.current_player_card and self.current_player_card.hp <= 0:
            dead = self.current_player_card
        elif self.current_dungeon_card and self.current_dungeon_card.hp <= 0:
            dead = self.current_dungeon_card

        if dead:
            self.log(f"{dead.name} elesett!")
            self.anim_phase = "DEATH"
            self.anim_timer = 0
        else:
            self.turn = "PLAYER" if self.turn == "DUNGEON" else "DUNGEON"
            self.anim_phase = "IDLE"
            self.anim_timer = 0

    def handle_death_completion(self):
        player_died = self.current_player_card and self.current_player_card.hp <= 0
        dungeon_died = self.current_dungeon_card and self.current_dungeon_card.hp <= 0

        if player_died:
            self.player_card_idx += 1
            self.player_card_pos = list(DECK_PLAYER_POS)
            self.turn = "DUNGEON"

        if dungeon_died:
            self.dungeon_card_idx += 1
            self.dungeon_card_pos = list(DECK_DUNGEON_POS)
            self.turn = "DUNGEON"

        self.update_current_cards()
        self.check_win_condition()

        if self.state == "FIGHT":
            self.anim_phase = "ENTER"
            self.anim_timer = 0

    def check_win_condition(self):
        if not self.current_player_card:
            self.state = "LOSE"
            self.log("VESZTETTEL!")
            save.delete_current_save()
        elif not self.current_dungeon_card:
            self.state = "WIN"
            self.log("NYERTEL!")
            self.handle_rewards()

    def handle_rewards(self):
        if not self.dungeon:
            return

        reward_type = getattr(self.dungeon, "reward", None)
        dungeon_type = getattr(self.dungeon, "type", None)

        scales = 1
        if dungeon_type == "nagy":
            scales = 3
        elif dungeon_type == "kis":
            scales = 2

        inventory.COINS += scales
        self.log(f"Kaptal {scales} pikkelyt!")

        winning_card = self.current_player_card
        if winning_card is None and self.player_card_idx > 0:
            winning_card = inventory.PLAYERDECK[self.player_card_idx - 1]

        if dungeon_type == "nagy":
            new_card = None
            for card in inventory.GAMECARDS:
                if card not in inventory.PLAYERCARDS:
                    new_card = card
                    break
            if new_card:
                inventory.PLAYERCARDS.append(new_card)
                self.log(f"Uj kartya: {new_card.name}")
            else:
                self.log("Minden kartyat megszereztel mar!")
        elif dungeon_type in ("kis", "egyszeru"):
            if winning_card:
                if reward_type == "eletero":
                    winning_card.basehp += 2
                    winning_card.hp += 2
                    self.log(f"{winning_card.name} +2 Eletero")
                elif reward_type == "sebzes":
                    winning_card.dmg += 1
                    self.log(f"{winning_card.name} +1 Sebzes")
                else:
                    winning_card.basehp += 1
                    winning_card.hp += 1
                    self.log(f"{winning_card.name} +1 Eletero")

    def finish_combat(self):
        for card in inventory.PLAYERDECK:
            card.reset()
        if self.dungeon and hasattr(self.dungeon, "reset"):
            self.dungeon.reset()

        if self.state == "WIN":
            self.goto_menu()
        elif self.state == "LOSE":
            # Clear everything except PLAYERARMOR on loss
            inventory.EQUIPPED_ARMOR.clear()
            inventory.PLAYERARMOR.clear()
            inventory.COINS = 0
            inventory.PLAYERDECK.clear()
            inventory.PLAYERCARDS.clear()
            inventory.GAMECARDS.clear()
            inventory.ENEMIES.clear()
            inventory.DIFFICULTY = 0
            inventory.DIFFICULTY_SELECTED = False
            inventory.SHOP_ENABLED = False
            inventory.SHOP_NEEDS_REFRESH = True
            inventory.SELECTED_DUNGEON_INDEX = 0
            
            self.goto_start()

    # -------------------------------------------------------------------------
    # DRAW HELPERS
    # -------------------------------------------------------------------------
    def draw_card(self, surf, card, pos, is_player=True):
        """
        Draw a big card where:
        - name, element icon, and dmg/hp are all centered as a group
        - text and icon are bigger
        """
        if card is None:
            return

        x, y = int(pos[0]), int(pos[1])
        card_rect = pygame.Rect(0, 0, CARD_W, CARD_H)
        card_rect.center = (x, y)

        # Background & border
        if is_player:
            bg_col = (35, 45, 70)   # bluish
        else:
            bg_col = (70, 35, 35)   # reddish
        border_col = (255, 255, 255)

        pygame.draw.rect(surf, bg_col, card_rect, border_radius=16)
        pygame.draw.rect(surf, border_col, card_rect, 3, border_radius=16)

        # --- Build surfaces (bigger fonts) ---
        # Name
        name_surf = DMG_FONT.render(card.name, True, theme.TEXT_WHITE)

        # Power (icon or text)
        icon = self.element_icons.get(card.power)
        if icon is not None:
            power_surf = icon
        else:
            power_surf = DMG_FONT.render(str(card.power), True, theme.TEXT_WHITE)

        # DMG / HP
        dmg_hp_surf = DMG_FONT.render(f"{card.dmg}/{card.hp}", True, theme.TEXT_WHITE)

        # Put them into a list in order
        parts = [name_surf, power_surf, dmg_hp_surf]
        spacing = 12

        total_h = sum(p.get_height() for p in parts) + spacing * (len(parts) - 1)
        start_y = card_rect.centery - total_h // 2

        # Draw each centered horizontally, stacked vertically
        cy = start_y
        for p in parts:
            rect = p.get_rect()
            rect.centerx = card_rect.centerx
            rect.top = cy
            surf.blit(p, rect.topleft)
            cy += p.get_height() + spacing

    def draw_deck_back(self, surf, pos, count, is_player=True):
        """Draw stacked deck backs for remaining cards."""
        x, y = pos
        max_draw = min(count, 3)
        for i in range(max_draw):
            offset = i * 6
            # smaller than full card so they don't cover everything
            w = CARD_W * 0.5
            h = CARD_H * 0.5
            rect = pygame.Rect(0, 0, int(w), int(h))
            rect.center = (x + offset, y - offset)
            if is_player:
                col = (50, 70, 100)
            else:
                col = (100, 50, 50)
            pygame.draw.rect(surf, col, rect, border_radius=10)
            pygame.draw.rect(surf, (255, 255, 255), rect, 2, border_radius=10)

    def draw_logs(self, surf):
        """Draw combat log in the top-center area."""
        y = 40
        for log in self.logs:
            text = SMALL_FONT.render(log, True, theme.TEXT_WHITE)
            surf.blit(text, (1280 // 2 - text.get_width() // 2, y))
            y += 26

    def draw_turn_indicator(self, surf):
        """Simple label for whose turn it is."""
        if self.state != "FIGHT":
            return
        txt = f"KOR: {'Kazamata' if self.turn == 'DUNGEON' else 'Jatekos'}"
        text_surf = BP.render(txt, True, theme.TEXT_WHITE)
        surf.blit(text_surf, (1280 // 2 - text_surf.get_width() // 2, 8))

    # -------------------------------------------------------------------------
    # MAIN DRAW
    # -------------------------------------------------------------------------
    def draw(self, surf):
        # Background
        surf.fill((0, 0, 0))
        self.particles.draw(surf)
        surf.blit(self.vignette, (0, 0))

        # Draw deck backs (remaining cards)
        remaining_player = len(inventory.PLAYERDECK) - self.player_card_idx - (1 if self.current_player_card else 0)
        if remaining_player > 0:
            self.draw_deck_back(surf, DECK_PLAYER_POS, remaining_player, is_player=True)

        if self.dungeon:
            remaining_dungeon = len(self.dungeon.deck) - self.dungeon_card_idx - (1 if self.current_dungeon_card else 0)
        else:
            remaining_dungeon = 0

        if remaining_dungeon > 0:
            self.draw_deck_back(surf, DECK_DUNGEON_POS, remaining_dungeon, is_player=False)

        # Decide draw order so attacking card is on top
        player_first = True
        if (
            self.state == "FIGHT"
            and self.anim_phase in ("LUNGE", "IMPACT", "RETURN")
            and self.turn == "PLAYER"
        ):
            # Player is attacking -> draw dungeon first, then player on top
            player_first = False

        # Draw current cards in the middle (animated positions)
        if player_first:
            if self.current_player_card:
                self.draw_card(surf, self.current_player_card, self.player_card_pos, is_player=True)
            if self.current_dungeon_card:
                self.draw_card(surf, self.current_dungeon_card, self.dungeon_card_pos, is_player=False)
        else:
            if self.current_dungeon_card:
                self.draw_card(surf, self.current_dungeon_card, self.dungeon_card_pos, is_player=False)
            if self.current_player_card:
                self.draw_card(surf, self.current_player_card, self.player_card_pos, is_player=True)

        # Floating texts (damage numbers)
        for ft in self.floating_texts:
            ft.draw(surf)

        # Logs + turn indicator
        self.draw_turn_indicator(surf)
        self.draw_logs(surf)

        # WIN / LOSE overlays
        if self.state == "WIN":
            text = TITLE_FONT.render("GYOZELEM!", True, theme.SUCCESS)
            surf.blit(text, (1280 // 2 - text.get_width() // 2, 260))
            self.next_btn.draw(surf)
        elif self.state == "LOSE":
        
            text = TITLE_FONT.render("VERESEG!", True, theme.DANGER)
            surf.blit(text, (1280 // 2 - text.get_width() // 2, 260))
            self.next_btn.draw(surf)
