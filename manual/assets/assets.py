import pygame
import os

ASSETS_DIR = os.path.dirname(__file__)  # folder containing this file


def load_asset(name, subfolder=""):
    # Build the full path correctly
    path = os.path.join(ASSETS_DIR, subfolder, name) if subfolder else os.path.join(ASSETS_DIR, name)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Asset '{name}' not found in: {path}")

    surf = pygame.image.load(path)

    # IMPORTANT:
    # Convert only if the display exists!
    if pygame.display.get_surface() is not None:
        try:
            return surf.convert_alpha()
        except pygame.error:
            return surf.convert()

    # No display yet → cannot convert → return raw surface
    return surf
