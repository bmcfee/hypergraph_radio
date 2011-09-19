#!/usr/bin/env python
'''
CREATED:2011-09-19 15:38:11 by Brian McFee <bmcfee@cs.ucsd.edu>

Index tracks by meta data (artist, title)

Usage:

./indexTracksMeta.py /path/to/unique_tracks.txt /path/to/output.pickle

'''

import sys, pprint, os
import cPickle as pickle


def createMetaIndex(metaFile, outPickle):

    M = {}

    with open(metaFile, 'r') as f:
        for line in f:
            (track_id, song_id, artist, title) = line.strip().split('<SEP>', 4)
            M[song_id] = {'artist': artist, 'title': title}

    with open(outPickle, 'w') as f:
        pickle.dump(M, f)
    pass


if __name__ == '__main__':
    createMetaIndex(sys.argv[1], sys.argv[2])
