import pygame, sys, json
from manual.ui.ui_manager import UIStateManager
from manual.screens.shop import ShopScreen
from manual.screens.arena import ArenaScreen
from manual.screens.menu import MenuScreen

pygame.init()
SCREEN = pygame.display.set_mode((1280,720))
CLOCK = pygame.time.Clock()

def load_state():
    try:
        with open("save.json","r") as f:
            return json.load(f)
    except:
        return {"currency":100,"inventory":[]}

state = load_state()
ui = UIStateManager()

def goto_shop(): ui.set("SHOP")
def goto_arena(): ui.set("ARENA")
def goto_menu(): ui.set("MENU")

ui.add("SHOP", ShopScreen(goto_arena, state))
ui.add("ARENA", ArenaScreen(goto_shop, state))
ui.add("MENU", MenuScreen(goto_arena, goto_shop))
ui.set("MENU")

def ml():
    while True:
        dt = CLOCK.tick(60)/1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        ui.update(dt)
        SCREEN.fill((30,30,30))
        ui.draw(SCREEN)
        pygame.display.flip()
