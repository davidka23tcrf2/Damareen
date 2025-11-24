# cards amount, then cards line by line, enemies amount, then enemies line by line,

from manual.inventory import inventory
import os
import json
from datetime import datetime

SAVES_DIR = os.path.join(os.path.dirname(__file__), "saves")
GAMES_DIR = os.path.join(os.path.dirname(__file__), "games")

# Track the currently loaded save file for overwriting
CURRENT_SAVE_FILE = None

def save_game():
    existing = [f for f in os.listdir(SAVES_DIR) if f.startswith("save") and f.endswith(".txt")]

    if existing:
        numbers = [int(f.split("_")[0][4:]) for f in existing]
        next_num = max(numbers) + 1
    else:
        next_num = 1

    filename = f"save{next_num}_{len(inventory.GAMECARDS)}_{len(inventory.ENEMIES)}.txt"
    path = os.path.join(SAVES_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
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
        if inventory.SHOP_ENABLED:
            f.write(f"1\n")
        else:
            f.write(f"0\n")
        cards = []
        for i in inventory.PLAYERCARDS:
            cards.append(i.name)
        f.write(f"{';'.join(cards)}\n")

def save_game_state(save_name=None):
    """
    Save the current game state to the games folder.
    If save_name is None and CURRENT_SAVE_FILE exists, overwrite it.
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    Otherwise create a new save with sequential naming (jatek1, jatek2, etc.)
=======
    Otherwise create a new save with timestamp.
>>>>>>> Stashed changes
=======
    Otherwise create a new save with timestamp.
>>>>>>> Stashed changes
=======
    Otherwise create a new save with timestamp.
>>>>>>> Stashed changes
=======
    Otherwise create a new save with timestamp.
>>>>>>> Stashed changes
    """
    global CURRENT_SAVE_FILE
    
    # Ensure games directory exists
    os.makedirs(GAMES_DIR, exist_ok=True)
    
    # Determine filename
    if save_name is None:
        if CURRENT_SAVE_FILE:
            filename = CURRENT_SAVE_FILE
        else:
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
            # Find existing jatek saves and get next number
            existing = [f for f in os.listdir(GAMES_DIR) if f.startswith("jatek") and f.endswith(".json")]
            if existing:
                # Extract numbers from filenames like "jatek1.json", "jatek2.json"
                numbers = []
                for f in existing:
                    try:
                        num = int(f.replace("jatek", "").replace(".json", ""))
                        numbers.append(num)
                    except:
                        pass
                next_num = max(numbers) + 1 if numbers else 1
            else:
                next_num = 1
            
            filename = f"jatek{next_num}.json"
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_{timestamp}.json"
            CURRENT_SAVE_FILE = filename
# cards amount, then cards line by line, enemies amount, then enemies line by line,

from manual.inventory import inventory
import os
import json
from datetime import datetime

SAVES_DIR = os.path.join(os.path.dirname(__file__), "saves")
GAMES_DIR = os.path.join(os.path.dirname(__file__), "games")

# Track the currently loaded save file for overwriting
CURRENT_SAVE_FILE = None

def save_game():
    existing = [f for f in os.listdir(SAVES_DIR) if f.startswith("save") and f.endswith(".txt")]

    if existing:
        numbers = [int(f.split("_")[0][4:]) for f in existing]
        next_num = max(numbers) + 1
    else:
        next_num = 1

    filename = f"save{next_num}_{len(inventory.GAMECARDS)}_{len(inventory.ENEMIES)}.txt"
    path = os.path.join(SAVES_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
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
        if inventory.SHOP_ENABLED:
            f.write(f"1\n")
        else:
            f.write(f"0\n")
        cards = []
        for i in inventory.PLAYERCARDS:
            cards.append(i.name)
        f.write(f"{';'.join(cards)}\n")

def save_game_state(save_name=None):
    """
    Save the current game state to the games folder.
    If save_name is None and CURRENT_SAVE_FILE exists, overwrite it.
    Otherwise create a new save with timestamp.
    """
    global CURRENT_SAVE_FILE
    
    # Ensure games directory exists
    os.makedirs(GAMES_DIR, exist_ok=True)
    
    # Determine filename
    if save_name is None:
        if CURRENT_SAVE_FILE:
            filename = CURRENT_SAVE_FILE
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_{timestamp}.json"
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
            CURRENT_SAVE_FILE = filename
    else:
        filename = f"{save_name}.json" if not save_name.endswith(".json") else save_name
        CURRENT_SAVE_FILE = filename
    
    path = os.path.join(GAMES_DIR, filename)
    
    # Collect all game state
    game_state = {
        "coins": inventory.COINS,
        "shop_enabled": inventory.SHOP_ENABLED,
        "volume": inventory.VOLUME,
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        "selected_dungeon_index": inventory.SELECTED_DUNGEON_INDEX,
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        "playerdeck": [card.name for card in inventory.PLAYERDECK],
        "playercards": [card.name for card in inventory.PLAYERCARDS],
        "playerarmor": [{"type": armor.type, "slot": armor.slot} for armor in inventory.PLAYERARMOR],
        "playeraccessories": [],  # Will be populated when accessories have a name attribute
        "gamecards": [
            {
                "type": card.type,
                "name": card.name,
                "dmg": card.dmg,
                "hp": card.hp,
                "power": card.power
            } for card in inventory.GAMECARDS
        ],
        "enemies": [
            {
                "type": enemy.type,
                "name": enemy.name,
                "deck": [card.name for card in enemy.deck],
                "reward": enemy.reward if hasattr(enemy, 'reward') else None
            } for enemy in inventory.ENEMIES
        ]
    }
    
    # Save as JSON
    with open(path, "w", encoding="utf-8") as f:
        json.dump(game_state, f, indent=2, ensure_ascii=False)
    
    return filename