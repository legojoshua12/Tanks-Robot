# Tanks-Robot
![Python Version](https://img.shields.io/badge/Python_Version-3.8-informational?style=flat&logo=python&logoColor=white&color=11BB11)
![PR Status](https://img.shields.io/badge/PRs-Welcome-informational?style=flat&logoColor=white&color=11BB11)

This is a robot for the game tanks inspired by [HalfBrick studios](https://www.halfbrick.com/).

## Local Compiling
In order to run a local instance of this robot, you need [Python 3.8](https://www.python.org/downloads/release/python-380/) and the following libraries:
 - [discord py](https://github.com/Rapptz/discord.py)
 - [Pillow](https://github.com/python-pillow/Pillow)
 - [python-dotenv](https://github.com/theskumar/python-dotenv)
 - [numpy](https://github.com/numpy/numpy)
 - [schedule](https://github.com/dbader/schedule)

The above libraries come with lower level libraries needed for operation and pip will automatically install those as needed.

In addition to the packages above, you will also need a discord developer token from the [discord developer portal](https://discord.com/developers/applications).
You can add the token to your `.env` file to initialize the connection with the discord servers.

## Heroku Deployment

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

### Planned Features
 - Setup a game with random map (mountains, rivers, hills, etc.)
 - Everyone gets 1 action a day at 12pm (noon) PST
 - Tokens can be traded in secret
 - Health is tracked publicly
 - Dead players can vote on an extra action per day (3 votes to pass)