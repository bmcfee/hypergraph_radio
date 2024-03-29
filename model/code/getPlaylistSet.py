#!/usr/bin/env python
'''
CREATED:2011-10-11 11:05:27 by Brian McFee <bmcfee@cs.ucsd.edu>

Get just the playlists we care about, indexed by mix_id

Usage:

./getPlaylistSet.py output.pickle PLAYLIST1.pickle PLAYLIST2.pickle ...


Output pickle contains hash:
    playlists: hash mix_id => list of playlists
    songs:  set of song_ids
'''

import sys
import cPickle as pickle

# MIN_LENGTH = 4
# BAD_CATEGORIES = set([u'Single Artist', u'Alternating DJ', u'Cover'])
# MIN_LENGTH = 3
# BAD_CATEGORIES = set([u'Single Artist', u'Cover'])
MIN_LENGTH = 2
BAD_CATEGORIES = set()

def loadlist(inpickle):
    X = []
    with open(inpickle, 'r') as f:
        X = pickle.load(f)
    return X

def cleanlist(p):

    q = [p[0]]
    for (i, s) in enumerate(p[1:]):
        if s == q[-1]:
            yield q
            q = []
        q.append(s)
    yield q
    pass

def cleanGenerator(l):
    for p in l:
        for q in cleanlist(p):
            yield q
    pass

def getPlaylistSet(output, inpickles):

    P = []
    for x in inpickles:
        P.extend(loadlist(x))

    playlists   = {}
    songs       = set()

    for l in P:
        if l['category'] in BAD_CATEGORIES:
            continue
        new_lists = []
        for sublist in cleanGenerator(l['filtered_lists']):
            if len(sublist) >= MIN_LENGTH:
                new_lists.append(sublist)
                songs.update(sublist)
        if len(new_lists) > 0:
            playlists[l['mix_id']] = new_lists
        pass

    with open(output, 'w') as f:
        pickle.dump({'P': playlists, 'songs': songs}, f)
    pass

if __name__ == '__main__':
    getPlaylistSet(sys.argv[1], sys.argv[2:])
    pass
