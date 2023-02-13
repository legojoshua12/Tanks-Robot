"""This is the main function that should be run to start the robot"""
import logging
import sys
import os
from queue import Queue
import schedule

import discord
import asyncio

from dotenv import load_dotenv

from src.tanks.libraries import configUtils, jsonManager, messageHandler, commands, dailyUpkeepManager


if __name__ == "__main__":
    # This is a clean windows shutdown procedure as to not throw memory heap errors
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Setup .env for instancing
    if os.path.exists('../../.env'):
        print('Env file located, initializing...')
        load_dotenv()
        TOKEN = os.getenv('DISCORD_TOKEN')
        if TOKEN == '':
            logging.critical('DISCORD_TOKEN is not set, please set one first before continuing')
            exit()
    else:
        logging.critical('Env file not located, generating now...')
        with open('../../.env', 'w') as f:
            f.write('DISCORD_TOKEN=')
        logging.critical('Exiting, please set a DISCORD_TOKEN in the env file')
        exit()

    print('Discord Version Info: ' + str(discord.version_info))
    configUtils.initialize()
    jsonManager.initialize()
    commandMessageStarter = configUtils.read_value('botSettings', 'botCommandPrefix')
    client = discord.Client(intents=discord.Intents.all())
    messageQueue = Queue()
    dailyQueue = Queue()


    @client.event
    async def on_ready() -> None:
        """Runs when the robot has connected to discord and begin setup of status and queue handler"""
        print(f'{client.user} has connected to Discord!')
        # First set up a coroutine for handling jobs
        asyncio.get_event_loop().create_task(handle_queue())
        # Add a schedule for daily upkeep
        upkeep_time = str(configUtils.read_value('gameSettings', 'dailyUpkeepTime'))
        # Run a coroutine for checking the schedule
        schedule.every().day.at(upkeep_time).do(add_daily_queue)
        asyncio.get_event_loop().create_task(check_schedule_time())
        # Set discord presence
        await client.change_presence(activity=discord.Game(name='Tanks'), status=discord.Status.online)


    @client.event
    async def on_message(message) -> None:
        """Runs on any message sent that the robot can see, then it takes that message and sends it to the queue"""
        # So the bot doesn't talk to itself
        if message.author == client.user:
            return
        messageQueue.put(message)


    @client.event
    async def on_reaction_add(reaction, user):
        """Runs whenever a reaction is added to a message sent by this robot, then handles it with the correct action"""
        if (reaction.message.author != client.user) or (user == client.user):
            return
        if len(reaction.message.embeds) > 0:
            if isinstance(reaction.message.channel, discord.channel.DMChannel):
                try:
                    if ('U+{:X}'.format(ord(reaction.emoji))) == 'U+27A1':
                        is_in_games = jsonManager.is_player_in_game(None, user.id)
                        is_in_multiple_games = jsonManager.is_player_in_multiple_games(None, user.id)
                        await reaction.message.delete()
                        if is_in_games and not is_in_multiple_games:
                            guild_id, channel_id = jsonManager.get_player_server_channel_single(None, user.id)
                            player_index = str(int(reaction.message.embeds[0].fields[0].value[2:]) + 1)
                            await commands.show_player_statistics(reaction.message, jsonManager.read_games_json(), client,
                                                                  guild_id, channel_id, player_index)

                    elif ('U+{:X}'.format(ord(reaction.emoji))) == 'U+2B05':
                        is_in_games = jsonManager.is_player_in_game(None, user.id)
                        is_in_multiple_games = jsonManager.is_player_in_multiple_games(None, user.id)
                        await reaction.message.delete()
                        if is_in_games and not is_in_multiple_games:
                            guild_id, channel_id = jsonManager.get_player_server_channel_single(None, user.id)
                            player_index = str(int(reaction.message.embeds[0].fields[0].value[2:]) - 1)
                            await commands.show_player_statistics(reaction.message, jsonManager.read_games_json(), client,
                                                                  guild_id, channel_id, player_index)
                except TypeError:
                    return
            else:
                await reaction.message.remove_reaction(reaction.emoji, user)
                try:
                    data = jsonManager.read_games_json()
                    if ('U+{:X}'.format(ord(reaction.emoji))) == 'U+27A1':
                        await commands.flip_through_player_stats_card(reaction.message, data, 1, client)
                    elif ('U+{:X}'.format(ord(reaction.emoji))) == 'U+2B05':
                        await commands.flip_through_player_stats_card(reaction.message, data, -1, client)
                except TypeError:
                    return


    async def handle_queue():
        """Takes items off of the queue and sends the message to the processor
        Once it has been fully handled, it will grab the next message in the queue"""
        while True:
            if messageQueue.qsize() > 0:
                await messageHandler.handle_message(messageQueue.get(), client, commandMessageStarter)
            # This is a delay to slow down the processing speed of the queue if it is too processor intensive
            # Param is in seconds
            await asyncio.sleep(1)


    def add_daily_queue():
        """Adds a value to the daily queue for when it is time to start daily upkeep"""
        dailyQueue.put('Daily upkeep ordered')


    async def check_schedule_time():
        """Checks for the current system time and if it is daily upkeep for the games to gain an action"""
        while True:
            schedule.run_pending()
            if dailyQueue.qsize() > 0:
                dailyQueue.get()
                await dailyUpkeepManager.dailyActionsAndVoteUpkeep(client)
            await asyncio.sleep(1)


    # Start main program and connect to discord
    print('Connecting to discord...')

    # noinspection PyUnboundLocalVariable
    client.run(TOKEN)
