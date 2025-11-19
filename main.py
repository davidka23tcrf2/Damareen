import sys
from pathlib import Path
from auto import card, enemy, fight
import copy
from manual import mainloop

def main():
    if len(sys.argv) == 1:
        print("Használat: python script.py [--ui | <test_dir_path>]")
        sys.exit(1)

    if sys.argv[1] == "--ui":
        run_ui()
    else:
        run_automated_test(sys.argv[1])
def run_ui():
    mainloop.ml()
def run_automated_test(test_dir_path):
    world_cards = []  # jatekban levo kartyak
    enemies = []  # kazamata
    playercards = []  # gyujtemeny
    playerpack = []  # jatekospakli
    with open(Path(test_dir_path) / 'in.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            line = line.split(';')

            if line[0] == 'harc':
                with open(f'{sys.argv[1]}/{line[2]}', 'w') as file:
                    file.write(f'harc kezdodik;{line[1]}\n\n')
                    e = [i for i in enemies if i.name == line[1]][0]  # enemy
                    win, winning_card = fight.attack(e.pack, playerpack, file) #win/lose, card
                    file.write('\n')
                    if not win:
                        pass
                    else:
                        if e.type == 'egyszeru' or e.type == 'kis':
                            if e.reward == 'eletero':
                                winning_card.basehp+=2
                                file.write(f'jatekos nyert;eletero;{winning_card.name}\n')
                            else:
                                winning_card.dmg += 1
                                file.write(f'jatekos nyert;sebzes;{winning_card.name}\n')
                        else:
                            for i in world_cards:
                                v = False
                                for j in playercards:
                                    if i.name == j.name:
                                        v = True
                                        break
                                if not v:
                                    playercards.append(copy.deepcopy(i))
                                    file.write(f'jatekos nyert;{i.name}\n')
                                    break
                for i in playercards:
                    i.reset()
                for i in e.pack:
                    i.reset()
            elif line[0] == 'uj kartya':
                world_cards.append(card.Card('kartya',line[1], int(line[2]), int(line[3]), line[4]))

            elif line[0] == 'uj vezer':
                for i in world_cards:
                    if i.name == line[2] and i.type == 'kartya':
                        if line[3] == 'eletero':
                            world_cards.append(card.Card('vezer', line[1], i.dmg, i.basehp*2, i.power))
                        else:
                            world_cards.append(card.Card('vezer', line[1], i.dmg*2, i.basehp, i.power))
                        break

            elif line[0] == 'uj jatekos':
                playerpack.clear()
                playercards.clear()

            elif line[0] == 'felvetel gyujtemenybe':
                for i in world_cards:
                    if i.name == line[1]:
                        playercards.append(copy.deepcopy(i))

            elif line[0] == 'uj pakli':
                k = line[1].split(',')
                for i in k:
                    for j in playercards:
                        if j.name == i:
                            playerpack.append(j)
                            break

            elif line[0] == 'uj kazamata':
                if line[1] == 'egyszeru':
                    enemies.append(enemy.Enemies(line[1], line[2],[[copy.deepcopy(i) for i in world_cards if i.name == line[3]][0]], line[4]))
                elif line[1] == 'kis':
                    p = []
                    k = line[3].split(',')
                    k.append(line[4])
                    for i in k:
                        for j in world_cards:
                            if i == j.name:
                                p.append(copy.deepcopy(j))
                    enemies.append(enemy.Enemies(line[1], line[2], p, line[5]))

                elif line[1] == 'nagy':
                    p = []
                    k = line[3].split(',')
                    k.append(line[4])
                    for i in k:
                        for j in world_cards:
                            if i == j.name:
                                p.append(copy.deepcopy(j))
                    enemies.append(enemy.Enemies(line[1], line[2], p, None))

            elif line[0] == "export vilag":
                with open(f'{sys.argv[1]}/{line[1]}', 'w') as vilagexp:
                    for i in world_cards:
                        if i.type == 'kartya':
                            vilagexp.write(f'{i.write()}')
                    vilagexp.write('\n')

                    a = False
                    for i in world_cards:
                        if i.type == 'vezer':
                            vilagexp.write(f'{i.write()}')
                            a = True

                    if a: vilagexp.write('\n')

                    for i in enemies:
                        if i.type == 'egyszeru':
                            vilagexp.write(f'kazamata;egyszeru;{i.name};{','.join([kartya.name for kartya in i.pack if kartya.type == 'kartya'])};{i.reward}\n')
                        elif i.type == 'kis':
                            for j in i.pack:
                                if j.type != 'kartya':
                                    vezercard = j.name
                            vilagexp.write(f'kazamata;kis;{i.name};{','.join([kartya.name for kartya in i.pack if kartya.type == 'kartya'])};{vezercard};{i.reward}\n')
                        elif i.type == 'nagy':
                            for j in i.pack:
                                if j.type != 'kartya':
                                    vezercard = j.name
                            vilagexp.write(f'kazamata;nagy;{i.name};{','.join([kartya.name for kartya in i.pack if kartya.type == 'kartya'])};{vezercard}\n')


            elif line[0] == "export jatekos":
                with open(f'{sys.argv[1]}/{line[1]}', 'w') as jatekosxp:
                    for i in playercards:
                        jatekosxp.write(f'gyujtemeny;{i.name};{i.dmg};{i.basehp};{i.power}\n')
                    jatekosxp.write('\n')
                    for i in playerpack:
                        jatekosxp.write(f'pakli;{i.name}\n')
if __name__ == "__main__":
    main()