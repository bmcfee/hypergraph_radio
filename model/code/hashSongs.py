#!/usr/bin/env python

import sys, cPickle as pickle

songmap = {}
with open(sys.argv[1], 'r') as f:
    for line in f:
        (track, song, artist, title) = line.strip().split('<SEP>', 4)
        songmap[song] = (artist, title)

with open(sys.argv[2], 'w') as f:
    pickle.dump(songmap, f)

