"""
Integration tests for command interaction and interfacing generically
"""
import asyncio

import discord.ext.test as dpytest
import pytest

import main
from src.tanks.libraries import messageHandler


@pytest.mark.asyncio
async def test_not_command(bot, command_prefix):
    channel = bot.guilds[0].text_channels[0]
    await channel.send("Hello, World!")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().nothing()


@pytest.mark.asyncio
async def test_mentioned(bot, command_prefix):
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{bot.user.mention}")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().nothing()


@pytest.mark.asyncio
async def test_extra_marks(bot, command_prefix):
    channel = bot.guilds[0].text_channels[0]
    await channel.send(f"{command_prefix}{command_prefix}")
    mess = dpytest.get_message()
    await messageHandler.handle_message(mess, bot, command_prefix)
    assert dpytest.verify().message().nothing()


@pytest.mark.asyncio
@pytest.mark.cogs("cogs.message")
async def test_queue(full_bot, command_prefix):
    guild = full_bot.guilds[0]
    channel = guild.text_channels[0]

    assert main.messageQueue.unfinished_tasks == 0
    assert len(main.messageQueue.queue) == 0
    await channel.send("Hey!")
    main.messageQueue.put(dpytest.get_message())
    assert main.messageQueue.unfinished_tasks == 1
    assert len(main.messageQueue.queue) == 1
    asyncio.create_task(main.__handle_queue__(full_bot, command_prefix))
    await asyncio.sleep(2)
    await dpytest.run_all_events()
    assert len(main.messageQueue.queue) == 0
