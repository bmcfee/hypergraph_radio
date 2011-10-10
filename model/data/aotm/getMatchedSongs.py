#!/usr/bin/env python
'''
CREATED:2011-10-09 12:56:32 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Get the matched songs from a set of playlists

Usage:

./getMatchedSongs.py PLAYLIST1.pickle PLAYLIST2.pickle ...
'''

import sys, numpy
import cPickle as pickle
import pprint

MIN_LENGTH = 4
BAD_CATEGORIES = set([u'Single Artist', u'Alternating DJ', u'Cover'])

def loadlist(inpickle):
    X = []
    with open(inpickle, 'r') as f:
        X = pickle.load(f)
    return X

def getMatchedSongs(listpickles):

    P = []
    for x in listpickles:
        P.extend(loadlist(x))

    songs   = set()
    for playlist in P:
        if playlist['category'] in BAD_CATEGORIES:
            continue
        for sublist in playlist['filtered_lists']:
            if len(sublist) >= MIN_LENGTH:
                songs.update(sublist)

    for x in songs:
        print x

    pass


if __name__ == '__main__':
    getMatchedSongs(sys.argv[1:])
    pass
