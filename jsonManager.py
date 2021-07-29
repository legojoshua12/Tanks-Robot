import json


def createGame(message):
    players = {}
    data = {'games': {message.guild.id: {message.channel.id: {}}}}
    data['games'][message.guild.id][message.channel.id]['players'] = players
    data['games'][message.guild.id][message.channel.id]['board'] = []
    data['games'][message.guild.id][message.channel.id]['gameStatus'] = "lobby"
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data

def addPlayerToGame(message, playerNumber):
    data = __readJson()
    newPlayerData = {
        message.author.id: {
            'playerNumber': playerNumber,
            'lives': 3,
            'actions': 0,
            'range': 1
        }
    }
    playersList = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
    playersList.update(newPlayerData)
    data['games'][str(message.guild.id)][str(message.channel.id)]['players'] = playersList
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def getNumberOfPlayersInGame(message):
    data = __readJson()
    numberOfPlayers = 0
    playersList = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
    for player in playersList:
        numberOfPlayers = numberOfPlayers + 1
    return numberOfPlayers

def checkIfGameIsInChannel(message):
    data = __readJson()
    try:
        gameState = data['games'][str(message.guild.id)][str(message.channel.id)]['gameStatus']
        return gameState
    except:
        return 'none'

def __readJson():
    file = open('Games.json', )
    data = json.load(file)
    file.close()
    return data
