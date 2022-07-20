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
    assert len(board) == 10
