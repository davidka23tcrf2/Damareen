import pygame
import os

ASSETS_DIR = os.path.dirname(__file__)  # the folder containing your assets

def load_asset(name):
    """
    Load any asset from the assets folder by just providing the filename.
    """
    path = os.path.join(ASSETS_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Asset '{name}' not found in {ASSETS_DIR}")
    return pygame.image.load(path).convert_alpha()
