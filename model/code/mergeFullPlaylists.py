#!/usr/bin/env python
'''
CREATED:2011-10-14 09:27:03 by Brian McFee <bmcfee@cs.ucsd.edu>

Merge playlist sets into a single set

Usage:

./mergeFullPlaylists.py merged.pickle playlist_1.pickle playlist2.pickle [...]
'''

import cPickle as pickle
import sys

def mergeLists(outfile, infiles):
    P = []
    songs = set()

    for path in infiles:
        with open(path, 'r') as f:
            Q = pickle.load(f)
            P.extend(Q['P'])
            songs.update(Q['songs'])
        pass

    print '%d total playlists' % len(P)
    with open(outfile, 'w') as f:
        pickle.dump({'P': P, 'songs': songs}, f)
    pass

if __name__ == '__main__':
    mergeLists(sys.argv[1], sys.argv[2:])
    pass
