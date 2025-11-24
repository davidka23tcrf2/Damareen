import pygame, sys, json, os
from manual.screens.configure import CONFIGURE
from manual.screens.start import StartScreen
from manual.ui.ui_manager import UIStateManager
from manual.screens.shop import ShopScreen
from manual.screens.arena import ArenaScreen
from manual.screens.menu import MenuScreen
from manual.screens.gameloader import GameLoader
from manual.screens.inventory import InventoryScreen
from manual.screens.savedgames import SavedGamesScreen

pygame.init()
SCREEN_SIZE = (1280, 720)
SCREEN = pygame.display.set_mode(SCREEN_SIZE)
CLOCK = pygame.time.Clock()
pygame.display.set_caption("Damareen")
ui = UIStateManager(SCREEN_SIZE)

def goto_shop(): ui.switch_to("SHOP", duration=0.5)
def goto_arena(): ui.switch_to("ARENA", duration=0.5)
def goto_menu(): ui.switch_to("MENU", duration=0.5)
def goto_deckbuilder(): 
    ui.screens["DECKBUILDER"].refresh_list() # Refresh list when entering
    ui.switch_to("DECKBUILDER", duration=0.5)
def goto_gameloader(): 
    ui.screens["GAMELOADER"].reload_saves()
    ui.switch_to("GAMELOADER", duration=0.5)
def goto_configure(): ui.switch_to("CONFIGURE", duration=0.5)
def goto_start(): ui.switch_to("START", duration=0.5)
def goto_savedgames(): 
    ui.screens["SAVEDGAMES"].reload_saves()
    ui.switch_to("SAVEDGAMES", duration=0.5)

ui.add("SHOP", ShopScreen(goto_arena))
ui.add("ARENA", ArenaScreen(goto_shop))
ui.add("DECKBUILDER", InventoryScreen(goto_menu))
ui.add("MENU", MenuScreen(goto_arena, goto_shop, goto_deckbuilder))
ui.add("START", StartScreen(goto_configure, goto_gameloader, goto_savedgames))
ui.add("GAMELOADER", GameLoader(goto_menu, goto_start))
ui.add("CONFIGURE", CONFIGURE(goto_start, goto_menu))
ui.add("SAVEDGAMES", SavedGamesScreen(goto_start, goto_menu))

ui.set("START")

while True:
    dt = CLOCK.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        ui.handle_event(event)
    
    ui.update(dt)
    ui.draw(SCREEN)
    pygame.display.flip()
