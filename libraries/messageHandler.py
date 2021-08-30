"""This is the main loader for the robot, handling any and all incoming commands off of the command queue"""
import discord

from libraries import jsonManager, renderPipeline, commands, boardConstructor


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
            # First we check to make sure someone isn't doing something in italics
            # Check to make sure this is inline with config.ini
            # TODO change this to be more robust for later
            stars = 0
            for c in message.content:
                if c == '*':
                    stars = stars + 1
            if stars == 2:
                return

            # Here is a slicer of the message to make an easy reference
            # TODO Make it dynamic in length
            command = message.content[2:].lower()

            # Commands
            # Check if there is a game going
            isGamePresent = jsonManager.checkIfGameIsInChannel(message)
            if isGamePresent == 'lobby':
                action = await commands.public_commands_lobby(message, command)
                if action == 'join':
                    data = jsonManager.readJson()
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
                            renderedBoard = renderPipeline.constructImage(board, jsonManager.readJson()['games'][str(message.guild.id)][str(message.channel.id)]['playerColors'])
                            await message.channel.send('Welcome to tanks!')
                            await commands.displayBoard(message, renderedBoard)
                    else:
                        if numberOfPlayers <= 4:
                            await message.channel.send('There are not enough players in the game to start!')
                        else:
                            await message.channel.send('There are too many players in the game to start!')

            elif isGamePresent == 'active':
                action = await commands.public_commands_game(message, command)
                if action == 'board':
                    renderedBoard = renderPipeline.constructImage(jsonManager.getBoard(message), jsonManager.readJson()['games'][str(message.guild.id)][str(message.channel.id)]['playerColors'])
                    await commands.displayBoard(message, renderedBoard)
                elif action == 'players':
                    await commands.showPlayerStatistics(message, jsonManager.readJson(), client)
                elif action == 'increase range':
                    await commands.increaseRange(message, jsonManager.readJson())
                elif action == 'move':
                    await commands.move(message, jsonManager.readJson(), command)
                elif action == 'shoot':
                    await commands.shoot(message, jsonManager.readJson(), command)

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