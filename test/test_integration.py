"""
All tests related to discord and checking to make sure that the robot is interacting with the discord servers correctly
"""
import discord
import discord.ext.test as dpytest
import pytest

import test.utilstest as utils

from src.tanks.libraries import messageHandler


class TestGeneric:
    @pytest.mark.asyncio
    async def test_not_command(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send("Hello, World!")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().contains().nothing()


class TestBeforeGame:
    @pytest.mark.asyncio
    async def test_command_invalid_syntax(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send((command_prefix + "test"))
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().contains().content(f"<@{bot.user.id}> Unknown command. "
                                                             f"Please use `{command_prefix}help` "
                                                             f"to view a list of commands and options.")

    @pytest.mark.asyncio
    async def test_help(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send((command_prefix + "help"))
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        embeds = dpytest.get_message(peek=True).embeds
        assert len(embeds) == 1
        assert dpytest.verify().message().contains().embed(embeds[0])

    @pytest.mark.asyncio
    async def test_rules(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send((command_prefix + "rules"))
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        embeds = dpytest.get_message(peek=True).embeds
        assert len(embeds) == 1
        assert dpytest.verify().message().contains().embed(embeds[0])

    # TODO Look into dpytest and verifying messages that contain emojis
    @pytest.mark.asyncio
    async def test_dm(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send((command_prefix + "dm"))
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)

        private_message = dpytest.get_message(peek=True)
        assert private_message.channel.type == discord.ChannelType.private
        assert utils.CodecUtility.encodeByteToString(private_message.content) == \
               "b'Hey there! \\xf0\\x9f\\x91\\x8b How can I help you? Use `help` to get started!'"
        # assert dpytest.verify().message().content(
        #     "b'Hey there! \\xf0\\x9f\\x91\\x8b How can I help you? Use `help` to get started!'")

        public_message = dpytest.get_message()
        assert public_message.channel.type == discord.ChannelType.text
        assert utils.CodecUtility.encodeByteToString(public_message.content) == \
               f"b'<@{mess.author.id}> I just sent you a private message! \\xe2\\x9c\\x89'"
        # assert dpytest.verify().message().content(
        #     f"b'<@{mess.author.id}> I just sent you a private message! \\xe2\\x9c\\x89'")

        # TODO temporary measure for now to implement dypytest verify
        assert dpytest.verify().message().contains().content("How can I help you? Use `help` to get started!")
