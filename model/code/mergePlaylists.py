#!/usr/bin/env python
'''
CREATED:2011-10-14 09:27:03 by Brian McFee <bmcfee@cs.ucsd.edu>

Merge (train,test) playlist sets into a single set

Usage:

./mergePlaylists.py merged_train.pickle train_1.pickle train_2.pickle [...]
'''

import cPickle as pickle
import sys

def mergeLists(outfile, infiles):
    P = []

    for path in infiles:
        with open(path, 'r') as f:
            P.extend(pickle.load(f))
        pass

    print '%d total playlists' % len(P)
    with open(outfile, 'w') as f:
        pickle.dump(P, f)
    pass

if __name__ == '__main__':
    mergeLists(sys.argv[1], sys.argv[2:])
    pass
