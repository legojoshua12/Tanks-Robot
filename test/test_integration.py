"""
All tests related to discord and checking to make sure that the robot is interacting with the discord servers
correctly
"""
import pytest
import discord.ext.test as dpytest

from src.tanks.libraries import configUtils


@pytest.mark.asyncio
async def test_ping(bot):
    """Test if the ping command works"""
    messageStarter = configUtils.read_value('botSettings', 'botCommandPrefix', '../config.ini')
    await dpytest.message(messageStarter + "ping")
    assert dpytest.verify().message().contains().content("pong")
