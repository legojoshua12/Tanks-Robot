"""Conftest setup for integration testing"""
import glob
import os
import pytest
import discord
from discord.client import _LoopSentinel

import src.tanks.libraries.configUtils as cfgUtils

import discord.ext.test as dpytest
import pytest_asyncio
from discord.ext import commands


@pytest.fixture(autouse=True)
def run_around_tests() -> None:
    """Fixture for each test setup and teardown of json file."""
    # Runs before each test
    if os.path.exists("Games.json"):
        os.remove("Games.json")
    with open('Games.json', 'w') as f:
        f.write('{}')
    f.close()
    if os.path.exists("PlayerData.json"):
        os.remove("PlayerData.json")
    with open('PlayerData.json', 'w') as f:
        f.write('{}')
    f.close()
    yield
    # Runs after each test
    if os.path.exists("Games.json"):
        os.remove("Games.json")
    if os.path.exists("PlayerData.json"):
        os.remove("PlayerData.json")


@pytest_asyncio.fixture
async def bot(request, event_loop):
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    b = commands.Bot(command_prefix=get_command_prefix(), event_loop=event_loop, intents=intents)
    await b._async_setup_hook()

    dpytest.configure(b)
    return b


@pytest_asyncio.fixture(autouse=True)
async def cleanup():
    yield
    await dpytest.empty_queue()


@pytest_asyncio.fixture
async def full_bot(request):
    intents = discord.Intents.all()
    b = commands.Bot(command_prefix=get_command_prefix(), intents=intents)
    # set up the loop
    if isinstance(b.loop, _LoopSentinel):
        await b._async_setup_hook()

    marks = request.function.pytestmark
    mark = None
    for mark in marks:
        if mark.name == "cogs":
            break

    if mark is not None:
        for extension in mark.args:
            await b.load_extension("test.integration.internal." + extension)

    dpytest.configure(b)
    return b


@pytest.fixture
def command_prefix() -> str:
    return cfgUtils.read_value('botSettings', 'botCommandPrefix')


@pytest.fixture
def is_admin() -> bool:
    val: str = cfgUtils.read_value('startGame', 'adminTesting')
    return True if val.lower() == "true" else False


def get_command_prefix() -> str:
    return cfgUtils.read_value('botSettings', 'botCommandPrefix')


def pytest_sessionfinish() -> None:
    """Clean up files"""
    files = glob.glob('./dpytest_*.dat')
    for path in files:
        try:
            os.remove(path)
        except Exception as e:
            print(f"Error while deleting file {path}: {e}")
