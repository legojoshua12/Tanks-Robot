"""
Tests as a real database is stood up for testing purposes
"""
import discord.ext.test as dpytest
import pytest
import os

from src.tanks.libraries import messageHandler, commands


@pytest.mark.integration
def test_print_env_variables():
    print("DB_NAME:", os.getenv('TEST_DB_NAME'))
    print("DB_USER:", os.getenv('TEST_DB_USER'))
    print("DB_PASSWORD:", os.getenv('TEST_DB_PASSWORD'))
    print("DB_HOST:", os.getenv('TEST_DB_HOST'))
    print("DB_PORT:", os.getenv('TEST_DB_PORT'))
    assert False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_help(live_bot, command_prefix, setUpIntegrationDatabase):
    channel = live_bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}help")
    mess = dpytest.get_message()

    await messageHandler.handle_message(mess, live_bot, command_prefix)
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.help_embed_no_game(embeds[0].color)
    assert dpytest.verify().message().contains().embed(new_embed)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_start_lobby(live_bot, command_prefix, setUpIntegrationDatabase):
    channel = live_bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}start")
    mess = dpytest.get_message()
    mess.author = live_bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, live_bot, command_prefix)
    assert dpytest.verify().message().content("Starting a game...")
    assert dpytest.verify().message().content(f"Adding {mess.author.mention} to the new game of Tanks!")
    embed = dpytest.get_message(peek=True).embeds[0]
    assert dpytest.verify().message().contains().embed(embed=embed)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_join_game(live_bot, command_prefix, setUpIntegrationDatabase):
    channel = live_bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}join")
    mess = dpytest.get_message()
    mess.author = live_bot.guilds[0].members[3]
    await messageHandler.handle_message(mess, live_bot, command_prefix)
    assert dpytest.verify().message().content(f"Adding {mess.author.mention} to the new game of Tanks!")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_start_game(live_bot, command_prefix, is_admin, setUpIntegrationDatabase):
    channel = live_bot.guilds[0].text_channels[0]
    if not is_admin:
        for i in range(3):
            await channel.send(f"{command_prefix}join")
            mess = dpytest.get_message()
            mess.author = live_bot.guilds[0].members[i+4]
            await messageHandler.handle_message(mess, live_bot, command_prefix)
            assert dpytest.verify().message().content(f"Adding {mess.author.mention} to the new game of Tanks!")
    await channel.send(f"{command_prefix}start")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, live_bot, command_prefix)
    if is_admin:
        assert dpytest.verify().message().content(f"Welcome to tanks {live_bot.guilds[0].members[2].mention}, " +
                                                  f"{live_bot.guilds[0].members[3].mention}!")
    else:
        assert dpytest.verify().message().content(f"Welcome to tanks {live_bot.guilds[0].members[2].mention}, " +
                                                  f"{live_bot.guilds[0].members[3].mention}, " +
                                                  f"{live_bot.guilds[0].members[4].mention}, " +
                                                  f"{live_bot.guilds[0].members[5].mention}, " +
                                                  f"{live_bot.guilds[0].members[6].mention}!")
    mess = dpytest.get_message()
    assert len(mess.attachments) == 1
    assert mess.attachments[0].filename == 'image.png'


@pytest.mark.asyncio
@pytest.mark.integration
async def test_board(live_bot, command_prefix, setUpIntegrationDatabase):
    channel = live_bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}board")
    mess = dpytest.get_message()
    mess.author = live_bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, live_bot, command_prefix)
    mess = dpytest.get_message()
    assert len(mess.attachments) == 1
    assert mess.attachments[0].filename == 'image.png'
