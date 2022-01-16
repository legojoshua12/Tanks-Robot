"""These are the commands that do actions given to the robot, AKA do the command shoot or do the command move"""
import io
import random

import discord

import libraries.configUtils as configUtils
import libraries.jsonManager as jsonManager
import libraries.renderPipeline as renderPipeline


async def direct_message_commands(message, command):
    embedColor = int('0x' + ("%06x" % random.randint(0, 0xFFFFFF)), 0)
    if command.startswith(configUtils.readValue('botSettings', 'botCommandPrefix')):
        command = command[2:].lower()
    else:
        command = command.lower()
    if command == 'help':
        embed = discord.Embed(title="Command Reference", description="Here is a list of bot commands for your "
                                                                     "reference! Simply type one of these to get "
                                                                     "started.",
                              color=embedColor)
        embed.add_field(name="help", value="Gives a list of commands", inline=False)
        embed.add_field(name="rules", value="Gives the game rules and how to play", inline=False)
        await message.channel.send(embed=embed)
    elif command == 'rules':
        emoji = '\U0001F52B'
        embed = discord.Embed(title="Rules", description=f"This is the rules on how to play tanks! {emoji}",
                              color=embedColor)
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
    embedColor = int('0x' + ("%06x" % random.randint(0, 0xFFFFFF)), 0)
    if command == 'help':
        commandPrefix = configUtils.readValue('botSettings', 'botCommandPrefix')
        embed = discord.Embed(title="Command Reference", description="Here is a list of bot commands for your "
                                                                     "reference! All commands may be done in "
                                                                     "private as well using a direct message.",
                              color=embedColor)
        embed.add_field(name=f"{commandPrefix}help", value="Gives a list of commands", inline=False)
        embed.add_field(name=f"{commandPrefix}rules", value="Gives the game rules and how to play", inline=False)
        embed.add_field(name=f"{commandPrefix}dm", value="Sends a direct message for privacy", inline=False)
        embed.add_field(name=f"{commandPrefix}start", value="Begins game setup lobby in this channel", inline=False)
        await message.channel.send(embed=embed)
    elif command == 'rules':
        embed = makeRulesEmbed(embedColor)
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
    letterEmoji = '\U00002709'
    waveEmoji = '\U0001F44B'
    await message.channel.send(message.author.mention + f' I just sent you a private message! {letterEmoji}')
    await message.author.send(f"Hey there! {waveEmoji} How can I help you? Use `help` to get started!")


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
    # Rest of these are for concurrency sake with the rest of the bot commands
    else:
        await message.channel.send(message.author.mention + ' Unknown command. Please use `*/help` to view a '
                                                            'list of commands and options.')


async def sendLobbyHelpMenu(message):
    commandPrefix = configUtils.readValue('botSettings', 'botCommandPrefix')
    embedColor = int('0x' + ("%06x" % random.randint(0, 0xFFFFFF)), 0)
    embed = discord.Embed(title="Welcome to the game of Tanks!",
                          description="For constructing a game, add players as shown below and start "
                                      "it when you are ready to begin a game",
                          color=embedColor)
    embed.add_field(name=f'{commandPrefix}join',
                    value=f'Each player who wishes to play can do a `{commandPrefix}join` to join this '
                          f'new game', inline=False)
    embed.add_field(name=f'{commandPrefix}leave',
                    value='That player will be removed from the game and not be in once started. If '
                          'the player who created this lobby leaves then the lobby is ended and anyone '
                          'can recreate a game', inline=False)
    embed.add_field(name=f'{commandPrefix}players',
                    value='Lists all players currently in queue to play', inline=False)
    embed.add_field(name=f'{commandPrefix}help',
                    value='Shows this menu again', inline=False)
    embed.add_field(name=f'{commandPrefix}dm',
                    value="Sends a direct message for privacy", inline=False)
    embed.add_field(name=f'{commandPrefix}start',
                    value='Will start the game if enough players have joined', inline=False)
    await message.channel.send(embed=embed)


async def public_commands_game(message, command):
    data = jsonManager.readJson()
    try:
        data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)]
    except KeyError:
        await message.channel.send('You are not playing in this game ' + message.author.mention + '!')
        return
    commandPrefix = configUtils.readValue('botSettings', 'botCommandPrefix')
    embedColor = int('0x' + ("%06x" % random.randint(0, 0xFFFFFF)), 0)
    if command == 'help':
        embed = discord.Embed(title="Command Reference", description="Here is a list of bot commands for your "
                                                                     "reference! Simply type one of these to get "
                                                                     "started.",
                              color=embedColor)
        embed.add_field(name=f'{commandPrefix}help', value="Gives a list of commands", inline=False)
        embed.add_field(name=f'{commandPrefix}rules', value="Gives the game rules and how to play", inline=False)
        embed.add_field(name=f'{commandPrefix}dm', value="Sends a direct message for privacy", inline=False)
        embed.add_field(name=f'{commandPrefix}board', value="Shows the board of the current game", inline=False)
        embed.add_field(name=f'{commandPrefix}players', value="Shows the players of the game and their accompanying "
                                                              "statistics", inline=False)
        embed.add_field(name=f'{commandPrefix}increase range', value="Spends 1 action point to increase your range",
                        inline=False)
        embed.add_field(name=f'{commandPrefix}move',
                        value="Spends 1 action point to 1 space north, south, west, or east",
                        inline=False)
        await message.channel.send(embed=embed)
    elif command == 'rules':
        embed = makeRulesEmbed(embedColor)
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
    else:
        await message.channel.send(message.author.mention + ' Unknown command. Please use `*/help` to view a '
                                                            'list of commands and options.')


async def increaseRange(message, data):
    if int(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
               'actions']) > 0:
        data = jsonManager.updatePlayerRange(message, data)
        await message.channel.send('Your range is now ' + str(
            data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                'range']) + ' tiles ' + message.author.mention + '!')
    else:
        await message.channel.send('You do not have any actions to increase your range ' + message.author.mention + '!')


async def move(message, data, command):
    splitCommand = command.split(' ')
    if len(splitCommand) == 1:
        await message.channel.send('Please specify a tile or a direction to move in ' + message.author.mention + '!')
        return
    elif len(splitCommand) > 2:
        await message.channel.send(
            'Invalid information provided for where to go ' + message.author.mention + '! Please specify a tile or a direction to move.')
        return

    board = data['games'][str(message.guild.id)][str(message.channel.id)]['board']['data']
    playerNumber = str(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                           'playerNumber'])
    newPlayerStats = data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)]
    if newPlayerStats['actions'] <= 0:
        await message.channel.send('You have no more actions remaining ' + message.author.mention + '!')
        return
    for i in range(len(board)):
        for j in range(len(board[i])):
            if str(board[i][j]) == playerNumber:
                if splitCommand[1] == 'north':
                    if i >= (len(board) - 1):
                        await message.channel.send(
                            'You may not move any farther north ' + message.author.mention + ', as you are at the top!')
                        return
                    if board[i + 1][j] != 0:
                        await message.channel.send(
                            'There is a player above you ' + message.author.mention + '. You may not move onto players.')
                        return
                    board[i][j] = 0
                    board[i + 1][j] = int(playerNumber)
                    jsonManager.saveBoard(message, board)
                    await displayBoard(message, renderPipeline.constructImage(board,
                                                                              data['games'][str(message.guild.id)][
                                                                                  str(message.channel.id)][
                                                                                  'playerColors']),
                                       ('You have moved north 1 tile ' + message.author.mention + '!'))
                    newPlayerStats['actions'] -= 1
                    newPlayerStats['moves'] += 1
                    jsonManager.savePlayer(message, message.author.id, newPlayerStats)
                    return
                elif splitCommand[1] == 'south':
                    if i <= 0:
                        await message.channel.send(
                            'You may not move any farther south ' + message.author.mention + ', as you are at the bottom!')
                        return
                    if board[i - 1][j] != 0:
                        await message.channel.send(
                            'There is a player below you ' + message.author.mention + '. You may not move onto players.')
                        return
                    board[i][j] = 0
                    board[i - 1][j] = int(playerNumber)
                    jsonManager.saveBoard(message, board)
                    await displayBoard(message, renderPipeline.constructImage(board,
                                                                              data['games'][str(message.guild.id)][
                                                                                  str(message.channel.id)][
                                                                                  'playerColors']),
                                       ('You have moved south 1 tile ' + message.author.mention + '!'))
                    newPlayerStats['actions'] -= 1
                    newPlayerStats['moves'] += 1
                    jsonManager.savePlayer(message, message.author.id, newPlayerStats)
                    return
                elif splitCommand[1] == 'east':
                    if j >= (len(board[i]) - 1):
                        await message.channel.send(
                            'You may not move any farther east ' + message.author.mention + ', as you are at the edge!')
                        return
                    if board[i][j + 1] != 0:
                        await message.channel.send(
                            'There is a player to the right of you ' + message.author.mention + '. You may not move onto players.')
                        return
                    board[i][j] = 0
                    board[i][j + 1] = int(playerNumber)
                    jsonManager.saveBoard(message, board)
                    await displayBoard(message, renderPipeline.constructImage(board,
                                                                              data['games'][str(message.guild.id)][
                                                                                  str(message.channel.id)][
                                                                                  'playerColors']),
                                       ('You have moved east 1 tile ' + message.author.mention + '!'))
                    newPlayerStats['actions'] -= 1
                    newPlayerStats['moves'] += 1
                    jsonManager.savePlayer(message, message.author.id, newPlayerStats)
                    return
                elif splitCommand[1] == 'west':
                    if j <= 0:
                        await message.channel.send(
                            'You may not move any farther west ' + message.author.mention + ', as you are at the edge!')
                        return
                    if board[i][j - 1] != 0:
                        await message.channel.send(
                            'There is a player to the left of you ' + message.author.mention + '. You may not move onto players.')
                        return
                    board[i][j] = 0
                    board[i][j - 1] = int(playerNumber)
                    jsonManager.saveBoard(message, board)
                    await displayBoard(message, renderPipeline.constructImage(board,
                                                                              data['games'][str(message.guild.id)][
                                                                                  str(message.channel.id)][
                                                                                  'playerColors']),
                                       ('You have moved west 1 tile ' + message.author.mention + '!'))
                    newPlayerStats['actions'] -= 1
                    newPlayerStats['moves'] += 1
                    jsonManager.savePlayer(message, message.author.id, newPlayerStats)
                    return
                elif splitCommand[1] == 'weast':
                    await message.channel.send(
                        'I am sorry ' + message.author.mention + ', but you do not have the power to move weast.')
                else:
                    await message.channel.send('\'' + splitCommand[1] + '\' is not an ordinal direction or a '
                                                                        'coordinate ' + message.author.mention + '!')


async def shoot(message, data, command, client):
    splitCommand = command.split(' ')
    if len(splitCommand) == 1:
        await message.channel.send(
            'Please specify a tile, player, or a direction to shoot at ' + message.author.mention + '!')
        return
    elif len(splitCommand) > 2:
        await message.channel.send(
            'Invalid information provided for where to shoot ' + message.author.mention + '! Please specify a tile, '
                                                                                          'player, or a direction to '
                                                                                          'shoot.')
        return

    board = data['games'][str(message.guild.id)][str(message.channel.id)]['board']['data']
    playerNumber = str(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                           'playerNumber'])
    if data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
        'actions'] <= 0:
        await message.channel.send('You have no more actions remaining ' + message.author.mention + '!')
        return
    if splitCommand[1] == str(playerNumber):
        # Reason we don't say shoot yourself here is that is not something everyone can handle hearing,
        # so we say you cannot shoot your own player instead
        await message.channel.send('You cannot shoot your own player ' + message.author.mention + '!')
        return
    try:
        specifiedNumber = int(splitCommand[1])
        if specifiedNumber > len(
                data['games'][str(message.guild.id)][str(message.channel.id)]['players']) or specifiedNumber <= 0:
            await message.channel.send(
                'The player number of ' + str(specifiedNumber) + ' does not exist ' + message.author.mention + '.')
            return
    except ValueError:
        if str(splitCommand[1][:3]) == '<@!':
            try:
                splitCommand[1] = data['games'][str(message.guild.id)][str(message.channel.id)]['players'][
                    str((splitCommand[1][3:])[:-1])]['playerNumber']
            except KeyError:
                await message.channel.send('That player is not currently in the game ' + message.author.mention + '!')
                return
        else:
            return
    if isPlayerInRange(board, str(
            data['games'][str(message.guild.id)][str(message.channel.id)]['players'][str(message.author.id)][
                'range']), str(playerNumber), str(splitCommand[1])):
        for player in data['games'][str(message.guild.id)][str(message.channel.id)]['players']:
            if str(data['games'][str(message.guild.id)][str(message.channel.id)]['players'][player][
                       'playerNumber']) == str(splitCommand[1]):
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
                jsonManager.saveData(message, data)
                user = await client.fetch_user(player)
                if lives > 0:
                    await message.channel.send(
                        'Player ' + user.mention + ' has been shot! They now have ' + str(lives) + '\u2665 lives left.')
                else:
                    await jsonManager.killPlayer(message, str(splitCommand[1]), user)
                break
    else:
        await message.channel.send(
            'Player ' + str(splitCommand[1]) + ' is out of range ' + message.author.mention + '!')


def isPlayerInRange(board, playerRange, attacker, defense):
    attackerPos = None
    defenderPos = None
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == int(attacker):
                attackerPos = (j, i)
            elif board[i][j] == int(defense):
                defenderPos = (j, i)
    if abs(defenderPos[0] - attackerPos[0]) > int(playerRange):
        return False
    elif abs(defenderPos[1] - attackerPos[1]) > int(playerRange):
        return False
    return True


# TODO
async def voteAction(message, data, command, client):
    print(command[6:])


async def listPlayersLobby(message, data, client):
    """
    Shows the players in queue before a game has been started that used */join
    """
    data = data['games'][str(message.guild.id)][str(message.channel.id)]

    embedColor = int('0x' + ("%06x" % random.randint(0, 0xFFFFFF)), 0)
    embed = discord.Embed(title="Players List", description="Here is a list of all the players "
                                                            "currently queued to play", color=embedColor)
    for key in data['players']:
        username = await client.fetch_user(key)
        playerNumber = data['players'][key]['playerNumber']
        embed.add_field(name=f"Player {playerNumber}", value=username, inline=False)
    await message.channel.send(embed=embed)


async def showPlayerStatistics(message, data, client):
    """
    Shows player 1 in the game and their information, along with the template for the player card moving forward
    :param message: The original message sent
    :param data: The complete JSON file
    :param client: The discord rpc client
    """
    data = data['games'][str(message.guild.id)][str(message.channel.id)]
    for key in data['players']:
        if data['players'][str(key)]['playerNumber'] == 1:
            playerID = key
            break

    user = await client.fetch_user(playerID)
    colorInfo = data['playerColors'][str(data['players'][str(key)]['playerNumber'])]
    embed = addPlayercardFields(colorInfo, user, data['players'][str(key)]['playerNumber'],
                                data['players'][str(key)]['lives'],
                                data['players'][str(key)]['actions'], data['players'][str(key)]['range'],
                                data['players'][str(key)]['hits'], data['players'][str(key)]['moves'])
    msg = await message.channel.send(embed=embed)

    await msg.add_reaction("\u2B05")
    await msg.add_reaction("\u27A1")


async def flipThroughPlayerStatsCard(message, data, direction, client):
    data = data['games'][str(message.guild.id)][str(message.channel.id)]
    embed = message.embeds[0]
    playerIndex = str(int(embed.fields[0].value[2:]) + direction)
    if playerIndex == str(0) or int(playerIndex) > len(data['players']):
        return

    for key in data['players']:
        if str(data['players'][str(key)]['playerNumber']) == playerIndex:
            playerID = key
            break

    user = await client.fetch_user(playerID)
    colorInfo = data['playerColors'][playerIndex]
    embed = addPlayercardFields(colorInfo, user, data['players'][str(key)]['playerNumber'],
                                data['players'][str(key)]['lives'],
                                data['players'][str(key)]['actions'], data['players'][str(key)]['range'],
                                data['players'][str(key)]['hits'], data['players'][str(key)]['moves'])
    await message.edit(embed=embed)


def addPlayercardFields(colorInfo, user, playerNumber, lives, actions, range, hits, moves):
    embedColor = int('0x' + str('%02x%02x%02x' % (colorInfo[0], colorInfo[1], colorInfo[2])).upper(), 16)
    embed = discord.Embed(title=str(user)[:-5] + ' Statistics',
                          description='Here is ' + str(user)[:-5] + ' and how much they have done this game!',
                          color=embedColor
                          )
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name='Player Number', value='\U0001F464 ' + str(playerNumber), inline=True)
    embed.add_field(name='Health', value='\u2665 ' + str(lives), inline=True)
    embed.add_field(name='Actions', value='\u2694 ' + str(actions), inline=True)
    embed.add_field(name='Range', value='\U0001F3AF ' + str(range), inline=True)
    embed.add_field(name='Hits', value='\U0001F4A5 ' + str(hits), inline=True)
    embed.add_field(name='Times Moved', value='\U0001F4A8 ' + str(moves), inline=True)
    return embed


def makeRulesEmbed(embedColor):
    waveEmoji = '\U0001F52B'
    embed = discord.Embed(title="Rules", description=f"This is the rules on how to play tanks! {waveEmoji}",
                          color=embedColor)
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


async def displayBoard(message, board, ping=False):
    if ping != False:
        await message.channel.send(ping)

    with io.BytesIO() as image_binary:
        board.save(image_binary, 'PNG')
        image_binary.seek(0)
        await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
