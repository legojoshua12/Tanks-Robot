"""
Utility setup for hard JSON values as well as configuring states of testing classes for fixtures
"""
import json

import discord.ext.test as dpytest

from src.tanks.libraries import messageHandler
from src.tanks.libraries import jsonManager
from src.tanks.libraries.CustomIndentEncoder import MyEncoder


class CodecUtility:
    @staticmethod
    def encodeByteToString(mess):
        return str(bytes(mess, 'utf-8'))


# TODO add definition annotations for documentation
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

    @staticmethod
    def remove_player_actions(guild_id: str, channel_id: str, player_id: str) -> None:
        data = jsonManager.read_games_json()
        data['games'][guild_id][channel_id]['players'][player_id]['actions'] = 0
        with open('Games.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)

    @staticmethod
    def infinite_player_actions(guild_id: str, channel_id: str, player_id: str) -> None:
        data = jsonManager.read_games_json()
        data['games'][guild_id][channel_id]['players'][player_id]['actions'] = 999
        with open('Games.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)

    @staticmethod
    def get_player_range(message, guild_id=None, channel_id=None, player_id=None) -> int:
        data = jsonManager.read_games_json()
        if guild_id is not None and channel_id is not None:
            return int(data['games'][str(guild_id)][str(channel_id)]['players'][str(player_id)]['range'])
        else:
            return int(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                           'range'])

    @staticmethod
    def kill_player(guild_id: str, channel_id: str, player_id: str) -> None:
        data = jsonManager.read_games_json()
        data['games'][guild_id][channel_id]['players'][player_id]['lives'] = 0
        with open('Games.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)

    @staticmethod
    def give_dead_player_vote(guild_id: str, channel_id: str, player_id: str, votes: int = 1) -> None:
        data = jsonManager.read_games_json()
        data['games'][guild_id][channel_id]['players'][player_id]['remainingVotes'] = votes
        with open('Games.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)

    @staticmethod
    def get_game_board(guild_id: str, channel_id: str) -> list[list]:
        data = jsonManager.read_games_json()
        return data['games'][guild_id][channel_id]['board']['data']
