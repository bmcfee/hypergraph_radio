#!/usr/bin/env python
'''
CREATED:2011-10-11 11:05:27 by Brian McFee <bmcfee@cs.ucsd.edu>

Get just the playlists we care about, indexed by mix_id

Usage:

./getPlaylistSet.py output.pickle PLAYLIST1.pickle PLAYLIST2.pickle ...
'''

import sys
import cPickle as pickle

MIN_LENGTH = 4
BAD_CATEGORIES = set([u'Single Artist', u'Alternating DJ', u'Cover'])

def loadlist(inpickle):
    X = []
    with open(inpickle, 'r') as f:
        X = pickle.load(f)
    return X

def getPlaylistSet(output, inpickles):

    P = []
    for x in inpickles:
        P.extend(loadlist(x))

    playlists = {}
    for l in P:
        if l['category'] in BAD_CATEGORIES:
            continue
        new_lists = []
        for sublist in l['filtered_lists']:
            if len(sublist) >= MIN_LENGTH:
                new_lists.append(sublist)
        if len(new_lists) > 0:
            playlists[l['mix_id']] = new_lists
        pass

    with open(output, 'w') as f:
        pickle.dump(playlists, f)
    pass

if __name__ == '__main__':
    getPlaylistSet(sys.argv[1], sys.argv[2:])
    pass
