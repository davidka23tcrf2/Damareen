relation = {
    "fold":["levego", "tuz"],
    "viz":["levego", "tuz"],
    "tuz":["fold", "viz"],
    "levego":["fold", "viz"]
}

def get_type_multiplier(power1, power2):
    if power1 == power2:
        return 1
    if power2 in relation[power1]:
        return 2
    else:
        return 0.5

class Card:
    def __init__(self, type_, name, dmg, hp, power):
        self.type = type_ #lehet "kartya" | vezer"
        self.name = name
        self.dmg = dmg
        self.basehp = hp
        self.power = power #powers = ["fold", "viz", "tuz", "levego"]
        self.hp = hp

    def reset(self): #resets card's hp
        self.hp = self.basehp

    def write(self): #returns card details
        return f"{self.type};{self.name};{self.dmg};{self.basehp};{self.power}\n"