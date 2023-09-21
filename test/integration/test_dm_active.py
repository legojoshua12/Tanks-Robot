"""
Tests for the robots interactions when the player is in one or many lobbies
"""
import discord
import discord.ext.test as dpytest
import pytest

import test.utilstest as utils

from src.tanks.libraries import messageHandler, commands


@pytest.mark.asyncio
async def test_unknown_command_no_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send("hello")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    verifier: str = f"{mess.author.mention} Unknown command. Please use `help` to view a list of commands and options."
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_unknown_command_with_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send(f"{command_prefix}hello")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    verifier: str = f"{mess.author.mention} Unknown command. Please use `help` to view a list of commands and options."
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_help_no_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send("help")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.dm_help_embed(embeds[0].color, True)
    assert dpytest.verify().message().contains().embed(new_embed)


@pytest.mark.asyncio
async def test_help_with_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send(f"{command_prefix}help")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.dm_help_embed(embeds[0].color, True)
    assert dpytest.verify().message().contains().embed(new_embed)


@pytest.mark.asyncio
async def test_rules_with_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send(f"{command_prefix}rules")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.make_rules_embed(embeds[0].color)
    assert dpytest.verify().message().contains().embed(new_embed)


@pytest.mark.asyncio
async def test_rules_no_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send("rules")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.make_rules_embed(embeds[0].color)
    assert dpytest.verify().message().contains().embed(new_embed)


@pytest.mark.asyncio
async def test_rules_dm(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send("dm")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    verifier: str = "I'm already here talking to you! Use `help` to get a list of commands."
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_single_board_dm_no_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send("board")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    mess = dpytest.get_message()
    assert len(mess.attachments) == 1
    assert mess.attachments[0].filename == 'image.png'


@pytest.mark.asyncio
async def test_single_board_dm_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send(f"{command_prefix}board")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    mess = dpytest.get_message()
    assert len(mess.attachments) == 1
    assert mess.attachments[0].filename == 'image.png'


@pytest.mark.asyncio
async def test_single_board_players_no_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send("players")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    message_embeds = dpytest.get_message(peek=True).embeds
    assert len(message_embeds) == 1
    assert dpytest.verify().message().embed(message_embeds[0])


@pytest.mark.asyncio
async def test_single_players_dm_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send(f"{command_prefix}players")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    message_embeds = dpytest.get_message(peek=True).embeds
    assert len(message_embeds) == 1
    assert dpytest.verify().message().embed(message_embeds[0])


@pytest.mark.asyncio
async def test_single_increase_range_no_actions_dm_no_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send("increase range")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    member_id: str = str(bot.guilds[0].members[2].id)
    utils.JsonUtility.remove_player_actions(guild_id, channel_id, member_id)
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    verifier: str = f"You do not have any actions to increase your range {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_single_increase_range_no_actions_dm_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send(f"{command_prefix}increase range")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    member_id: str = str(bot.guilds[0].members[2].id)
    utils.JsonUtility.remove_player_actions(guild_id, channel_id, member_id)
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    verifier: str = f"You do not have any actions to increase your range {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_single_increase_range_dm_no_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send("increase range")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    member_id: str = str(bot.guilds[0].members[2].id)
    previous_range = utils.JsonUtility.get_player_range(mess, guild_id, channel_id, member_id)
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    verifier: str = f"Your range is now {previous_range + 1} tiles {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_single_increase_range_dm_prefix(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = await utils.JsonUtility.get_private_channel(bot, 2)
    await channel.send(f"{command_prefix}increase range")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    member_id: str = str(bot.guilds[0].members[2].id)
    previous_range = utils.JsonUtility.get_player_range(mess, guild_id, channel_id, member_id)
    await messageHandler.handle_message(mess, bot, command_prefix)

    assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
    verifier: str = f"Your range is now {previous_range + 1} tiles {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)
