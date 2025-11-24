import pygame

def create_red_vignette(screen_size=(1280, 720)):
    """Create a red vignette overlay for screens"""
    vignette = pygame.Surface(screen_size, pygame.SRCALPHA)
    w, h = screen_size
    cx, cy = w // 2, h // 2
    max_dist = ((w/2)**2 + (h/2)**2) ** 0.5
    
    for y in range(h):
        for x in range(w):
            dx = x - cx
            dy = y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            
            # Vignette strength (0 at center, 1 at edges)
            t = min(1.0, dist / max_dist)
            # Quadratic falloff for smoother gradient
            alpha = int(180 * (t ** 2))
            
            # Red tint
            vignette.set_at((x, y), (50, 0, 0, alpha))
    
    return vignette
