"""
All tests related to discord and checking to make sure that the robot is interacting with the discord servers correctly
"""
import pytest
import discord.ext.test as dpytest


@pytest.mark.asyncio
async def test_ping(bot):
    await dpytest.message("!ping")
    assert dpytest.verify().message().contains().content("pong")
