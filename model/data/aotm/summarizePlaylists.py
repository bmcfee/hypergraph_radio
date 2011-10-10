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

MIN_LENGTH = 3

def loadlist(inpickle):
    X = []
    with open(inpickle, 'r') as f:
        X = pickle.load(f)
    return X

def summarizePlaylists(listpickles):

    P = []
    for x in listpickles:
        P.extend(loadlist(x))

    lengths = []
    songs   = set()
    C       = {}
    for playlist in P:
        if playlist['category'] not in C:
            C[playlist['category']] = 0
        count = 0
        for sublist in playlist['filtered_lists']:
            if len(sublist) >= MIN_LENGTH:
                lengths.append(len(sublist))
                songs.update(sublist)
                count = count + 1
        C[playlist['category']] += count

    pprint.pprint(('Unique songs: ', len(songs)))
    pprint.pprint(('Unique playlists: ', len(lengths)))
    Z = numpy.histogram(lengths, range(1, max(lengths)+2))
    pprint.pprint(('Length histogram:',Z))

    pprint.pprint(C)
    pass


if __name__ == '__main__':
    summarizePlaylists(sys.argv[1:])
    pass
