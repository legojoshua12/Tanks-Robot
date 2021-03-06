import os
from configparser import ConfigParser

config = ConfigParser()


def initialize():
    """
    Calls a shutdown if a config file cannot be located
    """
    if os.path.exists('config.ini'):
        print('Config file located, initializing...')
    else:
        print('Config file not located, exiting...')
        exit()


def writeValue(section, key, value):
    """
    Adds config values to the config file
    :param section: Which header to write or write to
    :param key: Which key to be used in the section
    :param value: The value of the given key
    """
    config.read('config.ini')
    config.set(section, key, value)

    with open('../config.ini', 'w') as f:
        config.write(f)


def readValue(section, key):
    """
    Grabs a configuration option out of the config file
    :param section: Which header to grab
    :param key: Which value is desired
    """
    config.read('config.ini')

    return config.get(section, key)
