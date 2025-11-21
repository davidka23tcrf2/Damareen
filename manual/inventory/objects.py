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