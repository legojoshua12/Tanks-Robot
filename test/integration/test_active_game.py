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
    # TODO WTF?! This works but if you remove the try again clause it fails
    try:
        await utils.JsonUtility.start_sample_game(bot, command_prefix)
    except Exception:
        print("trying again")
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


# TODO Look into dpytest and verifying messages that contain emojis
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
    print(dpytest.get_message(peek=True).content)
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
