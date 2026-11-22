"""K-Dramas and K-Movies collection art (poster + wide) in the colorful genre style.
Usage: python3 tools/make_kdrama.py   (writes into covers/collections/)"""
import math, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
import make_color_genres as g


def person(c, x, foot, h, v, coat=False):
    """Simple standing figure; x = centre, foot = ground y, h = height."""
    hw = h * .13
    c.ell([x - h * .07, foot - h, x + h * .07, foot - h * .86], v)               # head
    body = [(x - hw, foot - h * .84), (x + hw, foot - h * .84),
            (x + hw * (1.5 if coat else 1.05), foot - h * .42), (x - hw * (1.5 if coat else 1.05), foot - h * .42)]
    c.poly(body, v)
    c.poly([(x - hw * .95, foot - h * .45), (x - hw * .15, foot - h * .45), (x - hw * .25, foot), (x - hw * .85, foot)], v)
    c.poly([(x + hw * .15, foot - h * .45), (x + hw * .95, foot - h * .45), (x + hw * .85, foot), (x + hw * .25, foot)], v)


def hanok_roof(c, x0, x1, y, depth, v):
    """Front view of a tiled hanok roof: ridge at y, concave slopes, eave tips lifted at x0/x1."""
    W = x1 - x0; n = 30
    xa, xb = x0 + W * .2, x1 - W * .2            # ridge ends
    yt = y + depth * .7                           # eave tips
    def slope(xs, xe):                            # tip -> ridge end, bowed below the chord (concave)
        return [(xs + (xe - xs) * t, yt + (y - yt) * t + depth * .28 * math.sin(math.pi * t)) for t in np.linspace(0, 1, n)]
    eave = [(x0 + W * t, yt + depth * .3 * math.sin(math.pi * t) ** .6) for t in np.linspace(0, 1, n)]
    top = slope(x0, xa) + slope(x1, xb)[::-1]
    c.poly(top + eave[::-1], v)
    for i in range(2, n - 1, 2):                  # tile rows
        ex, ey = eave[i]; tx, ty = top[min(int(i / n * len(top)), len(top) - 1)]
        c.line([(ex, ey - 4), (ex + (tx - ex) * .85, ey + (ty - ey) * .85)], v + 12, 3)
    c.line([(xa - 6, y - 5), (xb + 6, y - 5)], v, 14)    # ridge cap
    for ex, s in ((xa, -1), (xb, 1)):                     # ridge end flicks
        c.poly([(ex, y - 12), (ex + s * 34, y - 36), (ex + s * 14, y + 4)], v)


def sc_kdrama(seed):
    W, H = g.W, g.H
    c = g.C((150, 70)); r = np.random.default_rng(seed)
    # big hazy moon
    cx = W * .62
    c.glow(cx, H * .24, min(W, H) * .22, .35)
    c.ell([cx - 110, H * .24 - 110, cx + 110, H * .24 + 110], 225)
    # far hills with a broadcast tower on the left hill
    hill = c.ridge(H * .55, 40, seed, 95, .5)
    tx = W * .26; ty = float(hill(tx)) - H * .02
    c.ell([tx - W * .16, ty - 30, tx + W * .16, ty + 120], 95)
    c.rect([tx - 7, ty - H * .2, tx + 7, ty + 10], 60)
    c.poly([(tx - 34, ty - H * .2), (tx + 34, ty - H * .2), (tx + 22, ty - H * .2 - 38), (tx - 22, ty - H * .2 - 38)], 60)
    c.rect([tx - 3, ty - H * .2 - 130, tx + 3, ty - H * .2 - 38], 60)
    c.ell([tx - 7, ty - H * .2 - 138, tx + 7, ty - H * .2 - 124], 240); c.glow(tx, ty - H * .2 - 131, 18, .6)
    # city below the hills
    gy = H * .66
    x = -20
    while x < W:
        w = r.uniform(W * .03, W * .08); h = r.uniform(H * .04, H * .14)
        c.rect([x, gy - h, x + w, gy + 20], 45)
        for wy in np.arange(gy - h + 10, gy, 16):
            for wx in np.arange(x + 5, x + w - 5, 12):
                if r.random() < .3: c.rect([wx, wy, wx + 5, wy + 7], int(r.uniform(150, 230)))
        x += w + r.uniform(-4, 4)
    # rooftop terrace in the foreground: ledge + railing
    ry = H * .75
    c.rect([0, ry, W, H], 14)
    c.rect([0, ry - 8, W, ry + 6], 30)
    c.rect([0, ry - 70, W, ry - 62], 18)
    for px in np.arange(10, W, 46): c.rect([px, ry - 70, px + 5, ry], 18)
    # string lights across the top
    for k in range(2):
        y0 = H * (.06 + k * .05)
        pts = [(t * W, y0 + math.sin(t * math.pi) * H * .05) for t in np.linspace(0, 1, 16)]
        c.line(pts, 20, 2)
        for px, py in pts[1:-1]:
            c.ell([px - 6, py + 2, px + 6, py + 14], 245); c.glow(px, py + 8, 14, .35)
    # couple under one umbrella, standing at the railing
    ux, foot = W * .5, ry - 4
    hgt = min(W, H) * .33
    person(c, ux - hgt * .11, foot, hgt, 10, coat=True)
    person(c, ux + hgt * .12, foot, hgt * .93, 10)
    c.line([(ux, foot - hgt * .62), (ux, foot - hgt * 1.18)], 10, 6)
    uw = hgt * .52
    canopy = [(ux - uw, foot - hgt * 1.08)] + [(ux + uw * math.cos(a), foot - hgt * 1.08 - uw * .55 * math.sin(a)) for a in np.linspace(math.pi, 0, 30)] + [(ux + uw, foot - hgt * 1.08)]
    c.poly(canopy, 10)
    for k in range(5):
        sx = ux - uw + k * uw / 2
        c.ell([sx - uw / 4, foot - hgt * 1.08 - 14, sx + uw / 4, foot - hgt * 1.08 + 14], 10)
    # falling blossom petals
    for _ in range(140):
        px, py = r.uniform(0, W), r.uniform(0, H * .9); s = r.uniform(3, 8)
        c.ell([px - s, py - s * .6, px + s, py + s * .6], int(r.uniform(190, 250)))
    return g.fog(c.finish(), seed, .58, .25, 170)


def sc_kmovie(seed):
    W, H = g.W, g.H
    c = g.C((120, 40)); r = np.random.default_rng(seed)
    # projector beam from the top right
    beam = Image.new('L', (W * g.S, H * g.S), 0)
    ImageDraw.Draw(beam).polygon([(W * .95 * g.S, -10), (W * 1.02 * g.S, 0), (W * .2 * g.S, H * .72 * g.S), (W * -.2 * g.S, H * .6 * g.S)], fill=60)
    beam = beam.filter(ImageFilter.GaussianBlur(30 * g.S))
    c.im = Image.fromarray(np.clip(np.array(c.im, float) + np.array(beam, float), 0, 255).astype('uint8')); c.d = ImageDraw.Draw(c.im)
    # dust in the beam
    for _ in range(90):
        t = r.uniform(0, 1); x = W * (.98 - .95 * t) + r.normal(0, 40); y = H * .66 * t + r.normal(0, 30)
        s = r.uniform(1.5, 3.5); c.ell([x - s, y - s, x + s, y + s], int(r.uniform(150, 220)))
    # far apartment blocks
    gy = H * .7
    x = -10
    while x < W:
        w = r.uniform(W * .12, W * .2); h = r.uniform(H * .2, H * .34)
        c.rect([x, gy - h, x + w, gy], 52)
        for wy in np.arange(gy - h + 18, gy - 10, 26):
            for wx in np.arange(x + 10, x + w - 10, 20):
                if r.random() < .14: c.rect([wx, wy, wx + 9, wy + 12], int(r.uniform(140, 220)))
        x += w + r.uniform(4, 20)
    # hanok roof in the foreground left, wall below it
    rx0, rx1 = W * .03, W * .5
    hanok_roof(c, rx0, rx1, gy - H * .2, H * .1, 10)
    c.rect([rx0 + W * .05, gy - H * .12, rx1 - W * .05, gy], 10)
    for k in range(4):  # wall posts
        px = rx0 + W * .06 + k * (rx1 - rx0 - W * .12) / 3
        c.rect([px - 5, gy - H * .12, px + 5, gy], 26)
    # alley floor, wet with a reflection strip
    c.rect([0, gy, W, H], 16)
    # streetlamp and its pool of light
    lx = W * .76
    c.rect([lx - 5, gy - H * .3, lx + 5, gy + 30], 12)
    c.line([(lx, gy - H * .3), (lx - 50, gy - H * .3 - 10)], 12, 8)
    c.ell([lx - 72, gy - H * .3 - 6, lx - 32, gy - H * .3 + 14], 250); c.glow(lx - 52, gy - H * .3 + 6, 60, .55)
    c.glow(lx - 60, gy + H * .06, 160, .4)
    # lone figure in a long coat
    fx, foot = W * .62, gy + H * .1
    hgt = min(W, H) * .36
    person(c, fx, foot, hgt, 8, coat=True)
    # reflection on the wet ground
    for k in range(10):
        y = foot + 6 + k * 9
        c.rect([fx - hgt * .1 + r.normal(0, 4), y, fx + hgt * .1 + r.normal(0, 4), y + 4], 30)
    for k in range(14):
        y = gy + H * .1 + k * 8
        c.rect([lx - 70 + r.normal(0, 8), y, lx - 10 + r.normal(0, 8), y + 3], int(110 - k * 5))
    # film-frame sprocket holes down both edges
    for y in np.arange(20, H, 70):
        for x0 in (14, W - 40):
            c.rect([x0, y, x0 + 26, y + 38], 205)
    return g.fog(c.finish(), seed, .62, .18, 140)


SPECS = [  # slug, title, scene, hue, seed
    ('kdramas', 'K-Dramas', sc_kdrama, (235, 95, 150), 31),
    ('kmovies', 'K-Movies', sc_kmovie, (215, 60, 60), 32),
]


def build(W, H, title, scene, hue, seed, out):
    g.W, g.H = W, H
    img = g.tone(scene(seed), hue, seed + 100)
    if title:
        img = g.title(img, title)
    img.save(out, quality=90); return out


if __name__ == '__main__':
    os.makedirs('covers/collections', exist_ok=True)
    for slug, t, fn, hue, seed in SPECS:
        print(build(1000, 1500, t, fn, hue, seed, f'covers/collections/{slug}-poster.jpg'))
        print(build(1920, 1080, None, fn, hue, seed, f'covers/collections/{slug}-wide.jpg'))
