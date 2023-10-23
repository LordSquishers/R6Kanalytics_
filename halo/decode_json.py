import json

GAMEMODE_LOOKUP = {"King of the Hill": "KOTH", "CTF 5 Captures": "5-CTF", "CTF 3 Captures": "3-CTF", "Extraction": "EXTRACTION", "Oddball": "ODDBALL", "Strongholds": "STRONGHOLDS"}

with open("output.json") as f:
    inf = json.load(f)

# GAME:
# date, time, map, gamemode, eagle_win, cobra_win, eagle score, cobra score
print(inf['match_date'], inf['match_time'], inf['map'], GAMEMODE_LOOKUP[inf['gamemode']], inf['eagle_win'], inf['cobra_win'], inf['eagle_score'], inf['cobra_score'], sep=',')
for player in inf['players']:
    # PLAYER:
    # name, score, obj, obj assists, kills, deaths, assists, dmg dlt, dmg tkn, shots landed, shots fired
    st = inf['players'][player]
    gamemode = GAMEMODE_LOOKUP[inf['gamemode']]

    obj_main = 0
    obj_assists = 0

    if gamemode == "5-CTF":
        obj_main = st['flag_captures']
        obj_assists = st['flag_capture_assists']
    elif gamemode == "3-CTF":
        obj_main = st['flag_captures']
        obj_assists = st['flag_capture_assists']
    elif gamemode == "ODDBALL":
        obj_main = st['skull_scoring_ticks']
    elif gamemode == "STRONGHOLDS":
        hold_times = st['total_zone_occupation_time'].split(":")
        obj_main = int(hold_times[0]) * 60 + int(hold_times[1])
    elif gamemode == "EXTRACTION":
        obj_main = st['extractions']
        obj_assists = st['conversions']
    elif gamemode == "SLAYER":
        obj_main = st['kills']
        obj_assists = st['assists']

    print(player,int(st['score'].replace(',', '')),obj_main,obj_assists,int(st['kills'].replace(',', '')),int(st['deaths'].replace(',', '')),int(st['assists'].replace(',', '')),int(st['damage_dealt'].replace(',', '')),int(st['damage_taken'].replace(',', '')),int(st['shots_hit'].replace(',', '')),int(st['shots_fired'].replace(',', '')),sep=',')

# for player in inf['players']:
#     print(player, "=IMAGE(\"" + inf['players'][player]['emblem'] + "\")", sep=',')