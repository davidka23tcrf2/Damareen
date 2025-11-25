import pygame
from ..ui.button import Button
from manual.assets.assets import ASSETS_DIR
from manual.ui.particles import ParticleManager
from manual.ui.vignette import create_red_vignette
import os

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "SELINCAH.ttf"), 24)

class ArenaScreen:
    def __init__(self, goto_shop):
        self.elements = []
        
        # Red vignette and particles
        self.particles = ParticleManager(mode="blood")
        self.vignette = create_red_vignette()
        
    def handle_event(self, e):
        for el in self.elements: el.handle_event(e)
        
    def update(self, dt):
        self.particles.update(dt)
        for el in self.elements: el.update(dt)
        
    def draw(self, surf):
        surf.fill((0, 0, 0))  # Black background
        
        # Draw particles
        self.particles.draw(surf)
        
        # Draw vignette
        surf.blit(self.vignette, (0, 0))
        
        for el in self.elements: el.draw(surf)
