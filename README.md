# Tanks-Robot
![Python Version](https://img.shields.io/badge/Python_Version-3.8-informational?style=flat&logo=python&logoColor=white&color=11BB11)
![PR Status](https://img.shields.io/badge/PRs-Welcome-informational?style=flat&logo=git&logoColor=white&color=11BB11)
![Tests Status](https://github.com/legojoshua12/Tanks-Robot/actions/workflows/tests.yml/badge.svg)

This is a robot for the game tanks inspired by [HalfBrick studios](https://www.halfbrick.com/).

## Local Compiling
In order to run a local instance of this robot, you need [Python 3.8](https://www.python.org/downloads/release/python-380/).
All required libraries can be obtained with correct versioning for pip via the [requirements.txt](requirements.txt) file. If you would like to run the project and the tests, then use the [requirements_dev.txt](requirements_dev.txt) file.

The libraries referenced come with lower level libraries needed for operation and pip will automatically install those as needed.

In addition to the packages above, you will also need a discord developer token from the [discord developer portal](https://discord.com/developers/applications).
You can add the token to your `.env` file to initialize the connection with the discord servers.

## Integration Tests
All code within the robot is unit and integration tested and all tests can be run on a local machine before deployment to a [docker container](https://www.docker.com/) or [Heroku](https://www.heroku.com/).

## Heroku Deployment

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

### Planned Features
 - Set up a game with random map (mountains, rivers, hills, etc.)
 - Different kinds of tanks with different abilities
 - Fire mechanic that makes some tiles temporarily unusable