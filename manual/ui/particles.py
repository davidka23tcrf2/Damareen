import pygame
import random
import math
from manual.ui import theme


class Particle:
    # Cache textures so we don't rebuild the same soft-circle over and over
    _texture_cache = {}

    def __init__(self, x, y, screen_width, screen_height, mode="default"):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.mode = mode

        self.age = 0.0  # seconds

        if self.mode == "blood":
            # Cinematic red dust: slow drift downward, soft glow, long fade
            self.size = random.randint(6, 14)  # logical radius
            self.color = random.choice([
                (220, 40, 40),
                (255, 60, 60),
                (150, 10, 10),
            ])

            # Velocity in px/sec
            self.vx = random.uniform(-10.0, 10.0)
            self.vy = random.uniform(20.0, 60.0)

            # Lifetime in seconds - much longer for atmospheric effect
            self.max_life = random.uniform(5.0, 10.0)
            self.life = self.max_life

            # Gentle side sway
            self.sway_amp = random.uniform(3.0, 10.0)
            self.sway_freq = random.uniform(0.8, 2.0)
        else:
            # Default: soft ambient floaty particles
            self.size = random.randint(4, 10)
            colors = [
                theme.PRIMARY,
                theme.PRIMARY_HOVER,
                theme.ACCENT,
                (120, 120, 180),
            ]
            self.color = random.choice(colors)

            # Velocity in px/sec (slow drifting)
            self.vx = random.uniform(-15.0, 15.0)
            self.vy = random.uniform(-10.0, 10.0)

            self.max_life = random.uniform(4.0, 8.0)
            self.life = self.max_life

            self.sway_amp = random.uniform(1.0, 5.0)
            self.sway_freq = random.uniform(0.5, 1.5)

    @classmethod
    def _get_texture(cls, size, color):
        """
        Returns a soft, glowing circular texture for the given size + color.
        Cached so we only build each combination once.
        """
        key = (size, color)
        if key in cls._texture_cache:
            return cls._texture_cache[key]

        radius = size
        tex_size = radius * 4  # Padding to allow very soft edges
        surf = pygame.Surface((tex_size, tex_size), pygame.SRCALPHA)
        cx = cy = tex_size // 2

        # Draw multiple circles with decreasing alpha for a smooth radial gradient
        for r in range(radius, 0, -1):
            t = r / radius  # 1 at center, 0 at edge
            # Slightly bias center so it feels like a glow
            alpha = int(255 * (t ** 2))
            col = (color[0], color[1], color[2], alpha)
            pygame.draw.circle(surf, col, (cx, cy), r)

        cls._texture_cache[key] = surf
        return surf

    def update(self, dt):
        # dt is seconds
        self.age += dt
        self.life -= dt

        # Basic movement
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surf):
        if self.life <= 0:
            return

        # Normalized life (1 at birth, 0 near death)
        life_ratio = max(self.life / self.max_life, 0.0)

        tex = self._get_texture(self.size, self.color)

        # Sway / flutter for a more organic feel
        sway_offset_x = math.sin(self.age * self.sway_freq) * self.sway_amp

        draw_x = self.x + sway_offset_x - tex.get_width() // 2
        draw_y = self.y - tex.get_height() // 2

        # Fade alpha over lifetime
        # Copy the texture alpha via a temporary surface with overall fade
        temp = tex.copy()
        temp.set_alpha(int(255 * life_ratio))

        surf.blit(temp, (int(draw_x), int(draw_y)))


class ParticleManager:
    def __init__(self, screen_width=1280, screen_height=720, mode="default"):
        self.particles = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.mode = mode
        self.spawn_timer = 0.0

        # Faster spawn for blood mode to feel denser and more atmospheric
        self.spawn_rate = 0.03 if mode == "blood" else 0.08  # seconds between spawns

    def _spawn_particle(self):
        if self.mode == "blood":
            # Spawn just above the top edge so they drift into view
            x = random.randint(0, self.screen_width)
            y = random.uniform(-40, -10)
            self.particles.append(
                Particle(x, y, self.screen_width, self.screen_height, mode="blood")
            )
        else:
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            self.particles.append(
                Particle(x, y, self.screen_width, self.screen_height, mode="default")
            )

    def update(self, dt):
        # dt in seconds
        self.spawn_timer += dt
        # Handle variable frame times robustly
        while self.spawn_timer >= self.spawn_rate:
            self.spawn_timer -= self.spawn_rate
            self._spawn_particle()

        for p in self.particles:
            p.update(dt)

        # Keep only alive and on-screen (for blood, we only care until they leave bottom)
        if self.mode == "blood":
            self.particles = [
                p for p in self.particles
                if p.life > 0 and p.y < self.screen_height + 50
            ]
        else:
            self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surf):
        for p in self.particles:
            p.draw(surf)
