# cards amount, then cards line by line, enemies amount, then enemies line by line,

from manual.inventory import inventory
import os
SAVES_DIR = os.path.join(os.path.dirname(__file__), "saves")

def save_game():
    existing = [f for f in os.listdir(SAVES_DIR) if f.startswith("save") and f.endswith(".txt")]

    if existing:
        numbers = [int(f.split("_")[0][4:]) for f in existing]
        next_num = max(numbers) + 1
    else:
        next_num = 1

    filename = f"save{next_num}_{len(inventory.GAMECARDS)}_{len(inventory.ENEMIES)}.txt"
    path = os.path.join(SAVES_DIR, filename)

    with open(path, "w") as f:
        f.write(f'{len(inventory.GAMECARDS)}\n')
        for i in inventory.GAMECARDS:
            f.write(f'{i.type};')
            f.write(f'{i.name};')
            f.write(f'{i.dmg};')
            f.write(f'{i.hp};')
            f.write(f'{i.power}\n')
        f.write(f'{len(inventory.ENEMIES)}\n')
        for i in inventory.ENEMIES:
            deck = ";".join([j.name for j in i.deck])
            if i.reward:
                f.write(f'{i.type};{i.name};{deck};{i.reward}\n')
            else:
                f.write(f'{i.type};{i.name};{deck}\n')