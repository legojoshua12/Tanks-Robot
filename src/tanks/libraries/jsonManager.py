import json
import logging
import os

import cmapy
import random

import discord

from src.tanks.libraries.CustomIndentEncoder import NoIndent, MyEncoder


def create_game(message: discord.Message):
    """Creates a game with a lobby state in the given guild and channel of the start command
    :param message: The start command with locational data of the message
    """
    data = read_games_json()
    # These are redundancy checks to ensure no data corruption
    if 'games' not in data:
        data = {'games': {}}
    if str(message.guild.id) not in data['games']:
        new_guild = {
            str(message.guild.id): {}
        }
        data['games'].update(new_guild)
    if str(message.channel.id) not in data['games'][str(message.guild.id)]:
        new_channel = {
            str(message.channel.id): {}
        }
        data['games'][str(message.guild.id)].update(new_channel)
    new_setup = {
        'players': {},
        'board': [],
        'gameStatus': "lobby"
    }
    data['games'][str(message.guild.id)][str(message.channel.id)] = new_setup
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data


def save_player_json(message: discord.Message, data: dict):
    """Appends over old player data if there is an update or cancels writing if that player does not exist
    :param message: The message by the player whose data is being overwritten
    :param data: The new dataset
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


def is_player_in_game(message: discord.Message, user_id=None) -> bool:
    """Finds whether a player is in any game or not
    :param message: The message of the user being located
    :param user_id: (Optional) search by discord uuid instead
    """
    player_data = read_players_json()
    for player in player_data:
        if user_id is not None:
            if str(player) == str(user_id):
                return True
        elif message is not None:
            if str(player) == str(message.author.id):
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


def add_player_to_game(message: discord.Message, player_number: int) -> bool:
    """Adds a player to the game within the lobby
    :param message: The join command message
    :param player_number: The player number order of the player being added
    """
    data = read_games_json()
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
    players_list = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
    # Check if player is already there, then no need to write to memory
    for player in players_list:
        if player == str(message.author.id):
            return True
    players_list.update(new_player_data)
    data['games'][str(message.guild.id)][str(message.channel.id)]['players'] = players_list
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return False


def remove_player_from_game(message: discord.Message) -> bool:
    """Removes a player from the lobby if they don't want to play
    :param message: The leave command message
    :returns: Boolean of whether the player was removed or not
    """
    data = read_games_json()
    players_list = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
    for player in players_list:
        if player == str(message.author.id):
            del players_list[player]
            data['games'][str(message.guild.id)][str(message.channel.id)]['players'] = players_list
            # Here we want to purge data, e.i if there is no one in a lobby clear the json of it reducing overall load
            if len(players_list) == 0:
                del data['games'][str(message.guild.id)][str(message.channel.id)]
                if len(data['games'][str(message.guild.id)]) == 0:
                    del data['games'][str(message.guild.id)]
            with open('Games.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return False
    return True


async def kill_player(message: discord.Message, playerNumber, user) -> None:
    """Removed a player from the board that is being killed, but does not change their lives count
    :param message: The message sent by the player being killed
    :param playerNumber: The game assigned player number of the player being killed
    :param user: The ID of the user being killed
    """
    data = read_games_json()
    board = data['games'][str(message.guild.id)][str(message.channel.id)]['board']['data']
    for i in range(len(board)):
        for j in range(len(board[i])):
            if int(playerNumber) == board[i][j]:
                board[i][j] = 0
    save_board(message, board)
    await message.channel.send(user.mention + ' is now dead! They have 0\u2665 lives left!')


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


def check_if_game_is_in_channel(message: discord.Message) -> str:
    """Returns the game state of a given command specified
    :param message: The message for grabbing the game state
    """
    data = read_games_json()
    try:
        game_state = data['games'][str(message.guild.id)][str(message.channel.id)]['gameStatus']
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
    data = read_games_json()
    if guild_id is not None and channel_id is not None:
        data['games'][guild_id][channel_id]['board'] = board
        data = __format_board_json(guild_id, channel_id, data)
    else:
        data['games'][str(message.guild.id)][str(message.channel.id)]['board'] = board
        data = __format_board_json(str(message.guild.id), (str(message.channel.id)), data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def save_player(message: discord.Message, userId, playerInfo, guild_id=None, channel_id=None) -> None:
    """Writes new player data to an existing game without destroying other game info
    :param message: Identifier for which game is being saved
    :param userId: The player ID for whose data is being stored
    :param playerInfo: The new player data
    :param guild_id: (Optional) Guild used if this is a direct message for game handling
    :param channel_id: (Optional) Channel used if this is a direct message for game handling
    """
    data = read_games_json()
    if guild_id is not None and channel_id is not None:
        data['games'][guild_id][channel_id]['players'][str(userId)] = playerInfo
        data = __format_board_json(guild_id, channel_id, data)
    else:
        data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(userId)] = playerInfo
        data = __format_board_json(str(message.guild.id), (str(message.channel.id)), data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def save_data(data) -> None:
    """Saves all data that has been manipulated over the original json file
    :param data: The complete dataset with the {games: ...} tag
    """
    for server in data['games']:
        for channel in data['games'][server]:
            data = __format_board_json(server, channel, data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def get_board(message: discord.Message, guild_id=None, channel_id=None) -> list:
    """Pass in a message to get the board of that ongoing game
    :param message: The message asking for the respective game board
    :param guild_id: (Optional) Direct access of guild instead of using the message attribute
    :param channel_id: (Optional) Direct access of channel instead of using the message attribute
    """
    data = read_games_json()
    if guild_id is not None and channel_id is not None:
        return data['games'][guild_id][channel_id]['board']['data']
    else:
        return data['games'][str(message.guild.id)][str(message.channel.id)]['board']['data']


def update_status(message: discord.Message) -> None:
    """Changes a game state to active and assigns player colors
    :param message: The message with the command for starting the game
    """
    data = read_games_json()
    data['games'][str(message.guild.id)][str(message.channel.id)]['gameStatus'] = 'active'
    number_of_players = get_number_of_players_in_game(message)
    player_colors = {'playerColors': {}}
    for player in range(number_of_players):
        rgb_color = cmapy.color('plasma', random.randrange(0, 256, 10), rgb_order=True)
        player_colors['playerColors'][str(player + 1)] = NoIndent(rgb_color)
    data['games'][str(message.guild.id)][str(message.channel.id)].update(player_colors)
    data = __format_board_json(str(message.guild.id), str(message.channel.id), data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def update_player_range(message: discord.Message, data, guild_id=None, channel_id=None) -> None:
    """Removes a player action and gives them an extra range in the game specified
    :param message: The message of the player having range increased
    :param data: The original complete games.json data
    :param guild_id: (Optional) Direct access of guild instead of using the message attribute
    :param channel_id: (Optional) Direct access of channel instead of using the message attribute
    """
    if guild_id is not None and channel_id is not None:
        actions: int = int(data['games'][guild_id][channel_id]['players'][str(message.author.id)]['actions']) - 1
        player_range: int = int(data['games'][guild_id][channel_id]['players'][str(message.author.id)]['range']) + 1
        data['games'][guild_id][channel_id]['players'][str(message.author.id)]['actions'] = actions
        data['games'][guild_id][channel_id]['players'][str(message.author.id)]['range'] = player_range
    else:
        guild: str = str(message.guild.id)
        channel: str = str(message.channel.id)
        actions: int = int(data['games'][guild][channel]['players'][str(message.author.id)]['actions']) - 1
        player_range: int = int(data['games'][guild][channel]['players'][str(message.author.id)]['range']) + 1
        data['games'][guild][channel]['players'][str(message.author.id)]['actions'] = actions
        data['games'][guild][channel]['players'][str(message.author.id)]['range'] = player_range
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)
    return data


def clear_all_data() -> None:
    """Deletes all data in the games json"""
    data = {}
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)
    print('admin cleared board')


def initialize() -> None:
    """Locates and verifies there is both necessary json files and will create them if they don't exist"""
    if os.path.exists('Games.json'):
        print('Games file located, initializing...')
    else:
        logging.warning('Games file not located, generating now...')
        with open('Games.json', 'w') as f:
            f.write('{}')

    if os.path.exists('PlayerData.json'):
        print('Player data file located, initializing...')
    else:
        logging.warning('Player data file not located, generating now...')
        with open('PlayerData.json', 'w') as f:
            f.write('{}')


def read_games_json() -> dict:
    """Reads all games across all servers and returns an array of all game data
    :return: Every game's data ever
    """
    file = open('Games.json', )
    data = json.load(file)
    file.close()
    return data


def read_players_json() -> dict:
    """A quick storage of all games a certain player is in for handling dms
    :return: Every player's data ever"""
    file = open('PlayerData.json', )
    data: dict = json.load(file)
    file.close()
    return data


def __format_board_json(guild_id, channel_id, data) -> dict:
    format_data = data['games'][guild_id][channel_id]['board']
    try:
        format_data = format_data['data']
    except TypeError:
        pass

    format_data = {
        'data': [NoIndent(elem) for elem in format_data]
    }
    data['games'][guild_id][channel_id]['board'] = format_data
    return data
