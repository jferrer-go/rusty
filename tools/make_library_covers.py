"""Wide (16:9) covers for Rusty's top-level libraries and home rows, same look as make_wide_covers.py."""
import math, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
import make_wide_covers as base


def m_films(d):  # film strip, tilted
    t = Image.new('L', (1300, 420), 0)
    td = ImageDraw.Draw(t)
    td.rectangle([0, 0, 1299, 419], fill=255)
    for x in range(30, 1300, 90):
        td.rounded_rectangle([x, 22, x + 50, 70], radius=8, fill=0)
        td.rounded_rectangle([x, 350, x + 50, 398], radius=8, fill=0)
    for x in range(40, 1300, 300):
        td.rounded_rectangle([x, 100, x + 260, 320], radius=14, fill=90)
    t = t.rotate(-14, expand=True, resample=Image.BICUBIC)
    d._image.paste(255, (1480 - t.width // 2, 560 - t.height // 2), t)


def m_series(d):  # retro TV with antenna
    cx, cy = 1470, 600
    d.line([(cx - 40, cy - 250), (cx - 170, cy - 420)], fill=255, width=16)
    d.line([(cx + 40, cy - 250), (cx + 170, cy - 420)], fill=255, width=16)
    d.rounded_rectangle([cx - 360, cy - 250, cx + 360, cy + 230], radius=60, fill=255)
    d.rounded_rectangle([cx - 300, cy - 195, cx + 180, cy + 175], radius=40, fill=60)
    for y in (cy - 110, cy + 0):
        d.ellipse([cx + 230, y - 40, cx + 310, y + 40], fill=120)
    d.rectangle([cx - 250, cy + 230, cx - 200, cy + 300], fill=255)
    d.rectangle([cx + 200, cy + 230, cx + 250, cy + 300], fill=255)


def m_streaming(d):  # play button in a rounded screen with a progress bar
    cx, cy = 1470, 540
    d.rounded_rectangle([cx - 380, cy - 260, cx + 380, cy + 260], radius=50, outline=255, width=22)
    d.polygon([(cx - 90, cy - 150), (cx - 90, cy + 110), (cx + 150, cy - 20)], fill=255)
    d.rounded_rectangle([cx - 320, cy + 170, cx + 320, cy + 196], radius=13, fill=90)
    d.rounded_rectangle([cx - 320, cy + 170, cx + 60, cy + 196], radius=13, fill=255)
    d.ellipse([cx + 40, cy + 160, cx + 86, cy + 206], fill=255)


def m_genres(d):  # comedy / drama style masks (generic)
    def mask(cx, cy, r, f, smile):
        d.ellipse([cx - r, cy - r * 1.2, cx + r, cy + r * 1.2], fill=f)
        e = r * 0.32
        d.ellipse([cx - r * 0.55 - e / 2, cy - r * 0.35 - e / 3, cx - r * 0.55 + e / 2, cy - r * 0.35 + e / 3], fill=0)
        d.ellipse([cx + r * 0.55 - e / 2, cy - r * 0.35 - e / 3, cx + r * 0.55 + e / 2, cy - r * 0.35 + e / 3], fill=0)
        if smile:
            d.arc([cx - r * 0.55, cy, cx + r * 0.55, cy + r * 0.75], 20, 160, fill=0, width=int(r * 0.12))
        else:
            d.arc([cx - r * 0.55, cy + r * 0.35, cx + r * 0.55, cy + r * 1.1], 200, 340, fill=0, width=int(r * 0.12))
    mask(1330, 480, 230, 190, False)
    mask(1610, 600, 230, 255, True)


def m_awards(d):  # laurel wreath around a star
    cx, cy = 1470, 540
    for side in (-1, 1):
        for i in range(10):
            a = math.radians(115 + i * 15) if side < 0 else math.radians(65 - i * 15)
            x, y = cx + 300 * math.cos(a), cy + 300 * math.sin(a)
            ang = a + (math.pi / 2 if side < 0 else -math.pi / 2)
            pts = []
            for t in [k * 2 * math.pi / 24 for k in range(24)]:
                px, py = 58 * math.cos(t), 24 * math.sin(t)
                pts.append((x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang)))
            d.polygon(pts, fill=230)
    d.polygon(base.star(cx, cy, 170), fill=255)


def m_directors(d):  # director's chair and megaphone
    x0, y0 = 1190, 360
    d.rectangle([x0, y0, x0 + 360, y0 + 120], fill=255)          # backrest
    d.rectangle([x0 - 10, y0 + 230, x0 + 370, y0 + 290], fill=255)  # seat
    d.line([(x0 + 10, y0 + 120), (x0 + 10, y0 + 230)], fill=255, width=22)
    d.line([(x0 + 350, y0 + 120), (x0 + 350, y0 + 230)], fill=255, width=22)
    d.line([(x0, y0 + 290), (x0 + 360, y0 + 560)], fill=255, width=26)
    d.line([(x0 + 360, y0 + 290), (x0, y0 + 560)], fill=255, width=26)
    mx, my = 1690, 360
    d.polygon([(mx, my + 40), (mx + 60, my + 40), (mx + 230, my - 40), (mx + 230, my + 200), (mx + 60, my + 120), (mx, my + 120)], fill=210)


def m_anime(d):
    base.m_anime_top(d)


def m_all(d):  # grid of poster frames
    for r in range(3):
        for c in range(4):
            x, y = 1090 + c * 200, 180 + r * 260
            f = 255 if (r + c) % 3 == 0 else 150
            d.rounded_rectangle([x, y, x + 170, y + 230], radius=18, fill=f)


def m_watchlist(d):  # bookmark ribbon
    cx = 1470
    d.polygon([(cx - 190, 120), (cx + 190, 120), (cx + 190, 900), (cx, 740), (cx - 190, 900)], fill=255)
    d.polygon(base.star(cx, 420, 110), fill=80)


def m_suggests(d):  # sparkles
    def sparkle(cx, cy, r, f):
        d.polygon([(cx, cy - r), (cx + r * 0.22, cy - r * 0.22), (cx + r, cy), (cx + r * 0.22, cy + r * 0.22),
                   (cx, cy + r), (cx - r * 0.22, cy + r * 0.22), (cx - r, cy), (cx - r * 0.22, cy - r * 0.22)], fill=f)
    sparkle(1450, 560, 330, 255)
    sparkle(1780, 250, 120, 200)
    sparkle(1150, 260, 90, 170)
    sparkle(1790, 860, 80, 150)


SPECS = [
    # file, label, title lines, motif, colours, seed
    ('library/films', 'LIBRARY', ['FILMS'], m_films, ((220, 70, 50), (120, 30, 120)), 31),
    ('library/series', 'LIBRARY', ['SERIES'], m_series, ((40, 130, 230), (90, 40, 200)), 32),
    ('library/anime', 'LIBRARY', ['ANIME'], m_anime, ((235, 90, 160), (120, 50, 220)), 33),
    ('library/streaming', 'LIBRARY', ['STREAMING'], m_streaming, ((230, 50, 70), (40, 80, 220)), 34),
    ('library/genres', 'LIBRARY', ['GENRES'], m_genres, ((40, 190, 150), (40, 90, 200)), 35),
    ('library/awards', 'LIBRARY', ['AWARDS'], m_awards, ((225, 165, 40), (150, 60, 20)), 36),
    ('library/directors', 'LIBRARY', ['DIRECTORS'], m_directors, ((170, 175, 190), (60, 60, 120)), 37),
    ('library/all-films', 'BROWSE', ['ALL FILMS'], m_all, ((220, 70, 50), (200, 130, 30)), 38),
    ('library/all-series', 'BROWSE', ['ALL SERIES'], m_all, ((40, 130, 230), (30, 190, 200)), 39),
    ('library/watchlist-films', 'WATCHLIST', ['FILMS'], m_watchlist, ((230, 60, 90), (120, 40, 160)), 40),
    ('library/watchlist-series', 'WATCHLIST', ['SERIES'], m_watchlist, ((60, 110, 230), (120, 40, 160)), 41),
    ('library/sam-suggests', 'FOR YOU', ['SAM', 'SUGGESTS'], m_suggests, ((140, 80, 240), (40, 170, 220)), 42),
]

if __name__ == '__main__':
    out = sys.argv[1]
    for s in SPECS:
        print(base.make(*s, out))
