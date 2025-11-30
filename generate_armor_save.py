import json
import os
import random

# Create the save directory path
GAMES_DIR = os.path.join(os.path.dirname(__file__), "manual", "saving", "games")
os.makedirs(GAMES_DIR, exist_ok=True)

# Armor types and slots
armor_types = ["fold", "viz", "tuz", "levego"]  # earth, water, fire, air
armor_slots = ["sapka", "mellvert", "nadrag", "cipo"]  # hat, chestplate, leggings, boots
armor_images = {
    ("fold", "sapka"): "dirthelmet.png",
    ("viz", "sapka"): "waterhelmet.png",
    ("tuz", "sapka"): "firehelmet.png",
    ("levego", "sapka"): "airhelmet.png",
    ("fold", "mellvert"): "dirtchestplate.png",
    ("viz", "mellvert"): "waterchestplate.png",
    ("tuz", "mellvert"): "firechestplate.png",
    ("levego", "mellvert"): "airchestplate.png",
    ("fold", "nadrag"): "dirtleggings.png",
    ("viz", "nadrag"): "waterleggings.png",
    ("tuz", "nadrag"): "fireleggings.png",
    ("levego", "nadrag"): "airleggings.png",
    ("fold", "cipo"): "dirtboots.png",
    ("viz", "cipo"): "waterboots.png",
    ("tuz", "cipo"): "fireboots.png",
    ("levego", "cipo"): "airboots.png",
}

# Generate 25 armor pieces with different defense percentages
player_armor = []
for i in range(25):
    armor_type = random.choice(armor_types)
    armor_slot = random.choice(armor_slots)
    image_name = armor_images[(armor_type, armor_slot)]
    defense = random.randint(10, 20)  # Random defense between 10% and 20%
    
    player_armor.append({
        "type": armor_type,
        "what": armor_slot,
        "image_name": image_name,
        "defense": defense
    })

# Create the game state
game_state = {
    "cards": [],
    "enemies": [],
    "player_cards": [],
    "player_armor": player_armor,
    "equipped_armor": [],
    "shop_enabled": False,
    "coins": 100,
    "volume": 50,
    "difficulty": 0,
    "selected_dungeon": 0
}

# Save to JSON file
output_path = os.path.join(GAMES_DIR, "test_armor.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(game_state, f, indent=2, ensure_ascii=False)

print(f"✅ Created save file: {output_path}")
print(f"📦 Generated {len(player_armor)} armor pieces with defense ranging from 10% to 20%")
print("\nArmor breakdown:")
for idx, armor in enumerate(player_armor, 1):
    print(f"  {idx}. {armor['type']} {armor['what']} - {armor['defense']}% defense")
