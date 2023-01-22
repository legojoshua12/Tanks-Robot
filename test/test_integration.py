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
        await channel.send(f"{bot.user.mention}")
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
               f"b'{mess.author.mention} I just sent you a private message! \\xe2\\x9c\\x89'"
        # assert dpytest.verify().message().content(
        #     f"b'{mess.author.mention} I just sent you a private message! \\xe2\\x9c\\x89'")

        # TODO temporary measure for now to implement dypytest verify
        assert dpytest.verify().message().contains().content("How can I help you? Use `help` to get started!")

    @pytest.mark.asyncio
    async def test_start_game(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}start")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content("Starting a game...")
        assert dpytest.verify().message().content(f"Adding {mess.author.mention} to the new game of Tanks!")
        embed = dpytest.get_message(peek=True).embeds[0]
        assert dpytest.verify().message().contains().embed(embed=embed)

    @pytest.mark.asyncio
    async def test_command_invalid_syntax(self, bot, command_prefix):
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}test")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"{bot.user.mention} Unknown command. "
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
        await channel.send(f"{bot.user.mention}")
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
        assert dpytest.verify().message().content(f"Adding {mess.author.mention} to the new game of Tanks!")

    @pytest.mark.asyncio
    async def test_join_already_present(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}join")
        mess = dpytest.get_message()
        # Member already joined from setup in utils
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"{mess.author.mention} is already in the game!")

    @pytest.mark.asyncio
    async def test_leave(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}leave")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"{mess.author.mention} left the game. \U0001F622")

    @pytest.mark.asyncio
    async def test_leave_not_present(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}leave")
        mess = dpytest.get_message()
        # Member already joined from setup in utils
        mess.author = bot.guilds[0].members[3]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"{mess.author.mention} cannot leave when you are not in the game!")

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
               f"b'{mess.author.mention} I just sent you a private message! \\xe2\\x9c\\x89'"
        # assert dpytest.verify().message().content(
        #     f"b'{mess.author.mention} I just sent you a private message! \\xe2\\x9c\\x89'")

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
            mess.author = bot.guilds[0].members[idx + 3]
            await messageHandler.handle_message(mess, bot, command_prefix)
            assert dpytest.verify().message().content(f"Adding {member.mention} to the new game of Tanks!")
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
            mess.author = bot.guilds[0].members[i + 3]
            await messageHandler.handle_message(mess, bot, command_prefix)
            assert dpytest.verify().message().content(f"Adding {mess.author.mention} to the new game of Tanks!")
        if not str(configUtils.read_value('startGame', 'adminTesting')).lower() == 'true':
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
    async def test_command_invalid_syntax(self, bot, command_prefix):
        await utils.JsonUtility.set_games_json_lobby(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}test")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"{bot.user.mention} Unknown command. "
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
        await channel.send(f"{bot.user.mention}")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().nothing()


class TestInGame:
    @pytest.mark.asyncio
    async def test_board(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}board")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        mess = dpytest.get_message()
        assert len(mess.attachments) == 1
        assert mess.attachments[0].filename == 'image.png'

    @pytest.mark.asyncio
    async def test_players(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}players")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        message_embeds = dpytest.get_message(peek=True).embeds
        assert len(message_embeds) == 1
        assert dpytest.verify().message().embed(message_embeds[0])

    # TODO Look into dpytest and verifying messages that contain emojis
    @pytest.mark.asyncio
    async def test_dm(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}dm")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
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
               f"b'{mess.author.mention} I just sent you a private message! \\xe2\\x9c\\x89'"
        # assert dpytest.verify().message().content(
        #     f"b'{mess.author.mention} I just sent you a private message! \\xe2\\x9c\\x89'")

        # TODO temporary measure for now to implement dypytest verify
        assert dpytest.verify().message().contains().content("How can I help you? Use `help` to get started!")

    @pytest.mark.asyncio
    async def test_increase_range_no_actions(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}increase range")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        utils.JsonUtility.remove_player_actions(str(bot.guilds[0].id), str(bot.guilds[0].text_channels[0].id),
                                                str(bot.guilds[0].members[2].id))
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(
            f"You do not have any actions to increase your range {mess.author.mention}!")

    @pytest.mark.asyncio
    async def test_increase_range(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}increase range")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        previous_range = utils.JsonUtility.get_player_range(mess)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"Your range is now {previous_range + 1} tiles {mess.author.mention}!")

    @pytest.mark.asyncio
    async def test_vote_alive(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}vote")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(
            f"Only players with no more lives may vote on an extra action for a player {mess.author.mention}.")

    @pytest.mark.asyncio
    async def test_vote_no_player(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}vote")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        utils.JsonUtility.kill_player(str(bot.guilds[0].id), str(bot.guilds[0].text_channels[0].id),
                                      str(bot.guilds[0].members[2].id))
        await messageHandler.handle_message(mess, bot, command_prefix)
        print(dpytest.get_message(peek=True).content)
        assert dpytest.verify().message().content(f"Please specify a player to vote for {mess.author.mention}.")

    @pytest.mark.asyncio
    async def test_vote_non_existing_player(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}vote some_random_person")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        utils.JsonUtility.kill_player(str(bot.guilds[0].id), str(bot.guilds[0].text_channels[0].id),
                                      str(bot.guilds[0].members[2].id))
        await messageHandler.handle_message(mess, bot, command_prefix)
        print(dpytest.get_message(peek=True).content)
        assert dpytest.verify().message().content(f"*some_random_person* is not a player {mess.author.mention}!")

    @pytest.mark.asyncio
    async def test_vote_no_remaining(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}vote {bot.guilds[0].members[2].id}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        utils.JsonUtility.kill_player(str(bot.guilds[0].id), str(bot.guilds[0].text_channels[0].id),
                                      str(bot.guilds[0].members[2].id))
        await messageHandler.handle_message(mess, bot, command_prefix)
        print(dpytest.get_message(peek=True).content)
        assert dpytest.verify().message().content(f"You have no more remaining votes today {mess.author.mention}!")

    @pytest.mark.asyncio
    async def test_vote_self(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}vote {bot.guilds[0].members[2].mention}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        utils.JsonUtility.kill_player(str(bot.guilds[0].id), str(bot.guilds[0].text_channels[0].id),
                                      str(bot.guilds[0].members[2].id))
        utils.JsonUtility.give_dead_player_vote(str(bot.guilds[0].id), str(bot.guilds[0].text_channels[0].id),
                                                str(bot.guilds[0].members[2].id), 1)
        await messageHandler.handle_message(mess, bot, command_prefix)
        print(dpytest.get_message(peek=True).content)
        assert dpytest.verify().message().content(f"You may not vote for yourself {mess.author.mention}!")

    @pytest.mark.asyncio
    async def test_command_not_in_game(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}test")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"You are not playing in this game {bot.user.mention}!")

    @pytest.mark.asyncio
    async def test_command_invalid_syntax(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = bot.guilds[0].text_channels[0]
        await channel.send(f"{command_prefix}test")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().content(f"{bot.guilds[0].members[2].mention} Unknown command. "
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
        await channel.send(f"{bot.user.mention}")
        mess = dpytest.get_message()
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.verify().message().nothing()
