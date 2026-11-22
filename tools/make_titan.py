"""Titans collection art (poster + wide, greyscale): an original crystal-spined shell surfacing in a harbor.
Usage: python3 tools/make_titan.py   (writes into covers/collections/)"""
import math, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
import make_color_genres as g


def scene(seed):
    W, H = g.W, g.H
    c = g.C((205, 95)); r = np.random.default_rng(seed)
    wy = H * .64                                    # waterline
    # low sun behind the titan
    sx, sy = W * (.58 if H > W else .55), H * .42
    c.glow(sx, sy - min(W, H) * .12, min(W, H) * .22, .22)
    c.ell([sx - 70, sy - 70, sx + 70, sy + 70], 245)
    # distant mountains
    c.ridge(H * .56, 40, seed, 150, .5, bottom=wy + 5)
    # --- the titan: domed shell like a small mountain range ---
    portrait = H > W
    cx = W * (.5 if portrait else .52); sw = W * .29 if portrait else H * .33       # half-width of shell
    top = wy - sw * 1.05
    V = 12
    shell = [(cx - sw * 1.15, wy + 10)]
    for t in np.linspace(0, 1, 60):
        x = cx - sw * 1.15 + t * sw * 2.3
        y = wy - math.sin(t * math.pi) ** .7 * sw * .95 + r.normal(0, 4)
        shell.append((x, y))
    shell.append((cx + sw * 1.15, wy + 10))
    c.poly(shell, V)
    # crystal spires growing from the shell
    for k in range(11):
        t = r.uniform(.15, .85)
        x = cx - sw * 1.15 + t * sw * 2.3
        base = wy - math.sin(t * math.pi) ** .7 * sw * .95 + 12
        hgt = sw * r.uniform(.18, .55) * math.sin(t * math.pi)
        w = r.uniform(10, 26); lean = r.normal(0, 14)
        c.poly([(x - w, base), (x + lean, base - hgt), (x + w, base)], V)
        if r.random() < .5: c.glow(x + lean * .9, base - hgt * .92, 12, .35)
    # glowing seams across the shell plates
    for k in range(5):
        t0 = .2 + k * .15
        pts = []
        for t in np.linspace(t0 - .08, t0 + .06, 10):
            x = cx - sw * 1.15 + t * sw * 2.3
            y = wy - math.sin(t * math.pi) ** .7 * sw * (.55 + .2 * math.sin(k)) + r.normal(0, 3)
            pts.append((x, y))
        c.line(pts, 150, 3)
    # front leg breaking the water
    c.poly([(cx + sw * .55, wy + 10), (cx + sw * .62, wy - sw * .25), (cx + sw * .8, wy - sw * .25), (cx + sw * .85, wy + 10)], V)
    # water + wake + spray
    c.rect([0, wy, W, H], 60)
    for k in range(40):
        y = wy + 6 + k * (H - wy) / 40
        for _ in range(3):
            x = r.uniform(0, W); l = r.uniform(30, 160) * (1 + k / 20)
            c.line([(x, y), (x + l, y)], int(r.uniform(90, 160)), 2 + k / 20)
    for _ in range(160):
        x = cx + r.normal(0, sw * .9); y = wy - abs(r.normal(0, 18)); s = r.uniform(2, 6)
        c.ell([x - s, y - s, x + s, y + s], int(r.uniform(180, 240)))
    # sun reflection column
    for k in range(18):
        y = wy + 10 + k * 14; w = 50 + k * 6
        c.rect([sx - w / 2 + r.normal(0, 10), y, sx + w / 2 + r.normal(0, 10), y + 4], 215)
    # foreground: harbor cranes and a small tug for scale
    for bx, h in (((W * .05, H * .2),) if H > W else ((W * .06, H * .3), (W * .17, H * .22))):
        base = wy + H * .05
        c.rect([bx - 6, base - h, bx + 6, base], 14)
        c.line([(bx, base - h), (bx + W * .14, base - h * 1.05)], 14, 7)
        c.line([(bx, base - h * .8), (bx + W * .1, base - h * 1.04)], 14, 3)
        c.line([(bx + W * .12, base - h * 1.04), (bx + W * .12, base - h * .7)], 14, 2)
    c.rect([0, wy + H * .05, W * (.18 if H > W else .26), H], 8)
    tx, ty = W * .72, wy + H * .1
    c.poly([(tx - 50, ty), (tx + 60, ty), (tx + 45, ty + 18), (tx - 40, ty + 18)], 14)
    c.rect([tx - 10, ty - 22, tx + 20, ty], 14)
    # birds fleeing
    g.birds(c, seed, 14, (W * .55, H * .12, W * .95, H * .3), 30)
    return g.fog(c.finish(), seed, .62, .12, 190)


def build(W, H, title, out, jp=None):
    g.W, g.H = W, H
    img = g.tone(scene(11), (150, 150, 150), 21).convert('L').convert('RGB')
    if title:
        img = g.title(img, title)
    if jp:  # vertical Japanese title down the top-right edge
        from PIL import ImageFont
        d = ImageDraw.Draw(img)
        size = int(min(W, H) * .17)
        f = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', size, index=0)
        x = W - size - int(W * .06); y = int(H * .06)
        sh = Image.new('L', img.size, 0); sd = ImageDraw.Draw(sh)
        for i, ch in enumerate(jp):
            sd.text((x + 3, y + 4 + i * size * 1.05), ch, font=f, fill=150)
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        img.paste(Image.new('RGB', img.size, (0, 0, 0)), (0, 0), sh)
        for i, ch in enumerate(jp):
            d.text((x, y + i * size * 1.05), ch, font=f, fill=(250, 250, 248))
    img.save(out, quality=90); return out


if __name__ == '__main__':
    print(build(1000, 1500, 'Kaiju', 'covers/collections/titans-poster.jpg', jp='怪獣'))
    print(build(1920, 1080, None, 'covers/collections/titans-wide.jpg'))
