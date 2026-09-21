"""
render.py —— 绘制模块
职责：画箭头、画棋盘、画各页面 UI、动画
所有 pygame 绘制集中在此，core.py 不依赖 pygame。
"""
import math
import pygame
from core import DIRS
from levels import LEVELS

# ── 配色（深蓝系） ──
BG          = (18, 24, 48)
CARD        = (32, 40, 72)
CELL        = (42, 50, 88)
CELL_HOVER  = (62, 72, 118)
CELL_HINT   = (45, 85, 65)
ARROW       = (235, 240, 252)
ARROW_BAD   = (240, 95, 95)
TEXT        = (255, 255, 255)
TEXT_DIM    = (155, 160, 188)
ACCENT      = (120, 210, 195)
GOLD        = (255, 210, 75)


# ── 画一个箭头 ──
def draw_arrow(surf, cx, cy, size, direction, color):
    """在 (cx, cy) 中心绘制方向箭头"""
    s = size * 0.35
    if direction == 'RIGHT':
        pygame.draw.line(surf, color, (cx - s, cy), (cx + s * 0.4, cy), 4)
        pygame.draw.polygon(surf, color, [
            (cx + s * 0.4, cy - s * 0.55),
            (cx + s,       cy),
            (cx + s * 0.4, cy + s * 0.55),
        ])
    elif direction == 'LEFT':
        pygame.draw.line(surf, color, (cx + s, cy), (cx - s * 0.4, cy), 4)
        pygame.draw.polygon(surf, color, [
            (cx - s * 0.4, cy - s * 0.55),
            (cx - s,       cy),
            (cx - s * 0.4, cy + s * 0.55),
        ])
    elif direction == 'UP':
        pygame.draw.line(surf, color, (cx, cy + s), (cx, cy - s * 0.4), 4)
        pygame.draw.polygon(surf, color, [
            (cx - s * 0.55, cy - s * 0.4),
            (cx,            cy - s),
            (cx + s * 0.55, cy - s * 0.4),
        ])
    elif direction == 'DOWN':
        pygame.draw.line(surf, color, (cx, cy - s), (cx, cy + s * 0.4), 4)
        pygame.draw.polygon(surf, color, [
            (cx - s * 0.55, cy + s * 0.4),
            (cx,            cy + s),
            (cx + s * 0.55, cy + s * 0.4),
        ])


# ── 画星星 ──
def draw_star(surf, cx, cy, r, color):
    pts = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(angle), cy + rad * math.sin(angle)))
    pygame.draw.polygon(surf, color, pts)


# ── 渐变背景（由上到下：深蓝→深紫蓝） ──
def draw_gradient_bg(surf, h=540):
    top    = (14, 20, 44)
    bottom = (28, 22, 54)
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (720, y))


# ── 按钮辅助函数 ──
def draw_button(surf, rect, text, font, hover=False):
    # hover 时按钮微微放大 + 光晕
    r2 = rect.inflate(10, 10) if hover else rect
    # 光晕（只 hover 时）
    if hover:
        glow = pygame.Surface(r2.size, pygame.SRCALPHA)
        pygame.draw.rect(glow, (120, 210, 195, 60), glow.get_rect(), border_radius=12)
        surf.blit(glow, r2)
    # 按钮主体
    color = (60, 95, 110) if hover else (40, 55, 75)
    pygame.draw.rect(surf, color, r2, border_radius=10)
    # 顶部亮边
    pygame.draw.line(surf, (90, 115, 140) if hover else (60, 78, 100),
                     (r2.left + 8, r2.top + 3), (r2.right - 8, r2.top + 3), 2)
    ts = font.render(text, True, TEXT)
    surf.blit(ts, ts.get_rect(center=r2.center))


def button_rect(x, y, w=130, h=38):
    return pygame.Rect(x, y, w, h)


# ── 计算棋盘位置 ──
def board_layout(rows, cols, win_w=720, top=70, bottom=70):
    avail_w = win_w - 40
    avail_h = 540 - top - bottom
    cell = min(avail_w // cols, avail_h // rows)
    bw = cell * cols
    bh = cell * rows
    bx = (win_w - bw) // 2
    by = top + (avail_h - bh) // 2
    return bx, by, cell


# ════════════════════════════════════════
#  各页面绘制函数
# ════════════════════════════════════════

def draw_menu(surf, font_l, font_m, time_ms=0):
    draw_gradient_bg(surf)

    # 顶部一排"漂浮的装饰箭头"（淡色 + 呼吸感）
    t = time_ms / 1000
    deco_pts = [(60, 90, 'RIGHT'), (180, 120, 'UP'), (540, 120, 'DOWN'), (660, 90, 'LEFT')]
    for x, y, d in deco_pts:
        alpha = 80 + int(40 * math.sin(t * 1.5 + x))
        float_y = y + int(math.sin(t * 2 + x * 0.01) * 6)   # 上下浮动
        tmp = pygame.Surface((50, 50), pygame.SRCALPHA)
        draw_arrow(tmp, 25, 25, 50, d, (150, 170, 210, alpha))
        surf.blit(tmp, (x - 25, float_y - 25))

    # 标题发光：先画一层扩散的"光晕"字（浅色 + 偏移），再画实体字
    glow_color = (90, 180, 165)
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
        glow = font_l.render("一 箭 又 一 箭", True, glow_color)
        surf.blit(glow, glow.get_rect(center=(360 + dx, 200 + dy)))
    title = font_l.render("一 箭 又 一 箭", True, ACCENT)
    surf.blit(title, title.get_rect(center=(360, 200)))

    # 副标题
    sub = font_m.render("点击箭头 · 路径无阻则飞出 · 有阻则失误", True, TEXT_DIM)
    surf.blit(sub, sub.get_rect(center=(360, 250)))

    # 开始按钮（带光晕 hover）
    btn = button_rect(295, 320, 130, 44)
    hover = btn.collidepoint(pygame.mouse.get_pos()) if pygame.mouse.get_pos() else False
    draw_button(surf, btn, "开始游戏", font_m, hover)

    # 底部提示（淡淡的）
    tip = font_m.render("→ 点击开始游戏 ←", True, TEXT_DIM)
    surf.blit(tip, tip.get_rect(center=(360, 400)))


def draw_level_select(surf, unlocked, stars, font_l, font_m, font_s):
    draw_gradient_bg(surf)
    title = font_l.render("选 择 关 卡", True, ACCENT)
    surf.blit(title, title.get_rect(center=(360, 50)))
    cols = 4
    bw, bh = 130, 100
    gap = 20
    total_w = cols * bw + (cols - 1) * gap
    sx = (720 - total_w) // 2
    sy = 130
    for i in range(len(LEVELS)):
        col = i % cols
        row = i // cols
        x = sx + col * (bw + gap)
        y = sy + row * (bh + gap)
        locked = i >= unlocked
        rect = pygame.Rect(x, y, bw, bh)
        color = (32, 38, 60) if locked else CARD
        pygame.draw.rect(surf, color, rect, border_radius=10)
        if locked:
            t = font_m.render("未解锁", True, TEXT_DIM)
            surf.blit(t, t.get_rect(center=rect.center))
        else:
            t = font_l.render(str(i + 1), True, TEXT)
            surf.blit(t, t.get_rect(center=(rect.centerx, rect.centery - 10)))
            # 星星
            for s in range(3):
                star_color = GOLD if s < stars[i] else (180, 175, 195)
                draw_star(surf, rect.centerx - 24 + s * 24, rect.bottom - 18, 8, star_color)
            tip = font_s.render("点击进入", True, TEXT_DIM)
            surf.blit(tip, tip.get_rect(center=(rect.centerx, rect.bottom - 4)))


def draw_game(surf, game, level_idx, font_m, font_s, mouse_pos):
    draw_gradient_bg(surf)
    # 顶部信息栏
    info_card = pygame.Rect(20, 12, 680, 48)
    pygame.draw.rect(surf, CARD, info_card, border_radius=10)
    info = f"第 {level_idx + 1} 关    剩余箭头 {game.arrows_left}    失误 {game.mistakes}/{game.max_mistakes}    用时 {game.elapsed}s"
    ts = font_m.render(info, True, TEXT)
    surf.blit(ts, ts.get_rect(center=info_card.center))

    # 棋盘
    bx, by, cs = board_layout(game.rows, game.cols)
    for r in range(game.rows):
        for c in range(game.cols):
            x = bx + c * cs
            y = by + r * cs
            rect = pygame.Rect(x + 2, y + 2, cs - 4, cs - 4)
            if (r, c) in game.hint_cells:
                pygame.draw.rect(surf, CELL_HINT, rect, border_radius=6)
            elif rect.collidepoint(mouse_pos):
                pygame.draw.rect(surf, CELL_HOVER, rect, border_radius=6)
            else:
                pygame.draw.rect(surf, CELL, rect, border_radius=6)
            d = game.board[r][c]
            if d != 0:
                color = ARROW
                ox, oy = 0, 0
                if game.shake and game.shake[0] == r and game.shake[1] == c:
                    t = game.shake[2]
                    ox = int(math.sin(t * 0.8) * 6)
                    color = ARROW_BAD
                cx = x + cs / 2 + ox
                cy = y + cs / 2 + oy
                draw_arrow(surf, cx, cy, cs, d, color)

    # 飞出动画
    for fa in game.fly_arrows:
        fa['progress'] += 0.06
        fa['alpha'] = max(0, int(255 * (1 - fa['progress'])))
        dr, dc = DIRS[fa['dir']]
        dist = fa['progress'] * cs * 3
        cx = bx + fa['c'] * cs + cs / 2 + dc * dist
        cy = by + fa['r'] * cs + cs / 2 + dr * dist
        if fa['alpha'] > 0:
            tmp = pygame.Surface((cs, cs), pygame.SRCALPHA)
            draw_arrow(tmp, cs / 2, cs / 2, cs, fa['dir'], (*ARROW, fa['alpha']))
            surf.blit(tmp, (cx - cs / 2, cy - cs / 2))
    game.fly_arrows = [fa for fa in game.fly_arrows if fa['alpha'] > 0]

    # 底部按钮
    by_btn = 470
    btns = [
        (f"撤销({3 - game.undo_count})", 30, by_btn),
        (f"提示({3 - game.hint_count})", 175, by_btn),
        ("重新开始", 320, by_btn),
        ("返回选关", 465, by_btn),
    ]
    for text, x, y in btns:
        rect = button_rect(x, y)
        hover = rect.collidepoint(mouse_pos)
        draw_button(surf, rect, text, font_s, hover)


def draw_win(surf, game, level_idx, stars, font_l, font_m, font_s, mouse_pos):
    draw_gradient_bg(surf)
    card = pygame.Rect(160, 120, 400, 300)
    pygame.draw.rect(surf, CARD, card, border_radius=16)
    t = font_l.render("太棒了！", True, GOLD)
    surf.blit(t, t.get_rect(center=(360, 180)))
    for i in range(3):
        c = GOLD if i < stars else (180, 175, 195)
        draw_star(surf, 300 + i * 60, 240, 16, c)
    info = font_m.render(f"用时 {game.elapsed}s  ·  失误 {game.mistakes} 次", True, TEXT_DIM)
    surf.blit(info, info.get_rect(center=(360, 290)))
    last = level_idx >= len(LEVELS) - 1
    if last:
        draw_button(surf, button_rect(295, 330), "返回选关", font_s, button_rect(295, 330).collidepoint(mouse_pos))
    else:
        draw_button(surf, button_rect(220, 330), "下一关", font_s, button_rect(220, 330).collidepoint(mouse_pos))
        draw_button(surf, button_rect(370, 330), "返回选关", font_s, button_rect(370, 330).collidepoint(mouse_pos))


def draw_lose(surf, game, level_idx, font_l, font_m, font_s, mouse_pos):
    draw_gradient_bg(surf)
    card = pygame.Rect(160, 120, 400, 260)
    pygame.draw.rect(surf, CARD, card, border_radius=16)
    t = font_l.render("再试一次吧！", True, ARROW_BAD)
    surf.blit(t, t.get_rect(center=(360, 200)))
    info = font_m.render(f"失误已达 {game.max_mistakes} 次", True, TEXT_DIM)
    surf.blit(info, info.get_rect(center=(360, 250)))
    draw_button(surf, button_rect(220, 300), "重来", font_s, button_rect(220, 300).collidepoint(mouse_pos))
    draw_button(surf, button_rect(370, 300), "返回选关", font_s, button_rect(370, 300).collidepoint(mouse_pos))
