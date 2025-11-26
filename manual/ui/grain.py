import pygame
import random
import os

class GrainEffect:
    def __init__(self, width, height, intensity=50):
        self.width = width
        self.height = height
import pygame
import random
import os

class GrainEffect:
    def __init__(self, width, height, intensity=50):
        self.width = width
        self.height = height
        self.intensity = intensity
        self.noise_surfaces = []
        self.frame_index = 0
        self.generate_noise()

    def generate_noise(self):
        self.noise_surfaces = []
        scale = 2
        w, h = self.width // scale, self.height // scale
        
        # Generate 30 frames for very smooth/random animation
        for _ in range(30):
            # Create random RGB noise
            raw = os.urandom(w * h * 3)
            noise = pygame.image.frombuffer(raw, (w, h), "RGB")
            
            # Set alpha for the whole surface
            noise.set_alpha(self.intensity)
            
            # Scale up
            final = pygame.transform.scale(noise, (self.width, self.height))
            self.noise_surfaces.append(final)

    def update(self, dt):
        # Pick a random frame each time for maximum randomness
        self.frame_index = random.randint(0, len(self.noise_surfaces) - 1)

    def draw(self, surf, alpha_mult=1.0):
        current_surf = self.noise_surfaces[self.frame_index]
        
        # Calculate effective alpha
        effective_alpha = int(self.intensity * alpha_mult)
        
        # Only draw if visible
        if effective_alpha > 0:
            current_surf.set_alpha(effective_alpha)
            surf.blit(current_surf, (0, 0))
            # Restore alpha for next usage (though we reset it every time anyway)
