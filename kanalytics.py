from prettytable import PrettyTable
import json
import lookup
import os

# OP STATS AVAILABLE #
# timeplayed, kills, deaths, k/d, wins, losses, win %, kost, headshots, kpr, ok (opening kills), od (opening deaths),
# distance per round, rounds with a kill, rounds with a multi-kill, rounds survived, rounds with an ace, rounds with a clutch

# parameters (must delete players.json if you change the parameters.)
#                    win rate,   k/d,         kost,     kills per round,  % played
#                       (50)            (1)         (100)         (1)             (1)
std_overall_params = [20 * 0.01,        0.5 * 1,     10 * 0.001,      1 * 1,        20 * 1   ]

#                   movement,  opening kills, opening deaths,     win rate
#                     (100)        (100)           (100)            (50)
std_roam_params = [4 * 0.01,     10 * 0.01,       -20 * 0.01,     20 * 0.01   ]

# how much influence your team's performance has on bans (a really bad teammate will influence priorities) (1 means atk = def)
HOME_TEAM_BAN_INFLUENCE_MULTIPLIER = 3


def create_table(score_dicts, value_names, first, last):
    if len(score_dicts) != len(value_names):
        print('Dictionaries do not match number of headers! (', len(score_dicts), '!=', len(value_names), ')')
        return -1

    headers = ['Operator']
    for v_name in value_names:
        headers.append(v_name)
    score_table = PrettyTable(headers)
    dot_flag = False
    filter_index = 0

    for op in score_dicts[0]:
        if first <= filter_index < len(score_dicts[0]) - last:
            if not dot_flag:
                row_entry = ['...']
                for sd in score_dicts:
                    row_entry.append('...')
                score_table.add_row(row_entry)
                dot_flag = True
            filter_index += 1
            continue
        row_entry = [op]
        for sd in score_dicts:
            row_entry.append(round(sd[op], 3))
        score_table.add_row(row_entry)
        filter_index += 1

    return score_table


def find_total_time_played(data):
    total_time_atk = 0
    total_time_def = 0
    for op in data:
        if lookup.get_op_side(op) == 'ATK':
            total_time_atk += data[op]['TIMEPLAYED']
        else:
            total_time_def += data[op]['TIMEPLAYED']
    return total_time_atk, total_time_def


def handle_player(pfile, overall_params, roam_params, print_individual_statistics):
    # print('Stats for', pfile)

    pfile = open(pfile)
    playerOpData = json.load(pfile)
    op_overall_scores_atk = dict()
    op_roam_scores_atk = dict()
    op_overall_scores_def = dict()
    op_roam_scores_def = dict()

    total_time_played_atk, total_time_played_def = find_total_time_played(playerOpData)

    for operator in playerOpData:
        op_data = playerOpData[operator]
        is_atk = lookup.get_op_side(operator) == 'ATK'

        # gather all materials
        op_time_played = op_data['TIMEPLAYED']  # (minutes)
        if op_time_played < 30:  # minutes
            continue
        op_presence = op_time_played / (total_time_played_atk if is_atk else total_time_played_def)

        # impact and effectiveness #
        win_rate = op_data['WIN %'] - 50.0
        k_d = op_data['K/D'] - 1
        kills_per_round = op_data['KPR'] - 1
        kost = op_data['KOST']

        # roaming #
        ok = op_data['OK']
        od = op_data['OD']
        dist_travelled = op_data['DISTANCE PER ROUND']  # (meters)

        op_score = win_rate * overall_params[0] + k_d * overall_params[1] + kost * overall_params[
            2] + kills_per_round * overall_params[
                       3] + op_presence * overall_params[4]
        op_roam = dist_travelled * roam_params[0] + ok * roam_params[1] + od * roam_params[2] + win_rate * \
                  roam_params[3]

        op_score *= 2.5
        op_roam *= 1

        if is_atk:
            op_overall_scores_atk[operator] = op_score
            op_roam_scores_atk[operator] = op_roam
        else:
            op_overall_scores_def[operator] = op_score
            op_roam_scores_def[operator] = op_roam
    pfile.close()

    op_overall_scores_atk = {key: val for key, val in
                             sorted(op_overall_scores_atk.items(), key=lambda ele: ele[1], reverse=True)}
    op_roam_scores_atk = {key: val for key, val in
                          sorted(op_roam_scores_atk.items(), key=lambda ele: ele[1], reverse=True)}
    op_overall_scores_def = {key: val for key, val in
                             sorted(op_overall_scores_def.items(), key=lambda ele: ele[1], reverse=True)}
    op_roam_scores_def = {key: val for key, val in
                          sorted(op_roam_scores_def.items(), key=lambda ele: ele[1], reverse=True)}

    score_atk = op_overall_scores_atk.copy()
    score_def = op_overall_scores_def.copy()
    roam_atk = op_roam_scores_atk.copy()
    roam_def = op_roam_scores_def.copy()
    if print_individual_statistics:
        print()
        print('STATS FOR', str(pfile).split('/')[1].split('.')[0], ':')

        print('[ATTACK]')
        print(create_table([score_atk, roam_atk], ['Impact', 'RoamEff'], 5, 3))
    for op in lookup.ATK_OPS:
        if op in roam_atk and roam_atk[op] < -99:
            score_atk.pop(op)
            roam_atk.pop(op)
    if print_individual_statistics:
        print(create_table([roam_atk, score_atk], ['RoamEff', 'Impact'], 5, 5))

        print('\n[DEFENCE]')
        print(create_table([score_def, roam_def], ['Impact', 'RoamEff'], 5, 3))
    for op in lookup.DEF_OPS:
        if op in roam_def and roam_def[op] < -99:
            score_def.pop(op)
            roam_def.pop(op)
    if print_individual_statistics:
        print(create_table([roam_def, score_def], ['RoamEff', 'Impact'], 5, 5))
        print()

    total_atk_ops = 0
    total_atk_score = 0
    for value in score_atk.values():
        total_atk_score += value
        total_atk_ops += 1
    total_atk_ops = max(total_atk_ops, 1)
    score_avg_atk = total_atk_score / total_atk_ops

    total_def_ops = 0
    total_def_score = 0
    for value in score_def.values():
        total_def_score += value
        total_def_ops += 1
    total_def_ops = max(total_def_ops, 1)
    score_avg_def = total_def_score / total_def_ops

    total_atk_roam = 0
    for value in roam_atk.values():
        total_atk_roam += value
    roam_avg_atk = total_atk_roam / total_atk_ops

    total_def_roam = 0
    for value in roam_def.values():
        total_def_roam += value
    roam_avg_def = total_def_roam / total_def_ops

    if save_to_database:
        save_player_to_database(pfile.name[:-5], [op_overall_scores_atk, op_roam_scores_atk, op_overall_scores_def, op_roam_scores_def, score_avg_atk, score_avg_def, roam_avg_atk, roam_avg_def])
    return (op_overall_scores_atk, op_roam_scores_atk), (op_overall_scores_def, op_roam_scores_def), (score_avg_atk, score_avg_def), (roam_avg_atk, roam_avg_def)


def ban_report(home_team='home_team', away_team='away_team', show_home=False):
    ban_prio_scores_atk = {}
    ban_prio_scores_def = {}

    # ========= AWAY ========= #
    directory = os.fsencode(away_team)
    op_scores_away_atk = {}
    op_roams_away_atk = {}
    op_scores_away_def = {}
    op_roams_away_def = {}

    away_op_score_total_atk = 0
    away_op_score_total_def = 0
    away_op_roam_total_atk = 0
    away_op_roam_total_def = 0

    for file in os.listdir(directory):
        (aops, aors), (dops, dors), (soa, sod), (roa, rod) = handle_player(away_team + '/' + str(os.fsdecode(file)), std_overall_params,
                                                   std_roam_params, verbose_stats)

        # AGGREGATING OP SCORES ATK
        for op in aops:  # ITERATE THROUGH OPERATORS
            away_op_score_total_atk += aops[op]
            if op not in ban_prio_scores_atk:  # SORT BAN PRIORITIES
                ban_prio_scores_atk[op] = aops[op]
            else:
                ban_prio_scores_atk[op] += aops[op]

            if op not in op_scores_away_atk:  # SORT IMPACTS
                op_scores_away_atk[op] = aops[op]
            else:
                op_scores_away_atk[op] += aops[op]
        # AGGREGATING OP SCORES DEF
        for op in dops:  # ITERATE THROUGH OPERATORS
            away_op_score_total_def += dops[op]
            if op not in ban_prio_scores_def:  # SORT BAN PRIORITIES
                ban_prio_scores_def[op] = dops[op]
            else:
                ban_prio_scores_def[op] += dops[op]

            if op not in op_scores_away_def:  # SORT IMPACTS
                op_scores_away_def[op] = dops[op]
            else:
                op_scores_away_def[op] += dops[op]

        # ORDER IMPACTS
        op_scores_away_atk = {key: val for key, val in
                              sorted(op_scores_away_atk.items(), key=lambda ele: ele[1], reverse=True)}
        op_scores_away_def = {key: val for key, val in
                              sorted(op_scores_away_def.items(), key=lambda ele: ele[1], reverse=True)}

        for op in aors:  # SORT ROAMEFF ATK
            away_op_roam_total_atk += aors[op]
            if op not in op_roams_away_atk:
                op_roams_away_atk[op] = aors[op]
            else:
                op_roams_away_atk[op] += aors[op]
        for op in dors:  # SORT ROAMEFF ATK
            away_op_roam_total_def += dors[op]
            if op not in op_roams_away_def:
                op_roams_away_def[op] = dors[op]
            else:
                op_roams_away_def[op] += dors[op]

        # ORDER ROAMEFF
        op_roams_away_atk = {key: val for key, val in
                             sorted(op_roams_away_atk.items(), key=lambda ele: ele[1], reverse=True)}
        op_roams_away_def = {key: val for key, val in
                             sorted(op_roams_away_def.items(), key=lambda ele: ele[1], reverse=True)}
    # ====== END AWAY ======= #

    # ========= HOME ========= #
    directory = os.fsencode(home_team)
    op_scores_home_atk = {}
    op_scores_home_def = {}
    op_roams_home_atk = {}
    op_roams_home_def = {}

    home_op_score_total_atk = 0
    home_op_score_total_def = 0
    home_op_roam_total_atk = 0
    home_op_roam_total_def = 0

    for file in os.listdir(directory):
        (aops, aors), (dops, dors), (soa, sod), (roa, rod) = handle_player(home_team + '/' + str(os.fsdecode(file)), std_overall_params,
                                                   std_roam_params, verbose_stats)

        # AGGREGATING OP SCORES ATK
        for op in aops:  # ITERATE THROUGH OPERATORS
            home_op_score_total_atk += aops[op]
            if op not in ban_prio_scores_atk:  # SORT BAN PRIORITIES
                ban_prio_scores_atk[op] = aops[op]
            else:
                ban_prio_scores_atk[op] -= aops[op] / HOME_TEAM_BAN_INFLUENCE_MULTIPLIER

            if op not in op_scores_home_atk:  # SORT IMPACTS
                op_scores_home_atk[op] = aops[op]
            else:
                op_scores_home_atk[op] += aops[op]
        # AGGREGATING OP SCORES DEF
        for op in dops:  # ITERATE THROUGH OPERATORS
            home_op_score_total_def += dops[op]
            if op not in ban_prio_scores_def:  # SORT BAN PRIORITIES
                ban_prio_scores_def[op] = dops[op]
            else:
                ban_prio_scores_def[op] -= dops[op] / HOME_TEAM_BAN_INFLUENCE_MULTIPLIER

            if op not in op_scores_home_def:  # SORT IMPACTS
                op_scores_home_def[op] = dops[op]
            else:
                op_scores_home_def[op] += dops[op]

        # ORDER IMPACTS
        op_scores_home_atk = {key: val for key, val in
                              sorted(op_scores_home_atk.items(), key=lambda ele: ele[1], reverse=True)}
        op_scores_home_def = {key: val for key, val in
                              sorted(op_scores_home_def.items(), key=lambda ele: ele[1], reverse=True)}

        for op in aors:  # SORT ROAMEFF ATK
            home_op_roam_total_atk += aors[op]
            if op not in op_roams_home_atk:
                op_roams_home_atk[op] = aors[op]
            else:
                op_roams_home_atk[op] += aors[op]
        for op in dors:  # SORT ROAMEFF ATK
            home_op_roam_total_def += dors[op]
            if op not in op_roams_home_def:
                op_roams_home_def[op] = dors[op]
            else:
                op_roams_home_def[op] += dors[op]

        # ORDER ROAMEFF
        op_roams_home_atk = {key: val for key, val in
                             sorted(op_roams_home_atk.items(), key=lambda ele: ele[1], reverse=True)}
        op_roams_home_def = {key: val for key, val in
                             sorted(op_roams_home_def.items(), key=lambda ele: ele[1], reverse=True)}

    ban_prio_scores_atk = {key: val for key, val in
                           sorted(ban_prio_scores_atk.items(), key=lambda ele: ele[1], reverse=True)}
    ban_prio_scores_def = {key: val for key, val in
                           sorted(ban_prio_scores_def.items(), key=lambda ele: ele[1], reverse=True)}

    # ====== END HOME ======= #

    # PARALLEL DICT STRUCT [ATK DICT, DEF DICT]
    # ATK/DEF DICT [IMPACT, ROAMEFF]
    # IMPACT/ROAMEFF [OP: VAL]

    print()
    print('BAN PRIORITY (ATK):')
    print(create_table([ban_prio_scores_atk], ['Priority'], 5, 0))
    print('BAN PRIORITY (DEF):')
    print(create_table([ban_prio_scores_def], ['Priority'], 5, 0))
    print()
    print('AWAY (', round(away_op_score_total_atk + away_op_score_total_def), '):')
    print('[ATTACK]')
    print(create_table([op_scores_away_atk, op_roams_away_atk], ['Team Impact', 'Team RoamEff'], 5, 3))
    print(create_table([op_roams_away_atk, op_scores_away_atk], ['Team RoamEff', 'Team Impact'], 5, 0))
    print('[DEFENCE]')
    print(create_table([op_scores_away_def, op_roams_away_def], ['Team Impact', 'Team RoamEff'], 5, 3))
    print(create_table([op_roams_away_def, op_scores_away_def], ['Team RoamEff', 'Team Impact'], 5, 0))
    print()
    if show_home:
        print('HOME (', round(home_op_score_total_atk + home_op_score_total_def), '):')
        print('[ATTACK]')
        print(create_table([op_scores_home_atk, op_roams_home_atk], ['Team Impact', 'Team RoamEff'], 5, 3))
        print(create_table([op_roams_home_atk, op_scores_home_atk], ['Team RoamEff', 'Team Impact'], 5, 0))
        print('[DEFENCE]')
        print(create_table([op_scores_home_def, op_roams_home_def], ['Team Impact', 'Team RoamEff'], 5, 3))
        print(create_table([op_roams_home_def, op_scores_home_def], ['Team RoamEff', 'Team Impact'], 5, 0))
    print()
    print('Overall Teams')
    print('ATK:')
    print('AWAY Impact:', round(away_op_score_total_atk, 0), ' AWAY RoamEff:', round(away_op_roam_total_atk, 0))
    print('HOME Impact:', round(home_op_score_total_atk, 0), ' HOME RoamEff:', round(home_op_roam_total_atk, 0))
    print('\nDEF:')
    print('AWAY Impact:', round(away_op_score_total_def, 0), ' AWAY RoamEff:', round(away_op_roam_total_def, 0))
    print('HOME Impact:', round(home_op_score_total_def, 0), ' HOME RoamEff:', round(home_op_roam_total_def, 0))


def presence_report(team):
    directory = os.fsencode(team)
    op_apresence = {}
    op_dpresence = {}
    for file in os.listdir(directory):
        (apresence, aroameff), (dpresence, droameff), (scoreavgatk, scoreavgdef), (roamavgatk, roamavgdef) = handle_player(team + '/' + str(os.fsdecode(file)),
                                                                     std_overall_params, std_roam_params, verbose_stats)

        for op in apresence:
            if op not in op_apresence:
                op_apresence[op] = apresence[op]
            else:
                op_apresence[op] += apresence[op]
        total_apresence = 0
        for val in op_apresence.values():
            total_apresence += abs(val)
        for key in op_apresence.keys():
            op_apresence[key] /= total_apresence / 100.
        op_apresence = {key: val for key, val in sorted(op_apresence.items(), key=lambda ele: ele[1], reverse=True)}
        for op in dpresence:
            if op not in op_dpresence:
                op_dpresence[op] = dpresence[op]
            else:
                op_dpresence[op] += dpresence[op]
        total_dpresence = 0
        for val in op_dpresence.values():
            total_dpresence += abs(val)
        for key in op_dpresence.keys():
            op_dpresence[key] /= total_dpresence / 100.
        op_dpresence = {key: val for key, val in sorted(op_dpresence.items(), key=lambda ele: ele[1], reverse=True)}
        print("Player: "  + str(file))
        print("Avg. Impact (ATK): " + str(round(scoreavgatk, 2)))
        print("Avg. Impact (DEF): " + str(round(scoreavgdef, 2)))
        print("Avg. RoamEff (ATK): " + str(round(roamavgatk, 2)))
        print("Avg. RoamEff (DEF): " + str(round(roamavgdef, 2)))
        print()

    print()
    print('PRESENCE REPORT (', team, '):')
    print('[ATTACK]')
    print(create_table([op_apresence], ['Presence'], 10, 0))
    print('[DEFENCE]')
    print(create_table([op_dpresence], ['Presence'], 10, 0))


# DATABASE SAVING #
def write_database_file():
    with open('players.json', 'w') as f:
        f.write(json.dumps(db))

def save_player_to_database(player_name, stats):
    db[player_name] = {
        "impact_atk": stats[0],
        "roam_atk": stats[1],
        "impact_def": stats[2],
        "roam_def": stats[3],
        "impact_avg_atk": stats[4],
        "impact_avg_def": stats[5],
        "roam_avg_atk": stats[6],
        "roam_avg_def": stats[7]
    }



# END FUNCTION DEFINITIONS #

db = {}
verbose_stats = True
save_to_database = True

def run():
    # ban_report(home_team='dokkaebees',away_team='OPPONENTS', show_home=False)
    print('\n\n')
    presence_report('dokkaebees')

    if save_to_database:
        write_database_file()

run()