import json
import logging
import os

import cmapy
import random

from libraries.CustomIndentEncoder import NoIndent, MyEncoder


def createGame(message):
    data = readGamesJson()
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
    data = readGamesJson()
    newPlayerData = {
        message.author.id: {
            'playerNumber': playerNumber,
            'lives': 3,
            'actions': 1,
            'range': 1,
            'hits': 0,
            'moves': 0,
            'votes': 0,
            'remainingVotes': 0
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
    data = readGamesJson()
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
    data = readGamesJson()
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
    data = readGamesJson()
    numberOfPlayers = 0
    playersList = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
    for player in playersList:
        numberOfPlayers = numberOfPlayers + 1
    return numberOfPlayers


def checkIfGameIsInChannel(message):
    data = readGamesJson()
    try:
        gameState = data['games'][str(message.guild.id)][str(message.channel.id)]['gameStatus']
        return gameState
    except:
        return 'none'


def saveBoard(message, board):
    data = readGamesJson()
    data['games'][str(message.guild.id)][str(message.channel.id)]['board'] = board
    data = __formatBoardJson(str(message.guild.id), (str(message.channel.id)), data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def savePlayer(message, userId, playerInfo):
    data = readGamesJson()
    data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(userId)] = playerInfo
    data = __formatBoardJson(str(message.guild.id), (str(message.channel.id)), data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def saveData(data):
    """
    Saves all data that has been manipulated over the original json file
    :param data: The complete dataset with the {games: ...} tag
    """
    for server in data['games']:
        for channel in data['games'][server]:
            data = __formatBoardJson(server, channel, data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def getBoard(message):
    """
    Pass in a message to get the board of that ongoing game
    :param message: The message asking for the respective game board
    """
    data = readGamesJson()
    return data['games'][str(message.guild.id)][str(message.channel.id)]['board']['data']


def updateStatus(message):
    data = readGamesJson()
    data['games'][str(message.guild.id)][str(message.channel.id)]['gameStatus'] = 'active'
    numberOfPlayers = getNumberOfPlayersInGame(message)
    playerColors = {'playerColors': {}}
    for player in range(numberOfPlayers):
        rgb_color = cmapy.color('plasma', random.randrange(0, 256, 10), rgb_order=True)
        playerColors['playerColors'][str(player + 1)] = NoIndent(rgb_color)
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
        logging.warning('Games file not located, generating now...')
        with open('Games.json', 'w') as f:
            f.write('{}')

    if os.path.exists('PlayerData.json'):
        print('Player data file located, initializing...')
    else:
        logging.warning('Player data file not located, generating now...')
        with open('PlayerData.json', 'w') as f:
            f.write('{}')


def readGamesJson():
    """
    Reads all games across all servers and returns an array of all game data
    """
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
