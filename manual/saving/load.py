import os, re, json
from manual.inventory import inventory
from manual.inventory import objects
from manual.inventory.inventory import SHOP_ENABLED
from manual.saving import save

SAVES_DIR = os.path.join(os.path.dirname(__file__), "saves")
GAMES_DIR = os.path.join(os.path.dirname(__file__), "games")

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

def get_game_saves():
    """Get all saved games from the games folder"""
    if not os.path.isdir(GAMES_DIR):
        return []
    
    files = [f for f in os.listdir(GAMES_DIR) if f.lower().endswith(".json")]
    saves = []
    
    for f in files:
        path = os.path.join(GAMES_DIR, f)
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
                # Get file modification time
                mod_time = os.path.getmtime(path)
                saves.append({
                    "filename": f,
                    "coins": data.get("coins", 0),
                    "cards": len(data.get("playercards", [])),
                    "mod_time": mod_time
                })
        except:
            pass
    
    # Sort by modification time (newest first)
    saves.sort(key=lambda x: x["mod_time"], reverse=True)
    return saves

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
    # inventory.ENEMIES.clear()
    # inventory.PLAYERCARDS.clear()
    # inventory.GAMECARDS.clear()
    path = os.path.join(SAVES_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        line = f.readline()
        for i in range(int(line)):
            line = f.readline().strip().split(";")
            if len(line) >= 5:
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
        line = f.readline().strip().split(";")
        if line[0] != '':
            for i in line:
                for j in inventory.GAMECARDS:
                    if j.name == i:
                        inventory.PLAYERCARDS.append(j)

def load_game_state(filename):
    """
    Load game state from the games folder.
    """
    path = os.path.join(GAMES_DIR, filename)
    
    with open(path, "r", encoding="utf-8") as f:
        game_state = json.load(f)
    
    # Clear existing inventory
    inventory.PLAYERDECK.clear()
    inventory.PLAYERCARDS.clear()
    inventory.GAMECARDS.clear()
    inventory.ENEMIES.clear()
    inventory.PLAYERARMOR.clear()
    inventory.PLAYERACCESSORIES.clear()
    
    # Load basic values
    inventory.COINS = game_state.get("coins", 0)
    inventory.SHOP_ENABLED = game_state.get("shop_enabled", False)
    inventory.VOLUME = game_state.get("volume", 50)
    inventory.SELECTED_DUNGEON_INDEX = game_state.get("selected_dungeon_index", 0)
    
    # Apply volume to pygame mixer
    try:
        import pygame
        pygame.mixer.music.set_volume(inventory.VOLUME / 100.0)
    except:
        pass
    
    # Load game cards first
    for card_data in game_state.get("gamecards", []):
        card = objects.Card(
            card_data["type"],
            card_data["name"],
            card_data["dmg"],
            card_data["hp"],
            card_data["power"]
        )
        inventory.GAMECARDS.append(card)
    
    # Load enemies
    for enemy_data in game_state.get("enemies", []):
        deck = []
        for card_name in enemy_data["deck"]:
            for card in inventory.GAMECARDS:
                if card.name == card_name:
                    deck.append(card)
                    break
        
        enemy = objects.Enemy(
            enemy_data["type"],
            enemy_data["name"],
            deck,
            enemy_data.get("reward")
        )
        inventory.ENEMIES.append(enemy)
    
    # Load player cards
    for card_name in game_state.get("playercards", []):
        for card in inventory.GAMECARDS:
            if card.name == card_name:
                inventory.PLAYERCARDS.append(card)
                break
    
    # Load player deck
    for card_name in game_state.get("playerdeck", []):
        for card in inventory.GAMECARDS:
            if card.name == card_name:
                inventory.PLAYERDECK.append(card)
                break
    
    # Load player armor
    for armor_data in game_state.get("playerarmor", []):
        for armor in inventory.ARMOR:
            if armor.type == armor_data["type"] and armor.slot == armor_data["slot"]:
                inventory.PLAYERARMOR.append(armor)
                break
    
    # Set current save file
    save.CURRENT_SAVE_FILE = filename
    
    return game_state
