"""This is the main function that should be run to start the robot"""
import sys
import asyncio
import os
import time
from datetime import datetime, timezone
from queue import Queue

import discord
import schedule
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
    """
    Runs when the robot has connected to discord and begin setup of status and queue handler
    """
    print(f'{client.user} has connected to Discord!')
    # First set up a coroutine for handling jobs
    asyncio.get_event_loop().create_task(handleQueue())
    # Add a schedule for daily upkeep
    upkeepTime = str(configUtils.readValue('gameSettings', 'dailyUpkeepTime'))
    schedule.every().day.at(upkeepTime).do(dailyActionsAndVoteUpkeep)
    # Run a coroutine for checking the schedule
    asyncio.get_event_loop().create_task(checkScheduleTime())
    # Set discord presence
    await client.change_presence(activity=discord.Game(name='Tanks'),
                                 status=discord.Status.online, afk=False)


@client.event
async def on_message(message):
    """
    Runs on any message sent that the robot can see, then it takes that message and sends it to the queue
    """
    # So the bot doesn't talk to itself
    if message.author == client.user:
        return
    messageQueue.put(message)


@client.event
async def on_reaction_add(reaction, user):
    """
    Runs whenever a reaction is added to a message sent by this robot, then handles it with the correct action
    """
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
    """
    Takes items off of the queue and sends the message to the processor. Once it has been fully handled, it will grab
    the next message in the queue
    """
    while True:
        if messageQueue.qsize() > 0:
            await messageHandler.handleMessage(messageQueue.get(), client, commandMessageStarter)
        # This is a delay to slow down the processing speed of the queue if it is too processor intensive
        # Param is in seconds
        await asyncio.sleep(0)


async def checkScheduleTime():
    """
    Checks for the current system time and if it is daily upkeep for the games to gain an action
    """
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


def dailyActionsAndVoteUpkeep():
    """
    Performs the daily action giving and vote tally
    """
    data = jsonManager.readJson()
    try:
        data = data['games']
    except KeyError:
        print("No games running for today's upkeep! Skipping processing")
        return
    for server in data:
        for channel in data[server]:
            if data[server][channel]['gameStatus'] == "active":
                for player in data[server][channel]['players']:
                    if data[server][channel]['players'][player]['lives'] <= 0:
                        # TODO
                        print('Do Something')
                    else:
                        data[server][channel]['players'][player]['actions'] = (int(data[server][channel]['players']
                                                                                   [player]['actions']) + 1)
    newData = {'games': data}
    jsonManager.saveData(newData)
    print('Completed Daily Upkeep at: ' + str(datetime.now()))
    return


# Start main program and connect to discord
dailyActionsAndVoteUpkeep()
print('Connecting to discord...')
client.run(TOKEN)
