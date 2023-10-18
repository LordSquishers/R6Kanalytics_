import json

import numpy as np

with open('players.json') as f:
    players = json.load(f)

teams = dict()
for player in players:
    player_team = player.split('/')[0]
    player_name = player.split('/')[1]
    value_impact = players[player]['impact_avg_atk'] + players[player]['impact_avg_def']
    value_roam = players[player]['roam_avg_atk'] + players[player]['roam_avg_def']
    total_value = value_roam + value_impact

    if player_team not in teams:
        teams[player_team] = {}
    teams[player_team][player_name] = int(total_value)

for player in players:
    player_team = player.split('/')[0]
    player_name = player.split('/')[1]
    if teams[player_team][player_name] == 0:
        total_value = np.average(list(teams[player_team].values())) / 1.5
        teams[player_team][player_name] = int(total_value)

for team in teams.keys():
    print('Team:', team, '(' + str(sum(list(teams[team].values()))) + ')')
    print(teams[team].keys())
    print(teams[team].values())