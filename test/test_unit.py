"""
Tests functions that require no use of the discord API and can be run locally
"""
from libraries import boardConstructor as bc
import pytest

def test_boardDataBuilder():
    board = bc.constructBoardData(5)
    assert len(board) == 10

def test_boardPopulator():
    players = [1, 2, 3, 4, 5]
    board = bc.constructBoardData(len(players))
    board = bc.populateBoard(board, 5)
    foundPlayers = []
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] != 0:
                for fp in foundPlayers:
                    if fp == board[row][col]:
                        break
                foundPlayers.append(board[row][col])
    assert len(foundPlayers) == 5
