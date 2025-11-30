from manual.inventory import inventory
class Card:
    def __init__(self, type_, name, dmg, hp, power):
        self.type = type_ #lehet "kartya" | vezer"
        self.name = name
        self.dmg = int(dmg)
        self.basehp = int(hp)
        self.power = power #powers = ["fold", "viz", "tuz", "levego"]
        self.hp = int(hp)

    def reset(self): #resets card's hp
        self.hp = self.basehp

class Enemy:
    def __init__(self, type, name, deck, reward = None):
        self.type = type
        self.name = name
        self.deck = deck
        self.reward = reward
    def reset(self):
        for card in self.deck:
            if hasattr(card, "reset"):
                card.reset()

class Armor:
    def __init__(self, type_, what, image_name, defense=0):
        self.type = type_
        self.what = what
        self.image_name = image_name
        self.defense = defense

    def get_image(self):
        from manual.assets.assets import load_asset
        return load_asset(self.image_name, "armor")

    def buy(self):
        inventory.PLAYERARMOR.append(self)
        print(f"Bought armor: {self.what}")

    def equip(self):
        if inventory.EQUIPPED_ARMOR:
            print(f"Unequipped: {inventory.EQUIPPED_ARMOR[0].what}")
            inventory.EQUIPPED_ARMOR[0] = self
        else:
            inventory.EQUIPPED_ARMOR.append(self)
        print(f"Equipped armor: {self.what}")
