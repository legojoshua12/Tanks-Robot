"""Builds and returns a board function, as well as the search area function on the board"""
import random

import libraries.configUtils as configUtils


def constructBoardData(players):
    """
    Returns a 2x2 array which is the board filled with the players
    :param players: The number of players in the game
    """
    board = []
    for i in range(players * 2):
        board.append([])
        for j in range(players * 2):
            board[i].append(0)
    return board


def populateBoard(board, players):
    """
    Inserts each player on the board in random positions while constructing a new board
    :param board: The partially completed board array
    :param players: The number of players in the game
    """
    for player in range(players):
        while True:
            posX = random.randint(1, ((players * 2) - 2))
            posY = random.randint(1, ((players * 2) - 2))
            # Check for players in area
            if not __checkForPlayersAroundArea(board, posX, posY):
                board[posX][posY] = player + 1
                break
    return board


def __checkForPlayersAroundArea(board, posX, posY):
    """
    Returns a true or false if another player is within range of a given x & y from the config distance checker for spawns
    :param board: The player board
    :param posX: The x position of the check coordinate
    :param posY: The y position of the check coordinate
    """
    savedValue = int(configUtils.readValue('startGame', 'playerSpawnDistance'))
    checkDistance = savedValue + (savedValue + 1)
    for i in range(checkDistance):
        for j in range(checkDistance):
            xIndex = -savedValue + i + posX
            yIndex = -savedValue + j + posY
            if board[xIndex][yIndex] != 0:
                return True
    return False
