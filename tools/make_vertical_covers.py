"""Vertical (2:3) folder covers in the Rusty style. Reuses the wide motifs by cropping their right-hand area."""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import make_wide_covers as wide
import make_award_covers as aw
import make_library_covers as lib

VW, VH = 1000, 1500
FONT = wide.FONT
LABEL = ImageFont.truetype(FONT + 'InterDisplay-Bold.otf', 40)


def m_globe(d):
    cx, cy, r = 1470, 540, 340
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=255, width=22)
    for k in (0.35, 0.7):
        d.ellipse([cx - r * k, cy - r, cx + r * k, cy + r], outline=200, width=14)
    for y in (-0.5, 0, 0.5):
        w = r * math.sqrt(1 - y * y)
        d.line([(cx - w, cy + y * r), (cx + w, cy + y * r)], fill=200, width=14)


def m_west(d):  # sun over a mesa
    d.ellipse([1290, 230, 1650, 590], fill=255)
    d.polygon([(1000, 1080), (1000, 700), (1150, 700), (1220, 600), (1560, 600), (1640, 720),
               (1920, 720), (1920, 1080)], fill=190)


def mesh_v(cols, seed):
    main, acc = cols
    yy, xx = np.mgrid[0:VH, 0:VW].astype(float)
    img = np.tile(wide.BG, (VH, VW, 1))
    for c, (cx, cy, r) in [(acc, (0.9, 0.05, 0.75)), (main, (0.55, 0.35, 0.85)), (main, (0.1, 0.6, 0.5))]:
        dd = np.sqrt((xx - cx * VW) ** 2 + (yy - cy * VH) ** 2) / (r * VW)
        a = np.clip(1 - dd, 0, 1) ** 2.2
        img = img * (1 - a[..., None]) + np.array(c, float) * a[..., None]
    shade = np.clip(1 - (yy / VH - 0.45) * 1.4, 0.25, 1)
    img = wide.BG + (img - wide.BG) * shade[..., None]
    rng = np.random.default_rng(seed)
    return np.clip(img + rng.normal(0, 9, (VH, VW, 1)), 0, 255).astype('uint8')


def make_v(path, label, lines, motif, cols, seed, out):
    main, acc = cols
    img = Image.fromarray(mesh_v(cols, seed))
    m = Image.new('L', (wide.W, wide.H), 0)
    motif(ImageDraw.Draw(m))
    m = m.crop((990, 40, 1930, 1080)).resize((900, 996))
    mask = Image.new('L', (VW, VH), 0)
    mask.paste(m, (50, 90))
    from PIL import ImageFilter
    glow = mask.filter(ImageFilter.GaussianBlur(26))
    tint = Image.new('RGB', (VW, VH), tuple(min(255, int(c * 0.35 + 165)) for c in main))
    img = Image.composite(Image.blend(img, Image.new('RGB', (VW, VH), main), 0.6), img, glow.point(lambda v: int(v * 0.8)))
    img = Image.composite(tint, img, mask.point(lambda v: int(v * 0.85)))
    d = ImageDraw.Draw(img)
    size = 150
    while max(d.textlength(l, font=ImageFont.truetype(FONT + 'InterDisplay-Black.otf', size)) for l in lines) > 860:
        size -= 6
    title = ImageFont.truetype(FONT + 'InterDisplay-Black.otf', size)
    lh = int(size * 0.94)
    y0 = VH - 110 - lh * len(lines)
    d.rounded_rectangle([70, y0 - 88, 70 + d.textlength(label, font=LABEL) + 44, y0 - 30], radius=29, fill=(255, 255, 255))
    d.text((92, y0 - 85), label, font=LABEL, fill=(15, 15, 18))
    for i, l in enumerate(lines):
        d.text((64, y0 + i * lh), l, font=title, fill=(255, 255, 255))
    dst = os.path.join(out, path + '-poster.jpg')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    img.save(dst, quality=90)
    return dst


GOLD, ORANGE, PINK, BLUE, PURPLE = ((230, 170, 40), (200, 80, 20)), ((235, 105, 30), (190, 30, 60)), \
    ((225, 40, 120), (110, 40, 220)), ((40, 120, 235), (20, 200, 200)), ((140, 60, 230), (230, 60, 150))
GREY = ((170, 175, 190), (60, 60, 120))

SPECS = [
    ('films/popular', 'FILMS', ['POPULAR'], wide.m_popular, ORANGE, 51),
    ('films/trending', 'FILMS', ['TRENDING'], wide.m_trending, PINK, 52),
    ('films/top-rated', 'FILMS', ['TOP', 'RATED'], wide.m_top_rated, GOLD, 53),
    ('series/popular', 'SERIES', ['POPULAR'], wide.m_popular, ORANGE, 54),
    ('series/trending', 'SERIES', ['TRENDING'], wide.m_trending, PINK, 55),
    ('series/top-rated', 'SERIES', ['TOP', 'RATED'], wide.m_top_rated, GOLD, 56),
    ('series/airing-today', 'SERIES', ['AIRING', 'TODAY'], wide.m_airing, BLUE, 57),
    ('anime/airing-now', 'ANIME', ['AIRING', 'NOW'], wide.m_anime_airing, PURPLE, 58),
    ('anime/top-anime', 'ANIME', ['TOP', 'ANIME'], wide.m_anime_top, ((235, 90, 160), (120, 50, 220)), 59),
    # genre gaps
    ('genres/anime', 'GENRE', ['ANIME'], wide.m_anime_top, ((235, 90, 160), (120, 50, 220)), 61),
    ('genres/classics', 'GENRE', ['CLASSICS'], aw.m_reel, ((200, 160, 110), (90, 60, 40)), 62),
    ('genres/fantasy', 'GENRE', ['FANTASY'], lib.m_suggests, ((120, 80, 230), (40, 170, 160)), 63),
    ('genres/independent', 'GENRE', ['INDIE'], aw.m_clapper, ((60, 190, 110), (20, 110, 120)), 64),
    ('genres/international', 'GENRE', ['WORLD', 'CINEMA'], m_globe, ((40, 150, 210), (40, 200, 140)), 65),
    ('genres/westerns', 'GENRE', ['WESTERNS'], m_west, ((220, 120, 40), (150, 50, 30)), 66),
    # streaming gaps (no logos, just the name)
    ('streaming/crunchyroll', 'STREAMING', ['CRUNCHY', 'ROLL'], lib.m_streaming, ((240, 120, 30), (180, 60, 20)), 71),
    ('streaming/discovery-plus', 'STREAMING', ['DISCOVERY+'], lib.m_streaming, ((40, 120, 235), (20, 60, 160)), 72),
    ('streaming/k-drama-plus', 'STREAMING', ['K-DRAMA+'], lib.m_streaming, ((150, 50, 180), (220, 60, 140)), 73),
]
DIRECTORS = [('anderson', ['PAUL THOMAS', 'ANDERSON']), ('carpenter', ['JOHN', 'CARPENTER']),
             ('depalma', ['BRIAN', 'DE PALMA']), ('fincher', ['DAVID', 'FINCHER']),
             ('hitchcock', ['ALFRED', 'HITCHCOCK']), ('kubrick', ['STANLEY', 'KUBRICK']),
             ('nolan', ['CHRISTOPHER', 'NOLAN']), ('scorsese', ['MARTIN', 'SCORSESE']),
             ('spielberg', ['STEVEN', 'SPIELBERG']), ('villeneuve', ['DENIS', 'VILLENEUVE'])]
for i, (k, n) in enumerate(DIRECTORS):
    SPECS.append((f'directors/{k}', 'DIRECTOR', n, lib.m_directors, GREY, 80 + i))

if __name__ == '__main__':
    for s in SPECS:
        print(make_v(*s, sys.argv[1]))
