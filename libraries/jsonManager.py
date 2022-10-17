import json
import logging
import os

import cmapy
import random

from libraries.CustomIndentEncoder import NoIndent, MyEncoder


def create_game(message):
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


def save_player_json(message, data):
    players = read_players_json()
    playersData = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
    serverData = (str(message.guild.id), str(message.channel.id))
    for player in playersData:
        if str(player) not in players:
            players[str(player)] = [serverData]
        else:
            old_data = players[str(player)]
            old_data.append(serverData)
            players[str(player)] = old_data
    with open('PlayerData.json', 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=4)
    return


def is_player_in_multiple_games(message):
    player_data = read_players_json()
    for player in player_data:
        if str(player) == str(message.author.id):
            if len(player_data[player]) > 1:
                return True
    return False


def is_player_in_game(message):
    player_data = read_players_json()
    for player in player_data:
        if str(player) == str(message.author.id):
            return True
    return False


def get_player_server_channel_single(message):
    player_data = read_players_json()
    for player in player_data:
        if str(player) == str(message.author.id):
            return str(player_data[player][0][0]), str(player_data[player][0][1])
    return False


def add_player_to_game(message, player_number):
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
    # Check if player is already there, then no need to do the rest and write
    for player in players_list:
        if player == str(message.author.id):
            return 'playerAlreadyPresent'
    players_list.update(new_player_data)
    data['games'][str(message.guild.id)][str(message.channel.id)]['players'] = players_list
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def remove_player_from_game(message, playerNumber):
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
            return
    return 'playerNotPresent'


async def kill_player(message, playerNumber, user):
    data = read_games_json()
    board = data['games'][str(message.guild.id)][str(message.channel.id)]['board']['data']
    for i in range(len(board)):
        for j in range(len(board[i])):
            if int(playerNumber) == board[i][j]:
                board[i][j] = 0
    save_board(message, board)
    await message.channel.send(user.mention + ' is now dead! They have 0\u2665 lives left!')


def get_number_of_players_in_game(message):
    """
    This gives back an int of the number of players in a game at a given moment
    :param message: Used to determine which game you want information on
    :return:
    """
    data = read_games_json()
    number_of_players = 0
    players_list = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
    for _ in players_list:
        number_of_players = number_of_players + 1
    return number_of_players


def check_if_game_is_in_channel(message):
    data = read_games_json()
    try:
        game_state = data['games'][str(message.guild.id)][str(message.channel.id)]['gameStatus']
        return game_state
    except:
        return 'none'


def save_board(message, board, guild_id=None, channel_id=None):
    data = read_games_json()
    if guild_id is not None and channel_id is not None:
        data['games'][guild_id][channel_id]['board'] = board
        data = __format_board_json(guild_id, channel_id, data)
    else:
        data['games'][str(message.guild.id)][str(message.channel.id)]['board'] = board
        data = __format_board_json(str(message.guild.id), (str(message.channel.id)), data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def save_player(message, userId, playerInfo, guild_id=None, channel_id=None):
    data = read_games_json()
    if guild_id is not None and channel_id is not None:
        data['games'][guild_id][channel_id]['players'][str(userId)] = playerInfo
        data = __format_board_json(guild_id, channel_id, data)
    else:
        data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(userId)] = playerInfo
        data = __format_board_json(str(message.guild.id), (str(message.channel.id)), data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def save_data(data):
    """
    Saves all data that has been manipulated over the original json file
    :param data: The complete dataset with the {games: ...} tag
    """
    for server in data['games']:
        for channel in data['games'][server]:
            data = __format_board_json(server, channel, data)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)


def get_board(message, guild_id=None, channel_id=None):
    """
    Pass in a message to get the board of that ongoing game
    :param message: The message asking for the respective game board
    :param guild_id: An optional field for direct access of guild instead of using the message attribute
    :param channel_id: An optional field for direct access of channel instead of using the message attribute
    """
    data = read_games_json()
    if guild_id is not None and channel_id is not None:
        return data['games'][guild_id][channel_id]['board']['data']
    else:
        return data['games'][str(message.guild.id)][str(message.channel.id)]['board']['data']


def update_status(message):
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


def update_player_range(message, data, guild_id=None, channel_id=None):
    if guild_id is not None and channel_id is not None:
        data['games'][guild_id][channel_id]['players'][str(message.author.id)]['actions'] = (
                int(data['games'][guild_id][channel_id]['players'][str(message.author.id)]['actions']) - 1)
        data['games'][guild_id][channel_id]['players'][str(message.author.id)]['range'] = (
                int(data['games'][guild_id][channel_id]['players'][str(message.author.id)]['range']) + 1)
    else:
        data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)]['actions'] = (
                int(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                        'actions']) - 1)
        data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)]['range'] = (
                int(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                        'range']) + 1)
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)
    return data


def clear_all_data():
    data = {}
    with open('Games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=MyEncoder)
    print('admin cleared board')


def initialize():
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


def read_games_json():
    """
    Reads all games across all servers and returns an array of all game data
    """
    file = open('Games.json', )
    data = json.load(file)
    file.close()
    return data


def read_players_json():
    """
    A quick storage of all games a certain player is in for handling dms
    """
    file = open('PlayerData.json', )
    data = json.load(file)
    file.close()
    return data


def __format_board_json(guild_id, channel_id, data):
    format_data = data['games'][guild_id][channel_id]['board']
    try:
        format_data = format_data['data']
    except:
        pass

    format_data = {
        'data': [NoIndent(elem) for elem in format_data]
    }
    data['games'][guild_id][channel_id]['board'] = format_data
    return data
