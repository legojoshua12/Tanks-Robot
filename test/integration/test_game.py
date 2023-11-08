"""
Tests as a real database is stood up for testing purposes
"""
import discord.ext.test as dpytest
import pytest

import test.utilstest as utils

from src.tanks.libraries import messageHandler, commands


@pytest.mark.asyncio
async def test_help_not_in_game(bot, command_prefix, mock_cursor):
    await utils.JsonUtility.start_sample_game(bot, mock_cursor)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}help")
    mess = dpytest.get_message()

    await messageHandler.handle_message(mess, bot, command_prefix)
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.active_game_help_embed(embeds[0].color, command_prefix)
    assert dpytest.verify().message().contains().embed(new_embed)