"""Kaiju collection art (poster + wide) in the colorful genre style. No specific monster is drawn."""
import math, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
import make_color_genres as g


def scene(seed):
    W, H, S = g.W, g.H, g.S
    c = g.C((35, 120)); r = np.random.default_rng(seed)
    gy = H * .72
    # fire glow behind skyline
    
    # searchlights converging high above the skyline (on something unseen)
    beams = Image.new('L', (W * S, H * S), 0); bd = ImageDraw.Draw(beams)
    tgt = (W * .62, H * .12)
    for bx in (.12, .35, .8, .95):
        x0 = W * bx
        bd.polygon([(x0 * S, gy * S), ((x0 + 12) * S, gy * S), ((tgt[0] + 60) * S, tgt[1] * S), ((tgt[0] - 60) * S, tgt[1] * S)], fill=55)
    beams = beams.filter(ImageFilter.GaussianBlur(8 * S))
    c.im = Image.fromarray(np.clip(np.array(c.im, float) + np.array(beams, float), 0, 255).astype('uint8')); c.d = ImageDraw.Draw(c.im)
    # fire glow + smoke on its own blurred layer, painted under the skyline
    fx = Image.new('L', (W * S, H * S), 0); fd = ImageDraw.Draw(fx)
    for sx in (.3, .58, .74):
        fd.ellipse([(W * sx - W * .12) * S, (gy - H * .1) * S, (W * sx + W * .12) * S, (gy + H * .06) * S], fill=150)
    fx = fx.filter(ImageFilter.GaussianBlur(40 * S))
    sm = Image.new('L', (W * S, H * S), 0); sd = ImageDraw.Draw(sm)
    for sx in (.3, .58, .74):
        for i in range(40):
            x = W * sx + r.normal(0, 20) + i * 5; y = gy - i * H * .011; s = 14 + i * 2.2
            sd.ellipse([(x - s) * S, (y - s) * S, (x + s) * S, (y + s) * S], fill=int(r.uniform(12, 26)))
    sm = sm.filter(ImageFilter.GaussianBlur(14 * S))
    arr = np.array(c.im, float) + np.array(fx, float) - np.array(sm, float)
    c.im = Image.fromarray(np.clip(arr, 0, 255).astype('uint8')); c.d = ImageDraw.Draw(c.im)
    # skyline with a few broken towers
    x = -20
    while x < W:
        w = r.uniform(W * .04, W * .1); h = r.uniform(H * .08, H * .32)
        top = gy - h
        if r.random() < .25:
            c.poly([(x, gy), (x, top + 30), (x + w * .4, top), (x + w * .55, top + 50), (x + w, top + 20), (x + w, gy)], 14)
        else:
            c.rect([x, top, x + w, gy], 14)
        for wy in np.arange(top + 15, gy - 10, 24):
            for wx in np.arange(x + 8, x + w - 8, 18):
                if r.random() < .12: c.rect([wx, wy, wx + 7, wy + 10], int(r.uniform(130, 210)))
        x += w + r.uniform(-6, 4)
    c.rect([0, gy, W, H], 10)
    # helicopters
    for hx, hy, k in ((W * .2, H * .25, 1), (W * .85, H * .32, .7)):
        c.ell([hx - 40 * k, hy - 15 * k, hx + 30 * k, hy + 18 * k], 25); c.line([(hx + 25 * k, hy), (hx + 100 * k, hy - 8 * k)], 25, 6 * k)
        c.line([(hx - 90 * k, hy - 26 * k), (hx + 80 * k, hy - 30 * k)], 25, 3); c.line([(hx - 3, hy - 15 * k), (hx - 3, hy - 28 * k)], 25, 3)
    return g.fog(c.finish(), seed, .6, .15, 120)


def build(W, H, title, out):
    g.W, g.H = W, H
    img = g.tone(scene(7), (235, 75, 35), 9)
    if title:
        img = g.title(img, title)
    img.save(out, quality=90); return out


if __name__ == '__main__':
    print(build(1000, 1500, 'Kaiju', 'covers/collections/kaiju-poster.jpg'))
    print(build(1920, 1080, None, 'covers/collections/kaiju-wide.jpg'))
