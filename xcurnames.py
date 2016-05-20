nXCUR = 'this-xcur-filename-is-undefined'
ukCNAME = 'UnknownMouseCapeCursorName'

name_table = [
    ('com.apple.coregraphics.Alias',    'Alias',        'alias'),
    ('com.apple.coregraphics.Arrow',    'Arrow',        'left-main'),
    ('com.apple.coregraphics.Copy',     'Copy',         nXCUR),
    ('com.apple.coregraphics.IBeam',    'IBeam',        'horizontal-text'),
    ('com.apple.cursor.3',              ukCNAME,        nXCUR),
    ('com.apple.cursor.4',              ukCNAME,        nXCUR),
    ('com.apple.cursor.5',              ukCNAME,        nXCUR),
    ('com.apple.cursor.7',              ukCNAME,        nXCUR),
    ('com.apple.cursor.11',             ukCNAME,        nXCUR),
    ('com.apple.cursor.13',             ukCNAME,        nXCUR),
    ('com.apple.cursor.18',             ukCNAME,        nXCUR),
    ('com.apple.cursor.19',             ukCNAME,        nXCUR),
    ('com.apple.cursor.21',             ukCNAME,        nXCUR),
    ('com.apple.cursor.23',             ukCNAME,        nXCUR),
    ('com.apple.cursor.24',             ukCNAME,        nXCUR),
    ('com.apple.cursor.30',             ukCNAME,        nXCUR),
    ('com.apple.cursor.32',             ukCNAME,        nXCUR),
    ('com.apple.cursor.34',             ukCNAME,        nXCUR),
    ('com.apple.cursor.36',             ukCNAME,        nXCUR),
    ('com.apple.cursor.38',             ukCNAME,        nXCUR),
    ('com.apple.cursor.39',             ukCNAME,        nXCUR),
    ('com.apple.cursor.40',             ukCNAME,        nXCUR),
    ('com.apple.cursor.41',             ukCNAME,        nXCUR)
]


def mc_to_plist(mouse_cape_cursor_name):
    for line in name_table:
        if line[1] == mouse_cape_cursor_name:
            return line[0]
    return None
