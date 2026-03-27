# -*- coding: utf-8 -*-
"""关卡数据"""
from config import *

import pygame

# ---- 墙壁矩形 ----
class Wall:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.rect = pygame.Rect(x, y, w, h)

# ---- 关卡数据 ----
LEVELS = [
    # ===== 关卡1: 秦岭深山 - 外墓入口 =====
    {
        "id": 1,
        "name": "秦岭深山 · 外墓入口",
        "subtitle": "古墓入口现 机关暗藏",
        "bg": "assets/images/backgrounds/level1_entrance.png",
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT,
        "hints": [
            "【探墓提示】仔细观察墓门周围的石刻文字，可能藏有开启机关的线索",
            "【工具提示】使用「风水罗盘」探测气场，寻找墓室的正确方位",
            "【危险提示】甬道中可能有落石陷阱，脚步要轻",
        ],
        "puzzle": {
            "type": "door_lock",
            "title": "墓门机关",
            "description": "墓门上有四个按顺序排列的石刻符号，需按正确顺序点击",
            "symbols": ["☰", "☷", "☴", "☶"],
            "answer": [0, 3, 1, 2],  # ☰ ☶ ☷ ☴
            "hint": "「前朱雀，后玄武，左青龙，右白虎」——上北下南左西右东",
            "success_msg": "咔嚓——墓门缓缓开启，一股陈腐的气息扑面而来",
        },
        "walls": [
            Wall(0, 0, SCREEN_WIDTH, 30),
            Wall(0, 0, 30, SCREEN_HEIGHT),
            Wall(SCREEN_WIDTH-30, 0, 30, SCREEN_HEIGHT),
            Wall(0, SCREEN_HEIGHT-30, SCREEN_WIDTH, 30),
            Wall(200, 300, 180, 420),
            Wall(400, 300, 180, 420),
            Wall(600, 300, 180, 420),
            Wall(800, 300, 180, 420),
            Wall(1000, 300, 180, 420),
        ],
        "doors": [
            {"rect": pygame.Rect(540, 50, 200, 300), "to_level": 2, "locked": True, "key_item": "key_bronze"}
        ],
        "items": [
            {"id": "flashlight", "name": "手电筒", "x": 300, "y": 400},
            {"id": "ancient_coin", "name": "古钱币", "x": 700, "y": 350},
        ],
        "monsters": [],
        "traps": [],
        "player_start": (100, 500),
        "ambient_sfx": "wind",
        "music": "tomb_ambient_1",
    },

    # ===== 关卡2: 幽暗甬道 =====
    {
        "id": 2,
        "name": "幽暗甬道",
        "subtitle": "甬道深深 暗藏机关",
        "bg": "assets/images/backgrounds/level2_corridor.png",
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT,
        "hints": [
            "【探墓提示】甬道两侧的壁画描述了墓主人生前的故事，也许暗藏线索",
            "【机关提示】踩到地板上的特定位置才能安全通过，注意观察石砖颜色差异",
            "【道具提示】「洛阳铲」可以提前探测前方土质，判断是否有塌方危险",
        ],
        "puzzle": {
            "type": "floor_tiles",
            "title": "机关地板",
            "description": "甬道中有多块地砖，只有按正确顺序踩过才能安全到达对岸",
            "hint": "壁画中的人物正从左上向右下行走——「踩白石，不踩黑砖」",
            "success_msg": "所有地砖安全落下，一条安全的道路出现在你面前",
            "tiles": [
                {"x": 300, "y": 300, "safe": True},  {"x": 400, "y": 300, "safe": False},
                {"x": 500, "y": 300, "safe": True},  {"x": 600, "y": 300, "safe": False},
                {"x": 700, "y": 300, "safe": True},  {"x": 800, "y": 300, "safe": False},
                {"x": 400, "y": 400, "safe": False}, {"x": 500, "y": 400, "safe": True},
                {"x": 600, "y": 400, "safe": False}, {"x": 700, "y": 400, "safe": True},
                {"x": 800, "y": 400, "safe": True},  {"x": 900, "y": 400, "safe": True},
            ],
            "sequence": [0, 2, 4, 7, 9, 10, 11],
        },
        "walls": [
            Wall(0, 0, SCREEN_WIDTH, 30),
            Wall(0, 0, 30, SCREEN_HEIGHT),
            Wall(SCREEN_WIDTH-30, 0, 30, SCREEN_HEIGHT),
            Wall(0, SCREEN_HEIGHT-30, SCREEN_WIDTH, 30),
            Wall(200, 0, 80, 200),
            Wall(200, 350, 80, 370),
            Wall(1000, 0, 80, 200),
            Wall(1000, 350, 80, 370),
        ],
        "doors": [
            {"rect": pygame.Rect(1100, 280, 100, 200), "to_level": 3, "locked": False}
        ],
        "items": [
            {"id": "dust_probe", "name": "洛阳铲", "x": 250, "y": 500},
            {"id": "rope", "name": "捆尸索", "x": 600, "y": 500},
        ],
        "monsters": [
            {"type": "jinipo", "x": 700, "y": 450},
        ],
        "traps": [
            {"x": 380, "y": 300, "w": 60, "h": 60, "type": "spike", "damage": 25,
             "hint": "脚下有翻板陷阱！"},
            {"x": 580, "y": 300, "w": 60, "h": 60, "type": "spike", "damage": 25,
             "hint": "脚下有翻板陷阱！"},
            {"x": 780, "y": 300, "w": 60, "h": 60, "type": "spike", "damage": 25,
             "hint": "脚下有翻板陷阱！"},
        ],
        "player_start": (80, 350),
        "ambient_sfx": "drip",
        "music": "tomb_ambient_2",
    },

    # ===== 关卡3: 主墓室 =====
    {
        "id": 3,
        "name": "主墓室",
        "subtitle": "棺椁静卧 暗室深藏",
        "bg": "assets/images/backgrounds/level3_main_chamber.png",
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT,
        "hints": [
            "【探墓提示】墓室中央的棺材周围有四尊镇墓兽，它们的朝向暗藏玄机",
            "【星象提示】墓顶的星图对应北斗七星，按顺序点燃七星灯柱",
            "【警告】不可随意开棺——若未破解机关强行开棺，将触发墓室坍塌！",
        ],
        "puzzle": {
            "type": "star_lantern",
            "title": "七星续命灯",
            "description": "墓顶的星图需要按北斗七星顺序依次点亮对应的灯柱",
            "hint": "「一曰天枢、二曰天璇、三曰天玑、四曰天权、五曰玉衡、六曰开阳、七曰摇光」",
            "lantern_positions": [
                {"x": 300, "y": 150, "star": 1, "name": "天枢"},
                {"x": 500, "y": 120, "star": 2, "name": "天璇"},
                {"x": 700, "y": 150, "star": 3, "name": "天玑"},
                {"x": 400, "y": 200, "star": 4, "name": "天权"},
                {"x": 600, "y": 200, "star": 5, "name": "玉衡"},
                {"x": 500, "y": 280, "star": 6, "name": "开阳"},
                {"x": 640, "y": 280, "star": 7, "name": "摇光"},
            ],
            "correct_order": [1, 2, 3, 4, 5, 6, 7],
            "success_msg": "七灯齐明！棺材缓缓移开，露出了通往更深处的密道！",
        },
        "walls": [
            Wall(0, 0, SCREEN_WIDTH, 30),
            Wall(0, 0, 30, SCREEN_HEIGHT),
            Wall(SCREEN_WIDTH-30, 0, 30, SCREEN_HEIGHT),
            Wall(0, SCREEN_HEIGHT-30, SCREEN_WIDTH, 30),
            Wall(100, 60, 180, 150),
            Wall(SCREEN_WIDTH-280, 60, 180, 150),
            Wall(100, SCREEN_HEIGHT-230, 180, 150),
            Wall(SCREEN_WIDTH-280, SCREEN_HEIGHT-230, 180, 150),
        ],
        "doors": [
            {"rect": pygame.Rect(590, 0, 100, 80), "to_level": 4, "locked": True, "key_item": "jade_bead"},
            {"rect": pygame.Rect(1100, 300, 100, 200), "to_level": 5, "locked": False}
        ],
        "items": [
            {"id": "compass", "name": "风水罗盘", "x": 180, "y": 500},
            {"id": "skull", "name": "骷髅头", "x": 1100, "y": 200},
            {"id": "jade_bead", "name": "玉佩", "x": 500, "y": 400},
        ],
        "monsters": [
            {"type": "zongzi", "x": 800, "y": 400},
            {"type": "zongzi", "x": 300, "y": 500},
        ],
        "traps": [],
        "player_start": (50, 350),
        "ambient_sfx": "deep_breath",
        "music": "tomb_ambient_3",
    },

    # ===== 关卡4: 机关室 =====
    {
        "id": 4,
        "name": "机关室",
        "subtitle": "机括万千 生门何在",
        "bg": "assets/images/backgrounds/level4_mechanism.png",
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT,
        "hints": [
            "【探墓提示】机关室地面有河图洛书图案，踏对位置才能打开通道",
            "【风水提示】「天三地四」——三与四的和是七，代表生门",
            "【配合提示】需要两名玩家同时按住机关才能开启大门",
        ],
        "puzzle": {
            "type": "fengshui_mech",
            "title": "河图洛书机关",
            "description": "地板上刻有河图洛书图案，按「戴九履一，左三右七，二四为肩，六八为足」排列",
            "hint": "口诀：「九履一」——9在下、1在上、7在右、3在左",
            "success_msg": "轰隆声中，沉重的大门缓缓开启",
            "positions": [
                {"x": SCREEN_WIDTH//2-80, "y": SCREEN_HEIGHT//2-80, "num": 5, "safe": False},
                {"x": SCREEN_WIDTH//2+20, "y": SCREEN_HEIGHT//2-80, "num": 1, "safe": True},
                {"x": SCREEN_WIDTH//2-80, "y": SCREEN_HEIGHT//2+20, "num": 3, "safe": True},
                {"x": SCREEN_WIDTH//2+20, "y": SCREEN_HEIGHT//2+20, "num": 7, "safe": True},
            ],
            "correct_nums": [5, 1, 3, 7],
        },
        "walls": [
            Wall(0, 0, SCREEN_WIDTH, 30),
            Wall(0, 0, 30, SCREEN_HEIGHT),
            Wall(SCREEN_WIDTH-30, 0, 30, SCREEN_HEIGHT),
            Wall(0, SCREEN_HEIGHT-30, SCREEN_WIDTH, 30),
            Wall(300, 0, 80, 250),
            Wall(900, 0, 80, 250),
            Wall(300, SCREEN_HEIGHT-250, 80, 250),
            Wall(900, SCREEN_HEIGHT-250, 80, 250),
            Wall(400, 250, 480, 220),
        ],
        "doors": [
            {"rect": pygame.Rect(1100, 280, 100, 200), "to_level": 5, "locked": False}
        ],
        "items": [
            {"id": "ancient_map", "name": "古籍残卷", "x": 1100, "y": 200},
            {"id": "herb", "name": "避毒草药", "x": 400, "y": 500},
        ],
        "monsters": [
            {"type": "muzhu", "x": 600, "y": 100},
            {"type": "muzhu", "x": 900, "y": 500},
        ],
        "traps": [
            {"x": 340, "y": 340, "w": 80, "h": 60, "type": "arrow", "damage": 30,
             "hint": "箭阵陷阱！"},
            {"x": 860, "y": 340, "w": 80, "h": 60, "type": "arrow", "damage": 30,
             "hint": "箭阵陷阱！"},
        ],
        "player_start": (50, 350),
        "ambient_sfx": "mechanism",
        "music": "tomb_ambient_4",
    },

    # ===== 关卡5: 陪葬坑 =====
    {
        "id": 5,
        "name": "陪葬坑",
        "subtitle": "亡魂无数 遗骸遍野",
        "bg": "assets/images/backgrounds/level5_pit.png",
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT,
        "hints": [
            "【探墓提示】陪葬坑中散落着帛书残片，拼接后可得到逃生路线",
            "【危险提示】大量粽子苏醒，保持安静，用「捆尸索」可暂时限制其行动",
            "【鉴定提示】「古钱币」可作为鉴定明器的参照——真品入水即沉",
        ],
        "puzzle": {
            "type": "relic_appraisal",
            "title": "明器鉴定",
            "description": "墓室中有多件明器，需要鉴定出哪些是真品、哪些有诅咒",
            "hint": "「青铜照镜，锈色均匀者真；玉器入水，沉者无殃」",
            "items": [
                {"id": "relic_vase", "name": "瓷瓶", "x": 300, "y": 400, "is_cursed": False},
                {"id": "jade_bead", "name": "玉佩", "x": 600, "y": 350, "is_cursed": False},
                {"id": "skull", "name": "骷髅头", "x": 900, "y": 400, "is_cursed": True},
                {"id": "ancient_coin", "name": "古钱币", "x": 1100, "y": 350, "is_cursed": False},
            ],
            "success_msg": "明器鉴定完毕——真正的宝物散发出淡淡的光泽",
        },
        "walls": [
            Wall(0, 0, SCREEN_WIDTH, 30),
            Wall(0, 0, 30, SCREEN_HEIGHT),
            Wall(SCREEN_WIDTH-30, 0, 30, SCREEN_HEIGHT),
            Wall(0, SCREEN_HEIGHT-30, SCREEN_WIDTH, 30),
            Wall(0, 380, 200, 340),
            Wall(250, 380, 200, 340),
            Wall(500, 380, 200, 340),
            Wall(750, 380, 200, 340),
            Wall(1000, 380, 200, 340),
        ],
        "doors": [
            {"rect": pygame.Rect(1100, 50, 100, 200), "to_level": 6, "locked": True, "key_item": "ancient_map"},
            {"rect": pygame.Rect(1100, 300, 100, 200), "to_level": 6, "locked": True, "key_item": "note_scroll"},
        ],
        "items": [
            {"id": "torch", "name": "火把", "x": 350, "y": 500},
            {"id": "lantern", "name": "古灯笼", "x": 800, "y": 500},
            {"id": "note_scroll", "name": "帛书残片", "x": 550, "y": 450},
        ],
        "monsters": [
            {"type": "zongzi", "x": 300, "y": 200},
            {"type": "zongzi", "x": 700, "y": 200},
            {"type": "youhun", "x": 500, "y": 250},
        ],
        "traps": [
            {"x": 450, "y": 380, "w": 100, "h": 30, "type": "collapse", "damage": 50,
             "hint": "注意脚下！地面不稳！"},
        ],
        "player_start": (50, 250),
        "ambient_sfx": "bones",
        "music": "tomb_ambient_5",
    },

    # ===== 关卡6: 逃出生天 =====
    {
        "id": 6,
        "name": "逃出生天",
        "subtitle": "限时撤离 生死一线",
        "bg": "assets/images/backgrounds/level6_escape.png",
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT,
        "hints": [
            "【撤离提示】墓室即将坍塌！必须在倒计时结束前逃出洞口",
            "【路线提示】「古籍残卷」中记载了最近的逃生路线",
            "【协作提示】路途中会遭遇粽子阻挡，需配合通过",
        ],
        "puzzle": {
            "type": "escape_timer",
            "title": "生死撤离",
            "description": "墓室结构开始崩塌，必须在塌方前逃出墓穴",
            "time_limit": 60,  # 秒
            "hint": "不要回头，一直向前跑！",
            "success_msg": "终于冲出了墓穴！阳光洒在脸上，你大口喘息——活着真好",
        },
        "walls": [
            Wall(0, 0, SCREEN_WIDTH, 30),
            Wall(0, 0, 30, SCREEN_HEIGHT),
            Wall(SCREEN_WIDTH-30, 0, 30, SCREEN_HEIGHT),
            Wall(0, SCREEN_HEIGHT-30, SCREEN_WIDTH, 30),
            Wall(200, 0, 80, 300),
            Wall(400, 420, 80, 300),
            Wall(600, 0, 80, 300),
            Wall(800, 420, 80, 300),
            Wall(1000, 0, 80, 300),
        ],
        "doors": [
            {"rect": pygame.Rect(1100, 280, 100, 200), "to_level": -1, "locked": False, "is_exit": True}
        ],
        "items": [],
        "monsters": [
            {"type": "zongzi", "x": 500, "y": 300},
            {"type": "zongzi", "x": 900, "y": 400},
        ],
        "traps": [
            {"x": 280, "y": 0, "w": 120, "h": 40, "type": "collapse", "damage": 80,
             "hint": "头顶落石！快跑！"},
            {"x": 680, "y": 0, "w": 120, "h": 40, "type": "collapse", "damage": 80,
             "hint": "头顶落石！快跑！"},
            {"x": 1080, "y": 0, "w": 120, "h": 40, "type": "collapse", "damage": 80,
             "hint": "头顶落石！快跑！"},
        ],
        "player_start": (50, 350),
        "ambient_sfx": "collapse",
        "music": "tomb_escape",
    },
]

import pygame

def get_level(level_id):
    for lvl in LEVELS:
        if lvl["id"] == level_id:
            return lvl
    return LEVELS[0]
