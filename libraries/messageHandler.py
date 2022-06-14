"""This is the main loader for the robot, handling any and all incoming commands off of the command queue"""
import discord

from libraries import boardConstructor as bC
from libraries import jsonManager, renderPipeline, commands


async def handleMessage(message, client, commandMessageStarter):
    """
    Used to parse and perform functions based on an incoming message
    :param message: Main message from the queue
    :param client: Discord client for instantiation of user objects
    :param commandMessageStarter: Start prefix for a command
    :return: None
    """
    if isinstance(message.channel, discord.channel.DMChannel):
        await commands.direct_message_commands(message, message.content)
    else:
        # TODO This is for audit purposes only, remove on final build
        if message.content == 'clear':
            jsonManager.clearAllData()

        if message.content.startswith(commandMessageStarter):
            # Check to make sure this is inline with config.ini
            if commandMessageStarter[0] == '*':
                # Only check for star if there is one, otherwise no need to do an italics check
                stars = 0
                for c in message.content:
                    if c == '*':
                        stars = stars + 1
                if stars >= 2:
                    return

            # Don't say anything, there was no command and only the prefix given
            if len(message.content) == len(commandMessageStarter) or message.content[len(commandMessageStarter):].isspace():
                await message.channel.send(message.author.mention + ' No input command. Please use `*/help` to view a '
                                                                    'list of commands and options.')
                return

            # A slicer of the message to make an easy reference
            command = message.content[len(commandMessageStarter):].lower()

            # Commands
            # Check if there is a game going
            isGamePresent = jsonManager.checkIfGameIsInChannel(message)
            if isGamePresent == 'lobby':
                action = await commands.public_commands_lobby(message, command)
                if action == 'join':
                    data = jsonManager.readGamesJson()
                    newPlayerNumber = (len(data['games'][str(message.guild.id)][str(message.channel.id)]['players'])+1)
                    isPresent = jsonManager.addPlayerToGame(message, newPlayerNumber)
                    if isPresent == 'playerAlreadyPresent':
                        await message.channel.send(message.author.mention + ' is already in the game!')
                    else:
                        await message.channel.send('Adding ' + message.author.mention + ' to the new game of Tanks!')
                elif action == 'leave':
                    isPresent = jsonManager.removePlayerFromGame(message, 1)
                    if isPresent == 'playerNotPresent':
                        await message.channel.send(message.author.mention + ' cannot leave when you are not in the '
                                                                            'game!')
                    else:
                        sadEmoji = '\U0001F622'
                        await message.channel.send(message.author.mention + f' left the game. {sadEmoji}')
                elif action == 'help':
                    await commands.sendLobbyHelpMenu(message)
                elif action == 'dm':
                    await commands.send_dm_starter(message)
                elif action == 'players':
                    data = jsonManager.readGamesJson()
                    await commands.listPlayersLobby(message, data, client)
                elif action == 'start':
                    # Here we want to actually boot the game
                    numberOfPlayers = jsonManager.getNumberOfPlayersInGame(message)
                    # TODO this is an admin number
                    numberOfPlayers = 5
                    if 5 <= numberOfPlayers <= 20:
                        booted = False
                        try:
                            boardData = bC.constructBoardData(numberOfPlayers)
                            boardData = bC.populateBoard(boardData, numberOfPlayers)
                            jsonManager.saveBoard(message, boardData)
                            jsonManager.updateStatus(message)
                            booted = True
                        except:
                            await message.channel.send('Error! Could not start game!')
                        if booted:
                            board = jsonManager.getBoard(message)
                            renderedBoard = renderPipeline.constructImage(board, jsonManager.readGamesJson()['games'][str(message.guild.id)][str(message.channel.id)]['playerColors'])
                            data = jsonManager.readGamesJson()
                            data = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
                            mentionString = 'Welcome to tanks '
                            index = 0
                            for player in data:
                                if index == (len(data) - 1):
                                    mentionString += (await client.fetch_user(player)).mention + '!'
                                else:
                                    index += 1
                                    mentionString += (await client.fetch_user(player)).mention + ', '
                            await message.channel.send(mentionString)
                            await commands.displayBoard(message, renderedBoard)
                    else:
                        if numberOfPlayers <= 4:
                            await message.channel.send('There are not enough players in the game to start!')
                        else:
                            await message.channel.send('There are too many players in the game to start!')

            elif isGamePresent == 'active':
                action = await commands.public_commands_game(message, command)
                if action == 'board':
                    renderedBoard = renderPipeline.constructImage(jsonManager.getBoard(message), jsonManager.readGamesJson()['games'][str(message.guild.id)][str(message.channel.id)]['playerColors'])
                    await commands.displayBoard(message, renderedBoard)
                elif action == 'players':
                    await commands.showPlayerStatistics(message, jsonManager.readGamesJson(), client)
                elif action == 'dm':
                    await commands.send_dm_starter(message)
                elif action == 'increase range':
                    await commands.increaseRange(message, jsonManager.readGamesJson())
                elif action == 'move':
                    await commands.move(message, jsonManager.readGamesJson(), command)
                elif action == 'shoot':
                    await commands.shoot(message, jsonManager.readGamesJson(), command, client)
                elif action == 'vote':
                    await commands.voteAction(message, jsonManager.readGamesJson(), command)
                elif action == 'send':
                    await commands.sendActions(message, jsonManager.readGamesJson())

            elif isGamePresent == 'none':
                possibleCommand = await commands.public_commands_no_game(message, command)
                if possibleCommand == 'startCommandReceived':
                    wroteToJson = False
                    try:
                        jsonManager.createGame(message)
                        jsonManager.addPlayerToGame(message, 1)
                        await message.channel.send('Adding ' + message.author.mention + ' to the new game of Tanks!')
                        wroteToJson = True
                    except:
                        await message.channel.send('An error has occurred in creating the game! Reverting now!')
                    if wroteToJson:
                        await commands.sendLobbyHelpMenu(message)
