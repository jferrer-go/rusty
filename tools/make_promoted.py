"""Wide (1920x1080) covers for collections promoted to their own Remux library,
plus posters for the awards that had none. Same style as the existing covers.
Usage: python3 tools/make_promoted.py covers"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import make_wide_covers as base, make_vertical_covers as v, make_library_covers as lib, make_award_covers as aw
import make_streaming_posters as sp

COLS = {slug: cols for slug, _l, cols in sp.SPECS}
NAMES = {slug: lines for slug, lines, _c in sp.SPECS}
WIDE = [('streaming-v2/' + s, 'STREAMING', NAMES[s], lib.m_streaming, COLS[s], 400 + i)
        for i, s in enumerate(['netflix', 'hulu', 'disney-plus', 'hbo-max', 'apple-tv'])]
WIDE += [('awards/best-picture', 'AWARDS', ['BEST', 'PICTURE'], aw.m_trophy, ((225, 165, 40), (150, 70, 20)), 21),
         ('directors/nolan', 'DIRECTOR', ['CHRISTOPHER', 'NOLAN'], lib.m_directors, v.GREY, 86)]
POSTERS = [(p.replace('-wide', ''), 'AWARDS', l, m, c, s) for p, l, m, c, s in aw.SPECS[2:]]

if __name__ == '__main__':
    out = sys.argv[1]
    for s in WIDE:
        print(base.make(*s, out))
    for s in POSTERS:
        print(v.make_v(*s, out))
