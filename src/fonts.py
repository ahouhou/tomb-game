# -*- coding: utf-8 -*-
"""
跨平台中文字体解决方案
自动检测并加载 macOS / Windows / Linux 可用的中文字体
"""
import os, sys, pygame

# 字体注册表（按优先级）
FONT_REGISTRY = [
    # macOS 字体
    ("Hiragino Sans GB", "/System/Library/Fonts/Hiragino Sans GB.ttc"),
    ("STHeiti", "/System/Library/Fonts/STHeiti Medium.ttc"),
    ("PingFang", "/System/Library/Fonts/PingFang.ttc"),
    # Linux 字体
    ("Noto Sans CJK SC", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    ("WenQuanYi Micro Hei", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
    ("Source Han Sans", "/usr/share/fonts/OTF/SourceHanSans-Regular.otf"),
    # Windows 字体
    ("SimHei", "C:/Windows/Fonts/simhei.ttf"),
    ("SimSun", "C:/Windows/Fonts/simsun.ttc"),
    ("Microsoft YaHei", "C:/Windows/Fonts/msyh.ttc"),
]

_font_cache = {}

def get_font(name_hint=None, size=16, bold=False):
    """
    获取支持中文的字体
    name_hint: 优先使用的字体名（如 "Hiragino Sans GB"）
    size: 字号
    bold: 是否加粗
    返回: pygame.font.Font 对象
    """
    cache_key = (name_hint, size, bold)
    if cache_key in _font_cache:
        return _font_cache[cache_key]

    # 方法1: SysFont 方式
    sys_font_names = [
        name_hint,
        "Hiragino Sans GB",
        "PingFang SC",
        "PingFang TC",
        "STHeiti",
        "WenQuanYi Micro Hei",
        "Noto Sans CJK SC",
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
    ]

    for fname in sys_font_names:
        if not fname:
            continue
        try:
            f = pygame.font.SysFont(fname, size, bold=bold)
            # 验证字体能渲染中文
            test = f.render("盗墓笔记", True, (0,0,0))
            if test.get_width() > 0:
                _font_cache[cache_key] = f
                print(f"[字体] 使用 SysFont: {fname} (size={size})")
                return f
        except Exception:
            pass

    # 方法2: 直接加载字体文件
    for font_name, font_path in FONT_REGISTRY:
        if os.path.exists(font_path):
            try:
                f = pygame.font.Font(font_path, size)
                if bold:
                    f.set_bold(True)
                test = f.render("盗墓笔记", True, (0,0,0))
                if test.get_width() > 0:
                    _font_cache[cache_key] = f
                    print(f"[字体] 加载字体文件: {font_path} (size={size})")
                    return f
            except Exception as e:
                print(f"[字体] 加载失败 {font_path}: {e}")

    # 方法3: 降级到默认字体
    print("[字体] 降级使用默认字体")
    f = pygame.font.Font(None, size)
    if bold:
        f.set_bold(True)
    _font_cache[cache_key] = f
    return f


def render(text, size=16, color=(255,255,255), bold=False, aa=True):
    """快捷渲染文字（返回 Surface）"""
    font = get_font(size=size, bold=bold)
    return font.render(text, aa, color)


# ─── 预设字号字体 ────────────────────────────────────────────────
FONT_CACHE = {}

def F(size, bold=False):
    """获取指定字号字体（带缓存）"""
    key = (size, bold)
    if key not in FONT_CACHE:
        FONT_CACHE[key] = get_font(size=size, bold=bold)
    return FONT_CACHE[key]

def T(text, size=16, color=(220,200,170), bold=False):
    """渲染文字的快捷函数"""
    return F(size, bold).render(text, True, color)

def T_shadow(text, size=16, color=(220,200,170), shadow=(0,0,0), bold=False):
    """带阴影的文字"""
    font = F(size, bold)
    shadow_surf = font.render(text, True, shadow)
    text_surf = font.render(text, True, color)
    w, h = text_surf.get_size()
    result = pygame.Surface((w+4, h+4), pygame.SRCALPHA)
    result.blit(shadow_surf, (2, 2))
    result.blit(text_surf, (0, 0))
    return result
