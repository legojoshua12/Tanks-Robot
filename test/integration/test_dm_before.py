"""
Tests for the robots interactions when the player hasn't started a lobby or joined any game within a private message
channel
"""
import discord
import discord.ext.test as dpytest
import pytest

import test.utilstest as utils

from src.tanks.libraries import messageHandler, commands


@pytest.mark.asyncio
async def test_unknown_command_no_prefix(bot, command_prefix):
    channel = await utils.JsonUtility.get_private_channel(bot, 0)
    await channel.send("hello")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[0]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    verifier: str = f"{mess.author.mention} Unknown command. Please use `help` to view a list of commands and options."
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_unknown_command_with_prefix(bot, command_prefix):
    channel = await utils.JsonUtility.get_private_channel(bot, 0)
    await channel.send(f"{command_prefix}hello")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[0]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    verifier: str = f"{mess.author.mention} Unknown command. Please use `help` to view a list of commands and options."
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_help_no_prefix(bot, command_prefix):
    channel = await utils.JsonUtility.get_private_channel(bot, 0)
    await channel.send("help")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[0]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.dm_help_embed(embeds[0].color, None)
    assert dpytest.verify().message().contains().embed(new_embed)


@pytest.mark.asyncio
async def test_help_with_prefix(bot, command_prefix):
    channel = await utils.JsonUtility.get_private_channel(bot, 0)
    await channel.send(f"{command_prefix}help")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[0]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.dm_help_embed(embeds[0].color, None)
    assert dpytest.verify().message().contains().embed(new_embed)


@pytest.mark.asyncio
async def test_rules_with_prefix(bot, command_prefix):
    channel = await utils.JsonUtility.get_private_channel(bot, 0)
    await channel.send(f"{command_prefix}rules")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[0]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.make_rules_embed(embeds[0].color)
    assert dpytest.verify().message().contains().embed(new_embed)


@pytest.mark.asyncio
async def test_rules_no_prefix(bot, command_prefix):
    channel = await utils.JsonUtility.get_private_channel(bot, 0)
    await channel.send("rules")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[0]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.make_rules_embed(embeds[0].color)
    assert dpytest.verify().message().contains().embed(new_embed)


@pytest.mark.asyncio
async def test_rules_dm(bot, command_prefix):
    channel = await utils.JsonUtility.get_private_channel(bot, 0)
    await channel.send("dm")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[0]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    verifier: str = "I'm already here talking to you! Use `help` to get a list of commands."
    assert dpytest.verify().message().content(verifier)
