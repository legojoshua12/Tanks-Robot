import json


def createGame(data):
    print(data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def addPlayerToGame(player):
    print(f'Adding player {player}')
