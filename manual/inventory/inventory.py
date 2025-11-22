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
    objects.Armor("fold", "helmet", load_asset("dirthelmet.png", "armor")),
    objects.Armor("viz", "helmet", load_asset("waterhelmet.png", "armor")),
    objects.Armor("tuz", "helmet", load_asset("firehelmet.png", "armor")),
    objects.Armor("levego", "helmet", load_asset("airhelmet.png", "armor")),
    objects.Armor("fold", "chestplate", load_asset("dirtchestplate.png", "armor")),
    objects.Armor("viz", "chestplate", load_asset("waterchestplate.png", "armor")),
    objects.Armor("tuz", "chestplate", load_asset("firechestplate.png", "armor")),
    objects.Armor("levego", "chestplate", load_asset("airchestplate.png", "armor")),
    objects.Armor("fold", "leggings", load_asset("dirtleggings.png", "armor")),
    objects.Armor("viz", "leggings", load_asset("waterleggings.png", "armor")),
    objects.Armor("tuz", "leggings", load_asset("fireleggings.png", "armor")),
    objects.Armor("levego", "leggings", load_asset("airleggings.png", "armor")),
    objects.Armor("fold", "boots", load_asset("dirtboots.png", "armor")),
    objects.Armor("viz", "boots", load_asset("waterboots.png", "armor")),
    objects.Armor("tuz", "boots", load_asset("fireboots.png", "armor")),
    objects.Armor("levego", "boots", load_asset("airboots.png", "armor")),
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