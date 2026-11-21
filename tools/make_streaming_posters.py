"""Streaming folder posters in the Films/Series poster style (name only, no logos)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import make_vertical_covers as v, make_library_covers as lib

SPECS = [
    ('netflix', ['NETFLIX'], ((225, 40, 45), (120, 20, 60))),
    ('apple-tv', ['APPLE', 'TV+'], ((150, 155, 170), (70, 80, 120))),
    ('disney-plus', ['DISNEY+'], ((40, 90, 220), (40, 190, 220))),
    ('hbo-max', ['HBO MAX'], ((110, 50, 230), (40, 70, 200))),
    ('hulu', ['HULU'], ((40, 200, 110), (20, 120, 90))),
    ('k-drama-plus', ['K-DRAMA+'], ((230, 70, 150), (120, 50, 220))),
    ('crunchyroll', ['CRUNCHY', 'ROLL'], ((240, 120, 30), (200, 60, 30))),
    ('discovery-plus', ['DISCOVERY+'], ((30, 130, 230), (20, 200, 220))),
    ('paramount-plus', ['PARAMOUNT+'], ((30, 90, 230), (90, 140, 240))),
    ('peacock', ['PEACOCK'], ((230, 180, 30), (60, 170, 220))),
    ('prime-video', ['PRIME', 'VIDEO'], ((30, 160, 230), (40, 90, 200))),
]
if __name__ == '__main__':
    for i, (slug, lines, cols) in enumerate(SPECS):
        print(v.make_v('streaming-v2/' + slug, 'STREAMING', lines, lib.m_streaming, cols, 300 + i, sys.argv[1]))
