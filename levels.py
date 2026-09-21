"""
levels.py —— 关卡数据
每个关卡定义：网格大小、失误上限、箭头列表 [(行, 列, 方向), ...]
方向字符串：'UP' 上 / 'DOWN' 下 / 'LEFT' 左 / 'RIGHT' 右
"""

LEVELS = [
    # ── 第 1 关：4×4，6 个箭头，入门 ──
    {
        'rows': 4, 'cols': 4, 'mistakes': 3,
        'arrows': [
            (0, 0, 'DOWN'),  (0, 1, 'RIGHT'), (0, 3, 'DOWN'),
            (2, 0, 'LEFT'),  (2, 3, 'RIGHT'),
            (3, 1, 'UP'),
        ],
    },
    # ── 第 2 关：4×4，8 个箭头，进阶 ──
    {
        'rows': 4, 'cols': 4, 'mistakes': 3,
        'arrows': [
            (0, 0, 'RIGHT'), (0, 2, 'UP'), (0, 3, 'DOWN'),
            (1, 1, 'DOWN'),
            (2, 0, 'LEFT'),  (2, 1, 'DOWN'), (2, 3, 'RIGHT'),
            (3, 3, 'LEFT'),
        ],
    },
    # ── 第 3 关：5×5，10 个箭头，挑战 ──
    {
        'rows': 5, 'cols': 5, 'mistakes': 3,
        'arrows': [
            (0, 0, 'RIGHT'), (0, 2, 'DOWN'),
            (1, 1, 'DOWN'),  (1, 4, 'UP'),
            (2, 0, 'LEFT'),  (2, 2, 'RIGHT'),
            (3, 0, 'DOWN'),  (3, 3, 'LEFT'),
            (4, 3, 'RIGHT'), (4, 4, 'UP'),
        ],
    },
    # ── 第 4 关：6×6，12 个箭头，高手 ──
    {
        'rows': 6, 'cols': 6, 'mistakes': 4,
        'arrows': [
            (0, 2, 'DOWN'),  (0, 3, 'DOWN'),
            (1, 2, 'RIGHT'),
            (2, 0, 'LEFT'),  (2, 2, 'RIGHT'), (2, 4, 'DOWN'),
            (3, 1, 'UP'),    (3, 5, 'RIGHT'),
            (4, 3, 'LEFT'),  (4, 5, 'LEFT'),
            (5, 0, 'DOWN'),  (5, 4, 'RIGHT'),
        ],
    },
]
