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
        for i in self.deck:
            i.reset()

class Armor: #boost defense (less dmg taken) by some percent
    def __init__(self, type, what, img, defense = None):
        self.type = type #fold/viz.tuz...
        self.what = what #leggings/boots/chestplate...
        self.img = img #the image of the said armorpiece
        self.defense = defense #percentage of the defense

    def buy(self):
        inventory.PLAYERARMOR.append(self)

class Accessory:
    def __init__(self, type, what, img, attack = None):
        self.type = type #same as armor
        self.what = what #bracelet/ring/necklace
        self.img = img #same as armor
        self.attack = attack #same logic as armor

    def buy(self):
        inventory.PLAYERACCESSORIES.append(self)