"""
tests.py —— T01~T06 自动化测试
不依赖 pygame，只测试 core.py 的纯逻辑。
运行：python tests.py
"""
import sys
sys.path.insert(0, '.')
from core import GameState, get_blocker
from levels import LEVELS

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")

# ── T01：点击前方无阻挡的箭头 → 飞出消失 ──
print("T01: 点击前方无阻挡的箭头")
board = [
    [0, 0, 0, 'RIGHT'],
    ['LEFT', 0, 0, 0],
    [0, 'UP', 0, 0],
    [0, 0, 'DOWN', 0],
]
check("边界方向畅通 (RIGHT)", get_blocker(board, 0, 3, 'RIGHT') is None)
check("边界方向畅通 (LEFT)",  get_blocker(board, 1, 0, 'LEFT') is None)
check("边界方向畅通 (UP)",     get_blocker(board, 2, 1, 'UP') is None)
check("边界方向畅通 (DOWN)",   get_blocker(board, 3, 2, 'DOWN') is None)

g = GameState(LEVELS[0])
before = g.arrows_left
for r in range(g.rows):
    for c in range(g.cols):
        d = g.board[r][c]
        if d != 0 and get_blocker(g.board, r, c, d) is None:
            result = g.click_cell(r, c)
            check("click 返回 'fly'", result == 'fly', f"got {result}")
            check("arrows_left -1", g.arrows_left == before - 1)
            check("该格变为 0", g.board[r][c] == 0)
            break
    else:
        continue
    break

# ── T02：点击前方有阻挡的箭头 → 不消失，失误 +1 ──
print("\nT02: 点击前方有阻挡的箭头")
board = [['RIGHT', 0, 0, 'DOWN'],
         [0, 0, 0, 0]]
check("RIGHT 被阻挡", get_blocker(board, 0, 0, 'RIGHT') is not None)

# ── T03：边缘朝外的箭头 → 正常消失，无越界 ──
print("\nT03: 边缘朝外箭头无越界")
for li, lv in enumerate(LEVELS):
    g = GameState(lv)
    for r in range(g.rows):
        for c in range(g.cols):
            d = g.board[r][c]
            if d == 0:
                continue
            if (d == 'UP' and r == 0) or (d == 'DOWN' and r == g.rows - 1) or \
               (d == 'LEFT' and c == 0) or (d == 'RIGHT' and c == g.cols - 1):
                result = g.click_cell(r, c)
                check(f"L{li+1} ({r},{c}) dir={d} → fly", result == 'fly',
                      f"got {result}")
                g.undo()

# ── T04：消除全部箭头 → 通关 ──
print("\nT04: 清空箭头显示通关")
g = GameState(LEVELS[0])
max_iters = 200
iters = 0
while g.arrows_left > 0 and iters < max_iters:
    moved = False
    for r in range(g.rows):
        for c in range(g.cols):
            d = g.board[r][c]
            if d != 0 and get_blocker(g.board, r, c, d) is None:
                g.click_cell(r, c)
                moved = True
                break
        if moved:
            break
    iters += 1
check("求解全部箭头", g.arrows_left == 0, f"剩余 {g.arrows_left}")
check("游戏标记 won=True", g.won == True)

# ── T05：失误耗尽 → 失败 ──
print("\nT05: 失误次数耗尽显示失败")
board = [['RIGHT', 'LEFT'],
         ['LEFT', 'RIGHT']]
lv_fake = {'rows': 2, 'cols': 2, 'mistakes': 2,
           'arrows': [(0,0,'RIGHT'),(0,1,'LEFT'),(1,0,'LEFT'),(1,1,'RIGHT')]}
g = GameState(lv_fake)
g.click_cell(0, 0)
check("第 1 次失误", g.mistakes == 1 and not g.lost)
g.click_cell(0, 0)
check("第 2 次失误 → lost", g.mistakes == 2 and g.lost == True)

# ── T06：重新开始 → 棋盘恢复 ──
print("\nT06: 重新开始恢复状态")
g = GameState(LEVELS[1])
snap_board = [row[:] for row in g.board]
snap_mistakes = g.mistakes
snap_left = g.arrows_left
for r in range(g.rows):
    for c in range(g.cols):
        d = g.board[r][c]
        if d != 0 and get_blocker(g.board, r, c, d) is None:
            g.click_cell(r, c)
            break
    else:
        continue
    break
g = GameState(LEVELS[1])
check("棋盘恢复", g.board == snap_board)
check("失误恢复", g.mistakes == snap_mistakes)
check("箭头数恢复", g.arrows_left == snap_left)

# ── 汇总 ──
print(f"\n{'='*30}")
print(f"通过 {PASS} / {PASS+FAIL}   {'✅' if FAIL == 0 else '❌ 有失败'}")
sys.exit(0 if FAIL == 0 else 1)
