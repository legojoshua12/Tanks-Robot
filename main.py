import sys
import asyncio
import os

import discord

from dotenv import load_dotenv

from libraries import jsonManager, renderPipeline, commands, boardConstructor as bC, configUtils

# This is a clean windows shutdown procedure as to not throw memory heap errors
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Setup .env for instancing
if os.path.exists('.env'):
    print('Env file located, initializing...')
    try:
        load_dotenv()
        TOKEN = os.getenv('DISCORD_TOKEN')
    except:
        print('DISCORD_TOKEN is not set, please set one first before continuing')
        exit()
else:
    print('Env file not located, generating now...')
    with open('.env', 'w') as f:
        f.write('DISCORD_TOKEN=')
    print('Exiting, please set a DISCORD_TOKEN in the env file')
    exit()


client = discord.Client()
configUtils.initialize()
jsonManager.initialize()
commandMessageStarter = configUtils.readValue('botSettings', 'botCommandPrefix')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Game(name='Tanks'),
                                 status=discord.Status.online, afk=False)

@client.event
async def on_message(message):
    # So the bot doesn't talk to itself
    if message.author == client.user:
        return
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


@client.event
async def on_reaction_add(reaction, user):
    if (reaction.message.author != client.user) or (user == client.user):
        return
    if len(reaction.message.embeds) > 0:
        await reaction.message.remove_reaction(reaction.emoji, user)
        data = jsonManager.readJson()
        if ('U+{:X}'.format(ord(reaction.emoji))) == 'U+27A1':
            await commands.flipThroughPlayerStatsCard(reaction.message, data, 1, client)
        elif ('U+{:X}'.format(ord(reaction.emoji))) == 'U+2B05':
            await commands.flipThroughPlayerStatsCard(reaction.message, data, -1, client)

# Start main program and connect to discord
print('Connecting to discord...')
client.run(TOKEN)
