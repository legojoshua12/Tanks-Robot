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
            stars = 0
            for c in message.content:
                if c == '*':
                    stars = stars + 1
            if stars == 2:
                return

            # Here is a slicer of the message to make an easy reference
            command = message.content[2:].lower()

            # Commands
            await commands.public_commands(message, command)


# For first time boot of the robot,
# it is a good idea to run even if the values exist to ensure that nothing gets messed up
configUtils.initialize()
commandMessageStarter = configUtils.readValue('botSettings', 'botCommandPrefix')
client.run(TOKEN)
