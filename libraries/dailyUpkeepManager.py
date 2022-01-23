"""Completes the daily upkeep with a call from the main class coroutine"""
from datetime import datetime, timezone

from libraries import jsonManager


async def dailyActionsAndVoteUpkeep(client):
    """
    Performs the daily action giving and vote tally
    """
    print('Daily upkeep started at: ' + str(datetime.utcnow()))
    data = jsonManager.readJson()
    try:
        data = data['games']
    except KeyError:
        print("No games running for today's upkeep! Skipping processing")
        return
    for server in data:
        for channel in data[server]:
            if data[server][channel]['gameStatus'] == "active":
                # Here the votes are tallied for the day if they received enough dead votes
                championPlayer = None
                champions = 0
                championVotes = 0
                for player in data[server][channel]['players']:
                    if int(data[server][channel]['players'][player]['votes']) > 0:
                        if champions == 0 and championPlayer is None:
                            champions = 1
                            championPlayer = player
                            championVotes = int(data[server][channel]['players'][player]['votes'])
                        elif champions == 1:
                            if int(data[server][channel]['players'][player]['votes']) > championVotes:
                                champions = 1
                                championPlayer = player
                                championVotes = int(data[server][channel]['players'][player]['votes'])
                            elif int(data[server][channel]['players'][player]['votes']) == championVotes:
                                champions += 1
                            else:
                                data[server][channel]['players'][player]['votes'] = 0
                        data[server][channel]['players'][player]['votes'] = 0
                if champions == 1:
                    data[server][channel]['players'][championPlayer]['actions'] = int(data[server][channel]['players']
                                                                                      [championPlayer]['actions']) + 1
                    await client.get_channel(id=int(channel)).send(
                        '<@!' + str(championPlayer) + '> won the vote of the dead today and gets an extra action!')
                elif champions >= 2:
                    await client.get_channel(id=int(channel)).send('There was a tie for votes today! No one got extra '
                                                                   'actions!')
                else:
                    await client.get_channel(id=int(channel)).send('There were no votes today and no one got an extra '
                                                                   'action!')

                    # Here each person receives either a vote if they are dead or an action if they are alive
                for player in data[server][channel]['players']:
                    if data[server][channel]['players'][player]['lives'] <= 0:
                        data[server][channel]['players'][player]['remainingVotes'] = 1
                    else:
                        data[server][channel]['players'][player]['actions'] = (int(data[server][channel]['players']
                                                                                   [player]['actions']) + 1)
                await client.get_channel(id=int(channel)).send('Daily upkeep finished! All living players have '
                                                               'received an action and all others received a vote for'
                                                               ' the day!')
    newData = {'games': data}
    jsonManager.saveData(newData)
    print('Completed Daily Upkeep at: ' + str(datetime.utcnow()))
    return
