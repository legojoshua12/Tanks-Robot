"""
Utility setup for hard JSON values as well as configuring states of testing classes for fixtures
"""
import discord
import discord.ext.test as dpytest

from src.tanks.libraries import jsonManager


class CodecUtility:
    @staticmethod
    def encodeByteToString(mess):
        return str(bytes(mess, 'utf-8'))


# TODO add definition annotations for documentation
class JsonUtility:
    @staticmethod
    async def set_games_json_lobby(bot, mock_cursor, members_list=None):
        guild = bot.guilds[0]
        channel = guild.channels[0]
        if members_list is None:
            for i in range(5):
                await dpytest.member_join(name="Dummy", discrim=(i + 1))
            members_list = bot.guilds[0].members[2:]
        db_response = await JsonUtility.build_lobby_db_response(str(channel.id), members_list)

        # noinspection PyUnusedLocal
        def execute_side_effect(instruction, args):
            if "player_data.player_data" in instruction:
                response = []
                for member in members_list:
                    response_list: str = f'{{"({str(guild.id)},{str(channel.id)})"}}'
                    response.append((str(member.id), response_list))
                mock_cursor.fetchall.return_value = response
            elif instruction == "SELECT tablename FROM pg_tables WHERE schemaname = 'games'":
                mock_cursor.fetchall.return_value = [(str(guild.id),)]
            else:
                mock_cursor.fetchall.return_value = db_response

        mock_cursor.execute.side_effect = execute_side_effect

    @staticmethod
    async def start_games_json_lobby(bot, mock_cursor):
        guild = bot.guilds[0]
        channel = guild.channels[0]
        insert_query_executed = False
        for i in range(5):
            await dpytest.member_join(name="Dummy", discrim=(i + 1))
        members_list = bot.guilds[0].members[2:]
        db_response = await JsonUtility.build_lobby_db_response(str(channel.id), members_list)

        # noinspection PyUnusedLocal
        def execute_side_effect(instruction, args):
            nonlocal insert_query_executed
            if not insert_query_executed:
                if "INSERT INTO" in instruction:
                    insert_query_executed = True
                mock_cursor.fetchall.return_value = []
            else:
                if instruction == "SELECT tablename FROM pg_tables WHERE schemaname = 'games'":
                    mock_cursor.fetchall.return_value = [(str(guild.id),)]
                else:
                    mock_cursor.fetchall.return_value = db_response

        mock_cursor.execute.side_effect = execute_side_effect

    @staticmethod
    async def start_games_json_active(bot, mock_cursor, members_list=None):
        guild = bot.guilds[0]
        channel = guild.channels[0]
        insert_query_executed = False
        if members_list is None:
            for i in range(5):
                await dpytest.member_join(name="Dummy", discrim=(i + 1))
            members_list = bot.guilds[0].members[2:]
        channel = bot.guilds[0].text_channels[0]
        db_response = await JsonUtility.build_lobby_db_response(str(channel.id), members_list)
        complete_response = await JsonUtility.build_active_game_db_response(str(channel.id), members_list)

        # noinspection PyUnusedLocal
        def execute_side_effect(instruction, args):
            nonlocal insert_query_executed
            if "player_data.player_data" in instruction:
                response = []
                for member in members_list:
                    response_list: str = f'{{"({str(guild.id)},{str(channel.id)})"}}'
                    response.append((str(member.id), response_list))
                mock_cursor.fetchall.return_value = response
            elif instruction == "SELECT tablename FROM pg_tables WHERE schemaname = 'games'":
                mock_cursor.fetchall.return_value = [(str(guild.id),)]
            else:
                if not insert_query_executed:
                    if "SET player_colors =" in instruction:
                        insert_query_executed = True
                        mock_cursor.fetchall.return_value = []
                    mock_cursor.fetchall.return_value = db_response
                else:
                    mock_cursor.fetchall.return_value = complete_response
        mock_cursor.execute.side_effect = execute_side_effect

    @staticmethod
    async def add_many_players(bot, mock_cursor):
        guild = bot.guilds[0]
        channel = guild.channels[0]
        for i in range(21):
            await dpytest.member_join(name="Dummy", discrim=(i + 1))
        members_list = bot.guilds[0].members[2:]
        db_response = await JsonUtility.build_lobby_db_response(str(channel.id), members_list)

        # noinspection PyUnusedLocal
        def execute_side_effect(instruction, args):
            if instruction == "SELECT tablename FROM pg_tables WHERE schemaname = 'games'":
                mock_cursor.fetchall.return_value = [(str(guild.id),)]
            else:
                mock_cursor.fetchall.return_value = db_response

        mock_cursor.execute.side_effect = execute_side_effect

    @staticmethod
    async def start_sample_game(bot, mock_cursor, players_together=True) -> None:
        guild = bot.guilds[0]
        for i in range(5):
            await dpytest.member_join(name="Dummy", discrim=(i + 1))
        members_list = bot.guilds[0].members[2:]
        channel = bot.guilds[0].text_channels[0]
        db_response = await JsonUtility.build_active_game_db_response(str(channel.id), members_list, players_together)

        # noinspection PyUnusedLocal
        def execute_side_effect(instruction, args):
            if "player_data.player_data" in instruction:
                response = []
                for member in members_list:
                    response_list: str = f'{{"({str(guild.id)},{str(channel.id)})"}}'
                    response.append((str(member.id), response_list))
                mock_cursor.fetchall.return_value = response
            elif instruction == "SELECT tablename FROM pg_tables WHERE schemaname = 'games'":
                mock_cursor.fetchall.return_value = [(str(guild.id),)]
            else:
                mock_cursor.fetchall.return_value = db_response

        mock_cursor.execute.side_effect = execute_side_effect

    @staticmethod
    async def build_active_game_db_response(channel_id: str, members_list: list, players_together=True, *args) -> list:
        players_data = {}
        for i in range(len(members_list)):
            players_data[str(members_list[i].id)] = {
                'hits': 0,
                'lives': 3,
                'moves': 1,
                'range': 1,
                'votes': 0,
                'actions': 1,
                'playerNumber': (i + 1),
                'remainingVotes': 0
            }
        for arg in args:
            if type(arg) is not tuple:
                continue
            if len(arg) < 3:
                continue
            if (len(arg) - 1) % 2 != 0:
                continue
            for i in range(int((len(arg) - 1) / 2)):
                players_data[arg[0]][arg[(i * 2) + 1]] = arg[(i * 2) + 2]
        if players_together:
            board = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 5, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 2, 1, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 4, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        else:
            board = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 5, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 2, 0, 0, 1, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 4, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        db_response = [(channel_id,
                        players_data,
                        board,
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
    async def build_lobby_db_response(channel_id: str, members_list: list) -> list:
        players_data = {}
        for i in range(len(members_list)):
            players_data[str(members_list[i].id)] = {
                'hits': 0,
                'lives': 3,
                'moves': 1,
                'range': 1,
                'votes': 0,
                'actions': 1,
                'playerNumber': 1,
                'remainingVotes': 0
            }
        db_response = [(channel_id,
                        players_data,
                        [],
                        'lobby',
                        {})
                       ]
        return db_response

    @staticmethod
    async def start_multiple_sample_games(bot, mock_cursor, players_together=True):
        guild = bot.guilds[0]
        for i in range(5):
            await dpytest.member_join(name="Dummy", discrim=(i + 1))
        members_list = bot.guilds[0].members[2:]
        channel = bot.guilds[0].text_channels[0]
        first_guild_id: str = str(guild.id)
        first_channel_id: str = str(channel.id)
        first_game_data = await JsonUtility.build_active_game_db_response(first_channel_id, members_list, players_together)

        guild = bot.guilds[0]
        http = bot.http
        self = guild  # noqa: F841
        name = "TextChannel_1"
        channel = await http.create_channel(guild, channel_type=discord.ChannelType.text.value)
        assert channel['type'] == discord.ChannelType.text
        assert channel['name'] == name
        channel = bot.guilds[0].channels[2]
        second_guild_id: str = str(guild.id)
        second_channel_id: str = str(channel.id)
        second_game_data = await JsonUtility.build_active_game_db_response(second_channel_id, members_list, True)

        db_response = [first_game_data[0], second_game_data[0]]

        # noinspection PyUnusedLocal
        def execute_side_effect(instruction, args):
            if "player_data.player_data" in instruction:
                response = []
                for member in members_list:
                    response_list: str = f'{{"({first_guild_id},{first_channel_id})","({second_guild_id},{second_channel_id})"}}'
                    response.append((str(member.id), response_list))
                mock_cursor.fetchall.return_value = response
            elif instruction == "SELECT tablename FROM pg_tables WHERE schemaname = 'games'":
                mock_cursor.fetchall.return_value = [(str(guild.id),)]
            else:
                mock_cursor.fetchall.return_value = db_response

        mock_cursor.execute.side_effect = execute_side_effect

    @staticmethod
    async def remove_player_actions(bot, channel_id: str, user_id: str, mock_cursor) -> None:
        guild = bot.guilds[0]
        members_list = bot.guilds[0].members[2:]
        db_response = await JsonUtility.build_active_game_db_response(channel_id,
                                                                      members_list,
                                                                      True,
                                                                      (str(user_id), 'actions', 0))

        # noinspection PyUnusedLocal
        def execute_side_effect(instruction, args):
            if "player_data.player_data" in instruction:
                response = []
                for member in members_list:
                    response_list: str = f'{{"({str(guild.id)},{str(channel_id)})"}}'
                    response.append((str(member.id), response_list))
                mock_cursor.fetchall.return_value = response
            elif instruction == "SELECT tablename FROM pg_tables WHERE schemaname = 'games'":
                mock_cursor.fetchall.return_value = [(str(guild.id),)]
            else:
                mock_cursor.fetchall.return_value = db_response

        mock_cursor.execute.side_effect = execute_side_effect

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
    async def kill_player(bot, channel_id: str, user_id: str, mock_cursor) -> None:
        guild = bot.guilds[0]
        members_list = bot.guilds[0].members[2:]
        db_response = await JsonUtility.build_active_game_db_response(channel_id,
                                                                      members_list,
                                                                      True,
                                                                      (str(user_id), 'actions', 0, 'lives', 0))

        # noinspection PyUnusedLocal
        def execute_side_effect(instruction, args):
            if "player_data.player_data" in instruction:
                response = []
                for member in members_list:
                    response_list: str = f'{{"({str(guild.id)},{str(channel_id)})"}}'
                    response.append((str(member.id), response_list))
                mock_cursor.fetchall.return_value = response
            elif instruction == "SELECT tablename FROM pg_tables WHERE schemaname = 'games'":
                mock_cursor.fetchall.return_value = [(str(guild.id),)]
            else:
                mock_cursor.fetchall.return_value = db_response

        mock_cursor.execute.side_effect = execute_side_effect

    @staticmethod
    async def give_dead_player_vote(bot, channel_id: str, user_id: str, mock_cursor, votes: int = 1) -> None:
        guild = bot.guilds[0]
        members_list = bot.guilds[0].members[2:]
        db_response = await JsonUtility.build_active_game_db_response(channel_id,
                                                                      members_list,
                                                                      True,
                                                                      (
                                                                          str(user_id),
                                                                          'actions', 0,
                                                                          'lives', 0,
                                                                          'remainingVotes', votes))

        # noinspection PyUnusedLocal
        def execute_side_effect(instruction, args):
            if "player_data.player_data" in instruction:
                response = []
                for member in members_list:
                    response_list: str = f'{{"({str(guild.id)},{str(channel_id)})"}}'
                    response.append((str(member.id), response_list))
                mock_cursor.fetchall.return_value = response
            elif instruction == "SELECT tablename FROM pg_tables WHERE schemaname = 'games'":
                mock_cursor.fetchall.return_value = [(str(guild.id),)]
            else:
                mock_cursor.fetchall.return_value = db_response

        mock_cursor.execute.side_effect = execute_side_effect

    @staticmethod
    def get_game_board(guild_id: str, channel_id: str) -> list[list]:
        data = jsonManager.read_games_json()
        return data['games'][guild_id][channel_id]['board']

    @staticmethod
    def get_game_board_example(direction: str) -> list[list]:
        match direction.lower():
            case 'north':
                board = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 5, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 4, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
                return board
            case 'south':
                board = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 5, 0, 0],
                         [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 4, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
                return board
            case 'west':
                board = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 5, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 2, 0, 1, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 4, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
                return board
            case 'east':
                board = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 5, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 2, 0, 0, 0, 1, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 4, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
                return board

    @staticmethod
    async def move_players_away(bot, channel_id: str, mock_cursor) -> None:
        guild = bot.guilds[0]
        members_list = bot.guilds[0].members[2:]
        db_response = await JsonUtility.build_active_game_db_response(channel_id,
                                                                      members_list,
                                                                      False
                                                                      )

        # noinspection PyUnusedLocal
        def execute_side_effect(instruction, args):
            if "player_data.player_data" in instruction:
                response = []
                for member in members_list:
                    response_list: str = f'{{"({str(guild.id)},{str(channel_id)})"}}'
                    response.append((str(member.id), response_list))
                mock_cursor.fetchall.return_value = response
            elif instruction == "SELECT tablename FROM pg_tables WHERE schemaname = 'games'":
                mock_cursor.fetchall.return_value = [(str(guild.id),)]
            else:
                mock_cursor.fetchall.return_value = db_response

        mock_cursor.execute.side_effect = execute_side_effect

    @staticmethod
    async def move_players_together(bot, channel_id: str, mock_cursor) -> None:
        guild = bot.guilds[0]
        members_list = bot.guilds[0].members[2:]
        db_response = await JsonUtility.build_active_game_db_response(channel_id,
                                                                      members_list,
                                                                      True
                                                                      )

        # noinspection PyUnusedLocal
        def execute_side_effect(instruction, args):
            if "player_data.player_data" in instruction:
                response = []
                for member in members_list:
                    response_list: str = f'{{"({str(guild.id)},{str(channel_id)})"}}'
                    response.append((str(member.id), response_list))
                mock_cursor.fetchall.return_value = response
            elif instruction == "SELECT tablename FROM pg_tables WHERE schemaname = 'games'":
                mock_cursor.fetchall.return_value = [(str(guild.id),)]
            else:
                mock_cursor.fetchall.return_value = db_response

        mock_cursor.execute.side_effect = execute_side_effect

    @staticmethod
    async def get_private_channel(bot, member_id: int = 0):
        guild = bot.guilds[0]
        member = guild.members[member_id]
        channel = await member.create_dm()
        return channel
