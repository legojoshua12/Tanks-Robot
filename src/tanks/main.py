"""This is the main function that should be run to start the robot"""
import logging
import random
import sys
import os
from queue import Queue
import schedule

import discord
import discord.ext
import asyncio

from dotenv import load_dotenv

from src.tanks.libraries import configUtils, jsonManager, messageHandler, dailyUpkeepManager, commands

client = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(client)
messageQueue = Queue()
dailyQueue = Queue()


async def __handle_queue__(client=None, commandMessageStarter=None):
    """Takes items off of the queue and sends the message to the processor
    Once it has been fully handled, it will grab the next message in the queue"""
    while True:
        if messageQueue.qsize() > 0:

            await messageHandler.handle_message(messageQueue.get(), client, commandMessageStarter)
        # This is a delay to slow down the processing speed of the queue if it is too processor intensive
        # Param is in seconds
        await asyncio.sleep(1)

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

    @client.event
    async def on_ready() -> None:
        """Runs when the robot has connected to discord and begin setup of status and queue handler"""
        print(f'{client.user} has connected to Discord!')
        print('Initializing coroutine loops...')
        # First set up a coroutine for handling jobs
        asyncio.get_event_loop().create_task(__handle_queue__(
            client=client,
            commandMessageStarter=commandMessageStarter)
        )
        # Add a schedule for daily upkeep
        upkeep_time = str(configUtils.read_value('gameSettings', 'dailyUpkeepTime'))
        # Run a coroutine for checking the schedule
        schedule.every().day.at(upkeep_time).do(add_daily_queue)
        asyncio.get_event_loop().create_task(check_schedule_time())
        # Set discord presence
        await client.change_presence(activity=discord.Game(name='Tanks'), status=discord.Status.online)
        await tree.sync(guild=None)
        print('Initialization complete, bot is now running! (づ｡◕‿‿◕｡)づ')

    @tree.command(name="help", description="Gives a list of all possible commands")
    async def help_slash_command(interaction: discord.Interaction):
        if isinstance(interaction.channel, discord.channel.DMChannel):
            is_in_games = jsonManager.is_player_in_game(message=None, user_id=interaction.user.id)
            if is_in_games:
                embed = commands.dm_help_embed(in_game=True)
            else:
                embed = commands.dm_help_embed()
            await interaction.response.send_message(embed=embed)
        else:
            is_game_present: str = jsonManager.check_if_game_is_in_channel(None,
                                                                           interaction.guild_id, interaction.channel_id)
            if is_game_present == "lobby":
                embed = commands.get_lobby_help_menu()
                await interaction.response.send_message(embed=embed, ephemeral=True)
            elif is_game_present == "active":
                embed = commands.active_game_help_embed()
                await interaction.response.send_message(embed=embed, ephemeral=True)
            elif is_game_present == "none":
                embed = commands.help_embed_no_game()
                await interaction.response.send_message(embed=embed, ephemeral=True)
            elif is_game_present == "completed":
                embed = commands.completed_game_help_embed()
                await interaction.response.send_message(embed=embed, ephemeral=True)

    @tree.command(name="rules", description="List the rules for how to play tanks")
    async def rules_slash_command(interaction: discord.Interaction):
        embed_color = int('0x' + ("%06x" % random.randint(0, 0xFFFFFF)), 0)
        embed = commands.make_rules_embed(embed_color)
        if isinstance(interaction.channel, discord.channel.DMChannel):
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @client.event
    async def on_message(message) -> None:
        """Runs on any message sent that the robot can see, then it takes that message and sends it to the queue"""
        # So the bot doesn't talk to itself
        if message.author == client.user:
            return
        messageQueue.put(message)

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
