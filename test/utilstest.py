"""
Utility setup for hard JSON values as well as configuring states of testing classes for fixtures
"""
import json

import discord
import discord.ext.test as dpytest
from unittest.mock import patch, MagicMock

import psycopg2

from src.tanks.libraries import messageHandler
from src.tanks.libraries import jsonManager
from src.tanks.libraries.connectionPool import ConnectionPool


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
            await dpytest.member_join(name="Dummy", discrim=(i + 1))
        author = guild.members[2]

        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        mess.author = author

        jsonManager.create_game(mess)
        jsonManager.add_player_to_game(mess, 1)

    @staticmethod
    async def add_many_players(bot, command_prefix):
        guild = bot.guilds[0]
        channel = guild.channels[0]
        for i in range(21):
            await dpytest.member_join(name="Dummy", discrim=(i + 1))
        author = guild.members[2]

        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        mess.author = author

        jsonManager.create_game(mess)
        jsonManager.add_player_to_game(mess, 1)

    @staticmethod
    async def start_sample_game(bot, mock_cursor) -> None:
        guild = bot.guilds[0]
        for i in range(5):
            await dpytest.member_join(name="Dummy", discrim=(i + 1))
        members_list = bot.guilds[0].members[2:]
        channel = bot.guilds[0].text_channels[0]
        db_response = await JsonUtility.build_active_game_db_response(str(channel.id), members_list)

        def execute_side_effect(instruction, args):
            if instruction == "SELECT tablename FROM pg_tables WHERE schemaname = 'public'":
                mock_cursor.fetchall.return_value = [(str(guild.id),)]
            else:
                mock_cursor.fetchall.return_value = db_response

        mock_cursor.execute.side_effect = execute_side_effect

    @staticmethod
    async def build_active_game_db_response(channel_id: str, members_list: list, actions=1) -> list:
        players_data = {}
        for i in range(len(members_list)):
            players_data[str(members_list[i].id)] = {
                            'hits': 0,
                            'lives': 3,
                            'moves': 1,
                            'range': 1,
                            'votes': 0,
                            'actions': actions,
                            'playerNumber': 1,
                            'remainingVotes': 0
                        }
        db_response = [(channel_id,
                        players_data,
                        [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 5, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 2, 1, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 4, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
                        'active',
                        {'1':
                             [73, 2, 159],
                         '2':
                             [37, 5, 145],
                         '3':
                             [128, 91, 45],
                         '4':
                             [5, 211, 11],
                         '5':
                             [193, 43, 48]
                         })
                       ]
        return db_response

    @staticmethod
    async def start_multiple_sample_games(bot, command_prefix):
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

        # Start second game
        guild = bot.guilds[0]
        http = bot.http
        self = guild  # noqa: F841
        name = "TextChannel_1"
        channel = await http.create_channel(guild, channel_type=discord.ChannelType.text.value)
        assert channel['type'] == discord.ChannelType.text
        assert channel['name'] == name
        channel = bot.guilds[0].channels[2]

        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        mess.author = guild.members[2]
        jsonManager.create_game(mess)
        jsonManager.add_player_to_game(mess, 1)

        members_list = bot.guilds[0].members[3:]
        for idx, member in enumerate(members_list):
            await channel.send(f"{command_prefix}join")
            mess = dpytest.get_message()
            mess.author = bot.guilds[0].members[idx + 3]
            await messageHandler.handle_message(mess, bot, command_prefix)
            dpytest.get_message()

        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        dpytest.get_message()
        dpytest.get_message()

    @staticmethod
    def remove_player_actions(guild_id: str, channel_id: str, player_id: str) -> None:
        data = jsonManager.read_games_json()
        data['games'][guild_id][channel_id]['players'][player_id]['actions'] = 0
        jsonManager.save_data(data['games'][guild_id][channel_id], guild_id, channel_id)

    @staticmethod
    def get_player_range(message, guild_id=None, channel_id=None, player_id=None) -> int:
        data = jsonManager.read_games_json()
        if guild_id is not None and channel_id is not None:
            return int(data['games'][str(guild_id)][str(channel_id)]['players'][str(player_id)]['range'])
        else:
            return int(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                           'range'])

    @staticmethod
    def get_player_stats(message, guild_id=None, channel_id=None, player_id=None) -> dict:
        data = jsonManager.read_games_json()
        if guild_id is not None and channel_id is not None:
            players: list = data['games'][str(guild_id)][str(channel_id)]['players']
            return players[str(player_id)]
        else:
            players: list = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
            return players[str(message.author.id)]

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
        return data['games'][guild_id][channel_id]['board']

    @staticmethod
    def move_players_away(guild_id: str, channel_id: str) -> None:
        board: list[list] = JsonUtility.get_game_board(guild_id, channel_id)
        board_x: int = len(board)
        board_y: int = len(board[0])
        found_single: bool = False
        for x in range(board_x):
            for y in range(board_y):
                if int(board[x][y]) == 1 or int(board[x][y]) == 2:
                    board[x][y] = 0
                    if found_single:
                        break
                    else:
                        found_single = True

        board[0][0] = 1
        board[4][4] = 2
        data = jsonManager.read_games_json()
        data['games'][guild_id][channel_id]['board'] = board
        with open('Games.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)

    @staticmethod
    def move_players_together(guild_id: str, channel_id: str) -> None:
        board: list[list] = JsonUtility.get_game_board(guild_id, channel_id)
        board_x: int = len(board)
        board_y: int = len(board[0])
        found_single: bool = False
        for x in range(board_x):
            for y in range(board_y):
                if int(board[x][y]) == 1 or int(board[x][y]) == 2:
                    board[x][y] = 0
                    if found_single:
                        break
                    else:
                        found_single = True

        board[0][0] = 1
        board[0][1] = 2
        data = jsonManager.read_games_json()
        data['games'][guild_id][channel_id]['board'] = board
        with open('Games.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)

    @staticmethod
    async def get_private_channel(bot, member_id: int = 0):
        guild = bot.guilds[0]
        member = guild.members[member_id]
        channel = await member.create_dm()
        return channel
