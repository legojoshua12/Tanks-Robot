"""
Integration tests for command interaction and interfacing generically
"""
import discord.ext.test as dpytest
import pytest

from src.tanks.libraries import messageHandler


@pytest.mark.asyncio
async def test_not_command(bot, command_prefix):
    channel = bot.guilds[0].text_channels[0]
    await channel.send("Hello, World!")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().nothing()


@pytest.mark.asyncio
async def test_mentioned(bot, command_prefix):
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{bot.user.mention}")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().nothing()


@pytest.mark.asyncio
async def test_queue(full_bot):
    guild = full_bot.guilds[0]
    channel = guild.text_channels[0]

    await channel.send("Test Message")
    print(dpytest.get_message(peek=True).author)
    assert dpytest.verify().message().content("Test Message")
