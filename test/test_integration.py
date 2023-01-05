"""
All tests related to discord and checking to make sure that the robot is interacting with the discord servers correctly
"""
import discord
import discord.ext.test as dpytest
import pytest

import test.utilstest as utils

from src.tanks.libraries import messageHandler, configUtils


class TestGeneric:
    @pytest.mark.asyncio
    async def test_not_command(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send("Hello, World!")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().nothing()

    @pytest.mark.asyncio
    async def test_mentioned(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"<@{bot.user.id}>")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().nothing()

    @pytest.mark.skip(reason="Skipping due to a lack of testing suite")
    @pytest.mark.asyncio
    async def test_queue(self):
        assert True


class TestDailyUpkeep:
    @pytest.mark.skip(reason='Skipping daily check for now as there is a lot of utils that need to be made first')
    @pytest.mark.asyncio
    async def test_daily_upkeep(self):
        assert True


class TestBeforeGame:
    @pytest.mark.asyncio
    async def test_help(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}help")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        embeds = dpytest.get_message(peek=True).embeds
        assert len(embeds) == 1
        assert dpytest.verify().message().contains().embed(embeds[0])

    @pytest.mark.asyncio
    async def test_rules(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}rules")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        embeds = dpytest.get_message(peek=True).embeds
        assert len(embeds) == 1
        assert dpytest.verify().message().contains().embed(embeds[0])

    # TODO Look into dpytest and verifying messages that contain emojis
    @pytest.mark.asyncio
    async def test_dm(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}dm")
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

    @pytest.mark.asyncio
    async def test_start_game(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content("Starting a game...")
        assert dpytest.verify().message().content(f"Adding <@{mess.author.id}> to the new game of Tanks!")
        embed = dpytest.get_message(peek=True).embeds[0]
        assert dpytest.verify().message().contains().embed(embed=embed)

    @pytest.mark.asyncio
    async def test_command_invalid_syntax(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}test")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"<@{bot.user.id}> Unknown command. "
                                                  f"Please use `{command_prefix}help` "
                                                  f"to view a list of commands and options.")

    @pytest.mark.asyncio
    async def test_ignored_message(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send('test')
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().nothing()

    @pytest.mark.asyncio
    async def test_mentioned(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"<@{bot.user.id}>")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().nothing()


class TestLobby:
    @pytest.mark.asyncio
    async def test_join_new_player(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}join")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[3]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"Adding <@{mess.author.id}> to the new game of Tanks!")

    @pytest.mark.asyncio
    async def test_join_already_present(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}join")
        mess = dpytest.get_message()
        # Member already joined from setup in utils
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"<@{mess.author.id}> is already in the game!")

    @pytest.mark.asyncio
    async def test_leave(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}leave")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"<@{mess.author.id}> left the game. \U0001F622")

    @pytest.mark.asyncio
    async def test_leave_not_present(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}leave")
        mess = dpytest.get_message()
        # Member already joined from setup in utils
        mess.author = bot.guilds[0].members[3]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"<@{mess.author.id}> cannot leave when you are not in the game!")

    @pytest.mark.asyncio
    async def test_help(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}help")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        embeds = dpytest.get_message(peek=True).embeds
        assert len(embeds) == 1
        assert dpytest.verify().message().contains().embed(embeds[0])

    @pytest.mark.asyncio
    async def test_list_players(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}players")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        embeds = dpytest.get_message(peek=True).embeds
        assert len(embeds) == 1
        assert dpytest.verify().message().contains().embed(embeds[0])

    @pytest.mark.asyncio
    async def test_help(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}help")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        embeds = dpytest.get_message(peek=True).embeds
        assert len(embeds) == 1
        assert dpytest.verify().message().contains().embed(embeds[0])

    # TODO Look into dpytest and verifying messages that contain emojis
    @pytest.mark.asyncio
    async def test_dm(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
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

    @pytest.mark.asyncio
    async def test_start_not_enough_players(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content("There are not enough players in the game to start!")

    @pytest.mark.asyncio()
    async def test_start_too_many_players(self, bot, command_prefix):
        await utils.JsonUtility.add_many_players(bot, command_prefix)
        members_list = bot.guilds[0].members[3:]
        channel = bot.guilds[0].text_channels[0]
        for idx, member in enumerate(members_list):
            await channel.send(f"{command_prefix}join")
            mess = dpytest.get_message()
            mess.author = bot.guilds[0].members[idx+3]
            await messageHandler.handle_message(mess, bot, command_prefix)
            assert dpytest.verify().message().content(f"Adding <@{member.id}> to the new game of Tanks!")
        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content("There are too many players in the game to start!")

    @pytest.mark.asyncio
    async def test_start(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        for i in range(4):
            await channel.send(f"{command_prefix}join")
            mess = dpytest.get_message()
            mess.author = bot.guilds[0].members[i+3]
            await messageHandler.handle_message(mess, bot, command_prefix)
            assert dpytest.verify().message().content(f"Adding <@{mess.author.id}> to the new game of Tanks!")
        if not str(configUtils.read_value('startGame', 'adminTesting')).lower() == 'true':
            await channel.send(f"{command_prefix}start")
            mess = dpytest.get_message()
            await messageHandler.handle_message(mess, bot, command_prefix)
            assert dpytest.verify().message().content(f"Welcome to tanks <@{bot.guilds[0].members[2].id}>, " +
                                                      f"<@{bot.guilds[0].members[3].id}>, " +
                                                      f"<@{bot.guilds[0].members[4].id}>, " +
                                                      f"<@{bot.guilds[0].members[5].id}>, " +
                                                      f"<@{bot.guilds[0].members[6].id}>!")
            mess = dpytest.get_message()
            assert len(mess.attachments) == 1
            assert mess.attachments[0].filename == 'image.png'
        else:
            assert True

    @pytest.mark.asyncio
    async def test_command_invalid_syntax(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}test")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"<@{bot.user.id}> Unknown command. "
                                                  f"Please use `{command_prefix}help` "
                                                  f"to view a list of commands and options.")

    @pytest.mark.asyncio
    async def test_ignored_message(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send('test')
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().nothing()

    @pytest.mark.asyncio
    async def test_mentioned(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"<@{bot.user.id}>")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().nothing()


class TestInGame:
    @pytest.mark.asyncio
    async def test_command_not_in_game(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}test")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"You are not playing in this game <@{bot.user.id}>!")

    @pytest.mark.asyncio
    async def test_command_invalid_syntax(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}test")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"<@{bot.guilds[0].members[2].id}> Unknown command. "
                                                  f"Please use `{command_prefix}help` "
                                                  f"to view a list of commands and options.")

    @pytest.mark.asyncio
    async def test_ignored_message(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send('test')
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().nothing()

    @pytest.mark.asyncio
    async def test_mentioned(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"<@{bot.user.id}>")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().nothing()
