# -*- coding: utf-8 -*-
"""游戏资源生成器"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

from config import IMAGES_DIR, SCREEN_WIDTH, SCREEN_HEIGHT

def _d(path):
    os.makedirs(path, exist_ok=True)

def _glow(draw, pos, radius, color, intensity=1.0):
    cx, cy = pos
    for i in range(radius, 0, -3):
        a = int(50 * intensity * (i / radius))
        col = (*color[:3], a) if len(color) == 4 else (*color, a)
        draw.ellipse([cx-i, cy-i, cx+i, cy+i], fill=col)

def _vignette(img, strength=0.75):
    w, h = img.size
    arr = img.load()
    cx, cy = w//2, h//2
    max_r = math.sqrt(cx**2+cy**2)
    for y in range(h):
        for x in range(w):
            d = math.sqrt((x-cx)**2+(y-cy)**2)
            f = max(0.05, 1.0 - (d/max_r)*strength)
            p = arr[x,y]
            img.putpixel((x,y), tuple(max(0,min(255,int(c*f))) for c in p))

def _perlin(w, h, seed=0):
    random.seed(seed)
    p = [[0.0]*w for _ in range(h)]
    for o in range(4):
        sc = 2**o
        amp = 0.5**o
        for y in range(h):
            for x in range(w):
                v = math.sin(x/sc*7.13+y/sc*3.71+random.random()*10)*0.5+\
                    math.cos(y/sc*5.23+x/sc*2.37)*0.5
                p[y][x] += v*amp
    mn,mx = min(min(r) for r in p), max(max(r) for r in p)
    return [[(v-mn)/(mx-mn+1e-9) for v in r] for r in p]

def _stone(size, seed_val, base=(22,18,15), var=15):
    w,h = size
    n = _perlin(w, h, seed_val)
    img = Image.new("RGB", size)
    for y in range(h):
        for x in range(w):
            v = int(n[y][x]*var)
            c = tuple(max(0,min(255,b+v+random.randint(-3,3))) for b in base)
            img.putpixel((x,y), c)
    return ImageEnhance.Contrast(img).enhance(1.3)

def generate_all():
    bg_dir = os.path.join(IMAGES_DIR, "backgrounds")
    _d(bg_dir)
    char_dir = os.path.join(IMAGES_DIR, "characters")
    _d(char_dir)
    mon_dir = os.path.join(IMAGES_DIR, "monsters")
    _d(mon_dir)
    item_dir = os.path.join(IMAGES_DIR, "items")
    _d(item_dir)
    fx_dir = os.path.join(IMAGES_DIR, "effects")
    _d(fx_dir)
    ui_dir = os.path.join(IMAGES_DIR, "ui")
    _d(ui_dir)

    # ---- 背景 ----
    # 关卡1: 秦岭入口
    img = _stone((SCREEN_WIDTH,SCREEN_HEIGHT), 101, (25,22,18), 20)
    dr = ImageDraw.Draw(img)
    for i in range(5):
        x = 100+i*250
        dr.rectangle([x,300,x+180,720], fill=(15,12,8))
        dr.rectangle([x+5,305,x+175,345], fill=(25,20,15))
        for j in range(8):
            dr.rectangle([x+5+j*22,305,x+24+j*22,345], fill=(30,24,18))
    dr.rectangle([550,50,730,350], fill=(5,4,3))
    dr.rectangle([555,55,725,345], fill=(10,8,5))
    dr.arc([520,20,760,360], start=200, end=340, fill=(50,40,25), width=8)
    _vignette(img, 0.8)
    img.save(os.path.join(bg_dir, "level1_entrance.png"))

    # 关卡2: 甬道
    img = _stone((SCREEN_WIDTH,SCREEN_HEIGHT), 202, (20,17,14), 12)
    dr = ImageDraw.Draw(img)
    for i in range(0,SCREEN_WIDTH,200):
        dr.rectangle([i,0,i+80,SCREEN_HEIGHT], fill=(12,10,8))
        dr.line([i,0,i,SCREEN_HEIGHT], fill=(5,4,3), width=2)
    dr.line([0,SCREEN_HEIGHT//2-30,SCREEN_WIDTH,SCREEN_HEIGHT//2-30], fill=(35,28,20), width=4)
    dr.line([0,SCREEN_HEIGHT//2+30,SCREEN_WIDTH,SCREEN_HEIGHT//2+30], fill=(35,28,20), width=4)
    _vignette(img, 0.85)
    img.save(os.path.join(bg_dir, "level2_corridor.png"))

    # 关卡3: 主墓室
    img = _stone((SCREEN_WIDTH,SCREEN_HEIGHT), 303, (18,15,12), 18)
    dr = ImageDraw.Draw(img)
    cx,cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
    for r in range(200,0,-15):
        dr.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(max(0,5-r//20),max(0,4-r//20),max(0,3-r//20)))
    for angle in range(0,360,30):
        rad = math.radians(angle)
        x1,y1 = cx+int(math.cos(rad)*80), cy+int(math.sin(rad)*80)
        x2,y2 = cx+int(math.cos(rad)*160), cy+int(math.sin(rad)*160)
        dr.line([x1,y1,x2,y2], fill=(90,70,20), width=2)
    dr.arc([cx-60,cy-80,cx+60,cy+80], start=0, end=180, fill=(120,90,30), width=3)
    for px,py in [(200,100),(SCREEN_WIDTH-200,100),(200,SCREEN_HEIGHT-100),(SCREEN_WIDTH-200,SCREEN_HEIGHT-100)]:
        dr.rectangle([px-40,py-70,px+40,py+70], fill=(22,18,12))
        dr.text((px-22,py-55), "镇墓兽", fill=(70,55,25))
    _vignette(img, 0.9)
    img.save(os.path.join(bg_dir, "level3_main_chamber.png"))

    # 关卡4: 机关室
    img = _stone((SCREEN_WIDTH,SCREEN_HEIGHT), 404, (22,19,15), 10)
    dr = ImageDraw.Draw(img)
    for x in range(0,SCREEN_WIDTH,160):
        for y in range(0,SCREEN_HEIGHT,160):
            dr.rectangle([x,y,x+150,y+150], outline=(30,24,15), width=2)
            dr.arc([x+25,y+25,x+125,y+125], start=0, end=360, fill=(60,48,25), width=2)
            dr.ellipse([x+60,y+60,x+90,y+90], fill=(45,36,18))
    dr.line([0,SCREEN_HEIGHT//2,SCREEN_WIDTH,SCREEN_HEIGHT//2], fill=(70,55,30), width=6)
    dr.line([SCREEN_WIDTH//2,0,SCREEN_WIDTH//2,SCREEN_HEIGHT], fill=(70,55,30), width=6)
    _vignette(img, 0.75)
    img.save(os.path.join(bg_dir, "level4_mechanism.png"))

    # 关卡5: 陪葬坑
    img = _stone((SCREEN_WIDTH,SCREEN_HEIGHT), 505, (15,12,10), 8)
    dr = ImageDraw.Draw(img)
    for i in range(-2,6):
        x = i*180
        dr.rectangle([x,450,x+160,720], fill=(10,8,6))
        dr.text((x+20,460), "石棺", fill=(45,35,18))
    for i in range(8):
        x = 50+i*155
        dr.rectangle([x,0,x+50,320], fill=(14,11,8))
        dr.text((x+5,5), "陶俑", fill=(40,32,16))
    _vignette(img, 0.88)
    img.save(os.path.join(bg_dir, "level5_pit.png"))

    # 关卡6: 逃出生天
    img = _stone((SCREEN_WIDTH,SCREEN_HEIGHT), 606, (30,26,20), 25)
    dr = ImageDraw.Draw(img)
    for i in range(12):
        y = 50+i*55
        dr.rectangle([0,y,SCREEN_WIDTH,y+3], fill=(40,33,25))
        for j in range(20):
            x = j*65+random.randint(-5,5)
            dr.rectangle([x,y+3,x+55,y+50], fill=(25+random.randint(-5,5),20+random.randint(-3,3),15+random.randint(-3,3)))
    dr.rectangle([550,0,730,720], fill=(20,15,10))
    dr.text((580,350),"出口", fill=(120,90,40))
    _vignette(img, 0.7)
    img.save(os.path.join(bg_dir, "level6_escape.png"))

    # ---- 角色 ----
    char_info = {
        "wu_xie": {"color":(60,90,130),"accent":(100,140,180),"skin":(180,150,120)},
        "pang_ci": {"color":(130,80,50),"accent":(170,110,70),"skin":(190,140,110)},
        "zhang_qi_le": {"color":(50,60,70),"accent":(80,100,120),"skin":(170,140,110)},
    }
    for key,info in char_info.items():
        for direction in ["left","right"]:
            for stance in ["idle","walk","crouch","search"]:
                folder = os.path.join(char_dir, key, direction)
                _d(folder)
                img = _gen_character(64, 96, info, direction, stance)
                img.save(os.path.join(folder, f"{stance}.png"))
            img = _gen_character(64, 96, info, direction, "idle")
            img.save(os.path.join(char_dir, f"{key}_portrait.png"))

    # ---- 怪物 ----
    mon_info = {
        "jinipo": {"name":"禁婆","body":(20,15,30),"accent":(40,20,60),"eyes":(200,150,255)},
        "zongzi": {"name":"粽子","body":(60,55,50),"accent":(80,75,70),"eyes":(255,60,20)},
        "muzhu": {"name":"墓蛛","body":(30,25,20),"accent":(50,40,30),"eyes":(255,200,50)},
        "youhun": {"name":"幽魂","body":(40,50,60),"accent":(60,80,100),"eyes":(150,200,255)},
    }
    for key,info in mon_info.items():
        for action in ["idle","move","attack"]:
            img = _gen_monster(80, 80, info, action)
            img.save(os.path.join(mon_dir, f"{key}_{action}.png"))

    # ---- 物品 ----
    item_list = [
        ("flashlight",(180,160,80),"cyl"),("firecracker",(200,100,40),"cyl"),
        ("glowstick",(80,220,100),"cyl"),("compass",(200,170,80),"circ"),
        ("ancient_map",(180,150,90),"rect"),("dust_probe",(100,90,80),"line"),
        ("rope",(150,100,60),"coil"),("herb",(60,140,60),"leaf"),
        ("key_bronze",(160,120,60),"key"),("skull",(200,190,170),"skull"),
        ("ancient_coin",(180,160,60),"circ"),("jade_bead",(80,180,100),"circ"),
        ("torch",(180,80,30),"cyl"),("lantern",(220,180,60),"lantern"),
    ]
    for name,color,shape in item_list:
        img = _gen_item(32, 32, color, shape)
        img.save(os.path.join(item_dir, f"{name}.png"))
        img.save(os.path.join(item_dir, f"{name}_large.png"))

    # ---- UI ----
    # 血条
    img = Image.new("RGBA", (200, 16), (0,0,0,0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([0,0,199,15], radius=5, fill=(30,20,20))
    dr.rounded_rectangle([2,2,197,13], radius=4, fill=(180,30,30))
    _glow(draw=dr, pos=(50,8), radius=8, color=(255,80,80), intensity=0.6)
    img.save(os.path.join(ui_dir, "health_bar.png"))

    img = Image.new("RGBA", (200, 10), (0,0,0,0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([0,0,199,9], radius=4, fill=(20,20,40))
    dr.rounded_rectangle([2,2,197,7], radius=3, fill=(80,160,255))
    img.save(os.path.join(ui_dir, "stamina_bar.png"))

    # 道具格子
    for i in range(8):
        img = Image.new("RGBA", (50,50), (0,0,0,0))
        dr = ImageDraw.Draw(img)
        dr.rounded_rectangle([0,0,49,49], radius=6, fill=(20,16,12,200), outline=(60,48,30), width=2)
        img.save(os.path.join(ui_dir, f"slot_{i}.png"))
        img_sel = Image.new("RGBA", (50,50), (0,0,0,0))
        dr2 = ImageDraw.Draw(img_sel)
        dr2.rounded_rectangle([0,0,49,49], radius=6, fill=(30,24,15,200), outline=(220,180,80), width=3)
        img_sel.save(os.path.join(ui_dir, f"slot_{i}_sel.png"))

    # 准星
    img = Image.new("RGBA", (40,40), (0,0,0,0))
    dr = ImageDraw.Draw(img)
    dr.line([20,0,20,14], fill=(200,180,120), width=2)
    dr.line([20,26,20,40], fill=(200,180,120), width=2)
    dr.line([0,20,14,20], fill=(200,180,120), width=2)
    dr.line([26,20,40,20], fill=(200,180,120), width=2)
    dr.ellipse([17,17,23,23], fill=(200,180,120))
    img.save(os.path.join(ui_dir, "crosshair.png"))

    print("[资源] 全部美术资源生成完毕!")

def _gen_character(w, h, info, direction, stance):
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    dr = ImageDraw.Draw(img)
    flip = (direction == "left")
    bob = 3 if stance == "walk" else 0
    leg_h = 24 if stance != "crouch" else 10
    leg_y = h - leg_h - 4
    body_y = leg_y - 30
    # 背包
    bx = w//2 - 18 if not flip else w//2 + 14
    dr.rectangle([bx-4,body_y+5+bob,bx+4,body_y+22+bob], fill=(80,60,30))
    # 身体
    dr.rectangle([w//2-14,body_y+bob,w//2+14,leg_y+bob], fill=info["color"])
    # 腿
    dr.rectangle([w//2-12,leg_y,w//2+12,h-4], fill=tuple(max(0,c-20) for c in info["color"]))
    # 头
    head_y = body_y - 24
    dr.ellipse([w//2-13,head_y,w//2+13,head_y+26], fill=info["skin"])
    # 眼睛
    eye_y = head_y + 12
    eye_col = (40,30,20)
    dr.ellipse([w//2-8,eye_y,w//2-2,eye_y+5], fill=eye_col)
    dr.ellipse([w//2+2,eye_y,w//2+8,eye_y+5], fill=eye_col)
    # 手电筒
    fx = w//2+14 if not flip else w//2-18
    fy = body_y+10
    dr.rectangle([fx,fy,fx+8,fy+4], fill=(100,90,70))
    dr.ellipse([fx-2,fy-2,fx+10,fy+8], fill=(200,180,100))
    _glow(dr, (fx+3,fy+2), 10, (255,220,120), 0.7)
    return img

def _gen_monster(w, h, info, action):
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    dr = ImageDraw.Draw(img)
    bob = 4 if action in ("move","attack") else 0
    body = info["body"]
    acc = info["accent"]
    eye = info["eyes"]
    nm = info["name"]

    if nm == "禁婆":
        for i in range(6):
            off = math.sin(i*1.2)*5 + (5 if action=="move" else 0)
            dr.line([w//2-15+i*5, 12, w//2-18+i*5+off, h-5],
                    fill=(*acc, 160), width=3)
        dr.ellipse([w//2-15,8+bob,w//2+15,32+bob], fill=body)
        dr.ellipse([w//2-8,14+bob,w//2-2,20+bob], fill=eye)
        dr.ellipse([w//2+2,14+bob,w//2+8,20+bob], fill=eye)
        dr.rectangle([w//2-12,32+bob,w//2+12,h-8], fill=(*body[:3],140))
        _glow(dr,(w//2,18+bob),30,eye,0.5)
    elif nm == "粽子":
        dr.rectangle([w//2-20,18+bob,w//2+20,h-8], fill=body)
        dr.rectangle([w//2-24,22+bob,w//2-14,50+bob], fill=acc)
        dr.rectangle([w//2+14,22+bob,w//2+24,50+bob], fill=acc)
        dr.rectangle([w//2-22,50+bob,w//2-8,h-8], fill=acc)
        dr.rectangle([w//2+8,50+bob,w//2+22,h-8], fill=acc)
        dr.ellipse([w//2-14,4+bob,w//2+14,24+bob], fill=(50,45,40))
        dr.ellipse([w//2-7,12+bob,w//2-2,17+bob], fill=eye)
        dr.ellipse([w//2+2,12+bob,w//2+7,17+bob], fill=eye)
        _glow(dr,(w//2,14+bob),25,eye,0.3)
    elif nm == "墓蛛":
        cx,cy = w//2, h//2+5
        br = 14
        dr.ellipse([cx-br,cy-br+bob,cx+br,cy+br+bob], fill=body)
        dr.ellipse([cx-8,cy-br-8+bob,cx+8,cy-br+8+bob], fill=acc)
        for la in [30,60,120,150,210,240,300,330]:
            rad = math.radians(la)
            x1,y1 = cx+int(math.cos(rad)*br), cy+int(math.sin(rad)*br+bob)
            x2,y2 = cx+int(math.cos(rad)*38), cy+int(math.sin(rad)*38+bob)
            dr.line([x1,y1,x2,y2], fill=acc, width=2)
        dr.ellipse([cx-5,cy-br+2+bob,cx+5,cy-br+10+bob], fill=eye)
        _glow(dr,(cx,cy-br+6+bob),18,eye,0.6)
    elif nm == "幽魂":
        alpha = 140 if action in ("idle","move") else 190
        for i in range(5):
            y_off = i*10-5+math.sin(i*1.5)*3
            al = int(alpha*(1-i*0.15))
            col = (*acc[:3],al)
            x1,y1 = w//2-20+i*4, 10+y_off+i*8
            x2,y2 = w//2+20-i*4, y1+30-i*4
            dr.ellipse([x1,y1+bob,x2,y2+bob], fill=col)
        dr.ellipse([w//2-10,13+bob,w//2+10,28+bob], fill=(*body[:3],200))
        dr.ellipse([w//2-5,18+bob,w//2+5,24+bob], fill=eye)
        _glow(dr,(w//2,20+bob),35,eye,0.5)
    return img

def _gen_item(w, h, color, shape):
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    dr = ImageDraw.Draw(img)
    if shape == "cyl":
        dr.rectangle([6,4,26,28], fill=color)
        dr.ellipse([6,2,16,12], fill=(220,200,120))
        _glow(dr,(11,7),8,(255,240,150),0.8)
    elif shape == "circ":
        dr.ellipse([4,4,28,28], fill=color)
        dr.ellipse([8,8,24,24], fill=tuple(max(0,c-30) for c in color))
        _glow(dr,(16,16),10,color,0.5)
    elif shape == "rect":
        dr.rectangle([4,6,28,26], fill=color)
        dr.rectangle([6,8,26,24], fill=(150,120,70))
        dr.text((8,14),"古", fill=(80,60,30))
    elif shape == "line":
        dr.line([16,2,16,30], fill=color, width=4)
        dr.ellipse([12,26,20,34], fill=(80,70,60))
    elif shape == "coil":
        for i in range(4):
            dr.ellipse([4+i*3,8+i*4,28-i*3,24+i*4], outline=color, width=2)
    elif shape == "leaf":
        pts = [(16,2),(28,16),(16,30),(4,16)]
        dr.polygon(pts, fill=color)
        dr.line([16,2,16,30], fill=(40,100,40), width=2)
    elif shape == "key":
        dr.ellipse([4,4,18,18], fill=color)
        dr.ellipse([6,6,16,16], fill=(10,10,8))
        dr.rectangle([14,10,30,14], fill=color)
        dr.rectangle([24,14,28,20], fill=color)
    elif shape == "skull":
        dr.ellipse([6,4,26,22], fill=color)
        dr.ellipse([9,8,15,14], fill=(20,15,10))
        dr.ellipse([17,8,23,14], fill=(20,15,10))
        dr.rectangle([10,20,26,30], fill=color)
    elif shape == "torch":
        dr.rectangle([14,16,22,32], fill=(100,80,40))
        dr.ellipse([10,4,26,16], fill=(200,80,30))
        _glow(dr,(18,10),12,(255,150,50),0.9)
    elif shape == "lantern":
        dr.rectangle([12,8,24,10], fill=(100,80,50))
        dr.rectangle([10,10,26,28], fill=(220,180,60,200), outline=(180,140,40), width=2)
        dr.rectangle([14,12,22,26], fill=(255,220,100,150))
        _glow(dr,(18,18),16,(255,220,120),0.7)
    return img

if __name__ == "__main__":
    generate_all()
