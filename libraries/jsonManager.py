import json
import os

import cmapy
import random

from libraries.CustomIndentEncoder import NoIndent, MyEncoder


def createGame(message):
    data = readJson()
    # These are redundancy checks to ensure no data corruption
    if 'games' not in data:
        data = {'games': {}}
    if str(message.guild.id) not in data['games']:
        newGuild = {
            str(message.guild.id): {}
        }
        data['games'].update(newGuild)
    if str(message.channel.id) not in data['games'][str(message.guild.id)]:
        newChannel = {
            str(message.channel.id): {}
        }
        data['games'][str(message.guild.id)].update(newChannel)
    newSetup = {
        'players': {},
        'board': [],
        'gameStatus': "lobby"
    }
    data['games'][str(message.guild.id)][str(message.channel.id)] = newSetup
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data


def addPlayerToGame(message, playerNumber):
    data = readJson()
    newPlayerData = {
        message.author.id: {
            'playerNumber': playerNumber,
            'lives': 3,
            'actions': 0,
            'range': 1,
            'hits': 0,
            'moves': 0
        }
    }
    playersList = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
    # Check if player is already there, then no need to do the rest and write
    for player in playersList:
        if player == str(message.author.id):
            return 'playerAlreadyPresent'
    playersList.update(newPlayerData)
    data['games'][str(message.guild.id)][str(message.channel.id)]['players'] = playersList
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def removePlayerFromGame(message, playerNumber):
    data = readJson()
    playersList = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
    for player in playersList:
        if player == str(message.author.id):
            del playersList[player]
            data['games'][str(message.guild.id)][str(message.channel.id)]['players'] = playersList
            # Here we want to purge data, e.i if there is no one in a lobby clear the json of it reducing overall load
            if len(playersList) == 0:
                del data['games'][str(message.guild.id)][str(message.channel.id)]
                if len(data['games'][str(message.guild.id)]) == 0:
                    del data['games'][str(message.guild.id)]
            with open('Games.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return
    return 'playerNotPresent'


async def killPlayer(message, playerNumber, user):
    data = readJson()
    board = data['games'][str(message.guild.id)][str(message.channel.id)]['board']['data']
    for i in range(len(board)):
        for j in range(len(board[i])):
            if int(playerNumber) == board[i][j]:
                board[i][j] = 0
    saveBoard(message, board)
    await message.channel.send(user.mention + ' is now dead! They have 0\u2665 lives left!')


def getNumberOfPlayersInGame(message):
    """
    This gives back an int of the number of players in a game at a given moment
    :param message: Used to determine which game you want information on
    :return:
    """
    data = readJson()
    numberOfPlayers = 0
    playersList = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
    for player in playersList:
        numberOfPlayers = numberOfPlayers + 1
    return numberOfPlayers


def checkIfGameIsInChannel(message):
    data = readJson()
    try:
        gameState = data['games'][str(message.guild.id)][str(message.channel.id)]['gameStatus']
        return gameState
    except:
        return 'none'


def saveBoard(message, board):
    data = readJson()
    data['games'][str(message.guild.id)][str(message.channel.id)]['board'] = board
    data = __formatBoardJson(str(message.guild.id), (str(message.channel.id)), data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def savePlayer(message, userId, playerInfo):
    data = readJson()
    data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(userId)] = playerInfo
    data = __formatBoardJson(str(message.guild.id), (str(message.channel.id)), data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def saveData(message, data):
    data = __formatBoardJson(str(message.guild.id), (str(message.channel.id)), data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def getBoard(message):
    data = readJson()
    return data['games'][str(message.guild.id)][str(message.channel.id)]['board']['data']


def updateStatus(message):
    data = readJson()
    data['games'][str(message.guild.id)][str(message.channel.id)]['gameStatus'] = 'active'
    numberOfPlayers = getNumberOfPlayersInGame(message)
    playerColors = {'playerColors': {}}
    for player in range(numberOfPlayers):
        rgb_color = cmapy.color('plasma', random.randrange(0, 256, 10), rgb_order=True)
        playerColors['playerColors'][str(player+1)] = NoIndent(rgb_color)
    data['games'][str(message.guild.id)][str(message.channel.id)].update(playerColors)
    data = __formatBoardJson(str(message.guild.id), str(message.channel.id), data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def updatePlayerRange(message, data):
    data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)]['actions'] = (
            int(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                    'actions']) - 1)
    data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)]['range'] = (
            int(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                    'range']) + 1)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)
    return data


def clearAllData():
    data = {}
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)
    print('admin cleared board')


def initialize():
    if os.path.exists('Games.json'):
        print('Games file located, initializing...')
    else:
        print('Games file not located, generating now...')
        with open('Games.json', 'w') as f:
            f.write('{}')

def readJson():
    file = open('Games.json', )
    data = json.load(file)
    file.close()
    return data


def __formatBoardJson(guildID, channelID, data):
    formatData = data['games'][guildID][channelID]['board']
    try:
        formatData = formatData['data']
    except:
        pass

    formatData = {
        'data': [NoIndent(elem) for elem in formatData]
    }
    data['games'][guildID][channelID]['board'] = formatData
    return data
