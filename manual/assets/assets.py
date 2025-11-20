import pygame
import os

ASSETS_DIR = os.path.dirname(__file__)  # folder containing this file

def load_asset(name, subfolder=""):
    path = os.path.join(ASSETS_DIR, subfolder, name) if subfolder else os.path.join(ASSETS_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Asset '{name}' not found in {path}")
    return pygame.image.load(path).convert_alpha()
