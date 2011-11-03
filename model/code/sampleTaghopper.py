#!/usr/bin/env python
'''
CREATED:2011-11-03 10:23:22 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Generate a tag-hopper playlist

Usage:

./sampleTaghopper.py featuremap.pickle songhash.pickle N [model.pickle]

'''

import cPickle as pickle
import sys
import taghopper


def samplePlaylist(M, N, songs):
    (playlist, tagindex) = M.sample(N)
    
    for (song_id, tag) in zip(playlist, tagindex):
        print '[%20s] %s' % (M.X.tagnum(tag), songs[song_id])

    pass

if __name__ == '__main__':
    with open(sys.argv[2], 'r') as f:
        songs = pickle.load(f)
    N = int(sys.argv[3])

    if len(sys.argv) > 4:
        M = pickle.load(f)
    else:
        with open(sys.argv[1], 'r') as f:
            X = pickle.load(f)['X']
        M = taghopper.Model(X)

    samplePlaylist(M, N, songs)
    pass
