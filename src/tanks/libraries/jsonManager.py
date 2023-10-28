"""General class for reading and writing data to json files with correct formatting and data protection"""
import json
import logging

import cmapy
import random

from src.tanks.libraries.connectionPool import ConnectionPool, query_database

import discord
import psycopg2


def create_game(message: discord.Message) -> dict:
    connection_pool = ConnectionPool.get_instance()
    connection = connection_pool.getconn()

    guild_id = str(message.guild.id)
    channel_id = str(message.channel.id)
    table_name = f"{guild_id}"

    create_table_query = f'''
        CREATE TABLE IF NOT EXISTS games."{table_name}" (
            channel_id TEXT PRIMARY KEY NOT NULL,
            players JSONB,
            board JSONB,
            game_status TEXT,
            player_colors JSONB
        )
    '''
    try:
        query_database(connection, create_table_query)
    except psycopg2.Error as _:
        pass
    insert_query = f'''
        INSERT INTO games."{table_name}" (channel_id, players, board, game_status, player_colors)
        VALUES (%s, %s, %s, %s, %s)
    '''

    players = json.dumps({})
    board = json.dumps([])
    game_status = "lobby"
    player_colors = json.dumps({})

    try:
        query_database(connection, insert_query, channel_id, players, board, game_status, player_colors)
    except psycopg2.Error as _:
        pass
    finally:
        connection_pool.putconn(connection)
    return read_games_json()


def save_player_json(message: discord.Message, data: dict):
    """Appends over old player data if there is an update or cancels writing if that player does not exist
    :param message: The message by the player whose data is being overwritten
    :param data: The new complete dataset with {'games': ...}
    """
    players: dict = read_players_json()
    players_data: dict = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
    server_data: tuple[str, str] = (str(message.guild.id), str(message.channel.id))
    for player in players_data:
        if str(player) not in players:
            players[str(player)] = [server_data]
        else:
            old_data = players[str(player)]
            old_data.append(server_data)
            players[str(player)] = old_data
    with open('PlayerData.json', 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=4)
    return


def remove_player_json(player_id: str, guild_id: str, channel_id: str) -> None:
    """Removes a specific game from the player data json
    :param player_id: String player id
    :param guild_id: String guild id
    :param channel_id: String channel id
    """
    players: dict = read_players_json()
    players[player_id].remove([guild_id, channel_id])
    with open('PlayerData.json', 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=4)
    return


def is_player_in_multiple_games(message: discord.Message, user_id=None) -> bool:
    """Checks for if a player is in multiple games or not
    :param message: The message of the user being checked
    :param user_id: (Optional) Check by discord uuid instead
    """
    player_data = read_players_json()
    for player in player_data:
        if user_id is not None:
            if str(player) == str(user_id):
                if len(player_data[player]) > 1:
                    return True
        elif message is not None:
            if str(player) == str(message.author.id):
                if len(player_data[player]) > 1:
                    return True
    return False


def is_player_in_game(message: discord.Message = None, user_id=None) -> bool:
    """Finds whether a player is in any game or not
    :param message: (Optional) The message of the user being located
    :param user_id: (Optional) search by discord uuid instead
    """
    player_data = read_players_json()
    for player in player_data:
        if user_id is not None:
            if str(player) == str(user_id):
                if len(player_data[player]) > 0:
                    return True
        elif message is not None:
            if str(player) == str(message.author.id):
                if len(player_data[player]) > 0:
                    return True
    return False


def get_player_server_channel_single(message: discord.Message, user_id=None) -> tuple[str, str] or bool:
    """Attempts to provide the player guild and channel id for an assigned game from direct message context
    :param message: The message of the player being checked
    :param user_id: (Optional) Search by discord uuid instead
    """
    player_data = read_players_json()
    for player in player_data:
        if user_id is not None:
            if str(player) == str(user_id):
                return str(player_data[player][0][0]), str(player_data[player][0][1])
        elif message is not None:
            if str(player) == str(message.author.id):
                return str(player_data[player][0][0]), str(player_data[player][0][1])
    return False


def get_player_server_channels(message: discord.Message, user_id=None) -> list[tuple[str, str]]:
    """Attempts to provide the player guild and channel id for an assigned game from direct message context
    :param message: The message of the player being checked
    :param user_id: (Optional) Search by discord uuid instead
    """
    player_data = read_players_json()
    located_servers = []
    if user_id is not None:
        located_servers = player_data[str(message.author.id)]
    if message is not None:
        located_servers = player_data[str(message.author.id)]
    servers = []
    for entry in located_servers:
        servers.append(tuple(entry))
    return servers


def add_player_to_game(message: discord.Message, player_number: int) -> bool:
    """Adds a player to the game within the lobby
    :param message: The join command message
    :param player_number: The player number order of the player being added
    """
    data = read_games_json()
    connection_pool = ConnectionPool.get_instance()
    connection = connection_pool.getconn()

    guild_id = str(message.guild.id)
    channel_id = str(message.channel.id)
    table_name = f"{guild_id}"

    new_player_data = {
        message.author.id: {
            'playerNumber': player_number,
            'lives': 3,
            'actions': 1,
            'range': 1,
            'hits': 0,
            'moves': 0,
            'votes': 0,
            'remainingVotes': 0
        }
    }
    players_list = data['games'][guild_id][channel_id]['players']
    # Check if player is already there, then no need to write to the database
    for player in players_list:
        if player == str(message.author.id):
            return True

    players_list.update(new_player_data)
    players = json.dumps(players_list)

    update_query = f'UPDATE games."{table_name}" SET players = %s WHERE channel_id = %s'
    try:
        query_database(connection, update_query, players, channel_id)
    except psycopg2.Error as _:
        pass
    finally:
        connection_pool.putconn(connection)
    return False


def remove_player_from_game(message: discord.Message) -> bool:
    """Removes a player from the lobby if they don't want to play
    :param message: The leave command message
    :returns: Boolean of whether the player was removed or not
    """
    data = read_games_json()
    connection_pool = ConnectionPool.get_instance()
    connection = connection_pool.getconn()

    guild_id = str(message.guild.id)
    channel_id = str(message.channel.id)
    table_name = f"{guild_id}"

    players_list = data['games'][guild_id][channel_id]['players']
    try:
        for player in players_list:
            if player == str(message.author.id):
                del players_list[player]
                # Here we want to purge data, e.i if there is no one in a lobby clear the json of it reducing load
                if len(players_list) == 0:
                    del data['games'][guild_id][channel_id]
                    if len(data['games'][guild_id]) == 0:
                        delete_query = f'DROP TABLE games."{table_name}"'
                        query_database(connection, delete_query)
                    else:
                        delete_query = f'DELETE FROM games."{table_name}" WHERE channel_id = %s'
                        query_database(connection, delete_query, channel_id)
                else:
                    players = json.dumps(players_list)
                    update_query = f'UPDATE games."{table_name}" SET players = %s WHERE channel_id = %s'
                    query_database(connection, update_query, players, channel_id)
                return True
    except psycopg2.Error as _:
        pass
    finally:
        connection_pool.putconn(connection)
    return False


def kill_player(playerNumber, message: discord.Message = None, guild_id: str = None, channel_id: str = None) -> None:
    """Removed a player from the board that is being killed, but does not change their lives count
    :param message: The message sent by the player being killed
    :param guild_id: The guild id of the game of the player being killed
    :param channel_id: The channel id of the game of the dead player
    :param playerNumber: Killed player ID
    """
    data = read_games_json()
    if guild_id is None and channel_id is None:
        board = data['games'][str(message.guild.id)][str(message.channel.id)]['board']
    else:
        board = data['games'][str(guild_id)][str(channel_id)]['board']
    for i in range(len(board)):
        for j in range(len(board[i])):
            if int(playerNumber) == board[i][j]:
                board[i][j] = 0
    save_board(message, board, guild_id, channel_id)


def check_win(board_data: list[list[int]]) -> bool:
    """Validates whether there is 1 player left on the map or not
    :param board_data: The board of the game
    :return: True if there is only 1 person left that has won the game, otherwise false
    """
    found_players: int = 0
    for i in range(len(board_data)):
        for j, value in enumerate(board_data[i]):
            if value != 0:
                found_players += 1
    return True if found_players < 2 else False


def mark_game_win(guild_id: str, channel_id: str) -> None:
    data = read_games_json()
    connection_pool = ConnectionPool.get_instance()
    connection = connection_pool.getconn()
    table_name = f"{guild_id}"

    for player in data['games'][guild_id][channel_id]['players']:
        remove_player_json(str(player), guild_id, channel_id)

    data['games'][guild_id][channel_id]['gameStatus'] = "completed"
    update_query = f'''
            UPDATE games."{table_name}" SET game_status = %s WHERE channel_id = %s
            '''
    try:
        query_database(connection, update_query, "completed", channel_id)
    except psycopg2.Error as _:
        pass
    finally:
        connection_pool.putconn(connection)


def get_number_of_players_in_game(message: discord.Message) -> int:
    """This gives back an int of the number of players in a game at a given moment
    :param message: Used to determine which game you want information on
    """
    data = read_games_json()
    number_of_players = 0
    players_list = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
    for _ in players_list:
        number_of_players = number_of_players + 1
    return number_of_players


def check_if_game_is_in_channel(message: discord.Message = None, guild_id=None, channel_id=None) -> str:
    """Returns the game state of a given command specified
    :param message: The message for grabbing the game state
    :param guild_id: The guild id instead of using message
    :param channel_id: The channel id instead of using message
    """
    data = read_games_json()
    try:
        if guild_id is None and channel_id is None:
            game_state = data['games'][str(message.guild.id)][str(message.channel.id)]['gameStatus']
        else:
            game_state = data['games'][str(guild_id)][str(channel_id)]['gameStatus']
        return game_state
    except TypeError:
        return 'none'
    except KeyError:
        return 'none'


def save_board(message: discord.Message, board: list[list], guild_id=None, channel_id=None):
    """Saves a new board over old game data
    :param message: The message for the channel and guild the board is being saved over
    :param board: The new board data
    :param guild_id: (Optional) Guild used if this is a direct message for game handling
    :param channel_id: (Optional) Channel used if this is a direct message for game handling
    """
    connection_pool = ConnectionPool.get_instance()
    connection = connection_pool.getconn()

    if guild_id is None and channel_id is None:
        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)

    table_name = f"{guild_id}"
    board_string = json.dumps(board)
    update_query = f'UPDATE games."{table_name}" SET board = %s WHERE channel_id = %s'
    try:
        query_database(connection, update_query, board_string, channel_id)
    except psycopg2.Error as _:
        pass
    finally:
        connection_pool.putconn(connection)


def save_player(message: discord.Message, userId, playerInfo, guild_id=None, channel_id=None) -> None:
    """Writes new player data to an existing game without destroying other game info
    :param message: Identifier for which game is being saved
    :param userId: The player ID for whose data is being stored
    :param playerInfo: The new player data
    :param guild_id: (Optional) Guild used if this is a direct message for game handling
    :param channel_id: (Optional) Channel used if this is a direct message for game handling
    """
    data = read_games_json()
    connection_pool = ConnectionPool.get_instance()
    connection = connection_pool.getconn()

    if guild_id is None and channel_id is None:
        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)

    player_data = data['games'][guild_id][channel_id]['players']
    player_data[str(userId)] = playerInfo
    table_name = f"{guild_id}"
    player_data_string = json.dumps(player_data)
    update_query = f'UPDATE games."{table_name}" SET players = %s WHERE channel_id = %s'
    try:
        query_database(connection, update_query, player_data_string, channel_id)
    except psycopg2.Error as _:
        pass
    finally:
        connection_pool.putconn(connection)


def save_data(data: dict, guild_id: str, channel_id: str) -> None:
    """Saves all data that has been manipulated over the original json file
    :param data: Complete dataset for a given game, each tag of the game is included
    and nothing else about any other game present in the database
    :param guild_id: Guild id in string form
    :param channel_id: Channel id in string form
    """
    connection_pool = ConnectionPool.get_instance()
    connection = connection_pool.getconn()
    table_name = f"{guild_id}"

    players = json.dumps(data['players'])
    board = json.dumps(data['board'])
    game_status = json.dumps(data['gameStatus'])
    player_colors = json.dumps(data['playerColors'])
    update_query = f'''
        UPDATE games."{table_name}" SET players = %s, board = %s, game_status = %s, player_colors = %s 
        WHERE channel_id = %s
        '''
    try:
        query_database(connection, update_query, players, board, game_status, player_colors, channel_id)
    except psycopg2.Error as _:
        pass
    finally:
        connection_pool.putconn(connection)


def get_board(message: discord.Message, guild_id=None, channel_id=None) -> list:
    """Pass in a message to get the board of that ongoing game
    :param message: The message asking for the respective game board
    :param guild_id: (Optional) Direct access of guild instead of using the message attribute
    :param channel_id: (Optional) Direct access of channel instead of using the message attribute
    """
    data = read_games_json()
    if guild_id is not None and channel_id is not None:
        return data['games'][guild_id][channel_id]['board']
    else:
        return data['games'][str(message.guild.id)][str(message.channel.id)]['board']


def update_status(message: discord.Message) -> None:
    """Changes a game state to active and assigns player colors
    :param message: The message with the command for starting the game
    """
    connection_pool = ConnectionPool.get_instance()
    connection = connection_pool.getconn()

    guild_id = str(int(message.guild.id))
    channel_id = str(int(message.channel.id))
    table_name = f"{guild_id}"

    number_of_players = get_number_of_players_in_game(message)
    player_colors = {}
    for player in range(number_of_players):
        rgb_color = cmapy.color('plasma', random.randrange(0, 256, 10), rgb_order=True)
        player_colors[str(player + 1)] = rgb_color
    player_colors_string = json.dumps(player_colors)

    update_game_status_query = f'UPDATE games."{table_name}" SET game_status = %s WHERE channel_id = %s'
    update_player_colors_query = f'UPDATE games."{table_name}" SET player_colors = %s WHERE channel_id = %s'

    try:
        query_database(connection, update_game_status_query, "active", channel_id)
        query_database(connection, update_player_colors_query, player_colors_string, channel_id)
    except psycopg2.Error as _:
        pass
    finally:
        connection_pool.putconn(connection)


def update_player_range(message: discord.Message, data, guild_id=None, channel_id=None) -> dict:
    """Removes a player action and gives them an extra range in the game specified
    :param message: The message of the player having range increased
    :param data: The original complete dataset of all games
    :param guild_id: (Optional) Direct access of guild instead of using the message attribute
    :param channel_id: (Optional) Direct access of channel instead of using the message attribute
    """
    connection_pool = ConnectionPool.get_instance()
    connection = connection_pool.getconn()
    if guild_id is None and channel_id is None:
        guild_id: str = str(message.guild.id)
        channel_id: str = str(message.channel.id)

    table_name = f"{guild_id}"
    actions: int = int(data['games'][guild_id][channel_id]['players'][str(message.author.id)]['actions']) - 1
    player_range: int = int(data['games'][guild_id][channel_id]['players'][str(message.author.id)]['range']) + 1
    data['games'][guild_id][channel_id]['players'][str(message.author.id)]['actions'] = actions
    data['games'][guild_id][channel_id]['players'][str(message.author.id)]['range'] = player_range
    players_string = json.dumps(data['games'][guild_id][channel_id]['players'])

    update_game_status_query = f'UPDATE games."{table_name}" SET players = %s WHERE channel_id = %s'
    try:
        query_database(connection, update_game_status_query, players_string, channel_id)
    except psycopg2.Error as _:
        pass
    finally:
        connection_pool.putconn(connection)
    return data


def initialize() -> None:
    """Initializes a database pool object in memory and establishes the correct amount of connections. A check will
    also be run to verify that the database does provide enough connections and proper queries can be made.
    Any exceptions will cause a program exit until a valid database connection can be established."""
    logging.info('Initializing database connection pool...')
    try:
        connection_pool = ConnectionPool.get_instance()
        connection = connection_pool.getconn()
        verifier = "SELECT NOW()"
        response = query_database(connection, verifier)
        if response is None:
            logging.error('Unable to query database error, no response received...')
            logging.critical('Uncaught exception, exiting now...')
            exit()
        if type(response) is list:
            if len(response) == 0:
                logging.error('Unable to query database error, no response received...')
                logging.critical('Uncaught exception, exiting now...')
                exit()
        logging.info('Database connection established successfully')
        logging.info('Initializing schemas...')
        create_game_schema = 'CREATE SCHEMA IF NOT EXISTS games'
        create_player_data_schema = 'CREATE SCHEMA IF NOT EXISTS player_data'
        query_database(connection, create_game_schema)
        query_database(connection, create_player_data_schema)
        create_player_data_table = f'''
                CREATE TABLE IF NOT EXISTS player_data.player_data (
                    user_id TEXT PRIMARY KEY NOT NULL,
                    guild_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL
                )
            '''
        query_database(connection, create_player_data_table)
        logging.info('Database Initialization Complete')
    except psycopg2.Error as e:
        logging.error(f"Unable to connect to the database: {e}")
        logging.critical('Uncaught exception, exiting now...')
        exit()


def read_games_json() -> dict:
    """Reads all games across all servers and returns an array of all game data
    :return: Every game's data ever
    """
    data = {'games': {}}
    connection_pool = ConnectionPool.get_instance()
    connection = connection_pool.getconn()
    statement: str = "SELECT tablename FROM pg_tables WHERE schemaname = 'games'"
    try:
        table_names = query_database(connection, statement)
        for idx, entry in enumerate(table_names):
            table_name: str = str(entry[0])
            val = query_database(connection, f'SELECT * FROM games."{table_name}"')
            for i in range(len(val)):
                if table_name not in data['games']:
                    new_guild = {
                        table_name: {}
                    }
                    data['games'].update(new_guild)
                if str(val[i][0]) not in data['games'][table_name]:
                    new_channel = {
                        str(val[i][0]): {}
                    }
                    data['games'][str(table_name)].update(new_channel)
                new_setup = {
                    'players': dict(val[i][1]),
                    'board': list(val[i][2]),
                    'gameStatus': str(val[i][3]),
                    'playerColors': dict(val[i][4])
                }
                data['games'][table_name][str(val[i][0])] = new_setup
    except psycopg2.Error as _:
        pass
    finally:
        connection_pool.putconn(connection)
    return data


def read_players_json() -> dict:
    """A quick storage of all games a certain player is in for handling dms
    :return: Every player's data ever"""
    data = {}
    connection_pool = ConnectionPool.get_instance()
    connection = connection_pool.getconn()
    try:
        val = query_database(connection, f'SELECT * FROM player_data.player_data')
        for i in range(len(val)):
            if str(val[i][0]) not in data:
                new_player_data = [[
                    str(val[i][1]), str(val[i][2])
                ]]
                data[str(val[i][0])].update(new_player_data)
            else:
                old_list = data[str(val[i][0])]
                old_list.insert(0, [])
    except psycopg2.Error as _:
        pass
    finally:
        connection_pool.putconn(connection)
    return data
