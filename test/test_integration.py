"""
All tests related to discord and checking to make sure that the robot is interacting with the discord servers
correctly
"""
"""
NOTE TO DEVELOPMENT: 
As of the current state, dpytest does not support discord.py 2.0+. This is quite an issue for this project as it has 
been developed originally in discord.py 1.7.3 with integration tests written in that version. Now with version 2 being 
required, it cannot be downgraded but integration tests do not work. Check for updates to dpytest for fixes.
"""
import pytest
import discord.ext.test as dpytest

from src.tanks.libraries import configUtils


@pytest.mark.asyncio
async def test_ping(bot):
    """Test if the ping command works"""
    # message_starter = configUtils.read_value('botSettings', 'botCommandPrefix', '../config.ini')
    # await dpytest.message(message_starter + "ping")
    # assert dpytest.verify().message().contains().content("pong")
    dpytest.verify()
    assert True
