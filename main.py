#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""盗墓笔记 - 探墓解谜游戏 主程序"""
import sys, os, pygame

# 确保模块路径正确
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "src"))

from config import *
from game_scene import GameScene


def main():
    # pygame 初始化
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    os.environ["SDL_RENDER_SCALE_QUALITY"] = "2"
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    # 设置窗口
    flags = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SRCALPHA
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    pygame.display.set_caption(TITLE)
    pygame.mouse.set_visible(True)

    # 图标
    icon = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.rect(icon, (180, 130, 40), [20, 20, 24, 24])
    pygame.draw.rect(icon, (140, 100, 30), [22, 22, 20, 20])
    pygame.draw.circle(icon, (200, 150, 50), (32, 10), 6)
    pygame.display.set_icon(icon)

    # 创建游戏场景
    game = GameScene(screen)

    # 主循环
    while game.running:
        for event in pygame.event.get():
            game.handle_event(event)
        game.update()
        game.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
