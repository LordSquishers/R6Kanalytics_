from prettytable import PrettyTable
import json
import lookup
import os

# OP STATS AVAILABLE #
# timeplayed, kills, deaths, k/d, wins, losses, win %, kost, headshots, kpr, ok (opening kills), od (opening deaths),
# distance per round, rounds with a kill, rounds with a multi-kill, rounds survived, rounds with an ace, rounds with a clutch

# parameters
std_overall_params = [1 * 0.05, 1 * 10, 1 * 0.1, 1 * 10,
                      0.75 * 100]  # win rate and wins, k/d, kost, kills per round, % played
std_roam_params = [0.5 * 0.05, 6 * 0.05, -10 * 0.05, 0.03]  # movement, ok, od, win rate and wins


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
        if op_time_played < 15:  # minutes
            continue
        op_presence = op_time_played / (total_time_played_atk if is_atk else total_time_played_def)

        # impact and effectiveness #
        win_rate = op_data['WIN %'] - 50.0
        wins = op_data['WINS']  # using this with win rate because some people have 1 win. (games)
        k_d = op_data['K/D'] - 1
        kills_per_round = op_data['KPR'] - (2. / 3.)
        kost = op_data['KOST']

        # roaming #
        ok = op_data['OK']
        od = op_data['OD']
        dist_travelled = op_data['DISTANCE PER ROUND']  # (meters)

        op_score = win_rate * wins * overall_params[0] + k_d * overall_params[1] + kost * overall_params[
            2] + kills_per_round * overall_params[
                       3] + op_presence * overall_params[4]
        op_roam = dist_travelled * roam_params[0] + ok * roam_params[1] + od * roam_params[2] + win_rate * wins * \
                  roam_params[3]

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

    if print_individual_statistics:
        print()
        print('STATS FOR', str(pfile).split('/')[1].split('.')[0], ':')
        print('[ATTACK]')
        print(create_table([op_overall_scores_atk, op_roam_scores_atk], ['Impact', 'RoamEff'], 5, 3))
        print(create_table([op_roam_scores_atk, op_overall_scores_atk], ['RoamEff', 'Impact'], 5, 5))
        print('\n[DEFENCE]')
        print(create_table([op_overall_scores_def, op_roam_scores_def], ['Impact', 'RoamEff'], 5, 3))
        print(create_table([op_roam_scores_def, op_overall_scores_def], ['RoamEff', 'Impact'], 5, 5))
        print()

    return (op_overall_scores_atk, op_roam_scores_atk), (op_overall_scores_def, op_roam_scores_def)


def ban_report():
    ban_prio_scores_atk = {}
    ban_prio_scores_def = {}

    # ========= AWAY ========= #
    directory = os.fsencode('away_team')
    op_scores_away_atk = {}
    op_roams_away_atk = {}
    op_scores_away_def = {}
    op_roams_away_def = {}

    away_op_score_total_atk = 0
    away_op_score_total_def = 0
    away_op_roam_total_atk = 0
    away_op_roam_total_def = 0

    for file in os.listdir(directory):
        (aops, aors), (dops, dors) = handle_player('away_team/' + str(os.fsdecode(file)), std_overall_params,
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
    directory = os.fsencode('home_team')
    op_scores_home_atk = {}
    op_scores_home_def = {}
    op_roams_home_atk = {}
    op_roams_home_def = {}

    home_op_score_total_atk = 0
    home_op_score_total_def = 0
    home_op_roam_total_atk = 0
    home_op_roam_total_def = 0

    for file in os.listdir(directory):
        (aops, aors), (dops, dors) = handle_player('home_team/' + str(os.fsdecode(file)), std_overall_params,
                                                   std_roam_params, verbose_stats)

        # AGGREGATING OP SCORES ATK
        for op in aops:  # ITERATE THROUGH OPERATORS
            home_op_score_total_atk += aops[op]
            if op not in ban_prio_scores_atk:  # SORT BAN PRIORITIES
                ban_prio_scores_atk[op] = aops[op]
            else:
                ban_prio_scores_atk[op] -= aops[op]

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
                ban_prio_scores_def[op] -= dops[op]

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
    print('AWAY:')
    print('[ATTACK]')
    print(create_table([op_scores_away_atk, op_roams_away_atk], ['Team Impact', 'Team RoamEff'], 5, 3))
    print(create_table([op_roams_away_atk, op_scores_away_atk], ['Team RoamEff', 'Team Impact'], 5, 5))
    print('[DEFENCE]')
    print(create_table([op_scores_away_def, op_roams_away_def], ['Team Impact', 'Team RoamEff'], 5, 3))
    print(create_table([op_roams_away_def, op_scores_away_def], ['Team RoamEff', 'Team Impact'], 5, 5))
    print()
    print('HOME:')
    print('[ATTACK]')
    print(create_table([op_scores_home_atk, op_roams_home_atk], ['Team Impact', 'Team RoamEff'], 5, 3))
    print(create_table([op_roams_home_atk, op_scores_home_atk], ['Team RoamEff', 'Team Impact'], 5, 5))
    print('[DEFENCE]')
    print(create_table([op_scores_home_def, op_roams_home_def], ['Team Impact', 'Team RoamEff'], 5, 3))
    print(create_table([op_roams_home_def, op_scores_home_def], ['Team RoamEff', 'Team Impact'], 5, 5))
    print()
    print('Overall Teams\n')
    print('ATK:\n')
    print('AWAY Impact:', round(away_op_score_total_atk, 0), ' AWAY RoamEff:', round(away_op_roam_total_atk, 0))
    print('HOME Impact:', round(home_op_score_total_atk, 0), ' HOME RoamEff:', round(home_op_roam_total_atk, 0))
    print('DEF:\n')
    print('AWAY Impact:', round(away_op_score_total_def, 0), ' AWAY RoamEff:', round(away_op_roam_total_def, 0))
    print('HOME Impact:', round(home_op_score_total_def, 0), ' HOME RoamEff:', round(home_op_roam_total_def, 0))


def presence_report(team):
    directory = os.fsencode(team)
    op_apresence = {}
    op_dpresence = {}
    for file in os.listdir(directory):
        (apresence, aroameff), (dpresence, droameff) = handle_player(team + '/' + str(os.fsdecode(file)),
                                                                     [0, 0, 0, 0, 100], [0, 0, 0, 0], verbose_stats)
        for op in apresence:
            if op not in op_apresence:
                op_apresence[op] = apresence[op] / 5.
            else:
                op_apresence[op] += apresence[op] / 5.
        op_apresence = {key: val for key, val in sorted(op_apresence.items(), key=lambda ele: ele[1], reverse=True)}
        for op in dpresence:
            if op not in op_dpresence:
                op_dpresence[op] = dpresence[op] / 5.
            else:
                op_dpresence[op] += dpresence[op] / 5.
        op_dpresence = {key: val for key, val in sorted(op_dpresence.items(), key=lambda ele: ele[1], reverse=True)}

    print()
    print('PRESENCE REPORT (', team, '):')
    print('[ATTACK]')
    print(create_table([op_apresence], ['Presence (%)'], 10, 0))
    print('[DEFENCE]')
    print(create_table([op_dpresence], ['Presence (%)'], 10, 0))


# END FUNCTION DEFINITIONS #
verbose_stats = True
ban_report()
print('\n\n')
presence_report('home_team')
