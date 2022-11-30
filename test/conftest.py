"""Conftest setup for integration testing"""
import glob
import os
import pytest
import discord

import discord.ext.test as dpytest
import pytest_asyncio
from discord.ext import commands


@pytest.fixture(autouse=True)
def run_around_tests():
    # Runs before each test
    with open('Games.json', 'w') as f:
        f.write('{}')
    f.close()
    yield
    # Runs after each test
    if os.path.exists("Games.json"):
        os.remove("Games.json")


@pytest_asyncio.fixture
async def bot(request, event_loop):
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    b = commands.Bot(command_prefix="!", event_loop=event_loop,
                     intents=intents)
    await b._async_setup_hook()

    b.add_command(ping)
    dpytest.configure(b)
    return b


@commands.command()
async def ping(ctx):
    """Send message to a channel where !ping was called"""
    await ctx.send("pong")


def pytest_sessionfinish():
    """Clean up files"""
    files = glob.glob('./dpytest_*.dat')
    for path in files:
        try:
            os.remove(path)
        except Exception as e:
            print(f"Error while deleting file {path}: {e}")