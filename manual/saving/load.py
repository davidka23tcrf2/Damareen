import os, re
from manual.inventory import inventory
from manual.inventory import objects
from manual.inventory.inventory import SHOP_ENABLED

SAVES_DIR = os.path.join(os.path.dirname(__file__), "saves")

SAVE_PATTERN = re.compile(r"(\d+)_(\d+)_(\d+)\.txt")

def get_save_files():
    if not os.path.isdir(SAVES_DIR):
        return []
    files = [f for f in os.listdir(SAVES_DIR) if f.lower().endswith(".txt")]
    parsed = []
    for f in files:
        name = f.replace(".txt","")
        m = re.match(r"^save(\d+)_(\d+)_(\d+)$", name)
        if m:
            parsed.append({
                "save_num": int(m.group(1)),
                "cards": int(m.group(2)),
                "enemies": int(m.group(3)),
                "file": f
            })
    parsed.sort(key=lambda x: x["save_num"])
    return parsed

def parse_save_filename(filename):
    name = os.path.splitext(filename)[0]
    m = re.match(r"^save(\d+)[_-](\d+)[_-](\d+)$", name, flags=re.IGNORECASE)
    if not m:
        return None
    return {
        "save_num": int(m.group(1)),
        "cards": int(m.group(2)),
        "enemies": int(m.group(3))
    }

def load_game(filename):
    inventory.ENEMIES.clear()
    inventory.PLAYERCARDS.clear()
    inventory.GAMECARDS.clear()
    path = os.path.join(SAVES_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        line = f.readline()
        for i in range(int(line)):
            line = f.readline().strip().split(";")
            inventory.GAMECARDS.append(objects.Card(line[0], line[1], line[2], line[3], line[4]))
        line = f.readline()
        for i in range(int(line)):
            line = f.readline().strip().split(";")
            deck = []
            if line[0] == "nagy":
                for ci in range(2, len(line)):
                    for wc in inventory.GAMECARDS:
                        if line[ci] == wc.name:
                            deck.append(wc)
                inventory.ENEMIES.append(objects.Enemy(line[0], line[1], deck))
            else:
                for ci in range(2, len(line)-1):
                    for wc in inventory.GAMECARDS:
                        if line[ci] == wc.name:
                            deck.append(wc)
                inventory.ENEMIES.append(objects.Enemy(line[0], line[1], deck, line[len(line)-1]))
        line = f.readline()
        if int(line):
            inventory.SHOP_ENABLED = True
        line = f.readline().split(";")
        if line[0] != '':
            for i in line:
                for j in inventory.GAMECARDS:
                    if j.name == i:
                        inventory.PLAYERCARDS.append(j)
