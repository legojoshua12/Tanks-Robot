"""These are the commands that do actions given to the robot, AKA do the command shoot or do the command move"""
import io
import random

import discord

import libraries.configUtils as configUtils
import libraries.jsonManager as jsonManager
import libraries.renderPipeline as renderPipeline


async def direct_message_commands(message, command):
    embed_color = int('0x' + ("%06x" % random.randint(0, 0xFFFFFF)), 0)
    if command.startswith(configUtils.read_value('botSettings', 'botCommandPrefix')):
        command = command[2:].lower()
    else:
        command = command.lower()
    if command == 'help':
        embed = discord.Embed(title="Command Reference", description="Here is a list of bot commands for your "
                                                                     "reference! Simply type one of these to get "
                                                                     "started.",
                              color=embed_color)
        embed.add_field(name="help", value="Gives a list of commands", inline=False)
        embed.add_field(name="rules", value="Gives the game rules and how to play", inline=False)
        await message.channel.send(embed=embed)
    elif command == 'rules':
        emoji = '\U0001F52B'
        embed = discord.Embed(title="Rules", description=f"This is the rules on how to play tanks! {emoji}",
                              color=embed_color)
        embed.add_field(name="1. You use actions to do things", value="Actions are the the core of the game, "
                                                                      "they can be used to move, shoot, or "
                                                                      "increase your tank's range.",
                        inline=False)
        embed.add_field(name="2. You receive 1 action a day", value="Every player in the game receives 1 "
                                                                    "action a day at 12pm (noon) PST",
                        inline=False)
        embed.add_field(name="3. Dead players can give an extra action",
                        value="All dead players have the option to vote once a day. If a living player "
                              "receives 3+ votes, they will get 2 actions instead of 1 at 12pm.",
                        inline=False)
        embed.add_field(name="4. You have health",
                        value="Each player has a total of 3 health points. If you lose a health point, "
                              "it cannot be regenerated and the damage is permanent.",
                        inline=False)
        embed.add_field(name="5. Actions can be given",
                        value="You can bribe other players to give you actions. You are not bound by the "
                              "actions you receive each day and can get more from other players by asking them.",
                        inline=False)
        embed.add_field(name="6. You use actions whenever you want",
                        value="Using your actions is not time bound. You may chose to use them at any point in "
                              "the day should you still be alive and have the available actions.",
                        inline=False)
        embed.add_field(name="7. There are 5-20 players",
                        value="The game requires at least 5 unique players to get started and will work with up to "
                              "a maximum of 20 people.",
                        inline=False)
        embed.add_field(name="8. Last person standing wins!",
                        value="If you have the ability to make it to being the last person alive, you will "
                              "win! Congratulations if you manage to make it here!",
                        inline=False)
        await message.channel.send(embed=embed)
    elif command == 'dm':
        await message.author.send("I'm already here talking to you! Use `help` to get a list of commands.")
    else:
        await message.channel.send(message.author.mention + ' Unknown command. Please use `help` to view a '
                                                            'list of commands and options.')


async def public_commands_no_game(message, command):
    embed_color = int('0x' + ("%06x" % random.randint(0, 0xFFFFFF)), 0)
    if command == 'help':
        command_prefix = configUtils.read_value('botSettings', 'botCommandPrefix')
        embed = discord.Embed(title="Command Reference", description="Here is a list of bot commands for your "
                                                                     "reference! All commands may be done in "
                                                                     "private as well using a direct message.",
                              color=embed_color)
        embed.add_field(name=f"{command_prefix}help", value="Gives a list of commands", inline=False)
        embed.add_field(name=f"{command_prefix}rules", value="Gives the game rules and how to play", inline=False)
        embed.add_field(name=f"{command_prefix}dm", value="Sends a direct message for privacy", inline=False)
        embed.add_field(name=f"{command_prefix}start", value="Begins game setup lobby in this channel", inline=False)
        await message.channel.send(embed=embed)
    elif command == 'rules':
        embed = make_rules_embed(embed_color)
        await message.channel.send(embed=embed)
    elif command == 'dm':
        await send_dm_starter(message)
    elif command == 'start':
        await message.channel.send('Starting a game...')
        return 'startCommandReceived'
    else:
        await message.channel.send(message.author.mention + ' Unknown command. Please use `*/help` to view a '
                                                            'list of commands and options.')


async def send_dm_starter(message):
    """
    Sends a direct message to the person who sent the command with a hello from the robot
    :param message: The message of the command that was sent
    """
    letter_emoji = '\U00002709'
    wave_emoji = '\U0001F44B'
    await message.channel.send(message.author.mention + f' I just sent you a private message! {letter_emoji}')
    await message.author.send(f"Hey there! {wave_emoji} How can I help you? Use `help` to get started!")


async def public_commands_lobby(message, command):
    if command == 'help':
        return command
    elif command == 'players':
        return command
    elif command == 'dm':
        return command
    elif command == 'join':
        return command
    elif command == 'leave':
        return command
    elif command == 'start':
        return command
    # Rest of these are for concurrency’s sake with the rest of the bot commands
    else:
        await message.channel.send(message.author.mention + ' Unknown command. Please use `*/help` to view a '
                                                            'list of commands and options.')


async def send_lobby_help_menu(message):
    command_prefix = configUtils.read_value('botSettings', 'botCommandPrefix')
    embed_color = int('0x' + ("%06x" % random.randint(0, 0xFFFFFF)), 0)
    embed = discord.Embed(title="Welcome to the game of Tanks!",
                          description="For constructing a game, add players as shown below and start "
                                      "it when you are ready to begin a game",
                          color=embed_color)
    embed.add_field(name=f'{command_prefix}join',
                    value=f'Each player who wishes to play can do a `{command_prefix}join` to join this '
                          f'new game', inline=False)
    embed.add_field(name=f'{command_prefix}leave',
                    value='That player will be removed from the game and not be in once started. If '
                          'the player who created this lobby leaves then the lobby is ended and anyone '
                          'can recreate a game', inline=False)
    embed.add_field(name=f'{command_prefix}players',
                    value='Lists all players currently in queue to play', inline=False)
    embed.add_field(name=f'{command_prefix}help',
                    value='Shows this menu again', inline=False)
    embed.add_field(name=f'{command_prefix}dm',
                    value="Sends a direct message for privacy", inline=False)
    embed.add_field(name=f'{command_prefix}start',
                    value='Will start the game if enough players have joined', inline=False)
    await message.channel.send(embed=embed)


async def public_commands_game(message, command):
    data = jsonManager.read_games_json()
    try:
        data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)]
    except KeyError:
        await message.channel.send('You are not playing in this game ' + message.author.mention + '!')
        return
    command_prefix = configUtils.read_value('botSettings', 'botCommandPrefix')
    embed_color = int('0x' + ("%06x" % random.randint(0, 0xFFFFFF)), 0)
    if command == 'help':
        await active_game_help_embed(message, embed_color, command_prefix)
    elif command == 'rules':
        embed = make_rules_embed(embed_color)
        await message.channel.send(embed=embed)
    elif command == 'board':
        return command
    elif command == 'players':
        return command
    elif command == 'dm':
        return command
    elif command == 'increase range':
        if str(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                   'lives']) == str(0):
            await message.channel.send('You are dead and have no more lives ' + message.author.mention + '.')
            return
        else:
            return command
    elif command[0:5] == 'move ' or (len(command) == 4 and command == 'move'):
        if str(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                   'lives']) == str(0):
            await message.channel.send('You are dead and have no more lives ' + message.author.mention + '.')
            return
        else:
            return 'move'
    elif command[0:6] == 'shoot ' or (len(command) == 5 and command == 'shoot'):
        if str(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                   'lives']) == str(0):
            await message.channel.send('You are dead and have no more lives ' + message.author.mention + '.')
            return
        else:
            return 'shoot'
    elif command[0:4] == 'vote':
        if len(command) == 4:
            if str(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                       'lives']) == str(0):
                await message.channel.send('Please specify a player to vote for '
                                           + message.author.mention + '.')
                return
            else:
                await message.channel.send('Only players with no more lives may vote on an extra action for a player '
                                           + message.author.mention + '.')
                return
        else:
            if command[0:5] == 'vote ':
                if str(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                           'lives']) == str(0):
                    return 'vote'
                else:
                    await message.channel.send(
                        'Only players with no more lives may vote on an extra action for a player '
                        + message.author.mention + '.')
                    return
            else:
                # TODO pass to next if
                pass
    elif command[0:4] == 'send':
        return 'send'
    else:
        await message.channel.send(message.author.mention + ' Unknown command. Please use `*/help` to view a '
                                                            'list of commands and options.')


async def active_game_help_embed(message, embed_color, command_prefix):
    embed = discord.Embed(title="Command Reference", description="Here is a list of bot commands for your "
                                                                 "reference! Simply type one of these to get "
                                                                 "started.",
                          color=embed_color)
    embed.add_field(name=f'{command_prefix}help', value="Gives a list of commands", inline=False)
    embed.add_field(name=f'{command_prefix}rules', value="Gives the game rules and how to play", inline=False)
    embed.add_field(name=f'{command_prefix}dm', value="Sends a direct message for privacy", inline=False)
    embed.add_field(name=f'{command_prefix}board', value="Shows the board of the current game", inline=False)
    embed.add_field(name=f'{command_prefix}players', value="Shows the players of the game and their accompanying "
                                                           "statistics", inline=False)
    embed.add_field(name=f'{command_prefix}increase range', value="Spends 1 action point to increase your range",
                    inline=False)
    embed.add_field(name=f'{command_prefix}move [direction]',
                    value=f'Spends 1 action point to 1 space north, south, west, or east '
                          f'(Example: {command_prefix}move west)',
                    inline=False)
    embed.add_field(name=f'{command_prefix}send [player or player number] [number of actions]',
                    value=f'Sends a player the number of specified actions '
                          f'(Example: {command_prefix}send @testsubject 2) '
                          f'(Example: {command_prefix}send 3 1)', inline=False)
    await message.channel.send(embed=embed)


async def increase_range(message, data):
    if int(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
               'actions']) > 0:
        data = jsonManager.update_player_range(message, data)
        await message.channel.send('Your range is now ' + str(
            data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                'range']) + ' tiles ' + message.author.mention + '!')
    else:
        await message.channel.send('You do not have any actions to increase your range ' + message.author.mention + '!')


async def move(message, data, command):
    split_command = command.split(' ')
    if len(split_command) == 1:
        await message.channel.send('Please specify a tile or a direction to move in ' + message.author.mention + '!')
        return
    elif len(split_command) > 2:
        await message.channel.send(
            'Invalid information provided for where to go ' + message.author.mention + '! Please specify a tile or a '
                                                                                       'direction to move.')
        return

    board = data['games'][str(message.guild.id)][str(message.channel.id)]['board']['data']
    player_number = str(
        data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
            'playerNumber'])
    new_player_stats = data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)]
    if new_player_stats['actions'] <= 0:
        await message.channel.send('You have no more actions remaining ' + message.author.mention + '!')
        return
    for i in range(len(board)):
        for j in range(len(board[i])):
            if str(board[i][j]) == player_number:
                if split_command[1] == 'north':
                    if i >= (len(board) - 1):
                        await message.channel.send(
                            'You may not move any farther north ' + message.author.mention + ', as you are at the top!')
                        return
                    if board[i + 1][j] != 0:
                        await message.channel.send(
                            'There is a player above you ' + message.author.mention +
                            '. You may not move onto players.')
                        return
                    board[i][j] = 0
                    board[i + 1][j] = int(player_number)
                    jsonManager.save_board(message, board)
                    await display_board(message, renderPipeline.construct_image(board,
                                                                                data['games'][str(message.guild.id)][
                                                                                   str(message.channel.id)][
                                                                                   'playerColors']),
                                        ('You have moved north 1 tile ' + message.author.mention + '!'))
                    new_player_stats['actions'] -= 1
                    new_player_stats['moves'] += 1
                    jsonManager.save_player(message, message.author.id, new_player_stats)
                    return
                elif split_command[1] == 'south':
                    if i <= 0:
                        await message.channel.send(
                            'You may not move any farther south ' + message.author.mention + ', as you are at the '
                                                                                             'bottom!')
                        return
                    if board[i - 1][j] != 0:
                        await message.channel.send(
                            'There is a player below you ' + message.author.mention +
                            '. You may not move onto players.')
                        return
                    board[i][j] = 0
                    board[i - 1][j] = int(player_number)
                    jsonManager.save_board(message, board)
                    await display_board(message, renderPipeline.construct_image(board,
                                                                                data['games'][str(message.guild.id)][
                                                                                   str(message.channel.id)][
                                                                                   'playerColors']),
                                        ('You have moved south 1 tile ' + message.author.mention + '!'))
                    new_player_stats['actions'] -= 1
                    new_player_stats['moves'] += 1
                    jsonManager.save_player(message, message.author.id, new_player_stats)
                    return
                elif split_command[1] == 'east':
                    if j >= (len(board[i]) - 1):
                        await message.channel.send(
                            'You may not move any farther east ' + message.author.mention + ', as you are at the edge!')
                        return
                    if board[i][j + 1] != 0:
                        await message.channel.send(
                            'There is a player to the right of you ' + message.author.mention + '. You may not move '
                                                                                                'onto players.')
                        return
                    board[i][j] = 0
                    board[i][j + 1] = int(player_number)
                    jsonManager.save_board(message, board)
                    await display_board(message, renderPipeline.construct_image(board,
                                                                                data['games'][str(message.guild.id)][
                                                                                   str(message.channel.id)][
                                                                                   'playerColors']),
                                        ('You have moved east 1 tile ' + message.author.mention + '!'))
                    new_player_stats['actions'] -= 1
                    new_player_stats['moves'] += 1
                    jsonManager.save_player(message, message.author.id, new_player_stats)
                    return
                elif split_command[1] == 'west':
                    if j <= 0:
                        await message.channel.send(
                            'You may not move any farther west ' + message.author.mention + ', as you are at the edge!')
                        return
                    if board[i][j - 1] != 0:
                        await message.channel.send(
                            'There is a player to the left of you ' + message.author.mention + '. You may not move '
                                                                                               'onto players.')
                        return
                    board[i][j] = 0
                    board[i][j - 1] = int(player_number)
                    jsonManager.save_board(message, board)
                    await display_board(message, renderPipeline.construct_image(board,
                                                                                data['games'][str(message.guild.id)][
                                                                                   str(message.channel.id)][
                                                                                   'playerColors']),
                                        ('You have moved west 1 tile ' + message.author.mention + '!'))
                    new_player_stats['actions'] -= 1
                    new_player_stats['moves'] += 1
                    jsonManager.save_player(message, message.author.id, new_player_stats)
                    return
                elif split_command[1] == 'weast':
                    await message.channel.send(
                        'I am sorry ' + message.author.mention + ', but you do not have the power to move weast.')
                else:
                    await message.channel.send('\'' + split_command[1] + '\' is not an ordinal direction or a '
                                                                         'coordinate ' + message.author.mention + '!')


async def shoot(message, data, command, client):
    split_command = command.split(' ')
    if len(split_command) == 1:
        await message.channel.send(
            'Please specify a tile, player, or a direction to shoot at ' + message.author.mention + '!')
        return
    elif len(split_command) > 2:
        await message.channel.send(
            'Invalid information provided for where to shoot ' + message.author.mention + '! Please specify a tile, '
                                                                                          'player, or a direction to '
                                                                                          'shoot.')
        return

    board = data['games'][str(message.guild.id)][str(message.channel.id)]['board']['data']
    player_number = str(
        data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
            'playerNumber'])
    if data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)]['actions'] <= 0:
        await message.channel.send('You have no more actions remaining ' + message.author.mention + '!')
        return
    if split_command[1] == str(player_number):
        # Reason we don't say shoot yourself here is that is not something everyone can handle hearing,
        # so we say you cannot shoot your own player instead
        await message.channel.send('You cannot shoot your own player ' + message.author.mention + '!')
        return
    try:
        specified_number = int(split_command[1])
        if specified_number > len(
                data['games'][str(message.guild.id)][str(message.channel.id)]['players']) or specified_number <= 0:
            await message.channel.send(
                'The player number of ' + str(specified_number) + ' does not exist ' + message.author.mention + '.')
            return
    except ValueError:
        if str(split_command[1][:3]) == '<@!':
            try:
                split_command[1] = data['games'][str(message.guild.id)][str(message.channel.id)]['players'][
                    str((split_command[1][3:])[:-1])]['playerNumber']
            except KeyError:
                await message.channel.send('That player is not currently in the game ' + message.author.mention + '!')
                return
        else:
            return
    if is_player_in_range(board, str(
            data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                'range']), str(player_number), str(split_command[1])):
        for player in data['games'][str(message.guild.id)][str(message.channel.id)]['players']:
            if str(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][player][
                       'playerNumber']) == str(split_command[1]):
                # TODO finish up shooting players
                # Remove a life from an enemy
                lives = data['games'][str(message.guild.id)][str(message.channel.id)]['players'][player]['lives'] - 1
                data['games'][str(message.guild.id)][str(message.channel.id)]['players'][player]['lives'] = lives
                # Remove an action from the attacker
                data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                    'actions'] -= 1
                # Add a hit to the attacker's record
                data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                    'hits'] += 1
                jsonManager.save_data(data)
                user = await client.fetch_user(player)
                if lives > 0:
                    await message.channel.send(
                        'Player ' + user.mention + ' has been shot! They now have ' + str(lives) + '\u2665 lives left.')
                else:
                    await jsonManager.kill_player(message, str(split_command[1]), user)
                break
    else:
        await message.channel.send(
            'Player ' + str(split_command[1]) + ' is out of range ' + message.author.mention + '!')


def is_player_in_range(board, player_range, attacker, defense):
    attacker_pos = None
    defender_pos = None
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == int(attacker):
                attacker_pos = (j, i)
            elif board[i][j] == int(defense):
                defender_pos = (j, i)
    if abs(defender_pos[0] - attacker_pos[0]) > int(player_range):
        return False
    elif abs(defender_pos[1] - attacker_pos[1]) > int(player_range):
        return False
    return True


async def vote_action(message, data, command):
    data = data['games'][str(message.guild.id)][str(message.channel.id)]
    player_number = 0
    if command[5:8] != '<@!':
        try:
            int(command[5:])
        except ValueError:
            await message.channel.send('*' + str(command[5:]) + '* is not a player ' + message.author.mention + '!')
            return
        player_number = int(command[5:])
    else:
        user_id = command[8:(len(command) - 1)]
        player_number = int(data['players'][str(user_id)]['playerNumber'])

    # Prevents the edge case of player number not being assigned
    if player_number == 0:
        await message.channel.send('Internal error processing request *playerNumber*')
        return

    # Prevents a player from voting for themselves
    if int(data['players'][str(message.author.id)]['playerNumber']) == player_number:
        await message.channel.send('You may not vote for yourself ' + message.author.mention + '!')
        return

    # Prevents a player from voting if they have no more votes today remaining
    if int(data['players'][str(message.author.id)]['remainingVotes']) <= 0:
        await message.channel.send('You have no more remaining votes today ' + message.author.mention + '!')
        return

    data['players'][str(message.author.id)]['remainingVotes'] = int(data['players'][str(message.author.id)]
                                                                    ['remainingVotes']) - 1
    jsonManager.save_player(message, message.author.id, data['players'][str(message.author.id)])
    for player in data['players']:
        if int(data['players'][player]['playerNumber']) == player_number:
            data['players'][player]['votes'] = int(data['players'][player]['votes']) + 1
            jsonManager.save_player(message, message.author.id, data['players'][player])
            break


async def send_actions(message, data):
    """
    Sends a number of actions from the message sender to their desired target
    :param message: The original message sent by the commander
    :param data: The complete json dataset
    """
    data = data['games'][str(message.guild.id)][str(message.channel.id)]
    locators = str(message.content)[2:].split()
    if len(locators) != 3:
        command_prefix = configUtils.read_value('botSettings', 'botCommandPrefix')
        await message.channel.send('Invalid command ' + message.author.mention +
                                   f'! Please use {command_prefix}send [player or player number] [number of actions]')
        return
    else:
        if locators[1][:3] == '<@!':
            player_id = locators[1][3:len(locators[1]) - 1]
            for player in data['players']:
                if player == player_id:
                    locators[1] = int(data['players'][player]['playerNumber'])
                    break
            if not isinstance(locators[1], int):
                await message.channel.send(locators[1] + ' is not in this game ' + message.author.mention + '!')
                return
        else:
            try:
                # noinspection PyTypeChecker
                locators[1] = int(locators[1])
            except ValueError:
                await message.channel.send('Invalid player number given ' + message.author.mention)
                return
        try:
            # noinspection PyTypeChecker
            locators[2] = int(locators[2])
        except ValueError:
            await message.channel.send('Invalid number of actions specified ' + message.author.mention)
            return
        if int(data['players'][str(message.author.id)]['actions']) < int(locators[2]):
            await message.channel.send('You do not have enough actions to do that ' + message.author.mention)
            return

        for player in data['players']:
            if int(data['players'][player]['playerNumber']) == locators[1]:
                data['players'][player]['actions'] = int(data['players'][player]['actions']) + int(locators[2])
                data['players'][str(message.author.id)]['actions'] = \
                    int(data['players'][str(message.author.id)]['actions']) - int(locators[2])
                await message.channel.send(message.author.mention + ' gave ' + str(locators[2]) + ' actions to ' +
                                           '<@!' + player + '>')
                break


async def list_players_lobby(message, data, client):
    """
    Shows the players in queue before a game has been started that used */join
    :param message: The original message with command
    :param data: The complete JSON dataset
    :param client: The discord RPC client
    """
    data = data['games'][str(message.guild.id)][str(message.channel.id)]

    embed_color = int('0x' + ("%06x" % random.randint(0, 0xFFFFFF)), 0)
    embed = discord.Embed(title="Players List", description="Here is a list of all the players "
                                                            "currently queued to play", color=embed_color)
    for key in data['players']:
        username = await client.fetch_user(key)
        player_number = data['players'][key]['playerNumber']
        embed.add_field(name=f"Player {player_number}", value=username, inline=False)
    await message.channel.send(embed=embed)


async def show_player_statistics(message, data, client):
    """
    Shows player 1 in the game and their information, along with the template for the player card moving forward
    :param message: The original message sent
    :param data: The complete JSON file
    :param client: The discord rpc client
    """
    data = data['games'][str(message.guild.id)][str(message.channel.id)]
    for key in data['players']:
        if data['players'][str(key)]['playerNumber'] == 1:
            player_id = key
            break

    user = await client.fetch_user(player_id)
    color_info = data['playerColors'][str(data['players'][str(key)]['playerNumber'])]
    embed = add_player_card_fields(color_info, user, data['players'][str(key)]['playerNumber'],
                                   data['players'][str(key)]['lives'],
                                   data['players'][str(key)]['actions'], data['players'][str(key)]['range'],
                                   data['players'][str(key)]['hits'], data['players'][str(key)]['moves'])
    msg = await message.channel.send(embed=embed)

    await msg.add_reaction("\u2B05")
    await msg.add_reaction("\u27A1")


async def flip_through_player_stats_card(message, data, direction, client):
    """
    Edits an original sent message by the robot to a new embed of player statistics
    :param message: The message sent by the discord robot
    :param data: The complete JSON dataset
    :param direction: A positive or negative 1 for which index to grab
    :param client: Discord RPC client connection
    """
    data = data['games'][str(message.guild.id)][str(message.channel.id)]
    embed = message.embeds[0]
    player_index = str(int(embed.fields[0].value[2:]) + direction)
    if player_index == str(0) or int(player_index) > len(data['players']):
        return

    for key in data['players']:
        if str(data['players'][str(key)]['playerNumber']) == player_index:
            player_id = key
            break

    user = await client.fetch_user(player_id)
    color_info = data['playerColors'][player_index]
    embed = add_player_card_fields(color_info, user, data['players'][str(key)]['playerNumber'],
                                   data['players'][str(key)]['lives'],
                                   data['players'][str(key)]['actions'], data['players'][str(key)]['range'],
                                   data['players'][str(key)]['hits'], data['players'][str(key)]['moves'])
    await message.edit(embed=embed)


def add_player_card_fields(color_info, user, player_number, lives, actions, range, hits, moves):
    """
    Adds information to an embed of player statistics
    """
    embed_color = int('0x' + str('%02x%02x%02x' % (color_info[0], color_info[1], color_info[2])).upper(), 16)
    embed = discord.Embed(title=str(user)[:-5] + ' Statistics',
                          description='Here is ' + str(user)[:-5] + ' and how much they have done this game!',
                          color=embed_color
                          )
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name='Player Number', value='\U0001F464 ' + str(player_number), inline=True)
    embed.add_field(name='Health', value='\u2665 ' + str(lives), inline=True)
    embed.add_field(name='Actions', value='\u2694 ' + str(actions), inline=True)
    embed.add_field(name='Range', value='\U0001F3AF ' + str(range), inline=True)
    embed.add_field(name='Hits', value='\U0001F4A5 ' + str(hits), inline=True)
    embed.add_field(name='Times Moved', value='\U0001F4A8 ' + str(moves), inline=True)
    return embed


def make_rules_embed(embed_color):
    """
    Returns a discord embed of the game rules
    :param embed_color: The color used for the embed
    """
    wave_emoji = '\U0001F52B'
    embed = discord.Embed(title="Rules", description=f"This is the rules on how to play tanks! {wave_emoji}",
                          color=embed_color)
    embed.add_field(name="1. You use actions to do things", value="Actions are the the core of the game, "
                                                                  "they can be used to move, shoot, or "
                                                                  "increase your tank's range.",
                    inline=False)
    embed.add_field(name="2. You receive 1 action a day", value="Every player in the game receives 1 "
                                                                "action a day at 12pm (noon) PST",
                    inline=False)
    embed.add_field(name="3. Dead players can give an extra action",
                    value="All dead players have the option to vote once a day. If a living player "
                          "receives 3+ votes, they will get 2 actions instead of 1 at 12pm.",
                    inline=False)
    embed.add_field(name="4. You have health",
                    value="Each player has a total of 3 health points. If you lose a health point, "
                          "it cannot be regenerated and the damage is permanent.",
                    inline=False)
    embed.add_field(name="5. Actions can be given",
                    value="You can bribe other players to give you actions. You are not bound by the "
                          "actions you receive each day and can get more from other players by asking them.",
                    inline=False)
    embed.add_field(name="6. You use actions whenever you want",
                    value="Using your actions is not time bound. You may chose to use them at any point in "
                          "the day should you still be alive and have the available actions.",
                    inline=False)
    embed.add_field(name="7. There are 5-20 players",
                    value="The game requires at least 5 unique players to get started and will work with up to "
                          "a maximum of 20 people.",
                    inline=False)
    embed.add_field(name="8. Last person standing wins!",
                    value="If you have the ability to make it to being the last person alive, you will "
                          "win! Congratulations if you manage to make it here!",
                    inline=False)
    return embed


async def display_board(message, board, ping=False):
    if ping:
        await message.channel.send(ping)

    with io.BytesIO() as image_binary:
        board.save(image_binary, 'PNG')
        image_binary.seek(0)
        await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
