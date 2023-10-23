"""
Tests for the robots interactions when the player is in one or many lobbies
"""
import discord
import discord.ext.test as dpytest
import pytest

import test.utilstest as utils

from src.tanks.libraries import messageHandler, commands, jsonManager


class TestSingleActiveGame:
    @pytest.mark.asyncio
    async def test_unknown_command_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("hello")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = (f"{mess.author.mention} Unknown command. "
                         f"Please use `help` to view a list of commands and options.")
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_unknown_command_with_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}hello")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = (f"{mess.author.mention} Unknown command. "
                         f"Please use `help` to view a list of commands and options.")
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_help_no_prefix(self, bot, command_prefix):
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
    async def test_help_with_prefix(self, bot, command_prefix):
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
    async def test_rules_with_prefix(self, bot, command_prefix):
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
    async def test_rules_no_prefix(self, bot, command_prefix):
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
    async def test_rules_dm(self, bot, command_prefix):
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
    async def test_single_board_dm_no_prefix(self, bot, command_prefix):
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
    async def test_single_board_dm_prefix(self, bot, command_prefix):
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
    async def test_single_board_players_no_prefix(self, bot, command_prefix):
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
    async def test_single_players_dm_prefix(self, bot, command_prefix):
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
    async def test_single_increase_range_no_actions_dm_no_prefix(self, bot, command_prefix):
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
    async def test_single_increase_range_no_actions_dm_prefix(self, bot, command_prefix):
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
    async def test_single_increase_range_dm_no_prefix(self, bot, command_prefix):
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
    async def test_single_increase_range_dm_prefix(self, bot, command_prefix):
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

    @pytest.mark.asyncio
    async def test_single_increase_range_dead_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("increase range")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, str(bot.guilds[0].members[2].id))
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You are dead and have no more lives {mess.author.mention}."
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_increase_range_dead_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}increase range")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, str(bot.guilds[0].members[2].id))
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You are dead and have no more lives {mess.author.mention}."
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_move_no_information_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("move")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"Please specify a tile or a direction to move in {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_move_no_information_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}move")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"Please specify a tile or a direction to move in {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_move_too_many_args_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("move some info")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"Invalid information provided for where to go {mess.author.mention}! "
        verifier += "Please specify a tile or a direction to move."
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_move_too_many_args_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}move some info")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"Invalid information provided for where to go {mess.author.mention}! "
        verifier += "Please specify a tile or a direction to move."
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_move_invalid_arg_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        direction: str = "somewhere"
        await channel.send(f"move {direction}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"'{direction}' is not an ordinal direction or a coordinate {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_move_invalid_arg_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        direction: str = "somewhere"
        await channel.send(f"{command_prefix}move {direction}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"'{direction}' is not an ordinal direction or a coordinate {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_move_no_actions_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("move north")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.remove_player_actions(guild_id, channel_id, player_id)
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You have no more actions remaining {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_move_no_actions_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}move north")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.remove_player_actions(guild_id, channel_id, player_id)
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You have no more actions remaining {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_move_north_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        guild_id: str = str(bot.guilds[0].id)
        channel_id = str(bot.guilds[0].text_channels[0].id)
        old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        i, j = 0, 0
        for row in range(len(old_board)):
            for col in range(len(old_board[row])):
                if str(old_board[row][col]) == "1":
                    i = row
                    j = col
                    break
        if i == len(old_board) - 1:
            channel = await utils.JsonUtility.get_private_channel(bot, 2)
            await channel.send("move south")
            mess = dpytest.get_message()
            mess.author = bot.guilds[0].members[2]
            await messageHandler.handle_message(mess, bot, command_prefix)
            dpytest.get_message()
            dpytest.get_message()
            old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
            i, j = 0, 0
            for row in range(len(old_board)):
                for col in range(len(old_board[row])):
                    if str(old_board[row][col]) == "1":
                        i = row
                        j = col
                        break

        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("move north")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You have moved north 1 tile {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)
        response: discord.Message = dpytest.get_message()
        assert len(response.attachments) == 1
        assert response.attachments[0].filename == 'image.png'

        new_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        assert old_board != new_board
        k, w = 0, 0
        for row in range(len(new_board)):
            for col in range(len(new_board[row])):
                if str(new_board[row][col]) == "1":
                    k = row
                    w = col
                    break
        assert k == (i + 1) and w == j

    @pytest.mark.asyncio
    async def test_single_move_north_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        guild_id: str = str(bot.guilds[0].id)
        channel_id = str(bot.guilds[0].text_channels[0].id)
        old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        i, j = 0, 0
        for row in range(len(old_board)):
            for col in range(len(old_board[row])):
                if str(old_board[row][col]) == "1":
                    i = row
                    j = col
                    break
        if i == len(old_board) - 1:
            channel = await utils.JsonUtility.get_private_channel(bot, 2)
            await channel.send(f"{command_prefix}move south")
            mess = dpytest.get_message()
            mess.author = bot.guilds[0].members[2]
            await messageHandler.handle_message(mess, bot, command_prefix)
            dpytest.get_message()
            dpytest.get_message()
            old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
            i, j = 0, 0
            for row in range(len(old_board)):
                for col in range(len(old_board[row])):
                    if str(old_board[row][col]) == "1":
                        i = row
                        j = col
                        break

        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}move north")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You have moved north 1 tile {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)
        response: discord.Message = dpytest.get_message()
        assert len(response.attachments) == 1
        assert response.attachments[0].filename == 'image.png'

        new_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        assert old_board != new_board
        k, w = 0, 0
        for row in range(len(new_board)):
            for col in range(len(new_board[row])):
                if str(new_board[row][col]) == "1":
                    k = row
                    w = col
                    break
        assert k == (i + 1) and w == j

    @pytest.mark.asyncio
    async def test_single_move_south_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        guild_id: str = str(bot.guilds[0].id)
        channel_id = str(bot.guilds[0].text_channels[0].id)
        old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        i, j = 0, 0
        for row in range(len(old_board)):
            for col in range(len(old_board[row])):
                if str(old_board[row][col]) == "1":
                    i = row
                    j = col
                    break
        if i == 0:
            channel = await utils.JsonUtility.get_private_channel(bot, 2)
            await channel.send("move north")
            mess = dpytest.get_message()
            mess.author = bot.guilds[0].members[2]
            await messageHandler.handle_message(mess, bot, command_prefix)
            dpytest.get_message()
            dpytest.get_message()
            old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
            i, j = 0, 0
            for row in range(len(old_board)):
                for col in range(len(old_board[row])):
                    if str(old_board[row][col]) == "1":
                        i = row
                        j = col
                        break

        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("move south")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You have moved south 1 tile {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)
        response: discord.Message = dpytest.get_message()
        assert len(response.attachments) == 1
        assert response.attachments[0].filename == 'image.png'

        new_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        assert old_board != new_board
        k, w = 0, 0
        for row in range(len(new_board)):
            for col in range(len(new_board[row])):
                if str(new_board[row][col]) == "1":
                    k = row
                    w = col
                    break
        assert k == (i - 1) and w == j

    @pytest.mark.asyncio
    async def test_single_move_south_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        guild_id: str = str(bot.guilds[0].id)
        channel_id = str(bot.guilds[0].text_channels[0].id)
        old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        i, j = 0, 0
        for row in range(len(old_board)):
            for col in range(len(old_board[row])):
                if str(old_board[row][col]) == "1":
                    i = row
                    j = col
                    break
        if i == 0:
            channel = await utils.JsonUtility.get_private_channel(bot, 2)
            await channel.send(f"{command_prefix}move north")
            mess = dpytest.get_message()
            mess.author = bot.guilds[0].members[2]
            await messageHandler.handle_message(mess, bot, command_prefix)
            dpytest.get_message()
            dpytest.get_message()
            old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
            i, j = 0, 0
            for row in range(len(old_board)):
                for col in range(len(old_board[row])):
                    if str(old_board[row][col]) == "1":
                        i = row
                        j = col
                        break

        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}move south")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You have moved south 1 tile {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)
        response: discord.Message = dpytest.get_message()
        assert len(response.attachments) == 1
        assert response.attachments[0].filename == 'image.png'

        new_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        assert old_board != new_board
        k, w = 0, 0
        for row in range(len(new_board)):
            for col in range(len(new_board[row])):
                if str(new_board[row][col]) == "1":
                    k = row
                    w = col
                    break
        assert k == (i - 1) and w == j

    @pytest.mark.asyncio
    async def test_single_move_west_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        guild_id: str = str(bot.guilds[0].id)
        channel_id = str(bot.guilds[0].text_channels[0].id)
        old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        i, j = 0, 0
        for row in range(len(old_board)):
            for col in range(len(old_board[row])):
                if str(old_board[row][col]) == "1":
                    i = row
                    j = col
                    break
        if j == 0:
            channel = await utils.JsonUtility.get_private_channel(bot, 2)
            await channel.send("move east")
            mess = dpytest.get_message()
            mess.author = bot.guilds[0].members[2]
            await messageHandler.handle_message(mess, bot, command_prefix)
            dpytest.get_message()
            dpytest.get_message()
            old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
            i, j = 0, 0
            for row in range(len(old_board)):
                for col in range(len(old_board[row])):
                    if str(old_board[row][col]) == "1":
                        i = row
                        j = col
                        break

        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("move west")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You have moved west 1 tile {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)
        response: discord.Message = dpytest.get_message()
        assert len(response.attachments) == 1
        assert response.attachments[0].filename == 'image.png'

        new_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        assert old_board != new_board
        k, w = 0, 0
        for row in range(len(new_board)):
            for col in range(len(new_board[row])):
                if str(new_board[row][col]) == "1":
                    k = row
                    w = col
                    break
        assert k == i and w == (j - 1)

    @pytest.mark.asyncio
    async def test_single_move_west_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        guild_id: str = str(bot.guilds[0].id)
        channel_id = str(bot.guilds[0].text_channels[0].id)
        old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        i, j = 0, 0
        for row in range(len(old_board)):
            for col in range(len(old_board[row])):
                if str(old_board[row][col]) == "1":
                    i = row
                    j = col
                    break
        if j == 0:
            channel = await utils.JsonUtility.get_private_channel(bot, 2)
            await channel.send(f"{command_prefix}move east")
            mess = dpytest.get_message()
            mess.author = bot.guilds[0].members[2]
            await messageHandler.handle_message(mess, bot, command_prefix)
            dpytest.get_message()
            dpytest.get_message()
            old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
            i, j = 0, 0
            for row in range(len(old_board)):
                for col in range(len(old_board[row])):
                    if str(old_board[row][col]) == "1":
                        i = row
                        j = col
                        break

        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}move west")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You have moved west 1 tile {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)
        response: discord.Message = dpytest.get_message()
        assert len(response.attachments) == 1
        assert response.attachments[0].filename == 'image.png'

        new_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        assert old_board != new_board
        k, w = 0, 0
        for row in range(len(new_board)):
            for col in range(len(new_board[row])):
                if str(new_board[row][col]) == "1":
                    k = row
                    w = col
                    break
        assert k == i and w == (j - 1)

    @pytest.mark.asyncio
    async def test_single_move_east_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        guild_id: str = str(bot.guilds[0].id)
        channel_id = str(bot.guilds[0].text_channels[0].id)
        old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        i, j = 0, 0
        for row in range(len(old_board)):
            for col in range(len(old_board[row])):
                if str(old_board[row][col]) == "1":
                    i = row
                    j = col
                    break
        if j == len(old_board[0]) - 1:
            channel = await utils.JsonUtility.get_private_channel(bot, 2)
            await channel.send("move west")
            mess = dpytest.get_message()
            mess.author = bot.guilds[0].members[2]
            await messageHandler.handle_message(mess, bot, command_prefix)
            dpytest.get_message()
            dpytest.get_message()
            old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
            i, j = 0, 0
            for row in range(len(old_board)):
                for col in range(len(old_board[row])):
                    if str(old_board[row][col]) == "1":
                        i = row
                        j = col
                        break

        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("move east")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You have moved east 1 tile {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)
        response: discord.Message = dpytest.get_message()
        assert len(response.attachments) == 1
        assert response.attachments[0].filename == 'image.png'

        new_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        assert old_board != new_board
        k, w = 0, 0
        for row in range(len(new_board)):
            for col in range(len(new_board[row])):
                if str(new_board[row][col]) == "1":
                    k = row
                    w = col
                    break
        assert k == i and w == (j + 1)

    @pytest.mark.asyncio
    async def test_single_move_east_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        guild_id: str = str(bot.guilds[0].id)
        channel_id = str(bot.guilds[0].text_channels[0].id)
        old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        i, j = 0, 0
        for row in range(len(old_board)):
            for col in range(len(old_board[row])):
                if str(old_board[row][col]) == "1":
                    i = row
                    j = col
                    break
        if j == len(old_board[0]) - 1:
            channel = await utils.JsonUtility.get_private_channel(bot, 2)
            await channel.send(f"{command_prefix}move west")
            mess = dpytest.get_message()
            mess.author = bot.guilds[0].members[2]
            await messageHandler.handle_message(mess, bot, command_prefix)
            dpytest.get_message()
            dpytest.get_message()
            old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
            i, j = 0, 0
            for row in range(len(old_board)):
                for col in range(len(old_board[row])):
                    if str(old_board[row][col]) == "1":
                        i = row
                        j = col
                        break

        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}move east")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You have moved east 1 tile {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)
        response: discord.Message = dpytest.get_message()
        assert len(response.attachments) == 1
        assert response.attachments[0].filename == 'image.png'

        new_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        assert old_board != new_board
        k, w = 0, 0
        for row in range(len(new_board)):
            for col in range(len(new_board[row])):
                if str(new_board[row][col]) == "1":
                    k = row
                    w = col
                    break
        assert k == i and w == (j + 1)

    @pytest.mark.asyncio
    async def test_single_move_easter_egg_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        guild_id: str = str(bot.guilds[0].id)
        channel_id = str(bot.guilds[0].text_channels[0].id)
        old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)

        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("move weast")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"I am sorry {mess.author.mention}, but you do not have the power to move weast."
        assert dpytest.verify().message().content(verifier)

        new_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        assert old_board == new_board

    @pytest.mark.asyncio
    async def test_single_move_easter_egg_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        guild_id: str = str(bot.guilds[0].id)
        channel_id = str(bot.guilds[0].text_channels[0].id)
        old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)

        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}move weast")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"I am sorry {mess.author.mention}, but you do not have the power to move weast."
        assert dpytest.verify().message().content(verifier)

        new_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        assert old_board == new_board

    @pytest.mark.asyncio
    async def test_single_move_not_alive_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        guild_id: str = str(bot.guilds[0].id)
        channel_id = str(bot.guilds[0].text_channels[0].id)
        old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)

        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}move north")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        utils.JsonUtility.kill_player(guild_id, channel_id, str(bot.guilds[0].members[2].id))

        await messageHandler.handle_message(mess, bot, command_prefix)
        verifier: str = f"You are dead and have no more lives {mess.author.mention}."
        assert dpytest.verify().message().content(verifier)

        new_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        assert old_board == new_board

    @pytest.mark.asyncio
    async def test_single_move_not_alive_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        guild_id: str = str(bot.guilds[0].id)
        channel_id = str(bot.guilds[0].text_channels[0].id)
        old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)

        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}move north")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        utils.JsonUtility.kill_player(guild_id, channel_id, str(bot.guilds[0].members[2].id))

        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You are dead and have no more lives {mess.author.mention}."
        assert dpytest.verify().message().content(verifier)

        new_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
        assert old_board == new_board

    @pytest.mark.asyncio
    async def test_single_shoot_no_args_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("shoot")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"Please specify a tile, player, or a direction to shoot at {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_no_args_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}shoot")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"Please specify a tile, player, or a direction to shoot at {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_too_many_args_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("shoot someone somewhere")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"Invalid information provided for where to shoot {mess.author.mention}! "
        verifier += "Please specify a tile, player, or a direction to shoot."
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_too_many_args_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}shoot someone somewhere")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"Invalid information provided for where to shoot {mess.author.mention}! "
        verifier += "Please specify a tile, player, or a direction to shoot."
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_no_actions_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("shoot 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(mess.author.id)
        utils.JsonUtility.remove_player_actions(guild_id, channel_id, player_id)
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You have no more actions remaining {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_no_actions_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}shoot 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(mess.author.id)
        utils.JsonUtility.remove_player_actions(guild_id, channel_id, player_id)
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You have no more actions remaining {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_no_player_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        non_player: str = "someone"
        await channel.send(f"shoot {non_player}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"That player is not currently in the game {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_no_player_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        non_player: str = "someone"
        await channel.send(f"{command_prefix}shoot {non_player}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"That player is not currently in the game {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_self_mention_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}shoot {bot.guilds[0].members[2].mention}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You cannot @ people in direct messages {mess.author.mention}! "
        verifier += f"Please use their in-game player-number found on {command_prefix}players"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_self_mention_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"shoot {bot.guilds[0].members[2].mention}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You cannot @ people in direct messages {mess.author.mention}! "
        verifier += f"Please use their in-game player-number found on {command_prefix}players"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_self_number_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("shoot 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You cannot shoot your own player {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_self_number_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}shoot 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You cannot shoot your own player {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_out_of_range_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        enemy_player_number: int = 2
        await channel.send(f"shoot {enemy_player_number}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        utils.JsonUtility.move_players_away(guild_id, channel_id)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"Player {enemy_player_number} is out of range {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_out_of_range_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        enemy_player_number: int = 2
        await channel.send(f"{command_prefix}shoot {enemy_player_number}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        utils.JsonUtility.move_players_away(guild_id, channel_id)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"Player {enemy_player_number} is out of range {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_mention_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"shoot {bot.guilds[0].members[3].mention}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        utils.JsonUtility.move_players_together(guild_id, channel_id)
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You cannot @ people in direct messages {mess.author.mention}! "
        verifier += f"Please use their in-game player-number found on {command_prefix}players"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_mention_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}shoot {bot.guilds[0].members[3].mention}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        utils.JsonUtility.move_players_together(guild_id, channel_id)
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You cannot @ people in direct messages {mess.author.mention}! "
        verifier += f"Please use their in-game player-number found on {command_prefix}players"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_shoot_number_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        enemy_player_number: int = 2
        await channel.send(f"shoot {enemy_player_number}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        utils.JsonUtility.move_players_together(guild_id, channel_id)
        await messageHandler.handle_message(mess, bot, command_prefix)

        verifier: str = f"Player {bot.guilds[0].members[3].mention} has been shot by {mess.author.mention}! "
        verifier += "They now have 2♥ lives left."
        verifier_dm: str = f"Player {bot.guilds[0].members[3].mention} has been shot! They now have 2♥ lives left."
        response = dpytest.get_message()
        second_response = dpytest.get_message()
        assert response.channel.type == discord.ChannelType.private
        assert response.content == verifier_dm
        assert second_response.channel.type == discord.ChannelType.text
        assert second_response.content == verifier

    @pytest.mark.asyncio
    async def test_single_shoot_number_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        enemy_player_number: int = 2
        await channel.send(f"{command_prefix}shoot {enemy_player_number}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        utils.JsonUtility.move_players_together(guild_id, channel_id)
        await messageHandler.handle_message(mess, bot, command_prefix)

        verifier: str = f"Player {bot.guilds[0].members[3].mention} has been shot by {mess.author.mention}! "
        verifier += "They now have 2♥ lives left."
        verifier_dm: str = f"Player {bot.guilds[0].members[3].mention} has been shot! They now have 2♥ lives left."
        response = dpytest.get_message()
        second_response = dpytest.get_message()
        assert response.channel.type == discord.ChannelType.private
        assert response.content == verifier_dm
        assert second_response.channel.type == discord.ChannelType.text
        assert second_response.content == verifier

    @pytest.mark.asyncio
    async def test_single_vote_alive_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("vote")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = (f"Only players with no more lives may vote on an extra action for a player "
                         f"{mess.author.mention}.")
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_vote_alive_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}vote")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = (f"Only players with no more lives may vote on an extra action for a player "
                         f"{mess.author.mention}.")
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_vote_no_info_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("vote")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        assert dpytest.verify().message().content(f"Please specify a player to vote for {mess.author.mention}.")

    @pytest.mark.asyncio
    async def test_single_vote_no_info_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}vote")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        assert dpytest.verify().message().content(f"Please specify a player to vote for {mess.author.mention}.")

    @pytest.mark.asyncio
    async def test_single_vote_no_player_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("vote")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        assert dpytest.verify().message().content(f"Please specify a player to vote for {mess.author.mention}.")

    @pytest.mark.asyncio
    async def test_single_vote_no_player_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}vote")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        assert dpytest.verify().message().content(f"Please specify a player to vote for {mess.author.mention}.")

    @pytest.mark.asyncio
    async def test_single_vote_non_existing_player_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        bad_name: str = "some_random_person"
        await channel.send(f"vote {bad_name}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        assert dpytest.verify().message().content(f"*{bad_name}* is not a player {mess.author.mention}!")

    @pytest.mark.asyncio
    async def test_single_vote_non_existing_player_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        bad_name: str = "some_random_person"
        await channel.send(f"{command_prefix}vote {bad_name}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        assert dpytest.verify().message().content(f"*{bad_name}* is not a player {mess.author.mention}!")

    @pytest.mark.asyncio
    async def test_single_vote_no_remaining_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"vote {bot.guilds[0].members[2].id}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        assert dpytest.verify().message().content(f"You have no more remaining votes today {mess.author.mention}!")

    @pytest.mark.asyncio
    async def test_single_vote_no_remaining_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}vote {bot.guilds[0].members[2].id}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        assert dpytest.verify().message().content(f"You have no more remaining votes today {mess.author.mention}!")

    @pytest.mark.asyncio
    async def test_single_vote_self_mention_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"vote {bot.guilds[0].members[2].mention}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        utils.JsonUtility.give_dead_player_vote(str(bot.guilds[0].id), str(bot.guilds[0].text_channels[0].id),
                                                str(bot.guilds[0].members[2].id), 1)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = (f"You cannot vote for players using @ in a direct message {mess.author.mention}! "
                         f"Please use player-number instead")
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_vote_self_mention_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}vote {bot.guilds[0].members[2].mention}")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        utils.JsonUtility.give_dead_player_vote(str(bot.guilds[0].id), str(bot.guilds[0].text_channels[0].id),
                                                str(bot.guilds[0].members[2].id), 1)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = (f"You cannot vote for players using @ in a direct message {mess.author.mention}! "
                         f"Please use player-number instead")
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_vote_self_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("vote 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        utils.JsonUtility.give_dead_player_vote(str(bot.guilds[0].id), str(bot.guilds[0].text_channels[0].id),
                                                str(bot.guilds[0].members[2].id), 1)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        assert dpytest.verify().message().content(f"You may not vote for yourself {mess.author.mention}!")

    @pytest.mark.asyncio
    async def test_single_vote_self_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}vote 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        utils.JsonUtility.give_dead_player_vote(str(bot.guilds[0].id), str(bot.guilds[0].text_channels[0].id),
                                                str(bot.guilds[0].members[2].id), 1)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        assert dpytest.verify().message().content(f"You may not vote for yourself {mess.author.mention}!")

    @pytest.mark.asyncio
    async def test_single_vote_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("vote 2")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        utils.JsonUtility.give_dead_player_vote(str(bot.guilds[0].id), str(bot.guilds[0].text_channels[0].id),
                                                str(bot.guilds[0].members[2].id), 1)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"Your vote for {bot.guilds[0].members[3].mention} to receive 1 extra action has been counted."
        assert dpytest.verify().message().content(verifier)

        data = utils.JsonUtility.get_player_stats(mess, guild_id, channel_id, player_id)
        assert int(data['remainingVotes']) == 0
        data = utils.JsonUtility.get_player_stats(mess, guild_id, channel_id, str(bot.guilds[0].members[3].id))
        assert int(data['votes']) == 1

    @pytest.mark.asyncio
    async def test_single_vote_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}vote 2")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]

        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        player_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
        utils.JsonUtility.give_dead_player_vote(str(bot.guilds[0].id), str(bot.guilds[0].text_channels[0].id),
                                                str(bot.guilds[0].members[2].id), 1)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"Your vote for {bot.guilds[0].members[3].mention} to receive 1 extra action has been counted."
        assert dpytest.verify().message().content(verifier)

        data = utils.JsonUtility.get_player_stats(mess, guild_id, channel_id, player_id)
        assert int(data['remainingVotes']) == 0
        data = utils.JsonUtility.get_player_stats(mess, guild_id, channel_id, str(bot.guilds[0].members[3].id))
        assert int(data['votes']) == 1

    @pytest.mark.asyncio
    async def test_single_send_no_info_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}send")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        notification: str = f"Invalid command {mess.author.mention}! "
        notification += "Please use */send [player number] [number of actions]"
        assert dpytest.verify().message().content(notification)

    @pytest.mark.asyncio
    async def test_single_send_no_info_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("send")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        notification: str = f"Invalid command {mess.author.mention}! "
        notification += "Please use */send [player number] [number of actions]"
        assert dpytest.verify().message().content(notification)

    @pytest.mark.asyncio
    async def test_single_send_too_much_info_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("send some random information")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        notification: str = f"Invalid command {mess.author.mention}! "
        notification += "Please use */send [player number] [number of actions]"
        assert dpytest.verify().message().content(notification)

    @pytest.mark.asyncio
    async def test_single_send_too_much_info_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}send some random information")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        notification: str = f"Invalid command {mess.author.mention}! "
        notification += "Please use */send [player number] [number of actions]"
        assert dpytest.verify().message().content(notification)

    @pytest.mark.asyncio
    async def test_single_send_no_player_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("send some_random_player 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        notification: str = f"Invalid player number given {mess.author.mention}"
        assert dpytest.verify().message().content(notification)

    @pytest.mark.asyncio
    async def test_single_send_no_player_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}send some_random_player 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        notification: str = f"Invalid player number given {mess.author.mention}"
        assert dpytest.verify().message().content(notification)

    @pytest.mark.asyncio
    async def test_single_send_mention_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"send {bot.guilds[0].members[3].mention} 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You cannot @ people in direct messages {mess.author.mention}! "
        verifier += f"Please use their in-game player-number found on {command_prefix}players"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_send_mention_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}send {bot.guilds[0].members[3].mention} 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You cannot @ people in direct messages {mess.author.mention}! "
        verifier += f"Please use their in-game player-number found on {command_prefix}players"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_send_mention_not_in_game_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"send {bot.guilds[0].members[1].mention} 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You cannot @ people in direct messages {mess.author.mention}! "
        verifier += f"Please use their in-game player-number found on {command_prefix}players"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_send_mention_not_in_game_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}send {bot.guilds[0].members[1].mention} 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"You cannot @ people in direct messages {mess.author.mention}! "
        verifier += f"Please use their in-game player-number found on {command_prefix}players"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_send_not_in_game_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("send 6 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"6 is not a player number in this game {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_send_not_in_game_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}send 6 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        verifier: str = f"6 is not a player number in this game {mess.author.mention}!"
        assert dpytest.verify().message().content(verifier)

    @pytest.mark.asyncio
    async def test_single_send_number_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("send 2 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        notification: str = f"{mess.author.mention} gave 1 actions to {bot.guilds[0].members[3].mention}"
        assert dpytest.verify().message().content(notification)

        data = utils.JsonUtility.get_player_stats(mess, bot.guilds[0].id, bot.guilds[0].channels[0].id,
                                                  str(bot.guilds[0].members[2].id))
        assert int(data['actions']) == 0
        data = utils.JsonUtility.get_player_stats(mess, bot.guilds[0].id, bot.guilds[0].channels[0].id,
                                                  str(bot.guilds[0].members[3].id))
        assert int(data['actions']) == 2

    @pytest.mark.asyncio
    async def test_single_send_number_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}send 2 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        notification: str = f"{mess.author.mention} gave 1 actions to {bot.guilds[0].members[3].mention}"
        assert dpytest.verify().message().content(notification)

        data = utils.JsonUtility.get_player_stats(mess, bot.guilds[0].id, bot.guilds[0].channels[0].id,
                                                  str(bot.guilds[0].members[2].id))
        assert int(data['actions']) == 0
        data = utils.JsonUtility.get_player_stats(mess, bot.guilds[0].id, bot.guilds[0].channels[0].id,
                                                  str(bot.guilds[0].members[3].id))
        assert int(data['actions']) == 2

    @pytest.mark.asyncio
    async def test_single_send_self_player_number_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("send 1 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        notification: str = f"You may not send actions to yourself {mess.author.mention}!"
        assert dpytest.verify().message().content(notification)

    @pytest.mark.asyncio
    async def test_single_send_self_player_number_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}send 1 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        notification: str = f"You may not send actions to yourself {mess.author.mention}!"
        assert dpytest.verify().message().content(notification)

    @pytest.mark.asyncio
    async def test_single_send_no_actions_dm_no_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send("send 2 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        member_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.remove_player_actions(guild_id, channel_id, member_id)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        notification: str = f"You do not have enough actions to do that {mess.author.mention}!"
        assert dpytest.verify().message().content(notification)

        data = utils.JsonUtility.get_player_stats(mess, guild_id, channel_id,
                                                  str(bot.guilds[0].members[2].id))
        assert int(data['actions']) == 0
        data = utils.JsonUtility.get_player_stats(mess, guild_id, channel_id,
                                                  str(bot.guilds[0].members[3].id))
        assert int(data['actions']) == 1

    @pytest.mark.asyncio
    async def test_single_send_no_actions_dm_prefix(self, bot, command_prefix):
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}send 2 1")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        guild_id: str = str(bot.guilds[0].id)
        channel_id: str = str(bot.guilds[0].text_channels[0].id)
        member_id: str = str(bot.guilds[0].members[2].id)
        utils.JsonUtility.remove_player_actions(guild_id, channel_id, member_id)
        await messageHandler.handle_message(mess, bot, command_prefix)
        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        notification: str = f"You do not have enough actions to do that {mess.author.mention}!"
        assert dpytest.verify().message().content(notification)

        data = utils.JsonUtility.get_player_stats(mess, guild_id, channel_id,
                                                  str(bot.guilds[0].members[2].id))
        assert int(data['actions']) == 0
        data = utils.JsonUtility.get_player_stats(mess, guild_id, channel_id,
                                                  str(bot.guilds[0].members[3].id))
        assert int(data['actions']) == 1


class TestMultipleActiveGames:
    @pytest.mark.asyncio
    async def test_multiple_board_dm(self, bot, command_prefix):
        await utils.JsonUtility.start_multiple_sample_games(bot, command_prefix)
        channel = await utils.JsonUtility.get_private_channel(bot, 2)
        await channel.send(f"{command_prefix}board")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        await messageHandler.handle_message(mess, bot, command_prefix)

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        mess = dpytest.get_message()
        assert mess.content == f"Please select a game {bot.guilds[0].members[2].mention}."

        await channel.send(f"{command_prefix}board")
        mess = dpytest.get_message()
        mess.author = bot.guilds[0].members[2]
        server = jsonManager.get_player_server_channels(mess)[0]
        await commands.dm_multiple_commands(bot, mess, server[0], server[1])

        assert dpytest.get_message(peek=True).channel.type == discord.ChannelType.private
        mess = dpytest.get_message()
        assert len(mess.attachments) == 1
        assert mess.attachments[0].filename == 'image.png'
