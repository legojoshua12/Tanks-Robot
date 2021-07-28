import os
import random

import discord
from discord.ext.commands import bot

from dotenv import load_dotenv

import boardConstructor as bC
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
        embedColor = int('0x' + ("%06x" % random.randint(0, 0xFFFFFF)), 0)
        if command == 'help':
            embedVar = discord.Embed(title="Command Reference", description="Here is a list of bot commands for your "
                                                                            "reference! All commands may be done in "
                                                                            "private as well using a direct message.",
                                     color=embedColor)
            embedVar.add_field(name="*/help", value="Gives a list of commands", inline=False)
            embedVar.add_field(name="*/rules", value="Gives the game rules and how to play", inline=False)
            embedVar.add_field(name="*/dm", value="Sends a direct message for privacy", inline=False)
            await message.channel.send(embed=embedVar)
        elif command == 'rules':
            emoji = '\U0001F52B'
            embedVar = discord.Embed(title="Rules", description=f"This is the rules on how to play tanks! {emoji}", color=embedColor)
            embedVar.add_field(name="1. You use actions to do things", value="Actions are the the core of the game, "
                                                                             "they can be used to move, shoot, or "
                                                                             "increase your tank's range.",
                               inline=False)
            embedVar.add_field(name="2. You receive 1 action a day", value="Every player in the game receives 1 "
                                                                           "action a day at 12pm (noon) PST",
                               inline=False)
            embedVar.add_field(name="3. Dead players can give an extra action",
                               value="All dead players have the option to vote once a day. If a living player "
                                     "receives 3+ votes, they will get 2 actions instead of 1 at 12pm.",
                               inline=False)
            embedVar.add_field(name="4. You have health",
                               value="Each player has a total of 3 health points. If you lose a health point, "
                                     "it cannot be regenerated and the damage is permanent.",
                               inline=False)
            embedVar.add_field(name="5. Actions can be given",
                               value="You can bribe other players to give you actions. You are not bound by the "
                                     "actions you receive each day and can get more from other players by asking them.",
                               inline=False)
            embedVar.add_field(name="6. You use actions whenever you want",
                               value="Using your actions is not time bound. You may chose to use them at any point in "
                                     "the day should you still be alive and have the available actions.",
                               inline=False)
            embedVar.add_field(name="7. Last person standing wins!",
                               value="If you have the ability to make it to being the last person alive, you will "
                                     "win! Congratulations if you manage to make it here!",
                               inline=False)
            await message.channel.send(embed=embedVar)
        elif command == 'dm':
            emoji = '\U0001F44B'
            await message.author.send(f"Hey there! {emoji} How can I help you? Use `*/help` to get started!")
        else:
            await message.channel.send(message.author.mention + ' Unknown command. Please use `*/help` to view a '
                                                                'list of commands and options.')


# For first time boot of the robot,
# it is a good idea to run even if the values exist to ensure that nothing gets messed up
configUtils.initialize()
commandMessageStarter = configUtils.readValue('botSettings', 'botCommandPrefix')
client.run(TOKEN)
