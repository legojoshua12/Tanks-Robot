from src.tanks import main

import discord.ext.commands.bot
from discord.ext import commands


class Message(commands.Cog):
    def __init__(self, bot: discord.ext.commands.bot.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        queue = main.messageQueue
        queue.put(message)


async def setup(bot: discord.ext.commands.bot.Bot):
    await bot.add_cog(Message(bot))
