from auto import card
import math
import random

def attack(Enemy, Player, file, difficulty=1):
    """
    Combat function with randomized damage.
    
    Args:
        Enemy: List of enemy cards
        Player: List of player cards
        file: Output file for combat log
        difficulty: Difficulty level (affects damage variance)
    """
    Round = 1
    i = 0  # Játékos index
    j = 0  # Enemy index
    playedoutP = False
    playedoutE = False
    n = difficulty  # Use difficulty for damage variance
    
    while i < len(Player) and j < len(Enemy):

        if Round == 1:

            file.write(
                f"{Round}.kor;kazamata;kijatszik;{Enemy[j].name};"
                f"{Enemy[j].dmg};{Enemy[j].hp};{Enemy[j].power}\n"
            )
            file.write(
                f"{Round}.kor;jatekos;kijatszik;{Player[i].name};"
                f"{Player[i].dmg};{Player[i].hp};{Player[i].power}\n"
            )
            Round += 1
            file.write("\n")

            continue

        if not playedoutE:
            damage = card.get_type_multiplier(Enemy[j].power, Player[i].power)
            # Kazamata damage: round(base_damage * (1 + rnd() * n/10))
            final_damage = round(Enemy[j].dmg * damage * (1 + random.random() * n / 10))
            Player[i].hp -= final_damage
            file.write(
                f"{Round}.kor;kazamata;tamad;{Enemy[j].name};"
                f"{final_damage};{Player[i].name};{max(0, Player[i].hp)}\n"
            )
            if Player[i].hp <= 0:
                i += 1
                playedoutP = True
                if i == len(Player):
                    file.write("jatekos vesztett\n")
                    return False, None


        else:
            file.write(
                f"{Round}.kor;kazamata;kijatszik;{Enemy[j].name};{Enemy[j].dmg};{max(0, Enemy[j].hp)};{Enemy[j].power}\n")
            playedoutE = False

        if not playedoutP:
            damage = card.get_type_multiplier(Enemy[j].power, Player[i].power)
            # Jatekos damage: round(base_damage * (1 - rnd() * n/20))
            final_damage = round(Player[i].dmg * damage * (1 - random.random() * n / 20))
            Enemy[j].hp -= final_damage
            file.write(
                f"{Round}.kor;jatekos;tamad;{Player[i].name};"
                f"{final_damage};{Enemy[j].name};{max(0, Enemy[j].hp)}\n"
            )

            if Enemy[j].hp <= 0:

                j += 1
                playedoutE = True
                if j == len(Enemy):
                    return True, Player[i]

                Round += 1
                file.write("\n")
                continue

            Round += 1
            file.write("\n")

        else:
            file.write(
                f"{Round}.kor;jatekos;kijatszik;{Player[i].name};{Player[i].dmg};{max(0, Player[i].hp)};{Player[i].power}\n")
            playedoutP = False
            Round += 1
            file.write("\n")