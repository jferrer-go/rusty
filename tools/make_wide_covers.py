"""Wide (16:9) folder covers for Rusty: mesh gradient, grain, a graphic motif per folder, big type."""
import math, os, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FONT = '/usr/share/fonts/opentype/inter/'
TITLE = ImageFont.truetype(FONT + 'InterDisplay-Black.otf', 170)
LABEL = ImageFont.truetype(FONT + 'InterDisplay-Bold.otf', 44)
BG = np.array([12, 12, 15], float)


def mesh(colors, seed):
    rng = random.Random(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    img = np.tile(BG, (H, W, 1))
    for c, (cx, cy, r) in colors:
        d = np.sqrt((xx - cx * W) ** 2 + (yy - cy * H) ** 2) / (r * W)
        a = np.clip(1 - d, 0, 1) ** 2.2
        img = img * (1 - a[..., None]) + np.array(c, float) * a[..., None]
    # darken the left/bottom so the type reads
    shade = np.clip((xx / W) * 0.9 + 0.1, 0, 1) * np.clip(1 - (yy / H - 0.45) * 0.9, 0.35, 1)
    img = BG + (img - BG) * shade[..., None]
    return img


def grain(img, amt=10, seed=0):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, amt, (H, W, 1))
    return np.clip(img + n, 0, 255)


def glow_layer(draw_fn, blur=18):
    layer = Image.new('L', (W, H), 0)
    draw_fn(ImageDraw.Draw(layer))
    return layer, layer.filter(ImageFilter.GaussianBlur(blur))


def star(cx, cy, r, rot=-math.pi / 2):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.42
        a = rot + i * math.pi / 5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


# ---- motifs (drawn white on an L mask, right half of the frame) ----
def m_popular(d):  # concentric "heat" rings, like a pulse spreading out
    cx, cy = 1450, 560
    for i, r in enumerate(range(80, 760, 70)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=255 - i * 20, width=max(3, 14 - i))
    d.ellipse([cx - 55, cy - 55, cx + 55, cy + 55], fill=255)


def m_trending(d):  # rising line chart with an arrow head
    pts = [(1130, 880), (1290, 750), (1400, 805), (1540, 560), (1650, 615), (1800, 300)]
    d.line(pts, fill=255, width=26, joint='curve')
    for p in pts[:-1]:
        d.ellipse([p[0] - 18, p[1] - 18, p[0] + 18, p[1] + 18], fill=255)
    x, y = pts[-1]
    d.polygon([(x + 40, y - 40), (x - 60, y - 20), (x + 20, y + 60)], fill=255)
    for i in range(6):  # faint grid
        d.line([(1110, 940 - i * 130), (1840, 940 - i * 130)], fill=60, width=3)


def m_top_rated(d):  # big star with two smaller ones
    d.polygon(star(1470, 540, 330), fill=255)
    d.polygon(star(1080, 330, 110), fill=200)
    d.polygon(star(1790, 860, 90), fill=170)


def m_airing(d):  # broadcast arcs from a dot
    cx, cy = 1380, 700
    d.ellipse([cx - 45, cy - 45, cx + 45, cy + 45], fill=255)
    for i, r in enumerate([150, 260, 370, 480]):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=-75, end=15, fill=255 - i * 40, width=30)
        d.arc([cx - r, cy - r, cx + r, cy + r], start=165, end=255, fill=255 - i * 40, width=30)


def m_anime_airing(d):  # sunburst rays
    cx, cy = 1500, 540
    for i in range(18):
        a = i * math.pi / 9
        a2 = a + math.pi / 30
        d.polygon([(cx, cy), (cx + 1200 * math.cos(a), cy + 1200 * math.sin(a)),
                   (cx + 1200 * math.cos(a2), cy + 1200 * math.sin(a2))], fill=150)
    d.ellipse([cx - 170, cy - 170, cx + 170, cy + 170], fill=255)


def m_anime_top(d):  # sakura-like five-petal flowers
    def flower(cx, cy, r, f):
        for i in range(5):
            a = -math.pi / 2 + i * 2 * math.pi / 5
            px, py = cx + r * 0.55 * math.cos(a), cy + r * 0.55 * math.sin(a)
            d.ellipse([px - r * 0.45, py - r * 0.45, px + r * 0.45, py + r * 0.45], fill=f)
        d.ellipse([cx - r * 0.18, cy - r * 0.18, cx + r * 0.18, cy + r * 0.18], fill=0)
    flower(1480, 520, 330, 255)
    flower(1080, 260, 110, 190)
    flower(1800, 880, 120, 170)


SPECS = [
    # path, label, title lines, motif, (main colour, accent colour), seed
    ('films/popular', 'FILMS', ['POPULAR'], m_popular, ((235, 105, 30), (190, 30, 60)), 1),
    ('films/trending', 'FILMS', ['TRENDING'], m_trending, ((225, 40, 120), (110, 40, 220)), 2),
    ('films/top-rated', 'FILMS', ['TOP RATED'], m_top_rated, ((230, 170, 40), (200, 80, 20)), 3),
    ('series/popular', 'SERIES', ['POPULAR'], m_popular, ((235, 105, 30), (190, 30, 60)), 4),
    ('series/trending', 'SERIES', ['TRENDING'], m_trending, ((225, 40, 120), (110, 40, 220)), 5),
    ('series/top-rated', 'SERIES', ['TOP RATED'], m_top_rated, ((230, 170, 40), (200, 80, 20)), 6),
    ('series/airing-today', 'SERIES', ['AIRING', 'TODAY'], m_airing, ((40, 120, 235), (20, 200, 200)), 7),
    ('anime/airing-now', 'ANIME', ['AIRING NOW'], m_anime_airing, ((140, 60, 230), (230, 60, 150)), 8),
    ('anime/top-anime', 'ANIME', ['TOP ANIME'], m_anime_top, ((235, 90, 160), (120, 50, 220)), 9),
]


def make(path, label, lines, motif, cols, seed, out):
    main, acc = cols
    base = mesh([(acc, (0.95, 0.15, 0.55)), (main, (0.72, 0.55, 0.6)), (main, (1.0, 1.0, 0.4))], seed)
    img = Image.fromarray(grain(base, 9, seed).astype('uint8'))

    mask, glow = glow_layer(motif, 28)
    fade = Image.linear_gradient('L').rotate(90, expand=True).resize((W, H))  # 0 left -> 255 right
    fade = fade.point(lambda v: max(0, min(255, int((v - 95) * 3.2))))
    mask = Image.fromarray((np.array(mask, float) * np.array(fade, float) / 255).astype('uint8'))
    glow = Image.fromarray((np.array(glow, float) * np.array(fade, float) / 255).astype('uint8'))
    tint = Image.new('RGB', (W, H), tuple(min(255, int(c * 0.35 + 165)) for c in main))
    img = Image.composite(Image.blend(img, Image.new('RGB', (W, H), main), 0.6), img, glow.point(lambda v: int(v * 0.8)))
    img = Image.composite(tint, img, mask.point(lambda v: int(v * 0.85)))

    d = ImageDraw.Draw(img)
    lh = 160
    y0 = H - 120 - lh * len(lines)
    d.rounded_rectangle([110, y0 - 92, 110 + d.textlength(label, font=LABEL) + 48, y0 - 30], radius=31,
                        fill=(255, 255, 255))
    d.text((134, y0 - 88), label, font=LABEL, fill=(15, 15, 18))
    for i, l in enumerate(lines):
        d.text((104, y0 + i * lh), l, font=TITLE, fill=(255, 255, 255))
    dst = os.path.join(out, path + '-wide.jpg')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    img.save(dst, quality=90)
    return dst


if __name__ == '__main__':
    out = sys.argv[1]
    for s in SPECS:
        print(make(*s, out))
