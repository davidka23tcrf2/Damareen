import os
import glob

def fix_files():
    # Fix .txt saves
    txt_files = glob.glob("manual/saving/saves/*.txt")
    for fpath in txt_files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "levegő" in content:
            print(f"Fixing {fpath}")
            content = content.replace("levegő", "levego")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)

    # Fix .json games
    json_files = glob.glob("manual/saving/games/*.json")
    for fpath in json_files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "levegő" in content:
            print(f"Fixing {fpath}")
            content = content.replace("levegő", "levego")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)

if __name__ == "__main__":
    fix_files()
