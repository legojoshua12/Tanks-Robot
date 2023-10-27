"""Conftest setup for integration testing"""
import glob
import os
from unittest.mock import patch, MagicMock
import psycopg2

import discord
import discord.ext.test as dpytest
import pytest
import pytest_asyncio
from discord.client import _LoopSentinel
from discord.ext import commands

import src.tanks.libraries.configUtils as cfgUtils
from src.tanks.libraries.connectionPool import ConnectionPool


@pytest.fixture(autouse=True)
def run_around_tests() -> None:
    """Fixture for each test setup and teardown of json file."""
    # Runs before each test
    if os.path.exists("PlayerData.json"):
        os.remove("PlayerData.json")
    with open('PlayerData.json', 'w') as f:
        f.write('{}')
    f.close()
    yield
    # Runs after each test
    if os.path.exists("PlayerData.json"):
        os.remove("PlayerData.json")


@pytest.fixture
def mock_db_connection():
    with patch.object(ConnectionPool, '_connection_pool', None):
        mock_pool = MagicMock(spec=psycopg2.pool.SimpleConnectionPool)
        mock_conn = MagicMock(spec=psycopg2.extensions.connection)
        mock_cursor = mock_conn.cursor.return_value
        db_response = []
        mock_cursor.fetchall.return_value = db_response
        mock_pool.getconn.return_value = mock_conn
        with patch('src.tanks.libraries.connectionPool.psycopg2.connect') as mock_connect:
            mock_connect.return_value = mock_conn
            yield mock_pool, mock_cursor, db_response


@pytest.fixture(autouse=True)
def setup_database_tasks(mock_db_connection):
    mock_pool, mock_cursor, db_response = mock_db_connection


@pytest.fixture
def mock_pool(mock_db_connection):
    return mock_db_connection[0]


@pytest.fixture
def mock_cursor(mock_db_connection):
    return mock_db_connection[1]


@pytest.fixture
def db_response(mock_db_connection):
    return mock_db_connection[2]


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
