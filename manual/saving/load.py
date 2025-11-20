import os
from manual.inventory import inventory
from manual.inventory import objects

SAVES_DIR = os.path.join(os.path.dirname(__file__), "saves")

def load_game(filename):
    path = os.path.join(SAVES_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        line = f.readline()
        for i in range(int(line)):
            line = f.readline().strip().split(";")
            inventory.GAMECARDS.append(objects.Card(line[1], line[2], line[3], line[4], line[5]))
        line = f.readline()
        for i in range(int(line)):
            line = f.readline().strip().split(";")
            #enemies
