"""
Tests for all bot interactions when an active game is created in a channel
"""
import discord
import discord.ext.test as dpytest
import pytest

import test.utilstest as utils

from src.tanks.libraries import messageHandler, commands


@pytest.mark.asyncio
async def test_help_not_in_game(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}help")
    mess = dpytest.get_message()

    await messageHandler.handle_message(mess, bot, command_prefix)
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.active_game_help_embed(embeds[0].color, command_prefix)
    assert dpytest.verify().message().contains().embed(new_embed)


@pytest.mark.asyncio
async def test_help(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}help")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    await messageHandler.handle_message(mess, bot, command_prefix)
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.active_game_help_embed(embeds[0].color, command_prefix)
    assert dpytest.verify().message().contains().embed(new_embed)


@pytest.mark.asyncio
async def test_rules_not_in_game(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}rules")
    mess = dpytest.get_message()

    await messageHandler.handle_message(mess, bot, command_prefix)
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.make_rules_embed(embeds[0].color)
    assert dpytest.verify().message().contains().embed(new_embed)


@pytest.mark.asyncio
async def test_rules(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}rules")
    mess = dpytest.get_message()

    await messageHandler.handle_message(mess, bot, command_prefix)
    embeds = dpytest.get_message(peek=True).embeds
    assert len(embeds) == 1
    new_embed = commands.make_rules_embed(embeds[0].color)
    assert dpytest.verify().message().contains().embed(new_embed)


@pytest.mark.asyncio
async def test_board(bot, command_prefix):
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
async def test_players(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}players")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    message_embeds = dpytest.get_message(peek=True).embeds
    assert len(message_embeds) == 1
    assert dpytest.verify().message().embed(message_embeds[0])


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
async def test_increase_range_no_actions(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}increase range")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    member_id: str = str(bot.guilds[0].members[2].id)
    utils.JsonUtility.remove_player_actions(guild_id, channel_id, member_id)
    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"You do not have any actions to increase your range {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_increase_range(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}increase range")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    previous_range = utils.JsonUtility.get_player_range(mess)
    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"Your range is now {previous_range + 1} tiles {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_move_no_information(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}move")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"Please specify a tile or a direction to move in {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_move_too_many_args(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}move some info")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"Invalid information provided for where to go {mess.author.mention}! "
    verifier += "Please specify a tile or a direction to move."
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_move_invalid_arg(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    direction: str = "somewhere"
    await channel.send(f"{command_prefix}move {direction}")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"'{direction}' is not an ordinal direction or a coordinate {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_move_no_actions(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}move north")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    player_id: str = str(bot.guilds[0].members[2].id)
    utils.JsonUtility.remove_player_actions(guild_id, channel_id, player_id)

    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"You have no more actions remaining {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_move_north(bot, command_prefix):
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
    if i == len(old_board)-1:
        channel = bot.guilds[0].text_channels[0]
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

    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}move north")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    await messageHandler.handle_message(mess, bot, command_prefix)
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
    assert k == (i+1) and w == j


@pytest.mark.asyncio
async def test_move_south(bot, command_prefix):
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
        channel = bot.guilds[0].text_channels[0]
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

    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}move south")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    await messageHandler.handle_message(mess, bot, command_prefix)
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
    assert k == (i-1) and w == j


@pytest.mark.asyncio
async def test_move_west(bot, command_prefix):
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
        channel = bot.guilds[0].text_channels[0]
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

    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}move west")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    await messageHandler.handle_message(mess, bot, command_prefix)
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
    assert k == i and w == (j-1)


@pytest.mark.asyncio
async def test_move_east(bot, command_prefix):
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
    if j == len(old_board[0])-1:
        channel = bot.guilds[0].text_channels[0]
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

    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}move east")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    await messageHandler.handle_message(mess, bot, command_prefix)
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
    assert k == i and w == (j+1)


@pytest.mark.asyncio
async def test_move_easter_egg(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    guild_id: str = str(bot.guilds[0].id)
    channel_id = str(bot.guilds[0].text_channels[0].id)
    old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)

    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}move weast")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"I am sorry {mess.author.mention}, but you do not have the power to move weast."
    assert dpytest.verify().message().content(verifier)

    new_board = utils.JsonUtility.get_game_board(guild_id, channel_id)
    assert old_board == new_board


@pytest.mark.asyncio
async def test_move_not_alive(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    guild_id: str = str(bot.guilds[0].id)
    channel_id = str(bot.guilds[0].text_channels[0].id)
    old_board = utils.JsonUtility.get_game_board(guild_id, channel_id)

    channel = bot.guilds[0].text_channels[0]
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
async def test_shoot_no_args(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}shoot")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"Please specify a tile, player, or a direction to shoot at {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_shoot_too_many_args(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}shoot someone somewhere")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"Invalid information provided for where to shoot {mess.author.mention}! "
    verifier += "Please specify a tile, player, or a direction to shoot."
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_shoot_no_actions(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}shoot 1")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    player_id: str = str(mess.author.id)
    utils.JsonUtility.remove_player_actions(guild_id, channel_id, player_id)
    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"You have no more actions remaining {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_shoot_no_player(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    non_player: str = "someone"
    await channel.send(f"{command_prefix}shoot {non_player}")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"`{non_player}` is not a player {mess.author.mention}! "
    verifier += "Please specify a tile, player, or a direction to shoot."
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_shoot_self_mention(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}shoot {bot.guilds[0].members[2].mention}")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"You cannot shoot your own player {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_shoot_self_number(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}shoot 1")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"You cannot shoot your own player {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_shoot_out_of_range(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    enemy_player_number: int = 2
    await channel.send(f"{command_prefix}shoot {enemy_player_number}")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    utils.JsonUtility.move_players_away(guild_id, channel_id)
    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"Player {enemy_player_number} is out of range {mess.author.mention}!"
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_shoot_mention(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}shoot {bot.guilds[0].members[3].mention}")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    utils.JsonUtility.move_players_together(guild_id, channel_id)
    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"Player {bot.guilds[0].members[3].mention} has been shot! They now have 2♥ lives left."
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_shoot_number(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    enemy_player_number: int = 2
    await channel.send(f"{command_prefix}shoot {enemy_player_number}")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    utils.JsonUtility.move_players_together(guild_id, channel_id)
    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"Player {bot.guilds[0].members[3].mention} has been shot! They now have 2♥ lives left."
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_vote_alive(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}vote")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = f"Only players with no more lives may vote on an extra action for a player {mess.author.mention}."
    assert dpytest.verify().message().content(verifier)


@pytest.mark.asyncio
async def test_vote_no_info(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}vote")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    player_id: str = str(bot.guilds[0].members[2].id)
    utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().content(f"Please specify a player to vote for {mess.author.mention}.")


@pytest.mark.asyncio
async def test_vote_no_player(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}vote")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    player_id: str = str(bot.guilds[0].members[2].id)
    utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().content(f"Please specify a player to vote for {mess.author.mention}.")


@pytest.mark.asyncio
async def test_vote_non_existing_player(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}vote some_random_person")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    player_id: str = str(bot.guilds[0].members[2].id)
    utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().content(f"*some_random_person* is not a player {mess.author.mention}!")


@pytest.mark.asyncio
async def test_vote_no_remaining(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}vote {bot.guilds[0].members[2].id}")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    player_id: str = str(bot.guilds[0].members[2].id)
    utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().content(f"You have no more remaining votes today {mess.author.mention}!")


@pytest.mark.asyncio
async def test_vote_self(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
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
    assert dpytest.verify().message().content(f"You may not vote for yourself {mess.author.mention}!")


@pytest.mark.asyncio
async def test_vote_number(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
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
    verifier: str = (f"{bot.guilds[0].members[2].mention} voted for {bot.guilds[0].members[3].mention} "
                     f"to receive 1 extra action.")
    assert dpytest.verify().message().content(verifier)

    data = utils.JsonUtility.get_player_stats(mess, guild_id, channel_id, player_id)
    assert int(data['remainingVotes']) == 0
    data = utils.JsonUtility.get_player_stats(mess, guild_id, channel_id, str(bot.guilds[0].members[3].id))
    assert int(data['votes']) == 1


@pytest.mark.asyncio
async def test_vote_mention(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}vote {bot.guilds[0].members[3].mention}")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]

    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    player_id: str = str(bot.guilds[0].members[2].id)
    utils.JsonUtility.kill_player(guild_id, channel_id, player_id)
    utils.JsonUtility.give_dead_player_vote(str(bot.guilds[0].id), str(bot.guilds[0].text_channels[0].id),
                                            str(bot.guilds[0].members[2].id), 1)
    await messageHandler.handle_message(mess, bot, command_prefix)
    verifier: str = (f"{bot.guilds[0].members[2].mention} voted for {bot.guilds[0].members[3].mention} "
                     f"to receive 1 extra action.")
    assert dpytest.verify().message().content(verifier)

    data = utils.JsonUtility.get_player_stats(mess, guild_id, channel_id, player_id)
    assert int(data['remainingVotes']) == 0
    data = utils.JsonUtility.get_player_stats(mess, guild_id, channel_id, str(bot.guilds[0].members[3].id))
    assert int(data['votes']) == 1


@pytest.mark.asyncio
async def test_send_no_info(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}send")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    notification: str = f"Invalid command {mess.author.mention}! "
    notification += "Please use */send [player or player number] [number of actions]"
    assert dpytest.verify().message().content(notification)


@pytest.mark.asyncio
async def test_send_too_much_info(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}send some random information")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    notification: str = f"Invalid command {mess.author.mention}! "
    notification += "Please use */send [player or player number] [number of actions]"
    assert dpytest.verify().message().content(notification)


@pytest.mark.asyncio
async def test_send_no_player(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}send some_random_player 1")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    notification: str = f"Please specify the player number or @the_player instead {mess.author.mention}!"
    assert dpytest.verify().message().content(notification)


@pytest.mark.asyncio
async def test_send_mention(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}send {bot.guilds[0].members[3].mention} 1")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    notification: str = f"{mess.author.mention} gave 1 actions to {bot.guilds[0].members[3].mention}"
    assert dpytest.verify().message().content(notification)


@pytest.mark.asyncio
async def test_send_mention_not_in_game(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}send {bot.guilds[0].members[1].mention} 1")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    notification: str = f"{bot.guilds[0].members[1].mention} is not in this game {mess.author.mention}!"
    assert dpytest.verify().message().content(notification)


@pytest.mark.asyncio
async def test_send_number(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}send 2 1")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    notification: str = f"{mess.author.mention} gave 1 actions to {bot.guilds[0].members[3].mention}"
    assert dpytest.verify().message().content(notification)


@pytest.mark.asyncio
async def test_send_number_not_in_game(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}send 6 1")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    notification: str = f"6 is not a player number in this game {mess.author.mention}!"
    assert dpytest.verify().message().content(notification)


@pytest.mark.asyncio
async def test_send_self(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}send {bot.guilds[0].members[2].mention} 1")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    notification: str = f"You may not send actions to yourself {mess.author.mention}!"
    assert dpytest.verify().message().content(notification)


@pytest.mark.asyncio
async def test_send_self_player_number(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}send 1 1")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    notification: str = f"You may not send actions to yourself {mess.author.mention}!"
    assert dpytest.verify().message().content(notification)


@pytest.mark.asyncio
async def test_send_no_actions(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}send 2 1")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    guild_id: str = str(bot.guilds[0].id)
    channel_id: str = str(bot.guilds[0].text_channels[0].id)
    member_id: str = str(bot.guilds[0].members[2].id)
    utils.JsonUtility.remove_player_actions(guild_id, channel_id, member_id)
    await messageHandler.handle_message(mess, bot, command_prefix)
    notification: str = f"You do not have enough actions to do that {mess.author.mention}!"
    assert dpytest.verify().message().content(notification)


@pytest.mark.asyncio
async def test_command_not_in_game(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}test")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().content(f"You are not playing in this game {bot.user.mention}!")


@pytest.mark.asyncio
async def test_command_invalid_syntax(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}test")
    mess = dpytest.get_message()
    mess.author = bot.guilds[0].members[2]
    await messageHandler.handle_message(mess, bot, command_prefix)
    verify_message: str = f"{bot.guilds[0].members[2].mention} Unknown command. Please use `{command_prefix}help` "
    verify_message += "to view a list of commands and options."
    assert dpytest.verify().message().content(verify_message)


@pytest.mark.asyncio
async def test_ignored_message(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send('test')
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().nothing()


@pytest.mark.asyncio
async def test_mentioned(bot, command_prefix):
    await utils.JsonUtility.start_sample_game(bot, command_prefix)
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{bot.user.mention}")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().nothing()
