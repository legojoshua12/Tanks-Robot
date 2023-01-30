"""This is the main loader for the robot, handling any and all incoming commands off of the command queue"""
import discord

from src.tanks.libraries import boardConstructor as bC
from src.tanks.libraries import jsonManager, renderPipeline, commands, configUtils


async def handle_message(message, client, commandMessageStarter):
    """
    Used to parse and perform functions based on an incoming message
    :param message: Main message from the queue
    :param client: Discord client for instantiation of user objects
    :param commandMessageStarter: Start prefix for a command
    :return: None
    """
    if isinstance(message.channel, discord.channel.DMChannel):
        await commands.direct_message_commands(message, message.content, client)
    else:
        # TODO This is for audit purposes only, remove on final build
        if message.content == 'clear':
            jsonManager.clear_all_data()

        if message.content.startswith(commandMessageStarter):
            # Check to make sure this is inline with config.ini
            if commandMessageStarter[0] == '*':
                # Only check for star if there is one, otherwise no need to do an italics check
                stars = 0
                for c in message.content:
                    if c == '*':
                        stars = stars + 1
                if stars >= 2:
                    return

            # Don't say anything, there was no command and only the prefix given
            command_message_starter_length = len(commandMessageStarter)
            command_is_space = message.content[len(commandMessageStarter):].isspace()
            if len(message.content) == command_message_starter_length or command_is_space:
                await message.channel.send(message.author.mention + ' No input command. Please use `*/help` to view a '
                                                                    'list of commands and options.')
                return

            # A slicer of the message to make an easy reference
            command = message.content[len(commandMessageStarter):].lower()

            # Commands
            # Check if there is a game going
            is_game_present: str = jsonManager.check_if_game_is_in_channel(message)
            if is_game_present == 'lobby':
                action = await commands.public_commands_lobby(message, command)
                if action == 'join':
                    data = jsonManager.read_games_json()
                    new_player_number = len(data['games'][str(message.guild.id)][str(message.channel.id)]['players'])+1
                    is_present: bool = jsonManager.add_player_to_game(message, new_player_number)
                    if is_present:
                        await message.channel.send(message.author.mention + ' is already in the game!')
                    else:
                        await message.channel.send('Adding ' + message.author.mention + ' to the new game of Tanks!')
                elif action == 'leave':
                    is_not_present: bool = jsonManager.remove_player_from_game(message)
                    if is_not_present:
                        await message.channel.send(message.author.mention + ' cannot leave when you are not in the '
                                                                            'game!')
                    else:
                        sad_emoji = '\U0001F622'
                        await message.channel.send(message.author.mention + f' left the game. {sad_emoji}')
                elif action == 'help':
                    await commands.send_lobby_help_menu(message)
                elif action == 'dm':
                    await commands.send_dm_starter(message)
                elif action == 'players':
                    data = jsonManager.read_games_json()
                    await commands.list_players_lobby(message, data, client)
                elif action == 'start':
                    # Here we want to actually boot the game
                    number_of_players = jsonManager.get_number_of_players_in_game(message)
                    if str(configUtils.read_value('startGame', 'adminTesting')).lower() == 'true':
                        number_of_players = 5
                    if 5 <= number_of_players <= 20:
                        booted = False
                        try:
                            board_data = bC.construct_board_data(number_of_players)
                            board_data = bC.populate_board(board_data, number_of_players)
                            jsonManager.save_board(message, board_data)
                            jsonManager.update_status(message)
                            booted = True
                        except RuntimeError:
                            await message.channel.send('Error! Could not start game!')
                        if booted:
                            board = jsonManager.get_board(message)
                            games = jsonManager.read_games_json()['games']
                            player_colors = games[str(message.guild.id)][str(message.channel.id)]['playerColors']

                            rendered_board = renderPipeline.construct_image(board, player_colors)
                            data = jsonManager.read_games_json()
                            jsonManager.save_player_json(message, data)
                            data = data['games'][str(message.guild.id)][str(message.channel.id)]['players']
                            mention_string = 'Welcome to tanks '
                            index = 0
                            for player in data:
                                if index == (len(data) - 1):
                                    mention_string += (await client.fetch_user(int(player))).mention + '!'
                                else:
                                    index += 1
                                    mention_string += (await client.fetch_user(int(player))).mention + ', '
                            await message.channel.send(mention_string)
                            await commands.display_board(message, rendered_board)
                    else:
                        if number_of_players <= 4:
                            await message.channel.send('There are not enough players in the game to start!')
                        else:
                            await message.channel.send('There are too many players in the game to start!')

            elif is_game_present == 'active':
                action = await commands.public_commands_game(message, command)
                if action == 'board':
                    games_json = jsonManager.read_games_json()
                    player_colors = games_json['games'][str(message.guild.id)][str(message.channel.id)]['playerColors']
                    rendered_board = renderPipeline.construct_image(jsonManager.get_board(message), player_colors)
                    await commands.display_board(message, rendered_board)
                elif action == 'players':
                    await commands.show_player_statistics(message, jsonManager.read_games_json(), client)
                elif action == 'dm':
                    await commands.send_dm_starter(message)
                elif action == 'increase range':
                    await commands.increase_range(message, jsonManager.read_games_json())
                elif action == 'move':
                    await commands.move(message, jsonManager.read_games_json(), command)
                elif action == 'shoot':
                    await commands.shoot(message, jsonManager.read_games_json(), command, client)
                elif action == 'vote':
                    await commands.vote_action(message, jsonManager.read_games_json(), command)
                elif action == 'send':
                    await commands.send_actions(message, jsonManager.read_games_json())

            elif is_game_present == 'none':
                possible_command = await commands.public_commands_no_game(message, command)
                if possible_command:
                    wrote_to_json: bool = False
                    try:
                        jsonManager.create_game(message)
                        jsonManager.add_player_to_game(message, 1)
                        await message.channel.send('Adding ' + message.author.mention + ' to the new game of Tanks!')
                        wrote_to_json = True
                    except RuntimeError:
                        await message.channel.send('An error has occurred in creating the game! Reverting now!')
                    if wrote_to_json:
                        await commands.send_lobby_help_menu(message)
