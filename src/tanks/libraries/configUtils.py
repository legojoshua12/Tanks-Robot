"""Handles reading the config file and providing values when given a key"""
import os
import sys
import logging
from configparser import ConfigParser

config = ConfigParser()


def initialize():
    """Calls a shutdown if a config file cannot be located"""
    if os.path.exists('config.ini'):
        if str(read_value('startGame', 'adminTesting')).lower() == 'true':
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logging.info('Config file located, initializing...')
    else:
        logging.critical('Config file not located, exiting...')
        exit()


def write_value(section, key, value):
    """Adds config values to the config file
    :param section: Which header to write or write to
    :param key: Which key to be used in the section
    :param value: The value of the given key
    """
    config.read('config.ini')
    config.set(section, key, value)

    with open('./config.ini', 'w') as f:
        config.write(f)


def read_value(section, key, uniqueLocation=None):
    """Grabs a configuration option out of the config file
    :param section: Which header to grab
    :param key: Which value is desired
    :param uniqueLocation: Default None but can pass a string type for a location reader of a config file
    """
    if uniqueLocation is None:
        config.read('config.ini')
    else:
        config.read(uniqueLocation)

    try:
        value = config.get(section, key)
        return value
    except FileNotFoundError:
        config.read('../config.ini')
        value = config.get(section, key)
        return value
