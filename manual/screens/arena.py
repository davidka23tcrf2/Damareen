import pygame
from ..ui.button import Button
from manual.assets.assets import ASSETS_DIR
<<<<<<< Updated upstream
from manual.ui.particles import ParticleManager
from manual.ui.vignette import create_red_vignette
=======
>>>>>>> Stashed changes
import os

BP = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Saphifen.ttf"), 24)

class ArenaScreen:
    def __init__(self, goto_shop):
        self.elements = []
        
<<<<<<< Updated upstream
        # Red vignette and particles
        self.particles = ParticleManager(mode="blood")
        self.vignette = create_red_vignette()
        
=======
>>>>>>> Stashed changes
    def handle_event(self, e):
        for el in self.elements: el.handle_event(e)
        
    def update(self, dt):
        self.particles.update(dt)
        for el in self.elements: el.update(dt)
        
    def draw(self, surf):
        surf.fill((0, 0, 0))  # Black background
<<<<<<< Updated upstream
        
        # Draw particles
        self.particles.draw(surf)
        
        # Draw vignette
        surf.blit(self.vignette, (0, 0))
        
=======
>>>>>>> Stashed changes
        for el in self.elements: el.draw(surf)
