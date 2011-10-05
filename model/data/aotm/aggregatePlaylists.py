#!/usr/bin/env python
'''
CREATED:2011-10-05 09:59:16 by Brian McFee <bmcfee@cs.ucsd.edu>
 
JSON-import a ton of playlists, save as a pickled array

Usage:
./aggregatePlaylists.py path/to/playlists playlists.pickle
'''

import json
import sys, os, glob
import cPickle as pickle

def playlistGenerator(dirname):

    for path in glob.glob('%s/*.json' % dirname):
        with open(path, 'r') as f:
            P = json.load(f)
            if 'playlist' in P:
                yield P
    pass

def loadPlaylists(dirname, outpickle):

    playlists = []

    for P in playlistGenerator(dirname):
        playlists.append(P)

    with open(outpickle, 'w') as f:
        pickle.dump(playlists, f)
    pass

if __name__ == '__main__':
    loadPlaylists(sys.argv[1], sys.argv[2])
