"""Conftest setup for integration testing"""
import asyncio
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

from dotenv import load_dotenv

import src.tanks.libraries.configUtils as cfgUtils
from src.tanks.libraries import jsonManager
from src.tanks.libraries.connectionPool import ConnectionPool


@pytest.fixture
def mock_db_connection(request):
    if "integration" not in request.keywords:
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
    else:
        yield


@pytest.fixture
def mock_putconn():
    connection_pool = ConnectionPool.get_instance()
    with patch.object(connection_pool, 'putconn') as mock_putconn:
        yield mock_putconn


@pytest.fixture(autouse=True)
def setup_database_tasks(request, mock_db_connection):
    if "integration" not in request.keywords:
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


@pytest.fixture(scope='session')
def setUpIntegrationDatabase() -> None:
    load_dotenv()
    database_name: str = os.getenv('TEST_DB_NAME')
    print("DB_NAME:", os.getenv('TEST_DB_NAME'))
    print("DB_USER:", os.getenv('TEST_DB_USER'))
    print("DB_PASSWORD:", os.getenv('TEST_DB_PASSWORD'))
    print("DB_HOST:", os.getenv('TEST_DB_HOST'))
    print("DB_PORT:", os.getenv('TEST_DB_PORT'))
    conn = psycopg2.connect(
        dbname='postgres',
        user=os.getenv('TEST_DB_USER'),
        password=os.getenv('TEST_DB_PASSWORD'),
        host=os.getenv('TEST_DB_HOST'),
        port=os.getenv('TEST_DB_PORT')
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f'DROP DATABASE IF EXISTS "{database_name}" WITH (FORCE)')
    cur.execute(f'CREATE DATABASE "{database_name}"')
    cur.close()
    conn.close()

    os.environ['DB_NAME'] = os.getenv('TEST_DB_NAME')
    os.environ['DB_USER'] = os.getenv('TEST_DB_USER')
    os.environ['DB_PASSWORD'] = os.getenv('TEST_DB_PASSWORD')
    os.environ['DB_HOST'] = os.getenv('TEST_DB_HOST')
    os.environ['DB_PORT'] = os.getenv('TEST_DB_PORT')

    jsonManager.initialize()
    yield

    conn = psycopg2.connect(
        dbname='postgres',
        user=os.getenv('TEST_DB_USER'),
        password=os.getenv('TEST_DB_PASSWORD'),
        host=os.getenv('TEST_DB_HOST'),
        port=os.getenv('TEST_DB_PORT')
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f'DROP DATABASE IF EXISTS "{database_name}" WITH (FORCE)')
    cur.close()
    conn.close()

    del os.environ['DB_NAME']
    del os.environ['DB_USER']
    del os.environ['DB_PASSWORD']
    del os.environ['DB_HOST']
    del os.environ['DB_PORT']


@pytest_asyncio.fixture
async def bot(request, event_loop):
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    b = commands.Bot(command_prefix=get_command_prefix(), event_loop=event_loop, intents=intents)
    await b._async_setup_hook()

    dpytest.configure(b)
    return b


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def live_bot(request, event_loop):
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    b = commands.Bot(command_prefix=get_command_prefix(), event_loop=event_loop, intents=intents)
    await b._async_setup_hook()

    dpytest.configure(b)
    for i in range(5):
        await dpytest.member_join(name="Dummy", discrim=(i + 1))
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
            await b.load_extension("test.unit.internal." + extension)

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
