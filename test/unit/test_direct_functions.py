"""
Tests functions that require no use of the discord API and can be run locally
"""
from src.tanks.libraries import boardConstructor


def test_board_data_builder():
    board = boardConstructor.construct_board_data(5)
    assert len(board) == 10


def test_board_populate():
    players = [1, 2, 3, 4, 5]
    board = boardConstructor.construct_board_data(len(players))
    board = boardConstructor.populate_board(board, 5)
    found_players = []
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] != 0:
                for fp in found_players:
                    if fp == board[row][col]:
                        break
                found_players.append(board[row][col])
    assert len(found_players) == 5
