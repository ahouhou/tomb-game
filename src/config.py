# -*- coding: utf-8 -*-
"""游戏全局配置"""
import os

# ============ 项目路径 ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.dirname(BASE_DIR)
ASSETS_DIR = os.path.join(GAME_DIR, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

# ============ 窗口配置 ============
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "盗墓笔记 - 探墓解谜"

# ============ 颜色定义 ============
COLORS = {
    "black": (10, 8, 12),
    "dark": (20, 16, 24),
    "dark_gray": (40, 35, 45),
    "gray": (80, 75, 85),
    "light_gray": (120, 115, 125),
    "parchment": (210, 195, 155),
    "gold": (200, 170, 60),
    "dark_gold": (160, 120, 30),
    "red": (180, 40, 40),
    "dark_red": (120, 20, 20),
    "green": (60, 140, 60),
    "blue": (50, 80, 160),
    "cyan": (40, 160, 180),
    "orange": (200, 120, 40),
    "white": (240, 235, 220),
    "yellow": (220, 200, 80),
    "blood_red": (140, 20, 20),
    "fog": (30, 25, 35),
    "torch_light": (255, 160, 60),
    "candle_light": (255, 200, 100),
}

# ============ 玩家配置 ============
PLAYER_SPEED = 3.0
PLAYER_RUN_SPEED = 5.5
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 64
PLAYER_HEALTH = 100
PLAYER_STAMINA = 100
FLASHLIGHT_ANGLE = 45
FLASHLIGHT_RANGE = 280
FLASHLIGHT_ANGULAR_FALLOFF = True

# ============ 怪物配置 ============
MONSTER_WANDER_SPEED = 1.2
MONSTER_CHASE_SPEED = 2.8
MONSTER_DETECT_RANGE = 220
MONSTER_ATTACK_RANGE = 45
MONSTER_HEALTH = 60
MONSTER_DAMAGE = 15
MONSTER_IDLE_CHANCE = 0.002

# ============ 物品配置 ============
ITEM_WIDTH = 28
ITEM_HEIGHT = 28
ITEM_BOB_SPEED = 2.0
ITEM_BOB_AMPLITUDE = 3

# ============ 关卡配置 ============
GRAVITY = 0.5
MAX_FALL_SPEED = 12

# ============ 音效通道 ============
SOUND_CHANNELS = {
    "sfx": 0,
    "ambient": 1,
    "music": 2,
    "voice": 3,
}

# ============ 场景过渡 ============
FADE_COLOR = (5, 4, 6)
FADE_DURATION = 60  # frames

# ============ 震动效果 ============
SCREEN_SHAKE_DECAY = 0.85
SCREEN_SHAKE_AMPLITUDE = 8

# ============ 文字显示 ============
DIALOGue_FONT_SIZE = 22
DIALOGue_LINE_HEIGHT = 32
DIALOGue_BOX_PADDING = 20
NARRATIVE_FONT_SIZE = 20

# ============ UI 位置 ============
HEALTH_BAR_X = 20
HEALTH_BAR_Y = 20
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 18
STAMINA_BAR_Y = 45
INVENTORY_SLOT_SIZE = 50
INVENTORY_PADDING = 6
INVENTORY_SLOTS = 8
INVENTORY_BAR_Y = SCREEN_HEIGHT - INVENTORY_SLOT_SIZE - 20

# ============ 小地图 ============
MINIMAP_SIZE = 140
MINIMAP_X = SCREEN_WIDTH - MINIMAP_SIZE - 15
MINIMAP_Y = 15
MINIMAP_SCALE = 0.12

# ============ 提示框 ============
HINT_BOX_WIDTH = 500
HINT_BOX_Y = SCREEN_HEIGHT - 120
HINT_FONT_SIZE = 18

# ============ 道具列表 ============
TOOLS = [
    {"id": "flashlight", "name": "手电筒", "desc": "照亮黑暗，探测前方", "icon_key": "flashlight"},
    {"id": "firecracker", "name": "火折子", "desc": "可在黑暗中制造光源", "icon_key": "firecracker"},
    {"id": "glowstick", "name": "荧光棒", "desc": "弱光源，持续发光", "icon_key": "glowstick"},
    {"id": "compass", "name": "风水罗盘", "desc": "探测方向与气场", "icon_key": "compass"},
    {"id": "ancient_map", "name": "古籍残卷", "desc": "记载墓室结构与机关", "icon_key": "ancient_map"},
    {"id": "dust_probe", "name": "洛阳铲", "desc": "探测土质与结构", "icon_key": "dust_probe"},
    {"id": "rope", "name": "捆尸索", "desc": "攀爬与牵引", "icon_key": "rope"},
    {"id": "herb", "name": "避毒草药", "desc": "暂时抵御毒气", "icon_key": "herb"},
]
