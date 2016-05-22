nXCUR = 'this-xcur-filename-is-undefined'
ukCNAME = 'UnknownMouseCapeCursorName'


name_table = [
    ('com.apple.coregraphics.Alias',    'Alias',            'alias',            False),
    ('com.apple.coregraphics.Arrow',    'Arrow',            'left-main',        False),
    ('com.apple.coregraphics.Copy',     'Copy',             nXCUR,              False),
    ('com.apple.coregraphics.Move',     'Move',             nXCUR,              False),
    ('com.apple.coregraphics.Wait',     'Wait',             'wait',             True),
    ('com.apple.coregraphics.Empty',    'Empty',            nXCUR,              False),
    ('com.apple.coregraphics.IBeam',    'IBeam',            'horizontal-text',  False),
    ('com.apple.coregraphics.IBeamXOR', 'IBeamXOR',         nXCUR,              False),
    ('com.apple.coregraphics.ArrowCtx', 'Ctx Arrow',        nXCUR,              False),
    ('com.apple.cursor.2',              'Link',             nXCUR,              False),
    ('com.apple.cursor.3',              'Forbidden',        'no-drop',          False),
    ('com.apple.cursor.4',              'Busy',             'progress',         True),
    ('com.apple.cursor.5',              'Copy Drag',        'dnd-copy',         False),
    ('com.apple.cursor.7',              'Crosshair',        'crosshair',        False),
    ('com.apple.cursor.8',              'Crosshair 2',      'crosshair',        False),
    ('com.apple.cursor.9',              'Camera 2',         nXCUR,              False),
    ('com.apple.cursor.10',             'Camera',           nXCUR,              False),
    ('com.apple.cursor.11',             'Closed',           'closedhand',       False),
    ('com.apple.cursor.12',             'Open',             'openhand',         False),
    ('com.apple.cursor.13',             'Pointing',         'pointer',          False),
    ('com.apple.cursor.14',             'Counting Up',      nXCUR,              False),
    ('com.apple.cursor.15',             'Counting Down',    nXCUR,              False),
    ('com.apple.cursor.16',             'Counting Up/Down', nXCUR,              False),
    ('com.apple.cursor.17',             'Resize W',         nXCUR,              False),
    ('com.apple.cursor.18',             'Resize E',         nXCUR,              False),
    ('com.apple.cursor.19',             'Resize W-E',       'col-resize',       False),
    ('com.apple.cursor.20',             'Cell XOR',         nXCUR,              False),
    ('com.apple.cursor.21',             'Resize N',         nXCUR,              False),
    ('com.apple.cursor.22',             'Resize S',         nXCUR,              False),
    ('com.apple.cursor.23',             'Resize N-S',       'row-resize',       False),
    ('com.apple.cursor.24',             'Ctx Menu',         'context-menu',     False),
    ('com.apple.cursor.25',             'Poof',             'pirate',           False),
    ('com.apple.cursor.26',             'IBeamH.',          'vertical-text',    False),
    ('com.apple.cursor.27',             'Window E',         'right-arrow',      False),
    ('com.apple.cursor.28',             'Window E-W',       nXCUR,              False),
    ('com.apple.cursor.29',             'Window NE',        nXCUR,              False),
    ('com.apple.cursor.30',             'Window NE-SW',     'nesw-resize',      False),
    ('com.apple.cursor.31',             'Window N',         'up-arrow',         False),
    ('com.apple.cursor.32',             'Window N-S',       'ns-resize',        False),
    ('com.apple.cursor.33',             'Window NW',        nXCUR,              False),
    ('com.apple.cursor.34',             'Window NW-SE',     'nwse-resize',      False),
    ('com.apple.cursor.35',             'Window SE',        nXCUR,              False),
    ('com.apple.cursor.36',             'Window S',         'down-arrow',       False),
    ('com.apple.cursor.37',             'Window SW',        nXCUR,              False),
    ('com.apple.cursor.38',             'Window W',         'left-arrow',       False),
    ('com.apple.cursor.39',             'Resize Square',    'fleur',            False),
    ('com.apple.cursor.40',             'Help',             'help',             False),
    ('com.apple.cursor.41',             'Cell',             'cell',             False),
    ('com.apple.cursor.42',             'Zoom In',          'zoom-in',          False),
    ('com.apple.cursor.43',             'Zoom Out',         'zoom-out',         False)
]


cursor_name_map = {k: v for (v, k, f, a) in name_table}


