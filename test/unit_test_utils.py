import dataclasses

import discord.channel

from test import unit_test_class_handler as ut


def make_sample_message():
    return Message(1, "something", "some time", discord.channel.DMChannel)


@dataclasses.dataclass
class Message:
    id: int
    content: str
    timestamp: str
    channel: discord.channel
