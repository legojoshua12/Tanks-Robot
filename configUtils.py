from configparser import ConfigParser

config = ConfigParser()

def initialize():
    config.read('config.ini')
    if not config.has_section('startGame'):
        config.add_section('startGame')
    if not config.has_section('botSettings'):
        config.add_section('botSettings')
    if not config.has_option('startGame', 'playerSpawnDistance'):
        writeValue('startGame', 'playerSpawnDistance', '1')
    if not config.has_option('botSettings', 'botCommandPrefix'):
        writeValue('botSettings', 'botCommandPrefix', '*/')

def writeValue(section, key, value):
    config.read('config.ini')
    config.set(section, key, value)

    with open('config.ini', 'w') as f:
        config.write(f)

def readValue(section, key):
    config.read('config.ini')

    return config.get(section, key)
