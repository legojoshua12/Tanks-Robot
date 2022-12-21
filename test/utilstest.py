"""
Utility setup for hard JSON values as well as configuring states of testing classes for fixtures
"""
import discord.ext.test as dpytest

from src.tanks.libraries import jsonManager


class CodecUtility:
    @staticmethod
    def encodeByteToString(mess):
        return str(bytes(mess, 'utf-8'))


# TODO implement code for utils class
class JsonUtility:
    @staticmethod
    async def set_games_json_lobby(bot, command_prefix):
        guild = bot.guilds[0]
        channel = guild.channels[0]
        await dpytest.member_join(name="Dummy", discrim=1)
        await dpytest.member_join(name="Dummy", discrim=2)
        await dpytest.member_join(name="Dummy", discrim=3)
        await dpytest.member_join(name="Dummy", discrim=4)
        await dpytest.member_join(name="Dummy", discrim=5)
        author = guild.members[2]

        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        mess.author = author

        jsonManager.create_game(mess)
        jsonManager.add_player_to_game(mess, 1)

    @staticmethod
    def generateLobby():
        print('Hello World!')

    @staticmethod
    def generateGame():
        print('Hello Again World!')
