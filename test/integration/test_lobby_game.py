"""
Tests for all bot interactions when a lobby has been created however there is no active game yet
"""
import discord
import discord.ext.test as dpytest
import pytest

import test.utilstest as utils

from src.tanks.libraries import messageHandler, configUtils


@pytest.mark.asyncio
async def test_join_new_player(bot, command_prefix):
    await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}join")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[3]
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().content(f"Adding {mess.author.mention} to the new game of Tanks!")


@pytest.mark.asyncio
async def test_join_already_present(bot, command_prefix):
    await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}join")
    mess = dpytest.get_message()
    # Member already joined from setup in utils
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().content(f"{mess.author.mention} is already in the game!")


@pytest.mark.asyncio
async def test_leave(bot, command_prefix):
    await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}leave")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().content(f"{mess.author.mention} left the game. \U0001F622")


@pytest.mark.asyncio
async def test_leave_not_present(bot, command_prefix):
    await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}leave")
    mess = dpytest.get_message()
    # Member already joined from setup in utils
    mess.author = bot.guilds[0].members[3]
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().content(f"{mess.author.mention} cannot leave when you are not in the game!")


@pytest.mark.asyncio
async def test_help(bot, command_prefix):
    await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}help")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    assert dpytest.verify().message().contains().embed(embeds[0])


@pytest.mark.asyncio
async def test_list_players(bot, command_prefix):
    await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}players")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    assert dpytest.verify().message().contains().embed(embeds[0])


@pytest.mark.asyncio
async def test_dm(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
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
async def test_start_not_enough_players(bot, command_prefix, is_admin):
    if is_admin:
        pytest.skip("Admin currently enabled in config, skipping test")
    await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}start")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().content("There are not enough players in the game to start!")


@pytest.mark.asyncio
async def test_admin_start(bot, command_prefix, is_admin):
    if not is_admin:
        pytest.skip("Admin config not currently enabled, skipping test")
    await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}start")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().content(f"Welcome to tanks {bot.guilds[0].members[2].mention}!")
    mess = dpytest.get_message()
    assert len(mess.attachments) == 1
    assert mess.attachments[0].filename == 'image.png'


@pytest.mark.asyncio()
async def test_start_too_many_players(bot, command_prefix, is_admin):
    if is_admin:
        pytest.skip("Admin currently enabled in config, skipping test")
    await utils.JsonUtility.add_many_players(bot, command_prefix)
    members_list = bot.guilds[0].members[3:]
    channel = bot.guilds[0].text_channels[0]
    for idx, member in enumerate(members_list):
        await channel.send(f"{command_prefix}join")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[idx + 3]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"Adding {member.mention} to the new game of Tanks!")
    await channel.send(f"{command_prefix}start")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().content("There are too many players in the game to start!")


@pytest.mark.asyncio
async def test_start(bot, command_prefix, is_admin):
    await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    for i in range(4):
        await channel.send(f"{command_prefix}join")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[i + 3]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"Adding {mess.author.mention} to the new game of Tanks!")
    if not is_admin:
        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"Welcome to tanks {bot.guilds[0].members[2].mention}, " +
                                                  f"{bot.guilds[0].members[3].mention}, " +
                                                  f"{bot.guilds[0].members[4].mention}, " +
                                                  f"{bot.guilds[0].members[5].mention}, " +
                                                  f"{bot.guilds[0].members[6].mention}!")
        mess = dpytest.get_message()
        assert len(mess.attachments) == 1
        assert mess.attachments[0].filename == 'image.png'
    else:
        assert True


@pytest.mark.asyncio
async def test_command_invalid_syntax(bot, command_prefix):
    await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}test")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    verify_message: str = f"{bot.user.mention} Unknown command. Please use `{command_prefix}help` "
    verify_message += "to view a list of commands and options."
    assert dpytest.verify().message().content(verify_message)


@pytest.mark.asyncio
async def test_ignored_message(bot, command_prefix):
    await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send('test')
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().nothing()


@pytest.mark.asyncio
async def test_mentioned(bot, command_prefix):
    await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{bot.user.mention}")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().nothing()
