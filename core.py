"""
core.py —— 核心游戏逻辑
职责：方向定义、路径检测、游戏状态管理
不依赖 pygame，纯 Python 逻辑，方便单独测试。
"""

# ── 方向字典：方向名 → (行偏移, 列偏移) ──
# 行向下增长（和屏幕坐标一致），所以"上"是 -1，"下"是 +1
DIRS = {
    'UP':    (-1, 0),   # 上：行 -1
    'DOWN':  (1, 0),    # 下：行 +1
    'LEFT':  (0, -1),   # 左：列 -1
    'RIGHT': (0, 1),    # 右：列 +1
}


def get_blocker(board, r, c, direction):
    """
    路径检测核心函数：
    从 (r, c) 出发，沿 direction 方向逐格扫描，
    遇到非空格子 → 返回阻挡者坐标 (br, bc)
    走出棋盘边界 → 返回 None（畅通）
    """
    dr, dc = DIRS[direction]
    nr, nc = r + dr, c + dc
    rows = len(board)
    cols = len(board[0]) if rows else 0
    while 0 <= nr < rows and 0 <= nc < cols:
        if board[nr][nc] != 0:
            return (nr, nc)
        nr += dr
        nc += dc
    return None


class GameState:
    """管理一局游戏的完整状态"""

    def __init__(self, level_data):
        self.rows = level_data['rows']
        self.cols = level_data['cols']
        self.max_mistakes = level_data.get('mistakes', 3)

        # 初始化棋盘：二维列表，0 = 空，'UP'/'DOWN'/'LEFT'/'RIGHT' = 箭头方向
        self.board = [[0] * self.cols for _ in range(self.rows)]
        for r, c, d in level_data['arrows']:
            self.board[r][c] = d

        self.arrows_left = len(level_data['arrows'])
        self.mistakes = 0

        # 撤销栈（最多 3 次）
        self.undo_stack = []
        self.undo_count = 0
        # 提示（最多 3 次）
        self.hint_count = 0
        self.hint_cells = []

        # 计时
        self.start_ticks = 0
        self.elapsed = 0

        # 动画状态
        self.fly_arrows = []       # 飞出动画列表
        self.shake = None          # [r, c, timer] 碰撞晃动

        # 结局
        self.won = False
        self.lost = False

    # ── 撤销 ──
    def push_undo(self):
        if self.undo_count >= 3:
            return False
        self.undo_stack.append({
            'board': [row[:] for row in self.board],
            'mistakes': self.mistakes,
            'arrows_left': self.arrows_left,
        })
        self.undo_count += 1
        return True

    def undo(self):
        if not self.undo_stack:
            return False
        state = self.undo_stack.pop()
        self.board = state['board']
        self.mistakes = state['mistakes']
        self.arrows_left = state['arrows_left']
        self.hint_cells = []
        return True

    # ── 提示：找出所有前方无阻挡的箭头 ──
    def get_hint(self):
        if self.hint_count >= 3:
            return []
        self.hint_count += 1
        self.hint_cells = []
        for r in range(self.rows):
            for c in range(self.cols):
                d = self.board[r][c]
                if d != 0 and get_blocker(self.board, r, c, d) is None:
                    self.hint_cells.append((r, c))
        return self.hint_cells

    # ── 点击格子 ──
    def click_cell(self, r, c):
        """
        返回值：
          'fly'     — 箭头飞出
          'blocked' — 被阻挡
          'empty'   — 空格 / 游戏已结束
        """
        if self.won or self.lost:
            return 'empty'
        d = self.board[r][c]
        if d == 0:
            return 'empty'

        # 保存撤销快照
        self.push_undo()

        if get_blocker(self.board, r, c, d) is not None:
            # 碰撞：失误 +1，启动晃动动画
            self.mistakes += 1
            self.shake = [r, c, 20]   # 20 帧
            if self.mistakes >= self.max_mistakes:
                self.lost = True
            return 'blocked'
        else:
            # 飞出：从棋盘移除，加入飞出动画
            self.board[r][c] = 0
            self.arrows_left -= 1
            self.fly_arrows.append({
                'r': r, 'c': c, 'dir': d,
                'alpha': 255, 'progress': 0.0,
            })
            self.hint_cells = []
            if self.arrows_left == 0:
                self.won = True
            return 'fly'

    # ── 星级评定 ──
    def get_stars(self):
        if self.mistakes == 0:
            return 3
        elif self.mistakes == 1:
            return 2
        else:
            return 1
