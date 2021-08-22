import random

import configUtils


def constructBoardData(players):
    board = []
    for i in range(players*2):
        board.append([])
        for j in range(players*2):
            board[i].append(0)
    return board


def populateBoard(board, players):
    for player in range(players):
        while True:
            posX = random.randint(1, ((players * 2) - 2))
            posY = random.randint(1, ((players * 2) - 2))
            # Check for players in area
            if not __checkForPlayersAroundArea(board, posX, posY):
                board[posX][posY] = player+1
                break
    return board

def __checkForPlayersAroundArea(board, posX, posY):
    savedValue = int(configUtils.readValue('startGame', 'playerSpawnDistance'))
    checkDistance = savedValue + (savedValue+1)
    for i in range(checkDistance):
        for j in range(checkDistance):
            xIndex = -savedValue+i+posX
            yIndex = -savedValue+j+posY
            if board[xIndex][yIndex] != 0:
                return True
    return False
