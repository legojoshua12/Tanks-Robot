"""Completes the daily upkeep with a call from the main class coroutine"""
import os
import psycopg2

from datetime import datetime

from src.tanks.libraries import jsonManager, configUtils


async def dailyActionsAndVoteUpkeep(client) -> None:
    """Performs the daily action giving and vote tally"""
    print('Daily upkeep started at: ' + str(datetime.utcnow()))
    data = jsonManager.read_games_json()
    try:
        data = data['games']
    except KeyError:
        print("No games running for today's upkeep! Skipping processing")
        return
    for server in data:
        for channel in data[server]:
            if data[server][channel]['gameStatus'] == "active":
                # Here the votes are tallied for the day if they received enough dead votes
                champion_player = None
                champions = 0
                champion_votes = 0
                for player in data[server][channel]['players']:
                    if int(data[server][channel]['players'][player]['votes']) > 0:
                        if champions == 0 and champion_player is None:
                            champions = 1
                            champion_player = player
                            champion_votes = int(data[server][channel]['players'][player]['votes'])
                        elif champions == 1:
                            if int(data[server][channel]['players'][player]['votes']) > champion_votes:
                                champions = 1
                                champion_player = player
                                champion_votes = int(data[server][channel]['players'][player]['votes'])
                            elif int(data[server][channel]['players'][player]['votes']) == champion_votes:
                                champions += 1
                            else:
                                data[server][channel]['players'][player]['votes'] = 0
                        data[server][channel]['players'][player]['votes'] = 0
                if champions == 1:
                    contender_actions = int(data[server][channel]['players'][champion_player]['actions']) + 1
                    data[server][channel]['players'][champion_player]['actions'] = contender_actions
                    message = f"<@!{str(champion_player)}> won the vote of the dead today and gets an extra action!"
                    await client.get_channel(id=int(channel)).send(message)
                elif champions >= 2:
                    message = "There was a tie for votes today! No one got extra actions!"
                    await client.get_channel(id=int(channel)).send(message)
                else:
                    message = "There were no votes today and no one got an extra action!"
                    await client.get_channel(id=int(channel)).send(message)

                # Here each person receives either a vote if they are dead or an action if they are alive
                for player in data[server][channel]['players']:
                    if data[server][channel]['players'][player]['lives'] <= 0:
                        data[server][channel]['players'][player]['remainingVotes'] = 1
                    else:
                        extra_action = (int(data[server][channel]['players'][player]['actions']) + 1)
                        data[server][channel]['players'][player]['actions'] = extra_action
                upkeep_finished_msg = "Daily upkeep finished! "
                extra_action_msg = "All living players have received an action "
                extra_vote_msg = "and all others received a vote for the day!"
                await client.get_channel(id=int(channel)).send(upkeep_finished_msg + extra_action_msg + extra_vote_msg)
    new_data = {'games': data}
    for guild in new_data['games']:
        for channel in new_data['games'][guild]:
            jsonManager.save_data(new_data['games'][guild][channel], str(guild), str(channel))

    # Print time finished to process if admin
    if str(configUtils.read_value('startGame', 'adminTesting')).lower() == 'true':
        print('Completed Daily Upkeep at: ' + str(datetime.utcnow()))
    return
