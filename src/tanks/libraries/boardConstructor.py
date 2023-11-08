"""Builds and returns a board function, as well as the search area function on the board"""
import random

import src.tanks.libraries.configUtils as configUtils


def construct_board_data(players) -> list[list]:
    """
    Returns a 2x2 array which is the board filled with the players
    :param players: The number of players in the game
    """
    board = []
    for i in range(players * 2):
        board.append([])
        for _ in range(players * 2):
            board[i].append(0)
    return board


def populate_board(board, players) -> list[list]:
    """
    Inserts each player on the board in random positions while constructing a new board
    :param board: The partially completed board array
    :param players: The number of players in the game
    """
    for player in range(players):
        while True:
            pos_x = random.randint(1, ((players * 2) - 2))
            pos_y = random.randint(1, ((players * 2) - 2))
            # Check for players in area
            if not __check_for_players_around_area(board, pos_x, pos_y):
                board[pos_x][pos_y] = player + 1
                break
    return board


def __check_for_players_around_area(board, pos_x, pos_y) -> bool:
    """
    Returns a true or false if another player is within range of a given x & y
    from the config distance checker for spawns
    :param board: The player board
    :param pos_x: The x position of the check coordinate
    :param pos_y: The y position of the check coordinate
    """
    saved_value = int(configUtils.read_value('startGame', 'playerSpawnDistance'))
    check_distance = saved_value + (saved_value + 1)
    for i in range(check_distance):
        for j in range(check_distance):
            x_index = -saved_value + i + pos_x
            y_index = -saved_value + j + pos_y
            if board[x_index][y_index] != 0:
                return True
    return False
