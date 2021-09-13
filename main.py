"""This is the main function that should be run to start the robot"""
import sys
import asyncio
import os
from queue import Queue

import discord
import asyncio

from dotenv import load_dotenv

from libraries import configUtils, jsonManager, messageHandler, commands

# This is a clean windows shutdown procedure as to not throw memory heap errors
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Setup .env for instancing
if os.path.exists('.env'):
    print('Env file located, initializing...')
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN is None:
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
messageQueue = Queue(maxsize=0)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    asyncio.get_event_loop().create_task(handleQueue())
    await client.change_presence(activity=discord.Game(name='Tanks'),
                                 status=discord.Status.online, afk=False)


@client.event
async def on_message(message):
    # So the bot doesn't talk to itself
    if message.author == client.user:
        return
    messageQueue.put(message)


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


async def handleQueue():
    while True:
        if messageQueue.qsize() > 0:
            await messageHandler.handleMessage(messageQueue.get(), client, commandMessageStarter)
        # This is a delay to slow down the processing speed of the queue if it is too processor intensive
        # Param is in seconds
        await asyncio.sleep(0)

# Start main program and connect to discord
print('Connecting to discord...')
client.run(TOKEN)
