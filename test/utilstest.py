"""
Utility setup for hard JSON values as well as configuring states of testing classes for fixtures
"""
from typing import List


class CodecUtility:
    @staticmethod
    def encodeByteToString(mess):
        return str(bytes(mess, 'utf-8'))


# TODO implement code for utils class
class JsonUtility:
    @staticmethod
    def generateLobby():
        print('Hello World!')

    @staticmethod
    def generateGame():
        print('Hello Again World!')
