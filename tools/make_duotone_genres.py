"""Colorful duotone genre posters (1000x1500): one bold hue per genre, hazy layered scene, white title bottom-left."""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import make_wide_covers as wide

W, H = 1000, 1500
rng = np.random.default_rng(7)


def fog(seed, scale=60):
    r = np.random.default_rng(seed)
    acc = np.zeros((H, W))
    for s, a in ((scale * 4, .5), (scale * 2, .3), (scale, .2)):
        small = r.random((H // s + 2, W // s + 2))
        acc += a * np.array(Image.fromarray((small * 255).astype('uint8')).resize((W + s, H + s), Image.BICUBIC))[:H, :W] / 255
    return acc


def ridge(d, y, amp, seed, val, step=20):
    r = np.random.default_rng(seed)
    pts, v = [(0, H)], 0
    for x in range(0, W + step, step):
        v = v * .8 + r.normal(0, 1)
        pts.append((x, y + amp * math.sin(x / 170 + seed) + v * amp * .25))
    pts.append((W, H))
    d.polygon(pts, fill=val)


def sc_westerns(d):
    d.ellipse([560, 330, 860, 630], fill=245)
    d.polygon([(0, 900), (120, 900), (170, 820), (430, 820), (470, 900), (1000, 900), (1000, 1500), (0, 1500)], fill=150)
    d.polygon([(500, 1000), (600, 1000), (640, 760), (900, 760), (930, 1000), (1000, 1000), (1000, 1500), (500, 1500)], fill=110)
    ridge(d, 1150, 20, 3, 60)
    for x, y, s in ((230, 1180, 1.0), (760, 1230, .7)):
        d.rounded_rectangle([x - 22 * s, y - 260 * s, x + 22 * s, y + 40], radius=int(22 * s), fill=30)
        d.rounded_rectangle([x - 90 * s, y - 170 * s, x - 50 * s, y - 70 * s], radius=int(20 * s), fill=30)
        d.rectangle([x - 90 * s, y - 90 * s, x, y - 60 * s], fill=30)
        d.rounded_rectangle([x + 50 * s, y - 210 * s, x + 90 * s, y - 110 * s], radius=int(20 * s), fill=30)
        d.rectangle([x, y - 130 * s, x + 90 * s, y - 100 * s], fill=30)


def sc_fantasy(d):
    d.ellipse([600, 200, 820, 420], fill=245)
    ridge(d, 820, 140, 1, 160, 40)
    base = 900
    for x0, w, h in ((330, 70, 330), (420, 160, 230), (600, 70, 380), (700, 60, 260)):
        d.rectangle([x0, base - h, x0 + w, base + 300], fill=90)
        d.polygon([(x0 - 15, base - h), (x0 + w / 2, base - h - 130), (x0 + w + 15, base - h)], fill=90)
    ridge(d, 1050, 60, 4, 55)
    ridge(d, 1250, 40, 8, 25)


def sc_anime(d):
    d.ellipse([140, 260, 460, 580], fill=245)
    d.polygon([(0, 1050), (330, 760), (420, 700), (520, 700), (610, 760), (1000, 1050), (1000, 1500), (0, 1500)], fill=140)
    d.polygon([(330, 760), (420, 700), (520, 700), (610, 760), (560, 800), (520, 770), (470, 810), (420, 770), (380, 800)], fill=230)
    ridge(d, 1180, 30, 2, 60)
    br = [(1000, 150), (820, 250), (700, 380), (620, 450)]
    for a, b in zip(br, br[1:]):
        d.line([a, b], fill=30, width=26)
    d.line([(820, 250), (760, 160)], fill=30, width=16)
    r = np.random.default_rng(5)
    for _ in range(90):
        t = r.random(); seg = int(t * 3); p = br[seg]; q = br[seg + 1]; f = t * 3 - seg
        x = p[0] + (q[0] - p[0]) * f + r.normal(0, 70); y = p[1] + (q[1] - p[1]) * f + r.normal(0, 55)
        s = r.uniform(10, 24)
        d.ellipse([x - s, y - s, x + s, y + s], fill=int(r.uniform(200, 250)))


def make(slug, title, scene, hue, seed, out):
    lum = Image.new('L', (W, H), 0)
    yy = np.linspace(1, 0, H)[:, None] * np.ones((1, W))
    sky = (yy * 170 + 60)
    lum = Image.fromarray(sky.astype('uint8'))
    d = ImageDraw.Draw(lum)
    scene(d)
    L = np.array(lum, float)
    f = fog(seed)
    haze = np.clip(1 - np.linspace(0, 1, H)[:, None] * 1.2, 0, 1) * .45
    L = L * (1 - haze * f) + 235 * haze * f
    L = np.array(Image.fromarray(L.clip(0, 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2)), float) / 255
    dark = np.array(hue, float) * .12
    light = np.clip(np.array(hue, float) * .35 + 175, 0, 255)
    mid = np.array(hue, float)
    lo = L[..., None] * 2; hi = (L[..., None] - .5) * 2
    rgb = np.where(L[..., None] < .5, dark + (mid - dark) * lo, mid + (light - mid) * hi)
    v = np.linspace(0, 1, H)[:, None, None]
    rgb *= np.clip(1.15 - v * .55, 0, 1) ** .6
    rgb += rng.normal(0, 6, (H, W, 1))
    img = Image.fromarray(rgb.clip(0, 255).astype('uint8'))
    dr = ImageDraw.Draw(img)
    size = 168
    font = lambda s: ImageFont.truetype(wide.FONT + 'InterDisplay-SemiBold.otf', s)
    while dr.textlength(title, font=font(size)) > 860:
        size -= 4
    dr.text((70, H - 110 - size), title, font=font(size), fill=(255, 255, 255))
    p = os.path.join(out, f'{slug}-poster.jpg'); img.save(p, quality=90); return p


SPECS = [('westerns', 'Westerns', sc_westerns, (235, 120, 25), 1),
         ('fantasy', 'Fantasy', sc_fantasy, (130, 70, 235), 2),
         ('anime', 'Anime', sc_anime, (235, 60, 140), 3)]
if __name__ == '__main__':
    for s in SPECS:
        print(make(*s, sys.argv[1]))
