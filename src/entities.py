# -*- coding: utf-8 -*-
"""游戏实体模块 - 集成动态动画系统"""
import os, math, random, pygame
from config import *

_resources = {}

def load_image(path, alpha=True):
    key = path
    if key in _resources:
        return _resources[key]
    full = os.path.join(GAME_DIR, path)
    if not os.path.exists(full):
        surf = pygame.Surface((64,64))
        surf.fill((60,50,40))
        return surf.convert_alpha() if alpha else surf.convert()
    try:
        img = pygame.image.load(full)
        return img.convert_alpha() if alpha else img.convert()
    except:
        surf = pygame.Surface((64,64))
        surf.fill((60,50,40))
        return surf.convert_alpha() if alpha else surf.convert()

def get_image(path):
    return load_image(path)

# ─── 粒子系统 ─────────────────────────────────────────────────────

class Particle:
    def __init__(self, x, y, vx, vy, color, life, size=3, gravity=0.1):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity
        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        self.alpha = int(255 * (self.life / self.max_life))
        sz = int(self.size * max(0.2, self.life / self.max_life))
        self._current_size = max(1, sz)
        return self.life <= 0

    def draw(self, surface, cx=0, cy=0):
        if self.alpha < 5:
            return
        s = pygame.Surface((self._current_size*2, self._current_size*2), pygame.SRCALPHA)
        col = (*self.color[:3], self.alpha) if len(self.color) == 4 else (*self.color, self.alpha)
        pygame.draw.circle(s, col, (self._current_size, self._current_size), self._current_size)
        surface.blit(s, (int(self.x - cx - self._current_size),
                        int(self.y - cy - self._current_size)))

    def rect(self):
        sz = getattr(self, '_current_size', self.size)
        return pygame.Rect(self.x - sz, self.y - sz, sz*2, sz*2)


class ParticleSystem:
    """全局粒子系统"""
    def __init__(self, max_count=300):
        self.particles = []
        self.max_count = max_count

    def emit(self, x, y, count=5, ptype="dust", color=None, spread=8):
        for _ in range(count):
            if len(self.particles) >= self.max_count:
                self.particles.pop(0)
            if ptype == "dust":
                col = color or random.choice([(100,80,60),(90,72,52),(110,90,70)])
                spd = random.uniform(0.3, 2.0)
                ang = random.uniform(-math.pi, 0)
                life = random.randint(20, 45)
                sz = random.uniform(2, 5)
            elif ptype == "blood":
                col = (140, 20, 20)
                spd = random.uniform(1, 3.5)
                ang = random.uniform(-math.pi*0.8, -math.pi*0.2)
                life = random.randint(30, 60)
                sz = random.uniform(2, 4)
            elif ptype == "torch":
                col = random.choice([(255,150,30),(255,200,60),(220,100,20)])
                spd = random.uniform(0.4, 1.8)
                ang = random.uniform(-math.pi*0.75, -math.pi*0.25)
                life = random.randint(25, 50)
                sz = random.uniform(2, 6)
            elif ptype == "magic":
                col = color or random.choice([(180,100,220),(100,180,255),(220,180,80)])
                spd = random.uniform(0.5, 2.5)
                ang = random.uniform(-math.pi*1.2, -math.pi*0.8)
                life = random.randint(30, 70)
                sz = random.uniform(2, 5)
            elif ptype == "bone":
                col = (180, 170, 150)
                spd = random.uniform(0.5, 2)
                ang = random.uniform(-math.pi, 0)
                life = random.randint(40, 80)
                sz = random.uniform(2, 4)
            else:
                col = (150, 130, 100)
                spd = 1; ang = -math.pi/2; life = 30; sz = 3

            self.particles.append(Particle(
                x + random.uniform(-spread, spread),
                y + random.uniform(-spread, spread),
                math.cos(ang)*spd, math.sin(ang)*spd,
                col, life, sz,
                gravity=0.08 if ptype not in ("torch","magic") else 0.05
            ))

    def update(self):
        self.particles = [p for p in self.particles if not p.update()]

    def draw(self, surface, cx=0, cy=0):
        for p in self.particles:
            p.draw(surface, cx, cy)

    def clear(self):
        self.particles.clear()

    def __len__(self):
        return len(self.particles)


# ─── 玩家 ────────────────────────────────────────────────────────

class Player:
    def __init__(self, x, y, char_type="wu_xie"):
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.run_speed = PLAYER_RUN_SPEED
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_HEALTH
        self.stamina = PLAYER_STAMINA
        self.max_stamina = PLAYER_STAMINA
        self.direction = 1
        self.stance = "idle"
        self.is_running = False
        self.inventory = []
        self.selected_slot = 0
        self.has_flashlight = True
        self.light_on = True
        self.flashlight_angle = 0
        self.crouching = False
        self.searching = False
        self.search_timer = 0
        self.search_progress = 0
        self.invulnerable = 0
        self.hurt_timer = 0
        self.char_type = char_type
        self.jump_vel = 0
        self.on_ground = True
        # 动画时间
        self.anim_time = 0.0
        self.anim_frame = 0
        # 尘土粒子
        self.step_particles = []
        self.step_timer = 0
        self.inventory = [
            {"id": "flashlight", "name": "手电筒", "count": 1},
            {"id": "compass", "name": "风水罗盘", "count": 1},
            {"id": "ancient_map", "name": "古籍残卷", "count": 1},
        ]

    def update(self, keys, walls, dt):
        # 体力
        if not self.is_running and self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + 0.3)
        # 动画时间
        self.anim_time += dt / 60.0
        # 搜索
        if self.searching:
            self.search_timer += 1
            self.search_progress = min(100, self.search_timer / 60 * 100)
            if self.search_timer >= 60:
                self.searching = False
                self.search_timer = 0
        # 受伤
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
        if self.invulnerable > 0:
            self.invulnerable -= 1
        # 移动
        speed = self.speed
        if keys[pygame.K_LSHIFT] and self.stamina > 0 and not self.crouching:
            speed = self.run_speed
            self.stamina = max(0, self.stamina - 0.5)
            self.is_running = True
        else:
            self.is_running = False
        if self.crouching:
            speed *= 0.4
        self.vx = 0
        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -speed; self.direction = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = speed; self.direction = 1
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = -10
            self.on_ground = False
        # 碰撞
        nx, ny = self.x + self.vx, self.y + self.vy
        hit_x = hit_y = False
        for w in walls:
            if self._cr(self.x, ny, w):
                hit_y = True
            if self._cr(nx, self.y, w):
                hit_x = True
        if hit_y:
            ny = self.y; self.vy = 0
            if self.vy >= 0:
                self.on_ground = True
        if hit_x:
            nx = self.x; self.vx = 0
        self.x, self.y = nx, ny
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.height, self.y))
        # 状态
        if abs(self.vx) > 0:
            self.stance = "walk"
        else:
            self.stance = "idle"
        if self.crouching:
            self.stance = "crouch"
        if self.searching:
            self.stance = "search"
        # 尘土粒子
        self.step_timer += 1
        if (self.stance == "walk" or self.is_running) and self.step_timer >= (6 if self.is_running else 12):
            self.step_timer = 0
            self.step_particles.append({
                "x": self.x + self.width//2 + random.uniform(-5,5),
                "y": self.y + self.height,
                "life": random.randint(20, 35),
                "max_life": 35,
                "size": random.uniform(2,4),
            })
        self.step_particles = [p for p in self.step_particles if p["life"] > 0]
        for p in self.step_particles:
            p["life"] -= 1
            p["y"] += 0.2

    def _cr(self, x, y, w):
        return (x < w.x + w.w and x + self.width > w.x and
                y < w.y + w.h and y + self.height > w.y)

    def take_damage(self, amount):
        if self.invulnerable > 0:
            return
        self.health -= amount
        self.hurt_timer = 20
        self.invulnerable = 40
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def draw(self, surface, camera_x=0, camera_y=0, particles=None):
        from animator import draw_character
        sx = self.x - camera_x
        sy = self.y - camera_y
        # 受伤闪烁
        if self.hurt_timer > 0 and self.hurt_timer % 4 < 2:
            return
        # 绘制尘土步迹
        for p in self.step_particles:
            alpha = int(120 * (p["life"] / p["max_life"]))
            sz = int(p["size"] * (p["life"] / p["max_life"]))
            if sz < 1: sz = 1
            s = pygame.Surface((sz*2, sz*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (90,72,55, alpha), (sz, sz), sz)
            surface.blit(s, (int(p["x"] - sx - sz), int(p["y"] - sy - sz)))
        # 动态角色绘制
        char_surf, foot_pos = draw_character(
            surface, sx, sy,
            self.char_type, self.stance, self.direction,
            self.anim_time, self.is_running,
            self.crouching, self.searching,
            (self.hurt_timer > 0), self.hurt_timer,
            self.light_on, self.flashlight_angle
        )
        # 绘制尘土粒子（脚部）
        if particles is not None and (self.stance == "walk" or self.is_running):
            fx, fy = sx + self.width//2, sy + self.height
            if self.step_timer < 3:  # 刚迈步时
                particles.emit(fx, fy, count=2, ptype="dust", spread=6)

    def draw_ui(self, surface):
        font = pygame.font.SysFont("SimHei", 13, bold=True)
        # 血条
        pygame.draw.rect(surface, (30,20,20), [HEALTH_BAR_X, HEALTH_BAR_Y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT])
        w = int((self.health / self.max_health) * (HEALTH_BAR_WIDTH - 4))
        pygame.draw.rect(surface, (180,30,30), [HEALTH_BAR_X+2, HEALTH_BAR_Y+2, w, HEALTH_BAR_HEIGHT-4])
        txt = font.render(f"♥ {self.health}/{self.max_health}", True, (255,220,200))
        surface.blit(txt, (HEALTH_BAR_X+4, HEALTH_BAR_Y+2))
        # 体力
        pygame.draw.rect(surface, (20,20,40), [HEALTH_BAR_X, STAMINA_BAR_Y, HEALTH_BAR_WIDTH, 10])
        sw = int((self.stamina / self.max_stamina) * (HEALTH_BAR_WIDTH - 4))
        pygame.draw.rect(surface, (80,160,255), [HEALTH_BAR_X+2, STAMINA_BAR_Y+2, sw, 6])
        # 搜索进度
        if self.searching:
            bar_w = 200; bar_x = SCREEN_WIDTH//2 - bar_w//2; bar_y = SCREEN_HEIGHT//2 - 30
            pygame.draw.rect(surface, (20,18,15), [bar_x, bar_y, bar_w, 14], border_radius=5)
            pw = int((self.search_progress/100)*(bar_w-4))
            pygame.draw.rect(surface, (200,170,60), [bar_x+2, bar_y+2, pw, 10], border_radius=4)
            font2 = pygame.font.SysFont("SimHei", 12)
            txt2 = font2.render("搜索中...", True, (220,190,100))
            surface.blit(txt2, (bar_x + bar_w//2 - 30, bar_y - 18))
        # 道具栏
        self._draw_inventory(surface)
        # 手电筒指示
        if self.has_flashlight:
            col = (255,220,100) if self.light_on else (60,55,60)
            icon_s = pygame.Surface((10,10), pygame.SRCALPHA)
            pygame.draw.circle(icon_s, col, (5,5), 5)
            surface.blit(icon_s, (HEALTH_BAR_X, HEALTH_BAR_Y - 14))
            lbl = pygame.font.SysFont("SimHei", 10).render("手电筒", True, (120,110,90))
            surface.blit(lbl, (HEALTH_BAR_X+14, HEALTH_BAR_Y-13))

    def _draw_inventory(self, surface):
        slot_w = INVENTORY_SLOT_SIZE
        total_w = INVENTORY_SLOTS * (slot_w + INVENTORY_PADDING) + INVENTORY_PADDING
        start_x = SCREEN_WIDTH//2 - total_w//2 + INVENTORY_PADDING
        font_s = pygame.font.SysFont("SimHei", 10)
        for i in range(INVENTORY_SLOTS):
            x = start_x + i * (slot_w + INVENTORY_PADDING)
            fname = f"slot_{i}{'_sel' if i==self.selected_slot else ''}.png"
            img = load_image(f"assets/images/ui/{fname}.png")
            surface.blit(img, (x, INVENTORY_BAR_Y))
            if i < len(self.inventory):
                item = self.inventory[i]
                item_img = load_image(f"assets/images/items/{item['id']}_large.png")
                surface.blit(item_img, (x+1, INVENTORY_BAR_Y+1))
                if item.get("count", 1) > 1:
                    txt = font_s.render(str(item["count"]), True, (255,220,100))
                    surface.blit(txt, (x + slot_w - 14, INVENTORY_BAR_Y + slot_w - 14))

    def add_item(self, item):
        for inv in self.inventory:
            if inv["id"] == item["id"]:
                inv["count"] += item.get("count", 1)
                return True
        if len(self.inventory) < INVENTORY_SLOTS:
            self.inventory.append(item.copy())
            return True
        return False

    def select_slot(self, idx):
        if 0 <= idx < INVENTORY_SLOTS:
            self.selected_slot = idx

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


# ─── 怪物 ────────────────────────────────────────────────────────

class Monster:
    def __init__(self, x, y, mon_type="zongzi"):
        self.x, self.y = x, y
        self.width = 44
        self.height = 76
        self.vx, self.vy = 0, 0
        self.health = MONSTER_HEALTH
        self.max_health = MONSTER_HEALTH
        self.speed = MONSTER_WANDER_SPEED
        self.chase_speed = MONSTER_CHASE_SPEED
        self.detect_range = MONSTER_DETECT_RANGE
        self.attack_range = MONSTER_ATTACK_RANGE
        self.damage = MONSTER_DAMAGE
        self.state = "idle"
        self.direction = 1
        self.anim_time = 0.0
        self.anim_frame = 0
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.hurt_timer = 0
        self.wander_timer = 0
        self.wander_dir = random.choice([-1, 1])
        self.mon_type = mon_type

    def update(self, player, walls, dt):
        self.anim_time += dt / 60.0
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < self.detect_range:
            self.state = "chase"
            self.direction = 1 if dx > 0 else -1
            if dist > 0:
                self.x += (dx / dist) * self.chase_speed
        else:
            self.state = "idle" if random.random() > MONSTER_IDLE_CHANCE else "wander"
            if self.state == "wander":
                self.wander_timer += 1
                if self.wander_timer > 120:
                    self.wander_timer = 0
                    self.wander_dir = random.choice([-1, 1])
                self.x += self.wander_dir * MONSTER_WANDER_SPEED * 0.5
                self.direction = self.wander_dir
        # 边界
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.height, self.y))
        # 攻击
        if dist < self.attack_range and self.attack_cooldown == 0:
            self.state = "attack"
            player.take_damage(self.damage)
            self.attack_cooldown = 60

    def take_damage(self, amount):
        self.health -= amount
        self.hurt_timer = 15
        return self.health <= 0

    def draw(self, surface, camera_x=0, camera_y=0, particles=None):
        from animator import draw_monster
        sx = self.x - camera_x
        sy = self.y - camera_y
        if self.hurt_timer > 0 and self.hurt_timer % 3 < 2:
            return
        # 动态怪物绘制
        action = "attack" if self.state == "attack" else ("move" if self.state == "chase" else "idle")
        mon_surf = draw_monster(
            surface, sx, sy,
            self.mon_type, action, self.anim_time,
            self.direction, self.health / self.max_health
        )
        surface.blit(mon_surf, (sx - 40, sy - 20))
        # 怪物粒子（幽魂和墓蛛有特殊粒子）
        if particles is not None and self.state in ("move", "chase"):
            if self.mon_type in ("youhun", "jinipo", "muzhu"):
                fx = sx + self.width//2
                fy = sy + self.height//2
                if random.random() < 0.15:
                    particles.emit(fx, fy, count=1, ptype="magic",
                                   color=(100,80,150) if self.mon_type=="youhun" else (50,30,80))

    def draw_health(self, surface, cx=0, cy=0):
        if self.health < self.max_health:
            sx = self.x - cx + self.width//2 - 25
            sy = self.y - cy - 15
            pygame.draw.rect(surface, (40,10,10), [sx, sy, 50, 6])
            pw = int((self.health/self.max_health)*50)
            pygame.draw.rect(surface, (180,40,40), [sx, sy, pw, 6])


# ─── 物品实体 ────────────────────────────────────────────────────

class ItemEntity:
    def __init__(self, x, y, item_id, item_name, item_data=None):
        self.x = x
        self.y = y
        self.width = ITEM_WIDTH
        self.height = ITEM_HEIGHT
        self.item_id = item_id
        self.item_name = item_name
        self.item_data = item_data or {}
        self.bob_timer = random.uniform(0, math.pi * 2)
        self.collected = False
        self.collect_timer = 0
        self.glow_timer = random.uniform(0, math.pi * 2)
        self.image = load_image(f"assets/images/items/{item_id}.png")

    def update(self, player, dt):
        self.bob_timer += 0.06
        self.glow_timer += 0.05
        if self.collected:
            self.collect_timer += 1
            return self.collect_timer > 20
        pr = player.get_rect()
        ir = pygame.Rect(self.x, self.y + int(math.sin(self.bob_timer)*ITEM_BOB_AMPLITUDE),
                         self.width, self.height)
        if pr.colliderect(ir):
            if player.add_item({"id": self.item_id, "name": self.item_name,
                                "count": self.item_data.get("count", 1)}):
                self.collected = True
        return False

    def draw(self, surface, camera_x=0, camera_y=0):
        if self.collected:
            return
        sx = self.x - camera_x
        sy = self.y - camera_y + int(math.sin(self.bob_timer)*ITEM_BOB_AMPLITUDE)
        # 发光效果
        glow_intensity = (math.sin(self.glow_timer) * 0.3 + 0.7)
        glow_radius = int(20 * glow_intensity)
        s = pygame.Surface((self.width + glow_radius*2, self.height + glow_radius*2), pygame.SRCALPHA)
        for r in range(glow_radius, 0, -3):
            alpha = int(40 * glow_intensity * (r/glow_radius))
            pygame.draw.circle(s, (200,170,80, alpha), (self.width//2+glow_radius, self.height//2+glow_radius), r)
        surface.blit(s, (sx - glow_radius, sy - glow_radius))
        surface.blit(self.image, (sx, sy))
        # 名字
        font = pygame.font.SysFont("SimHei", 10)
        txt = font.render(self.item_name, True, (220,190,100))
        surface.blit(txt, (sx - 10, sy - 16))


# ─── 陷阱 ────────────────────────────────────────────────────────

class Trap:
    def __init__(self, rect, trap_type, damage=20, hint=""):
        self.rect = rect
        self.trap_type = trap_type
        self.damage = damage
        self.hint = hint
        self.triggered = False
        self.timer = 0
        self.active = True
        self.anim_time = 0.0

    def update(self, player, dt):
        self.anim_time += dt / 60.0
        if not self.active:
            return
        if self.rect.colliderect(player.get_rect()):
            if not self.triggered:
                self.triggered = True
                player.take_damage(self.damage)
                self.timer = 0
        if self.triggered:
            self.timer += 1
            if self.timer > 180:
                self.triggered = False

    def draw(self, surface, camera_x=0, camera_y=0):
        if not self.active:
            return
        rx = self.rect.x - camera_x
        ry = self.rect.y - camera_y
        pulse = math.sin(self.anim_time * 3) * 20
        if self.triggered:
            col = (200, 50, 50, 80)
        else:
            col = (100 + int(pulse), 80, 40, 40)
        s = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        s.fill(col)
        surface.blit(s, (rx, ry))
        if self.triggered and self.timer < 30:
            font = pygame.font.SysFont("SimHei", 12)
            txt = font.render(self.hint, True, (255, 80, 80))
            surface.blit(txt, (rx, ry - 20))


# ─── 灯光层 ──────────────────────────────────────────────────────

class LightLayer:
    def __init__(self):
        self.lights = []

    def add_light(self, x, y, radius, color=(255,200,100), intensity=1.0):
        self.lights.append({"x": x, "y": y, "radius": radius, "color": color, "intensity": intensity})

    def render(self, surface, player=None):
        """渲染全局暗色遮罩 + 灯光"""
        dark = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 200))
        # 玩家手电筒光
        if player and player.light_on and player.has_flashlight:
            cx = player.x + player.width//2 + (14 if player.direction==1 else -14)
            cy = player.y + 30
            # 光锥
            cone_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            base_angle = 0 if player.direction == 1 else 180
            for r in range(int(FLASHLIGHT_RANGE), 0, -8):
                alpha = int(120 * (r / FLASHLIGHT_RANGE))
                spread = int(r * math.tan(math.radians(FLASHLIGHT_ANGLE//2)))
                pts = [(cx, cy)]
                steps = 16
                for i in range(steps + 1):
                    ang = math.radians(-90 + base_angle - FLASHLIGHT_ANGLE//2 +
                                      (FLASHLIGHT_ANGLE * i / steps))
                    pts.append((cx + math.cos(ang)*r, cy + math.sin(ang)*r))
                pygame.draw.polygon(cone_surf, (*COLORS["torch_light"], alpha), pts)
            dark.blit(cone_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        # 其他光源
        for light in self.lights:
            lx = light["x"]
            ly = light["y"]
            r = light["radius"]
            col = light["color"]
            intensity = light["intensity"]
            for i in range(r, 0, -6):
                alpha = int(120 * intensity * (i / r))
                c = (*col[:3], alpha)
                cir = pygame.Surface((i*2+2, i*2+2), pygame.SRCALPHA)
                pygame.draw.circle(cir, c, (i+1, i+1), i)
                dark.blit(cir, (int(lx)-i-1, int(ly)-i-1), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.lights.clear()
