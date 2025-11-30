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
            # ORIGINAL BLOOD MODE (unchanged)
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

        elif self.mode == "horror":
            # NEW HORROR MODE: no circles – just jagged, flickering scratches
            self.size = random.randint(5, 12)

            # Desaturated, nasty tones
            self.color = random.choice([
                (180, 40, 40),   # dried blood
                (140, 140, 150), # ghost grey
                (90, 0, 0),      # deep red
            ])

            # Slow drifting motion
            self.vx = random.uniform(-20.0, 20.0)
            self.vy = random.uniform(-10.0, 15.0)

            self.max_life = random.uniform(3.0, 6.0)
            self.life = self.max_life

            # Wobbly / nervous movement
            self.sway_amp = random.uniform(8.0, 20.0)
            self.sway_freq = random.uniform(0.7, 1.8)

            # Scratch parameters
            self.length = random.uniform(30.0, 90.0)
            self.thickness = random.randint(1, 3)
            self.angle = random.uniform(-math.pi, math.pi)
            self.spin = random.uniform(-1.5, 1.5)

            # Flicker
            self.flicker_speed = random.uniform(3.0, 6.0)

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
        Used by blood + default modes only.
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

        # Spin only for horror scratches
        if self.mode == "horror":
            self.angle += self.spin * dt

        # Basic movement
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surf):
        if self.life <= 0:
            return

        # Normalized life (1 at birth, 0 near death)
        life_ratio = max(self.life / self.max_life, 0.0)

        # --- SPECIAL CASE: HORROR SCRATCHES (no circles) ---
        if self.mode == "horror":
            # base position with sway
            sway_offset_x = math.sin(self.age * self.sway_freq) * self.sway_amp
            x = self.x + sway_offset_x
            y = self.y

            # Flickering alpha
            alpha = int(255 * life_ratio)
            flick = 0.6 + 0.4 * math.sin(self.age * self.flicker_speed)
            alpha = int(alpha * flick)
            alpha = max(0, min(255, alpha))

            # Line endpoints
            dx = math.cos(self.angle) * self.length
            dy = math.sin(self.angle) * self.length

            start = (int(x - dx * 0.5), int(y - dy * 0.5))
            end   = (int(x + dx * 0.5), int(y + dy * 0.5))

            # Main scratch
            color = (self.color[0], self.color[1], self.color[2], alpha)
            pygame.draw.line(surf, color, start, end, self.thickness)

            # Second fainter scratch offset a bit (like claw marks)
            offset_dx = -dy * 0.15
            offset_dy = dx * 0.15
            start2 = (start[0] + offset_dx, start[1] + offset_dy)
            end2   = (end[0] + offset_dx, end[1] + offset_dy)
            color2 = (self.color[0], self.color[1], self.color[2], max(0, alpha // 2))
            pygame.draw.line(surf, color2, start2, end2, max(1, self.thickness - 1))

            return

        # --- BLOOD + DEFAULT: original circular glow rendering ---
        tex = self._get_texture(self.size, self.color)

        sway_offset_x = math.sin(self.age * self.sway_freq) * self.sway_amp

        draw_x = self.x + sway_offset_x - tex.get_width() // 2
        draw_y = self.y - tex.get_height() // 2

        # Fade alpha over lifetime
        alpha = int(255 * life_ratio)
        alpha = max(0, min(255, alpha))

        temp = tex.copy()
        temp.set_alpha(alpha)

        surf.blit(temp, (int(draw_x), int(draw_y)))


class ParticleManager:
    def __init__(self, screen_width=1280, screen_height=720, mode="default"):
        self.particles = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.mode = mode
        self.spawn_timer = 0.0

        # Faster spawn for blood mode to feel denser and more atmospheric
        if mode == "blood":
            self.spawn_rate = 0.03
        elif mode == "horror":
            # Medium dense ghosty scratches
            self.spawn_rate = 0.04
        else:
            self.spawn_rate = 0.08  # default

    def _spawn_particle(self):
        if self.mode == "blood":
            # ORIGINAL BLOOD SPAWN (unchanged)
            # Spawn just above the top edge so they drift into view
            x = random.randint(0, self.screen_width)
            y = random.uniform(-40, -10)
            self.particles.append(
                Particle(x, y, self.screen_width, self.screen_height, mode="blood")
            )

        elif self.mode == "horror":
            # Horror scratches: spawn from edges and inside
            spawn_edge = random.choice(["top", "bottom", "left", "right", "inside"])

            if spawn_edge == "top":
                x = random.randint(0, self.screen_width)
                y = random.uniform(-20, 40)
            elif spawn_edge == "bottom":
                x = random.randint(0, self.screen_width)
                y = random.uniform(self.screen_height - 40, self.screen_height + 20)
            elif spawn_edge == "left":
                x = random.uniform(-20, 40)
                y = random.randint(0, self.screen_height)
            elif spawn_edge == "right":
                x = random.uniform(self.screen_width - 40, self.screen_width + 20)
                y = random.randint(0, self.screen_height)
            else:  # inside
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)

            self.particles.append(
                Particle(x, y, self.screen_width, self.screen_height, mode="horror")
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
