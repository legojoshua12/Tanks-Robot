import os
import random

import discord
from discord.ext.commands import bot

from dotenv import load_dotenv

import boardConstructor as bC
import commands
import configUtils
import jsonManager

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
commandMessageStarter = ''


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Game(name='Tanks'),
                                 status=discord.Status.online, afk=False)
    numberOfPlayers = 5
    boardData = bC.constructBoardData(numberOfPlayers)
    boardData = bC.populateBoard(boardData, numberOfPlayers)


@client.event
async def on_message(message):
    # So the bot doesn't talk to itself
    if message.author == client.user:
        return
    if isinstance(message.channel, discord.channel.DMChannel):
        await commands.direct_message_commands(message, message.content)
    else:
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
            command = message.content[2:].lower()

            # Commands
            # Check if there is a game going
            isGamePresent = jsonManager.checkIfGameIsInChannel(message)
            if isGamePresent == 'lobby':
                action = await commands.public_commands_lobby(message, command)
                if action == 'join':
                    isPresent = jsonManager.addPlayerToGame(message, 1)
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
                    await message.channel.send('Starting...')
            elif isGamePresent == 'active':
                print('game active')
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


# For first time boot of the robot,
# it is a good idea to run even if the values exist to ensure that nothing gets messed up
configUtils.initialize()
commandMessageStarter = configUtils.readValue('botSettings', 'botCommandPrefix')
client.run(TOKEN)
