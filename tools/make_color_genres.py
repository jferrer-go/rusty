"""Colorful genre posters (1000x1500). Each genre: one hue, layered hazy scene, film grain, white title.
Usage: python3 make_color_genres.py OUT_DIR"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, S = 1000, 1500, 2
FONT = '/usr/share/fonts/opentype/inter/'


class C:  # supersampled grayscale canvas, coords in 1000x1500 space
    def __init__(s, sky):
        g = np.linspace(sky[0], sky[1], H * S)[:, None] * np.ones((1, W * S))
        s.im = Image.fromarray(g.astype('uint8'))
        s.d = ImageDraw.Draw(s.im)
        s.glows = []

    def P(s, pts): return [(x * S, y * S) for x, y in pts]
    def poly(s, pts, v): s.d.polygon(s.P(pts), fill=v)
    def rect(s, b, v): s.d.rectangle([c * S for c in b], fill=v)
    def ell(s, b, v): s.d.ellipse([c * S for c in b], fill=v)
    def line(s, pts, v, w): s.d.line(s.P(pts), fill=v, width=int(w * S), joint='curve')
    def glow(s, x, y, r, k=1.0): s.glows.append((x, y, r, k))

    def ridge(s, y, amp, seed, v, rough=.55, bottom=H):
        r = np.random.default_rng(seed)
        n = 257; h = np.zeros(n); step = n - 1; a = amp
        h[0], h[-1] = r.normal(0, amp), r.normal(0, amp)
        while step > 1:
            for i in range(step // 2, n, step):
                h[i] = (h[i - step // 2] + h[i + step // 2]) / 2 + r.normal(0, a)
            a *= rough; step //= 2
        xs = np.linspace(-10, W + 10, n)
        s.poly([(xs[0], bottom)] + [(x, y + hh) for x, hh in zip(xs, h)] + [(xs[-1], bottom)], v)
        return lambda x: y + np.interp(x, xs, h)

    def finish(s):
        L = np.array(s.im.resize((W, H), Image.LANCZOS), float)
        yy, xx = np.mgrid[0:H, 0:W]
        for x, y, r, k in s.glows:
            L += 255 * k * np.exp(-(((xx - x) ** 2 + (yy - y) ** 2) / (2 * r * r)))
        return np.clip(L, 0, 255)


def fog(L, seed, top=.55, amt=.5, base=210):
    r = np.random.default_rng(seed)
    acc = np.zeros((H, W))
    for sc, a in ((300, .5), (120, .3), (50, .2)):
        sm = r.random((H // sc + 3, W * 2 // sc + 3))
        big = np.array(Image.fromarray((sm * 255).astype('uint8')).resize(((W * 2 // sc + 3) * sc, (H // sc + 3) * sc), Image.BICUBIC), float) / 255
        acc += a * big[:H, :W]
    band = np.exp(-((np.linspace(0, 1, H) - top) ** 2) / .03)[:, None]
    m = np.clip(band * acc * amt * 1.6, 0, .85)
    return L * (1 - m) + base * m


def tone(L, hue, seed):
    L = L / 255
    hue = np.array(hue, float)
    dark = hue * .08 + 4
    light = np.clip(hue * .3 + 185, 0, 255)
    a = L[..., None]
    rgb = np.where(a < .5, dark + (hue - dark) * (a * 2) ** .9, hue + (light - hue) * ((a - .5) * 2) ** 1.1)
    # highlight bloom
    hl = Image.fromarray((np.clip(L - .72, 0, 1) * 255 / .28).astype('uint8')).filter(ImageFilter.GaussianBlur(40))
    rgb += (np.array(hl, float) / 255 * .35)[..., None] * (light - rgb) * .8
    # vignette + bottom darkening for the title
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - .45 * (((xx - W / 2) / W) ** 2 + ((yy - H * .45) / H) ** 2) * 2
    bot = 1 - .55 * np.clip((yy / H - .62) / .38, 0, 1) ** 1.6
    rgb *= (vig * bot)[..., None]
    # film grain: mixed sizes, luminance
    r = np.random.default_rng(seed)
    g = r.normal(0, 1, (H, W))
    g2 = np.array(Image.fromarray(((r.normal(0, 1, (H // 2, W // 2)) * 40 + 128).clip(0, 255)).astype('uint8')).resize((W, H), Image.BILINEAR), float) - 128
    rgb += (g * 7 + g2 * .25)[..., None]
    # slight channel misregistration
    img = Image.fromarray(rgb.clip(0, 255).astype('uint8'))
    rch, gch, bch = img.split()
    rch = rch.transform(img.size, Image.AFFINE, (1, 0, -1, 0, 1, 0))
    bch = bch.transform(img.size, Image.AFFINE, (1, 0, 1, 0, 1, 0))
    return Image.merge('RGB', (rch, gch, bch)).filter(ImageFilter.GaussianBlur(.5))


def title(img, text):
    d = ImageDraw.Draw(img)
    size = 150
    f = lambda s: ImageFont.truetype(FONT + 'InterDisplay-Bold.otf', s)
    while d.textlength(text, font=f(size)) > 840:
        size -= 4
    font = f(size)
    # soft shadow
    sh = Image.new('L', img.size, 0)
    ImageDraw.Draw(sh).text((72, H - 120 - size), text, font=font, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    img.paste(Image.new('RGB', img.size, (0, 0, 0)), (0, 0), sh)
    d.text((70, H - 124 - size), text, font=font, fill=(250, 250, 248))
    return img


R = np.random.default_rng


# ---------------- scenes (return luminance) ----------------
def birds(c, seed, n, box, v=30):
    r = R(seed)
    for _ in range(n):
        x, y = r.uniform(box[0], box[2]), r.uniform(box[1], box[3]); s = r.uniform(6, 14)
        c.line([(x - s, y - s * .4), (x - s * .3, y), (x, y - s * .15), (x + s * .3, y), (x + s, y - s * .5)], v, 2.2)


def sc_action(seed):
    c = C((70, 150)); r = R(seed)
    c.glow(560, 760, 170, 1.0); c.glow(560, 780, 380, .45)
    # smoke column
    for i in range(40):
        x = 560 + r.normal(0, 40) + i * 3; y = 760 - i * 16; s = 40 + i * 3
        c.ell([x - s, y - s, x + s, y + s], int(60 + r.uniform(0, 30)))
    c.ridge(860, 25, seed, 120)
    x = -20
    while x < W:
        w = r.uniform(50, 120); h = r.uniform(150, 520) * (0.6 if 430 < x < 680 else 1)
        c.rect([x, 1000 - h, x + w, H], 35)
        for wy in np.arange(1000 - h + 20, 1000, 28):
            for wx in np.arange(x + 10, x + w - 10, 20):
                if r.random() < .18: c.rect([wx, wy, wx + 8, wy + 12], int(r.uniform(120, 200)))
        if r.random() < .3: c.line([(x + w / 2, 1000 - h), (x + w / 2, 1000 - h - 60)], 35, 3)
        x += w + r.uniform(-8, 6)
    # helicopter
    hx, hy = 250, 420
    c.ell([hx - 45, hy - 18, hx + 35, hy + 22], 25); c.line([(hx + 30, hy), (hx + 120, hy - 10)], 25, 7)
    c.line([(hx - 110, hy - 30), (hx + 90, hy - 36)], 25, 3); c.line([(hx - 5, hy - 18), (hx - 5, hy - 32)], 25, 4)
    c.line([(hx - 40, hy + 30), (hx + 20, hy + 30)], 25, 3)
    c.rect([0, 1000, W, H], 30)
    return fog(c.finish(), seed, .55, .4, 150)


def sc_adventure(seed):
    c = C((215, 120)); c.glow(700, 420, 110, .6)
    c.ridge(700, 80, seed, 175, .6); c.ridge(820, 110, seed + 1, 140, .58)
    L = c.finish(); L = fog(L, seed, .5, .6)
    c2 = C((0, 0)); c2.im = Image.fromarray(np.array(Image.fromarray(L.astype('uint8')).resize((W * S, H * S))))
    c2.d = ImageDraw.Draw(c2.im)
    c2.ridge(1020, 70, seed + 2, 95, .6)
    # cliff from the left
    c2.poly([(-10, 900), (180, 905), (300, 930), (420, 960), (470, 1010), (430, 1100), (380, 1500), (-10, 1500)], 28)
    # explorer: hat, body, pack, staff
    x, y = 330, 930
    c2.ell([x - 13, y - 118, x + 13, y - 92], 20); c2.poly([(x - 26, y - 100), (x + 26, y - 100), (x + 14, y - 106), (x - 14, y - 106)], 20)
    c2.poly([(x - 18, y - 92), (x + 18, y - 92), (x + 22, y - 40), (x - 20, y - 40)], 20)
    c2.rect([x - 34, y - 88, x - 14, y - 50], 20)
    c2.poly([(x - 18, y - 42), (x - 4, y - 42), (x - 10, y), (x - 22, y)], 20); c2.poly([(x + 4, y - 42), (x + 20, y - 42), (x + 28, y), (x + 14, y)], 20)
    c2.line([(x + 30, y - 120), (x + 40, y)], 20, 5)
    birds(c2, seed, 6, (520, 330, 880, 520), 60)
    return c2.finish()


def sc_animation(seed):
    c = C((230, 170)); r = R(seed)
    for cx, cy, k in ((200, 330, 1), (760, 520, .8), (420, 640, .6)):
        for _ in range(9):
            s = r.uniform(40, 85) * k
            ox, oy = cx + r.normal(0, 70 * k), cy + r.normal(0, 18); c.ell([ox - s, oy - s, ox + s, oy + s], 248)
    # balloon
    bx, by = 640, 300
    c.ell([bx - 95, by - 120, bx + 95, by + 90], 120)
    for k in (-60, 0, 60):
        c.line([(bx + k * .3, by - 118), (bx + k, by - 20), (bx + k * .5, by + 85)], 95, 6)
    c.line([(bx - 60, by + 70), (bx - 22, by + 140)], 70, 2); c.line([(bx + 60, by + 70), (bx + 22, by + 140)], 70, 2)
    c.rect([bx - 24, by + 140, bx + 24, by + 175], 60)
    c.ridge(960, 50, seed, 200, .45); c.ridge(1060, 60, seed + 1, 165, .45); c.ridge(1200, 50, seed + 2, 120, .4)
    for x in (160, 300, 820):
        y = 1150 + r.uniform(-20, 20); c.line([(x, y), (x, y - 70)], 80, 8); c.ell([x - 38, y - 140, x + 38, y - 50], 90)
    return c.finish()


def sc_anime(seed):
    c = C((225, 160)); r = R(seed)
    c.glow(260, 470, 90, .9); c.glow(260, 470, 260, .25)
    # mountain with snow
    pk = [(-10, 1080), (160, 940), (330, 800), (440, 720), (470, 712), (500, 716), (560, 724), (670, 800), (850, 930), (1010, 1060), (1010, 1500), (-10, 1500)]
    c.poly(pk, 140)
    sn = [(330, 800), (440, 720), (470, 712), (500, 716), (560, 724), (670, 800), (630, 820), (600, 790), (570, 835), (535, 790), (500, 845), (470, 795), (430, 840), (400, 800), (365, 830)]
    c.poly(sn, 225)
    L = fog(c.finish(), seed, .6, .7)
    c2 = C((0, 0)); c2.im = Image.fromarray(np.array(Image.fromarray(L.astype('uint8')).resize((W * S, H * S)))); c2.d = ImageDraw.Draw(c2.im)
    c2.ridge(1150, 30, seed + 3, 70, .5)
    # pagoda
    px, py = 210, 1150
    for i, (w, h) in enumerate(((120, 60), (100, 55), (82, 50), (64, 45))):
        y = py - 60 - i * 60
        c2.rect([px - w * .35, y, px + w * .35, y + 60], 35)
        c2.poly([(px - w * .75, y + 8), (px - w * .5, y - 8), (px + w * .5, y - 8), (px + w * .75, y + 8), (px + w * .5, y + 2), (px - w * .5, y + 2)], 35)
    c2.line([(px, py - 300), (px, py - 360)], 35, 4)
    c2.rect([0, 1200, W, H], 40)
    # blossom branch
    br = [(1020, 120), (900, 170), (790, 260), (720, 300), (650, 330)]
    for i in range(len(br) - 1): c2.line([br[i], br[i + 1]], 22, 22 - i * 4)
    c2.line([(900, 170), (860, 90)], 22, 9); c2.line([(790, 260), (760, 380)], 22, 8)
    for _ in range(170):
        t = r.random() * (len(br) - 1); i = int(t); f = t - i
        x = br[i][0] + (br[i + 1][0] - br[i][0]) * f + r.normal(0, 60); y = br[i][1] + (br[i + 1][1] - br[i][1]) * f + r.normal(0, 50)
        s = r.uniform(5, 13); c2.ell([x - s, y - s * .8, x + s, y + s * .8], int(r.uniform(195, 250)))
    for _ in range(40):
        x, y, s = r.uniform(300, 1000), r.uniform(350, 1100), r.uniform(3, 7)
        c2.ell([x - s, y - s * .6, x + s, y + s * .6], 235)
    return c2.finish()


def sc_classics(seed):
    c = C((30, 15)); r = R(seed)
    # projector beam from top right toward lower left screen
    beam = Image.new('L', (W * S, H * S), 0); bd = ImageDraw.Draw(beam)
    bd.polygon([(900 * S, 300 * S), (930 * S, 330 * S), (300 * S, 1000 * S), (-100 * S, 600 * S)], fill=150)
    beam = beam.filter(ImageFilter.GaussianBlur(40 * S))
    c.im = Image.fromarray(np.clip(np.array(c.im, float) + np.array(beam, float), 0, 255).astype('uint8')); c.d = ImageDraw.Draw(c.im)
    c.glow(915, 315, 30, 1.0); c.glow(915, 315, 120, .35)
    for _ in range(260):
        t = r.random(); x = 915 + (100 - 915) * t + r.normal(0, 90 * t); y = 315 + (800 - 315) * t + r.normal(0, 90 * t)
        s = r.uniform(.8, 2.2); c.ell([x - s, y - s, x + s, y + s], int(r.uniform(140, 230)))
    # seat rows
    for row, y in enumerate((1080, 1190, 1310, 1440)):
        sw = 120 + row * 18
        for x in np.arange(-row * 40 - 30, W + 60, sw):
            c.d.rounded_rectangle([x * S, y * S, (x + sw - 14) * S, (y + 160) * S], radius=int(40 * S), fill=12 + row * 2)
    # projector box
    c.d.rounded_rectangle([905 * S, 270 * S, 1010 * S, 360 * S], radius=10 * S, fill=8)
    return c.finish()


def sc_comedy(seed):
    c = C((40, 25)); r = R(seed)
    # brick wall
    for y in range(0, 1150, 46):
        off = 0 if (y // 46) % 2 else 60
        for x in range(-120 + off, W, 120):
            c.rect([x + 3, y + 3, x + 117, y + 43], int(40 + r.uniform(-8, 10)))
    spot = Image.new('L', (W * S, H * S), 0); sd = ImageDraw.Draw(spot)
    sd.ellipse([180 * S, 380 * S, 820 * S, 1180 * S], fill=170)
    spot = spot.filter(ImageFilter.GaussianBlur(70 * S))
    c.im = Image.fromarray(np.clip(np.array(c.im, float) + np.array(spot, float), 0, 255).astype('uint8')); c.d = ImageDraw.Draw(c.im)
    c.rect([0, 1150, W, H], 30)
    c.d.ellipse([200 * S, 1120 * S, 800 * S, 1240 * S], fill=120)
    # stool + mic stand
    c.line([(500, 1170), (500, 720)], 15, 8); c.line([(500, 1170), (440, 1185)], 15, 6); c.line([(500, 1170), (560, 1185)], 15, 6)
    c.line([(500, 760), (540, 690)], 15, 6); c.d.rounded_rectangle([528 * S, 650 * S, 556 * S, 705 * S], radius=12 * S, fill=10)
    c.d.rounded_rectangle([600 * S, 960 * S, 720 * S, 985 * S], radius=10 * S, fill=15)
    for a, b in ((610, 600), (710, 720)): c.line([(a, 985), (b, 1180)], 15, 7)
    c.line([(605, 1090), (715, 1090)], 15, 5)
    return c.finish()


def sc_crime(seed):
    c = C((40, 70)); r = R(seed)
    for x in (-40, 120, 640, 820):
        h = r.uniform(500, 800); c.rect([x, 1100 - h, x + 170, 1100], 25)
        for wy in np.arange(1100 - h + 30, 1080, 40):
            for wx in np.arange(x + 15, x + 155, 32):
                if r.random() < .15: c.rect([wx, wy, wx + 12, wy + 18], 130)
    c.rect([0, 1100, W, H], 35)
    lx = 420
    c.line([(lx, 1105), (lx, 520)], 18, 12); c.line([(lx, 525), (lx + 70, 500), (lx + 110, 520)], 18, 9)
    c.d.polygon(c.P([(lx + 85, 520), (lx + 135, 520), (lx + 125, 545), (lx + 95, 545)]), fill=240)
    c.glow(lx + 110, 545, 60, .9); c.glow(lx + 110, 620, 240, .35)
    cone = Image.new('L', (W * S, H * S), 0); ImageDraw.Draw(cone).polygon(c.P([(lx + 95, 545), (lx + 125, 545), (lx + 330, 1120), (lx - 120, 1120)]), fill=70)
    cone = cone.filter(ImageFilter.GaussianBlur(20 * S))
    c.im = Image.fromarray(np.clip(np.array(c.im, float) + np.array(cone, float), 0, 255).astype('uint8')); c.d = ImageDraw.Draw(c.im)
    # puddle reflection
    c.d.ellipse([(lx - 60) * S, 1180 * S, (lx + 260) * S, 1240 * S], fill=110)
    c.line([(lx + 110, 1190), (lx + 110, 1235)], 200, 6)
    # figure in coat + hat
    fx = 700
    c.poly([(fx - 30, 1100), (fx - 38, 930), (fx - 25, 860), (fx + 25, 860), (fx + 38, 930), (fx + 30, 1100)], 12)
    c.ell([fx - 16, 818, fx + 16, 860], 12); c.poly([(fx - 34, 830), (fx + 34, 830), (fx + 18, 818), (fx + 14, 795), (fx - 14, 795), (fx - 18, 818)], 12)
    img = c.finish()
    # rain
    rain = np.zeros((H, W)); rr = R(seed + 9)
    for _ in range(900):
        x, y, l = rr.uniform(0, W), rr.uniform(0, H), rr.uniform(20, 45)
        x0, y0 = int(x), int(y)
        for k in range(int(l)):
            yy, xx = y0 + k, int(x0 - k * .25)
            if 0 <= yy < H and 0 <= xx < W: rain[yy, xx] = 60
    return np.clip(img + rain, 0, 255)


def sc_documentary(seed):
    c = C((200, 120)); r = R(seed)
    c.glow(560, 900, 120, 1.0); c.glow(560, 900, 380, .35)
    c.ridge(930, 25, seed, 120, .5)
    c.rect([0, 990, W, H], 70)
    c.ridge(1010, 15, seed + 1, 50, .5)
    # acacia
    tx, ty = 300, 1030
    c.line([(tx, ty), (tx - 10, 860), (tx - 40, 760)], 22, 22); c.line([(tx - 10, 860), (tx + 60, 760)], 22, 16)
    c.line([(tx - 40, 760), (tx - 140, 700)], 22, 10); c.line([(tx + 60, 760), (tx + 160, 710)], 22, 10)
    for _ in range(30):
        x = tx + r.uniform(-230, 250); y = 690 + r.uniform(-30, 25); s = r.uniform(30, 60)
        c.ell([x - s * 1.6, y - s * .45, x + s * 1.6, y + s * .45], 22)
    # giraffes far right
    for gx, k in ((760, 1), (850, .8)):
        y = 1015
        c.line([(gx - 25 * k, y), (gx - 25 * k, y - 80 * k)], 22, 6 * k); c.line([(gx + 25 * k, y), (gx + 25 * k, y - 80 * k)], 22, 6 * k)
        c.ell([gx - 40 * k, y - 115 * k, gx + 40 * k, y - 70 * k], 22)
        c.line([(gx + 30 * k, y - 100 * k), (gx + 65 * k, y - 220 * k)], 22, 10 * k)
        c.ell([gx + 55 * k, y - 240 * k, gx + 95 * k, y - 215 * k], 22)
    birds(c, seed, 9, (500, 450, 900, 650), 40)
    return fog(c.finish(), seed, .62, .35)


def sc_drama(seed):
    c = C((35, 25)); r = R(seed)
    # tall window with light pouring in
    wx0, wy0, wx1, wy1 = 330, 260, 700, 900
    c.rect([wx0, wy0, wx1, wy1], 235)
    for x in (wx0 + (wx1 - wx0) / 2,): c.rect([x - 8, wy0, x + 8, wy1], 25)
    for y in np.linspace(wy0, wy1, 5)[1:-1]: c.rect([wx0, y - 7, wx1, y + 7], 25)
    c.rect([wx0 - 20, wy0 - 20, wx1 + 20, wy0], 20); c.rect([wx0 - 30, wy1, wx1 + 30, wy1 + 25], 50)
    # curtain
    c.poly([(wx0 - 30, 230), (wx0 + 90, 230), (wx0 + 40, 600), (wx0 + 70, 1300), (wx0 - 60, 1300)], 30)
    c.poly([(wx1 - 60, 230), (wx1 + 40, 230), (wx1 + 70, 1300), (wx1 - 10, 1300), (wx1 + 5, 700)], 30)
    # light shaft on floor
    sh = Image.new('L', (W * S, H * S), 0); ImageDraw.Draw(sh).polygon(c.P([(wx0, wy1), (wx1, wy1), (wx1 + 250, 1500), (wx0 - 50, 1500)]), fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(30 * S))
    c.im = Image.fromarray(np.clip(np.array(c.im, float) + np.array(sh, float), 0, 255).astype('uint8')); c.d = ImageDraw.Draw(c.im)
    # chair silhouette
    cx = 560
    c.rect([cx - 70, 1060, cx + 70, 1085], 15); c.rect([cx + 55, 900, cx + 75, 1085], 15)
    for a in (cx - 65, cx + 55): c.rect([a, 1085, a + 14, 1250], 15)
    c.glow(515, 580, 260, .35)
    for _ in range(150):
        x, y, s = r.uniform(300, 900), r.uniform(300, 1300), r.uniform(.8, 2)
        c.ell([x - s, y - s, x + s, y + s], 200)
    return c.finish()


def sc_fantasy(seed):
    c = C((210, 110)); c.glow(700, 330, 70, .8); c.glow(700, 330, 250, .3)
    c.ridge(760, 160, seed, 175, .6)
    L = fog(c.finish(), seed, .55, .6)
    c2 = C((0, 0)); c2.im = Image.fromarray(np.array(Image.fromarray(L.astype('uint8')).resize((W * S, H * S)))); c2.d = ImageDraw.Draw(c2.im)
    # crag
    c2.poly([(180, 1500), (250, 1080), (330, 990), (420, 960), (560, 950), (650, 980), (720, 1060), (790, 1500)], 70)
    base = 965
    towers = [(330, 50, 300), (390, 120, 200), (520, 56, 420), (585, 110, 230), (700, 46, 330)]
    for x0, w, h in towers:
        c2.rect([x0, base - h, x0 + w, base + 20], 70)
        for bx in np.arange(x0, x0 + w, 14): c2.rect([bx, base - h - 12, bx + 8, base - h], 70)
        c2.poly([(x0 - 8, base - h - 10), (x0 + w / 2, base - h - w * 1.9), (x0 + w + 8, base - h - 10)], 70)
        for wy in np.arange(base - h + 40, base - 20, 70): c2.rect([x0 + w / 2 - 4, wy, x0 + w / 2 + 4, wy + 18], 210)
    c2.line([(550, 545), (550, 480)], 70, 3); c2.poly([(550, 480), (590, 492), (550, 504)], 70)
    c2.ridge(1250, 50, seed + 4, 40, .5)
    birds(c2, seed, 5, (150, 420, 420, 600), 80)
    return fog(c2.finish(), seed + 1, .8, .45, 150)


def sc_horror(seed):
    c = C((150, 40)); r = R(seed)
    c.glow(720, 330, 80, .9); c.glow(720, 330, 260, .3)
    c.ell([645, 255, 795, 405], 245); c.ell([610, 230, 760, 380], 150)  # crescent
    c.ridge(1000, 40, seed, 45, .5)
    # house on hill
    hx, hy = 620, 1000
    c.poly([(hx - 120, hy), (hx - 120, hy - 160), (hx - 140, hy - 160), (hx - 30, hy - 260), (hx + 80, hy - 160), (hx + 60, hy - 160), (hx + 60, hy)], 25)
    c.rect([hx + 60, hy - 120, hx + 160, hy], 25); c.poly([(hx + 50, hy - 120), (hx + 110, hy - 180), (hx + 170, hy - 120)], 25)
    c.rect([hx - 10, hy - 330, hx + 15, hy - 220], 25)
    c.rect([hx - 60, hy - 110, hx - 30, hy - 70], 200); c.glow(hx - 45, hy - 90, 30, .4)
    # dead tree
    def branch(x, y, ang, ln, w, d):
        if d == 0 or ln < 12: return
        x2, y2 = x + math.cos(ang) * ln, y - math.sin(ang) * ln
        c.line([(x, y), (x2, y2)], 15, w)
        for k in range(2):
            branch(x2, y2, ang + r.uniform(-.7, .7), ln * r.uniform(.6, .78), w * .65, d - 1)
    branch(230, 1240, math.pi / 2 + .05, 260, 30, 8)
    c.ridge(1220, 30, seed + 1, 15, .5)
    birds(c, seed, 5, (100, 380, 500, 560), 20)
    return fog(c.finish(), seed, .74, .7, 140)


def sc_independent(seed):
    c = C((215, 130)); r = R(seed)
    c.glow(500, 860, 100, .9); c.glow(500, 860, 340, .3)
    c.ridge(860, 30, seed, 140, .5)
    c.rect([0, 900, W, H], 90)
    # road to vanishing point
    c.poly([(495, 900), (505, 900), (850, 1500), (150, 1500)], 45)
    for i in range(14):
        t0 = (i / 14) ** 2.2; t1 = ((i + .45) / 14) ** 2.2
        y0, y1 = 900 + 600 * t0, 900 + 600 * t1
        w0, w1 = 1 + 12 * t0, 1 + 12 * t1
        c.poly([(500 - w0, y0), (500 + w0, y0), (500 + w1, y1), (500 - w1, y1)], 190)
    # telephone poles
    tops = []
    for i in range(9):
        t = (i / 8) ** 2.1; x = 520 + 420 * t; yb = 900 + 560 * t; h = 30 + 520 * t
        c.line([(x, yb), (x, yb - h)], 30, 1 + 9 * t); c.line([(x - 10 - 50 * t, yb - h + 8 + 25 * t), (x + 10 + 50 * t, yb - h + 8 + 25 * t)], 30, 1 + 5 * t)
        tops.append((x, yb - h + 8 + 25 * t))
    for a, b in zip(tops, tops[1:]): c.line([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 12), b], 30, 2)
    return fog(c.finish(), seed, .6, .3)


def sc_international(seed):
    c = C((210, 140)); r = R(seed)
    c.glow(300, 520, 110, .8); c.glow(300, 520, 330, .3)
    # sea of clouds
    for row in range(5):
        y = 760 + row * 120
        for x in np.arange(-80, W + 80, 70):
            s = r.uniform(50, 100); c.ell([x - s, y - s * .5 + r.normal(0, 15), x + s, y + s * .5 + r.normal(0, 15)], int(240 - row * 22))
    c.rect([0, 1350, W, H], 140)
    # airliner silhouette, banking slightly
    px, py, a = 640, 420, -.12
    def rot(p): x, y = p; return (px + x * math.cos(a) - y * math.sin(a), py + x * math.sin(a) + y * math.cos(a))
    body = [(-230, -14), (180, -16), (230, -6), (240, 4), (180, 16), (-210, 14), (-240, 6)]
    wing = [(-30, 0), (40, 0), (-60, 150), (-100, 150)]
    wing2 = [(-30, 0), (30, 0), (-40, -110), (-75, -110)]
    tail = [(-200, -10), (-170, -10), (-215, -95), (-238, -95)]
    stab = [(-210, 0), (-185, 0), (-225, 50), (-245, 50)]
    for shp in (wing2, body, wing, tail, stab): c.poly([rot(p) for p in shp], 35)
    for ex in (-55, -85):
        c.d.ellipse([c * S for c in (*rot((ex - 18, 52 + (ex + 55) * -.4)), *rot((ex + 18, 70 + (ex + 55) * -.4)))], fill=35)
    return c.finish()


def sc_romance(seed):
    c = C((200, 110)); r = R(seed)
    c.glow(500, 780, 300, .25)
    c.ell([340, 620, 660, 940], 235)
    c.ridge(900, 50, seed, 150, .55); c.ridge(975, 35, seed + 1, 105, .5)
    c.rect([0, 1075, W, H], 40)
    c.rect([0, 1072, W, 1080], 70)
    D = 18
    def limb(pts, w):
        c.line(pts, D, w)
        for x, y in pts: c.ell([x - w / 2, y - w / 2, x + w / 2, y + w / 2], D)
    # wheels
    for wx in (300, 700):
        c.ell([wx - 78, 1000 - 78, wx + 78, 1000 + 78], D)
        c.d.ellipse([(wx - 60) * S, 940 * S, (wx + 60) * S, 1060 * S], outline=55, width=4 * S)
        c.ell([wx - 12, 988, wx + 12, 1012], 60)
    # frame, fender, engine, tank, seat, fork, bars, light
    c.poly([(230, 960), (260, 915), (330, 900), (380, 905), (330, 935), (260, 950)], D)
    c.poly([(300, 1000), (390, 930), (560, 930), (600, 1000), (520, 1030), (380, 1020)], D)
    c.poly([(450, 900), (500, 870), (590, 865), (620, 885), (600, 930), (470, 935)], D)
    c.poly([(330, 900), (460, 895), (470, 925), (350, 930)], D)
    limb([(700, 1000), (640, 860)], 16)
    limb([(640, 860), (615, 835)], 10)
    c.ell([645, 865, 685, 905], D); c.glow(675, 885, 10, .6)
    limb([(330, 1015), (230, 1020)], 12)  # exhaust
    # rider
    limb([(500, 895), (575, 950), (560, 1005)], 34)          # leg
    c.poly([(462, 912), (548, 905), (628, 805), (612, 778), (585, 765), (560, 772)], D)  # torso, leaning forward
    c.ell([584, 722, 640, 778], D)                            # helmet
    limb([(605, 795), (642, 852)], 24)            # arm to bars
    # passenger
    limb([(405, 895), (470, 945), (455, 1000)], 30)
    c.poly([(378, 912), (455, 905), (532, 808), (518, 785), (492, 775), (468, 785)], D)
    c.ell([476, 742, 526, 792], D)                            # head
    hair = [(482, 752), (440, 740), (390, 755), (330, 745), (360, 765), (300, 780), (370, 785), (420, 790), (480, 780)]
    c.poly(hair, D)
    limb([(510, 805), (562, 850), (590, 842)], 22)            # arm around rider
    # motion streaks + road dashes
    for _ in range(14):
        y = r.uniform(880, 1060); x = r.uniform(0, 200); l = r.uniform(60, 180)
        c.line([(x, y), (x + l, y)], 200, 2)
    for x in np.arange(-40, W, 150): c.rect([x, 1180, x + 80, 1188], 120)
    return fog(c.finish(), seed, .45, .2)


def sc_scifi(seed):
    c = C((40, 110)); r = R(seed)
    for _ in range(500):
        x, y, s = r.uniform(0, W), r.uniform(0, 900), r.uniform(.6, 2.2) ** 1.5
        c.ell([x - s, y - s, x + s, y + s], int(r.uniform(120, 255)))
    # ringed planet
    px, py, pr = 380, 480, 230
    ring = Image.new('L', (W * S, H * S), 0); rd = ImageDraw.Draw(ring)
    for k, v in ((1.9, 160), (1.7, 120), (1.5, 190), (1.35, 0)):
        rd.ellipse([(px - pr * k) * S, (py - pr * k * .26) * S, (px + pr * k) * S, (py + pr * k * .26) * S], outline=v, width=int(14 * S))
    ring = ring.rotate(-14, center=(px * S, py * S))
    back = ring.copy(); bd = ImageDraw.Draw(back); bd.rectangle([0, py * S, W * S, H * S], fill=0)
    back = back.rotate(0)
    c.im.paste(back, (0, 0), back)
    c.d.ellipse([(px - pr) * S, (py - pr) * S, (px + pr) * S, (py + pr) * S], fill=150)
    sh = Image.new('L', (W * S, H * S), 0); ImageDraw.Draw(sh).ellipse([(px - pr + 90) * S, (py - pr + 40) * S, (px + pr + 140) * S, (py + pr + 120) * S], fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(30 * S))
    m = Image.new('L', (W * S, H * S), 0); ImageDraw.Draw(m).ellipse([(px - pr) * S, (py - pr) * S, (px + pr) * S, (py + pr) * S], fill=255)
    arr = np.array(c.im, float); arr -= np.array(sh, float) * (np.array(m, float) / 255)
    c.im = Image.fromarray(arr.clip(0, 255).astype('uint8')); c.d = ImageDraw.Draw(c.im)
    front = ring.copy(); ImageDraw.Draw(front).rectangle([0, 0, W * S, py * S - 1], fill=0)
    c.im.paste(front, (0, 0), front)
    c.glow(px - 120, py - 120, 200, .15)
    c.ridge(1000, 80, seed, 70, .55); c.ridge(1120, 50, seed + 1, 35, .5)
    # astronaut on ridge
    ax, ay = 700, 1105
    c.ell([ax - 16, ay - 108, ax + 16, ay - 74], 25); c.d.rounded_rectangle([(ax - 22) * S, (ay - 80) * S, (ax + 22) * S, (ay - 30) * S], radius=10 * S, fill=25)
    c.rect([ax - 34, ay - 78, ax - 20, ay - 40], 25); c.rect([ax - 20, ay - 32, ax - 4, ay], 25); c.rect([ax + 4, ay - 32, ax + 20, ay], 25)
    c.line([(ax + 22, ay - 70), (ax + 40, ay - 110)], 25, 8); c.line([(ax + 44, ay - 110), (ax + 44, ay - 175)], 25, 3)
    c.poly([(ax + 44, ay - 175), (ax + 85, ay - 165), (ax + 44, ay - 150)], 25)
    return c.finish()


def sc_thriller(seed):
    c = C((20, 20))
    vx, vy = 500, 720
    def p(x, y, t): return (vx + (x - vx) * t, vy + (y - vy) * t)
    # corridor walls/floor/ceiling shades
    c.poly([(0, 0), (W, 0), (vx + 60, vy - 80), (vx - 60, vy - 80)], 30)
    c.poly([(0, H), (W, H), (vx + 60, vy + 80), (vx - 60, vy + 80)], 55)
    c.poly([(0, 0), (vx - 60, vy - 80), (vx - 60, vy + 80), (0, H)], 40)
    c.poly([(W, 0), (vx + 60, vy - 80), (vx + 60, vy + 80), (W, H)], 36)
    c.rect([vx - 60, vy - 80, vx + 60, vy + 80], 70)
    c.rect([vx - 22, vy - 50, vx + 22, vy + 80], 245); c.glow(vx, vy + 20, 60, .7); c.glow(vx, vy + 20, 200, .2)
    # doors along walls
    for t in (1.0, .62, .4, .27, .19):
        for side in (-1, 1):
            xa = vx + side * (vx + 60) * t
            xb = vx + side * (vx + 60) * t * .82
            ya0, ya1 = vy - 520 * t, vy + 640 * t
            yb0, yb1 = vy - 520 * t * .82, vy + 640 * t * .82
            if t < 1: c.poly([(xa, ya0), (xb, yb0), (xb, yb1), (xa, ya1)], 22)
    # ceiling lights
    for t in (.85, .5, .3, .2):
        y = vy - 700 * t; c.rect([vx - 70 * t, y - 6 * t, vx + 70 * t, y + 6 * t], 200); c.glow(vx, y, 70 * t, .25)
    # figure at end
    c.rect([vx - 7, vy + 10, vx + 7, vy + 80], 10); c.ell([vx - 6, vy - 4, vx + 6, vy + 10], 10)
    return c.finish()


def sc_westerns(seed):
    c = C((215, 140)); r = R(seed)
    c.glow(620, 640, 100, 1.0); c.glow(620, 640, 360, .35)
    c.poly([(-10, 900), (90, 900), (130, 830), (160, 790), (420, 785), (450, 830), (480, 905), (1010, 905), (1010, 1500), (-10, 1500)], 150)
    c.poly([(520, 990), (590, 985), (620, 860), (650, 770), (880, 765), (910, 850), (930, 995), (1010, 995), (1010, 1500), (520, 1500)], 105)
    c.ridge(1140, 25, seed, 55, .55)
    def cactus(x, y, s):
        c.line([(x, y + 20), (x + 2 * s, y - 120 * s), (x, y - 250 * s)], 25, 40 * s); c.ell([x - 20 * s, y - 270 * s, x + 20 * s, y - 232 * s], 25)
        c.line([(x, y - 90 * s), (x - 70 * s, y - 100 * s), (x - 78 * s, y - 185 * s)], 25, 30 * s); c.ell([x - 93 * s, y - 200 * s, x - 63 * s, y - 172 * s], 25)
        c.line([(x, y - 140 * s), (x + 60 * s, y - 145 * s), (x + 66 * s, y - 210 * s)], 25, 28 * s); c.ell([x + 52 * s, y - 225 * s, x + 80 * s, y - 198 * s], 25)
    cactus(220, 1190, 1.1); cactus(800, 1215, .6)
    # rider far away
    hx, hy = 470, 1120
    c.ell([hx - 30, hy - 40, hx + 30, hy - 15], 30)
    for dx in (-24, -12, 14, 26): c.line([(hx + dx, hy - 20), (hx + dx * 1.1, hy + 10)], 30, 4)
    c.line([(hx + 26, hy - 30), (hx + 42, hy - 52)], 30, 8); c.rect([hx - 6, hy - 70, hx + 6, hy - 38], 30)
    c.poly([(hx - 14, hy - 74), (hx + 14, hy - 74), (hx + 6, hy - 84), (hx - 6, hy - 84)], 30)
    birds(c, seed, 3, (650, 420, 900, 520), 60)
    return fog(c.finish(), seed, .63, .35)


def sc_whodunits(seed):
    c = C((90, 30)); r = R(seed)
    c.glow(240, 280, 60, .7); c.glow(240, 280, 220, .25); c.ell([200, 240, 280, 320], 240)
    c.ridge(1030, 20, seed, 40, .5)
    # mansion
    mx, my = 500, 1040
    c.rect([mx - 330, my - 300, mx + 330, my], 22)
    c.poly([(mx - 350, my - 300), (mx - 250, my - 420), (mx + 250, my - 420), (mx + 350, my - 300)], 22)
    c.rect([mx - 90, my - 430, mx + 90, my - 300], 22); c.poly([(mx - 110, my - 430), (mx, my - 540), (mx + 110, my - 430)], 22)
    for x in (mx - 260, mx + 210): c.rect([x, my - 480, x + 40, my - 380], 22)
    for row in range(2):
        for k in range(7):
            x = mx - 290 + k * 90; y = my - 270 + row * 130
            lit = (row, k) in ((0, 5), (1, 1))
            c.rect([x, y, x + 40, y + 80], 230 if lit else 40)
            if lit: c.glow(x + 20, y + 40, 40, .45)
            c.rect([x + 18, y, x + 22, y + 80], 22); c.rect([x, y + 38, x + 40, y + 42], 22)
    c.rect([mx - 25, my - 85, mx + 25, my], 50)
    # iron fence
    c.rect([0, 1200, W, H], 15)
    for x in np.arange(-10, W + 20, 38):
        c.rect([x, 1090, x + 7, 1220], 15); c.poly([(x - 6, 1094), (x + 3.5, 1068), (x + 13, 1094)], 15)
    c.rect([0, 1110, W, 1120], 15); c.rect([0, 1190, W, 1200], 15)
    # bare tree right
    def br(x, y, a, l, w, d):
        if d == 0: return
        x2, y2 = x + math.cos(a) * l, y - math.sin(a) * l; c.line([(x, y), (x2, y2)], 15, w)
        br(x2, y2, a + r.uniform(.2, .6), l * .72, w * .62, d - 1); br(x2, y2, a - r.uniform(.2, .6), l * .7, w * .62, d - 1)
    br(900, 1210, math.pi / 2 + .15, 230, 26, 7)
    return fog(c.finish(), seed, .72, .55, 130)


SPECS = [  # slug, title, scene, hue
    ('action', 'Action', sc_action, (232, 70, 40)),
    ('adventure', 'Adventure', sc_adventure, (30, 160, 120)),
    ('animation', 'Animation', sc_animation, (40, 160, 235)),
    ('anime', 'Anime', sc_anime, (230, 70, 140)),
    ('classics', 'Classics', sc_classics, (205, 160, 100)),
    ('comedy', 'Comedy', sc_comedy, (245, 175, 30)),
    ('crime', 'Crime', sc_crime, (40, 110, 200)),
    ('documentary', 'Documentary', sc_documentary, (225, 130, 45)),
    ('drama', 'Drama', sc_drama, (175, 95, 200)),
    ('fantasy', 'Fantasy', sc_fantasy, (125, 85, 235)),
    ('horror', 'Horror', sc_horror, (200, 30, 40)),
    ('independent', 'Independent', sc_independent, (140, 185, 60)),
    ('international', 'International', sc_international, (30, 175, 200)),
    ('romance', 'Romance', sc_romance, (240, 90, 120)),
    ('sci-fi', 'Sci-fi', sc_scifi, (60, 90, 230)),
    ('thriller', 'Thriller', sc_thriller, (20, 180, 160)),
    ('westerns', 'Westerns', sc_westerns, (230, 110, 30)),
    ('whodunits', 'Whodunits', sc_whodunits, (70, 140, 130)),
]

if __name__ == '__main__':
    out = sys.argv[1]; only = sys.argv[2:]
    os.makedirs(out, exist_ok=True)
    for i, (slug, t, fn, hue) in enumerate(SPECS):
        if only and slug not in only: continue
        img = title(tone(fn(100 + i), hue, 200 + i), t)
        p = os.path.join(out, slug + '.jpg'); img.save(p, quality=90); print(p)
