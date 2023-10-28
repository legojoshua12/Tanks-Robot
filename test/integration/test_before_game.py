"""
Tests for the robots interactions when the players haven't started a game yet or a lobby yet
"""
import discord
import discord.ext.test as dpytest
import pytest

import test.utilstest as utils

from src.tanks.libraries import messageHandler


@pytest.mark.asyncio
async def test_help(bot, command_prefix):
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}help")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    assert dpytest.verify().message().contains().embed(embeds[0])


@pytest.mark.asyncio
async def test_rules(bot, command_prefix):
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}rules")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    assert dpytest.verify().message().contains().embed(embeds[0])


@pytest.mark.asyncio
async def test_dm(bot, command_prefix, mock_cursor):
    await utils.JsonUtility.start_sample_game(bot, mock_cursor)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}dm")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)

    private_message = dpytest.get_message(peek=True)
    assert private_message.channel.type == discord.ChannelType.private
    assert private_message.content == "Hey there! 👋 How can I help you? Use `help` to get started!"

    public_message = dpytest.get_message()
    assert public_message.channel.type == discord.ChannelType.text
    assert public_message.content == f"{mess.author.mention} I just sent you a private message! ✉"

    # Clear the queue
    dpytest.get_message()


@pytest.mark.asyncio
async def test_start_game(bot, command_prefix):
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}start")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().content("Starting a game...")
    assert dpytest.verify().message().content(f"Adding {mess.author.mention} to the new game of Tanks!")
    embed = dpytest.get_message(peek=True).embeds[0]
    assert dpytest.verify().message().contains().embed(embed=embed)


@pytest.mark.asyncio
async def test_command_invalid_syntax(bot, command_prefix):
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}test")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    verify_message: str = f"{bot.user.mention} Unknown command. Please use `{command_prefix}help` "
    verify_message += "to view a list of commands and options."
    assert dpytest.verify().message().content(verify_message)


@pytest.mark.asyncio
async def test_ignored_message(bot, command_prefix):
    channel = bot.guilds[0].text_channels[0]
    await channel.send('test')
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
