"""
main.py —— 入口文件
职责：页面管理、事件处理、主循环
运行：python main.py
"""
import sys
import json
import os
import pygame
from core import GameState, get_blocker
from levels import LEVELS
import render as R
import sound

SAVE_FILE = os.path.join(os.path.dirname(__file__), 'save.json')


def save_progress(unlocked, stars):
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'unlocked': unlocked, 'stars': stars}, f)
    except Exception:
        pass


def load_progress():
    try:
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            d = json.load(f)
        return d.get('unlocked', 1), d.get('stars', [0] * len(LEVELS))
    except Exception:
        return 1, [0] * len(LEVELS)

# ── 页面状态常量 ──
MENU          = 0
LEVEL_SELECT  = 1
PLAYING       = 2
WIN           = 3
LOSE          = 4

WIN_W, WIN_H = 720, 540


class App:
    def __init__(self):
        pygame.init()
        sound.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("一箭又一箭")
        self.clock = pygame.time.Clock()
        # 字体：微软雅黑（硬写路径绕开 SysFont 扫描）
        try:
            font_path = r"C:\Windows\Fonts\msyh.ttc"
            self.font_l = pygame.font.Font(font_path, 36)
            self.font_m = pygame.font.Font(font_path, 22)
            self.font_s = pygame.font.Font(font_path, 16)
        except (FileNotFoundError, OSError):
            self.font_l = pygame.font.Font(None, 36)
            self.font_m = pygame.font.Font(None, 22)
            self.font_s = pygame.font.Font(None, 16)

        self.page = MENU
        self.level_idx = 0
        self.unlocked, self.stars = load_progress()
        self.game = None

    # ── 启动某关 ──
    def start_level(self, idx):
        self.level_idx = idx
        self.game = GameState(LEVELS[idx])
        self.game.start_ticks = pygame.time.get_ticks()
        self.page = PLAYING

    # ── 主循环 ──
    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
            self.update()
            self.render(mouse_pos)
            pygame.display.flip()
            self.clock.tick(60)

    # ── 事件处理 ──
    def handle_click(self, pos):
        if self.page == MENU:
            if R.button_rect(295, 320, 130, 44).collidepoint(pos):
                self.page = LEVEL_SELECT

        elif self.page == LEVEL_SELECT:
            cols = 4
            bw, bh, gap = 130, 100, 20
            total_w = cols * bw + (cols - 1) * gap
            sx = (WIN_W - total_w) // 2
            sy = 130
            for i in range(len(LEVELS)):
                col = i % cols
                row = i // cols
                x = sx + col * (bw + gap)
                y = sy + row * (bh + gap)
                if pygame.Rect(x, y, bw, bh).collidepoint(pos) and i < self.unlocked:
                    self.start_level(i)
                    return

        elif self.page == PLAYING:
            # 检查按钮
            by_btn = 470
            if R.button_rect(30, by_btn).collidepoint(pos):
                if self.game.undo():
                    pass  # 撤销成功
                return
            if R.button_rect(175, by_btn).collidepoint(pos):
                self.game.get_hint()
                return
            if R.button_rect(320, by_btn).collidepoint(pos):
                self.start_level(self.level_idx)  # 重新开始
                return
            if R.button_rect(465, by_btn).collidepoint(pos):
                self.page = LEVEL_SELECT
                return
            # 检查棋盘点击
            bx, by, cs = R.board_layout(self.game.rows, self.game.cols)
            cx, cy = pos
            if bx <= cx < bx + cs * self.game.cols and by <= cy < by + cs * self.game.rows:
                c = (cx - bx) // cs
                r = (cy - by) // cs
                outcome = self.game.click_cell(int(r), int(c))
                if outcome == 'fly':
                    sound.play('fly')
                elif outcome == 'blocked':
                    sound.play('blocked')

        elif self.page == WIN:
            last = self.level_idx >= len(LEVELS) - 1
            if last:
                if R.button_rect(295, 330).collidepoint(pos):
                    self.page = LEVEL_SELECT
            else:
                if R.button_rect(220, 330).collidepoint(pos):
                    self.start_level(self.level_idx + 1)
                elif R.button_rect(370, 330).collidepoint(pos):
                    self.page = LEVEL_SELECT

        elif self.page == LOSE:
            if R.button_rect(220, 300).collidepoint(pos):
                self.start_level(self.level_idx)
            elif R.button_rect(370, 300).collidepoint(pos):
                self.page = LEVEL_SELECT

    # ── 更新逻辑 ──
    def update(self):
        if self.page == PLAYING and self.game:
            # 计时
            self.game.elapsed = (pygame.time.get_ticks() - self.game.start_ticks) // 1000
            # 晃动计时
            if self.game.shake:
                self.game.shake[2] -= 1
                if self.game.shake[2] <= 0:
                    self.game.shake = None
            # 胜负判定
            if self.game.won and self.page == PLAYING:
                new_unlock = min(self.level_idx + 2, len(LEVELS))
                self.unlocked = max(self.unlocked, new_unlock)
                s = self.game.get_stars()
                self.stars[self.level_idx] = max(self.stars[self.level_idx], s)
                save_progress(self.unlocked, self.stars)
                sound.play('win')
                self.page = WIN
            elif self.game.lost and self.page == PLAYING:
                sound.play('lose')
                self.page = LOSE

    # ── 渲染 ──
    def render(self, mouse_pos):
        if self.page == MENU:
            R.draw_menu(self.screen, self.font_l, self.font_m,
                        time_ms=pygame.time.get_ticks())
        elif self.page == LEVEL_SELECT:
            R.draw_level_select(self.screen, self.unlocked, self.stars,
                                self.font_l, self.font_m, self.font_s)
        elif self.page == PLAYING:
            R.draw_game(self.screen, self.game, self.level_idx,
                        self.font_m, self.font_s, mouse_pos)
        elif self.page == WIN:
            R.draw_win(self.screen, self.game, self.level_idx,
                       self.stars[self.level_idx],
                       self.font_l, self.font_m, self.font_s, mouse_pos)
        elif self.page == LOSE:
            R.draw_lose(self.screen, self.game, self.level_idx,
                        self.font_l, self.font_m, self.font_s, mouse_pos)


def main():
    App().run()


if __name__ == "__main__":
    main()
