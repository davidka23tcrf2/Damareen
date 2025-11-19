from auto import card
import math

def attack(Enemy, Player, file):
    Round = 1
    InnerRound = 0
    i = 0  # Játékos index
    j = 0  # Enemy index
    playedoutP = False
    playedoutE = False
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
            damge = card.get_type_multiplier(Enemy[j].power, Player[i].power)
            Player[i].hp -= math.floor(Enemy[j].dmg * damge)
            file.write(
                f"{Round}.kor;kazamata;tamad;{Enemy[j].name};"
                f"{damge * Enemy[j].dmg};{Player[i].name};{Player[i].hp}\n"
            )
            if Player[i].hp <= 0:
                i += 1
                playedoutP = True
                if i == len(Player):
                    file.write("jatekos vesztett\n")
                    return False, None


        else:
            file.write(
                f"{Round}.kor;kazamata;kijatszik;{Enemy[j].name};{Enemy[j].dmg};{Enemy[j].hp};{Enemy[j].power}\n")
            playedoutE = False

        if not playedoutP:
            damge = card.get_type_multiplier(Enemy[j].power, Player[i].power)
            Enemy[j].hp -= math.floor(damge * Player[i].dmg)
            file.write(
                f"{Round}.kor;jatekos;tamad;{Player[i].name};"
                f"{damge * Player[i].dmg};{Enemy[j].name};{Enemy[j].hp}\n"
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
                f"{Round}.kor;jatekos;kijatszik;{Player[i].name};{Player[i].dmg};{Player[i].hp};{Player[i].power}\n")
            playedoutP = False
            Round += 1
            file.write("\n")