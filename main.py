import os
import random

import discord
from discord.ext.commands import bot

from dotenv import load_dotenv

import boardConstructor as bC
import commands
import configUtils

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
    for row in range(len(boardData)):
        print(boardData[row])

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
            possibleCommand = await commands.public_commands(message, command)
            if possibleCommand == 'startCommandReceived':
                print(f'Starting new game on server {message.guild.name}#{message.guild.id}')
                commandPrefix = configUtils.readValue('botSettings', 'botCommandPrefix')
                embedColor = int('0x' + ("%06x" % random.randint(0, 0xFFFFFF)), 0)
                embedVar = discord.Embed(title="Welcome to the game of Tanks!",
                                         description="For constructing a game, add players as shown below and start "
                                                     "it when you are ready to begin a game",
                                         color=embedColor)
                embedVar.add_field(name=f'{commandPrefix}join',
                                   value=f'Each player who wishes to play can do a `{commandPrefix}join` to join this '
                                         f'new game', inline=False)
                embedVar.add_field(name=f'{commandPrefix}leave',
                                   value='That player will be removed from the game and not be in once started. If '
                                         'the player who created this lobby leaves then the lobby is ended and anyone '
                                         'can recreate a game', inline=False)
                embedVar.add_field(name=f'{commandPrefix}help',
                                   value='Shows this menu again', inline=False)
                embedVar.add_field(name=f'{commandPrefix}start',
                                   value='Will start the game if enough players have joined', inline=False)
                await message.channel.send(embed=embedVar)


# For first time boot of the robot,
# it is a good idea to run even if the values exist to ensure that nothing gets messed up
configUtils.initialize()
commandMessageStarter = configUtils.readValue('botSettings', 'botCommandPrefix')
client.run(TOKEN)
