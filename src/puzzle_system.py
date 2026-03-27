# -*- coding: utf-8 -*-
"""谜题交互系统"""
import pygame, math, random
from config import *

class PuzzleManager:
    def __init__(self, level_data):
        self.level_data = level_data
        self.puzzle = level_data.get("puzzle")
        self.state = "active"  # active, solved, failed
        self.hint_shown = False
        self.message = ""
        self.msg_timer = 0
        self.elements = []
        self.answer = []
        self.selected = []
        self.success = False
        self._init_puzzle()

    def _init_puzzle(self):
        pt = self.puzzle.get("type") if self.puzzle else None
        if pt == "door_lock":
            self._init_door_lock()
        elif pt == "floor_tiles":
            self._init_floor_tiles()
        elif pt == "star_lantern":
            self._init_star_lantern()
        elif pt == "fengshui_mech":
            self._init_fengshui()
        elif pt == "relic_appraisal":
            self._init_relic()
        elif pt == "escape_timer":
            self._init_escape()
        elif pt == "text_password":
            self._init_text()

    # ---- 门锁 ----
    def _init_door_lock(self):
        symbols = self.puzzle["symbols"]
        for i, sym in enumerate(symbols):
            col = i % 4
            row = i // 4
            x = SCREEN_WIDTH//2 - 200 + col * 100
            y = SCREEN_HEIGHT//2 - 100 + row * 100
            self.elements.append({"type": "symbol", "x": x, "y": y,
                                    "symbol": sym, "idx": i, "lit": False})

    # ---- 地板 ----
    def _init_floor_tiles(self):
        tiles = self.puzzle.get("tiles", [])
        for t in tiles:
            self.elements.append({
                "type": "tile", "x": t["x"], "y": t["y"],
                "w": 60, "h": 60, "safe": t["safe"],
                "pressed": False, "triggered": False
            })
        self.answer = self.puzzle.get("sequence", [])

    # ---- 七星灯 ----
    def _init_star_lantern(self):
        positions = self.puzzle.get("lantern_positions", [])
        for lp in positions:
            self.elements.append({
                "type": "lantern", "x": lp["x"], "y": lp["y"],
                "star": lp["star"], "name": lp["name"],
                "lit": False, "hover": False
            })
        self.answer = self.puzzle.get("correct_order", [])
        self.selected = []

    # ---- 河图洛书 ----
    def _init_fengshui(self):
        positions = self.puzzle.get("positions", [])
        for p in positions:
            self.elements.append({
                "type": "fs_pos", "x": p["x"], "y": p["y"],
                "w": 80, "h": 80, "num": p["num"],
                "pressed": False, "lit": False
            })
        self.answer = self.puzzle.get("correct_nums", [])

    # ---- 鉴定明器 ----
    def _init_relic(self):
        items = self.puzzle.get("items", [])
        for it in items:
            self.elements.append({
                "type": "relic", "x": it["x"], "y": it["y"],
                "name": it["name"], "id": it["id"],
                "cursed": it["is_cursed"], "examined": False,
                "selected": False
            })

    # ---- 逃生倒计时 ----
    def _init_escape(self):
        self.escape_timer = self.puzzle.get("time_limit", 60) * FPS
        self.escape_done = False

    # ---- 文字密码 ----
    def _init_text(self):
        pass

    def handle_event(self, event, player_pos):
        pt = self.puzzle.get("type") if self.puzzle else None
        if pt == "door_lock":
            return self._handle_door_lock(event)
        elif pt == "floor_tiles":
            return self._handle_floor_tiles(event, player_pos)
        elif pt == "star_lantern":
            return self._handle_star_lantern(event)
        elif pt == "fengshui_mech":
            return self._handle_fengshui(event)
        elif pt == "relic_appraisal":
            return self._handle_relic(event)
        return None

    def _handle_door_lock(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for el in self.elements:
                if el["type"] == "symbol":
                    rx, ry = el["x"], el["y"]
                    if rx - 30 < mx < rx + 30 and ry - 30 < my < ry + 30:
                        el["lit"] = True
                        self.selected.append(el["idx"])
                        if len(self.selected) == 4:
                            correct = self.puzzle["answer"]
                            if self.selected == correct:
                                self._solve()
                            else:
                                self._fail()
                        return True
        return False

    def _handle_floor_tiles(self, event, player_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for el in self.elements:
                if el["type"] == "tile":
                    tx, ty = el["x"], el["y"]
                    if tx - 5 < mx < tx + el["w"] + 5 and ty - 5 < my < ty + el["h"] + 5:
                        el["pressed"] = True
                        if not el["safe"]:
                            self._fail()
                            return "trap"
                        else:
                            self.answer.append(el["idx"])
                            return "step"
        return None

    def _handle_star_lantern(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for el in self.elements:
                if el["type"] == "lantern":
                    tx, ty = el["x"], el["y"]
                    if abs(tx - mx) < 35 and abs(ty - my) < 35:
                        next_star = len(self.selected) + 1
                        if el["star"] == next_star:
                            el["lit"] = True
                            self.selected.append(el["star"])
                            if len(self.selected) == 7:
                                self._solve()
                        else:
                            # 重置
                            for e in self.elements:
                                if e["type"] == "lantern":
                                    e["lit"] = False
                            self.selected = []
                        return True
        return False

    def _handle_fengshui(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for el in self.elements:
                if el["type"] == "fs_pos":
                    if (el["x"] < mx < el["x"]+el["w"] and
                        el["y"] < my < el["y"]+el["h"]):
                        if len(self.selected) < 4:
                            el["lit"] = True
                            self.selected.append(el["num"])
                            if len(self.selected) == 4:
                                if self.selected == self.answer:
                                    self._solve()
                                else:
                                    for e in self.elements:
                                        if e["type"] == "fs_pos":
                                            e["lit"] = False
                                    self.selected = []
                                    self._fail()
                        return True
        return False

    def _handle_relic(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for el in self.elements:
                if el["type"] == "relic":
                    tx, ty = el["x"], el["y"]
                    if abs(tx - mx) < 40 and abs(ty - my) < 40:
                        el["examined"] = True
                        return True
        return False

    def _solve(self):
        self.state = "solved"
        self.success = True
        self.message = self.puzzle.get("success_msg", "解谜成功！")

    def _fail(self):
        self.message = "机关触发！你受到了伤害！"
        self.msg_timer = 180
        # 重置
        for el in self.elements:
            el["pressed"] = False
        self.selected = []

    def update(self, dt=None):
        if self.msg_timer > 0:
            self.msg_timer -= 1
        pt = self.puzzle.get("type") if self.puzzle else None
        if pt == "escape_timer" and not self.escape_done:
            self.escape_timer -= 1
            if self.escape_timer <= 0:
                self.state = "failed"
                self.message = "墓室完全坍塌！撤离失败..."
        # 悬浮检测
        mx, my = pygame.mouse.get_pos()
        for el in self.elements:
            if el["type"] == "lantern":
                el["hover"] = abs(el["x"]-mx) < 35 and abs(el["y"]-my) < 35

    def draw(self, surface):
        pt = self.puzzle.get("type") if self.puzzle else None
        if pt == "door_lock":
            self._draw_door_lock(surface)
        elif pt == "floor_tiles":
            self._draw_floor_tiles(surface)
        elif pt == "star_lantern":
            self._draw_star_lantern(surface)
        elif pt == "fengshui_mech":
            self._draw_fengshui(surface)
        elif pt == "relic_appraisal":
            self._draw_relic(surface)
        elif pt == "escape_timer":
            self._draw_escape(surface)
        elif pt == "text_password":
            self._draw_text(surface)
        # 消息显示
        if self.message and (self.msg_timer > 0 or self.state == "solved"):
            self._draw_message(surface)
        # 提示
        if self.puzzle and not self.hint_shown and self.state == "active":
            self._draw_hint(surface)

    def _draw_symbol_btn(self, surface, x, y, symbol, lit):
        r = 30
        color = (220,180,80) if lit else (60,48,30)
        border = (180,140,50) if lit else (80,65,35)
        pygame.draw.circle(surface, color, (x, y), r)
        pygame.draw.circle(surface, border, (x, y), r, 3)
        if lit:
            pygame.draw.circle(surface, (255,220,100), (x, y), r-5)
        font = pygame.font.SysFont("SimSun", 28)
        txt = font.render(symbol, True, (40,30,15))
        rect = txt.get_rect(center=(x, y))
        surface.blit(txt, rect)

    def _draw_door_lock(self, surface):
        # 标题
        font_title = pygame.font.SysFont("SimHei", 26, bold=True)
        title = font_title.render(self.puzzle["title"], True, (220,180,80))
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 120))
        desc = pygame.font.SysFont("SimHei", 16).render(self.puzzle["description"], True, (180,160,120))
        surface.blit(desc, (SCREEN_WIDTH//2 - desc.get_width()//2, 160))
        for el in self.elements:
            self._draw_symbol_btn(surface, el["x"], el["y"], el["symbol"], el["lit"])

    def _draw_floor_tiles(self, surface):
        for el in self.elements:
            if el["type"] == "tile":
                x, y = el["x"], el["y"]
                w, h = el["w"], el["h"]
                color = (80,160,80) if el["safe"] else (160,30,30)
                if el["pressed"]:
                    color = (40,40,40)
                pygame.draw.rect(surface, color, [x, y, w, h])
                pygame.draw.rect(surface, (50,40,25), [x, y, w, h], 2)
                # 数字
                idx = self.elements.index(el)
                font = pygame.font.SysFont("Arial", 14)
                txt = font.render(str(idx+1), True, (255,220,180))
                surface.blit(txt, (x+w//2-5, y+h//2-8))

    def _draw_star_lantern(self, surface):
        # 标题
        font_title = pygame.font.SysFont("SimHei", 24, bold=True)
        title = font_title.render(self.puzzle["title"], True, (220,180,80))
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 40))
        desc = pygame.font.SysFont("SimHei", 14).render(
            f"已点燃: {len(self.selected)}/7", True, (200,170,100))
        surface.blit(desc, (SCREEN_WIDTH//2 - desc.get_width()//2, 75))
        for el in self.elements:
            if el["type"] == "lantern":
                x, y = el["x"], el["y"]
                col = (255,200,80) if el["lit"] else (60,50,30)
                pygame.draw.circle(surface, col, (x, y), 25)
                pygame.draw.circle(surface, (100,80,30), (x, y), 28, 2)
                if el["lit"]:
                    pygame.draw.circle(surface, (255,240,150), (x, y), 18)
                    # 光芒
                    for a in range(0, 360, 60):
                        rad = math.radians(a)
                        px = x + int(math.cos(rad) * 32)
                        py = y + int(math.sin(rad) * 32)
                        pygame.draw.line(surface, (255,220,100), (x, y), (px, py), 2)
                if el["hover"]:
                    font = pygame.font.SysFont("SimHei", 12)
                    txt = font.render(el["name"], True, (220,190,100))
                    surface.blit(txt, (x - txt.get_width()//2, y - 45))
                    star_txt = font.render(f"第{el['star']}星", True, (180,150,80))
                    surface.blit(star_txt, (x - star_txt.get_width()//2, y + 30))

    def _draw_fengshui(self, surface):
        font_title = pygame.font.SysFont("SimHei", 22, bold=True)
        title = font_title.render(self.puzzle["title"], True, (220,180,80))
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
        for el in self.elements:
            if el["type"] == "fs_pos":
                x, y, w, h = el["x"], el["y"], el["w"], el["h"]
                color = (220,180,80) if el["lit"] else (40,32,20)
                border = (180,140,50) if el["lit"] else (80,65,35)
                pygame.draw.rect(surface, color, [x, y, w, h])
                pygame.draw.rect(surface, border, [x, y, w, h], 3)
                font = pygame.font.SysFont("SimHei", 30, bold=True)
                txt = font.render(str(el["num"]), True, (40,30,15))
                surface.blit(txt, (x + w//2 - txt.get_width()//2, y + h//2 - txt.get_height()//2))

    def _draw_relic(self, surface):
        font_title = pygame.font.SysFont("SimHei", 22, bold=True)
        title = font_title.render("明器鉴定台", True, (220,180,80))
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
        for el in self.elements:
            if el["type"] == "relic":
                x, y = el["x"], el["y"]
                img = load_image(f"assets/images/items/{el['id']}.png")
                surface.blit(img, (x - 16, y - 16))
                if el["examined"]:
                    col = (80,200,80) if not el["cursed"] else (200,50,50)
                    status = "安全" if not el["cursed"] else "⚠ 诅咒"
                    font = pygame.font.SysFont("SimHei", 12, bold=True)
                    txt = font.render(status, True, col)
                    surface.blit(txt, (x - txt.get_width()//2, y + 20))

    def _draw_escape(self, surface):
        total = self.puzzle.get("time_limit", 60) * FPS
        remaining = self.escape_timer
        sec = remaining // FPS
        color = (80,220,80) if sec > 20 else (220,80,80) if sec > 10 else (255,50,50)
        font = pygame.font.SysFont("Arial", 48, bold=True)
        txt = font.render(f"{sec}", True, color)
        surface.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, SCREEN_HEIGHT//2 - 60))
        label = pygame.font.SysFont("SimHei", 18).render("秒内逃出墓穴！", True, (200,170,100))
        surface.blit(label, (SCREEN_WIDTH//2 - label.get_width()//2, SCREEN_HEIGHT//2))
        # 进度条
        bw = 400
        bx = SCREEN_WIDTH//2 - bw//2
        pygame.draw.rect(surface, (30,20,20), [bx, SCREEN_HEIGHT//2+30, bw, 16], border_radius=5)
        pw = int((remaining/total)*bw)
        pygame.draw.rect(surface, color, [bx, SCREEN_HEIGHT//2+30, pw, 16], border_radius=5)

    def _draw_text(self, surface):
        pass

    def _draw_message(self, surface):
        font = pygame.font.SysFont("SimHei", 20)
        txt = font.render(self.message, True, (220,180,80))
        x = SCREEN_WIDTH//2 - txt.get_width()//2
        y = SCREEN_HEIGHT - 180
        pygame.draw.rect(surface, (10,8,6,230), [x-15, y-8, txt.get_width()+30, 38], border_radius=8)
        pygame.draw.rect(surface, (180,140,60), [x-15, y-8, txt.get_width()+30, 38], width=2, border_radius=8)
        surface.blit(txt, (x, y))

    def _draw_hint(self, surface):
        hints = self.puzzle.get("hints", [])
        if not hints:
            return
        font = pygame.font.SysFont("SimHei", HINT_FONT_SIZE)
        hint = hints[0]
        txt = font.render(hint, True, (180,155,100))
        x = SCREEN_WIDTH//2 - txt.get_width()//2
        y = HINT_BOX_Y
        pygame.draw.rect(surface, (8,6,4,180), [x-10, y-5, txt.get_width()+20, 32], border_radius=6)
        surface.blit(txt, (x, y))
        small = pygame.font.SysFont("SimHei", 11)
        tip = small.render("[ 按 H 键隐藏提示 ]", True, (100,85,60))
        surface.blit(tip, (x + txt.get_width() - 120, y + 35))
