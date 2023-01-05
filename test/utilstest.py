"""
Utility setup for hard JSON values as well as configuring states of testing classes for fixtures
"""
import discord.ext.test as dpytest

from src.tanks.libraries import messageHandler
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
        for i in range(5):
            await dpytest.member_join(name="Dummy", discrim=(i+1))
        author = guild.members[2]

        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        mess.author = author

        jsonManager.create_game(mess)
        jsonManager.add_player_to_game(mess, 1)

    @staticmethod
    async def remove_testapp_game(bot, command_prefix):
        guild = bot.guilds[0]
        channel = guild.channels[0]
        await channel.send(f"{command_prefix}leave")

    @staticmethod
    async def add_many_players(bot, command_prefix):
        guild = bot.guilds[0]
        channel = guild.channels[0]
        for i in range(21):
            await dpytest.member_join(name="Dummy", discrim=(i+1))
        author = guild.members[2]

        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        mess.author = author

        jsonManager.create_game(mess)
        jsonManager.add_player_to_game(mess, 1)

    @staticmethod
    async def start_sample_game(bot, command_prefix):
        guild = bot.guilds[0]
        channel = guild.channels[0]
        for i in range(5):
            await dpytest.member_join(name="Dummy", discrim=(i + 1))
        author = guild.members[2]

        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        mess.author = author

        jsonManager.create_game(mess)
        jsonManager.add_player_to_game(mess, 1)

        members_list = bot.guilds[0].members[3:]
        channel = bot.guilds[0].text_channels[0]
        for idx, member in enumerate(members_list):
            await channel.send(f"{command_prefix}join")
            mess = dpytest.get_message()
            mess.author = bot.guilds[0].members[idx + 3]
            await messageHandler.handle_message(mess, bot, command_prefix)
            # Clear out the message queue
            dpytest.get_message()

        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        # Clear out the message queue
        dpytest.get_message()
        dpytest.get_message()
