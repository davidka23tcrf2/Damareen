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
TITLE_FONT = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 64)  # Bigger for WIN/LOSE

# Layout Constants
DECK_PLAYER_POS = (150, 360)
DECK_DUNGEON_POS = (1130, 360)
CENTER_PLAYER_POS = (540, 360)
CENTER_DUNGEON_POS = (740, 360)

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
        self.y -= 30 * dt # Float up
        
    def draw(self, surf):
        if self.timer >= self.duration: return
        alpha = max(0, 255 * (1 - self.timer / self.duration))
        
        txt_surf = DMG_FONT.render(self.text, True, self.color)
        txt_surf.set_alpha(int(alpha))
        surf.blit(txt_surf, (self.x - txt_surf.get_width()//2, self.y))

class ArenaScreen:
    def __init__(self, goto_shop, goto_menu, goto_start):
        self.goto_shop = goto_shop
        self.goto_menu = goto_menu
        self.goto_start = goto_start
        self.elements = []
        
        # Red vignette and particles
        self.particles = ParticleManager(mode="blood")
        self.vignette = create_red_vignette()
        
        # Load element icons
        self.element_icons = {
            "fold": load_asset("dirt.png", "elements"),
            "viz": load_asset("water.png", "elements"),
            "levego": load_asset("air.png", "elements"),
            "tuz": load_asset("fire.png", "elements")
        }
        # Scale icons to 48x48
        for key in self.element_icons:
            self.element_icons[key] = pygame.transform.scale(self.element_icons[key], (48, 48))
        
        # Combat State
        self.state = "START" # START, FIGHT, WIN, LOSE
        self.turn = "DUNGEON" # DUNGEON or PLAYER
        
        # Animation State
        self.anim_phase = "ENTER" # ENTER, IDLE, LUNGE, IMPACT, RETURN, DEATH
        self.anim_timer = 0
        
        # Current visual positions of the active cards
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
        
        # UI Elements
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

    def setup_combat(self):
        # Clear previous state
        self.logs = []
        self.floating_texts = []
        
        # Reset all cards HP
        for card in inventory.PLAYERDECK:
            card.reset()
            
        # Get current dungeon
        if inventory.ENEMIES and inventory.SELECTED_DUNGEON_INDEX < len(inventory.ENEMIES):
            self.dungeon = inventory.ENEMIES[inventory.SELECTED_DUNGEON_INDEX]
            self.dungeon.reset()
        else:
            self.dungeon = None
            self.state = "WIN" # Fallback if no dungeon
            return

        self.player_card_idx = 0
        self.dungeon_card_idx = 0
        
        self.update_current_cards()
        self.log("Harc kezdodik!")
        self.state = "FIGHT"
        self.turn = "DUNGEON"
        
        # Start with ENTER animation
        self.anim_phase = "ENTER"
        self.anim_timer = 0
        
        # Start positions at decks
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

    def handle_event(self, e):
        if self.state in ["WIN", "LOSE"]:
            self.next_btn.handle_event(e)
        
    def update(self, dt):
        self.particles.update(dt)
        
        # Update floating texts
        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.timer < ft.duration]
        
        if self.state == "FIGHT":
            self.update_combat_logic(dt)
                
        elif self.state in ["WIN", "LOSE"]:
            self.next_btn.update(dt)

    def update_combat_logic(self, dt):
        self.anim_timer += dt
        # print(f"State: {self.anim_phase}, Timer: {self.anim_timer:.2f}")
        
        if self.anim_phase == "ENTER":
            # Move cards from Deck to Center
            duration = 0.4 # Even faster entry
            t = min(1.0, self.anim_timer / duration)
            
            # Ease out cubic
            t = 1 - (1 - t) ** 3
            
            # Only animate cards that are actually at the deck position
            # Player: Deck -> Center (only if starting from deck)
            if abs(self.player_card_pos[0] - DECK_PLAYER_POS[0]) > 5:  # Already at center
                # Keep at center
                self.player_card_pos = list(CENTER_PLAYER_POS)
            else:
                # Animate from deck to center
                self.player_card_pos[0] = DECK_PLAYER_POS[0] + (CENTER_PLAYER_POS[0] - DECK_PLAYER_POS[0]) * t
                self.player_card_pos[1] = DECK_PLAYER_POS[1] + (CENTER_PLAYER_POS[1] - DECK_PLAYER_POS[1]) * t
            
            # Dungeon: Deck -> Center (only if starting from deck)
            if abs(self.dungeon_card_pos[0] - DECK_DUNGEON_POS[0]) > 5:  # Already at center
                # Keep at center
                self.dungeon_card_pos = list(CENTER_DUNGEON_POS)
            else:
                # Animate from deck to center
                self.dungeon_card_pos[0] = DECK_DUNGEON_POS[0] + (CENTER_DUNGEON_POS[0] - DECK_DUNGEON_POS[0]) * t
                self.dungeon_card_pos[1] = DECK_DUNGEON_POS[1] + (CENTER_DUNGEON_POS[1] - DECK_DUNGEON_POS[1]) * t
            
            if self.anim_timer >= duration:
                # Ensure both are at center
                self.player_card_pos = list(CENTER_PLAYER_POS)
                self.dungeon_card_pos = list(CENTER_DUNGEON_POS)
                self.anim_phase = "IDLE"
                self.anim_timer = 0
                
        elif self.anim_phase == "IDLE":
            if self.anim_timer >= 0.4: # Wait before attack
                self.start_attack_anim()
                
        elif self.anim_phase == "LUNGE":
            # Move attacker towards defender
            t = min(1.0, self.anim_timer / 0.2) # Even faster lunge
            
            start = CENTER_DUNGEON_POS if self.turn == "DUNGEON" else CENTER_PLAYER_POS
            target = CENTER_PLAYER_POS if self.turn == "DUNGEON" else CENTER_DUNGEON_POS
            
            # Lunge 60% of the way
            mid_x = start[0] + (target[0] - start[0]) * 0.6
            
            curr_pos = self.dungeon_card_pos if self.turn == "DUNGEON" else self.player_card_pos
            curr_pos[0] = start[0] + (mid_x - start[0]) * t
            
            if t >= 1.0:
                self.execute_attack_hit()
                
        elif self.anim_phase == "IMPACT":
            if self.anim_timer >= 0.15: # Quick pause on impact
                self.anim_phase = "RETURN"
                self.anim_timer = 0
                 
        elif self.anim_phase == "RETURN":
            t = min(1.0, self.anim_timer / 0.2) # Even faster return
            
            start = CENTER_DUNGEON_POS if self.turn == "DUNGEON" else CENTER_PLAYER_POS
            target = CENTER_PLAYER_POS if self.turn == "DUNGEON" else CENTER_DUNGEON_POS
            mid_x = start[0] + (target[0] - start[0]) * 0.6
            
            curr_pos = self.dungeon_card_pos if self.turn == "DUNGEON" else self.player_card_pos
            curr_pos[0] = mid_x + (start[0] - mid_x) * t
            
            if t >= 1.0:
                # Reset positions exactly to center
                self.player_card_pos = list(CENTER_PLAYER_POS)
                self.dungeon_card_pos = list(CENTER_DUNGEON_POS)
                self.check_death_or_next_turn()
                
        elif self.anim_phase == "DEATH":
            if self.anim_timer >= 0.5: # Even faster death fade
                self.handle_death_completion()

    def start_attack_anim(self):
        if not self.current_player_card or not self.current_dungeon_card:
            self.check_win_condition()
            return
            
        self.anim_phase = "LUNGE"
        self.anim_timer = 0

    def execute_attack_hit(self):
        attacker = None
        defender = None
        
        if self.turn == "DUNGEON":
            attacker = self.current_dungeon_card
            defender = self.current_player_card
            attacker_name = "Kazamata"
            defender_name = "Jatekos"
        else:
            attacker = self.current_player_card
            defender = self.current_dungeon_card
            attacker_name = "Jatekos"
            defender_name = "Kazamata"
            
        # Calculate base damage with elemental multiplier
        multiplier = card_logic.get_type_multiplier(attacker.power, defender.power)
        damage = int(attacker.dmg * multiplier)
        
        # Apply armor defense if player is defending
        if self.turn == "DUNGEON":  # Dungeon attacking player
            armor_defense = 0
            # Check equipped armor for defense against attacker's element
            for item in inventory.EquipedItems:
                if hasattr(item, 'type') and hasattr(item, 'defense'):
                    # If armor type matches attacker's power, apply defense
                    if item.type == attacker.power:
                        armor_defense += item.defense
            
            # Reduce damage by armor defense percentage
            if armor_defense > 0:
                damage = int(damage * (1 - armor_defense / 100))
        
        # Apply damage and clamp HP to minimum 0
        defender.hp -= damage
        defender.hp = max(0, defender.hp)
        
        # Floating Text
        target_pos = CENTER_PLAYER_POS if self.turn == "DUNGEON" else CENTER_DUNGEON_POS
        color = theme.DANGER if multiplier > 1 else (theme.WARNING if multiplier < 1 else theme.TEXT_WHITE)
        self.floating_texts.append(FloatingText(target_pos[0], target_pos[1] - 100, f"-{damage}", color))
        
        self.log(f"{attacker_name} tamad: {damage} ({multiplier}x)")
        
        self.anim_phase = "IMPACT"
        self.anim_timer = 0

    def check_death_or_next_turn(self):
        # Check if anyone died
        dead_card = None
        if self.current_player_card and self.current_player_card.hp <= 0:
            dead_card = self.current_player_card
        elif self.current_dungeon_card and self.current_dungeon_card.hp <= 0:
            dead_card = self.current_dungeon_card
            
        if dead_card:
            self.log(f"{dead_card.name} elesett!")
            self.anim_phase = "DEATH"
            self.anim_timer = 0
        else:
            # Next turn
            self.turn = "PLAYER" if self.turn == "DUNGEON" else "DUNGEON"
            self.anim_phase = "IDLE"
            self.anim_timer = 0

    def handle_death_completion(self):
        # Determine who died and update index
        player_died = self.current_player_card and self.current_player_card.hp <= 0
        dungeon_died = self.current_dungeon_card and self.current_dungeon_card.hp <= 0
        
        if player_died:
            self.player_card_idx += 1
            # Reset player pos to deck for new card entry
            self.player_card_pos = list(DECK_PLAYER_POS)
            self.turn = "DUNGEON"
        
        if dungeon_died:
            self.dungeon_card_idx += 1
            # Reset dungeon pos to deck for new card entry
            self.dungeon_card_pos = list(DECK_DUNGEON_POS)
            self.turn = "DUNGEON"
            
        self.update_current_cards()
        self.check_win_condition()
        
        if self.state == "FIGHT":
            # Start ENTER animation for the new card(s)
            self.anim_phase = "ENTER"
            self.anim_timer = 0

    def check_win_condition(self):
        if not self.current_player_card:
            self.state = "LOSE"
            self.log("VESZTEL!")
            save.delete_current_save()
        elif not self.current_dungeon_card:
            self.state = "WIN"
            self.log("NYERTEL!")
            self.handle_rewards()

    def handle_rewards(self):
        if not self.dungeon: return
        
        reward_type = self.dungeon.reward
        dungeon_type = self.dungeon.type
        
        scales = 0
        if dungeon_type == "nagy": scales = 3
        elif dungeon_type == "kis": scales = 2
        else: scales = 1
            
        inventory.COINS += scales
        self.log(f"Kaptal {scales} pikkelyt!")
        
        winning_card = None
        if self.current_player_card:
            winning_card = self.current_player_card
        elif self.player_card_idx > 0:
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
                self.log("Minden kartyat megszereztel!")
                
        elif dungeon_type == "kis" or dungeon_type == "egyszeru":
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
        # Reset all card HP after battle
        for card in inventory.PLAYERDECK:
            card.reset()
        if self.dungeon:
            self.dungeon.reset()
        
        if self.state == "WIN":
            self.goto_menu()
        elif self.state == "LOSE":
            # Save is already deleted in check_win_condition
            self.goto_start()

    def draw(self, surf):
        surf.fill((0, 0, 0))
        self.particles.draw(surf)
        surf.blit(self.vignette, (0, 0))
        
        # Draw Deck Stacks (Visual only)
        # Player Deck (Left)
        self.draw_deck_stack(surf, DECK_PLAYER_POS[0], DECK_PLAYER_POS[1], len(inventory.PLAYERDECK) - self.player_card_idx - 1)
        
        # Dungeon Deck (Right)
        if self.dungeon:
            self.draw_deck_stack(surf, DECK_DUNGEON_POS[0], DECK_DUNGEON_POS[1], len(self.dungeon.deck) - self.dungeon_card_idx - 1)
        
        # Draw Active Cards
        # Draw defender first, then attacker on top
        if self.anim_phase in ["LUNGE", "IMPACT", "RETURN"]:
            # During attack animations, draw defender first
            if self.turn == "DUNGEON":
                # Dungeon attacking, draw player first (defender)
                if self.current_player_card:
                    alpha = 255
                    if self.anim_phase == "DEATH" and self.current_player_card.hp <= 0:
                        alpha = int(255 * (1.0 - min(1.0, self.anim_timer)))
                    self.draw_card(surf, self.current_player_card, self.player_card_pos[0], self.player_card_pos[1], "Jatekos", alpha)
                
                if self.current_dungeon_card:
                    alpha = 255
                    if self.anim_phase == "DEATH" and self.current_dungeon_card.hp <= 0:
                        alpha = int(255 * (1.0 - min(1.0, self.anim_timer)))
                    self.draw_card(surf, self.current_dungeon_card, self.dungeon_card_pos[0], self.dungeon_card_pos[1], "Kazamata", alpha)
            else:
                # Player attacking, draw dungeon first (defender)
                if self.current_dungeon_card:
                    alpha = 255
                    if self.anim_phase == "DEATH" and self.current_dungeon_card.hp <= 0:
                        alpha = int(255 * (1.0 - min(1.0, self.anim_timer)))
                    self.draw_card(surf, self.current_dungeon_card, self.dungeon_card_pos[0], self.dungeon_card_pos[1], "Kazamata", alpha)
                
                if self.current_player_card:
                    alpha = 255
                    if self.anim_phase == "DEATH" and self.current_player_card.hp <= 0:
                        alpha = int(255 * (1.0 - min(1.0, self.anim_timer)))
                    self.draw_card(surf, self.current_player_card, self.player_card_pos[0], self.player_card_pos[1], "Jatekos", alpha)
        else:
            # Normal order for other phases
            if self.current_player_card:
                alpha = 255
                if self.anim_phase == "DEATH" and self.current_player_card.hp <= 0:
                    alpha = int(255 * (1.0 - min(1.0, self.anim_timer)))
                self.draw_card(surf, self.current_player_card, self.player_card_pos[0], self.player_card_pos[1], "Jatekos", alpha)
            
            if self.current_dungeon_card:
                alpha = 255
                if self.anim_phase == "DEATH" and self.current_dungeon_card.hp <= 0:
                    alpha = int(255 * (1.0 - min(1.0, self.anim_timer)))
                self.draw_card(surf, self.current_dungeon_card, self.dungeon_card_pos[0], self.dungeon_card_pos[1], "Kazamata", alpha)
            
        # Draw Floating Texts
        for ft in self.floating_texts:
            ft.draw(surf)
            
        # Draw Logs
        y = 50
        for log in self.logs:
            text = SMALL_FONT.render(log, True, theme.TEXT_WHITE)
            surf.blit(text, (1280//2 - text.get_width()//2, y))
            y += 30
            
        # Draw State Message (now way bigger)
        if self.state == "WIN":
            text = TITLE_FONT.render("GYOZELEM!", True, theme.SUCCESS)
            surf.blit(text, (1280//2 - text.get_width()//2, 260))
            self.next_btn.draw(surf)
        elif self.state == "LOSE":
            text = TITLE_FONT.render("VERSEG!", True, theme.DANGER)
            surf.blit(text, (1280//2 - text.get_width()//2, 260))
            self.next_btn.draw(surf)

    def draw_deck_stack(self, surf, x, y, count):
        if count <= 0: return
        # Draw up to 3 cards
        for i in range(min(count, 3), 0, -1):
            offset = i * 5
            rect = pygame.Rect(x - 100 - offset, y - 150 - offset, 200, 300)
            pygame.draw.rect(surf, (30, 30, 40), rect, border_radius=12)
            pygame.draw.rect(surf, theme.BORDER_COLOR, rect, 2, border_radius=12)

    def draw_card(self, surf, card, x, y, owner, alpha=255):
        w, h = 200, 300
        rect = pygame.Rect(x - w//2, y - h//2, w, h)
        
        card_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        color = theme.BG_PANEL
        if card.power == "tuz": color = (100, 40, 40)
        elif card.power == "viz": color = (40, 40, 100)
        elif card.power == "fold": color = (60, 100, 40)
        elif card.power == "levego": color = (150, 150, 150)
        
        pygame.draw.rect(card_surf, color, (0, 0, w, h), border_radius=12)
        pygame.draw.rect(card_surf, theme.BORDER_COLOR, (0, 0, w, h), 2, border_radius=12)
        
        name_txt = BP.render(card.name, True, theme.TEXT_WHITE)
        card_surf.blit(name_txt, (w//2 - name_txt.get_width()//2, 20))
        
        stats_txt = SMALL_FONT.render(f"DMG: {card.dmg}", True, theme.TEXT_WHITE)
        card_surf.blit(stats_txt, (w//2 - stats_txt.get_width()//2, h - 110))
        
        hp_txt = SMALL_FONT.render(f"HP: {card.hp}/{card.basehp}", True, theme.TEXT_WHITE)
        card_surf.blit(hp_txt, (w//2 - hp_txt.get_width()//2, h - 80))
        
        # Element icon instead of text
        if card.power in self.element_icons:
            icon = self.element_icons[card.power]
            icon_rect = icon.get_rect(center=(w//2, h - 30))
            card_surf.blit(icon, icon_rect)
        
        own_txt = SMALL_FONT.render(owner, True, theme.TEXT_GREY)
        card_surf.blit(own_txt, (w//2 - own_txt.get_width()//2, 5))
        
        if alpha < 255:
            card_surf.set_alpha(alpha)
            
        surf.blit(card_surf, rect.topleft)
