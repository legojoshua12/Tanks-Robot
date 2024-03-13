"""
Tests designed for measuring the queue system and that it handles incoming messages sequentially
"""
import pytest


@pytest.mark.skip(reason='Skipping daily check for now as there is a lot of utils that need to be made first')
@pytest.mark.asyncio
async def test_daily_upkeep():
    assert True
