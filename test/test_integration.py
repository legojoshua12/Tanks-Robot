"""
All tests related to discord and checking to make sure that the robot is interacting with the discord servers correctly
"""
import pytest
import discord.ext.test as dpytest

from src.tanks.libraries import messageHandler


class TestGeneric:
    @pytest.mark.asyncio
    async def test_not_command(self, bot, command_prefix):
        await dpytest.message("Hello, World!")
        assert dpytest.verify().message().nothing()

    @pytest.mark.asyncio
    async def test_command_invalid_syntax(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send((command_prefix + "test"))
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().contains().content(f"<@{bot.user.id}> Unknown command. "
                                                             f"Please use `{command_prefix}help` "
                                                             f"to view a list of commands and options.")
