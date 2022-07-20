"""
Tests functions that require no use of the discord API and can be run locally
"""
from libraries import boardConstructor as bc
import pytest

def test_boardDataBuilder():
    board = bc.constructBoardData(5)
    assert len(board) == 10

def test_boardPopulator():
    players = [0, 1, 2, 3, 4]
    board = bc.constructBoardData(len(players))
    board = bc.populateBoard(board, 5)
    foundPlayers = []
    for row in board:
        for col in board[row]:
            if board[row][col] is not 0:
                for fp in foundPlayers:
                    if fp == board[row][col]:
                        break
                foundPlayers.append(board[row][col])
                break
    assert len(foundPlayers) == 5
