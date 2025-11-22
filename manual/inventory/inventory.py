from manual.inventory import objects
from manual.assets.assets import load_asset
SHOP_ENABLED = False
COINS = 0

#empty from the start
PLAYERDECK = [

]

#gamemaster defines what payer has
PLAYERCARDS = [

]

#all cards ingame
GAMECARDS = [
]

#all enemies ingame
ENEMIES = [
]

#all armor ingame
ARMOR = [
    objects.Armor("fold", "sapka", load_asset("dirthelmet.png", "armor")),
    objects.Armor("viz", "sapka", load_asset("waterhelmet.png", "armor")),
    objects.Armor("tuz", "sapka", load_asset("firehelmet.png", "armor")),
    objects.Armor("levego", "sapka", load_asset("airhelmet.png", "armor")),
    objects.Armor("fold", "mellvert", load_asset("dirtchestplate.png", "armor")),
    objects.Armor("viz", "mellvert", load_asset("waterchestplate.png", "armor")),
    objects.Armor("tuz", "mellvert", load_asset("firechestplate.png", "armor")),
    objects.Armor("levego", "mellvert", load_asset("airchestplate.png", "armor")),
    objects.Armor("fold", "nadrag", load_asset("dirtleggings.png", "armor")),
    objects.Armor("viz", "nadrag", load_asset("waterleggings.png", "armor")),
    objects.Armor("tuz", "nadrag", load_asset("fireleggings.png", "armor")),
    objects.Armor("levego", "nadrag", load_asset("airleggings.png", "armor")),
    objects.Armor("fold", "cipo", load_asset("dirtboots.png", "armor")),
    objects.Armor("viz", "cipo", load_asset("waterboots.png", "armor")),
    objects.Armor("tuz", "cipo", load_asset("fireboots.png", "armor")),
    objects.Armor("levego", "cipo", load_asset("airboots.png", "armor")),
]

#armor the player has
PLAYERARMOR = [

]

#all accessories ingame
ACCESSORIES = [

]

#accessories the player has
PLAYERACCESSORIES = [

]