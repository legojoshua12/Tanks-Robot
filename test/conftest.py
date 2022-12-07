"""Conftest setup for integration testing"""
import glob
import os
import pytest
import discord

import src.tanks.libraries.configUtils as cfgUtils
import src.tanks.libraries.messageHandler as msgHandler

import discord.ext.test as dpytest
import pytest_asyncio
from discord.ext import commands
from discord.ext.commands import Cog, command


class Main_Cog(Cog):
    @commands.Cog.listener()
    async def handle_message(self, ctx, text: str):
        await ctx.send(text)


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
    b = commands.Bot(command_prefix=get_command_prefix(), event_loop=event_loop,
                     intents=intents)
    await b._async_setup_hook()
    await b.add_cog(Main_Cog())

    dpytest.configure(b)
    return b


@pytest.fixture
def command_prefix():
    return cfgUtils.read_value('botSettings', 'botCommandPrefix')


def get_command_prefix():
    return cfgUtils.read_value('botSettings', 'botCommandPrefix')


def pytest_sessionfinish():
    """Clean up files"""
    files = glob.glob('./dpytest_*.dat')
    for path in files:
        try:
            os.remove(path)
        except Exception as e:
            print(f"Error while deleting file {path}: {e}")
