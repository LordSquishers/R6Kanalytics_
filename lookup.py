ATK_OPS = ['SLEDGE', 'THATCHER', 'ASH', 'THERMITE', 'TWITCH', 'MONTAGNE', 'GLAZ', 'FUZE', 'BLITZ', 'IQ', 'BUCK', 'BLACKBEARD', 'CAPITÃO', 'HIBANA', 'JACKAL', 'YING', 'ZOFIA', 'DOKKAEBI', 'LION', 'FINKA', 'MAVERICK', 'NOMAD', 'GRIDLOCK', 'NØKK', 'AMARU', 'KALI', 'IANA', 'ACE', 'ZERO', 'FLORES', 'OSA', 'SENS', 'GRIM']
DEF_OPS = ['SMOKE', 'MUTE', 'CASTLE', 'PULSE', 'DOC', 'ROOK', 'KAPKAN', 'TACHANKA', 'JÄGER', 'BANDIT', 'JÄGER', 'FROST', 'VALKYRIE', 'CAVEIRA', 'ECHO', 'MIRA', 'LESION', 'ELA', 'VIGIL', 'MAESTRO', 'ALIBI', 'CLASH', 'KAID', 'MOZZIE', 'WARDEN', 'GOYO', 'WAMAI', 'ORYX', 'MELUSI', 'ARUNI', 'THUNDERBIRD', 'THORN', 'AZAMI']


def get_op_side(operator_name):
    if operator_name in ATK_OPS:
        return 'ATK'
    if operator_name in DEF_OPS:
        return 'DEF'

