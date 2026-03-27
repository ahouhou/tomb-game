# -*- coding: utf-8 -*-
"""
高级动态角色渲染系统
- 60fps 流畅动画插值
- 呼吸/Idle 微动
- 行走/奔跑周期
- 尘土粒子
- 动态光源光晕
- 阴影
"""
import os, math, random, pygame
from config import *

# ─────────────────────────────────────────────
# 角色美术资源（动态绘制，替代静态图片）
# ─────────────────────────────────────────────

def _lerp(a, b, t):
    """线性插值"""
    return a + (b - a) * max(0, min(1, t))

def _lerp_color(c1, c2, t):
    return tuple(int(_lerp(a, b, t)) for a, b in zip(c1, c2))

def _blend(a, b, t):
    """cosine 插值（更平滑）"""
    import math
    t2 = (1 - math.cos(t * math.pi)) / 2
    if isinstance(a, (list, tuple)) and len(a) >= 3:
        return tuple(int(_lerp(ca, cb, t2)) for ca, cb in zip(a, b))
    return int(_lerp(a, b, t2))

def _draw_glow(surf, pos, radius, color, intensity=1.0):
    """绘制发光层"""
    cx, cy = pos
    for i in range(radius, 0, -3):
        alpha = int(80 * intensity * (i / radius))
        col = (*color[:3], max(0, min(255, alpha)))
        s = pygame.Surface((i*2+2, i*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, col, (i+1, i+1), i)
        surf.blit(s, (int(cx)-i-1, int(cy)-i-1), special_flags=pygame.BLEND_RGBA_ADD)

def _draw_outline(surf, rect_list, color, width=2):
    """绘制轮廓线"""
    for rx, ry, rw, rh in rect_list:
        pygame.draw.rect(surf, color, [rx, ry, rw, rh], width)


# ─── 动态角色绘制 ───────────────────────────────────────────────

def draw_character(surf, x, y, char_type, stance, direction,
                   anim_time, is_running=False, is_crouching=False,
                   is_searching=False, is_hurt=False, hurt_timer=0,
                   light_on=True, flashlight_angle=0, dust_particles=None):
    """
    绘制完整动态角色（吴邪/胖子/张起灵）
    anim_time: 动画累计时间（秒）
    返回 (char_surf, foot_rect) 用于粒子生成
    """
    flip = (direction == -1)
    t = anim_time

    # ── 角色颜色配置 ────────────────────────────────────────────
    configs = {
        "wu_xie": {
            "skin":  (180, 150, 120),
            "body":  (55,  90,  135),
            "pants": (40,  55,  80),
            "coat":  (70,  110, 155),
            "hair":  (30,  20,  15),
            "boot":  (50,  40,  30),
            "bag":   (90,  65,  35),
            "flashlight": (200, 175, 90),
        },
        "pang_ci": {
            "skin":  (190, 140, 110),
            "body":  (135, 80,  50),
            "pants": (80,  50,  30),
            "coat":  (155, 100, 60),
            "hair":  (20,  15,  10),
            "boot":  (60,  45,  30),
            "bag":   (100, 75,  45),
            "flashlight": (210, 180, 100),
        },
        "zhang_qi_le": {
            "skin":  (170, 140, 115),
            "body":  (45,  55,  65),
            "pants": (30,  35,  45),
            "coat":  (55,  70,  85),
            "hair":  (15,  10,  10),
            "boot":  (40,  30,  25),
            "bag":   (70,  50,  30),
            "flashlight": (195, 170, 85),
        },
    }
    c = configs.get(char_type, configs["wu_xie"])

    # ── 动画周期参数 ────────────────────────────────────────────
    if is_crouching:
        cycle = 0
        bob_y = 0
        leg_swing = 0
        arm_swing = 0
        body_tilt = 0
    elif stance == "walk":
        cycle = t * 8  # 8秒/完整周期
        bob_y = abs(math.sin(cycle * math.pi * 2)) * 4  # 垂直颠簸
        leg_swing = math.sin(cycle * math.pi * 2) * 20  # 腿部摆幅
        arm_swing = -math.sin(cycle * math.pi * 2) * 25  # 手臂摆幅
        body_tilt = math.sin(cycle * math.pi * 2) * 3  # 身体微倾
    elif stance == "search":
        cycle = t * 2
        bob_y = math.sin(cycle * math.pi * 2) * 1.5  # 微微摇摆
        leg_swing = 0
        arm_swing = 0
        body_tilt = math.sin(cycle * math.pi * 2) * 5  # 搜索时左右看
    else:  # idle
        cycle = t * 1.5
        bob_y = math.sin(cycle * math.pi * 2) * 1.5  # 呼吸起伏
        leg_swing = 0
        arm_swing = math.sin(cycle * math.pi * 2) * 2  # 手臂微微摆动
        body_tilt = 0

    if is_running and stance == "walk":
        cycle = t * 14
        bob_y = abs(math.sin(cycle * math.pi * 2)) * 7
        leg_swing = math.sin(cycle * math.pi * 2) * 28
        arm_swing = -math.sin(cycle * math.pi * 2) * 35
        body_tilt = math.sin(cycle * math.pi * 2) * 6

    # 受伤闪烁
    if is_hurt and hurt_timer > 0 and hurt_timer % 4 < 2:
        # 绘制半透明受伤状态
        pass

    # ── 创建角色图层 ────────────────────────────────────────────
    w, h = 64, 96
    if is_crouching:
        h = 70
    char_surf = pygame.Surface((w + 60, h + 40), pygame.SRCALPHA)
    ox, oy = 30, h + 20  # 偏移到脚底中心

    # ── 脚底阴影 ────────────────────────────────────────────────
    shadow_w = int(30 + bob_y * 0.3)
    shadow_alpha = int(80 - bob_y * 2)
    s_shadow = pygame.Surface((shadow_w * 2, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(s_shadow, (0, 0, 0, max(30, shadow_alpha)), [0, 0, shadow_w*2, 14])
    char_surf.blit(s_shadow, (ox - shadow_w, oy + 8))

    # ── 背包 ──────────────────────────────────────────────────
    bx = ox - 14 if not flip else ox + 10
    _rrect(char_surf, [bx-4, oy-72+bob_y, 8, 18], c["bag"], radius=3)
    # 背包带
    pygame.draw.line(char_surf, c["bag"], (bx, oy-72+bob_y), (bx-4, oy-50+bob_y), 2)

    # ── 腿部 ──────────────────────────────────────────────────
    leg_h = 26 if not is_crouching else 12
    leg_y0 = oy - 26 + bob_y if not is_crouching else oy - 10
    # 左腿
    l_lerp = leg_swing * 0.5
    _rrect(char_surf, [
        ox - 10 + l_lerp//3, leg_y0,
        10, leg_h
    ], c["pants"], radius=3)
    # 右腿
    r_lerp = -leg_swing * 0.5
    _rrect(char_surf, [
        ox + l_lerp//3, leg_y0,
        10, leg_h
    ], c["pants"], radius=3)
    # 靴子
    boot_y = leg_y0 + leg_h - 6
    _rrect(char_surf, [ox-12+l_lerp//3, boot_y, 12, 8], c["boot"], radius=2)
    _rrect(char_surf, [ox+r_lerp//3, boot_y, 12, 8], c["boot"], radius=2)

    # ── 身体 ──────────────────────────────────────────────────
    body_h = 36 if not is_crouching else 24
    body_y0 = leg_y0 - body_h
    body_tilt_rad = math.radians(body_tilt)
    _rrect(char_surf, [
        ox - 14 + int(math.sin(body_tilt_rad) * 8),
        body_y0 + bob_y,
        28, body_h
    ], c["body"], radius=4)
    # 外套细节
    _rrect(char_surf, [
        ox - 13 + int(math.sin(body_tilt_rad) * 8),
        body_y0 + bob_y + 2,
        26, body_h - 4
    ], c["coat"], radius=3)

    # ── 手臂 ──────────────────────────────────────────────────
    arm_h = 28 if not is_crouching else 18
    arm_y0 = body_y0 + 6 + bob_y
    # 左臂
    al_x = ox - 18 + arm_swing//4 + int(math.sin(body_tilt_rad)*5)
    _rrect(char_surf, [al_x, arm_y0, 8, arm_h], c["coat"], radius=3)
    _rrect(char_surf, [al_x+1, arm_y0+arm_h-6, 6, 8], c["skin"], radius=2)
    # 右臂（持手电筒）
    ar_x = ox + 10 - arm_swing//4 + int(math.sin(body_tilt_rad)*5)
    _rrect(char_surf, [ar_x, arm_y0, 8, arm_h], c["coat"], radius=3)
    _rrect(char_surf, [ar_x+1, arm_y0+arm_h-6, 6, 8], c["skin"], radius=2)

    # ── 手电筒 ────────────────────────────────────────────────
    fl_x = ar_x + 8
    fl_y = arm_y0 + arm_h - 8
    _rrect(char_surf, [fl_x, fl_y, 12, 5], c["flashlight"], radius=2)
    # 镜片
    lens_s = pygame.Surface((8, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(lens_s, (220, 200, 100, 230), [0, 0, 8, 6])
    char_surf.blit(lens_s, (fl_x+1, fl_y-1))
    # 灯泡发光
    if light_on:
        _draw_glow(char_surf, (fl_x+6, fl_y+2), 14, (255, 210, 80), 0.9)
        # 光束锥（很淡，用于角色自身）
        _draw_cone(char_surf, (fl_x+12, fl_y+2),
                   flashlight_angle if direction == 1 else 180 - flashlight_angle,
                   80, (255, 200, 80, 25))

    # ── 头部 ──────────────────────────────────────────────────
    head_y = body_y0 - 28 + bob_y
    head_r = 13
    # 头发
    hair_s = pygame.Surface((head_r*2+4, head_r+8), pygame.SRCALPHA)
    pygame.draw.ellipse(hair_s, c["hair"], [0, 4, head_r*2+4, head_r+4])
    char_surf.blit(hair_s, (ox-head_r-2, head_y-2))
    # 脸
    _circle(char_surf, (ox, head_y + head_r), head_r, c["skin"])
    # 眼睛
    eye_y = head_y + head_r - 4
    eye_col = (40, 30, 20)
    _circle(char_surf, (ox - 5, eye_y), 3, eye_col)
    _circle(char_surf, (ox + 5, eye_y), 3, eye_col)
    # 眼白
    _circle(char_surf, (ox - 5, eye_y), 2, (240, 235, 225))
    _circle(char_surf, (ox + 5, eye_y), 2, (240, 235, 225))
    # 嘴巴
    if stance == "search" or is_crouching:
        # 紧张表情
        pygame.draw.line(char_surf, (80, 50, 40),
                         (ox - 4, head_y + head_r + 4),
                         (ox + 4, head_y + head_r + 4), 2)
    # 搜索视角（头部偏转）
    if stance == "search":
        look_offset = int(math.sin(t * 3) * 5)
        # 额外画一只看向侧面的眼睛
        eye_x2 = ox + 10 + look_offset
        _circle(char_surf, (eye_x2, eye_y - 2), 3, eye_col)
        _circle(char_surf, (eye_x2, eye_y - 2), 2, (240, 235, 225))

    # ── 受伤效果 ──────────────────────────────────────────────
    if is_hurt and hurt_timer > 0:
        hurt_flash = (255, 50, 50, 100) if hurt_timer % 4 < 2 else (0, 0, 0, 0)
        if hurt_flash[3] > 0:
            hs = pygame.Surface((w+40, h+20), pygame.SRCALPHA)
            hs.fill(hurt_flash)
            char_surf.blit(hs, (0, 0))

    # ── 绘制尘土粒子 ─────────────────────────────────────────
    if dust_particles is not None and (stance == "walk" or stance == "search"):
        foot_x = ox
        foot_y = oy + 8
        if abs(leg_swing) > 5:  # 迈步时产生尘土
            dust_particles.append({
                "x": foot_x + random.uniform(-8, 8),
                "y": foot_y,
                "vx": random.uniform(-0.5, 0.5) - direction * 0.3,
                "vy": random.uniform(-1.5, -0.5),
                "life": random.randint(15, 30),
                "max_life": 30,
                "size": random.uniform(2, 5),
            })

    # ── 翻转 ──────────────────────────────────────────────────
    if flip:
        char_surf = pygame.transform.flip(char_surf, True, False)

    return char_surf, (x + ox - 15, y + oy + 8, 30, 6)


# ─── 动态怪物绘制 ───────────────────────────────────────────────

MONSTER_CONFIGS = {
    "jinipo": {
        "body":  (20, 15, 30),
        "accent":(40, 20, 60),
        "eyes":  (200, 150, 255),
        "hair":  (25, 10, 40),
        "glow":  (150, 100, 200),
    },
    "zongzi": {
        "body":  (60, 55, 50),
        "accent":(80, 75, 70),
        "eyes":  (255, 60, 20),
        "hair":  (40, 35, 30),
        "glow":  (200, 50, 10),
    },
    "muzhu": {
        "body":  (30, 25, 20),
        "accent":(50, 40, 30),
        "eyes":  (255, 200, 50),
        "hair":  (40, 30, 20),
        "glow":  (220, 160, 30),
    },
    "youhun": {
        "body":  (40, 50, 60),
        "accent":(60, 80, 100),
        "eyes":  (150, 200, 255),
        "hair":  (30, 50, 70),
        "glow":  (100, 160, 220),
    },
}

def draw_monster(surf, x, y, mon_type, action, anim_time, direction, health_ratio=1.0):
    """
    绘制动态怪物
    action: idle / move / attack
    """
    flip = (direction == -1)
    t = anim_time
    cfg = MONSTER_CONFIGS.get(mon_type, MONSTER_CONFIGS["zongzi"])
    b = cfg["body"]
    a = cfg["accent"]
    e = cfg["eyes"]
    g = cfg["glow"]

    w, h = 80, 80
    mon_surf = pygame.Surface((w + 30, h + 20), pygame.SRCALPHA)
    ox, oy = w//2 + 10, h//2 - 5

    # 动画参数
    if action == "move":
        cycle = t * 10
        bob = abs(math.sin(cycle * math.pi * 2)) * 5
        sway = math.sin(cycle * math.pi * 2) * 4
        atk_ext = 0
    elif action == "attack":
        cycle = t * 6
        bob = 3
        sway = math.sin(cycle * math.pi * 2) * 8
        atk_ext = abs(math.sin(cycle * math.pi)) * 15
    else:  # idle
        cycle = t * 2
        bob = math.sin(cycle * math.pi * 2) * 2
        sway = math.sin(cycle * math.pi * 2) * 2
        atk_ext = 0

    if mon_type == "jinipo":
        _draw_jinipo(mon_surf, ox, oy + bob, cfg, sway, atk_ext, action)
    elif mon_type == "zongzi":
        _draw_zongzi(mon_surf, ox, oy + bob, cfg, sway, atk_ext, action, t)
    elif mon_type == "muzhu":
        _draw_muzhu(mon_surf, ox, oy + bob, cfg, sway, action, t)
    elif mon_type == "youhun":
        _draw_youhun(mon_surf, ox, oy + bob, cfg, sway, action, t)

    # ── 地面阴影 ──────────────────────────────────────────────
    shadow_s = pygame.Surface((60, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_s, (0, 0, 0, 60), [0, 0, 60, 12])
    mon_surf.blit(shadow_s, (ox - 30, oy + 35 + bob))

    # ── 受伤效果 ──────────────────────────────────────────────
    # 怪物发光
    _draw_glow(mon_surf, (ox, oy - 10 + bob), 30, g, 0.4)

    if flip:
        mon_surf = pygame.transform.flip(mon_surf, True, False)

    # ── 血条 ──────────────────────────────────────────────────
    if health_ratio < 1.0:
        bw = 50
        bx = x + w//2 - bw//2
        by = y - 15
        pygame.draw.rect(surf, (40, 10, 10), [bx, by, bw, 6])
        pw = int(health_ratio * bw)
        pygame.draw.rect(surf, (180, 40, 40), [bx, by, pw, 6])

    return mon_surf


def _draw_jinipo(surf, ox, oy, cfg, sway, atk_ext, action):
    b, a, e, g = cfg["body"], cfg["accent"], cfg["eyes"], cfg["glow"]
    # 长发飘动
    for i in range(7):
        wave = math.sin(i * 1.5 + sway * 0.3) * 6
        alpha = int(200 - i * 15)
        _line(surf, (ox - 18 + i * 6 + wave, oy - 30),
              (ox - 22 + i * 6 + wave * 1.5, oy + 35),
              (*a[:3], max(50, alpha)), 4)
    # 头
    _circle(surf, (ox, oy - 22), 16, b)
    # 眼睛（发光）
    _draw_glow(surf, (ox - 7, oy - 24), 8, e, 0.8)
    _draw_glow(surf, (ox + 7, oy - 24), 8, e, 0.8)
    _circle(surf, (ox - 7, oy - 24), 4, e)
    _circle(surf, (ox + 7, oy - 24), 4, e)
    # 身体
    _rect(surf, [ox - 14, oy - 8, 28, 42], (*b[:3], 160), radius=6)
    # 手臂（攻击伸展）
    arm_len = 22 + atk_ext
    _line(surf, (ox - 14, oy), (ox - 14 - arm_len, oy + 5), (*a[:3], 180), 6)
    _line(surf, (ox + 14, oy), (ox + 14 + arm_len, oy + 5), (*a[:3], 180), 6)
    if atk_ext > 5:
        _draw_glow(surf, (ox - 14 - arm_len, oy + 5), 10, g, 0.6)
        _draw_glow(surf, (ox + 14 + arm_len, oy + 5), 10, g, 0.6)


def _draw_zongzi(surf, ox, oy, cfg, sway, atk_ext, action, t):
    b, a, e, g = cfg["body"], cfg["accent"], cfg["eyes"], cfg["glow"]
    # 身体僵硬直立
    _rect(surf, [ox - 20, oy - 35, 40, 50], b, radius=4)
    # 铠甲纹路
    for i in range(5):
        yy = oy - 30 + i * 8
        _line(surf, (ox - 18, yy), (ox + 18, yy), (*a[:3], 150), 2)
    # 手臂僵硬伸出
    arm_x = 20 + atk_ext * 0.5
    _rect(surf, [ox - 24 - atk_ext, oy - 28, 8, 30], a, radius=2)
    _rect(surf, [ox + 16 + atk_ext, oy - 28, 8, 30], a, radius=2)
    # 头部
    _circle(surf, (ox, oy - 40), 14, (50, 45, 40))
    # 眼眶（燃烧红光）
    _draw_glow(surf, (ox - 6, oy - 42), 10, e, 0.9)
    _draw_glow(surf, (ox + 6, oy - 42), 10, e, 0.9)
    _circle(surf, (ox - 6, oy - 42), 4, e)
    _circle(surf, (ox + 6, oy - 42), 4, e)
    # 腿
    ls = sway * 0.3
    _rect(surf, [ox - 16 + ls, oy + 15, 12, 25], a, radius=2)
    _rect(surf, [ox + 4 - ls, oy + 15, 12, 25], a, radius=2)
    # 攻击特效
    if action == "attack":
        for i in range(5):
            ang = math.radians(i * 72 + t * 180)
            px = ox + math.cos(ang) * (35 + i * 3)
            py = oy - 10 + math.sin(ang) * (25 + i * 2)
            _draw_glow(surf, (px, py), 6, g, 0.7)


def _draw_muzhu(surf, ox, oy, cfg, sway, action, t):
    b, a, e, g = cfg["body"], cfg["accent"], cfg["eyes"], cfg["glow"]
    # 圆腹
    _circle(surf, (ox, oy), 18, b)
    # 头胸
    _circle(surf, (ox, oy - 20), 10, a)
    # 8条腿
    angles = [30, 60, 120, 150, 210, 240, 300, 330]
    for i, la in enumerate(angles):
        rad = math.radians(la + sway * 5)
        move_wiggle = math.sin(t * 12 + i) * 4 if action == "move" else 0
        x1 = ox + int(math.cos(rad) * 18)
        y1 = oy + int(math.sin(rad) * 18)
        x2 = ox + int(math.cos(rad) * 40 + move_wiggle)
        y2 = oy + int(math.sin(rad) * 40 + move_wiggle)
        _line(surf, (x1, y1), (x2, y2), (*a[:3], 200), 3)
    # 眼睛簇
    _circle(surf, (ox - 5, oy - 22), 4, e)
    _circle(surf, (ox + 5, oy - 22), 4, e)
    _draw_glow(surf, (ox, oy - 22), 8, g, 0.6)


def _draw_youhun(surf, ox, oy, cfg, sway, action, t):
    b, a, e, g = cfg["body"], cfg["accent"], cfg["eyes"], cfg["glow"]
    # 飘渺身形（多层透明椭圆叠加）
    for i in range(6):
        alpha = int(180 - i * 25)
        fade_col = (*a[:3], max(30, alpha))
        w2 = 24 - i * 2
        h2 = 35 - i * 3
        y_off = math.sin(i * 1.3 + sway * 0.2) * 4
        _ellipse_alpha(surf, (ox, oy - 10 + i * 9 + y_off), (w2, h2), fade_col)
    # 头
    _circle_alpha(surf, (ox, oy - 18), 12, (*b[:3], 200))
    # 眼睛（深邃蓝光）
    _draw_glow(surf, (ox - 5, oy - 20), 12, e, 0.8)
    _draw_glow(surf, (ox + 5, oy - 20), 12, e, 0.8)
    _circle(surf, (ox - 5, oy - 20), 3, e)
    _circle(surf, (ox + 5, oy - 20), 3, e)
    # 攻击触手
    if action == "attack":
        for i in range(4):
            wave = math.sin(t * 8 + i * 1.5) * 15
            _line(surf, (ox - 15 + i * 10, oy + 20),
                  (ox - 15 + i * 10 + wave, oy + 50), (*e[:3], 150), 3)


# ─── 基础绘图原语 ───────────────────────────────────────────────

def _circle(surf, pos, radius, color):
    if len(color) == 4 and color[3] < 255:
        s = pygame.Surface((radius*2+2, radius*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (radius+1, radius+1), radius)
        surf.blit(s, (int(pos[0]-radius-1), int(pos[1]-radius-1)))
    else:
        pygame.draw.circle(surf, color, (int(pos[0]), int(pos[1])), int(radius))

def _circle_alpha(surf, pos, radius, color):
    s = pygame.Surface((radius*2+4, radius*2+4), pygame.SRCALPHA)
    pygame.draw.circle(s, color, (radius+2, radius+2), radius)
    surf.blit(s, (int(pos[0]-radius-2), int(pos[1]-radius-2)))

def _rect(surf, rect_list, color, radius=0):
    x, y, w, h = rect_list
    if len(color) == 4 and color[3] < 255:
        s = pygame.Surface((w+2, h+2), pygame.SRCALPHA)
        pygame.draw.rect(s, color, [0, 0, w, h], border_radius=radius)
        surf.blit(s, (x, y))
    else:
        pygame.draw.rect(surf, color, [x, y, w, h], border_radius=radius)

def _rrect(surf, rect_list, color, radius=4):
    """圆角矩形"""
    x, y, w, h = rect_list
    r = min(radius, w//2, h//2)
    s = pygame.Surface((w+4, h+4), pygame.SRCALPHA)
    pygame.draw.rect(s, color, [0, 0, w, h], border_radius=r)
    surf.blit(s, (x, y))

def _line(surf, p1, p2, color, width=2):
    if len(color) == 4:
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(s, color, (int(p1[0]), int(p1[1])),
                         (int(p2[0]), int(p2[1])), width)
        surf.blit(s, (0, 0))
    else:
        pygame.draw.line(surf, color, (int(p1[0]), int(p1[1])),
                         (int(p2[0]), int(p2[1])), width)

def _ellipse_alpha(surf, pos, size, color):
    w2, h2 = size
    cx, cy = pos
    s = pygame.Surface((w2*2+4, h2*2+4), pygame.SRCALPHA)
    pygame.draw.ellipse(s, color, [0, 0, w2*2+4, h2*2+4])
    surf.blit(s, (int(cx-w2-2), int(cy-h2-2)))

def _draw_cone(surf, origin, angle_deg, length, color):
    """绘制锥形光束"""
    ang1 = math.radians(angle_deg - 22)
    ang2 = math.radians(angle_deg + 22)
    pts = [origin]
    steps = 12
    for i in range(steps + 1):
        r = length * (i / steps)
        a = ang1 + (ang2 - ang1) * i / steps
        pts.append((origin[0] + math.cos(a) * r,
                    origin[1] + math.sin(a) * r))
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(s, color, pts)
    surf.blit(s, (0, 0))


# ─── 粒子系统 ────────────────────────────────────────────────────


class ParticleSystem:
    """全局粒子系统（供外部使用）"""
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
                grav = 0.08
            elif ptype == "blood":
                col = (140, 20, 20); spd = random.uniform(1, 3.5)
                ang = random.uniform(-math.pi*0.8, -math.pi*0.2)
                life = random.randint(30, 60); sz = random.uniform(2, 4); grav = 0.12
            elif ptype == "torch":
                col = random.choice([(255,150,30),(255,200,60),(220,100,20)])
                spd = random.uniform(0.4, 1.8)
                ang = random.uniform(-math.pi*0.75, -math.pi*0.25)
                life = random.randint(25, 50); sz = random.uniform(2, 6); grav = 0.05
            elif ptype == "magic":
                col = color or random.choice([(180,100,220),(100,180,255)])
                spd = random.uniform(0.5, 2.5)
                ang = random.uniform(-math.pi*1.2, -math.pi*0.8)
                life = random.randint(30, 70); sz = random.uniform(2, 5); grav = 0.05
            elif ptype == "bone":
                col = (180,170,150); spd = random.uniform(0.5,2)
                ang = random.uniform(-math.pi, 0)
                life = random.randint(40, 80); sz = random.uniform(2,4); grav = 0.1
            else:
                col = (150,130,100); spd = 1; ang = -math.pi/2
                life = 30; sz = 3; grav = 0.08
            self.particles.append({
                "x": x + random.uniform(-spread, spread),
                "y": y + random.uniform(-spread, spread),
                "vx": math.cos(ang)*spd,
                "vy": math.sin(ang)*spd,
                "life": life, "max_life": life,
                "size": sz, "color": col, "gravity": grav
            })

    def update(self):
        self.particles = [p for p in self.particles if p["life"] > 0]
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += p["gravity"]
            p["life"] -= 1

    def draw(self, surface, cx=0, cy=0):
        for p in self.particles:
            alpha = int(255 * (p["life"] / p["max_life"]))
            sz = max(1, int(p["size"] * (p["life"] / p["max_life"])))
            s = pygame.Surface((sz*2+2, sz*2+2), pygame.SRCALPHA)
            col = (*p["color"][:3], alpha) if len(p["color"])==4 else (*p["color"], alpha)
            pygame.draw.circle(s, col, (sz+1, sz+1), sz)
            surface.blit(s, (int(p["x"]-cx-sz-1), int(p["y"]-cy-sz-1)))

    def clear(self):
        self.particles.clear()
