from src.tanks import main

import discord.ext.commands.bot
from discord.ext import commands


class Message(commands.Cog):
    def __init__(self, bot: discord.ext.commands.bot.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        await main.on_message(message)
        channel = self.bot.guilds[0].text_channels[0]
        if channel is not None:
            await channel.send(f"Hello there!")


async def setup(bot: discord.ext.commands.bot.Bot):
    await bot.add_cog(Message(bot))
