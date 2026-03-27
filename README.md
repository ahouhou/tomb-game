# 🎮 盗墓笔记 - 探墓解谜

> 根据南派三叔《盗墓笔记》改编 | 第三人称探险解谜 + 轻度恐怖

**GitHub**: https://github.com/ahouhou/tomb-game

---

<p align="center">
  <img src="https://raw.githubusercontent.com/ahouhou/tomb-game/main/game_screenshots/01_main_menu.png" width="100%" alt="主菜单"/>
</p>

---

## 📋 游戏介绍

本游戏改编自南派三叔《盗墓笔记》系列小说，还原真实的地下墓穴探险体验。

**核心体验：** 探墓解谜 · 找线索 · 队友配合 · 躲避机关 · 收集明器

**美术风格：** 写实偏暗 · 电影级氛围 · 古墓真实感

---

## 🕹️ 操作说明

| 按键 | 功能 |
|:---:|:---|
| `← → / A D` | 移动 |
| `W / ↑` | 跳跃 |
| `SHIFT` | 加速奔跑（消耗体力） |
| `CTRL` | 蹲下（躲避追踪者） |
| `E` | 原地搜索（获取线索道具） |
| `F` | 开关手电筒 |
| `1-8` | 切换道具栏 |
| `鼠标左键` | 谜题交互 |
| `H` | 显示/隐藏提示 |
| `ESC` | 暂停 |

---

## 🎨 游戏截图

<p align="center">
  <img src="https://raw.githubusercontent.com/ahouhou/tomb-game/main/game_screenshots/02_character_showcase.png" width="100%" alt="角色展示"/>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/ahouhou/tomb-game/main/game_screenshots/03_monster_showcase.png" width="100%" alt="怪物图鉴"/>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/ahouhou/tomb-game/main/game_screenshots/04_particle_effects.png" width="100%" alt="粒子特效"/>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/ahouhou/tomb-game/main/game_screenshots/05_level_scenes.png" width="100%" alt="关卡场景"/>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/ahouhou/tomb-game/main/game_screenshots/06_game_ui.png" width="100%" alt="游戏UI"/>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/ahouhou/tomb-game/main/game_screenshots/07_puzzle_system.png" width="100%" alt="谜题系统"/>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/ahouhou/tomb-game/main/game_screenshots/08_atmosphere.png" width="100%" alt="氛围场景"/>
</p>

---

## 🗺️ 关卡一览

| 关卡 | 名称 | 核心谜题 | 危险元素 |
|:---:|:---|:---|:---|
| 1 | **秦岭深山 · 外墓入口** | 石刻符号密码锁 | 初步探索 |
| 2 | **幽暗甬道** | 机关地板顺序 | 翻板陷阱、禁婆 |
| 3 | **主墓室** | 七星续命灯（星象） | 粽子镇守 |
| 4 | **机关室** | 河图洛书机关 | 墓蛛、箭阵 |
| 5 | **陪葬坑** | 明器鉴定（辨诅咒） | 幽魂、坍塌 |
| 6 | **逃出生天** | 60秒限时撤离 | 粽子追击、落石 |

---

## 🧩 谜题类型

| 类型 | 描述 | 提示 |
|:---|:---|:---|
| **门锁密码** | 按八卦方位排列石刻符号 | 「前朱雀，后玄武，左青龙，右白虎」 |
| **机关地板** | 按正确顺序踩过安全地砖 | 「踩白石，不踩黑砖」 |
| **七星续命灯** | 按北斗七星顺序点亮灯柱 | 「天枢→天璇→天玑→天权→玉衡→开阳→摇光」 |
| **河图洛书** | 踏上正确风水方位 | 「戴九履一，左三右七」 |
| **明器鉴定** | 辨别真品与诅咒物 | 「青铜照镜，锈色均匀者真」 |
| **限时撤离** | 墓室坍塌前逃出 | 60秒倒计时 |

---

## 👥 角色

| 角色 | 定位 | 描述 |
|:---|:---|:---|
| **吴邪** | 探险者 | 擅长分析古籍、解读密码 |
| **胖子** | 力量担当 | 体力充沛，负责重活 |
| **张起灵** | 神秘人 | 身手矫健，沉默寡言 |

## 👹 怪物

| 怪物 | 特征 | 弱点 |
|:---|:---|:---|
| **禁婆** | 长发遮面 · 诡异低语 | 手电筒强光可暂时驱退 |
| **粽子** | 僵硬尸体 · 关节作响 | 避免正面冲突 |
| **墓蛛** | 贴墙爬行 · 八眼锁定 | 注意墙角 |
| **幽魂** | 虚无缥缈 · 时隐时现 | 接触即寒 |

---

## ✨ 技术特色

- **程序化美术资源** — 所有图片（PIL）程序生成，无须外部美术文件
- **动态动画系统** — 行走/呼吸/尘土粒子/阴影，全部实时渲染
- **粒子特效引擎** — 5种粒子类型（尘土/血腥/火焰/魔法/骨骼碎片）
- **手电筒光锥** — 跟随角色方向，营造黑灯瞎火的真实氛围
- **全局暗色遮罩** — 极限沉浸感
- **屏幕震动** — 踩陷阱/击杀时触发
- **跨平台中文字体** — 自动适配 macOS/Windows/Linux
- **Pygame 2.6** — 高性能双缓冲渲染

---

## 🛠️ 安装运行

```bash
pip install pygame pillow numpy
cd ~/tomb-game
python3 main.py
```

---

## 📂 项目结构

```
tomb-game/
├── main.py                    # 主程序入口
├── README.md                  # 项目说明
├── src/
│   ├── config.py              # 全局配置 + 中文字体系统
│   ├── animator.py            # 动态渲染系统（角色/怪物/粒子）
│   ├── entities.py            # 实体系统（玩家/怪物/粒子）
│   ├── puzzle_system.py       # 谜题交互（6种谜题）
│   ├── level_data.py          # 关卡数据（6关）
│   └── resources.py           # 美术资源生成器
├── assets/images/             # 美术资源（程序生成）
└── game_screenshots/           # 测试效果图
```

---

> *"比鬼神更可怕的，是人心。比古墓更深的，是执念。"*
> —— 《盗墓笔记》
