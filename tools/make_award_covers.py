"""Original wide award covers for Rusty, built on the same look as make_wide_covers.py."""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
import make_wide_covers as base

W, H = base.W, base.H


def laurel(d, cx, cy, r, f, side):
    # a branch of leaves curving up one side of a circle
    for i in range(9):
        a = math.radians(110 + i * 17) if side < 0 else math.radians(70 - i * 17)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        ang = a + (math.pi / 2 if side < 0 else -math.pi / 2)
        lx, ly = 46, 20
        pts = []
        for t in np.linspace(0, 2 * math.pi, 24):
            px, py = lx * math.cos(t), ly * math.sin(t)
            pts.append((x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang)))
        d.polygon(pts, fill=f)
    d.arc([cx - r, cy - r, cx + r, cy + r], start=110 if side < 0 else -80, end=260 if side < 0 else 70, fill=f, width=8)


def m_trophy(d):  # two-handled cup inside a laurel wreath
    cx, cy = 1460, 520
    laurel(d, cx, cy + 20, 330, 170, -1)
    laurel(d, cx, cy + 20, 330, 170, 1)
    d.pieslice([cx - 150, cy - 230, cx + 150, cy + 70], 0, 180, fill=255)       # bowl
    d.rectangle([cx - 150, cy - 160, cx + 150, cy - 80], fill=255)
    d.arc([cx - 230, cy - 160, cx - 110, cy - 20], 90, 270, fill=255, width=26)  # handles
    d.arc([cx + 110, cy - 160, cx + 230, cy - 20], -90, 90, fill=255, width=26)
    d.rectangle([cx - 22, cy + 70, cx + 22, cy + 170], fill=255)                 # stem
    d.rounded_rectangle([cx - 120, cy + 170, cx + 120, cy + 215], radius=10, fill=255)
    d.rounded_rectangle([cx - 160, cy + 215, cx + 160, cy + 270], radius=10, fill=230)


def m_spotlights(d):  # crossing spotlight beams with a star at the meeting point
    for x0, a in [(1050, -0.55), (1880, 0.55)]:
        tip = (1460, 330)
        d.polygon([(x0 - 70, 1080), (x0 + 70, 1080), (tip[0] + 25, tip[1]), (tip[0] - 25, tip[1])], fill=120)
    d.polygon(base.star(1460, 300, 150), fill=255)
    for i in range(14):
        a = i * math.pi / 7
        d.line([(1460 + 190 * math.cos(a), 300 + 190 * math.sin(a)),
                (1460 + 240 * math.cos(a), 300 + 240 * math.sin(a))], fill=200, width=8)


def m_mask(d):  # ribbon medal
    cx, cy = 1460, 600
    d.polygon([(cx - 170, 120), (cx - 40, 120), (cx + 40, cy - 120), (cx - 60, cy - 100)], fill=170)
    d.polygon([(cx + 170, 120), (cx + 40, 120), (cx - 40, cy - 120), (cx + 60, cy - 100)], fill=210)
    d.ellipse([cx - 230, cy - 230, cx + 230, cy + 230], fill=255)
    d.ellipse([cx - 175, cy - 175, cx + 175, cy + 175], outline=120, width=10)
    d.polygon(base.star(cx, cy, 120), fill=140)


def m_reel(d):  # film reel
    cx, cy = 1470, 540
    d.ellipse([cx - 360, cy - 360, cx + 360, cy + 360], fill=255)
    d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=0)
    for i in range(6):
        a = i * math.pi / 3
        x, y = cx + 210 * math.cos(a), cy + 210 * math.sin(a)
        d.ellipse([x - 95, y - 95, x + 95, y + 95], fill=0)
    d.line([(cx + 250, cy + 260), (1900, 1000)], fill=200, width=40)


def m_ticket(d):  # admit-one ticket, tilted
    t = Image.new('L', (900, 420), 0)
    td = ImageDraw.Draw(t)
    td.rounded_rectangle([0, 0, 899, 419], radius=40, fill=255)
    for y in (0, 419):
        for x in range(60, 900, 120):
            td.ellipse([x - 22, y - 22, x + 22, y + 22], fill=0)
    td.line([(640, 40), (640, 380)], fill=0, width=10)
    td.polygon(base.star(320, 210, 120), fill=0)
    td.polygon(base.star(770, 210, 60), fill=0)
    t = t.rotate(14, expand=True, resample=Image.BICUBIC)
    d._image.paste(255, (1460 - t.width // 2, 560 - t.height // 2), t)


def m_clapper(d):  # clapperboard
    x0, y0 = 1130, 420
    d.rounded_rectangle([x0, y0, x0 + 680, y0 + 460], radius=30, fill=255)
    d.line([(x0 + 40, y0 + 200), (x0 + 640, y0 + 200)], fill=0, width=10)
    d.line([(x0 + 40, y0 + 320), (x0 + 640, y0 + 320)], fill=0, width=10)
    arm = [(x0 - 10, y0 - 40), (x0 + 690, y0 - 230), (x0 + 720, y0 - 130), (x0 + 20, y0 + 60)]
    d.polygon(arm, fill=255)
    for i in range(5):
        bx = x0 + 60 + i * 135
        d.polygon([(bx, y0 + 30 - i * 37), (bx + 70, y0 + 11 - i * 37), (bx + 40, y0 - 70 - i * 37),
                   (bx - 30, y0 - 51 - i * 37)], fill=0)


SPECS = [
    # file, title lines, motif, colours, seed   (folder in brackets)
    ('awards/best-picture-wide', ['BEST', 'PICTURE'], m_trophy, ((225, 165, 40), (150, 70, 20)), 21),      # Oscars
    ('awards/hollywood-honours-wide', ['HOLLYWOOD', 'HONOURS'], m_spotlights, ((235, 120, 40), (200, 40, 70)), 22),  # Golden Globes
    ('awards/british-cinema-wide', ['BRITISH', 'CINEMA'], m_mask, ((170, 185, 210), (40, 70, 160)), 23),   # BAFTA
    ('awards/festival-winners-wide', ['FESTIVAL', 'WINNERS'], m_reel, ((220, 50, 60), (120, 20, 80)), 24),  # Cannes
    ('awards/festival-cinema-wide', ['FESTIVAL', 'CINEMA'], m_ticket, ((30, 160, 190), (30, 60, 160)), 25),  # Venice
    ('awards/independent-film-wide', ['INDEPENDENT', 'FILM'], m_clapper, ((60, 190, 110), (20, 110, 120)), 26),  # Independent Spirit
]

if __name__ == '__main__':
    out = sys.argv[1]
    for path, lines, motif, cols, seed in SPECS:
        print(base.make(path.replace('-wide', ''), 'AWARDS', lines, motif, cols, seed, out))
