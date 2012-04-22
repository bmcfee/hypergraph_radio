#!/usr/bin/env python
'''
CREATED:2011-11-03 10:23:22 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Generate a tag-hopper playlist

Usage:

./sampleTaghopper.py model.pickle songhash.pickle N 

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
    with open(sys.argv[1], 'r') as f:
        M = pickle.load(f)
    with open(sys.argv[2], 'r') as f:
        songs = pickle.load(f)
    N = int(sys.argv[3])

    M.mu[0] = 0
    M.mu /= sum(M.mu)
    samplePlaylist(M, N, songs)
    pass
