from manual.inventory import objects
from manual.assets.assets import load_asset

SHOP_NEEDS_REFRESH = False
SHOP_ENABLED = False
COINS = 0

# Difficulty settings
DIFFICULTY = 0
DIFFICULTY_SELECTED = False

# Volume setting (0-100)
VOLUME = 50

# Selected Dungeon Index
SELECTED_DUNGEON_INDEX = 0

#empty from the start
PLAYERDECK = [

]

ENEMIES = [

]

#gamemaster defines what payer has
PLAYERCARDS = [

]

#all cards ingame
GAMECARDS = [
]

PLAYERARMOR = [
]

EQUIPPED_ARMOR = [

]  # Only one item at a time, treated as a list for simplicity

ARMOR = [
    objects.Armor("fold", "sapka", "dirthelmet.png"),
    objects.Armor("viz", "sapka", "waterhelmet.png"),
    objects.Armor("tuz", "sapka", "firehelmet.png"),
    objects.Armor("levego", "sapka", "airhelmet.png"),

    objects.Armor("fold", "mellvert", "dirtchestplate.png"),
    objects.Armor("viz", "mellvert", "waterchestplate.png"),
    objects.Armor("tuz", "mellvert", "firechestplate.png"),
    objects.Armor("levego", "mellvert", "airchestplate.png"),

    objects.Armor("fold", "nadrag", "dirtleggings.png"),
    objects.Armor("viz", "nadrag", "waterleggings.png"),
    objects.Armor("tuz", "nadrag", "fireleggings.png"),
    objects.Armor("levego", "nadrag", "airleggings.png"),

    objects.Armor("fold", "cipo", "dirtboots.png"),
    objects.Armor("viz", "cipo", "waterboots.png"),
    objects.Armor("tuz", "cipo", "fireboots.png"),
    objects.Armor("levego", "cipo", "airboots.png"),
]
