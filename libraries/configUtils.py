import os
from configparser import ConfigParser

config = ConfigParser()

def initialize():
    if os.path.exists('config.ini'):
        print('Config file located, initializing...')
    else:
        print('Config file not located, exiting...')
        exit()

def writeValue(section, key, value):
    config.read('config.ini')
    config.set(section, key, value)

    with open('../config.ini', 'w') as f:
        config.write(f)

def readValue(section, key):
    config.read('config.ini')

    return config.get(section, key)
