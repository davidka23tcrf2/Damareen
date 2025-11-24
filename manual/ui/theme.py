import pygame

# --- COLORS ---
# Backgrounds
BG_DARK = (20, 20, 30)       # Very dark blue/grey for main backgrounds
BG_PANEL = (40, 40, 55)      # Slightly lighter for panels/popups
BG_INPUT = (30, 30, 40)      # Input fields

# Accents
PRIMARY = (80, 140, 255)     # Blue - Primary actions (Save, Confirm)
PRIMARY_HOVER = (100, 160, 255)
SECONDARY = (100, 100, 120)  # Grey - Secondary actions (Cancel, Back)
SECONDARY_HOVER = (120, 120, 140)
ACCENT = (255, 215, 0)       # Gold - Highlights, Selection

# Status
SUCCESS = (50, 200, 80)      # Green
DANGER = (220, 60, 60)       # Red
WARNING = (255, 165, 0)      # Orange

# Text
TEXT_WHITE = (240, 240, 240)
TEXT_GREY = (180, 180, 190)
TEXT_BLACK = (20, 20, 20)

# Borders
BORDER_COLOR = (60, 60, 80)
BORDER_FOCUS = ACCENT

# --- DIMENSIONS ---
BORDER_RADIUS = 12
BORDER_WIDTH = 2
PADDING = 10

# --- FONTS ---
# (Fonts are usually loaded with pygame.font.Font, so we might just define sizes here 
# or helper functions if we had a font manager. For now, we stick to colors/constants)
FONT_SIZE_SMALL = 16
FONT_SIZE_NORMAL = 20
FONT_SIZE_LARGE = 32
FONT_SIZE_TITLE = 48
