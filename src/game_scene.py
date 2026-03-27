# -*- coding: utf-8 -*-
"""游戏主场景"""
import pygame, math, random, os
from config import *
from entities import ParticleSystem
from level_data import LEVELS, get_level, Wall
from puzzle_system import PuzzleManager

pygame.init()

class GameScene:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"
        self.current_level_id = 1
        self.level = None
        self.player = None
        self.monsters = []
        self.items = []
        self.traps = []
        self.walls = []
        self.puzzle_mgr = None
        self.particles = ParticleSystem(max_count=400)
        self.light_layer = LightLayer()
        self.camera_x = 0
        self.camera_y = 0
        self.screen_shake = 0
        self.fade_alpha = 255
        self.fade_dir = -1
        self.msg_timer = 0
        self.msg_text = ""
        self.msg_color = COLORS["gold"]
        self.level_bg = None
        self.ambient_timer = 0
        self.hint_visible = True
        self.dust_timer = 0.0
        self._generate_resources()
        self._init_menu()

    def _generate_resources(self):
        from resources import generate_all
        try:
            generate_all()
        except Exception as e:
            print(f"资源: {e}")

    def _init_menu(self):
        self.menu_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.menu_bg.fill(COLORS["dark"])
        for y in range(0, SCREEN_HEIGHT, 3):
            alpha = int(20 * (1 - abs(y - SCREEN_HEIGHT//2) / (SCREEN_HEIGHT//2)))
            pygame.draw.line(self.menu_bg, (25, 20, 15), (0, y), (SCREEN_WIDTH, y))
        font_title = pygame.font.SysFont("SimHei", 72, bold=True)
        font_sub = pygame.font.SysFont("SimSun", 28)
        # 光晕
        glow = pygame.Surface((600, 300), pygame.SRCALPHA)
        for r in range(200, 0, -4):
            a = int(15 * (r / 200))
            pygame.draw.ellipse(glow, (180, 130, 40, a), [300-r, 150-r, r*2, r*2])
        self.menu_bg.blit(glow, (SCREEN_WIDTH//2-300, 80))
        title = font_title.render("盗墓笔记", True, COLORS["gold"])
        self.menu_bg.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 140))
        subtitle = font_sub.render("探墓解谜 · 生死一線", True, COLORS["parchment"])
        self.menu_bg.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 220))
        self.menu_buttons = []
        btn_texts = ["开始探险", "继续游戏", "游戏说明", "退出游戏"]
        for i, txt in enumerate(btn_texts):
            btn = pygame.Rect(SCREEN_WIDTH//2 - 160, 310 + i * 72, 320, 58)
            self.menu_buttons.append({"rect": btn, "text": txt, "hover": False})

    def start_level(self, level_id):
        self.current_level_id = level_id
        self.level = get_level(level_id)
        self.state = "playing"
        sx, sy = self.level.get("player_start", (100, 400))
        self.player = Player(sx, sy, "wu_xie")
        self.monsters = [Monster(m["x"], m["y"], m["type"]) for m in self.level.get("monsters", [])]
        self.items = [ItemEntity(it["x"], it["y"], it["id"], it["name"], it) for it in self.level.get("items", [])]
        self.traps = [Trap(pygame.Rect(t["x"], t["y"], t["w"], t["h"]), t["type"],
                           t["damage"], t.get("hint", "")) for t in self.level.get("traps", [])]
        self.walls = [Wall(w.x, w.y, w.w, w.h) for w in self.level.get("walls", [])]
        if self.level.get("puzzle"):
            self.puzzle_mgr = PuzzleManager(self.level)
        else:
            self.puzzle_mgr = None
        self.particles = ParticleSystem(max_count=400)
        self.screen_shake = 0
        bg_path = os.path.join(GAME_DIR, self.level["bg"])
        self.level_bg = pygame.image.load(bg_path).convert() if os.path.exists(bg_path) else None
        self.fade_alpha = 255
        self.fade_dir = -1
        self.show_level_intro()

    def show_level_intro(self):
        self.state = "level_intro"
        self.intro_timer = 180
        self.intro_text = self.level["name"]
        self.intro_sub = self.level.get("subtitle", "")

    def show_message(self, text, color=None, duration=180):
        self.msg_text = text
        self.msg_timer = duration
        self.msg_color = color or COLORS["gold"]

    def add_particles(self, x, y, count=10, color=None, size=3, speed=3, ptype="dust"):
        self.particles.emit(x, y, count, ptype=ptype, color=color, spread=int(size*3))

    def trigger_shake(self, intensity=8):
        self.screen_shake = intensity

    def update(self):
        dt = self.clock.tick(FPS) / 16.67
        if self.state == "menu":
            self._update_menu(dt)
        elif self.state == "level_intro":
            self.intro_timer -= 1
            if self.intro_timer <= 0:
                self.state = "playing"
        elif self.state == "playing":
            self._update_playing(dt)
        elif self.state == "paused":
            pass
        elif self.state in ("game_over", "victory"):
            pass
        if self.fade_dir != 0:
            self.fade_alpha += self.fade_dir * 6
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_dir = 0
            elif self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fade_dir = 0

    def _update_menu(self, dt):
        mx, my = pygame.mouse.get_pos()
        for btn in self.menu_buttons:
            btn["hover"] = btn["rect"].collidepoint(mx, my)
        self.dust_timer += dt / 60
        if random.random() < 0.08:
            self.add_particles(random.randint(0, SCREEN_WIDTH),
                               random.randint(0, SCREEN_HEIGHT),
                               count=3, ptype="dust", spread=3)
        self.particles.update()

    def _update_playing(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(keys, self.walls, dt)
        if keys[pygame.K_e]:
            self.player.searching = True
        else:
            self.player.searching = False
            self.player.search_timer = 0
        self.player.crouching = keys[pygame.K_LCTRL]
        for i in range(INVENTORY_SLOTS):
            if keys[pygame.K_1 + i]:
                self.player.select_slot(i)
        if self.puzzle_mgr and self.puzzle_mgr.state == "active":
            self.puzzle_mgr.update(dt)
        if keys[pygame.K_h]:
            self.hint_visible = not self.hint_visible
        for mon in self.monsters[:]:
            mon.update(self.player, self.walls, dt)
            if mon.health <= 0:
                self.monsters.remove(mon)
                self.add_particles(mon.x + mon.width//2, mon.y + mon.height//2,
                                   count=20, ptype="blood", spread=15)
                self.add_particles(mon.x + mon.width//2, mon.y + mon.height//2,
                                   count=10, ptype="dust", spread=10)
                self.trigger_shake(6)
        self.items = [it for it in self.items if not it.update(self.player, dt)]
        for trap in self.traps:
            trap.update(self.player, dt)
            if trap.triggered and trap.trap_type == "collapse":
                self.trigger_shake(12)
                self.add_particles(self.player.x + self.player.width//2,
                                   self.player.y + self.player.height//2,
                                   count=15, ptype="dust", spread=20)
        self.particles.update()
        self.dust_timer += dt / 60
        # 环境尘土粒子
        if random.random() < 0.03:
            self.add_particles(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT,
                               count=1, ptype="dust", spread=2)
        # 火把粒子（如果有）
        if self.player and self.player.light_on:
            if random.random() < 0.2:
                fx = self.player.x + self.player.width//2 + (14 if self.player.direction==1 else -14)
                fy = self.player.y + 30
                self.add_particles(fx, fy, count=1, ptype="torch", spread=3)
        # 门检测
        self._check_doors()
        if self.screen_shake > 0:
            self.screen_shake *= SCREEN_SHAKE_DECAY
            if self.screen_shake < 0.3:
                self.screen_shake = 0
        if self.msg_timer > 0:
            self.msg_timer -= 1
        if self.puzzle_mgr and self.puzzle_mgr.state == "solved":
            self.show_message(self.puzzle_mgr.message, COLORS["green"])
            self.puzzle_mgr.state = "cleared"
            self.trigger_shake(3)
        if self.player and self.player.health <= 0:
            self.state = "game_over"
            self.fade_dir = 1
        if self.puzzle_mgr and self.puzzle_mgr.puzzle.get("type") == "escape_timer":
            if self.puzzle_mgr.state == "failed":
                self.state = "game_over"
                self.fade_dir = 1

    def _check_doors(self):
        for door in self.level.get("doors", []):
            dr = door["rect"]
            pr = self.player.get_rect()
            if dr.colliderect(pr):
                if door.get("locked"):
                    key_item = door.get("key_item")
                    has_key = any(it["id"] == key_item for it in self.player.inventory)
                    if has_key:
                        door["locked"] = False
                        self.show_message(f"使用了「{key_item}」打开了门！", COLORS["green"])
                        self.add_particles(dr.centerx, dr.centery, count=20, ptype="magic",
                                          color=(180, 140, 60), spread=30)
                    else:
                        self.show_message("门被锁住了，需要钥匙", COLORS["red"])
                        self.player.x = max(0, self.player.x - 20)
                elif door.get("is_exit"):
                    self.state = "victory"
                    self.show_message("成功逃出墓穴！", COLORS["green"])
                    self.fade_dir = 1
                else:
                    self.start_level(door.get("to_level", self.current_level_id + 1))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        if self.state == "menu":
            self._handle_menu(event)
        elif self.state == "playing":
            self._handle_playing(event)
        elif self.state == "paused":
            self._handle_paused(event)
        elif self.state in ("game_over", "victory"):
            self._handle_end(event)

    def _handle_menu(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, btn in enumerate(self.menu_buttons):
                if btn["rect"].collidepoint(event.pos):
                    if i == 0: self.start_level(1)
                    elif i == 1: self.start_level(self.current_level_id)
                    elif i == 2: self._show_rules()
                    elif i == 3: self.running = False
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for btn in self.menu_buttons:
                btn["hover"] = btn["rect"].collidepoint(mx, my)

    def _handle_playing(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "paused"
            if event.key == pygame.K_f and self.player:
                self.player.light_on = not self.player.light_on
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.puzzle_mgr and self.puzzle_mgr.state == "active":
                self.puzzle_mgr.handle_event(event, (self.player.x, self.player.y))

    def _handle_paused(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.state = "playing"
            if event.key == pygame.K_r:
                self.start_level(self.current_level_id)

    def _handle_end(self, event):
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            if self.state == "game_over":
                self.start_level(self.current_level_id)
            else:
                self._init_menu()
                self.state = "menu"

    def _show_rules(self):
        self.state = "rules"

    def draw(self):
        if self.state == "menu":
            self._draw_menu()
        elif self.state in ("playing", "paused", "level_intro"):
            self._draw_game()
        elif self.state == "rules":
            self._draw_rules()
        elif self.state in ("game_over", "victory"):
            self._draw_end_screen()
        if self.fade_alpha > 0:
            f = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            f.fill(FADE_COLOR)
            f.set_alpha(self.fade_alpha)
            self.screen.blit(f, (0, 0))

    def _draw_menu(self):
        self.screen.blit(self.menu_bg, (0, 0))
        font_btn = pygame.font.SysFont("SimHei", 24)
        for btn in self.menu_buttons:
            r = btn["rect"]
            base_col = (25, 20, 14) if not btn["hover"] else (40, 32, 20)
            s = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
            s.fill((*base_col, 220) if len(base_col)==3 else (*base_col[:3],220))
            self.screen.blit(s, (r.x, r.y))
            bdr = COLORS["dark_gold"] if not btn["hover"] else COLORS["gold"]
            pygame.draw.rect(self.screen, bdr, r, 3, border_radius=12)
            txt = font_btn.render(btn["text"], True, COLORS["parchment"])
            self.screen.blit(txt, (r.x + r.width//2 - txt.get_width()//2, r.y + 16))
        self.particles.draw(self.screen)
        font_tip = pygame.font.SysFont("SimHei", 13)
        tip = font_tip.render("← → 移动 | SHIFT奔跑 | E搜索 | F灯光 | CTRL蹲下 | 1-8道具栏 | ESC暂停",
                               True, (80, 65, 40))
        self.screen.blit(tip, (SCREEN_WIDTH//2 - tip.get_width()//2, SCREEN_HEIGHT - 38))

    def _draw_game(self):
        # 背景
        if self.level_bg:
            self.screen.blit(self.level_bg, (0, 0))
        else:
            self.screen.fill(COLORS["dark"])
        # 震动
        sx = random.randint(-int(self.screen_shake), int(self.screen_shake)) if self.screen_shake > 0 else 0
        sy = random.randint(-int(self.screen_shake), int(self.screen_shake)) if self.screen_shake > 0 else 0
        cam_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # 墙壁
        for w in self.walls:
            pygame.draw.rect(cam_surf, (22, 18, 14), [w.x, w.y, w.w, w.h])
            pygame.draw.rect(cam_surf, (12, 10, 7), [w.x, w.y, w.w, w.h], 2)
        # 门
        for door in self.level.get("doors", []):
            dr = door["rect"]
            col = (30, 110, 30) if not door.get("locked") else (110, 30, 30)
            pygame.draw.rect(cam_surf, col, [dr.x, dr.y, dr.w, dr.h])
            pygame.draw.rect(cam_surf, (70, 55, 25), [dr.x, dr.y, dr.w, dr.h], 3)
            font_d = pygame.font.SysFont("SimHei", 14)
            txt = "出口" if door.get("is_exit") else ("✅" if not door.get("locked") else "🔒")
            t = font_d.render(txt, True, COLORS["parchment"])
            cam_surf.blit(t, (dr.x + dr.w//2 - t.get_width()//2, dr.y + dr.h//2 - 8))
        # 陷阱
        for trap in self.traps:
            trap.draw(cam_surf)
        # 物品
        for item in self.items:
            item.draw(cam_surf)
        # 怪物
        for mon in self.monsters:
            mon.draw(cam_surf, particles=self.particles)
        # 玩家
        if self.player:
            self.player.draw(cam_surf, particles=self.particles)
        # 粒子
        self.particles.draw(cam_surf)
        # 应用相机偏移
        self.screen.blit(cam_surf, (sx, sy))
        # 灯光层
        if self.player:
            self.light_layer.render(self.screen, self.player)
        # UI（不受震动影响）
        if self.player:
            self.player.draw_ui(self.screen)
        # 消息
        if self.msg_timer > 0:
            alpha = min(255, self.msg_timer * 3)
            font = pygame.font.SysFont("SimHei", 18)
            txt = font.render(self.msg_text, True, self.msg_color)
            x = SCREEN_WIDTH//2 - txt.get_width()//2
            y = SCREEN_HEIGHT - 150
            s = pygame.Surface((txt.get_width()+20, 36), pygame.SRCALPHA)
            s.fill((5, 4, 3, alpha))
            self.screen.blit(s, (x-10, y-5))
            txt.set_alpha(alpha)
            self.screen.blit(txt, (x, y))
        # 关卡信息
        if self.level:
            pygame.draw.rect(self.screen, (5,4,3,180), [10, 70, 270, 58], border_radius=8)
            font_n = pygame.font.SysFont("SimHei", 16)
            n = font_n.render(self.level["name"], True, COLORS["parchment"])
            self.screen.blit(n, (18, 75))
            font_s = pygame.font.SysFont("SimSun", 12)
            s2 = font_s.render(self.level.get("subtitle", ""), True, (150,130,100))
            self.screen.blit(s2, (18, 100))
            # 关卡进度
            lvl_num = self.level.get("id", 1)
            pg = font_s.render(f"[ {lvl_num} / 6 ]", True, (100,85,60))
            self.screen.blit(pg, (220, 100))
        # 谜题
        if self.puzzle_mgr:
            self.puzzle_mgr.draw(self.screen)
        # 准星
        mx, my = pygame.mouse.get_pos()
        cs = 4
        alpha_cs = 180
        pygame.draw.circle(self.screen, (200,180,120,alpha_cs), (mx,my), cs, 2)
        pygame.draw.line(self.screen, (200,180,120,alpha_cs), (mx-12,my), (mx-5,my), 2)
        pygame.draw.line(self.screen, (200,180,120,alpha_cs), (mx+5,my), (mx+12,my), 2)
        pygame.draw.line(self.screen, (200,180,120,alpha_cs), (mx,my-12), (mx,my-5), 2)
        pygame.draw.line(self.screen, (200,180,120,alpha_cs), (mx,my+5), (mx,my+12), 2)
        # 暂停遮罩
        if self.state == "paused":
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0,0,0,150))
            self.screen.blit(s, (0,0))
            font_p = pygame.font.SysFont("SimHei", 48, bold=True)
            t = font_p.render("已暂停", True, COLORS["gold"])
            self.screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, SCREEN_HEIGHT//2 - 60))
            font_p2 = pygame.font.SysFont("SimHei", 18)
            t2 = font_p2.render("按 ESC 或 P 继续  |  按 R 重新开始关卡", True, (150,130,100))
            self.screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, SCREEN_HEIGHT//2))
        # 关卡介绍
        if self.state == "level_intro":
            self._draw_level_intro()

    def _draw_level_intro(self):
        alpha = 255
        if self.intro_timer > 120:
            alpha = int(255 * (self.intro_timer - 120) / 60)
        elif self.intro_timer < 60:
            alpha = int(255 * self.intro_timer / 60)
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0,0,0,140))
        self.screen.blit(s, (0,0))
        font1 = pygame.font.SysFont("SimHei", 54, bold=True)
        font2 = pygame.font.SysFont("SimSun", 24)
        t1 = font1.render(self.level["name"], True, COLORS["gold"])
        t2 = font2.render(self.level.get("subtitle", ""), True, COLORS["parchment"])
        t1.set_alpha(alpha); t2.set_alpha(alpha)
        self.screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, SCREEN_HEIGHT//2 - 55))
        self.screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, SCREEN_HEIGHT//2 + 5))
        if self.intro_timer < 100:
            font3 = pygame.font.SysFont("SimHei", 15)
            hints = self.level.get("hints", [])
            for i, h in enumerate(hints[:2]):
                th = font3.render(h[:60], True, (150,130,90))
                th.set_alpha(min(255, (100 - self.intro_timer) * 5))
                self.screen.blit(th, (SCREEN_WIDTH//2 - th.get_width()//2,
                                      SCREEN_HEIGHT//2 + 55 + i * 26))

    def _draw_rules(self):
        self.screen.fill(COLORS["dark"])
        font_title = pygame.font.SysFont("SimHei", 36, bold=True)
        title = font_title.render("游戏说明", True, COLORS["gold"])
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 28))
        rules = [
            "【游戏背景】南派三叔《盗墓笔记》改编",
            "【类型】第三人称探险解谜 + 轻度恐怖",
            "",
            "【操作】",
            "  ← → / A D — 移动   |   W / ↑ — 跳跃",
            "  SHIFT      — 奔跑（耗体力）",
            "  CTRL       — 蹲下躲避",
            "  E          — 原地搜索（获取线索）",
            "  F          — 开关手电筒",
            "  1-8        — 切换道具栏",
            "  鼠标左键   — 谜题交互 / 点击",
            "  H          — 显示/隐藏提示",
            "  ESC        — 暂停",
            "",
            "【玩法】",
            "  · 探墓解谜 — 破解机关谜题推进剧情",
            "  · 躲避怪物 — 被粽子等发现会扣血",
            "  · 收集道具 — 钥匙是开门的必要条件",
            "  · 限时撤离 — 第六关需在倒计时内逃出",
            "",
            "【六关】",
            "  1.秦岭深山·墓门密码  2.幽暗甬道·机关地板",
            "  3.主墓室·七星续命灯  4.机关室·河图洛书",
            "  5.陪葬坑·明器鉴定    6.逃出生天·限时撤离",
        ]
        font_body = pygame.font.SysFont("SimHei", 17)
        for i, line in enumerate(rules):
            col = COLORS["gold"] if line.startswith("【") else COLORS["parchment"]
            txt = font_body.render(line, True, col)
            self.screen.blit(txt, (60, 82 + i * 24))
        font_tip = pygame.font.SysFont("SimHei", 16)
        tip = font_tip.render("按 ESC 或 点击返回主菜单", True, (100,85,60))
        self.screen.blit(tip, (SCREEN_WIDTH//2 - tip.get_width()//2, SCREEN_HEIGHT - 40))
        for ev in pygame.event.get():
            if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self._init_menu()
                self.state = "menu"

    def _draw_end_screen(self):
        self.screen.fill(COLORS["black"])
        if self.state == "game_over":
            # 血红背景渐变
            for y in range(SCREEN_HEIGHT):
                a = int(80 * (y / SCREEN_HEIGHT))
                pygame.draw.line(self.screen, (80,0,0), (0,y), (SCREEN_WIDTH,y))
            font = pygame.font.SysFont("SimHei", 64, bold=True)
            txt = font.render("你死了", True, COLORS["blood_red"])
            self.screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, SCREEN_HEIGHT//2 - 80))
            font2 = pygame.font.SysFont("SimHei", 22)
            sub = font2.render("墓室中的危险夺去了你的生命...", True, (150,120,100))
            self.screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, SCREEN_HEIGHT//2 - 20))
            font3 = pygame.font.SysFont("SimHei", 18)
            tip = font3.render("点击任意处重新开始", True, (100,80,60))
            self.screen.blit(tip, (SCREEN_WIDTH//2 - tip.get_width()//2, SCREEN_HEIGHT//2 + 50))
        elif self.state == "victory":
            for y in range(SCREEN_HEIGHT):
                a = int(40 * (1 - abs(y - SCREEN_HEIGHT//2) / (SCREEN_HEIGHT//2)))
                pygame.draw.line(self.screen, (30,25,10), (0,y), (SCREEN_WIDTH,y))
            font = pygame.font.SysFont("SimHei", 60, bold=True)
            txt = font.render("逃出生天！", True, COLORS["gold"])
            self.screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, SCREEN_HEIGHT//2 - 80))
            font2 = pygame.font.SysFont("SimHei", 22)
            sub = font2.render("活着真好，阳光洒在脸上的感觉真好。", True, COLORS["parchment"])
            self.screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, SCREEN_HEIGHT//2 - 20))
            font3 = pygame.font.SysFont("SimHei", 18)
            tip = font3.render("恭喜完成《盗墓笔记》探墓之旅！", True, (150,130,80))
            self.screen.blit(tip, (SCREEN_WIDTH//2 - tip.get_width()//2, SCREEN_HEIGHT//2 + 40))
            tip2 = font3.render("点击任意处返回主菜单", True, (100,85,60))
            self.screen.blit(tip2, (SCREEN_WIDTH//2 - tip2.get_width()//2, SCREEN_HEIGHT//2 + 80))
