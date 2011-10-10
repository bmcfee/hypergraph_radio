#!/usr/bin/env python
'''
CREATED:2011-10-06 12:37:03 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Summarize stats of playlist translations

Usage:

./summarizePlaylists.py PLAYLIST1.pickle PLAYLIST2.pickle ...
'''

import sys, numpy
import cPickle as pickle
import pprint

def loadlist(inpickle):
    X = []
    with open(inpickle, 'r') as f:
        X = pickle.load(f)
    return X

def getMismatches(outpickle, listpickles):

    P = []
    for x in listpickles:
        P.extend(loadlist(x))

    mismatches = []
    for playlist in P:
        for (track, song_id) in playlist['playlist']:
            if song_id is None:
                mismatches.append(track)

    with open(outpickle, 'w') as f:
        pickle.dump(mismatches, f)

    pass


if __name__ == '__main__':
    getMismatches(sys.argv[1], sys.argv[2:])
    pass
