# temporary file to find best teams.

import json
import random

import numpy as np

PLAYERS_IMMUNE_TO_SCHEDULING = ['lord_squishers', 'shubielah']

with open('players.json') as f:
    players = json.load(f)

player_values = {}

for player in players:
    player_name = player.split('/')[1]
    value_impact = players[player]['impact_avg_atk']**2 + players[player]['impact_avg_def']
    value_roam = players[player]['roam_avg_atk'] + players[player]['roam_avg_def']
    total_value = value_roam / 2 + value_impact
    player_values[player_name] = total_value
    if player_name in PLAYERS_IMMUNE_TO_SCHEDULING:
        # add dual-roster players twice
        player_values[player_name + "2"] = total_value

sorted_team_1 = {}
st1_total = 0
sorted_team_2 = {}
st2_total = 0
print(player_values)
best_difference = 999999

for iteration in range(1000):
    sample = player_values.copy()
    st1 = {}
    st2 = {}
    team1_total = 0
    team2_total = 0
    for i in range(10):
        p = random.choice(list(sample.keys()))
        sample.pop(p)
        v = player_values[p]
        if i < 5:
            st1[p] = v
            team1_total += v
        else:
            st2[p] = v
            team2_total += v
    intersect = []
    for item in st1.keys():
        if item in st2.keys():
            team1_total = 99999
            team2_total = -99999
    if ('lord_squishers' in st1 and 'lord_squishers2' in st1) or ('lord_squishers' in st2 and 'lord_squishers2' in st2) or ('shubielah' in st1 and 'shubielah2' in st1) or ('shubielah' in st2 and 'shubielah2' in st2):
        team1_total = 99999
        team2_total = -99999
    if abs(team1_total - team2_total) < best_difference:
        best_difference = abs(team1_total - team2_total)
        sorted_team_1 = st1
        sorted_team_2 = st2
        st1_total = team1_total
        st2_total = team2_total


print("Team 1: ")
print(sorted_team_1.keys())
print(sorted_team_1.values())
print("Total value: " + str(round(st1_total)))

print("Team 2: ")
print(sorted_team_2.keys())
print(sorted_team_2.values())
print("Total value: " + str(round(st2_total)))
