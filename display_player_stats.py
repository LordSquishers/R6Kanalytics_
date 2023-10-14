import json

from kanalytics import create_table
import lookup

def display(player_name):
    op_overall_scores_atk, op_roam_scores_atk, op_overall_scores_def, op_roam_scores_def, total_value = get_player_by_name(player_name)
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
    print()
    print('STATS FOR', player_name, '(' + str(total_value) + '):')

    print('[ATTACK]')
    print(create_table([score_atk, roam_atk], ['Impact', 'RoamEff'], 5, 3))
    for op in lookup.ATK_OPS:
        if op in roam_atk and roam_atk[op] < 4:
            score_atk.pop(op)
            roam_atk.pop(op)
    print(create_table([roam_atk, score_atk], ['RoamEff', 'Impact'], 5, 5))

    print('\n[DEFENCE]')
    print(create_table([score_def, roam_def], ['Impact', 'RoamEff'], 5, 3))
    for op in lookup.DEF_OPS:
        if op in roam_def and roam_def[op] < 8:
            score_def.pop(op)
            roam_def.pop(op)
    print(create_table([roam_def, score_def], ['RoamEff', 'Impact'], 5, 5))
    print()


def get_player_by_name(player_name):
    with open('players.json') as f:
        players = json.load(f)
    p_data = players[player_name]
    op_overall_scores_atk = p_data['impact_atk']
    op_overall_scores_def = p_data['impact_def']
    op_roam_scores_atk = p_data['roam_atk']
    op_roam_scores_def = p_data['roam_def']
    total_value = int(p_data['impact_avg_atk'] + p_data['roam_avg_atk'] + p_data['impact_avg_def'] + p_data['roam_avg_def'])
    return op_overall_scores_atk, op_roam_scores_atk, op_overall_scores_def, op_roam_scores_def, total_value


display('coolvibes/lord_squishers')